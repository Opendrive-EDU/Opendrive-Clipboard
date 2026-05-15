"""Agent-like workflow for the OpenDrive Clipboard judge demo."""

from __future__ import annotations

import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from opendrive_clipboard.store import DemoStore
from opendrive_clipboard.tools import (
    CurriculumTools,
    DriveContextTools,
    DriveSheetTools,
    InstructorReviewTools,
)


@dataclass(frozen=True)
class TraceEntry:
    agent: str
    tool: str
    action: str
    detail: str

    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "tool": self.tool,
            "action": self.action,
            "detail": self.detail,
        }


class ScenarioIntakeAgent:
    def __init__(self, tools: DriveContextTools) -> None:
        self.tools = tools

    def run(self, scenario_id: str) -> tuple[dict, list[TraceEntry]]:
        scenario = self.tools.get_demo_drive(scenario_id)
        events = self.tools.get_intervention_events(scenario_id)
        scenario["events"] = events

        return scenario, [
            TraceEntry(
                "Scenario Intake Agent",
                "drive_context.get_demo_drive",
                "read",
                f"Loaded synthetic scenario '{scenario['title']}'.",
            ),
            TraceEntry(
                "Scenario Intake Agent",
                "drive_context.get_intervention_events",
                "read",
                f"Loaded {len(events)} fake OpenDrive Beacon-like events.",
            ),
        ]


class CurriculumRetrievalAgent:
    def __init__(self, tools: CurriculumTools) -> None:
        self.tools = tools

    def run(self, scenario: dict) -> tuple[list[dict], list[TraceEntry]]:
        topics = list(dict.fromkeys(event["pattern"] for event in scenario["events"]))
        snippets = [self.tools.lookup_lesson(topic) for topic in topics]

        return snippets, [
            TraceEntry(
                "Curriculum Retrieval Agent",
                "curriculum.lookup_lesson",
                "ground",
                f"Retrieved {len(snippets)} reviewed curriculum snippets.",
            )
        ]


class DraftAssemblyAgent:
    def __init__(self, provider: "DraftProvider") -> None:
        self.provider = provider

    def run(
        self,
        scenario: dict,
        curriculum: list[dict],
        instructor_notes: str,
    ) -> tuple[dict, list[TraceEntry]]:
        draft = self.provider.compose(scenario, curriculum, instructor_notes)

        return draft, [
            TraceEntry(
                "Draft Assembly Agent",
                self.provider.tool_name,
                "draft",
                "Assembled debrief artifacts for instructor review.",
            )
        ]


class ReviewGateAgent:
    def __init__(self, tools: InstructorReviewTools) -> None:
        self.tools = tools

    def run(self, draft_payload: dict) -> tuple[dict, list[TraceEntry]]:
        draft = self.tools.create_draft(draft_payload)
        submitted = self.tools.submit_for_instructor_review(draft["id"])

        return submitted, [
            TraceEntry(
                "Review Gate Agent",
                "review.create_draft",
                "create_demo_draft",
                "Created demo-only draft record.",
            ),
            TraceEntry(
                "Review Gate Agent",
                "review.submit_for_review",
                "block",
                "Stopped at the licensed instructor review gate.",
            ),
        ]


class DraftProvider:
    tool_name = "draft.local_template"

    def compose(
        self,
        scenario: dict,
        curriculum: list[dict],
        instructor_notes: str,
    ) -> dict:
        raise NotImplementedError


class LocalDraftProvider(DraftProvider):
    """Deterministic fallback used for local tests and no-secret demos."""

    tool_name = "draft.local_template"

    def compose(
        self,
        scenario: dict,
        curriculum: list[dict],
        instructor_notes: str,
    ) -> dict:
        primary = curriculum[0]
        notes = instructor_notes.strip() or scenario["instructor_notes"]
        standards = [snippet["standard"] for snippet in curriculum]

        return {
            "status_label": "DRAFT - INSTRUCTOR REVIEW REQUIRED",
            "headline": f"Post-drive debrief: {scenario['title']}",
            "safety_summary": (
                f"This fake drive centered on {scenario['focus']} "
                f"The instructor note was: {notes}"
            ),
            "observed_concern": scenario["events"][0]["observation"],
            "lesson_focus": primary["lesson"],
            "grounded_standards": standards,
            "reflection_prompt": primary["reflection_template"],
            "practice_assignment": (
                "On the next drive, repeat the same situation at lower workload. "
                "Ask the learner to name what they see, what could change, and "
                "how much space they want before the instructor prompts."
            ),
            "family_summary": (
                "Practice calm commentary driving on familiar streets. The learner "
                "should describe search, speed, and space choices before each adjustment."
            ),
            "language_access_preview": (
                "Vista previa: practiquen comentarios en voz alta sobre busqueda, "
                "velocidad y espacio. El instructor debe revisar antes de compartir."
            ),
            "official_record_mode": "demo_only_no_lms_or_dol_writes",
            "instructor_review_required": True,
        }


class GeminiDraftProvider(LocalDraftProvider):
    """Optional Gemini-backed provider.

    It is disabled unless OPENDRIVE_CLIPBOARD_ENABLE_GEMINI=true and an API key
    is present. The deterministic local provider remains the default so tests
    and judge dry-runs never depend on network access.
    """

    @property
    def tool_name(self) -> str:
        # Trace should reflect what actually fires, not which class wraps the call.
        if os.getenv("OPENDRIVE_CLIPBOARD_ENABLE_GEMINI") != "true":
            return "draft.local_template"
        if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
            return "draft.local_template"
        return "draft.gemini_api_optional"

    def compose(
        self,
        scenario: dict,
        curriculum: list[dict],
        instructor_notes: str,
    ) -> dict:
        if os.getenv("OPENDRIVE_CLIPBOARD_ENABLE_GEMINI") != "true":
            return super().compose(scenario, curriculum, instructor_notes)

        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return super().compose(scenario, curriculum, instructor_notes)

        prompt = self._prompt(scenario, curriculum, instructor_notes)
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-2.5-flash:generateContent?key="
            f"{api_key}"
        )
        body = (
            '{"contents":[{"parts":[{"text":'
            + json_escape(prompt)
            + '}]}],"generationConfig":{"temperature":0.2}}'
        ).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                text = response.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError):
            return super().compose(scenario, curriculum, instructor_notes)

        draft = super().compose(scenario, curriculum, instructor_notes)
        draft["gemini_raw_preview"] = text[:1200]
        draft["draft_provider"] = "gemini_api_optional"

        return draft

    def _prompt(self, scenario: dict, curriculum: list[dict], instructor_notes: str) -> str:
        standards = "\n".join(f"- {snippet['standard']}" for snippet in curriculum)

        return (
            "Create a concise, respectful post-drive debrief draft for a licensed "
            "driving instructor to review. Do not make official records. Mark every output "
            "as DRAFT - INSTRUCTOR REVIEW REQUIRED.\n\n"
            f"Scenario: {scenario['title']}\n"
            f"Focus: {scenario['focus']}\n"
            f"Instructor notes: {instructor_notes or scenario['instructor_notes']}\n"
            f"Grounding:\n{standards}\n"
        )


class DriveSheetGraderAgent:
    """Drafts a DOL-aligned drive report for instructor review."""

    def __init__(self, tools: DriveSheetTools) -> None:
        self.tools = tools

    def run(self, scenario_id: str) -> tuple[dict, list[TraceEntry]]:
        report = self.tools.draft_drive_report(scenario_id)

        return report, [
            TraceEntry(
                "Drive Sheet Grader Agent",
                "drive_sheet.draft_drive_report",
                "draft",
                "Drafted WA DOL DTS-661-047 ratings + Driver Health Panel + report. "
                "Awaiting licensed instructor review.",
            )
        ]


class ClipboardRunner:
    """Coordinates the synthetic multi-agent OpenDrive Clipboard workflow."""

    def __init__(
        self,
        store: DemoStore | None = None,
        draft_provider: DraftProvider | None = None,
    ) -> None:
        self.store = store or DemoStore()
        drive_tools = DriveContextTools(self.store)
        curriculum_tools = CurriculumTools(self.store)
        review_tools = InstructorReviewTools(self.store)
        drive_sheet_tools = DriveSheetTools(self.store)

        self.scenario_intake = ScenarioIntakeAgent(drive_tools)
        self.curriculum_retrieval = CurriculumRetrievalAgent(curriculum_tools)
        self.draft_assembly = DraftAssemblyAgent(draft_provider or GeminiDraftProvider())
        self.review_gate = ReviewGateAgent(review_tools)
        self.drive_sheet_grader = DriveSheetGraderAgent(drive_sheet_tools)

    def run(self, scenario_id: str, instructor_notes: str = "") -> dict:
        trace: list[TraceEntry] = []

        scenario, entries = self.scenario_intake.run(scenario_id)
        trace.extend(entries)

        curriculum, entries = self.curriculum_retrieval.run(scenario)
        trace.extend(entries)

        draft_payload, entries = self.draft_assembly.run(
            scenario,
            curriculum,
            instructor_notes,
        )
        trace.extend(entries)

        draft, entries = self.review_gate.run(draft_payload)
        trace.extend(entries)

        drive_report, entries = self.drive_sheet_grader.run(scenario_id)
        trace.extend(entries)

        run = self.store.create_run(
            {
                "scenario": scenario,
                "curriculum": curriculum,
                "draft": draft,
                "drive_report": drive_report,
                "trace": [entry.to_dict() for entry in trace],
                "safety_boundary": {
                    "demo_only_no_real_beacon_data": True,
                    "no_external_ai_calls_by_default": True,
                    "instructor_review_required": True,
                    "no_official_lms_or_dol_writes": True,
                },
            }
        )

        return run


def json_escape(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
