"""Synthetic OpenDrive Beacon telemetry for the public Clipboard demo.

This module fabricates a plausible-shaped recording for one of the seeded
demo scenarios. **It is not a real Beacon recording.** OpenDrive Beacon
itself lives in a private mono-repo (see ``docs/BOUNDARY.md`` and
``README.md``). Nothing here reads a CAN bus, an IMU, a GPS receiver,
or a forward camera.

Strict properties:

- Output is deterministic per ``scenario_id`` (seeded ``random.Random``).
  Two calls produce identical bytes so judges can reproduce the demo.
- ``meta["has_audio"]`` is always ``False``. **There is no microphone
  anywhere in OpenDrive Beacon.** This module never returns an ``audio``,
  ``cabin``, or ``microphone`` field.
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
            "duration_s": duration,
            "sample_hz": SAMPLE_HZ,
            "synthetic": True,
            "has_audio": False,
            "no_microphone_disclosure": (
                "OpenDrive Beacon never records, transmits, or processes audio "
                "of any kind from inside the vehicle."
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

    event_seconds = {_seconds(event["time"]) for event in scenario["events"]}
    samples: list[dict] = []
    base_speed = 22.0 if "residential" in scenario["route"].lower() else 28.0

    for t in timestamps:
        # gentle sinusoidal cruise + per-scenario jitter
        cruise = base_speed + 2.0 * math.sin(t / 6.0)
        jitter = rng.uniform(-0.6, 0.6)
        speed = cruise + jitter

        # near event timestamps, simulate brake/throttle behavior
        near_event = any(abs(t - sec) <= 1.5 for sec in event_seconds)
        if near_event:
            speed -= 3.5
            throttle = max(0.0, 18.0 + rng.uniform(-4.0, 4.0))
            brake = min(95.0, 55.0 + rng.uniform(-8.0, 12.0))
        else:
            throttle = max(0.0, 35.0 + rng.uniform(-6.0, 6.0))
            brake = max(0.0, 6.0 + rng.uniform(-4.0, 6.0))

        steering = 4.0 * math.sin(t / 4.0) + rng.uniform(-1.2, 1.2)

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
    """Instructor on-screen taps anchored on scenario event times (no audio)."""

    return [
        {
            "t": _seconds(event["time"]),
            "label": event["signal"],
            "pattern": event["pattern"],
        }
        for event in scenario["events"]
    ]


def _seconds(stamp: str) -> int:
    """Parse a ``MM:SS`` event time into integer seconds."""

    minutes, seconds = stamp.split(":")
    return int(minutes) * 60 + int(seconds)


def beacon_recording(scenario_id: str) -> dict:
    """Public deep-copying accessor (matches the demo_data helper pattern)."""

    return deepcopy(mock_beacon_recording(scenario_id))
