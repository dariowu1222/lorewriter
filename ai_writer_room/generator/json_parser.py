"""JSON parsing helpers for model-generated storyboard text."""

from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any

from pydantic import ValidationError

from ai_writer_room.schemas.storyboard_schema import Storyboard


class StoryboardJsonParser:
    """Extract and validate Storyboard JSON from raw model text."""

    def extract_json_text(self, raw_text: str) -> str:
        """Extract JSON text from raw output or fenced code blocks."""
        text = raw_text.strip()

        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise ValueError(
                "Could not find a JSON object in model output. "
                f"Raw preview: {self._preview(raw_text)}"
            )

        return text[start : end + 1]

    def parse_storyboard(self, raw_text: str) -> Storyboard:
        """Parse raw model output into a Storyboard Pydantic model."""
        json_text = self.extract_json_text(raw_text)

        try:
            payload: dict[str, Any] = json.loads(json_text)
        except JSONDecodeError as exc:
            raise ValueError(
                "Failed to decode storyboard JSON. "
                f"Raw preview: {self._preview(raw_text)}"
            ) from exc

        try:
            if hasattr(Storyboard, "model_validate"):
                return Storyboard.model_validate(payload)
            return Storyboard.parse_obj(payload)
        except ValidationError as exc:
            raise ValueError(
                "Storyboard JSON did not match the Storyboard schema. "
                f"Raw preview: {self._preview(raw_text)}"
            ) from exc

    def _preview(self, raw_text: str) -> str:
        """Return a safe preview for parse errors."""
        return raw_text[:500].replace("\n", "\\n")

