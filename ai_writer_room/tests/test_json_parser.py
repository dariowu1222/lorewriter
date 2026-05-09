"""Smoke tests for storyboard JSON parsing."""

from __future__ import annotations

import json
import unittest

from ai_writer_room.generator.json_parser import StoryboardJsonParser
from ai_writer_room.generator.story_planner import build_mock_rule_horror_storyboard


def _storyboard_json() -> str:
    storyboard = build_mock_rule_horror_storyboard(
        sub_genre="地鐵末班車",
        duration_sec=180,
    )
    storyboard.scenes[0].narration_zh += ' 牆上寫著 {"fake": "brace"}。'
    if hasattr(storyboard, "model_dump"):
        payload = storyboard.model_dump(mode="json")
    else:
        payload = storyboard.dict()
    return json.dumps(payload, ensure_ascii=False)


class StoryboardJsonParserTest(unittest.TestCase):
    """Parser should extract valid storyboard JSON from common model outputs."""

    def setUp(self) -> None:
        """Create parser and payload fixtures."""
        self.parser = StoryboardJsonParser()
        self.payload = _storyboard_json()

    def test_parse_direct_json(self) -> None:
        """Direct JSON should validate as a Storyboard."""
        storyboard = self.parser.parse_storyboard(self.payload)
        self.assertEqual(len(storyboard.scenes), 12)

    def test_parse_fenced_json(self) -> None:
        """Fenced JSON should have code fences removed."""
        storyboard = self.parser.parse_storyboard(f"```json\n{self.payload}\n```")
        self.assertEqual(storyboard.scenes[0].id, "S01")

    def test_parse_with_garbage_prefix_and_suffix_braces(self) -> None:
        """Balanced extraction should ignore non-JSON suffix braces."""
        raw_text = f"Here is the JSON:\n{self.payload}\nNote: {{placeholder}}"
        storyboard = self.parser.parse_storyboard(raw_text)
        self.assertEqual(storyboard.title, "地鐵末班車規則怪談")


if __name__ == "__main__":
    unittest.main()
