"""Estimated API cost guard for OpenAI provider runs."""

from __future__ import annotations

import json
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class CostGuard:
    """Estimate and guard OpenAI generation costs using local metadata."""

    def __init__(
        self,
        config_path: Path | str = Path("config/cost_guard.default.json"),
        logs_dir: Path | str = Path("logs"),
    ) -> None:
        """Create a cost guard from local config and logs."""
        self.config_path = self._resolve_package_path(config_path)
        self.logs_dir = self._resolve_package_path(logs_dir)
        self.config = self._load_config(self.config_path)

    def estimate_cost(
        self,
        model: str,
        prompt: str,
        estimated_output_tokens: int = 6500,
    ) -> dict[str, float | int]:
        """Estimate input/output tokens and rough USD cost for one run."""
        estimated_input_tokens = math.ceil(len(prompt) / 4)
        model_prices = self._get_model_prices(model)
        estimated_cost_usd = (
            estimated_input_tokens / 1000 * model_prices["estimated_input_per_1k"]
            + estimated_output_tokens / 1000 * model_prices["estimated_output_per_1k"]
        )

        return {
            "estimated_input_tokens": estimated_input_tokens,
            "estimated_output_tokens": estimated_output_tokens,
            "estimated_cost_usd": round(estimated_cost_usd, 8),
        }

    def check_single_run_budget(self, estimated_cost_usd: float) -> dict[str, object]:
        """Check whether one estimated run fits the configured max cost."""
        limit = float(self.config.get("single_run_max_usd", 0.0))
        if not self.config.get("enabled", True):
            return {
                "passed": True,
                "limit": limit,
                "estimated_cost_usd": estimated_cost_usd,
                "message": "Cost guard disabled.",
            }

        passed = estimated_cost_usd <= limit
        message = (
            "Single-run budget check passed."
            if passed
            else (
                f"Estimated cost ${estimated_cost_usd:.6f} exceeds "
                f"single-run limit ${limit:.6f}."
            )
        )
        return {
            "passed": passed,
            "limit": limit,
            "estimated_cost_usd": estimated_cost_usd,
            "message": message,
        }

    def get_monthly_usage(self) -> dict[str, object]:
        """Estimate current-month usage from generation logs."""
        current_month = datetime.now(UTC).strftime("%Y-%m")
        total_runs = 0
        total_estimated_cost_usd = 0.0
        generations_dir = self.logs_dir / "generations"

        if not generations_dir.exists():
            return {
                "total_runs": total_runs,
                "total_estimated_cost_usd": total_estimated_cost_usd,
                "current_month": current_month,
            }

        for log_path in generations_dir.glob("*/*.json"):
            record = self._load_log_record(log_path)
            if not record or record.get("provider") != "openai":
                continue

            created_at = str(record.get("created_at", ""))
            if not created_at.startswith(current_month):
                continue

            total_runs += 1
            total_estimated_cost_usd += float(record.get("estimated_cost_usd") or 0.0)

        return {
            "total_runs": total_runs,
            "total_estimated_cost_usd": round(total_estimated_cost_usd, 8),
            "current_month": current_month,
        }

    def check_monthly_budget(self) -> dict[str, object]:
        """Check current-month estimated usage against the configured budget."""
        usage = self.get_monthly_usage()
        monthly_budget = float(self.config.get("monthly_budget_usd", 0.0))
        warning_threshold = monthly_budget * float(
            self.config.get("warning_threshold_ratio", 0.8)
        )
        current_usage = float(usage["total_estimated_cost_usd"])

        if not self.config.get("enabled", True):
            return {
                "passed": True,
                "current_usage": usage,
                "monthly_budget": monthly_budget,
                "warning_threshold_reached": False,
                "message": "Cost guard disabled.",
            }

        passed = current_usage <= monthly_budget
        warning_threshold_reached = current_usage >= warning_threshold
        if not passed:
            message = (
                f"Current estimated monthly usage ${current_usage:.6f} exceeds "
                f"monthly budget ${monthly_budget:.6f}."
            )
        elif warning_threshold_reached:
            message = (
                f"Current estimated monthly usage ${current_usage:.6f} reached "
                f"the warning threshold ${warning_threshold:.6f}."
            )
        else:
            message = "Monthly budget check passed."

        return {
            "passed": passed,
            "current_usage": usage,
            "monthly_budget": monthly_budget,
            "warning_threshold_reached": warning_threshold_reached,
            "message": message,
        }

    def _get_model_prices(self, model: str) -> dict[str, float]:
        """Return model prices, falling back to gpt-4o-mini estimates."""
        models = self.config.get("models", {})
        model_config = models.get(model) or models.get("gpt-4o-mini")
        if not model_config:
            return {
                "estimated_input_per_1k": 0.0,
                "estimated_output_per_1k": 0.0,
            }

        return {
            "estimated_input_per_1k": float(
                model_config.get("estimated_input_per_1k", 0.0)
            ),
            "estimated_output_per_1k": float(
                model_config.get("estimated_output_per_1k", 0.0)
            ),
        }

    def _load_config(self, config_path: Path) -> dict[str, Any]:
        """Load cost guard JSON config."""
        return json.loads(config_path.read_text(encoding="utf-8"))

    def _load_log_record(self, log_path: Path) -> dict[str, Any] | None:
        """Load a generation log record, ignoring malformed old logs."""
        try:
            return json.loads(log_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def _resolve_package_path(self, path: Path | str) -> Path:
        """Resolve paths relative to cwd or the ai_writer_room package."""
        candidate = Path(path)
        if candidate.is_absolute() or candidate.exists():
            return candidate

        package_root = Path(__file__).resolve().parents[1]
        return package_root / candidate
