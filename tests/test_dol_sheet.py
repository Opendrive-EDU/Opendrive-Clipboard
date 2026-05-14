import unittest

from opendrive_clipboard.dol_sheet import (
    DOL_SKILLS,
    RATING_SCALE,
    REACTION_TO_COACHING,
    dol_skills,
    pattern_to_skills,
    rating_scale,
    skill_groups,
)


class DolSheetTest(unittest.TestCase):
    def test_skill_count_and_unique_ids(self):
        # 51 rows on form DTS-661-047 across pages 2-6 (the highway "Control
        # speed" row is renamed in the id to keep ids unique).
        self.assertEqual(len(DOL_SKILLS), 51)
        ids = [skill["id"] for skill in DOL_SKILLS]
        self.assertEqual(len(ids), len(set(ids)), "skill ids must be unique")

    def test_each_skill_has_required_keys(self):
        for skill in DOL_SKILLS:
            self.assertIn("id", skill)
            self.assertIn("label", skill)
            self.assertIn("group", skill)
            self.assertIsInstance(skill["telemetry"], list)
            self.assertIsInstance(skill["event_patterns"], list)

    def test_rating_scale_matches_dol_wording(self):
        self.assertEqual(set(RATING_SCALE.keys()), {1, 2, 3, 4})
        self.assertIn("Potential danger", RATING_SCALE[1]["label"])
        self.assertIn("Needs improvement", RATING_SCALE[2]["label"])
        self.assertIn("Developing", RATING_SCALE[3]["label"])
        self.assertIn("Meets standard", RATING_SCALE[4]["label"])

    def test_reaction_to_coaching_options(self):
        self.assertEqual(
            REACTION_TO_COACHING,
            ("needs_improvement", "good", "excellent"),
        )

    def test_pattern_to_skills_known_patterns(self):
        self.assertIn(
            "keep_safe_following_distance",
            pattern_to_skills("space_management"),
        )
        self.assertIn(
            "scan_the_road",
            pattern_to_skills("visual_search"),
        )
        self.assertIn(
            "follow_traffic_lights",
            pattern_to_skills("intersection_search"),
        )
        self.assertEqual(pattern_to_skills("nonexistent_pattern"), [])

    def test_helpers_return_copies(self):
        copy_one = dol_skills()
        copy_one[0]["label"] = "MUTATED"
        copy_two = dol_skills()
        self.assertNotEqual(copy_one[0]["label"], copy_two[0]["label"])

        scale_copy = rating_scale()
        scale_copy[1]["label"] = "X"
        self.assertNotEqual(rating_scale()[1]["label"], "X")

    def test_skill_groups_preserves_form_order(self):
        groups = skill_groups()
        self.assertEqual(groups[0], "Pre-drive")
        self.assertIn("Highway", groups)
        self.assertIn("Reflection", groups)


if __name__ == "__main__":
    unittest.main()
