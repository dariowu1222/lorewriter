"""Smoke tests for deterministic local auto-fix behavior."""

from __future__ import annotations

import unittest

from ai_writer_room.evaluator.auto_fix import LocalAutoFixer
from ai_writer_room.evaluator.forbidden_word_checker import ForbiddenWordChecker
from ai_writer_room.generator.story_planner import build_mock_rule_horror_storyboard


class LocalAutoFixerTest(unittest.TestCase):
    """Local auto-fix should be deterministic and conservative."""

    def test_forbidden_word_replacement_uses_ascii_word_boundary(self) -> None:
        """ASCII terms should not be replaced inside larger words."""
        storyboard = build_mock_rule_horror_storyboard("地鐵末班車")
        storyboard.scenes[0].narration_zh = "bad apple badminton"
        forbidden_words = {"bad": "good"}
        check = ForbiddenWordChecker(forbidden_words).check_storyboard(storyboard)

        fixed = LocalAutoFixer(forbidden_words).fix_forbidden_words(
            storyboard=storyboard,
            forbidden_word_check=check,
        )

        self.assertEqual(fixed.scenes[0].narration_zh, "good apple badminton")

    def test_unknown_missing_rule_id_is_not_forced_into_tail_scene(self) -> None:
        """Unknown rule ids should be left for caller review."""
        storyboard = build_mock_rule_horror_storyboard("地鐵末班車")

        fixed = LocalAutoFixer({}).fix_missing_rule_refs(
            storyboard=storyboard,
            rule_check={"missing_rule_ids": ["R06"]},
        )

        self.assertFalse(
            any("R06" in scene.rule_refs for scene in fixed.scenes),
        )

    def test_known_missing_rule_id_is_added_to_target_scene(self) -> None:
        """Known v0.1 rule ids should be restored to deterministic scenes."""
        storyboard = build_mock_rule_horror_storyboard("地鐵末班車")
        storyboard.scenes[1].rule_refs = [
            rule_id for rule_id in storyboard.scenes[1].rule_refs if rule_id != "R01"
        ]

        fixed = LocalAutoFixer({}).fix_missing_rule_refs(
            storyboard=storyboard,
            rule_check={"missing_rule_ids": ["R01"]},
        )

        self.assertIn("R01", fixed.scenes[1].rule_refs)


if __name__ == "__main__":
    unittest.main()
