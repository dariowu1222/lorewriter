"""Rule system helpers for rule horror stories."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_writer_room.schemas.storyboard_schema import Storyboard


@dataclass(slots=True)
class Rule:
    """A rule horror constraint that should appear in storyboard scenes."""

    id: str
    text: str
    category: str
    is_visual: bool
    expected_scene_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RuleSet:
    """Narrative rules and constraints for a rule horror premise."""

    rules: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)
    reveal_policy: str | None = None


@dataclass(slots=True)
class RuleEngine:
    """Create and validate story rules before generation and evaluation."""

    def build_mock_rules(self, sub_genre: str, rules_count: int = 5) -> list[Rule]:
        """Build mock v0.1 rule horror rules for a sub-genre."""
        templates: list[Rule] = [
            Rule(
                id="R01",
                text=f"在{sub_genre}裡，聽到自己的名字時不可回頭。",
                category="聲音規則",
                is_visual=False,
                expected_scene_ids=["S02", "S03", "S06", "S11"],
            ),
            Rule(
                id="R02",
                text=f"在{sub_genre}裡，看見倒影多出一個人時必須閉眼十秒。",
                category="空間規則",
                is_visual=True,
                expected_scene_ids=["S04", "S07", "S12"],
            ),
            Rule(
                id="R03",
                text=f"在{sub_genre}裡，空座位上出現票根時不可觸碰。",
                category="物件規則",
                is_visual=True,
                expected_scene_ids=["S05", "S09", "S12"],
            ),
            Rule(
                id="R04",
                text=f"在{sub_genre}裡，時間停在整點時必須留在原位。",
                category="時間規則",
                is_visual=False,
                expected_scene_ids=["S06", "S09", "S10"],
            ),
            Rule(
                id="R05",
                text=f"在{sub_genre}裡，自稱工作人員的人不能直接相信。",
                category="身分規則",
                is_visual=False,
                expected_scene_ids=["S08", "S09", "S11"],
            ),
        ]
        safe_count = max(rules_count, 0)
        return templates[:safe_count]

    def check_rule_refs_used(
        self,
        storyboard: Storyboard,
        rules: list[Rule],
    ) -> dict[str, object]:
        """Check whether each rule id is referenced by at least one scene."""
        expected_rule_ids = {rule.id for rule in rules}
        used_rule_ids: set[str] = set()

        for scene in storyboard.scenes:
            used_rule_ids.update(scene.rule_refs)

        missing_rule_ids = sorted(expected_rule_ids - used_rule_ids)
        unknown_rule_ids = sorted(used_rule_ids - expected_rule_ids)

        return {
            "total_rules": len(rules),
            "used_rules": len(expected_rule_ids & used_rule_ids),
            "missing_rules": len(missing_rule_ids),
            "missing_rule_ids": missing_rule_ids,
            "unknown_rule_ids": unknown_rule_ids,
            "passed": not missing_rule_ids and not unknown_rule_ids,
        }

    def build_rules(self, premise: str) -> RuleSet:
        """Build a candidate rule set from the story premise."""
        # TODO: Extract or synthesize rules from the premise.
        pass

    def validate_rule_consistency(self, rules: RuleSet) -> list[str]:
        """Return consistency issues found in a rule set."""
        # TODO: Check contradictions, missing payoffs, and unclear rules.
        pass

