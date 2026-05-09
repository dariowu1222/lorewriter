"""Programmatic entry point for storyboard generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Literal


PACKAGE_PARENT = Path(__file__).resolve().parent.parent
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))

from ai_writer_room.config import DEFAULT_MODEL
from ai_writer_room.evaluator.evaluator import StoryboardEvaluator
from ai_writer_room.generator.json_parser import StoryboardJsonParser
from ai_writer_room.generator.model_provider import (
    LOCAL_PROVIDER_MODEL,
    BaseModelProvider,
    LocalModelProvider,
    OpenAIModelProvider,
)
from ai_writer_room.generator.prompt_builder import PromptBuilder
from ai_writer_room.generator.story_planner import build_mock_rule_horror_storyboard
from ai_writer_room.schemas.storyboard_schema import Storyboard


ProviderName = Literal["mock", "openai", "local"]


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


def generate_storyboard_from_api(
    sub_genre: str,
    output_path: Path | None = None,
    duration_sec: int = 180,
    model: str = DEFAULT_MODEL,
) -> Storyboard:
    """Generate a storyboard through OpenAI and parse it into the schema."""
    return generate_storyboard_from_provider(
        provider_name="openai",
        sub_genre=sub_genre,
        output_path=output_path,
        duration_sec=duration_sec,
        model=model,
    )


def generate_storyboard_from_provider(
    provider_name: ProviderName,
    sub_genre: str,
    output_path: Path | None = None,
    duration_sec: int = 180,
    model: str | None = None,
) -> Storyboard:
    """Generate a storyboard with the selected provider."""
    if provider_name == "mock":
        return generate_storyboard(
            sub_genre=sub_genre,
            output_path=output_path,
            duration_sec=duration_sec,
        )

    prompt = PromptBuilder().build_rule_horror_prompt(
        sub_genre=sub_genre,
        duration_sec=duration_sec,
    )
    provider = build_model_provider(provider_name=provider_name, model=model)
    raw_text = provider.generate_text(prompt)
    storyboard = StoryboardJsonParser().parse_storyboard(raw_text)

    if output_path is not None:
        write_storyboard_json(storyboard=storyboard, output_path=output_path)

    return storyboard


def build_model_provider(
    provider_name: ProviderName,
    model: str | None = None,
) -> BaseModelProvider:
    """Create a model provider for OpenAI or local generation."""
    if provider_name == "openai":
        return OpenAIModelProvider(model=model or DEFAULT_MODEL)
    if provider_name == "local":
        return LocalModelProvider(model=model or LOCAL_PROVIDER_MODEL)

    raise ValueError(f"Unsupported model provider: {provider_name}")


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
    """Parse command line arguments for storyboard generation."""
    parser = argparse.ArgumentParser(
        description="Generate a rule horror storyboard JSON.",
    )
    parser.add_argument(
        "--provider",
        choices=["mock", "openai", "local"],
        default="mock",
        help="Generation provider. Default: mock.",
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
    parser.add_argument(
        "--use-api",
        action="store_true",
        help="Legacy alias for --provider openai.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "Model for openai/local providers. Defaults: "
            f"openai={DEFAULT_MODEL}, local={LOCAL_PROVIDER_MODEL}."
        ),
    )
    parser.add_argument(
        "--print-prompt",
        action="store_true",
        help="Print the assembled rule horror prompt without calling a model.",
    )
    return parser.parse_args()


def resolve_provider_name(args: argparse.Namespace) -> ProviderName:
    """Resolve provider selection, including the legacy --use-api alias."""
    if args.use_api:
        return "openai"
    return args.provider


def main() -> None:
    """Run storyboard generation from a script entry point."""
    args = parse_args()

    if args.print_prompt:
        prompt = PromptBuilder().build_rule_horror_prompt(
            sub_genre=args.sub_genre,
            duration_sec=args.duration,
        )
        print(prompt)
        return

    provider_name = resolve_provider_name(args)

    try:
        storyboard = generate_storyboard_from_provider(
            provider_name=provider_name,
            sub_genre=args.sub_genre,
            duration_sec=args.duration,
            output_path=args.output,
            model=args.model,
        )
    except (RuntimeError, ValueError) as exc:
        print(
            (
                f"Generation failed for provider '{provider_name}' "
                f"({exc.__class__.__name__}): {exc}"
            ),
            file=sys.stderr,
        )
        raise SystemExit(1) from None

    print(f"{provider_name.capitalize()} storyboard written to: {args.output}")

    if args.run_eval:
        eval_result = StoryboardEvaluator().evaluate(storyboard)
        eval_output_path = build_eval_output_path(args.output)
        write_json(payload=eval_result, output_path=eval_output_path)
        print(f"Evaluation written to: {eval_output_path}")


if __name__ == "__main__":
    main()

