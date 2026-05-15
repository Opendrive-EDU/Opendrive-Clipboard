"""In-memory synthetic store for the OpenDrive Clipboard demo."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from opendrive_clipboard.demo_data import (
    curriculum_snippets,
    demo_scenarios,
    language_access_glossary,
)


class DemoStore:
    """Holds synthetic scenarios, drafts, runs, and review decisions."""

    def __init__(self) -> None:
        self.scenarios = demo_scenarios()
        self.curriculum = curriculum_snippets()
        self.glossary = language_access_glossary()
        self.runs: dict[str, dict] = {}
        self.drafts: dict[str, dict] = {}
        self.drive_reports: dict[str, dict] = {}

    def list_scenarios(self) -> list[dict]:
        return [
            {
                "id": scenario["id"],
                "title": scenario["title"],
                "focus": scenario["focus"],
                "route": scenario["route"],
                "conditions": scenario["conditions"],
            }
            for scenario in self.scenarios.values()
        ]

    def get_scenario(self, scenario_id: str) -> dict:
        try:
            return deepcopy(self.scenarios[scenario_id])
        except KeyError as exc:
            raise ValueError(f"Unknown demo scenario: {scenario_id}") from exc

    def get_curriculum(self, topic: str) -> dict:
        try:
            return deepcopy(self.curriculum[topic])
        except KeyError as exc:
            raise ValueError(f"Unknown curriculum topic: {topic}") from exc

    def create_draft(self, draft: dict) -> dict:
        draft_id = f"draft-{uuid4().hex[:10]}"
        record = {
            **deepcopy(draft),
            "id": draft_id,
            "status": "draft_review_required",
            "status_label": "DRAFT - INSTRUCTOR REVIEW REQUIRED",
            "review_decision": None,
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        self.drafts[draft_id] = record

        return deepcopy(record)

    def submit_for_review(self, draft_id: str) -> dict:
        draft = self._draft(draft_id)
        draft["status"] = "submitted_for_instructor_review"
        draft["status_label"] = "DRAFT - INSTRUCTOR REVIEW REQUIRED"
        draft["updated_at"] = now_iso()
        self.drafts[draft_id] = draft

        return deepcopy(draft)

    def record_decision(self, draft_id: str, decision: str) -> dict:
        allowed = {"approve", "edit", "reject", "regenerate"}
        if decision not in allowed:
            raise ValueError(f"Unsupported review decision: {decision}")

        draft = self._draft(draft_id)
        draft["review_decision"] = decision
        draft["status"] = f"preview_{decision}"
        draft["updated_at"] = now_iso()
        self.drafts[draft_id] = draft

        return deepcopy(draft)

    def create_run(self, run: dict) -> dict:
        run_id = f"run-{uuid4().hex[:10]}"
        record = {
            **deepcopy(run),
            "id": run_id,
            "created_at": now_iso(),
        }
        self.runs[run_id] = record

        return deepcopy(record)

    def get_run(self, run_id: str) -> dict:
        try:
            return deepcopy(self.runs[run_id])
        except KeyError as exc:
            raise ValueError(f"Unknown demo run: {run_id}") from exc

    def save_drive_report(self, report: dict) -> dict:
        report_id = f"drive-report-{uuid4().hex[:10]}"
        record = {
            **deepcopy(report),
            "id": report_id,
            "review_decision": None,
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        self.drive_reports[report_id] = record

        return deepcopy(record)

    def get_drive_report(self, report_id: str) -> dict:
        try:
            return deepcopy(self.drive_reports[report_id])
        except KeyError as exc:
            raise ValueError(f"Unknown drive report: {report_id}") from exc

    def record_drive_report_decision(self, report_id: str, decision: str) -> dict:
        allowed = {"approve", "edit", "reject", "regenerate"}
        if decision not in allowed:
            raise ValueError(f"Unsupported review decision: {decision}")

        report = self.get_drive_report(report_id)
        report["review_decision"] = decision
        report["status"] = f"preview_{decision}"
        if decision == "approve":
            report["status_label"] = "INSTRUCTOR APPROVED - DRAFT"
        report["updated_at"] = now_iso()
        self.drive_reports[report_id] = report

        return deepcopy(report)

    def get_draft(self, draft_id: str) -> dict:
        return self._draft(draft_id)

    def mark_drive_report_audio(self, report_id: str) -> None:
        try:
            self.drive_reports[report_id]["has_audio"] = True
        except KeyError as exc:
            raise ValueError(f"Unknown drive report: {report_id}") from exc

    def _draft(self, draft_id: str) -> dict:
        try:
            return deepcopy(self.drafts[draft_id])
        except KeyError as exc:
            raise ValueError(f"Unknown draft: {draft_id}") from exc


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
