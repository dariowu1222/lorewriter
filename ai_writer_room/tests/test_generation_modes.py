"""Smoke tests for public generation mode metadata and checks."""

from __future__ import annotations

import json
import unittest

from ai_writer_room.evaluator.generation_mode_checker import GenerationModeChecker
from ai_writer_room.evaluator.evaluator import StoryboardEvaluator
from ai_writer_room.generator.generation_mode import (
    GenerationMode,
    GenerationModeRegistry,
)
from ai_writer_room.generator.story_planner import build_mock_rule_horror_storyboard
from ai_writer_room.tests.helpers import (
    load_json,
    run_main_with_args,
    sample_path,
    temp_project_cwd,
)


class GenerationModeTests(unittest.TestCase):
    """Validate manual/openai mode metadata and CLI contract."""

    def test_list_modes(self) -> None:
        """Registry should expose manual and openai in stable order."""
        modes = GenerationModeRegistry.list_modes()

        self.assertEqual([mode.mode for mode in modes], ["manual", "openai"])
        self.assertEqual(len(modes), 2)

    def test_manual_metadata(self) -> None:
        """Manual mode metadata should match the UI contract."""
        mode = GenerationModeRegistry.get_mode_info(GenerationMode.MANUAL)

        self.assertEqual(mode.mode, "manual")
        self.assertEqual(mode.display_name, "省錢模式")
        self.assertFalse(mode.requires_api_key)
        self.assertTrue(mode.supports_auto_fix)
        self.assertTrue(mode.supports_render_export)
        self.assertFalse(mode.supports_cost_guard)
        self.assertEqual(mode.estimated_speed, "慢")
        self.assertEqual(mode.estimated_cost_level, "低")
        self.assertIn("節省 API 成本", mode.recommended_for)

    def test_openai_metadata(self) -> None:
        """OpenAI mode metadata should match the UI contract."""
        mode = GenerationModeRegistry.get_mode_info(GenerationMode.OPENAI)

        self.assertEqual(mode.mode, "openai")
        self.assertEqual(mode.display_name, "API 自動模式")
        self.assertTrue(mode.requires_api_key)
        self.assertTrue(mode.supports_auto_fix)
        self.assertTrue(mode.supports_render_export)
        self.assertTrue(mode.supports_cost_guard)
        self.assertEqual(mode.estimated_speed, "快")
        self.assertEqual(mode.estimated_cost_level, "中")
        self.assertIn("商業化", mode.recommended_for)

    def test_list_generation_modes_cli(self) -> None:
        """CLI should print JSON mode metadata without running generation."""
        with temp_project_cwd() as temp_dir:
            exit_code, stdout, stderr = run_main_with_args(
                ["--list-generation-modes"]
            )

            self.assertEqual(exit_code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual([item["mode"] for item in payload], ["manual", "openai"])
            self.assertFalse((temp_dir / "logs" / "failures.jsonl").exists())
            self.assertEqual(list((temp_dir / "output").iterdir()), [])

    def test_generation_mode_checker(self) -> None:
        """GenerationModeChecker should validate manual/openai contracts."""
        checker = GenerationModeChecker()

        manual = checker.check(
            provider_name="manual",
            cost_guard_enabled=False,
            render_export_requested=True,
        )
        self.assertTrue(manual["passed"])
        self.assertEqual(manual["stats"]["generation_mode"], "manual")
        self.assertFalse(manual["stats"]["requires_api_key"])

        openai = checker.check(
            provider_name="openai",
            cost_guard_enabled=True,
            render_export_requested=True,
        )
        self.assertTrue(openai["passed"])
        self.assertEqual(openai["stats"]["generation_mode"], "openai")
        self.assertTrue(openai["stats"]["supports_cost_guard"])

        mock = checker.check(provider_name="mock")
        self.assertFalse(mock["passed"])
        self.assertIn("not a public generation mode", mock["warnings"][0])

    def test_generation_mode_check_in_evaluator(self) -> None:
        """Evaluator output should include generation_mode_check."""
        storyboard = build_mock_rule_horror_storyboard("地鐵末班車")
        result = StoryboardEvaluator().evaluate(
            storyboard=storyboard,
            provider_name="manual",
            cost_guard_enabled=False,
            render_export_requested=True,
        )

        self.assertIn("generation_mode_check", result)
        self.assertTrue(result["generation_mode_check"]["passed"])
        self.assertEqual(
            result["generation_mode_check"]["stats"]["generation_mode"],
            "manual",
        )

    def test_generation_log_metadata(self) -> None:
        """Successful manual runs should write safe generation mode metadata."""
        with temp_project_cwd() as temp_dir:
            exit_code, _, stderr = run_main_with_args(
                [
                    "--provider",
                    "manual",
                    "--manual-response",
                    str(sample_path("sample_manual_response.json")),
                    "--output",
                    "output/manual_storyboard.json",
                ]
            )

            self.assertEqual(exit_code, 0, stderr)
            log_paths = list((temp_dir / "logs" / "generations").glob("*/*.json"))
            self.assertEqual(len(log_paths), 1)
            record = load_json(log_paths[0])

        self.assertEqual(record["generation_mode"], "manual")
        self.assertEqual(record["generation_mode_display_name"], "省錢模式")
        self.assertTrue(record["used_manual_pipeline"])
        self.assertFalse(record["used_api_pipeline"])


if __name__ == "__main__":
    unittest.main()
