"""Smoke tests for storyboard evaluation."""

from __future__ import annotations

import unittest

from ai_writer_room.evaluator.evaluator import StoryboardEvaluator
from ai_writer_room.generator.story_planner import build_mock_rule_horror_storyboard


class StoryboardEvaluatorSmokeTest(unittest.TestCase):
    """Mock storyboard should satisfy the local v0.1 evaluator."""

    def test_mock_storyboard_passes_core_checks(self) -> None:
        """Rule, forbidden-word, and arc checks should pass for mock output."""
        storyboard = build_mock_rule_horror_storyboard("地鐵末班車")
        result = StoryboardEvaluator().evaluate(storyboard)

        self.assertTrue(result["passed"])
        self.assertTrue(result["rule_check"]["passed"])
        self.assertTrue(result["forbidden_word_check"]["passed"])
        self.assertTrue(result["arc_check"]["passed"])


if __name__ == "__main__":
    unittest.main()
