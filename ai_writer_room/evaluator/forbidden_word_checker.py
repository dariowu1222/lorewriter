"""Forbidden word and weak wording checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

from ai_writer_room.schemas.storyboard_schema import Storyboard


DEFAULT_FORBIDDEN_WORDS: tuple[str, ...] = (
    "詭異",
    "莫名",
    "感到不安",
    "恐怖",
    "陰森",
    "突然",
    "忽然",
    "無法形容",
    "說不上來",
    "有種感覺",
)


@dataclass(slots=True)
class ForbiddenWordHit:
    """A forbidden word match found in generated storyboard text."""

    word: str
    scene_id: str
    field: str
    count: int


@dataclass(slots=True)
class ForbiddenWordChecker:
    """Scan storyboard text for configured forbidden words."""

    forbidden_words: Sequence[str] = DEFAULT_FORBIDDEN_WORDS

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
            "passed": total_hits <= 2,
        }

    def scan_text(
        self,
        text: str,
        forbidden_words: Sequence[str] | None = None,
    ) -> list[ForbiddenWordHit]:
        """Scan plain text for forbidden words."""
        words = forbidden_words or self.forbidden_words
        return [
            ForbiddenWordHit(word=word, scene_id="", field="text", count=count)
            for word in words
            if (count := text.count(word)) > 0
        ]

    def scan_storyboard(
        self,
        storyboard: Storyboard,
        forbidden_words: Sequence[str] | None = None,
    ) -> list[ForbiddenWordHit]:
        """Scan a storyboard and return raw forbidden word hits."""
        checker = ForbiddenWordChecker(
            forbidden_words=forbidden_words or self.forbidden_words,
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
                scene_id=scene_id,
                field=field,
                count=count,
            )
            for word in self.forbidden_words
            if (count := text.count(word)) > 0
        ]

