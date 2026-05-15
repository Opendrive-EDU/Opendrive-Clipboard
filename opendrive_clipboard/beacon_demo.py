"""Synthetic OpenDrive Beacon telemetry for the public Clipboard demo.

This module fabricates a plausible-shaped recording for one of the seeded
demo scenarios. **It is not a real Beacon recording.** OpenDrive Beacon
itself lives in a private mono-repo (see ``docs/BOUNDARY.md`` and
``README.md``). Nothing here reads a CAN bus, an IMU, a GPS receiver,
or a forward camera.

Strict properties:

- A scenario is a one-hour lesson (Drive 1-6). The synthetic recording is
  a compact, deterministic, *representative* window (not real-time): each
  lesson event's MM:SS mark is scaled proportionally into the sampled
  window so the grader still responds to the events while the payload
  stays tiny. ``meta["lesson_minutes"]`` carries the true lesson length;
  ``meta["duration_s"]`` is the sampled-window length.
- Output is deterministic per ``scenario_id`` (seeded ``random.Random``).
  Two calls produce identical bytes so judges can reproduce the demo.
- ``meta["has_audio"]`` is ``False`` for this synthetic recording. The
  production boundary mic (Audio-Technica ATR4697-USB, opt-in, hardware
  kill switch + UI toggle) is used only for DOL commentary-driving
  exercises and is not present in synthetic data. This module never
  returns an ``audio``, ``cabin``, or raw-audio field.
- ``forward_camera`` carries text labels only - no image bytes, no URLs.
- GPS coordinates are local offsets around (0, 0); they are not real
  Washington locations and cannot be reverse-geocoded.
- Intervention taps are anchored on the scenario's existing event
  timestamps, so the grader and UI line up with the Clipboard demo.
"""

from __future__ import annotations

import math
import random
from copy import deepcopy

from opendrive_clipboard.demo_data import demo_scenarios


# 30-second window at 1 Hz keeps the payload tiny and reproducible.
DEFAULT_DURATION_S: int = 30
SAMPLE_HZ: int = 1


def mock_beacon_recording(scenario_id: str) -> dict:
    """Return a synthetic Beacon-shaped recording for ``scenario_id``.

    Raises ``ValueError`` for an unknown scenario.
    """

    scenarios = demo_scenarios()
    if scenario_id not in scenarios:
        raise ValueError(f"Unknown demo scenario: {scenario_id}")

    scenario = scenarios[scenario_id]
    rng = random.Random(_seed(scenario_id))
    duration = DEFAULT_DURATION_S
    timestamps = [round(t / SAMPLE_HZ, 2) for t in range(duration * SAMPLE_HZ)]

    can = _build_can(rng, timestamps, scenario)
    imu = _build_imu(rng, timestamps, can)
    gps = _build_gps(rng, timestamps, can)
    forward_camera = _build_forward_camera_labels(scenario)
    intervention_taps = _build_intervention_taps(scenario)

    return {
        "meta": {
            "scenario_id": scenario_id,
            "scenario_title": scenario["title"],
            "lesson_minutes": _lesson_minutes(scenario),
            "duration_s": duration,
            "sample_hz": SAMPLE_HZ,
            "sampled_window_note": (
                "Compact representative window. The lesson is "
                f"{_lesson_minutes(scenario)} minutes; event marks are scaled "
                "into this window for deterministic, low-payload grading."
            ),
            "synthetic": True,
            "has_audio": False,
            "mic_disclosure": (
                "This synthetic recording contains no audio. The production "
                "boundary mic is opt-in (hardware kill switch + UI toggle + "
                "ephemeral STT) for DOL commentary-driving exercises; "
                "transcript-only retention by default."
            ),
            "data_source": "mock_beacon_demo_generator_v1",
        },
        "can": can,
        "imu": imu,
        "gps": gps,
        "forward_camera": forward_camera,
        "intervention_taps": intervention_taps,
    }


# --- internals ---------------------------------------------------------------


def _seed(scenario_id: str) -> int:
    # Stable hash across Python runs (built-in hash() is salted per-process).
    total = 0
    for char in scenario_id:
        total = (total * 131 + ord(char)) & 0xFFFFFFFF
    return total


def _build_can(rng: random.Random, timestamps: list[float], scenario: dict) -> list[dict]:
    """Plausible speed / throttle / brake / steering trace, scenario-shaped."""

    window_s = len(timestamps) / SAMPLE_HZ if timestamps else DEFAULT_DURATION_S
    event_seconds = _scaled_event_seconds(scenario, window_s)
    samples: list[dict] = []
    base_speed = 22.0 if "residential" in scenario["route"].lower() else 28.0

    # Synthetic improvement arc: ``competence`` (0=rough .. 1=polished) drives
    # how hard the learner brakes/accelerates around an event and how much
    # speed/steering noise they carry. A polished Drive 6 reads smoother than
    # a first-hour Drive 1. ``severity`` is the rough-driver weight.
    competence = float(scenario.get("competence", 0.5))
    competence = max(0.0, min(1.0, competence))
    severity = 1.0 - competence

    for t in timestamps:
        # gentle sinusoidal cruise + per-scenario jitter (noise shrinks as the
        # learner improves, never to zero so the trace stays textured)
        cruise = base_speed + 2.0 * math.sin(t / 6.0)
        jitter = rng.uniform(-0.6, 0.6) * (0.35 + 0.65 * severity)
        speed = cruise + jitter

        # near event timestamps, simulate brake/throttle behavior. A rough
        # driver dumps speed and stabs the brake; a polished driver eases.
        near_event = any(abs(t - sec) <= 1.5 for sec in event_seconds)
        if near_event:
            speed -= 1.4 + 3.0 * severity
            throttle = max(0.0, (30.0 - 12.0 * severity) + rng.uniform(-4.0, 4.0) * (0.4 + severity))
            brake = min(95.0, (10.0 + 52.0 * severity) + rng.uniform(-6.0, 10.0) * (0.4 + severity))
        else:
            throttle = max(0.0, 33.0 + rng.uniform(-6.0, 6.0) * (0.4 + severity))
            brake = max(0.0, 5.0 + rng.uniform(-3.0, 5.0) * (0.4 + severity))

        # Keep the sinusoid (preserves mirror/scan cadence proxy); only the
        # amplitude and noise relax with competence, lowering lateral load.
        steering = (2.4 + 1.8 * severity) * math.sin(t / 4.0) + rng.uniform(
            -1.2, 1.2
        ) * (0.35 + 0.65 * severity)

        samples.append(
            {
                "t": t,
                "speed_mph": round(max(0.0, speed), 2),
                "throttle_pct": round(throttle, 2),
                "brake_pct": round(brake, 2),
                "steering_deg": round(steering, 2),
            }
        )

    return samples


def _build_imu(
    rng: random.Random,
    timestamps: list[float],
    can: list[dict],
) -> list[dict]:
    """IMU samples derived from the CAN trace + a small noise floor."""

    samples: list[dict] = []
    prev_speed = can[0]["speed_mph"] if can else 0.0
    prev_steer = can[0]["steering_deg"] if can else 0.0

    for idx, t in enumerate(timestamps):
        speed = can[idx]["speed_mph"]
        steer = can[idx]["steering_deg"]
        # mph -> m/s conversion factor 0.44704; per-second delta gives accel
        accel_long = (speed - prev_speed) * 0.44704
        # lateral accel proxy from steering rate at speed
        accel_lat = (steer - prev_steer) * 0.015 * max(1.0, speed / 10.0)
        # yaw rate proxy
        yaw_rate = (steer - prev_steer) * 0.6 + rng.uniform(-0.2, 0.2)

        samples.append(
            {
                "t": t,
                "accel_long_mps2": round(accel_long, 3),
                "accel_lat_g": round(accel_lat / 9.81, 4),
                "yaw_rate_deg_s": round(yaw_rate, 3),
            }
        )

        prev_speed = speed
        prev_steer = steer

    return samples


def _build_gps(
    rng: random.Random,
    timestamps: list[float],
    can: list[dict],
) -> list[dict]:
    """Synthetic local-frame polyline; not a real Washington location."""

    samples: list[dict] = []
    lat = 0.0
    lng = 0.0
    heading = math.pi / 4
    for idx, t in enumerate(timestamps):
        speed_mps = can[idx]["speed_mph"] * 0.44704
        # meters per sample -> degrees (rough conversion, demo-only)
        step = speed_mps / 111_320
        lat += step * math.cos(heading)
        lng += step * math.sin(heading)
        heading += can[idx]["steering_deg"] * 0.001 + rng.uniform(-0.004, 0.004)
        samples.append(
            {
                "t": t,
                "lat_offset": round(lat, 6),
                "lng_offset": round(lng, 6),
            }
        )

    return samples


def _build_forward_camera_labels(scenario: dict) -> list[dict]:
    """Text labels only - never images. Drawn from scenario observations."""

    return [
        {
            "t": _seconds(event["time"]),
            "frame_label": event["observation"],
        }
        for event in scenario["events"]
    ]


def _build_intervention_taps(scenario: dict) -> list[dict]:
    """Instructor on-screen taps for events the instructor verbally intervened on.

    Only events flagged ``"intervention": True`` produce a tap — a one-hour
    lesson has many observed teachable moments but few moments that required
    the instructor to step in. The tap carries a timestamp only, never audio,
    and is independent of the boundary mic used for DOL commentary-driving
    exercises. ``t`` is the real lesson-time mark (for display); the grader
    uses only the tap count.
    """

    return [
        {
            "t": _seconds(event["time"]),
            "label": event["signal"],
            "pattern": event["pattern"],
        }
        for event in scenario["events"]
        if event.get("intervention")
    ]


def _seconds(stamp: str) -> int:
    """Parse a ``MM:SS`` event time into integer seconds."""

    minutes, seconds = stamp.split(":")
    return int(minutes) * 60 + int(seconds)


def _lesson_seconds(scenario: dict) -> int:
    """Total lesson length in seconds (from ``duration_min``, with fallback)."""

    minutes = scenario.get("duration_min")
    if minutes:
        return int(minutes) * 60
    event_secs = [_seconds(e["time"]) for e in scenario["events"]]
    return max(event_secs) if event_secs else DEFAULT_DURATION_S


def _lesson_minutes(scenario: dict) -> int:
    """Lesson length in whole minutes, never below 1."""

    return max(1, round(_lesson_seconds(scenario) / 60))


def _scaled_event_seconds(scenario: dict, window_s: float) -> set[int]:
    """Map each event's lesson-time mark into the compact sampled window.

    A one-hour lesson is compressed into ``window_s`` seconds so the
    synthetic CAN/IMU trace still reacts to every event while the payload
    stays tiny. Pure arithmetic on fixed event times — fully deterministic.
    """

    span = max(1, _lesson_seconds(scenario))
    usable = max(1.0, window_s - 2.0)
    scaled: set[int] = set()
    for event in scenario["events"]:
        fraction = min(1.0, _seconds(event["time"]) / span)
        scaled.add(1 + round(fraction * usable))
    return scaled


def beacon_recording(scenario_id: str) -> dict:
    """Public deep-copying accessor (matches the demo_data helper pattern)."""

    return deepcopy(mock_beacon_recording(scenario_id))
