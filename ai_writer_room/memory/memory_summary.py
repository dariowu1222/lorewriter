"""Memory summary support for long-form generation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ai_writer_room.schemas.storyboard_schema import Storyboard


class MemorySummary(BaseModel):
    """Compressed story state for future long-form generation."""

    current_arc_summary: str = ""
    protagonist_goal: str = ""
    protagonist_status: str = ""
    current_arc_id: str = ""
    current_arc_goal: str = ""
    latest_payoff: str = ""
    known_rules: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    active_foreshadow_ids: list[str] = Field(default_factory=list)
    current_threat_level: int = 1
    emotional_curve: str = ""
    last_major_event: str = ""


class MemorySummarizer:
    """Create and update memory summaries."""

    def summarize_storyboard(self, storyboard: Storyboard) -> MemorySummary:
        """Create a memory summary from a storyboard draft."""
        raise NotImplementedError("LLM-assisted memory summarization is planned in v0.2.")

    def update_summary(
        self,
        current_summary: MemorySummary,
        new_events: list[str],
    ) -> MemorySummary:
        """Update an existing memory summary with new events."""
        raise NotImplementedError("Incremental memory updates are planned in v0.2.")
