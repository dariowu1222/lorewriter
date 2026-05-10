"""Pydantic schemas for render-friendly storyboard input."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RenderDialogueLine(BaseModel):
    """Dialogue text prepared for render and subtitle pipelines."""

    speaker: str
    text: str


class RenderScene(BaseModel):
    """A storyboard scene normalized for downstream render tooling."""

    scene_id: str
    title: str
    narration: str
    duration_sec: int
    mood: str
    bgm_intensity: int
    camera_style: str
    visual_style: str
    image_prompt: str
    tts_text: str
    subtitle_text: str
    dialogue_lines: list[RenderDialogueLine] = Field(default_factory=list)
    transition_type: str = "hard_cut"


class RenderProject(BaseModel):
    """A render-ready project payload for future video pipelines."""

    project_title: str
    provider: str
    model: str
    target_resolution: str
    fps: int
    total_duration_sec: int
    visual_theme: str
    scenes: list[RenderScene] = Field(default_factory=list)
