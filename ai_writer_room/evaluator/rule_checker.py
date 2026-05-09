"""Rule consistency checks for generated storyboards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_writer_room.generator.rule_engine import Rule, RuleEngine
from ai_writer_room.schemas.storyboard_schema import Storyboard


@dataclass(slots=True)
class RuleChecker:
    """Validate that storyboard rule references cover all known rules."""

    rule_engine: RuleEngine | None = None

    def check(self, storyboard: Storyboard) -> dict[str, object]:
        """Run rule reference checks through RuleEngine."""
        engine = self.rule_engine or RuleEngine()
        rules = self._load_rules_from_story_bible(storyboard)
        if not rules:
            rules = engine.build_mock_rules(sub_genre=storyboard.sub_genre)

        return engine.check_rule_refs_used(storyboard=storyboard, rules=rules)

    def check_rule_consistency(self, storyboard: Storyboard) -> list[str]:
        """Find contradictions or unclear rules in the storyboard."""
        # TODO: Add deeper consistency checks in a future evaluator step.
        return []

    def check_rule_payoff(self, storyboard: Storyboard) -> list[str]:
        """Find rules or warnings that do not receive payoff."""
        # TODO: Track rule setup and payoff across the storyboard.
        return []

    def _load_rules_from_story_bible(self, storyboard: Storyboard) -> list[Rule]:
        """Load Rule objects from storyboard.story_bible when available."""
        raw_rules = storyboard.story_bible.get("rules", [])
        rules: list[Rule] = []

        for raw_rule in raw_rules:
            if isinstance(raw_rule, Rule):
                rules.append(raw_rule)
            elif isinstance(raw_rule, dict):
                rules.append(self._rule_from_dict(raw_rule))

        return rules

    def _rule_from_dict(self, raw_rule: dict[str, Any]) -> Rule:
        """Convert a dictionary into a Rule dataclass."""
        return Rule(
            id=str(raw_rule.get("id", "")),
            text=str(raw_rule.get("text", "")),
            category=str(raw_rule.get("category", "")),
            is_visual=bool(raw_rule.get("is_visual", False)),
            expected_scene_ids=list(raw_rule.get("expected_scene_ids", [])),
        )

