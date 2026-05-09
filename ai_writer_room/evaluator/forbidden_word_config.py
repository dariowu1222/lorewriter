"""Config loader for forbidden words and deterministic replacements."""

from __future__ import annotations

import json
from pathlib import Path


class ForbiddenWordConfig:
    """Load and merge forbidden-word replacement dictionaries."""

    @staticmethod
    def load_default(
        path: Path | str = Path("config/forbidden_words.default.json"),
    ) -> dict[str, str]:
        """Load the default forbidden-word replacement config."""
        return ForbiddenWordConfig._load_json_dict(path)

    @staticmethod
    def load_custom(path: Path | str) -> dict[str, str]:
        """Load a custom forbidden-word replacement config."""
        return ForbiddenWordConfig._load_json_dict(path)

    @staticmethod
    def merge(
        defaults: dict[str, str],
        custom: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """Merge default and custom forbidden-word configs."""
        merged = dict(defaults)
        if custom:
            merged.update(custom)
        return merged

    @staticmethod
    def _load_json_dict(path: Path | str) -> dict[str, str]:
        """Load a JSON object as a string-to-string dictionary."""
        config_path = ForbiddenWordConfig._resolve_path(path)
        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Forbidden-word config file not found: {config_path}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Forbidden-word config is not valid JSON: {config_path}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                f"Forbidden-word config must be a JSON object: {config_path}"
            )

        return {str(key): str(value) for key, value in payload.items()}

    @staticmethod
    def _resolve_path(path: Path | str) -> Path:
        """Resolve config paths relative to cwd or the ai_writer_room package."""
        candidate = Path(path)
        if candidate.is_absolute() or candidate.exists():
            return candidate

        package_root = Path(__file__).resolve().parents[1]
        return package_root / candidate

