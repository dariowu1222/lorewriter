"""Arc planning data structures for long-form story foundations."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ArcPhase(BaseModel):
    """A planned long-form story phase."""

    id: str = ""
    name: str = ""
    purpose: str = ""
    emotional_goal: str = ""
    threat_level: int = 1
    target_scene_range: str = ""
    setup_requirements: list[str] = Field(default_factory=list)
    payoff_targets: list[str] = Field(default_factory=list)
    twist_type: str = ""
    status: str = "pending"


class ArcPlan(BaseModel):
    """Six-arc structure for future long-form story generation."""

    title: str = ""
    total_arcs: int = 0
    genre: str = ""
    pacing_style: str = ""
    protagonist_final_goal: str = ""
    core_theme: str = ""
    arcs: list[ArcPhase] = Field(default_factory=list)
