"""Tiny dependency-free HTTP server for the OpenDrive Clipboard demo."""

from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from opendrive_clipboard.agent import ClipboardRunner
from opendrive_clipboard.store import DemoStore
from opendrive_clipboard.tools import DriveSheetTools, InstructorReviewTools
from opendrive_clipboard.tts import synthesize


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web"


class ClipboardApp:
    def __init__(self) -> None:
        self.store = DemoStore()
        self.runner = ClipboardRunner(self.store)
        self.review_tools = InstructorReviewTools(self.store)
        self.drive_sheet_tools = DriveSheetTools(self.store)

    def list_scenarios(self) -> list[dict]:
        return self.store.list_scenarios()

    def create_run(self, payload: dict) -> dict:
        scenario_id = payload.get("scenario_id") or "drive-1"
        instructor_notes = payload.get("instructor_notes") or ""

        return self.runner.run(scenario_id, instructor_notes)

    def get_run(self, run_id: str) -> dict:
        return self.store.get_run(run_id)

    def review_draft(self, draft_id: str, payload: dict) -> dict:
        decision = payload.get("decision") or ""

        return self.review_tools.record_instructor_decision(draft_id, decision)

    def create_drive_report(self, payload: dict) -> dict:
        scenario_id = payload.get("scenario_id") or "drive-1"

        return self.drive_sheet_tools.draft_drive_report(scenario_id)

    def get_drive_report(self, report_id: str) -> dict:
        return self.store.get_drive_report(report_id)

    def review_drive_report(self, report_id: str, payload: dict) -> dict:
        decision = payload.get("decision") or ""

        return self.drive_sheet_tools.record_drive_report_decision(report_id, decision)

    def text_to_speech(self, payload: dict) -> dict:
        """Read back an instructor-APPROVED debrief as audio.

        The text is taken from the stored, approved artifact - never from the
        client - so audio can only ever voice what a licensed instructor signed
        off on. Youth Mode is reachable only through this same approval gate.
        """
        mode = payload.get("mode") or "professional"
        if mode not in {"professional", "youth"}:
            raise ValueError(f"Unsupported voice mode: {mode}")

        report_id = payload.get("report_id")
        draft_id = payload.get("draft_id")

        if report_id:
            item = self.store.get_drive_report(report_id)
            _require_instructor_approval(item)
            text = item.get("section_three_draft", {}).get("comments_draft", "")
        elif draft_id:
            item = self.store.get_draft(draft_id)
            _require_instructor_approval(item)
            text = _draft_speech_text(item)
        else:
            raise ValueError("Provide report_id or draft_id.")

        result = synthesize(text, mode)

        if result.get("enabled") and report_id:
            self.store.mark_drive_report_audio(report_id)

        return result


def _require_instructor_approval(item: dict) -> None:
    if item.get("review_decision") != "approve":
        raise ValueError(
            "Audio is available only after a licensed instructor approves the draft."
        )


def _draft_speech_text(draft: dict) -> str:
    parts = [
        draft.get("headline", ""),
        draft.get("safety_summary", ""),
        draft.get("observed_concern", ""),
        draft.get("lesson_focus", ""),
        draft.get("reflection_prompt", ""),
        draft.get("practice_assignment", ""),
        draft.get("family_summary", ""),
    ]
    return " ".join(part for part in parts if part)


class ClipboardRequestHandler(BaseHTTPRequestHandler):
    app: ClipboardApp = ClipboardApp()

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/health":
            self.send_json({"ok": True, "service": "opendrive-clipboard-demo"})
            return

        if path == "/api/scenarios":
            self.send_json({"scenarios": self.app.list_scenarios()})
            return

        if path.startswith("/api/demo-runs/"):
            run_id = path.rsplit("/", 1)[-1]
            self.safe_json(lambda: self.app.get_run(run_id))
            return

        if path.startswith("/api/drive-reports/"):
            report_id = path.rsplit("/", 1)[-1]
            self.safe_json(lambda: self.app.get_drive_report(report_id))
            return

        self.serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/demo-runs":
            payload = self.read_json()
            self.safe_json(lambda: self.app.create_run(payload), status=HTTPStatus.CREATED)
            return

        if path == "/api/drive-reports":
            payload = self.read_json()
            self.safe_json(
                lambda: self.app.create_drive_report(payload),
                status=HTTPStatus.CREATED,
            )
            return

        if path == "/api/tts":
            payload = self.read_json()
            self.safe_json(lambda: self.app.text_to_speech(payload))
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    def do_PATCH(self) -> None:
        path = urlparse(self.path).path

        if path.startswith("/api/drafts/") and path.endswith("/review"):
            draft_id = path.split("/")[-2]
            payload = self.read_json()
            self.safe_json(lambda: self.app.review_draft(draft_id, payload))
            return

        if path.startswith("/api/drive-reports/") and path.endswith("/review"):
            report_id = path.split("/")[-2]
            payload = self.read_json()
            self.safe_json(lambda: self.app.review_drive_report(report_id, payload))
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    def serve_static(self, path: str) -> None:
        if path in {"/", "/demo", "/boundary"}:
            file_path = WEB_ROOT / "index.html"
        elif path == "/drive-sheet":
            file_path = WEB_ROOT / "drive-sheet.html"
        else:
            file_path = (WEB_ROOT / path.lstrip("/")).resolve()
            if WEB_ROOT not in file_path.parents and file_path != WEB_ROOT:
                self.send_error(HTTPStatus.FORBIDDEN, "Forbidden path")
                return

        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        content_type = "text/html; charset=utf-8"
        if file_path.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        if file_path.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        if file_path.suffix == ".png":
            content_type = "image/png"
        if file_path.suffix == ".ico":
            content_type = "image/x-icon"
        if file_path.suffix == ".svg":
            content_type = "image/svg+xml"
        if file_path.suffix == ".webmanifest":
            content_type = "application/manifest+json"
        if file_path.suffix in {".jpg", ".jpeg"}:
            content_type = "image/jpeg"
        if file_path.suffix == ".webp":
            content_type = "image/webp"
        if file_path.suffix == ".json":
            content_type = "application/json"

        body = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}

        body = self.rfile.read(length).decode("utf-8")
        return json.loads(body)

    def safe_json(self, callback, status: HTTPStatus = HTTPStatus.OK) -> None:
        try:
            self.send_json(callback(), status)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


def build_server(host: str, port: int) -> ThreadingHTTPServer:
    ClipboardRequestHandler.app = ClipboardApp()

    return ThreadingHTTPServer((host, port), ClipboardRequestHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the OpenDrive Clipboard demo server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    args = parser.parse_args()

    server = build_server(args.host, args.port)
    print(f"OpenDrive Clipboard demo running at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
