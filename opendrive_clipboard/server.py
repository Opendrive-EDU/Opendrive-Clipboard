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
from opendrive_clipboard.tools import InstructorReviewTools


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web"


class ClipboardApp:
    def __init__(self) -> None:
        self.store = DemoStore()
        self.runner = ClipboardRunner(self.store)
        self.review_tools = InstructorReviewTools(self.store)

    def list_scenarios(self) -> list[dict]:
        return self.store.list_scenarios()

    def create_run(self, payload: dict) -> dict:
        scenario_id = payload.get("scenario_id") or "residential-following-distance"
        instructor_notes = payload.get("instructor_notes") or ""

        return self.runner.run(scenario_id, instructor_notes)

    def get_run(self, run_id: str) -> dict:
        return self.store.get_run(run_id)

    def review_draft(self, draft_id: str, payload: dict) -> dict:
        decision = payload.get("decision") or ""

        return self.review_tools.record_instructor_decision(draft_id, decision)


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

        self.serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/demo-runs":
            payload = self.read_json()
            self.safe_json(lambda: self.app.create_run(payload), status=HTTPStatus.CREATED)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    def do_PATCH(self) -> None:
        path = urlparse(self.path).path

        if path.startswith("/api/drafts/") and path.endswith("/review"):
            draft_id = path.split("/")[-2]
            payload = self.read_json()
            self.safe_json(lambda: self.app.review_draft(draft_id, payload))
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")

    def serve_static(self, path: str) -> None:
        if path in {"/", "/demo", "/boundary"}:
            file_path = WEB_ROOT / "index.html"
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
