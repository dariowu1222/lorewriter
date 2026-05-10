"""Shared helpers for smoke tests."""

from __future__ import annotations

from contextlib import contextmanager, redirect_stderr, redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import Iterator
from unittest.mock import patch


TESTS_DIR = Path(__file__).resolve().parent
TEST_DATA_DIR = TESTS_DIR / "test_data"


def sample_path(filename: str) -> Path:
    """Return a path inside tests/test_data."""
    return TEST_DATA_DIR / filename


def load_json(path: Path) -> dict:
    """Load a JSON object from disk."""
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def temp_project_cwd(
    cost_guard_config: dict | None = None,
) -> Iterator[Path]:
    """Create an isolated cwd with output/logs/config directories."""
    original_cwd = Path.cwd()
    with TemporaryDirectory() as temp_dir_text:
        temp_dir = Path(temp_dir_text)
        (temp_dir / "output").mkdir()
        (temp_dir / "logs").mkdir()
        if cost_guard_config is not None:
            config_dir = temp_dir / "config"
            config_dir.mkdir()
            (config_dir / "cost_guard.default.json").write_text(
                json.dumps(cost_guard_config, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        os.chdir(temp_dir)
        try:
            yield temp_dir
        finally:
            os.chdir(original_cwd)


def run_main_with_args(args: list[str]) -> tuple[int, str, str]:
    """Run generate_storyboard.main with patched argv and captured IO."""
    from ai_writer_room import generate_storyboard

    stdout = StringIO()
    stderr = StringIO()
    exit_code = 0
    argv = ["generate_storyboard.py", *args]

    with patch.object(sys, "argv", argv), redirect_stdout(stdout), redirect_stderr(
        stderr,
    ):
        try:
            generate_storyboard.main()
        except SystemExit as exc:
            exit_code = int(exc.code or 0)

    return exit_code, stdout.getvalue(), stderr.getvalue()


def run_cli_with_args(args: list[str]) -> tuple[int, str, str]:
    """Run ai_writer_room.cli.main with patched argv and captured IO."""
    from ai_writer_room import cli

    stdout = StringIO()
    stderr = StringIO()
    exit_code = 0
    argv = ["cli.py", *args]

    with patch.object(sys, "argv", argv), redirect_stdout(stdout), redirect_stderr(
        stderr,
    ):
        try:
            cli.main()
        except SystemExit as exc:
            exit_code = int(exc.code or 0)

    return exit_code, stdout.getvalue(), stderr.getvalue()


def tiny_cost_guard_config() -> dict:
    """Return a config that blocks any OpenAI generation before API calls."""
    return {
        "enabled": True,
        "default_currency": "USD",
        "monthly_budget_usd": 20.0,
        "single_run_max_usd": 0.000001,
        "warning_threshold_ratio": 0.8,
        "models": {
            "gpt-4o-mini": {
                "estimated_input_per_1k": 0.00015,
                "estimated_output_per_1k": 0.0006,
            }
        },
    }
