"""Tests for Creator UX and rule-first API workflow."""

from __future__ import annotations

import json
import unittest

from fastapi.testclient import TestClient

from ai_writer_room.tests.helpers import sample_path
from ai_writer_room.ui_contract.contract_loader import UIContractLoader
from api.main import app
from api.service import summarize_eval_for_creator


class CreatorWorkflowTests(unittest.TestCase):
    """Validate creator-first API contracts."""

    def setUp(self) -> None:
        """Create an API test client."""
        self.client = TestClient(app)

    def test_rules_generate_endpoint(self) -> None:
        """Rule generation workflow should return editable rule data."""
        response = self.client.post(
            "/api/rules/generate",
            json={
                "sub_genre": "地鐵末班車",
                "horror_style": "規則恐怖",
                "pacing_style": "高壓",
                "ending_style": "尾刀",
                "rule_count": 5,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        rules = payload["data"]["rules"]
        self.assertEqual(len(rules), 5)
        self.assertEqual(rules[0]["id"], "R01")
        self.assertIn("text", rules[0])
        self.assertIn("category", rules[0])

    def test_generation_request_preserves_creator_metadata(self) -> None:
        """Manual parse should persist creator controls into StoryBible."""
        response_text = sample_path("sample_manual_response.json").read_text(
            encoding="utf-8",
        )
        rules = [
            {
                "id": "R01",
                "text": "末班車進站後不能看窗外。",
                "category": "空間規則",
            },
            {
                "id": "R02",
                "text": "廣播若叫出你的名字，必須假裝沒聽見。",
                "category": "聲音規則",
            },
        ]

        response = self.client.post(
            "/api/manual/parse-response",
            json={
                "manual_response_text": response_text,
                "enable_eval": True,
                "enable_auto_fix": False,
                "export_render_input": True,
                "forbidden_words_text": "",
                "generated_rules": rules,
                "world_setting": "現代都市",
                "horror_style": "認知污染",
                "pacing_style": "慢燒",
                "ending_style": "假逃脫",
                "protagonist_type": "夜班人員",
                "object_focus": "黑色手機",
                "visual_style": "VHS",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"], payload.get("error"))
        story_bible = payload["data"]["storyboard"]["story_bible"]

        self.assertEqual(story_bible["world_setting"], "現代都市")
        self.assertEqual(story_bible["horror_style"], "認知污染")
        self.assertEqual(story_bible["pacing_style"], "慢燒")
        self.assertEqual(story_bible["ending_style"], "假逃脫")
        self.assertEqual(story_bible["protagonist_type"], "夜班人員")
        self.assertEqual(story_bible["object_focus"], "黑色手機")
        self.assertEqual(story_bible["visual_style"], "VHS")
        self.assertIn(
            "末班車進站後不能看窗外。",
            [rule["text"] for rule in story_bible["world_rules"]],
        )

    def test_eval_summary_translation(self) -> None:
        """Evaluator JSON should translate into creator-readable lines."""
        summary = summarize_eval_for_creator(
            {
                "rule_check": {"passed": True},
                "forbidden_word_check": {"total_hits": 2},
                "story_memory_check": {
                    "stats": {"unresolved_foreshadow_count": 3}
                },
            }
        )

        self.assertIn("✅ 規則完整", summary)
        self.assertIn("⚠ 偵測到 2 個禁忌詞", summary)
        self.assertIn("⚠ 有 3 個未完成伏筆", summary)

    def test_ui_contract_survives_creator_fields(self) -> None:
        """UI contract should keep tabs and creator-facing shared fields."""
        contract = UIContractLoader.load_contract()
        fields = {field.id for field in contract.shared_fields}
        tabs = {tab.id for tab in contract.tabs}

        self.assertEqual(tabs, {"manual", "openai"})
        self.assertIn("world_setting", fields)
        self.assertIn("horror_style", fields)
        self.assertIn("object_focus", fields)
        self.assertIn("visual_style", fields)
        self.assertIn("forbidden_words", fields)

    def test_manual_prompt_uses_generated_rules(self) -> None:
        """Manual prompt generation should include creator-provided rules."""
        response = self.client.post(
            "/api/manual/generate-prompt",
            json={
                "sub_genre": "地鐵末班車",
                "duration": 180,
                "generated_rules": [
                    {
                        "id": "R01",
                        "text": "看到空車廂時不要上車。",
                        "category": "空間規則",
                    }
                ],
                "world_setting": "現代都市",
                "horror_style": "規則恐怖",
                "pacing_style": "高壓",
                "ending_style": "尾刀",
                "protagonist_type": "上班族",
                "object_focus": "紅傘",
                "visual_style": "cinematic",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        prompt = payload["data"]["prompt"]
        self.assertIn("看到空車廂時不要上車。", prompt)
        self.assertIn("現代都市", prompt)
        self.assertIn("紅傘", prompt)


if __name__ == "__main__":
    unittest.main()
