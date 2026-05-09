"""API client boundary for future AI model providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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

