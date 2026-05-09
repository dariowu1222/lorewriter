"""Rule system helpers for rule horror stories."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuleSet:
    """Narrative rules and constraints for a rule horror premise."""

    rules: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)
    reveal_policy: str | None = None


@dataclass(slots=True)
class RuleEngine:
    """Create and validate story rules before generation."""

    def build_rules(self, premise: str) -> RuleSet:
        """Build a candidate rule set from the story premise."""
        # TODO: Extract or synthesize rules from the premise.
        pass

    def validate_rule_consistency(self, rules: RuleSet) -> list[str]:
        """Return consistency issues found in a rule set."""
        # TODO: Check contradictions, missing payoffs, and unclear rules.
        pass

