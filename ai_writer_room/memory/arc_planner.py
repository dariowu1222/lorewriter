"""Arc planning data structures for long-form story foundations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ArcPhase:
    """A planned long-form story phase."""

    id: str
    name: str
    purpose: str
    emotional_goal: str
    threat_level: int
    target_scene_range: str
    setup_requirements: list[str] = field(default_factory=list)
    payoff_targets: list[str] = field(default_factory=list)
    twist_type: str = ""
    status: str = "pending"


@dataclass(slots=True)
class ArcPlan:
    """Six-arc structure for future long-form story generation."""

    title: str
    total_arcs: int
    genre: str
    pacing_style: str
    protagonist_final_goal: str
    core_theme: str
    arcs: list[ArcPhase] = field(default_factory=list)
