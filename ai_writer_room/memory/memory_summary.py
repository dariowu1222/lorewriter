"""Memory summary support for long-form generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_writer_room.schemas.storyboard_schema import Storyboard


@dataclass(slots=True)
class MemorySummary:
    """Compressed story state for future long-form generation."""

    current_arc_summary: str
    protagonist_goal: str
    protagonist_status: str
    known_rules: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)
    current_threat_level: int = 1
    emotional_curve: str = ""
    last_major_event: str = ""


@dataclass(slots=True)
class MemorySummarizer:
    """Create and update memory summaries."""

    def summarize_storyboard(self, storyboard: Storyboard) -> MemorySummary:
        """Create a memory summary from a storyboard draft."""
        # TODO: Add LLM-assisted long-form memory summarization in a future step.
        raise NotImplementedError

    def update_summary(
        self,
        current_summary: MemorySummary,
        new_events: list[str],
    ) -> MemorySummary:
        """Update an existing memory summary with new events."""
        # TODO: Merge new events without losing unresolved threads.
        raise NotImplementedError

