"""Dataclass schemas for render-friendly storyboard input."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RenderDialogueLine:
    """Dialogue text prepared for render and subtitle pipelines."""

    speaker: str
    text: str


@dataclass(slots=True)
class RenderScene:
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
    dialogue_lines: list[RenderDialogueLine] = field(default_factory=list)
    transition_type: str = "hard_cut"


@dataclass(slots=True)
class RenderProject:
    """A render-ready project payload for future video pipelines."""

    project_title: str
    provider: str
    model: str
    target_resolution: str
    fps: int
    total_duration_sec: int
    visual_theme: str
    scenes: list[RenderScene] = field(default_factory=list)
