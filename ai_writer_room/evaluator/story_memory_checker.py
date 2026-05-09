"""Story memory readiness checks for long-form foundations."""

from __future__ import annotations

from dataclasses import is_dataclass
from typing import Any

from ai_writer_room.memory.foreshadow_tracker import ForeshadowItem
from ai_writer_room.memory.story_bible import StoryBible
from ai_writer_room.schemas.storyboard_schema import Storyboard


class StoryMemoryChecker:
    """Check that long-form memory scaffolding exists on a storyboard."""

    def check(self, storyboard: Storyboard) -> dict[str, object]:
        """Return warning-only memory readiness results."""
        warnings: list[str] = []
        stats = self._build_stats(storyboard)

        if not self._has_story_bible(storyboard.story_bible):
            warnings.append("story_bible is missing or empty.")
        if not self._has_memory_summary(storyboard.memory_summary):
            warnings.append("memory_summary is missing or empty.")
        if stats["foreshadow_count"] == 0:
            warnings.append("foreshadowing is missing or empty.")
        if stats["unresolved_foreshadow_count"] < 1:
            warnings.append("at least one unresolved foreshadow item is expected.")
        if stats["world_rule_count"] < 3:
            warnings.append("story_bible.world_rules should contain at least 3 rules.")

        return {
            "passed": not warnings,
            "warnings": warnings,
            "stats": stats,
        }

    def _build_stats(self, storyboard: Storyboard) -> dict[str, int]:
        """Build story-memory summary stats without logging full content."""
        return {
            "character_count": self._count_story_bible_list(
                storyboard.story_bible,
                "characters",
            ),
            "world_rule_count": self._count_story_bible_list(
                storyboard.story_bible,
                "world_rules",
            ),
            "foreshadow_count": len(storyboard.foreshadowing),
            "unresolved_foreshadow_count": self._count_unresolved_foreshadow(
                storyboard.foreshadowing,
            ),
        }

    def _has_story_bible(self, value: StoryBible | dict[Any, Any]) -> bool:
        """Return whether a Story Bible payload has usable content."""
        if isinstance(value, StoryBible):
            return bool(value.characters or value.world_rules)
        if isinstance(value, dict):
            return bool(value)
        return is_dataclass(value)

    def _has_memory_summary(self, value: object) -> bool:
        """Return whether a memory summary payload has usable content."""
        if isinstance(value, dict):
            return bool(value)
        return value is not None

    def _count_story_bible_list(
        self,
        story_bible: StoryBible | dict[Any, Any],
        field_name: str,
    ) -> int:
        """Count a list field on either dataclass or dict Story Bible values."""
        if isinstance(story_bible, StoryBible):
            value = getattr(story_bible, field_name)
        elif isinstance(story_bible, dict):
            value = story_bible.get(field_name, [])
        else:
            value = getattr(story_bible, field_name, [])

        return len(value) if isinstance(value, list) else 0

    def _count_unresolved_foreshadow(
        self,
        items: list[ForeshadowItem] | list[dict],
    ) -> int:
        """Count foreshadowing items that still need payoff."""
        count = 0
        for item in items:
            if isinstance(item, ForeshadowItem):
                status = item.status
            elif isinstance(item, dict):
                status = str(item.get("status", ""))
            else:
                status = str(getattr(item, "status", ""))

            if status == "setup_only":
                count += 1

        return count
