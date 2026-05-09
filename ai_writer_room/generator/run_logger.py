"""Run logging for generation and failure metadata."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


GENERATION_RECORD_FIELDS: tuple[str, ...] = (
    "run_id",
    "created_at",
    "provider",
    "model",
    "sub_genre",
    "duration_sec",
    "output_path",
    "eval_path",
    "success",
    "eval_passed",
    "error_type",
    "error_message",
    "scene_count",
    "rule_check_passed",
    "forbidden_word_check_passed",
    "auto_fix_applied",
    "final_eval_passed",
    "forbidden_words_source",
    "estimated_cost_usd",
    "estimated_input_tokens",
    "estimated_output_tokens",
)

FAILURE_RECORD_FIELDS: tuple[str, ...] = (
    "run_id",
    "created_at",
    "provider",
    "model",
    "sub_genre",
    "duration_sec",
    "error_type",
    "error_message",
    "stage",
)


class RunLogger:
    """Write generation and failure metadata logs."""

    def __init__(self, logs_dir: Path | str = Path("logs")) -> None:
        """Create a logger rooted at the logs directory."""
        candidate = Path(logs_dir)
        if not candidate.is_absolute() and not candidate.exists():
            candidate = Path(__file__).resolve().parents[1] / candidate

        self.logs_dir = candidate

    def create_run_id(self) -> str:
        """Create a unique run id that is safe for filenames."""
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        return f"run_{timestamp}_{uuid4().hex[:8]}"

    def log_generation(self, record: dict) -> Path:
        """Write a generation metadata record."""
        safe_record = self._filter_record(record, GENERATION_RECORD_FIELDS)
        run_id = str(safe_record["run_id"])
        created_at = str(safe_record["created_at"])
        date = created_at[:10] if len(created_at) >= 10 else self._today()

        target_dir = self.logs_dir / "generations" / date
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{run_id}.json"
        target_path.write_text(
            json.dumps(safe_record, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return target_path

    def log_failure(self, record: dict) -> Path:
        """Append a failure metadata record as JSONL."""
        safe_record = self._filter_record(record, FAILURE_RECORD_FIELDS)
        target_path = self.logs_dir / "failures.jsonl"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with target_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(safe_record, ensure_ascii=False) + "\n")
        return target_path

    def _filter_record(self, record: dict, fields: tuple[str, ...]) -> dict:
        """Keep only approved log fields and fill missing values with None."""
        return {field: record.get(field) for field in fields}

    def _today(self) -> str:
        """Return today's UTC date for fallback log paths."""
        return datetime.now(UTC).date().isoformat()
