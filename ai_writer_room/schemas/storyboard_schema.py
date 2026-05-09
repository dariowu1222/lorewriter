"""Pydantic schema for v0.1 storyboard JSON."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ai_writer_room.schemas.scene_schema import SceneDraft


class StoryboardDraft(BaseModel):
    """Generated 3-minute rule horror storyboard."""

    title: str | None = None
    logline: str | None = None
    target_minutes: int = 3
    rules: list[str] = Field(default_factory=list)
    scenes: list[SceneDraft] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

