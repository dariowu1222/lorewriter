"""Story Bible models for long-form continuity."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(slots=True)
class CharacterProfile:
    """Persistent character information for continuity."""

    id: str
    name: str
    role: str
    traits: list[str] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)
    introduced_scene_id: str = "S01"
    status: str = "active"
    suspicion_level: int = 0


@dataclass(slots=True)
class WorldRule:
    """Persistent world-rule information for long-form rule tracking."""

    id: str
    text: str
    category: str
    introduced_scene_id: str
    verified_scene_ids: list[str] = field(default_factory=list)
    broken_scene_ids: list[str] = field(default_factory=list)
    is_contradictory: bool = False


@dataclass(slots=True)
class StoryBible:
    """Persistent story-state container for long-form generation."""

    title: str
    sub_genre: str
    protagonist_name: str
    world_summary: str
    tone_keywords: list[str] = field(default_factory=list)
    core_theme: str = ""
    arc_summary: str = ""
    active_arc_id: str = ""
    current_story_stage: str = ""
    characters: list[CharacterProfile] = field(default_factory=list)
    world_rules: list[WorldRule] = field(default_factory=list)
    major_questions: list[str] = field(default_factory=list)
    hidden_truths: list[str] = field(default_factory=list)


class StoryBibleRepository:
    """Load and save Story Bible data."""

    def load(self, path: Path) -> StoryBible:
        """Load a Story Bible from disk."""
        payload = json.loads(path.read_text(encoding="utf-8"))
        return StoryBible(
            title=payload["title"],
            sub_genre=payload["sub_genre"],
            protagonist_name=payload["protagonist_name"],
            world_summary=payload["world_summary"],
            tone_keywords=list(payload.get("tone_keywords", [])),
            core_theme=str(payload.get("core_theme", "")),
            arc_summary=str(payload.get("arc_summary", "")),
            active_arc_id=str(payload.get("active_arc_id", "")),
            current_story_stage=str(payload.get("current_story_stage", "")),
            characters=[
                CharacterProfile(**character)
                for character in payload.get("characters", [])
            ],
            world_rules=[WorldRule(**rule) for rule in payload.get("world_rules", [])],
            major_questions=list(payload.get("major_questions", [])),
            hidden_truths=list(payload.get("hidden_truths", [])),
        )

    def save(self, bible: StoryBible, path: Path) -> None:
        """Save a Story Bible to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(asdict(bible), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
