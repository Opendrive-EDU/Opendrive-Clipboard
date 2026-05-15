"""Synthetic-only demo data for OpenDrive Clipboard.

The public challenge package must not include live student records, real
OpenDrive Beacon telemetry, production secrets, or private school data.

The demo models a six-lesson WA behind-the-wheel course: Drive 1 through
Drive 6, each a one-hour lesson, following a realistic instructor-led
progression (basic control -> residential -> arterials -> higher speed ->
freeway -> independent review). Event ``pattern`` values are drawn only
from the six patterns the DOL drive-sheet grader recognizes
(``opendrive_clipboard.dol_sheet``): ``visual_search``,
``space_management``, ``calm_recovery``, ``decision_recovery``,
``intersection_search``, ``speed_management``. Events flagged
``"intervention": True`` represent a moment the licensed instructor had to
verbally intervene; everything else is an observed teachable moment.
"""

from __future__ import annotations

from copy import deepcopy


# Lesson length for every drive in this synthetic course (minutes).
LESSON_MINUTES: int = 60


DEMO_SCENARIOS: dict[str, dict] = {
    "drive-1": {
        "id": "drive-1",
        "title": "Drive 1 — Vehicle Familiarization & Basic Control (1-hour lesson)",
        "student": "Demo learner",
        "instructor": "Licensed instructor",
        "vehicle": "Training vehicle placeholder",
        "duration_min": LESSON_MINUTES,
        "competence": 0.3,  # 0=rough .. 1=polished; drives the synthetic improvement arc
        "route": "Closed training lot and a quiet residential block",
        "conditions": "Daylight, dry pavement, empty lot then low-traffic street",
        "focus": "Cockpit setup, smooth starting and stopping, basic steering, and a mirror habit.",
        "instructor_notes": (
            "First behind-the-wheel hour. Learner completed the cockpit drill "
            "and the basic control set; steering inputs smoothed by the end of "
            "the lesson after one prompted reset."
        ),
        "events": [
            {
                "time": "02:30",
                "signal": "Mirror and seat setup",
                "observation": "Mirrors set after a reminder of the pre-drive sequence.",
                "pattern": "visual_search",
            },
            {
                "time": "11:15",
                "signal": "Smooth acceleration",
                "observation": "Gradual acceleration from a stop on the lot straight.",
                "pattern": "speed_management",
            },
            {
                "time": "19:40",
                "signal": "Controlled braking",
                "observation": "Braked early and smoothly to a marked stop.",
                "pattern": "speed_management",
            },
            {
                "time": "28:05",
                "signal": "Steering control",
                "observation": "Wide line on the oval, recovered without overcorrection.",
                "pattern": "calm_recovery",
            },
            {
                "time": "41:20",
                "signal": "First quiet-street stop sign",
                "observation": "Full stop and search at a low-traffic four-way.",
                "pattern": "intersection_search",
            },
            {
                "time": "54:50",
                "signal": "Calm reset after early brake",
                "observation": "Reset posture and attention after a prompted slow-down.",
                "pattern": "calm_recovery",
                "intervention": True,
            },
        ],
    },
    "drive-2": {
        "id": "drive-2",
        "title": "Drive 2 — Residential Streets & Basic Intersections (1-hour lesson)",
        "student": "Demo learner",
        "instructor": "Licensed instructor",
        "vehicle": "Training vehicle placeholder",
        "duration_min": LESSON_MINUTES,
        "competence": 0.45,  # 0=rough .. 1=polished; drives the synthetic improvement arc
        "route": "Residential grid with four-way stops into a low-speed collector",
        "conditions": "Daylight, dry pavement, light neighborhood traffic",
        "focus": "Intersection search, turn execution, lane position, and following distance.",
        "instructor_notes": (
            "Second hour on quiet residential streets. Turn execution improving; "
            "following distance opened after one prompt near a parked-car pull-out."
        ),
        "events": [
            {
                "time": "03:10",
                "signal": "Four-way stop approach",
                "observation": "Searched left-right-left before proceeding.",
                "pattern": "intersection_search",
            },
            {
                "time": "12:25",
                "signal": "Right turn lane position",
                "observation": "Held a tidy lane position through the turn.",
                "pattern": "visual_search",
            },
            {
                "time": "21:50",
                "signal": "Following distance",
                "observation": "Closed space behind a delivery vehicle pulling out.",
                "pattern": "space_management",
                "intervention": True,
            },
            {
                "time": "30:15",
                "signal": "Left turn gap judgment",
                "observation": "Accepted a safe gap after a brief hesitation.",
                "pattern": "decision_recovery",
            },
            {
                "time": "39:40",
                "signal": "Speed creep downhill",
                "observation": "Speed drifted up on a downhill block, eased off after a glance at the speedometer.",
                "pattern": "speed_management",
            },
            {
                "time": "48:05",
                "signal": "Mirror check before lane shift",
                "observation": "Mirror and shoulder check before repositioning.",
                "pattern": "visual_search",
            },
            {
                "time": "57:20",
                "signal": "Calm recovery",
                "observation": "Settled quickly after a prompted slow-down.",
                "pattern": "calm_recovery",
            },
        ],
    },
    "drive-3": {
        "id": "drive-3",
        "title": "Drive 3 — Arterials & Lane Changes (1-hour lesson)",
        "student": "Demo learner",
        "instructor": "Licensed instructor",
        "vehicle": "Training vehicle placeholder",
        "duration_min": LESSON_MINUTES,
        "competence": 0.5,  # 0=rough .. 1=polished; drives the synthetic improvement arc
        "route": "Multi-lane arterial with signal-controlled intersections",
        "conditions": "Cloudy, dry pavement, moderate arterial traffic",
        "focus": "Lane changes, blind-spot habit, signal timing, and speed matching.",
        "instructor_notes": (
            "Busiest environment so far. Two interventions on a late mirror "
            "before a lane change and a yellow-light decision; calm recovery held."
        ),
        "events": [
            {
                "time": "02:45",
                "signal": "Signal timing read",
                "observation": "Noticed a stale green and prepared to stop.",
                "pattern": "intersection_search",
            },
            {
                "time": "10:30",
                "signal": "Lane change blind-spot check",
                "observation": "Mirror and shoulder check before the first lane change.",
                "pattern": "visual_search",
            },
            {
                "time": "19:05",
                "signal": "Speed match into faster lane",
                "observation": "Matched the speed of the lane before moving over.",
                "pattern": "speed_management",
            },
            {
                "time": "27:40",
                "signal": "Following distance reset",
                "observation": "Reopened space after traffic compressed.",
                "pattern": "space_management",
            },
            {
                "time": "36:15",
                "signal": "Late mirror before second lane change",
                "observation": "Mirror check came late; corrected after a prompt.",
                "pattern": "visual_search",
                "intervention": True,
            },
            {
                "time": "45:50",
                "signal": "Yellow-light decision",
                "observation": "Carried speed toward a yellow; stopped smoothly on cue.",
                "pattern": "decision_recovery",
                "intervention": True,
            },
            {
                "time": "56:10",
                "signal": "Calm reset after busy stretch",
                "observation": "Attention returned to the driving task without lingering on the correction.",
                "pattern": "calm_recovery",
            },
        ],
    },
    "drive-4": {
        "id": "drive-4",
        "title": "Drive 4 — Higher-Speed Roads & Hazard Recognition (1-hour lesson)",
        "student": "Demo learner",
        "instructor": "Licensed instructor",
        "vehicle": "Training vehicle placeholder",
        "duration_min": LESSON_MINUTES,
        "competence": 0.66,  # 0=rough .. 1=polished; drives the synthetic improvement arc
        "route": "Rural highway connector and a higher-speed arterial",
        "conditions": "Daylight, dry pavement, steady higher-speed traffic",
        "focus": "Following distance at speed, hazard scanning, curve speed, and lane discipline.",
        "instructor_notes": (
            "Higher speeds handled with growing confidence. One prompt to "
            "rebuild the space cushion behind a truck; hazard scanning solid."
        ),
        "events": [
            {
                "time": "03:55",
                "signal": "Following distance at 45 mph",
                "observation": "Held a steady gap on the connector.",
                "pattern": "space_management",
            },
            {
                "time": "13:20",
                "signal": "Hazard scan",
                "observation": "Identified a pedestrian on the shoulder early.",
                "pattern": "visual_search",
            },
            {
                "time": "22:45",
                "signal": "Curve entry speed",
                "observation": "Eased off before the curve, smooth through the apex.",
                "pattern": "speed_management",
            },
            {
                "time": "32:10",
                "signal": "Space cushion behind truck",
                "observation": "Cushion shrank behind a slowing truck; rebuilt after a prompt.",
                "pattern": "space_management",
                "intervention": True,
            },
            {
                "time": "41:35",
                "signal": "Scan to crest of hill",
                "observation": "Searched the road to the crest before committing speed.",
                "pattern": "visual_search",
            },
            {
                "time": "50:00",
                "signal": "Hold-lane vs. pass decision",
                "observation": "Chose to hold the lane rather than a marginal pass.",
                "pattern": "decision_recovery",
            },
            {
                "time": "58:15",
                "signal": "Calm reset before return",
                "observation": "Relaxed grip and pace heading back toward town.",
                "pattern": "calm_recovery",
            },
        ],
    },
    "drive-5": {
        "id": "drive-5",
        "title": "Drive 5 — Freeway Entry, Merge & Exit (1-hour lesson)",
        "student": "Demo learner",
        "instructor": "Licensed instructor",
        "vehicle": "Training vehicle placeholder",
        "duration_min": LESSON_MINUTES,
        "competence": 0.78,  # 0=rough .. 1=polished; drives the synthetic improvement arc
        "route": "Interstate on-ramp, mainline, and exit sequence",
        "conditions": "Daylight, dry pavement, moderate freeway traffic",
        "focus": "Ramp acceleration, gap selection, merge, freeway scanning, and exit planning.",
        "instructor_notes": (
            "First full freeway hour. Two prompts — one on gap selection at the "
            "merge, one pacing the exit deceleration; both recovered calmly."
        ),
        "events": [
            {
                "time": "02:20",
                "signal": "Ramp acceleration",
                "observation": "Accelerated to merge speed along the on-ramp.",
                "pattern": "speed_management",
            },
            {
                "time": "09:45",
                "signal": "Gap selection for merge",
                "observation": "Hesitated on the gap; took the next one after a prompt.",
                "pattern": "decision_recovery",
                "intervention": True,
            },
            {
                "time": "17:10",
                "signal": "Mirror and blind-spot on merge",
                "observation": "Completed the mirror and blind-spot check entering the mainline.",
                "pattern": "visual_search",
            },
            {
                "time": "25:35",
                "signal": "Following distance at freeway speed",
                "observation": "Held a time gap appropriate for the speed.",
                "pattern": "space_management",
            },
            {
                "time": "34:00",
                "signal": "Lane discipline",
                "observation": "Kept right except to pass; signaled each move.",
                "pattern": "visual_search",
            },
            {
                "time": "42:25",
                "signal": "Speed management in flow",
                "observation": "Matched the flow of traffic without surging.",
                "pattern": "speed_management",
            },
            {
                "time": "50:50",
                "signal": "Exit planning",
                "observation": "Late to begin deceleration for the exit; paced it after a prompt.",
                "pattern": "decision_recovery",
                "intervention": True,
            },
            {
                "time": "58:30",
                "signal": "Calm reset on surface street",
                "observation": "Down-shifted attention smoothly back to surface speeds.",
                "pattern": "calm_recovery",
            },
        ],
    },
    "drive-6": {
        "id": "drive-6",
        "title": "Drive 6 — Mixed Environment & Independent Review (1-hour lesson)",
        "student": "Demo learner",
        "instructor": "Licensed instructor",
        "vehicle": "Training vehicle placeholder",
        "duration_min": LESSON_MINUTES,
        "competence": 0.93,  # 0=rough .. 1=polished; drives the synthetic improvement arc
        "route": "Independent route: residential, arterial, and a short freeway loop",
        "conditions": "Daylight, dry pavement, mixed traffic, student-led navigation",
        "focus": "Independent decision-making, commentary-driving practice, and calm self-correction.",
        "instructor_notes": (
            "Review hour with student-led navigation and commentary-driving "
            "practice. No interventions required; self-corrections were timely."
        ),
        "events": [
            {
                "time": "03:30",
                "signal": "Commentary-driving practice",
                "observation": "Began narrating hazards and intentions on request.",
                "pattern": "visual_search",
            },
            {
                "time": "12:55",
                "signal": "Independent intersection decision",
                "observation": "Read and cleared a complex intersection without prompting.",
                "pattern": "intersection_search",
            },
            {
                "time": "22:20",
                "signal": "Self-corrected following distance",
                "observation": "Noticed a shrinking gap and rebuilt it unprompted.",
                "pattern": "space_management",
            },
            {
                "time": "31:45",
                "signal": "Lane choice for upcoming turn",
                "observation": "Selected the correct lane well ahead of the turn.",
                "pattern": "decision_recovery",
            },
            {
                "time": "41:10",
                "signal": "School-zone speed adjustment",
                "observation": "Reduced speed appropriately entering a school zone.",
                "pattern": "speed_management",
            },
            {
                "time": "50:35",
                "signal": "Calm self-correction",
                "observation": "Adjusted a wide line calmly with no instructor input.",
                "pattern": "calm_recovery",
            },
            {
                "time": "58:50",
                "signal": "Final reset and debrief handoff",
                "observation": "Settled the vehicle and transitioned to the post-drive debrief.",
                "pattern": "calm_recovery",
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
    "blind spot": "punto ciego",
    "lane change": "cambio de carril",
    "stop sign": "senal de alto",
    "merge": "incorporacion",
    "scan": "explorar visualmente",
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
