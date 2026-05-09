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

        json_text = self._find_balanced_json_object(text)
        if json_text is None:
            raise ValueError(
                "Could not find a balanced JSON object in model output. "
                f"Raw preview: {self._preview(raw_text)}"
            )

        return json_text

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

    def _find_balanced_json_object(self, text: str) -> str | None:
        """Find the first balanced top-level JSON object in text."""
        start = -1
        depth = 0
        in_string = False
        escaped = False

        for index, char in enumerate(text):
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
                continue

            if char == "{":
                if depth == 0:
                    start = index
                depth += 1
            elif char == "}":
                if depth == 0:
                    continue
                depth -= 1
                if depth == 0 and start != -1:
                    return text[start : index + 1]

        return None
