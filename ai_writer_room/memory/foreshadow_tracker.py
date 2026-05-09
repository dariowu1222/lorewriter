"""Foreshadowing setup and payoff tracking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ForeshadowItem:
    """A planted hint that may need payoff later."""

    item_id: str
    setup_scene_id: str
    description: str
    payoff_scene_id: str | None = None
    resolved: bool = False


@dataclass(slots=True)
class ForeshadowTracker:
    """Track unresolved and resolved foreshadowing items."""

    def register(self, item: ForeshadowItem) -> None:
        """Register a foreshadowing setup."""
        # TODO: Store the item in future memory state.
        pass

    def resolve(self, item_id: str, payoff_scene_id: str) -> ForeshadowItem:
        """Mark a foreshadowing item as resolved."""
        # TODO: Find the item and attach payoff scene metadata.
        pass

    def list_unresolved(self) -> list[ForeshadowItem]:
        """List foreshadowing items that still need payoff."""
        # TODO: Return unresolved items from future tracker state.
        pass

