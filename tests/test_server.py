import base64
import json
import os
import sys
import threading
import types
import unittest
import urllib.error
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
                "scenario_id": "drive-1",
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
            {"scenario_id": "drive-1"},
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

    def test_tts_requires_instructor_approval(self):
        report = self.post_json("/api/drive-reports", {"scenario_id": "drive-1"})

        status, payload = self.post_expecting_error(
            "/api/tts", {"report_id": report["id"]}
        )

        self.assertEqual(status, 400)
        self.assertIn("instructor", payload["error"].lower())

    def test_tts_disabled_returns_enabled_false_after_approval(self):
        # Default build/test state: SPEECHIFY_ENABLE_TTS unset -> no SDK import,
        # no network. The approval gate still must pass first.
        self.assertNotEqual(os.getenv("SPEECHIFY_ENABLE_TTS"), "true")

        report = self.post_json("/api/drive-reports", {"scenario_id": "drive-1"})
        self.patch_json(
            f"/api/drive-reports/{report['id']}/review", {"decision": "approve"}
        )

        result = self.post_json("/api/tts", {"report_id": report["id"]})
        self.assertEqual(result, {"enabled": False})

    def test_tts_rejects_unknown_voice_mode(self):
        report = self.post_json("/api/drive-reports", {"scenario_id": "drive-1"})
        self.patch_json(
            f"/api/drive-reports/{report['id']}/review", {"decision": "approve"}
        )

        status, payload = self.post_expecting_error(
            "/api/tts", {"report_id": report["id"], "mode": "celebrity"}
        )

        self.assertEqual(status, 400)
        self.assertIn("voice mode", payload["error"].lower())

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

    def post_expecting_error(self, path, payload):
        request = urllib.request.Request(
            self.base_url + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))


class SpeechifyProviderTest(unittest.TestCase):
    """Unit-level checks for the optional Speechify provider (no network)."""

    def setUp(self):
        self._saved_env = {
            key: os.environ.get(key)
            for key in (
                "SPEECHIFY_ENABLE_TTS",
                "SPEECHIFY_API_KEY",
                "SPEECHIFY_VOICE_DEFAULT",
                "SPEECHIFY_VOICE_YOUTH",
            )
        }
        self._saved_module = sys.modules.get("speechify")

    def tearDown(self):
        for key, value in self._saved_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        if self._saved_module is None:
            sys.modules.pop("speechify", None)
        else:
            sys.modules["speechify"] = self._saved_module

    def _install_fake_sdk(self, fail_voices=()):
        calls = []

        class _Audio:
            def speech(self, input, voice_id):
                calls.append((input, voice_id))
                if voice_id in fail_voices:
                    raise RuntimeError(f"voice {voice_id} not licensed")
                return {"audio_data": base64.b64encode(b"AUDIO").decode("ascii")}

        class _TTS:
            audio = _Audio()

        class Speechify:
            def __init__(self, token=None):
                self.token = token
                self.tts = _TTS()

        module = types.ModuleType("speechify")
        module.Speechify = Speechify
        sys.modules["speechify"] = module
        return calls

    def test_disabled_without_env(self):
        os.environ.pop("SPEECHIFY_ENABLE_TTS", None)
        from opendrive_clipboard.tts import synthesize

        self.assertEqual(synthesize("hello"), {"enabled": False})

    def test_professional_voice_synthesizes(self):
        os.environ["SPEECHIFY_ENABLE_TTS"] = "true"
        os.environ["SPEECHIFY_API_KEY"] = "test-key"
        os.environ["SPEECHIFY_VOICE_DEFAULT"] = "scott"
        self._install_fake_sdk()
        from opendrive_clipboard.tts import synthesize

        result = synthesize("Approved comment.", mode="professional")
        self.assertTrue(result["enabled"])
        self.assertEqual(result["voice"], "scott")
        self.assertFalse(result["voice_fell_back"])
        self.assertEqual(base64.b64decode(result["audio_b64"]), b"AUDIO")

    def test_youth_voice_falls_back_when_unlicensed(self):
        os.environ["SPEECHIFY_ENABLE_TTS"] = "true"
        os.environ["SPEECHIFY_API_KEY"] = "test-key"
        os.environ["SPEECHIFY_VOICE_DEFAULT"] = "scott"
        os.environ["SPEECHIFY_VOICE_YOUTH"] = "snoop"
        self._install_fake_sdk(fail_voices=("snoop",))
        from opendrive_clipboard.tts import synthesize

        result = synthesize("Approved comment.", mode="youth")
        self.assertTrue(result["enabled"])
        self.assertTrue(result["voice_fell_back"])
        self.assertEqual(result["voice"], "scott")


if __name__ == "__main__":
    unittest.main()
