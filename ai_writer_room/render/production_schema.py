"""Schemas for local production handoff payloads.

These payloads are still pre-render artifacts. They do not create audio,
images, storyboards, or videos directly; they prepare clean JSON contracts for
future TTS, image, storyboard, and video pipelines.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class VoiceLine(BaseModel):
    """One render scene converted into a voice-generation script line."""

    scene_id: str
    title: str
    speaker: str
    text: str
    duration_sec: int
    voice_style: str
    output_filename: str
    status: str = "script_ready"


class VoiceProject(BaseModel):
    """Voice pipeline input prepared from a render project."""

    project_title: str
    total_duration_sec: int
    format: str = "wav"
    lines: list[VoiceLine] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ImagePromptItem(BaseModel):
    """One image prompt prepared for a future image-generation pipeline."""

    scene_id: str
    title: str
    prompt: str
    negative_prompt: str
    visual_style: str
    aspect_ratio: str
    output_filename: str
    status: str = "prompt_ready"


class ImagePromptProject(BaseModel):
    """Image prompt package prepared from a render project."""

    project_title: str
    total_images: int
    items: list[ImagePromptItem] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ShotItem(BaseModel):
    """One storyboard shot derived from a render scene."""

    shot_id: str
    scene_id: str
    title: str
    duration_sec: int
    camera_style: str
    visual_style: str
    image_prompt: str
    subtitle_text: str
    transition_type: str


class ShotStoryboardProject(BaseModel):
    """A render-friendly shot list for visual planning."""

    project_title: str
    total_shots: int
    shots: list[ShotItem] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class VideoManifestScene(BaseModel):
    """One scene entry for a future video assembly manifest."""

    scene_id: str
    duration_sec: int
    image_asset: str
    voice_asset: str
    subtitle_text: str
    transition_type: str
    bgm_intensity: int


class VideoManifestProject(BaseModel):
    """Video assembly manifest prepared for future ffmpeg/render tools."""

    project_title: str
    target_resolution: str
    fps: int
    total_duration_sec: int
    visual_theme: str
    status: str = "manifest_ready"
    scenes: list[VideoManifestScene] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
