"""Model provider abstractions for storyboard generation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from openai import APIConnectionError, OpenAI, OpenAIError

from ai_writer_room.config import DEFAULT_MODEL
from ai_writer_room.generator.api_client import OpenAIClient


LOCAL_PROVIDER_BASE_URL = "http://localhost:11434/v1"
LOCAL_PROVIDER_MODEL = "qwen2.5:7b"
LOCAL_PROVIDER_API_KEY = "ollama"


class BaseModelProvider(ABC):
    """Base interface for text generation providers."""

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generate raw text from a prompt."""


class OpenAIModelProvider(BaseModelProvider):
    """OpenAI model provider backed by the existing OpenAIClient."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        """Create an OpenAI provider."""
        self.model = model
        self._client = OpenAIClient(api_key=api_key, model=model)

    def generate_text(self, prompt: str) -> str:
        """Generate raw text from OpenAI."""
        return self._client.generate_text(prompt)


class LocalModelProvider(BaseModelProvider):
    """OpenAI-compatible local model provider, such as Ollama."""

    def __init__(
        self,
        base_url: str = LOCAL_PROVIDER_BASE_URL,
        model: str = LOCAL_PROVIDER_MODEL,
        api_key: str = LOCAL_PROVIDER_API_KEY,
    ) -> None:
        """Create a local OpenAI-compatible provider."""
        self.base_url = base_url
        self.model = model
        self._client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=10.0,
            max_retries=0,
        )

    def generate_text(self, prompt: str) -> str:
        """Generate raw text from a local OpenAI-compatible server."""
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
        except APIConnectionError as exc:
            raise RuntimeError(
                f"Local model server not reachable at {self.base_url}"
            ) from exc
        except OpenAIError as exc:
            raise RuntimeError(
                f"Local model generation failed: {exc.__class__.__name__}: {exc}"
            ) from exc

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Local model generation failed: empty response content.")

        return content
