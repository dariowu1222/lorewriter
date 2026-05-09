"""Pydantic schemas for storyboard scenes."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DialogueLine(BaseModel):
    """A single dialogue line in a storyboard scene."""

    speaker: str
    text: str


class Scene(BaseModel):
    """Scene schema for the v0.1 storyboard JSON output."""

    id: str
    title: str
    function: str
    mood: str
    bgm_intensity: int = Field(ge=1, le=5)
    time_in_story: str
    narration_zh: str
    dialogue_lines: list[DialogueLine] = Field(default_factory=list)
    rule_refs: list[str] = Field(default_factory=list)
    foreshadow_refs: list[str] = Field(default_factory=list)


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
