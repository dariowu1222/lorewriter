"""Pacing checks for short-form storyboard structure."""

from __future__ import annotations

from dataclasses import dataclass

from ai_writer_room.schemas.storyboard_schema import StoryboardDraft


@dataclass(slots=True)
class PacingIssue:
    """A pacing problem detected in a storyboard."""

    scene_id: str | None
    message: str


@dataclass(slots=True)
class PacingChecker:
    """Validate runtime and scene balance."""

    def check_runtime(
        self,
        storyboard: StoryboardDraft,
        target_minutes: int,
    ) -> list[PacingIssue]:
        """Check whether storyboard timing matches the target runtime."""
        raise NotImplementedError("Runtime pacing checks are planned for v0.2.")

    def check_scene_balance(self, storyboard: StoryboardDraft) -> list[PacingIssue]:
        """Check whether scenes have a usable short-form rhythm."""
        raise NotImplementedError("Scene-balance checks are planned for v0.2.")
