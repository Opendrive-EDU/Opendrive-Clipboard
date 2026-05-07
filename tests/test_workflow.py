import unittest

from opendrive_clipboard.agent import ClipboardRunner
from opendrive_clipboard.store import DemoStore
from opendrive_clipboard.tools import InstructorReviewTools, guard_demo_payload


class ClipboardWorkflowTest(unittest.TestCase):
    def test_runner_stops_at_instructor_review_gate(self):
        store = DemoStore()
        run = ClipboardRunner(store).run(
            "residential-following-distance",
            "Learner should repeat mirror cadence before the next merge.",
        )

        self.assertEqual(run["draft"]["status"], "submitted_for_instructor_review")
        self.assertEqual(run["draft"]["status_label"], "DRAFT - INSTRUCTOR REVIEW REQUIRED")
        self.assertTrue(run["draft"]["instructor_review_required"])
        self.assertTrue(run["safety_boundary"]["demo_only_no_real_beacon_data"])
        self.assertTrue(run["safety_boundary"]["no_official_lms_or_dol_writes"])
        self.assertGreaterEqual(len(run["trace"]), 6)

    def test_review_decision_updates_demo_only_state(self):
        store = DemoStore()
        run = ClipboardRunner(store).run("yellow-light-decision")

        reviewed = InstructorReviewTools(store).record_instructor_decision(
            run["draft"]["id"],
            "approve",
        )

        self.assertEqual(reviewed["review_decision"], "approve")
        self.assertEqual(reviewed["status"], "preview_approve")

    def test_guard_rejects_official_record_keys(self):
        with self.assertRaises(ValueError):
            guard_demo_payload({"lms_completion": True})


if __name__ == "__main__":
    unittest.main()
