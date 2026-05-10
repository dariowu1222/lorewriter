"""Warning-only checks for long-form Arc Plan readiness."""

from __future__ import annotations

from ai_writer_room.memory.arc_planner import ArcPhase, ArcPlan
from ai_writer_room.schemas.storyboard_schema import Storyboard


class ArcChecker:
    """Validate the v0.1 fixed six-arc planning scaffold."""

    def check(self, storyboard: Storyboard) -> dict[str, object]:
        """Check arc plan structure and return warning-only results."""
        warnings: list[str] = []
        arcs = self._get_arcs(storyboard.arc_plan)
        arc_ids = [arc.id for arc in arcs]
        unique_arc_ids = {arc_id for arc_id in arc_ids if arc_id}

        has_midpoint_twist = self._contains_arc_text(arcs, "中段反轉")
        has_main_twist = self._contains_arc_text(arcs, "主反轉")
        has_tail_sting = self._contains_arc_text(arcs, "尾刀")

        if storyboard.arc_plan is None or not arcs:
            warnings.append("arc_plan is missing or empty.")
        if len(arcs) != 6:
            warnings.append("arc_plan should contain exactly 6 arcs.")
        if len(unique_arc_ids) != len(arcs):
            warnings.append("arc ids should be unique and non-empty.")
        if not has_midpoint_twist:
            warnings.append("arc_plan should include a midpoint twist arc.")
        if not has_main_twist:
            warnings.append("arc_plan should include a main twist arc.")
        if not has_tail_sting:
            warnings.append("arc_plan should include a tail-sting arc.")

        for arc in arcs:
            arc_id = arc.id or "<unknown>"
            if not arc.emotional_goal:
                warnings.append(f"arc {arc_id} is missing emotional_goal.")
            if not 1 <= int(arc.threat_level) <= 10:
                warnings.append(f"arc {arc_id} threat_level should be 1-10.")

        return {
            "passed": not warnings,
            "warnings": warnings,
            "stats": {
                "arc_count": len(arcs),
                "unique_arc_count": len(unique_arc_ids),
                "has_midpoint_twist": has_midpoint_twist,
                "has_main_twist": has_main_twist,
                "has_tail_sting": has_tail_sting,
            },
        }

    def _get_arcs(self, arc_plan: ArcPlan | None) -> list[ArcPhase]:
        """Extract ArcPhase items from an ArcPlan."""
        if arc_plan is None:
            return []
        return list(arc_plan.arcs)

    def _contains_arc_text(self, arcs: list[ArcPhase], pattern: str) -> bool:
        """Return whether an arc contains a required phrase."""
        return any(pattern in self._combined_arc_text(arc) for arc in arcs)

    def _combined_arc_text(self, arc: ArcPhase) -> str:
        """Join important arc fields for simple v0.1 checks."""
        return " ".join((arc.name, arc.purpose, arc.twist_type))
