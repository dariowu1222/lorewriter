"""Memory summary support for long-form generation."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_writer_room.schemas.storyboard_schema import StoryboardDraft


@dataclass(slots=True)
class MemorySummary:
    """Compressed memory state for previous story content."""

    summary_text: str
    key_events: list[str] = field(default_factory=list)
    unresolved_threads: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MemorySummarizer:
    """Create and update memory summaries."""

    def summarize_storyboard(self, storyboard: StoryboardDraft) -> MemorySummary:
        """Create a memory summary from a storyboard draft."""
        # TODO: Extract durable plot, rule, character, and foreshadow data.
        pass

    def update_summary(
        self,
        current_summary: MemorySummary,
        new_events: list[str],
    ) -> MemorySummary:
        """Update an existing memory summary with new events."""
        # TODO: Merge new events without losing unresolved threads.
        pass

