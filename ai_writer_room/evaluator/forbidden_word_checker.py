"""Forbidden word and weak wording checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Sequence

from ai_writer_room.evaluator.forbidden_word_config import ForbiddenWordConfig
from ai_writer_room.schemas.storyboard_schema import Storyboard


DEFAULT_FORBIDDEN_WORDS = tuple(ForbiddenWordConfig.load_default().keys())


def build_forbidden_word_pattern(word: str) -> re.Pattern[str]:
    """Build a regex pattern with word boundaries for ASCII terms."""
    escaped_word = re.escape(word)
    if re.search(r"[A-Za-z0-9_]", word):
        return re.compile(rf"\b{escaped_word}\b")
    return re.compile(escaped_word)


@dataclass(slots=True)
class ForbiddenWordHit:
    """A forbidden word match found in generated storyboard text."""

    word: str
    replacement: str
    scene_id: str
    field: str
    count: int


class ForbiddenWordChecker:
    """Scan storyboard text for configured forbidden words."""

    def __init__(self, forbidden_words: dict[str, str] | None = None) -> None:
        """Create a checker using default or caller-provided forbidden words."""
        self.forbidden_words = (
            forbidden_words
            if forbidden_words is not None
            else ForbiddenWordConfig.load_default()
        )

    def check_storyboard(self, storyboard: Storyboard) -> dict[str, object]:
        """Check narration and dialogue lines for forbidden words."""
        hits: list[ForbiddenWordHit] = []

        for scene in storyboard.scenes:
            hits.extend(
                self._scan_field(
                    text=scene.narration_zh,
                    scene_id=scene.id,
                    field="narration_zh",
                )
            )
            for index, line in enumerate(scene.dialogue_lines):
                hits.extend(
                    self._scan_field(
                        text=line.text,
                        scene_id=scene.id,
                        field=f"dialogue_lines[{index}].text",
                    )
                )

        total_hits = sum(hit.count for hit in hits)
        return {
            "total_hits": total_hits,
            "hits": [asdict(hit) for hit in hits],
            "passed": total_hits == 0,
        }

    def scan_text(
        self,
        text: str,
        forbidden_words: Sequence[str] | dict[str, str] | None = None,
    ) -> list[ForbiddenWordHit]:
        """Scan plain text for forbidden words."""
        words = self._normalize_forbidden_words(forbidden_words)
        return [
            ForbiddenWordHit(
                word=word,
                replacement=replacement,
                scene_id="",
                field="text",
                count=count,
            )
            for word, replacement in words.items()
            if (count := len(build_forbidden_word_pattern(word).findall(text))) > 0
        ]

    def scan_storyboard(
        self,
        storyboard: Storyboard,
        forbidden_words: Sequence[str] | dict[str, str] | None = None,
    ) -> list[ForbiddenWordHit]:
        """Scan a storyboard and return raw forbidden word hits."""
        checker = ForbiddenWordChecker(
            forbidden_words=self._normalize_forbidden_words(forbidden_words),
        )
        result = checker.check_storyboard(storyboard)
        return [ForbiddenWordHit(**hit) for hit in result["hits"]]

    def _scan_field(
        self,
        text: str,
        scene_id: str,
        field: str,
    ) -> list[ForbiddenWordHit]:
        """Scan a single storyboard field."""
        return [
            ForbiddenWordHit(
                word=word,
                replacement=replacement,
                scene_id=scene_id,
                field=field,
                count=count,
            )
            for word, replacement in self.forbidden_words.items()
            if (count := len(build_forbidden_word_pattern(word).findall(text))) > 0
        ]

    def _normalize_forbidden_words(
        self,
        forbidden_words: Sequence[str] | dict[str, str] | None,
    ) -> dict[str, str]:
        """Normalize old sequence inputs and new replacement dictionaries."""
        if forbidden_words is None:
            return self.forbidden_words
        if isinstance(forbidden_words, dict):
            return forbidden_words
        return {word: "" for word in forbidden_words}
