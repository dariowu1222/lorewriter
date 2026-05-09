"""Forbidden word and unsafe wording checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ai_writer_room.schemas.storyboard_schema import StoryboardDraft


@dataclass(slots=True)
class ForbiddenWordHit:
    """A forbidden word match found in generated text."""

    word: str
    location: str


@dataclass(slots=True)
class ForbiddenWordChecker:
    """Scan story text for configured forbidden words."""

    def scan_text(
        self,
        text: str,
        forbidden_words: Sequence[str],
    ) -> list[ForbiddenWordHit]:
        """Scan plain text for forbidden words."""
        # TODO: Implement case and locale aware forbidden word matching.
        pass

    def scan_storyboard(
        self,
        storyboard: StoryboardDraft,
        forbidden_words: Sequence[str],
    ) -> list[ForbiddenWordHit]:
        """Scan a storyboard for forbidden words."""
        # TODO: Walk storyboard fields and collect forbidden word matches.
        pass

