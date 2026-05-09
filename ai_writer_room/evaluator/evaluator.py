"""Coordinator for storyboard evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_writer_room.evaluator.arc_checker import ArcChecker
from ai_writer_room.evaluator.forbidden_word_checker import ForbiddenWordChecker
from ai_writer_room.evaluator.rule_checker import RuleChecker
from ai_writer_room.evaluator.story_memory_checker import StoryMemoryChecker
from ai_writer_room.schemas.storyboard_schema import Storyboard


@dataclass(slots=True)
class EvaluationResult:
    """Aggregated evaluator output for a storyboard."""

    score: float | None = None
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


class StoryboardEvaluator:
    """Run local rule and forbidden-word checks for a storyboard."""

    def __init__(self, forbidden_words: dict[str, str] | None = None) -> None:
        """Create an evaluator with configurable forbidden words."""
        self.rule_checker = RuleChecker()
        self.forbidden_word_checker = ForbiddenWordChecker(
            forbidden_words=forbidden_words,
        )
        self.story_memory_checker = StoryMemoryChecker()
        self.arc_checker = ArcChecker()

    def evaluate(self, storyboard: Storyboard) -> dict[str, object]:
        """Evaluate a generated storyboard draft."""
        rule_check = self.rule_checker.check(storyboard)
        forbidden_word_check = self.forbidden_word_checker.check_storyboard(storyboard)
        story_memory_check = self.story_memory_checker.check(storyboard)
        arc_check = self.arc_checker.check(storyboard)

        return {
            "passed": bool(
                rule_check.get("passed") and forbidden_word_check.get("passed")
            ),
            "rule_check": rule_check,
            "forbidden_word_check": forbidden_word_check,
            "story_memory_check": story_memory_check,
            "arc_check": arc_check,
        }

    def summarize_findings(self, result: EvaluationResult) -> str:
        """Summarize evaluator findings for CLI output or auto-fix."""
        # TODO: Convert structured issues into concise feedback text.
        pass
