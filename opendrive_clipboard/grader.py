"""Deterministic rule-based grader for the DOL drive sheet draft.

What it does
------------
Given a scenario id, the grader:

1. Pulls the synthetic Beacon recording (``opendrive_clipboard.beacon_demo``).
2. Derives a blood-panel-style set of numeric metrics with reference ranges.
3. Drafts a 1-4 rating per WA DOL form skill row (``dol_sheet.DOL_SKILLS``).
   Skills with no telemetry signal are left ``None`` for the instructor.
4. Produces an eco score and a calm / tentative / aggressive attitude profile.
5. Pulls strengths and gaps from the rating sweep.
6. Drafts a Section 3 comment paragraph + suggested reaction-to-coaching.

What it does NOT do
-------------------
- It does not auto-approve anything. Every output is stamped
  ``DRAFT_INSTRUCTOR_REVIEW_REQUIRED``. The licensed instructor is the sole
  authority on the final form (``docs/BOUNDARY.md``).
- It does not "train" anything in the ML sense. The numbers are
  deterministic, rule-based, reproducible. The optional Gemini hook only
  ever varies prose - never the 1-4 ratings, never the blood-panel numbers.
- It does not read or produce audio. Beacon has no microphone.
"""

from __future__ import annotations

import statistics
from copy import deepcopy

from opendrive_clipboard.beacon_demo import mock_beacon_recording
from opendrive_clipboard.demo_data import curriculum_snippets, demo_scenarios
from opendrive_clipboard.dol_sheet import (
    DOL_SKILLS,
    RATING_SCALE,
    REACTION_TO_COACHING,
    pattern_to_skills,
    skill_groups,
)


DRAFT_STATUS: str = "DRAFT_INSTRUCTOR_REVIEW_REQUIRED"
DRAFT_LABEL: str = "DRAFT - INSTRUCTOR REVIEW REQUIRED"


def grade_drive(scenario_id: str) -> dict:
    """Produce a draft DOL-aligned drive report for ``scenario_id``."""

    scenarios = demo_scenarios()
    if scenario_id not in scenarios:
        raise ValueError(f"Unknown demo scenario: {scenario_id}")

    scenario = scenarios[scenario_id]
    beacon = mock_beacon_recording(scenario_id)
    panel = _blood_panel(beacon)
    panel_index = {row["metric"]: row for row in panel}

    skill_ratings = _rate_skills(scenario, panel_index)
    eco_score = _eco_score(panel_index)
    attitude = _attitude_profile(beacon, panel_index)
    strengths, gaps = _strengths_and_gaps(skill_ratings)
    section_three = _section_three_draft(scenario, gaps, attitude)

    return {
        "status": DRAFT_STATUS,
        "status_label": DRAFT_LABEL,
        "instructor_review_required": True,
        "synthetic_only": True,
        "has_audio": False,
        "no_microphone_disclosure": (
            "OpenDrive Beacon has no microphone. This report contains no audio."
        ),
        "scenario": {
            "id": scenario["id"],
            "title": scenario["title"],
            "focus": scenario["focus"],
            "route": scenario["route"],
            "conditions": scenario["conditions"],
        },
        "form_reference": {
            "agency": "Washington State Department of Licensing",
            "form_id": "DTS-661-047",
            "revision": "N/12/24",
            "section_1_drive_log": {
                "instructor": "Licensed instructor (placeholder)",
                "student": "Demo learner (placeholder)",
                "drive_date": "synthetic-demo",
                "start_time": "synthetic-demo",
                "end_time": "synthetic-demo",
                "total_time_min": beacon["meta"]["duration_s"] // 60 or 1,
            },
        },
        "rating_scale": RATING_SCALE,
        "skill_groups": skill_groups(),
        "skill_ratings": skill_ratings,
        "blood_panel": panel,
        "eco_score": eco_score,
        "attitude_profile": attitude,
        "strengths": strengths,
        "needs_improvement": gaps,
        "section_three_draft": section_three,
        "beacon_snapshot": {
            "meta": beacon["meta"],
            "intervention_taps": beacon["intervention_taps"],
            "forward_camera_labels": beacon["forward_camera"],
            "can_sample_count": len(beacon["can"]),
            "imu_sample_count": len(beacon["imu"]),
            "gps_sample_count": len(beacon["gps"]),
        },
    }


# --- skill ratings -----------------------------------------------------------


def _rate_skills(scenario: dict, panel: dict[str, dict]) -> list[dict]:
    """Suggest a 1-4 per DOL skill row from telemetry + scenario events."""

    pattern_hits: dict[str, list[str]] = {}
    for event in scenario["events"]:
        for skill_id in pattern_to_skills(event["pattern"]):
            pattern_hits.setdefault(skill_id, []).append(event["signal"])

    ratings: list[dict] = []
    for skill in DOL_SKILLS:
        rating, rationale = _rate_one_skill(skill, panel, pattern_hits)
        ratings.append(
            {
                "id": skill["id"],
                "label": skill["label"],
                "group": skill["group"],
                "suggested_rating": rating,
                "rating_label": RATING_SCALE[rating]["label"] if rating else None,
                "rationale": rationale,
                "instructor_override": None,
                "telemetry_signals": list(skill["telemetry"]),
            }
        )

    return ratings


def _rate_one_skill(
    skill: dict,
    panel: dict[str, dict],
    pattern_hits: dict[str, list[str]],
) -> tuple[int | None, str]:
    """Combine panel flags + event hits into a 1-4 (or None) per skill."""

    flag = _worst_flag(skill["telemetry"], panel)
    hits = pattern_hits.get(skill["id"], [])

    if flag is None and not hits:
        return (
            None,
            "No telemetry signal in this synthetic window. Instructor fills.",
        )

    # Skills tagged by intervention events drop a level - the moment needed
    # instructor prompting, which means at minimum it was a coaching moment.
    base = {"ok": 4, "watch": 3, "concern": 2, None: 3}[flag]
    if hits:
        base = min(base, 3)
        # If the panel itself flagged "concern", call it Needs improvement.
        if flag == "concern":
            base = 2

    rationale_parts: list[str] = []
    if flag is not None:
        signal_summary = ", ".join(skill["telemetry"]) or "panel signals"
        rationale_parts.append(f"Panel flag for {signal_summary}: {flag}.")
    if hits:
        rationale_parts.append(
            "Intervention event(s) observed: " + "; ".join(hits) + "."
        )

    return base, " ".join(rationale_parts)


def _worst_flag(signals: list[str], panel: dict[str, dict]) -> str | None:
    """Return the worst flag (concern > watch > ok) across panel signals."""

    severity = {"ok": 0, "watch": 1, "concern": 2}
    worst: str | None = None
    for signal in signals:
        row = panel.get(signal)
        if not row:
            continue
        flag = row["flag"]
        if worst is None or severity[flag] > severity[worst]:
            worst = flag

    return worst


# --- blood panel -------------------------------------------------------------


def _blood_panel(beacon: dict) -> list[dict]:
    """Clinical-style metrics with reference ranges + ok/watch/concern flag."""

    can = beacon["can"]
    imu = beacon["imu"]
    taps = beacon["intervention_taps"]

    speeds = [s["speed_mph"] for s in can]
    throttles = [s["throttle_pct"] for s in can]
    brakes = [s["brake_pct"] for s in can]
    steerings = [s["steering_deg"] for s in can]
    lat_accels = [abs(s["accel_lat_g"]) for s in imu]

    brake_jerk = _series_jerk(brakes)
    throttle_jerk = _series_jerk(throttles)

    # Clamp helpers
    def _clip(value: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, value))

    smooth_braking = _clip(100.0 - brake_jerk * 6.0, 0.0, 100.0)
    throttle_smooth = _clip(100.0 - throttle_jerk * 6.0, 0.0, 100.0)
    mean_following = round(_clip(4.0 - (statistics.mean(speeds) / 30.0), 1.5, 5.0), 2)
    peak_lat = round(max(lat_accels) if lat_accels else 0.0, 3)
    # Synthesize a mirror cadence from steering oscillation count
    mirror_cadence = round(_oscillations(steerings) * (60 / max(1, len(can))), 2)
    lane_position_var = round(statistics.pstdev(steerings) * 0.025, 3)
    intervention_count = len(taps)

    rows: list[dict] = [
        _row("smooth_braking_score", round(smooth_braking, 1), "/ 100",
             ">= 70", lambda v: "ok" if v >= 70 else "watch" if v >= 55 else "concern"),
        _row("throttle_smoothness", round(throttle_smooth, 1), "/ 100",
             ">= 70", lambda v: "ok" if v >= 70 else "watch" if v >= 55 else "concern"),
        _row("mean_following_distance_s", mean_following, "s",
             ">= 3.0",
             lambda v: "ok" if v >= 3.0 else "watch" if v >= 2.5 else "concern"),
        _row("peak_lateral_accel_g", peak_lat, "g",
             "< 0.40",
             lambda v: "ok" if v < 0.30 else "watch" if v < 0.40 else "concern"),
        _row("mirror_cadence_per_min", mirror_cadence, "per min",
             ">= 4",
             lambda v: "ok" if v >= 4 else "watch" if v >= 2 else "concern"),
        _row("intervention_count", intervention_count, "events",
             "<= 1 per drive",
             lambda v: "ok" if v <= 1 else "watch" if v <= 3 else "concern"),
        _row("lane_position_variance", lane_position_var, "m",
             "< 0.30",
             lambda v: "ok" if v < 0.20 else "watch" if v < 0.30 else "concern"),
    ]

    return rows


def _row(metric: str, value: float, unit: str, ref_range: str, flagger) -> dict:
    return {
        "metric": metric,
        "value": value,
        "unit": unit,
        "ref_range": ref_range,
        "flag": flagger(value),
    }


def _series_jerk(series: list[float]) -> float:
    """Mean absolute first difference - a proxy for jerkiness."""

    if len(series) < 2:
        return 0.0
    diffs = [abs(series[i] - series[i - 1]) for i in range(1, len(series))]
    return statistics.mean(diffs)


def _oscillations(series: list[float]) -> int:
    """Count sign flips of the series (proxy for mirror / scan cadence)."""

    flips = 0
    prev_sign = 0
    for value in series:
        sign = 1 if value > 0 else -1 if value < 0 else 0
        if sign != 0 and prev_sign != 0 and sign != prev_sign:
            flips += 1
        if sign != 0:
            prev_sign = sign
    return flips


# --- eco + attitude ----------------------------------------------------------


def _eco_score(panel: dict[str, dict]) -> dict:
    """0-100 eco score blended from throttle / brake smoothness."""

    throttle = panel["throttle_smoothness"]["value"]
    brake = panel["smooth_braking_score"]["value"]
    score = round((throttle * 0.55 + brake * 0.45), 1)

    if score >= 80:
        band = "efficient"
    elif score >= 60:
        band = "developing"
    else:
        band = "aggressive"

    return {
        "score": score,
        "band": band,
        "components": {
            "throttle_smoothness": throttle,
            "smooth_braking_score": brake,
        },
        "note": (
            "Eco score is a synthetic estimate derived from mock telemetry. "
            "It is not a fuel-economy measurement."
        ),
    }


def _attitude_profile(beacon: dict, panel: dict[str, dict]) -> dict:
    """Calm / tentative / aggressive split, sums to 100."""

    intervention = panel["intervention_count"]["value"]
    brake_smooth = panel["smooth_braking_score"]["value"]
    lat = panel["peak_lateral_accel_g"]["value"]
    follow = panel["mean_following_distance_s"]["value"]

    # Aggressive: low brake smoothness, high lat accel, short follow distance.
    aggressive_score = (
        max(0.0, 100.0 - brake_smooth) * 0.35
        + max(0.0, lat - 0.25) * 200.0
        + max(0.0, 3.0 - follow) * 25.0
    )
    # Tentative: many interventions + low-ish brake smoothness.
    tentative_score = (
        intervention * 12.0
        + max(0.0, 75.0 - brake_smooth) * 0.3
    )
    calm_score = max(10.0, 110.0 - aggressive_score - tentative_score)

    total = aggressive_score + tentative_score + calm_score
    if total <= 0:
        calm, tentative, aggressive = 100, 0, 0
    else:
        calm = round(calm_score * 100 / total)
        tentative = round(tentative_score * 100 / total)
        aggressive = 100 - calm - tentative
        # Avoid negative due to rounding
        if aggressive < 0:
            calm += aggressive
            aggressive = 0

    return {
        "calm_pct": calm,
        "tentative_pct": tentative,
        "aggressive_pct": aggressive,
        "note": (
            "Driver attitude is a synthetic estimate derived from mock "
            "telemetry. It is not a clinical assessment."
        ),
    }


# --- strengths, gaps, section 3 ---------------------------------------------


def _strengths_and_gaps(ratings: list[dict]) -> tuple[list[dict], list[dict]]:
    """Pull strengths (4s) and gaps (1-2s) out of the rated skill list."""

    snippets = curriculum_snippets()

    strengths: list[dict] = []
    gaps: list[dict] = []
    for row in ratings:
        rating = row["suggested_rating"]
        if rating == 4:
            strengths.append(
                {
                    "skill_id": row["id"],
                    "skill_label": row["label"],
                    "note": row["rationale"],
                }
            )
        elif rating in (1, 2):
            curriculum_link = _best_curriculum_link(row, snippets)
            gaps.append(
                {
                    "skill_id": row["id"],
                    "skill_label": row["label"],
                    "note": row["rationale"],
                    "curriculum": curriculum_link,
                }
            )

    return strengths, gaps


def _best_curriculum_link(row: dict, snippets: dict[str, dict]) -> dict | None:
    """Pick a curriculum snippet whose topic aligns with this skill."""

    # Match via the event pattern -> skill mapping in dol_sheet.
    for pattern, snippet in snippets.items():
        if row["id"] in pattern_to_skills(pattern):
            return {
                "topic": snippet["topic"],
                "lesson": snippet["lesson"],
                "standard": snippet["standard"],
            }
    return None


def _section_three_draft(
    scenario: dict,
    gaps: list[dict],
    attitude: dict,
) -> dict:
    """Draft text for DOL Section 3 (comments + reaction to coaching)."""

    if gaps:
        gap_summary = "; ".join(g["skill_label"] for g in gaps[:3])
        comment = (
            f"Synthetic drive focused on {scenario['focus'].rstrip('.')}. "
            f"Coaching priority next session: {gap_summary}. "
            "Calm correction observed; instructor to confirm the final rating."
        )
    else:
        comment = (
            f"Synthetic drive focused on {scenario['focus'].rstrip('.')}. "
            "No 1-2 ratings drafted. Instructor to confirm before any record."
        )

    if attitude["calm_pct"] >= 60:
        reaction = "good"
    elif attitude["tentative_pct"] >= 35 or attitude["aggressive_pct"] >= 35:
        reaction = "needs_improvement"
    else:
        reaction = "good"

    return {
        "comments_draft": comment,
        "reaction_to_coaching_suggested": reaction,
        "reaction_to_coaching_options": list(REACTION_TO_COACHING),
        "instructor_override": None,
    }


def grade_drive_copy(scenario_id: str) -> dict:
    """Deep-copying accessor for callers that need an isolated payload."""

    return deepcopy(grade_drive(scenario_id))
