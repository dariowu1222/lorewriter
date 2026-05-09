"""Pydantic schema for v0.1 storyboard JSON."""

from __future__ import annotations

from pydantic import BaseModel, Field

from ai_writer_room.memory.arc_planner import ArcPlan
from ai_writer_room.memory.foreshadow_tracker import ForeshadowItem
from ai_writer_room.memory.memory_summary import MemorySummary
from ai_writer_room.memory.story_bible import StoryBible
from ai_writer_room.schemas.scene_schema import Scene, SceneDraft


class Storyboard(BaseModel):
    """Storyboard schema for v0.1 local JSON output."""

    title: str
    sub_genre: str
    target_duration_sec: int
    generated_at: str
    model: str
    cost_usd: float
    prologue: str
    story_bible: StoryBible | dict
    scenes: list[Scene] = Field(default_factory=list)
    memory_summary: MemorySummary | dict
    foreshadowing: list[ForeshadowItem] | list[dict] = Field(default_factory=list)
    arc_plan: ArcPlan | dict | None = None


class StoryboardDraft(BaseModel):
    """Generated 3-minute rule horror storyboard."""

    title: str | None = None
    logline: str | None = None
    target_minutes: int = 3
    rules: list[str] = Field(default_factory=list)
    scenes: list[SceneDraft] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
