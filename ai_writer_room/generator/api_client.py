"""API client boundary for future AI model providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openai import OpenAI, OpenAIError

from ai_writer_room.config import DEFAULT_MODEL, load_openai_api_key


@dataclass(slots=True)
class GenerationRequest:
    """Request payload for text generation."""

    prompt: str
    model: str
    temperature: float
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class GenerationResponse:
    """Raw response returned by a model provider."""

    text: str
    raw: dict[str, Any] | None = None


class APIClient:
    """Boundary object for OpenAI or other model provider integrations."""

    def generate_text(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text from a prompt request."""
        # TODO: Implement provider-specific API call without leaking SDK details.
        pass


class OpenAIClient:
    """Small OpenAI client wrapper for storyboard text generation."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        """Create an OpenAI API client without exposing credentials."""
        self.model = model
        self._client = OpenAI(api_key=api_key or load_openai_api_key())

    def generate_text(self, prompt: str) -> str:
        """Generate raw text from a prompt using OpenAI Chat Completions."""
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.8,
            )
        except OpenAIError as exc:
            raise RuntimeError(
                f"OpenAI generation failed: {exc.__class__.__name__}: {exc}"
            ) from exc

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("OpenAI generation failed: empty response content.")

        return content
