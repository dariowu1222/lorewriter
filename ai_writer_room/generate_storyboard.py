"""Programmatic entry point for storyboard generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


PACKAGE_PARENT = Path(__file__).resolve().parent.parent
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))

from ai_writer_room.evaluator.evaluator import StoryboardEvaluator
from ai_writer_room.generator.story_planner import build_mock_rule_horror_storyboard
from ai_writer_room.schemas.storyboard_schema import Storyboard


def generate_storyboard(
    sub_genre: str,
    output_path: Path | None = None,
    duration_sec: int = 180,
) -> Storyboard:
    """Generate a local mock rule horror storyboard JSON file."""
    storyboard = build_mock_rule_horror_storyboard(
        sub_genre=sub_genre,
        duration_sec=duration_sec,
    )

    if output_path is not None:
        write_storyboard_json(storyboard=storyboard, output_path=output_path)

    return storyboard


def write_storyboard_json(storyboard: Storyboard, output_path: Path) -> None:
    """Write a storyboard as UTF-8 JSON."""
    if hasattr(storyboard, "model_dump"):
        payload = storyboard.model_dump(mode="json")
    else:
        payload = storyboard.dict()

    write_json(payload=payload, output_path=output_path)


def write_json(payload: dict[str, Any], output_path: Path) -> None:
    """Write a JSON payload with stable local formatting."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def build_eval_output_path(output_path: Path) -> Path:
    """Build the evaluator output path next to the storyboard JSON."""
    return output_path.with_suffix(".eval.json")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for mock storyboard generation."""
    parser = argparse.ArgumentParser(
        description="Generate a local mock rule horror storyboard JSON.",
    )
    parser.add_argument(
        "--sub-genre",
        required=True,
        help="Rule horror sub-genre or setting, for example: 地鐵末班車.",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=180,
        help="Target duration in seconds.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/storyboard_mock.json"),
        help="Output JSON path.",
    )
    parser.add_argument(
        "--eval",
        action="store_true",
        dest="run_eval",
        help="Run local evaluator and write a .eval.json file.",
    )
    return parser.parse_args()


def main() -> None:
    """Run storyboard generation from a script entry point."""
    args = parse_args()
    storyboard = generate_storyboard(
        sub_genre=args.sub_genre,
        duration_sec=args.duration,
        output_path=args.output,
    )
    print(f"Mock storyboard written to: {args.output}")

    if args.run_eval:
        eval_result = StoryboardEvaluator().evaluate(storyboard)
        eval_output_path = build_eval_output_path(args.output)
        write_json(payload=eval_result, output_path=eval_output_path)
        print(f"Evaluation written to: {eval_output_path}")


if __name__ == "__main__":
    main()

