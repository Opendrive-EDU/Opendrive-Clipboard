"""MCP-style tool surfaces for the synthetic OpenDrive Clipboard demo."""

from __future__ import annotations

from copy import deepcopy

from opendrive_clipboard.grader import grade_drive
from opendrive_clipboard.store import DemoStore


FORBIDDEN_OFFICIAL_KEYS = {
    "attendance_credit",
    "certificate",
    "completion_record",
    "dol_submission",
    "driver_license",
    "lms_completion",
    "official_record",
    "pass_fail",
    "student_pii",
    "transcript",
}


class DriveContextTools:
    """Read synthetic OpenDrive Beacon-like scenario data."""

    def __init__(self, store: DemoStore) -> None:
        self.store = store

    def get_demo_drive(self, scenario_id: str) -> dict:
        scenario = self.store.get_scenario(scenario_id)
        guard_demo_payload(scenario)

        return scenario

    def get_intervention_events(self, session_id: str) -> list[dict]:
        scenario = self.store.get_scenario(session_id)

        return deepcopy(scenario["events"])


class CurriculumTools:
    """Ground draft language in reviewed curriculum snippets."""

    def __init__(self, store: DemoStore) -> None:
        self.store = store

    def lookup_lesson(self, topic: str) -> dict:
        return self.store.get_curriculum(topic)

    def get_standard(self, code: str) -> dict:
        return self.lookup_lesson(code)


class InstructorReviewTools:
    """Create and review demo-only OpenDrive Clipboard drafts."""

    def __init__(self, store: DemoStore) -> None:
        self.store = store

    def create_draft(self, payload: dict) -> dict:
        guard_demo_payload(payload)

        return self.store.create_draft(payload)

    def submit_for_instructor_review(self, draft_id: str) -> dict:
        return self.store.submit_for_review(draft_id)

    def record_instructor_decision(self, draft_id: str, decision: str) -> dict:
        return self.store.record_decision(draft_id, decision)


class DriveSheetTools:
    """Draft and review WA DOL drive-sheet artifacts (demo-only)."""

    def __init__(self, store: DemoStore) -> None:
        self.store = store

    def draft_drive_report(self, scenario_id: str) -> dict:
        report = grade_drive(scenario_id)
        guard_demo_payload(report)

        return self.store.save_drive_report(report)

    def record_drive_report_decision(self, report_id: str, decision: str) -> dict:
        return self.store.record_drive_report_decision(report_id, decision)


def guard_demo_payload(payload: object) -> None:
    """Reject payloads that try to smuggle official-record semantics."""

    if isinstance(payload, dict):
        for key, value in payload.items():
            normalized = str(key).lower()
            if normalized in FORBIDDEN_OFFICIAL_KEYS:
                raise ValueError(
                    "OpenDrive Clipboard demo cannot create official LMS, "
                    "licensing, certificate, transcript, or DOL records."
                )
            guard_demo_payload(value)

    if isinstance(payload, list):
        for item in payload:
            guard_demo_payload(item)
