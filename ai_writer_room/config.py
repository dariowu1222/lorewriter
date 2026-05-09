"""Runtime configuration for AI Writer Room."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    """Application settings for paths and model defaults."""

    project_root: Path
    prompt_dir: Path
    output_dir: Path
    log_dir: Path
    model: str


def get_settings(project_root: Path | None = None) -> Settings:
    """Build settings for CLI and generation entry points."""
    # TODO: Load environment variables with python-dotenv.
    # TODO: Resolve prompt, output, and log directories using pathlib.
    pass

