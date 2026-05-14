"""Canonical WA DOL Driver Training School Behind-the-Wheel form constants.

Source of truth: WA DOL form **DTS-661-047 (N/12/24)** -
"Driver Training School Behind-the-Wheel Instruction Log" (8 pages).
A copy is shipped at ``docs/dol drive sheet.pdf`` in this repository.

This module is data-only. It does not grade, score, or judge anything.
The grader (``opendrive_clipboard.grader``) consumes these constants to draft
a 1-4 rating per skill row, and the licensed instructor reviews the draft
before any record becomes official. Nothing in this module short-circuits
the human review gate documented in ``docs/BOUNDARY.md``.

Synthetic-only: there is no real student data here. There is no audio,
no microphone, no cabin recording anywhere in OpenDrive.
"""

from __future__ import annotations

from copy import deepcopy


RATING_SCALE: dict[int, dict] = {
    1: {
        "value": 1,
        "label": "Potential danger",
        "description": (
            "Requires physical intervention by the instructor due to unsafe actions."
        ),
    },
    2: {
        "value": 2,
        "label": "Needs improvement",
        "description": (
            "Lacks necessary skills or knowledge; coaching is required, and best "
            "practices are not being followed."
        ),
    },
    3: {
        "value": 3,
        "label": "Developing",
        "description": (
            "Some coaching is needed; follows the rules of the road but does not "
            "consistently use best practices."
        ),
    },
    4: {
        "value": 4,
        "label": "Meets standard",
        "description": (
            "Minimal coaching is required; follows the rules of the road and "
            "often uses best practices."
        ),
    },
}


REACTION_TO_COACHING: tuple[str, ...] = ("needs_improvement", "good", "excellent")


# DOL_SKILLS preserves the exact form ordering from pages 2-6 of DTS-661-047.
# Each row records:
#   id              - stable snake_case key used by the grader and UI
#   label           - exact form wording (kept verbatim from the PDF)
#   group           - logical section heading for the UI
#   telemetry       - Beacon-derived signal hints the grader looks at
#   event_patterns  - synthetic scenario event.pattern values that map here
DOL_SKILLS: list[dict] = [
    # --- Pre-drive (page 2)
    {
        "id": "perform_pre_drive_check",
        "label": "Perform a pre-drive check",
        "group": "Pre-drive",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "familiarize_with_vehicle",
        "label": "Familiarize yourself with the vehicle",
        "group": "Pre-drive",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "use_hand_signals",
        "label": "Use hand signals",
        "group": "Pre-drive",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "start_the_vehicle",
        "label": "Start the vehicle",
        "group": "Pre-drive",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "hands_on_steering_wheel",
        "label": "Place hands on the steering wheel",
        "group": "Pre-drive",
        "telemetry": ["steering_deg"],
        "event_patterns": [],
    },
    # --- Basic control (page 3)
    {
        "id": "move_from_a_stop",
        "label": "Move from a stop",
        "group": "Basic control",
        "telemetry": ["speed_mph", "throttle_pct"],
        "event_patterns": [],
    },
    {
        "id": "control_steering",
        "label": "Control steering",
        "group": "Basic control",
        "telemetry": ["steering_deg", "yaw_rate"],
        "event_patterns": [],
    },
    {
        "id": "use_signaling_and_mirrors",
        "label": "Use signaling and mirrors",
        "group": "Basic control",
        "telemetry": ["mirror_cadence_per_min"],
        "event_patterns": ["visual_search"],
    },
    {
        "id": "check_blind_spots",
        "label": "Check blind spots",
        "group": "Basic control",
        "telemetry": ["mirror_cadence_per_min"],
        "event_patterns": ["visual_search"],
    },
    {
        "id": "position_vehicle_in_lane",
        "label": "Position the vehicle in the lane",
        "group": "Basic control",
        "telemetry": ["lane_position_variance"],
        "event_patterns": [],
    },
    {
        "id": "make_right_and_left_turns",
        "label": "Make right and left turns",
        "group": "Basic control",
        "telemetry": ["yaw_rate", "lat_accel"],
        "event_patterns": [],
    },
    {
        "id": "stop_the_vehicle",
        "label": "Stop the vehicle",
        "group": "Basic control",
        "telemetry": ["brake_pct", "smooth_braking_score"],
        "event_patterns": ["speed_management", "decision_recovery"],
    },
    {
        "id": "pull_to_curb_and_park",
        "label": "Pull to the curb and park",
        "group": "Basic control",
        "telemetry": ["speed_mph", "steering_deg"],
        "event_patterns": [],
    },
    {
        "id": "use_reference_points",
        "label": "Use reference points",
        "group": "Basic control",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "reverse_the_vehicle",
        "label": "Reverse the vehicle",
        "group": "Basic control",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "pull_into_parking_stall",
        "label": "Pull into a parking stall",
        "group": "Basic control",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "stop_at_stop_signs",
        "label": "Stop at stop signs",
        "group": "Basic control",
        "telemetry": ["brake_pct", "speed_mph"],
        "event_patterns": [],
    },
    {
        "id": "follow_traffic_lights",
        "label": "Follow traffic lights",
        "group": "Basic control",
        "telemetry": ["speed_mph", "brake_pct"],
        "event_patterns": ["intersection_search", "decision_recovery"],
    },
    # --- Roadway behavior (page 4)
    {
        "id": "control_speed",
        "label": "Control speed",
        "group": "Roadway behavior",
        "telemetry": ["speed_mph", "throttle_smoothness"],
        "event_patterns": ["speed_management"],
    },
    {
        "id": "scan_the_road",
        "label": "Scan the road",
        "group": "Roadway behavior",
        "telemetry": ["mirror_cadence_per_min"],
        "event_patterns": ["visual_search", "intersection_search"],
    },
    {
        "id": "maintain_lane_control",
        "label": "Maintain lane control",
        "group": "Roadway behavior",
        "telemetry": ["lane_position_variance", "steering_deg"],
        "event_patterns": [],
    },
    {
        "id": "keep_safe_following_distance",
        "label": "Keep a safe following distance",
        "group": "Roadway behavior",
        "telemetry": ["mean_following_distance_s"],
        "event_patterns": ["space_management"],
    },
    {
        "id": "follow_traffic_signs",
        "label": "Follow traffic signs",
        "group": "Roadway behavior",
        "telemetry": ["speed_mph"],
        "event_patterns": [],
    },
    {
        "id": "manage_space",
        "label": "Manage space",
        "group": "Roadway behavior",
        "telemetry": ["mean_following_distance_s", "lane_position_variance"],
        "event_patterns": ["space_management"],
    },
    {
        "id": "practice_commentary_driving",
        "label": "Practice commentary driving",
        "group": "Roadway behavior",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "yield_to_pedestrians",
        "label": "Yield to pedestrians",
        "group": "Roadway behavior",
        "telemetry": ["brake_pct"],
        "event_patterns": [],
    },
    {
        "id": "perform_angled_parking",
        "label": "Perform angled parking",
        "group": "Roadway behavior",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "right_turns_from_stop",
        "label": "Make right turns from a stop",
        "group": "Roadway behavior",
        "telemetry": ["yaw_rate", "lat_accel"],
        "event_patterns": [],
    },
    {
        "id": "right_turns_while_moving",
        "label": "Make right turns while moving",
        "group": "Roadway behavior",
        "telemetry": ["yaw_rate", "lat_accel"],
        "event_patterns": [],
    },
    {
        "id": "left_turns_from_stop",
        "label": "Make left turns from a stop",
        "group": "Roadway behavior",
        "telemetry": ["yaw_rate", "lat_accel"],
        "event_patterns": [],
    },
    {
        "id": "left_turns_while_moving",
        "label": "Make left turns while moving",
        "group": "Roadway behavior",
        "telemetry": ["yaw_rate", "lat_accel"],
        "event_patterns": [],
    },
    # --- Special conditions / advanced (page 5)
    {
        "id": "maintain_line_of_sight",
        "label": "Maintain line of sight",
        "group": "Special conditions",
        "telemetry": [],
        "event_patterns": ["visual_search"],
    },
    {
        "id": "follow_path_of_travel",
        "label": "Follow the path of travel",
        "group": "Special conditions",
        "telemetry": ["lane_position_variance"],
        "event_patterns": [],
    },
    {
        "id": "handle_special_driving_conditions",
        "label": "Handle special driving conditions",
        "group": "Special conditions",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "navigate_roundabouts",
        "label": "Navigate roundabouts",
        "group": "Special conditions",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "park_on_a_hill",
        "label": "Park on a hill",
        "group": "Special conditions",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "back_around_a_corner",
        "label": "Back around a corner",
        "group": "Special conditions",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "perform_u_turns_and_turnabouts",
        "label": "Perform U-turns and turnabouts",
        "group": "Special conditions",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "parallel_park",
        "label": "Parallel park",
        "group": "Special conditions",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "highway_following_distance",
        "label": "Maintain following distance on the highway",
        "group": "Highway",
        "telemetry": ["mean_following_distance_s"],
        "event_patterns": ["space_management"],
    },
    {
        "id": "highway_mirror_checks",
        "label": "Perform mirror checks on the highway",
        "group": "Highway",
        "telemetry": ["mirror_cadence_per_min"],
        "event_patterns": ["visual_search"],
    },
    {
        "id": "highway_scan_the_road",
        "label": "Scan the road on the highway",
        "group": "Highway",
        "telemetry": ["mirror_cadence_per_min"],
        "event_patterns": ["visual_search"],
    },
    {
        "id": "pass_other_vehicles",
        "label": "Pass other vehicles",
        "group": "Highway",
        "telemetry": ["speed_mph"],
        "event_patterns": [],
    },
    {
        "id": "on_off_ramps_merge",
        "label": "Navigate on and off ramps/merge",
        "group": "Highway",
        "telemetry": ["speed_mph", "lat_accel"],
        "event_patterns": [],
    },
    # --- Highway closeout + reflection (page 6)
    {
        "id": "manage_highway_hypnosis",
        "label": "Manage highway hypnosis",
        "group": "Highway",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "highway_control_speed",
        "label": "Control speed (highway)",
        "group": "Highway",
        "telemetry": ["speed_mph", "throttle_smoothness"],
        "event_patterns": ["speed_management"],
    },
    {
        "id": "maintain_stopping_distance",
        "label": "Maintain stopping distance",
        "group": "Highway",
        "telemetry": ["mean_following_distance_s", "brake_pct"],
        "event_patterns": ["space_management"],
    },
    {
        "id": "highway_check_blind_spots",
        "label": "Check blind spots on the highway",
        "group": "Highway",
        "telemetry": ["mirror_cadence_per_min"],
        "event_patterns": ["visual_search"],
    },
    {
        "id": "highway_use_signals",
        "label": "Use signals on the highway",
        "group": "Highway",
        "telemetry": [],
        "event_patterns": [],
    },
    {
        "id": "self_reflect_on_driving",
        "label": "Self-reflect on driving",
        "group": "Reflection",
        "telemetry": [],
        "event_patterns": ["calm_recovery"],
    },
    {
        "id": "identify_continued_areas_for_improvement",
        "label": "Identify continued areas for improvement",
        "group": "Reflection",
        "telemetry": [],
        "event_patterns": ["calm_recovery", "decision_recovery"],
    },
]


def dol_skills() -> list[dict]:
    """Return a deep copy of the canonical DOL skill rows (preserves form order)."""

    return deepcopy(DOL_SKILLS)


def rating_scale() -> dict[int, dict]:
    """Return a deep copy of the DOL 1-4 rating rubric."""

    return deepcopy(RATING_SCALE)


def pattern_to_skills(pattern: str) -> list[str]:
    """Map a scenario ``event.pattern`` value to matching DOL skill ids.

    Used by the grader to translate the synthetic scenario vocabulary
    (``space_management``, ``visual_search``, ``intersection_search``,
    ``speed_management``, ``calm_recovery``, ``decision_recovery``)
    into the official WA DOL skill rows on form DTS-661-047.
    """

    return [skill["id"] for skill in DOL_SKILLS if pattern in skill["event_patterns"]]


def skill_groups() -> list[str]:
    """Return the ordered list of unique skill groups for UI sectioning."""

    seen: list[str] = []
    for skill in DOL_SKILLS:
        if skill["group"] not in seen:
            seen.append(skill["group"])

    return seen
