"""Foreshadowing setup and payoff tracking."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_writer_room.schemas.storyboard_schema import Storyboard


@dataclass(slots=True)
class ForeshadowItem:
    """A planted hint that may need payoff later."""

    id: str
    setup_scene_id: str
    setup_text: str
    expected_payoff_scene_id: str
    planned_payoff_arc_id: str = "A06"
    payoff_scene_id: str | None = None
    payoff_text: str | None = None
    status: str = "setup_only"


class ForeshadowTracker:
    """Build and inspect foreshadowing state."""

    def build_initial_foreshadowing(
        self,
        storyboard: Storyboard,
    ) -> list[ForeshadowItem]:
        """Build initial foreshadowing items from storyboard scene refs."""
        items: list[ForeshadowItem] = []
        seen_ids: set[str] = set()

        for scene in storyboard.scenes:
            for foreshadow_id in scene.foreshadow_refs:
                if foreshadow_id in seen_ids:
                    continue
                seen_ids.add(foreshadow_id)
                items.append(
                    ForeshadowItem(
                        id=foreshadow_id,
                        setup_scene_id=scene.id,
                        setup_text=(
                            f"{scene.id} plants {foreshadow_id}: {scene.title}"
                        ),
                        expected_payoff_scene_id=self._expected_payoff_scene_id(
                            foreshadow_id,
                        ),
                        planned_payoff_arc_id=self._planned_payoff_arc_id(
                            foreshadow_id,
                        ),
                    )
                )

        if len(items) < 3:
            fallback_scene_id = storyboard.scenes[0].id if storyboard.scenes else "S01"
            while len(items) < 3:
                next_index = len(items) + 1
                items.append(
                    ForeshadowItem(
                        id=f"F{next_index:02d}",
                        setup_scene_id=fallback_scene_id,
                        setup_text=f"Fallback foreshadow setup F{next_index:02d}",
                        expected_payoff_scene_id="S12",
                        planned_payoff_arc_id="A06",
                    )
                )

        return items[: max(3, len(items))]

    def get_unresolved_items(
        self,
        items: list[ForeshadowItem],
    ) -> list[ForeshadowItem]:
        """Return foreshadowing items that still need payoff."""
        return [item for item in items if item.status == "setup_only"]

    def _expected_payoff_scene_id(self, foreshadow_id: str) -> str:
        """Map foreshadow ids to simple expected payoff scenes."""
        payoff_map = {
            "F01": "S11",
            "F02": "S09",
            "F03": "S12",
            "F04": "S10",
        }
        return payoff_map.get(foreshadow_id, "S12")

    def _planned_payoff_arc_id(self, foreshadow_id: str) -> str:
        """Map foreshadow ids to simple long-form payoff arcs."""
        payoff_arc_map = {
            "F01": "A05",
            "F02": "A04",
            "F03": "A06",
            "F04": "A05",
        }
        return payoff_arc_map.get(foreshadow_id, "A06")
