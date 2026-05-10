"""Smoke tests for the FastAPI web prototype."""

from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from ai_writer_room import config
from ai_writer_room.tests.helpers import sample_path
from api.main import app


class ApiSmokeTests(unittest.TestCase):
    """Validate the minimal API endpoints without external services."""

    def setUp(self) -> None:
        """Create a FastAPI test client."""
        self.client = TestClient(app)

    def test_health(self) -> None:
        """Health endpoint should return ok."""
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertEqual(payload["message"], "ok")

    def test_ui_contract(self) -> None:
        """UI contract endpoint should return manual/openai tabs."""
        response = self.client.get("/api/ui-contract")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        tabs = {tab["id"] for tab in payload["data"]["tabs"]}
        self.assertEqual(tabs, {"manual", "openai"})

    def test_generation_modes(self) -> None:
        """Generation modes endpoint should return manual/openai metadata."""
        response = self.client.get("/api/generation-modes")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        modes = {mode["mode"] for mode in payload["data"]["modes"]}
        self.assertEqual(modes, {"manual", "openai"})

    def test_manual_generate_prompt(self) -> None:
        """Manual prompt endpoint should return prompt text without a model call."""
        response = self.client.post(
            "/api/manual/generate-prompt",
            json={
                "sub_genre": "地鐵末班車",
                "duration": 180,
                "forbidden_words_text": "詭異=不合常理",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        self.assertIn("prompt", payload["data"])
        self.assertIn("地鐵末班車", payload["data"]["prompt"])

    def test_manual_parse_response(self) -> None:
        """Manual parse endpoint should parse sample JSON and return eval/render."""
        response_text = sample_path("sample_manual_response.json").read_text(
            encoding="utf-8",
        )
        response = self.client.post(
            "/api/manual/parse-response",
            json={
                "manual_response_text": response_text,
                "enable_eval": True,
                "enable_auto_fix": False,
                "export_render_input": True,
                "forbidden_words_text": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])
        data = payload["data"]
        self.assertEqual(len(data["storyboard"]["scenes"]), 12)
        self.assertIsNotNone(data["eval_result"])
        self.assertIsNotNone(data["render_project"])
        self.assertEqual(len(data["render_project"]["scenes"]), 12)

    def test_openai_generate_missing_key_fails_safely(self) -> None:
        """OpenAI endpoint should fail safely without exposing key details."""
        missing_key_path = Path("Z:/definitely/missing/openai_api_key")
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "", "OPENAI_API_KEY_FILE": ""},
        ):
            with patch.object(config, "API_KEY_FILE_PATH", missing_key_path):
                response = self.client.post(
                    "/api/openai/generate",
                    json={
                        "sub_genre": "地鐵末班車",
                        "duration": 180,
                        "model": "gpt-4o-mini",
                        "enable_eval": True,
                        "enable_auto_fix": False,
                        "export_render_input": True,
                        "ignore_budget_guard": False,
                        "forbidden_words_text": "",
                    },
                )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["success"])
        self.assertIn("OpenAI API key", payload["error"])
        self.assertNotIn("p0989", payload["error"])
        self.assertNotIn("claude floder", payload["error"])
        self.assertNotIn("sk-", payload["error"])


if __name__ == "__main__":
    unittest.main()
