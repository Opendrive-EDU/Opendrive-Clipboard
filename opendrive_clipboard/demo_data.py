"""Synthetic-only demo data for OpenDrive Clipboard.

The public challenge package must not include live student records, real
OpenDrive Beacon telemetry, production secrets, or private school data.
"""

from __future__ import annotations

from copy import deepcopy


DEMO_SCENARIOS: dict[str, dict] = {
    "residential-following-distance": {
        "id": "residential-following-distance",
        "title": "Residential Following Distance Reset",
        "student": "Demo learner",
        "instructor": "Licensed instructor",
        "vehicle": "Training vehicle placeholder",
        "route": "Residential streets into a low-speed arterial merge",
        "conditions": "Daylight, dry pavement, moderate neighborhood traffic",
        "focus": "Following distance, mirror cadence, and calm correction after prompt.",
        "instructor_notes": (
            "Learner closed space behind a parked delivery vehicle, then recovered "
            "after the instructor prompted a mirror check and speed reset."
        ),
        "events": [
            {
                "time": "00:04",
                "signal": "Mirror cadence",
                "observation": "Late mirror check before the lane-position correction.",
                "pattern": "visual_search",
            },
            {
                "time": "00:12",
                "signal": "Following distance",
                "observation": "Space opened after a prompt near the arterial approach.",
                "pattern": "space_management",
            },
            {
                "time": "00:19",
                "signal": "Recovery after correction",
                "observation": "Learner reset posture and steering after a short debrief.",
                "pattern": "calm_recovery",
            },
        ],
    },
    "yellow-light-decision": {
        "id": "yellow-light-decision",
        "title": "Yellow Light Decision Review",
        "student": "Demo learner",
        "instructor": "Licensed instructor",
        "vehicle": "Training vehicle placeholder",
        "route": "Urban arterial with protected turn pockets",
        "conditions": "Cloudy afternoon, dry pavement, steady signal timing",
        "focus": "Decision point, speed adjustment, and early verbal risk naming.",
        "instructor_notes": (
            "Learner hesitated at a stale green, carried speed toward the yellow, "
            "then accepted the instructor cue to stop smoothly."
        ),
        "events": [
            {
                "time": "00:08",
                "signal": "Signal timing",
                "observation": "Learner noticed the stale green late.",
                "pattern": "intersection_search",
            },
            {
                "time": "00:11",
                "signal": "Speed choice",
                "observation": "Speed stayed high until the instructor cue.",
                "pattern": "speed_management",
            },
            {
                "time": "00:15",
                "signal": "Stop decision",
                "observation": "Learner stopped smoothly after the prompt.",
                "pattern": "decision_recovery",
            },
        ],
    },
}


CURRICULUM_SNIPPETS: dict[str, dict] = {
    "visual_search": {
        "topic": "visual_search",
        "lesson": "OpenDrive Live 30: Searching for Risk",
        "standard": "Use central, fringe, and peripheral vision to identify changing risk early.",
        "reflection_template": "What did you see first, and what would help you notice it sooner next time?",
    },
    "space_management": {
        "topic": "space_management",
        "lesson": "OpenDrive Live 30: Speed and Space",
        "standard": "Maintain time and space margins before traffic changes force a correction.",
        "reflection_template": "How much space did you want, and what told you it was time to create more?",
    },
    "calm_recovery": {
        "topic": "calm_recovery",
        "lesson": "OpenDrive Live 30: Responsible Driver Mindset",
        "standard": "Recover from corrections calmly and return attention to the driving task.",
        "reflection_template": "What helped you reset after the correction?",
    },
    "intersection_search": {
        "topic": "intersection_search",
        "lesson": "OpenDrive Live 30: Intersections",
        "standard": "Identify signal age, cross traffic, pedestrians, and stopping options before entering.",
        "reflection_template": "What clues told you the light might change?",
    },
    "speed_management": {
        "topic": "speed_management",
        "lesson": "OpenDrive Live 30: Speed and Momentum",
        "standard": "Adjust speed early enough to preserve a smooth stop or safe continuation.",
        "reflection_template": "When did you know you could still stop comfortably?",
    },
    "decision_recovery": {
        "topic": "decision_recovery",
        "lesson": "OpenDrive Live 30: Responsible Choices",
        "standard": "Make a safe decision, commit calmly, and avoid rushing under pressure.",
        "reflection_template": "What would make your next decision earlier and calmer?",
    },
}


LANGUAGE_ACCESS_GLOSSARY: dict[str, str] = {
    "following distance": "distancia de seguimiento",
    "mirror check": "revision de espejos",
    "space": "espacio",
    "slow down": "reducir la velocidad",
    "smooth stop": "parada suave",
}


def demo_scenarios() -> dict[str, dict]:
    """Return a copy of synthetic drive scenarios."""

    return deepcopy(DEMO_SCENARIOS)


def curriculum_snippets() -> dict[str, dict]:
    """Return a copy of reviewed curriculum snippets."""

    return deepcopy(CURRICULUM_SNIPPETS)


def language_access_glossary() -> dict[str, str]:
    """Return a copy of the demo language-access glossary."""

    return deepcopy(LANGUAGE_ACCESS_GLOSSARY)
