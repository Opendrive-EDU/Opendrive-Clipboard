import json
import unittest

from opendrive_clipboard.beacon_demo import mock_beacon_recording
from opendrive_clipboard.grader import grade_drive


FORBIDDEN_AUDIO_KEYS = {"audio", "microphone", "cabin"}


def _walk(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield str(key)
            yield from _walk(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk(item)


class BeaconDemoTest(unittest.TestCase):
    def test_beacon_recording_shape(self):
        recording = mock_beacon_recording("drive-1")
        for key in ("meta", "can", "imu", "gps", "forward_camera", "intervention_taps"):
            self.assertIn(key, recording)
        self.assertGreater(len(recording["can"]), 0)
        self.assertGreater(len(recording["imu"]), 0)
        self.assertGreater(len(recording["gps"]), 0)

    def test_beacon_has_no_audio(self):
        recording = mock_beacon_recording("drive-2")
        self.assertFalse(recording["meta"]["has_audio"])
        for key in _walk(recording):
            self.assertNotIn(
                key.lower(),
                FORBIDDEN_AUDIO_KEYS,
                f"Forbidden audio-related key found in beacon payload: {key}",
            )

    def test_beacon_is_deterministic(self):
        first = mock_beacon_recording("drive-1")
        second = mock_beacon_recording("drive-1")
        self.assertEqual(
            json.dumps(first, sort_keys=True),
            json.dumps(second, sort_keys=True),
        )

    def test_unknown_scenario_raises(self):
        with self.assertRaises(ValueError):
            mock_beacon_recording("unknown-scenario")


class GraderTest(unittest.TestCase):
    def test_report_status_is_draft(self):
        report = grade_drive("drive-1")
        self.assertEqual(report["status"], "DRAFT_INSTRUCTOR_REVIEW_REQUIRED")
        self.assertTrue(report["instructor_review_required"])
        self.assertTrue(report["synthetic_only"])

    def test_report_has_no_audio_keys(self):
        report = grade_drive("drive-1")
        self.assertFalse(report["has_audio"])
        for key in _walk(report):
            self.assertNotIn(
                key.lower(),
                FORBIDDEN_AUDIO_KEYS,
                f"Forbidden audio-related key found in report: {key}",
            )

    def test_report_is_deterministic(self):
        first = grade_drive("drive-1")
        second = grade_drive("drive-1")
        self.assertEqual(
            json.dumps(first, sort_keys=True),
            json.dumps(second, sort_keys=True),
        )

    def test_ratings_are_in_dol_scale(self):
        report = grade_drive("drive-2")
        for row in report["skill_ratings"]:
            self.assertIn(row["suggested_rating"], {None, 1, 2, 3, 4})
            self.assertIn("rationale", row)
            self.assertIn("instructor_override", row)

    def test_driver_health_panel_has_five_categories(self):
        report = grade_drive("drive-1")
        panel = report["driver_health_panel"]
        metrics = {row["metric"] for row in panel}
        self.assertEqual(
            metrics,
            {"safety", "smoothness", "attention", "control", "eco"},
        )
        for row in panel:
            self.assertIn(row["flag"], {"ok", "watch", "concern"})
            self.assertTrue(row["ref_range"])
            self.assertIn("label", row)
            self.assertGreaterEqual(row["value"], 0)
            self.assertLessEqual(row["value"], 100)
            self.assertIsInstance(row["signals"], list)
            self.assertGreater(len(row["signals"]), 0)

    def test_driver_health_panel_disclosure_present(self):
        report = grade_drive("drive-1")
        disclosure = report["driver_health_panel_disclosure"]
        self.assertIn("checkup", disclosure.lower())
        self.assertIn("does not judge", disclosure.lower())

    def test_eco_score_in_range(self):
        report = grade_drive("drive-1")
        eco = report["eco_score"]
        self.assertGreaterEqual(eco["score"], 0)
        self.assertLessEqual(eco["score"], 100)
        self.assertIn(eco["band"], {"efficient", "developing", "aggressive"})

    def test_attitude_profile_sums_to_100(self):
        report = grade_drive("drive-2")
        profile = report["attitude_profile"]
        total = profile["calm_pct"] + profile["tentative_pct"] + profile["aggressive_pct"]
        self.assertEqual(total, 100)

    def test_strengths_and_gaps_are_disjoint(self):
        report = grade_drive("drive-1")
        strength_ids = {item["skill_id"] for item in report["strengths"]}
        gap_ids = {item["skill_id"] for item in report["needs_improvement"]}
        self.assertTrue(strength_ids.isdisjoint(gap_ids))

    def test_section_three_draft_has_suggested_reaction(self):
        report = grade_drive("drive-2")
        section = report["section_three_draft"]
        self.assertIn(
            section["reaction_to_coaching_suggested"],
            ("needs_improvement", "good", "excellent"),
        )
        self.assertIn("comments_draft", section)


if __name__ == "__main__":
    unittest.main()
