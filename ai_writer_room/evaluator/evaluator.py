"""Coordinator for storyboard evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_writer_room.schemas.storyboard_schema import StoryboardDraft


@dataclass(slots=True)
class EvaluationResult:
    """Aggregated evaluator output for a storyboard."""

    score: float | None = None
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class StoryboardEvaluator:
    """Run all storyboard checks and prepare feedback."""

    def evaluate(self, storyboard: StoryboardDraft) -> EvaluationResult:
        """Evaluate a generated storyboard draft."""
        # TODO: Combine pacing, rule, forbidden-word, and future quality checks.
        pass

    def summarize_findings(self, result: EvaluationResult) -> str:
        """Summarize evaluator findings for CLI output or auto-fix."""
        # TODO: Convert structured issues into concise feedback text.
        pass

