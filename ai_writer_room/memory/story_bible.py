"""Story Bible models and storage boundary."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class CharacterProfile(BaseModel):
    """Persistent character information for continuity."""

    name: str
    role: str | None = None
    notes: list[str] = Field(default_factory=list)


class StoryBible(BaseModel):
    """Persistent world, character, and rule context for a story."""

    title: str | None = None
    premise: str | None = None
    rules: list[str] = Field(default_factory=list)
    characters: list[CharacterProfile] = Field(default_factory=list)
    continuity_notes: list[str] = Field(default_factory=list)


class StoryBibleRepository:
    """Load and save Story Bible data."""

    def load(self, path: Path) -> StoryBible:
        """Load a Story Bible from disk."""
        # TODO: Deserialize StoryBible from a structured file.
        pass

    def save(self, bible: StoryBible, path: Path) -> None:
        """Save a Story Bible to disk."""
        # TODO: Serialize StoryBible using pathlib.
        pass

