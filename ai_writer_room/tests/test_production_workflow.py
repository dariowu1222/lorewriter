"""Tests for local next-step production packages."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from ai_writer_room.tests.helpers import sample_path
from api.main import app


class ProductionWorkflowTests(unittest.TestCase):
    """Validate voice/image/storyboard/video handoff endpoints."""

    def setUp(self) -> None:
        """Create an API client and a render-ready sample payload."""
        self.client = TestClient(app)
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
        payload = response.json()
        self.assertTrue(payload["success"], payload.get("error"))
        self.production_payload = {
            "storyboard": payload["data"]["storyboard"],
            "render_project": payload["data"]["render_project"],
            "visual_style": "cinematic",
        }

    def test_generate_voice_package(self) -> None:
        """Voice endpoint should prepare one script line per render scene."""
        response = self.client.post(
            "/api/production/voice",
            json=self.production_payload,
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"], payload.get("error"))
        voice_project = payload["data"]["voice_project"]
        self.assertEqual(len(voice_project["lines"]), 12)
        self.assertIn("output_filename", voice_project["lines"][0])

    def test_generate_image_prompt_package(self) -> None:
        """Image endpoint should prepare one prompt per render scene."""
        response = self.client.post(
            "/api/production/images",
            json=self.production_payload,
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"], payload.get("error"))
        image_project = payload["data"]["image_prompt_project"]
        self.assertEqual(image_project["total_images"], 12)
        self.assertIn("negative_prompt", image_project["items"][0])

    def test_generate_shot_storyboard(self) -> None:
        """Storyboard endpoint should prepare one shot per render scene."""
        response = self.client.post(
            "/api/production/storyboard",
            json=self.production_payload,
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"], payload.get("error"))
        shot_storyboard = payload["data"]["shot_storyboard"]
        self.assertEqual(shot_storyboard["total_shots"], 12)
        self.assertIn("camera_style", shot_storyboard["shots"][0])

    def test_generate_video_manifest(self) -> None:
        """Video endpoint should prepare an assembly manifest without ffmpeg."""
        response = self.client.post(
            "/api/production/video",
            json=self.production_payload,
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"], payload.get("error"))
        manifest = payload["data"]["video_manifest"]
        self.assertEqual(len(manifest["scenes"]), 12)
        self.assertEqual(manifest["status"], "manifest_ready")


if __name__ == "__main__":
    unittest.main()
