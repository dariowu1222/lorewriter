"""Rule consistency checks for generated storyboards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_writer_room.generator.rule_engine import Rule, RuleEngine
from ai_writer_room.memory.story_bible import StoryBible, WorldRule
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
        story_bible = storyboard.story_bible
        if isinstance(story_bible, StoryBible):
            return [
                self._rule_from_world_rule(world_rule)
                for world_rule in story_bible.world_rules
            ]

        if not isinstance(story_bible, dict):
            return []

        raw_rules = story_bible.get("rules") or story_bible.get("world_rules", [])
        rules: list[Rule] = []

        for raw_rule in raw_rules:
            if isinstance(raw_rule, Rule):
                rules.append(raw_rule)
            elif isinstance(raw_rule, dict):
                rules.append(self._rule_from_dict(raw_rule))

        return rules

    def _rule_from_world_rule(self, world_rule: WorldRule) -> Rule:
        """Convert a Story Bible WorldRule into evaluator Rule shape."""
        expected_scene_ids = [
            world_rule.introduced_scene_id,
            *world_rule.verified_scene_ids,
        ]
        return Rule(
            id=world_rule.id,
            text=world_rule.text,
            category=world_rule.category,
            is_visual=False,
            expected_scene_ids=expected_scene_ids,
        )

    def _rule_from_dict(self, raw_rule: dict[str, Any]) -> Rule:
        """Convert a dictionary into a Rule dataclass."""
        expected_scene_ids = raw_rule.get("expected_scene_ids")
        if expected_scene_ids is None:
            expected_scene_ids = [
                raw_rule.get("introduced_scene_id", ""),
                *raw_rule.get("verified_scene_ids", []),
            ]

        return Rule(
            id=str(raw_rule.get("id", "")),
            text=str(raw_rule.get("text", "")),
            category=str(raw_rule.get("category", "")),
            is_visual=bool(raw_rule.get("is_visual", False)),
            expected_scene_ids=[
                scene_id for scene_id in expected_scene_ids if scene_id
            ],
        )
