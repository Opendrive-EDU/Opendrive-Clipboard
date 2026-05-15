import json
import threading
import unittest
import urllib.request

from opendrive_clipboard.server import build_server


class ClipboardServerTest(unittest.TestCase):
    def setUp(self):
        self.server = build_server("127.0.0.1", 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_health_scenarios_and_demo_run(self):
        health = self.get_json("/api/health")
        self.assertTrue(health["ok"])

        scenarios = self.get_json("/api/scenarios")
        self.assertGreaterEqual(len(scenarios["scenarios"]), 2)

        run = self.post_json(
            "/api/demo-runs",
            {
                "scenario_id": "residential-following-distance",
                "instructor_notes": "Synthetic server test.",
            },
        )
        self.assertIn("draft", run)
        self.assertEqual(run["draft"]["status"], "submitted_for_instructor_review")

        reviewed = self.patch_json(
            f"/api/drafts/{run['draft']['id']}/review",
            {"decision": "reject"},
        )
        self.assertEqual(reviewed["review_decision"], "reject")

    def test_drive_sheet_grader_endpoints(self):
        report = self.post_json(
            "/api/drive-reports",
            {"scenario_id": "residential-following-distance"},
        )
        self.assertEqual(report["status"], "DRAFT_INSTRUCTOR_REVIEW_REQUIRED")
        self.assertFalse(report["has_audio"])
        self.assertIn("driver_health_panel", report)
        self.assertIn("skill_ratings", report)

        fetched = self.get_json(f"/api/drive-reports/{report['id']}")
        self.assertEqual(fetched["id"], report["id"])

        reviewed = self.patch_json(
            f"/api/drive-reports/{report['id']}/review",
            {"decision": "approve"},
        )
        self.assertEqual(reviewed["review_decision"], "approve")
        self.assertEqual(reviewed["status_label"], "INSTRUCTOR APPROVED - DRAFT")

    def test_drive_sheet_page_serves_html(self):
        with urllib.request.urlopen(self.base_url + "/drive-sheet", timeout=5) as response:
            body = response.read().decode("utf-8")
        self.assertIn("Drive Sheet Draft", body)
        self.assertIn("DRAFT - INSTRUCTOR REVIEW REQUIRED", body)

    def get_json(self, path):
        with urllib.request.urlopen(self.base_url + path, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def post_json(self, path, payload):
        request = urllib.request.Request(
            self.base_url + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))

    def patch_json(self, path, payload):
        request = urllib.request.Request(
            self.base_url + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="PATCH",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
