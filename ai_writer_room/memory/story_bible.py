"""Story Bible models for long-form continuity."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class CharacterProfile(BaseModel):
    """Persistent character information for continuity."""

    id: str = ""
    name: str = ""
    role: str = ""
    traits: list[str] = Field(default_factory=list)
    secrets: list[str] = Field(default_factory=list)
    introduced_scene_id: str = "S01"
    status: str = "active"
    suspicion_level: int = 0


class WorldRule(BaseModel):
    """Persistent world-rule information for long-form rule tracking."""

    id: str = ""
    text: str = ""
    category: str = ""
    introduced_scene_id: str = "S01"
    verified_scene_ids: list[str] = Field(default_factory=list)
    broken_scene_ids: list[str] = Field(default_factory=list)
    is_contradictory: bool = False


class StoryBible(BaseModel):
    """Persistent story-state container for long-form generation."""

    title: str = ""
    sub_genre: str = ""
    protagonist_name: str = ""
    world_summary: str = ""
    tone_keywords: list[str] = Field(default_factory=list)
    core_theme: str = ""
    arc_summary: str = ""
    active_arc_id: str = ""
    current_story_stage: str = ""
    characters: list[CharacterProfile] = Field(default_factory=list)
    world_rules: list[WorldRule] = Field(default_factory=list)
    major_questions: list[str] = Field(default_factory=list)
    hidden_truths: list[str] = Field(default_factory=list)


class StoryBibleRepository:
    """Load and save Story Bible data."""

    def load(self, path: Path) -> StoryBible:
        """Load a Story Bible from disk."""
        payload = json.loads(path.read_text(encoding="utf-8"))
        if hasattr(StoryBible, "model_validate"):
            return StoryBible.model_validate(payload)
        return StoryBible.parse_obj(payload)

    def save(self, bible: StoryBible, path: Path) -> None:
        """Save a Story Bible to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        if hasattr(bible, "model_dump"):
            payload = bible.model_dump(mode="json")
        else:
            payload = bible.dict()
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
