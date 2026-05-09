"""High-level planning for short and long-form story structure."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class StoryPlanRequest:
    """Input used to create a story plan."""

    premise: str
    target_minutes: int = 3
    tone: str = "rule_horror"
    constraints: list[str] = field(default_factory=list)


@dataclass(slots=True)
class StoryPlanner:
    """Plan story arcs, scene slots, and pacing targets."""

    def create_outline(self, request: StoryPlanRequest) -> list[str]:
        """Create a high-level outline for storyboard generation."""
        # TODO: Add short-form arc planning for v0.1.
        pass

    def allocate_pacing(self, request: StoryPlanRequest) -> dict[str, int]:
        """Allocate target seconds for each planned story segment."""
        # TODO: Map target runtime into setup, escalation, reveal, and ending.
        pass

