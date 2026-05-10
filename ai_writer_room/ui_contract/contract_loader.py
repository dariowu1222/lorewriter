"""Loader helpers for the versioned UI contract."""

from __future__ import annotations

import json
from pathlib import Path

from ai_writer_room.ui_contract.ui_schema import (
    ActionInfo,
    FieldInfo,
    TabInfo,
    UIContract,
)


class UIContractLoader:
    """Load and query the minimal web UI contract."""

    def __init__(
        self,
        path: Path | str = Path("ui_contract/ui_contract.json"),
    ) -> None:
        """Load a UI contract for query helpers."""
        self.contract = self.load_contract(path)

    @staticmethod
    def load_contract(
        path: Path | str = Path("ui_contract/ui_contract.json"),
    ) -> UIContract:
        """Load and validate a UI contract JSON file."""
        contract_path = UIContractLoader._resolve_path(path)
        payload = json.loads(contract_path.read_text(encoding="utf-8"))
        return UIContract.model_validate(payload)

    def list_tabs(self) -> list[TabInfo]:
        """Return frontend tabs from the loaded contract."""
        return list(self.contract.tabs)

    def get_fields_for_mode(self, mode: str) -> dict[str, list[FieldInfo]]:
        """Return shared and mode-specific fields."""
        if mode == "manual":
            mode_fields = self.contract.manual_fields
        elif mode == "openai":
            mode_fields = self.contract.openai_fields
        else:
            mode_fields = []

        return {
            "shared_fields": list(self.contract.shared_fields),
            "mode_fields": list(mode_fields),
        }

    def get_actions_for_mode(self, mode: str) -> dict[str, list[ActionInfo]]:
        """Return shared and mode-specific actions."""
        if mode == "manual":
            mode_actions = self.contract.manual_actions
        elif mode == "openai":
            mode_actions = self.contract.openai_actions
        else:
            mode_actions = []

        return {
            "shared_actions": list(self.contract.shared_actions),
            "mode_actions": list(mode_actions),
        }

    @staticmethod
    def _resolve_path(path: Path | str) -> Path:
        """Resolve contract paths from cwd or package location."""
        candidate = Path(path)
        if candidate.is_absolute() or candidate.exists():
            return candidate

        package_dir = Path(__file__).resolve().parent
        if candidate.parts and candidate.parts[0] == "ui_contract":
            return package_dir.joinpath(*candidate.parts[1:])
        return package_dir / candidate
