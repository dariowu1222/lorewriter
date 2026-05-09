"""Pydantic schemas for storyboard scenes."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SceneBeat(BaseModel):
    """A single narrative beat within a scene."""

    order: int
    description: str


class SceneDraft(BaseModel):
    """Draft schema for one storyboard scene."""

    scene_id: str
    title: str | None = None
    summary: str
    beats: list[SceneBeat] = Field(default_factory=list)
    estimated_seconds: int | None = None
    rule_signals: list[str] = Field(default_factory=list)
    foreshadows: list[str] = Field(default_factory=list)

