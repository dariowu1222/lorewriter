"""Integration smoke tests for the core AI Writer Room pipelines."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from pydantic import BaseModel

from ai_writer_room import config
from ai_writer_room.evaluator.evaluator import StoryboardEvaluator
from ai_writer_room.generator.api_client import OpenAIClient
from ai_writer_room.generator.json_parser import StoryboardJsonParser
from ai_writer_room.generator.model_provider import LocalModelProvider
from ai_writer_room.generator.story_planner import build_mock_rule_horror_storyboard
from ai_writer_room.memory.arc_planner import ArcPlan
from ai_writer_room.memory.memory_summary import MemorySummary
from ai_writer_room.memory.story_bible import StoryBible
from ai_writer_room.render.render_adapter import RenderAdapter
from ai_writer_room.render.render_schema import (
    RenderDialogueLine,
    RenderProject,
    RenderScene,
)
from ai_writer_room.schemas.storyboard_schema import Storyboard
from ai_writer_room.tests.helpers import (
    load_json,
    run_cli_with_args,
    run_main_with_args,
    sample_path,
    temp_project_cwd,
    tiny_cost_guard_config,
)


class IntegrationSmokeTests(unittest.TestCase):
    """Smoke coverage for the local integration paths."""

    def test_mock_generation_pipeline(self) -> None:
        """Mock generation should produce storyboard, eval, and render JSON."""
        with temp_project_cwd() as temp_dir:
            exit_code, stdout, stderr = run_main_with_args(
                [
                    "--provider",
                    "mock",
                    "--sub-genre",
                    "地鐵末班車",
                    "--duration",
                    "180",
                    "--output",
                    "output/storyboard.json",
                    "--eval",
                    "--export-render-input",
                ]
            )

            self.assertEqual(exit_code, 0, stderr)
            storyboard_path = temp_dir / "output" / "storyboard.json"
            render_path = temp_dir / "output" / "storyboard.render.json"
            eval_path = temp_dir / "output" / "storyboard.eval.json"
            self.assertTrue(storyboard_path.exists(), stdout)
            self.assertTrue(render_path.exists(), stdout)
            self.assertTrue(eval_path.exists(), stdout)

            storyboard = self._load_storyboard(storyboard_path)
            render_payload = load_json(render_path)
            eval_payload = load_json(eval_path)

            self.assertEqual(len(storyboard.scenes), 12)
            self.assertIsInstance(storyboard.story_bible, StoryBible)
            self.assertIsInstance(storyboard.memory_summary, MemorySummary)
            self.assertIsInstance(storyboard.arc_plan, ArcPlan)
            self.assertEqual(len(storyboard.arc_plan.arcs), 6)
            self.assertEqual(len(render_payload["scenes"]), 12)
            self.assertTrue(eval_payload["passed"])

    def test_manual_pipeline_parse(self) -> None:
        """Manual provider should parse sampled model output into typed models."""
        with temp_project_cwd() as temp_dir:
            exit_code, stdout, stderr = run_main_with_args(
                [
                    "--provider",
                    "manual",
                    "--manual-response",
                    str(sample_path("sample_manual_response.json")),
                    "--output",
                    "output/manual_storyboard.json",
                    "--eval",
                    "--export-render-input",
                ]
            )

            self.assertEqual(exit_code, 0, stderr)
            storyboard = self._load_storyboard(
                temp_dir / "output" / "manual_storyboard.json",
            )
            self.assertIsInstance(storyboard.story_bible, StoryBible)
            self.assertIsInstance(storyboard.memory_summary, MemorySummary)
            self.assertIsInstance(storyboard.arc_plan, ArcPlan)
            self.assertTrue((temp_dir / "output" / "manual_storyboard.eval.json").exists())
            self.assertTrue(
                (temp_dir / "output" / "manual_storyboard.render.json").exists(),
                stdout,
            )

    def test_auto_fix_pipeline(self) -> None:
        """Auto-fix should reduce forbidden hits and restore known missing rules."""
        with temp_project_cwd() as temp_dir:
            exit_code, _, stderr = run_main_with_args(
                [
                    "--provider",
                    "manual",
                    "--manual-response",
                    str(sample_path("sample_forbidden_storyboard.json")),
                    "--output",
                    "output/auto_fix_storyboard.json",
                    "--eval",
                    "--auto-fix",
                ]
            )

            self.assertEqual(exit_code, 0, stderr)
            eval_payload = load_json(temp_dir / "output" / "auto_fix_storyboard.eval.json")
            before_fix = eval_payload["before_fix"]
            after_fix = eval_payload["after_fix"]

            self.assertFalse(before_fix["passed"])
            self.assertTrue(eval_payload["final_passed"])
            self.assertTrue(after_fix["passed"])
            self.assertGreater(
                before_fix["forbidden_word_check"]["total_hits"],
                after_fix["forbidden_word_check"]["total_hits"],
            )
            self.assertEqual(after_fix["forbidden_word_check"]["total_hits"], 0)
            self.assertIn("R01", before_fix["rule_check"]["missing_rule_ids"])
            self.assertEqual(after_fix["rule_check"]["missing_rule_ids"], [])

            fixed_storyboard = self._load_storyboard(
                temp_dir / "output" / "auto_fix_storyboard.json",
            )
            self.assertIn("R01", fixed_storyboard.scenes[1].rule_refs)

    def test_render_adapter_pipeline(self) -> None:
        """Render adapter should produce Pydantic render models and JSON output."""
        self.assertTrue(issubclass(RenderDialogueLine, BaseModel))
        self.assertTrue(issubclass(RenderScene, BaseModel))
        self.assertTrue(issubclass(RenderProject, BaseModel))

        storyboard = build_mock_rule_horror_storyboard("地鐵末班車")
        render_project = RenderAdapter().storyboard_to_render_project(storyboard)

        self.assertIsInstance(render_project, RenderProject)
        self.assertGreater(render_project.total_duration_sec, 0)
        self.assertEqual(len(render_project.scenes), 12)
        for scene in render_project.scenes:
            self.assertTrue(scene.narration)
            self.assertTrue(scene.tts_text)
            self.assertTrue(scene.subtitle_text)
            self.assertTrue(scene.image_prompt)
            self.assertTrue(scene.transition_type)

        source = inspect.getsource(self._export_render_input_function())
        self.assertIn("model_dump(mode=\"json\")", source)
        self.assertNotIn("asdict", source)

    def test_story_memory_pipeline(self) -> None:
        """Story memory scaffolding should be initialized for mock output."""
        storyboard = build_mock_rule_horror_storyboard("地鐵末班車")
        result = StoryboardEvaluator().evaluate(storyboard)
        story_memory = result["story_memory_check"]

        self.assertIsInstance(storyboard.story_bible, StoryBible)
        self.assertIsInstance(storyboard.memory_summary, MemorySummary)
        self.assertTrue(storyboard.foreshadowing)
        self.assertGreater(
            story_memory["stats"]["unresolved_foreshadow_count"],
            0,
        )
        self.assertTrue(storyboard.story_bible.active_arc_id)
        self.assertTrue(storyboard.memory_summary.current_arc_id)

    def test_cost_guard_blocking(self) -> None:
        """Budget guard should block OpenAI before any provider call."""
        with temp_project_cwd(cost_guard_config=tiny_cost_guard_config()) as temp_dir:
            with patch("ai_writer_room.generate_storyboard.OpenAIModelProvider") as provider:
                exit_code, _, stderr = run_main_with_args(
                    [
                        "--provider",
                        "openai",
                        "--sub-genre",
                        "地鐵末班車",
                        "--duration",
                        "180",
                        "--output",
                        "output/blocked.json",
                    ]
                )

            self.assertNotEqual(exit_code, 0)
            provider.assert_not_called()
            self.assertIn("Generation failed", stderr)
            self.assertFalse((temp_dir / "output" / "blocked.json").exists())

            failure_log = temp_dir / "logs" / "failures.jsonl"
            self.assertTrue(failure_log.exists())
            failure_record = json.loads(failure_log.read_text(encoding="utf-8").splitlines()[-1])
            self.assertEqual(failure_record["stage"], "budget_guard")

    def test_local_provider_error_message(self) -> None:
        """Local provider failures should produce a clear message without server."""
        with temp_project_cwd():
            with patch(
                "ai_writer_room.generate_storyboard.LocalModelProvider.generate_text",
                side_effect=RuntimeError(
                    "Local model server not reachable at http://localhost:11434/v1"
                ),
            ):
                exit_code, _, stderr = run_main_with_args(
                    [
                        "--provider",
                        "local",
                        "--sub-genre",
                        "地鐵末班車",
                        "--duration",
                        "180",
                        "--output",
                        "output/local.json",
                    ]
                )

        self.assertNotEqual(exit_code, 0)
        self.assertIn("Local model server not reachable", stderr)

        fake_response = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="{\"ok\": true}"),
                )
            ]
        )
        with patch("ai_writer_room.generator.model_provider.OpenAI") as openai_cls:
            openai_cls.return_value.chat.completions.create.return_value = fake_response
            provider = LocalModelProvider()
            provider.generate_text("prompt")

        init_kwargs = openai_cls.call_args.kwargs
        self.assertEqual(init_kwargs["timeout"], 60.0)
        self.assertEqual(init_kwargs["max_retries"], 3)

        create_kwargs = openai_cls.return_value.chat.completions.create.call_args.kwargs
        self.assertEqual(create_kwargs["temperature"], 0.3)
        self.assertEqual(create_kwargs["max_tokens"], 6500)
        self.assertEqual(create_kwargs["response_format"], {"type": "json_object"})
        self.assertEqual(
            create_kwargs["messages"][0]["content"],
            "Always reply with valid JSON only.",
        )

    def test_openai_missing_key_error(self) -> None:
        """Missing OpenAI key errors should be clear and not expose private paths."""
        with temp_project_cwd() as temp_dir:
            missing_key_file = temp_dir / "missing_openai_key"
            with patch.dict("os.environ", {"OPENAI_API_KEY": ""}):
                with patch.object(config, "API_KEY_FILE_PATH", missing_key_file):
                    with self.assertRaisesRegex(RuntimeError, "OpenAI API key not found") as ctx:
                        OpenAIClient()

        message = str(ctx.exception)
        self.assertNotIn("claude floder", message)
        self.assertNotIn("p0989", message)
        self.assertNotIn("sk-", message)

    def test_cli_wrapper(self) -> None:
        """cli.py should call the same argparse main entry point."""
        with temp_project_cwd() as temp_dir:
            exit_code, stdout, stderr = run_cli_with_args(
                [
                    "--provider",
                    "mock",
                    "--sub-genre",
                    "地鐵末班車",
                    "--duration",
                    "180",
                    "--output",
                    "output/cli_storyboard.json",
                ]
            )

            self.assertEqual(exit_code, 0, stderr)
            self.assertTrue((temp_dir / "output" / "cli_storyboard.json").exists())
            self.assertIn("Mock storyboard written", stdout)

    def _load_storyboard(self, path: Path) -> Storyboard:
        """Load and validate a storyboard JSON file."""
        payload = load_json(path)
        if hasattr(Storyboard, "model_validate"):
            return Storyboard.model_validate(payload)
        return Storyboard.parse_obj(payload)

    def _export_render_input_function(self):
        """Import lazily so source inspection follows the active module."""
        from ai_writer_room.generate_storyboard import export_render_input

        return export_render_input


if __name__ == "__main__":
    unittest.main()
