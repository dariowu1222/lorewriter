"""Runtime configuration for AI Writer Room."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
DEFAULT_API_KEY_FILE_TEXT = "~/.config/ai_writer_room/openai_api_key"
API_KEY_FILE_PATH = Path(
    os.getenv("OPENAI_API_KEY_FILE")
    or Path.home() / ".config" / "ai_writer_room" / "openai_api_key"
)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@dataclass(frozen=True, slots=True)
class Settings:
    """Application settings for paths, model defaults, and API access."""

    project_root: Path
    prompt_dir: Path
    output_dir: Path
    log_dir: Path
    model: str
    openai_api_key: str
    api_key_file_path: Path


def load_openai_api_key() -> str:
    """Load the OpenAI API key from env first, then from the local key file."""
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key.strip()

    if API_KEY_FILE_PATH.exists():
        file_key = API_KEY_FILE_PATH.read_text(encoding="utf-8").strip()
        if file_key:
            return file_key

    raise RuntimeError(
        "OpenAI API key not found. Set OPENAI_API_KEY, set OPENAI_API_KEY_FILE, "
        f"or create the default local key file at {DEFAULT_API_KEY_FILE_TEXT}."
    )


def get_settings(project_root: Path | None = None) -> Settings:
    """Build settings for CLI and generation entry points."""
    root = project_root or Path(__file__).resolve().parent
    return Settings(
        project_root=root,
        prompt_dir=root / "prompts",
        output_dir=root / "output",
        log_dir=root / "logs",
        model=DEFAULT_MODEL,
        openai_api_key=load_openai_api_key(),
        api_key_file_path=API_KEY_FILE_PATH,
    )
