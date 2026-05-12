"""Tests for the minimal Web UI contract."""

from __future__ import annotations

import json
import unittest

from ai_writer_room.tests.helpers import run_main_with_args, temp_project_cwd
from ai_writer_room.ui_contract.contract_loader import UIContractLoader


class UIContractTests(unittest.TestCase):
    """Validate UI contract loading and CLI output."""

    def test_contract_loader_loads_contract(self) -> None:
        """UIContractLoader should load the versioned contract."""
        contract = UIContractLoader.load_contract()

        self.assertEqual(contract.version, "0.1")
        self.assertGreaterEqual(len(contract.tabs), 2)

    def test_contract_has_manual_and_openai_tabs(self) -> None:
        """Contract should expose enabled manual/openai tabs."""
        contract = UIContractLoader.load_contract()
        tabs = {tab.id: tab for tab in contract.tabs}

        self.assertIn("manual", tabs)
        self.assertIn("openai", tabs)
        self.assertTrue(tabs["manual"].enabled)
        self.assertTrue(tabs["openai"].enabled)
        self.assertEqual(tabs["manual"].mode, "manual")
        self.assertEqual(tabs["openai"].mode, "openai")

    def test_shared_fields_include_required_contract_fields(self) -> None:
        """Shared fields should include core generation inputs."""
        contract = UIContractLoader.load_contract()
        fields = {field.id: field for field in contract.shared_fields}

        self.assertIn("sub_genre", fields)
        self.assertIn("duration", fields)
        self.assertIn("forbidden_words", fields)
        self.assertIn("world_setting", fields)
        self.assertIn("horror_style", fields)
        self.assertIn("pacing_style", fields)
        self.assertIn("ending_style", fields)
        self.assertIn("protagonist_type", fields)
        self.assertIn("object_focus", fields)
        self.assertIn("visual_style", fields)
        self.assertEqual(fields["sub_genre"].type, "select")
        self.assertTrue(fields["sub_genre"].required)
        self.assertEqual(fields["duration"].default, 180)
        self.assertEqual(fields["forbidden_words"].type, "textarea")
        self.assertEqual(fields["object_focus"].type, "combobox")

    def test_mode_fields_include_manual_and_openai_fields(self) -> None:
        """Mode field helpers should hide engineering paths and expose OpenAI fields."""
        loader = UIContractLoader()
        manual_fields = {
            field.id for field in loader.get_fields_for_mode("manual")["mode_fields"]
        }
        openai_fields = {
            field.id for field in loader.get_fields_for_mode("openai")["mode_fields"]
        }

        self.assertNotIn("manual_prompt_output", manual_fields)
        self.assertNotIn("manual_response_input", manual_fields)
        self.assertIn("model", openai_fields)
        self.assertIn("ignore_budget_guard", openai_fields)

    def test_actions_are_present(self) -> None:
        """Shared and mode-specific actions should not be empty."""
        loader = UIContractLoader()
        manual_actions = loader.get_actions_for_mode("manual")
        openai_actions = loader.get_actions_for_mode("openai")

        self.assertTrue(manual_actions["shared_actions"])
        self.assertTrue(manual_actions["mode_actions"])
        self.assertTrue(openai_actions["shared_actions"])
        self.assertTrue(openai_actions["mode_actions"])

    def test_print_ui_contract_cli(self) -> None:
        """CLI should print contract JSON without running generation."""
        with temp_project_cwd() as temp_dir:
            exit_code, stdout, stderr = run_main_with_args(["--print-ui-contract"])

            self.assertEqual(exit_code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["version"], "0.1")
            self.assertEqual(
                {tab["id"] for tab in payload["tabs"]},
                {"manual", "openai"},
            )
            self.assertIn(
                "forbidden_words",
                {field["id"] for field in payload["shared_fields"]},
            )
            self.assertFalse((temp_dir / "logs" / "failures.jsonl").exists())
            self.assertEqual(list((temp_dir / "output").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
