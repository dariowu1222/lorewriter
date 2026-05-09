"""Prompt assembly utilities for storyboard generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class PromptContext:
    """Structured inputs used to render a generation prompt."""

    premise: str
    target_minutes: int = 3
    genre: str = "rule_horror"
    constraints: list[str] = field(default_factory=list)
    story_bible: str | None = None


@dataclass(slots=True)
class PromptBuilder:
    """Build prompts from templates and structured story context."""

    template_dir: Path

    def load_template(self, template_name: str) -> str:
        """Load a prompt template by filename."""
        # TODO: Read template content from template_dir using pathlib.
        pass

    def build_rule_horror_prompt(self, context: PromptContext) -> str:
        """Build the v0.1 rule horror storyboard prompt."""
        # TODO: Render rule_horror.tmpl with PromptContext values.
        pass

