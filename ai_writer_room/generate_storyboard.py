"""Programmatic entry point for storyboard generation."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
import sys
from typing import Any, Literal


PACKAGE_PARENT = Path(__file__).resolve().parent.parent
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))

from ai_writer_room.config import DEFAULT_MODEL
from ai_writer_room.evaluator.auto_fix import LocalAutoFixer
from ai_writer_room.evaluator.evaluator import StoryboardEvaluator
from ai_writer_room.evaluator.forbidden_word_config import ForbiddenWordConfig
from ai_writer_room.generator.cost_guard import CostGuard
from ai_writer_room.generator.generation_mode import (
    GenerationMode,
    GenerationModeInfo,
    GenerationModeRegistry,
)
from ai_writer_room.generator.json_parser import StoryboardJsonParser
from ai_writer_room.generator.model_provider import (
    LOCAL_PROVIDER_MODEL,
    BaseModelProvider,
    LocalModelProvider,
    OpenAIModelProvider,
)
from ai_writer_room.generator.prompt_builder import PromptBuilder
from ai_writer_room.generator.run_logger import RunLogger
from ai_writer_room.generator.story_planner import (
    build_initial_arc_plan,
    build_initial_memory_summary,
    build_initial_story_bible,
    build_mock_rule_horror_storyboard,
)
from ai_writer_room.memory.arc_planner import ArcPlan
from ai_writer_room.memory.foreshadow_tracker import ForeshadowTracker
from ai_writer_room.memory.memory_summary import MemorySummary
from ai_writer_room.memory.story_bible import StoryBible
from ai_writer_room.render.render_adapter import RenderAdapter
from ai_writer_room.render.render_schema import RenderProject
from ai_writer_room.schemas.storyboard_schema import Storyboard
from ai_writer_room.ui_contract.contract_loader import UIContractLoader


ProviderName = Literal["mock", "openai", "local", "manual"]


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
    initialize_story_memory(storyboard)

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
    if provider_name == "manual":
        raise ValueError("Manual provider requires --manual-response for parsing.")

    prompt = PromptBuilder().build_rule_horror_prompt(
        sub_genre=sub_genre,
        duration_sec=duration_sec,
    )
    if provider_name == "openai":
        run_budget_guard(
            prompt=prompt,
            model_name=model or DEFAULT_MODEL,
            cost_ref={},
            ignore_budget_guard=False,
        )
    provider = build_model_provider(provider_name=provider_name, model=model)
    raw_text = provider.generate_text(prompt)
    storyboard = StoryboardJsonParser().parse_storyboard(raw_text)
    initialize_story_memory(storyboard)

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


def build_storyboard_without_output(
    provider_name: ProviderName,
    sub_genre: str | None,
    duration_sec: int,
    model: str | None,
    manual_response: Path | None,
    stage_ref: dict[str, str],
    cost_ref: dict[str, float | int],
    ignore_budget_guard: bool = False,
) -> Storyboard:
    """Build a storyboard while exposing coarse failure stages to the CLI."""
    if provider_name == "manual":
        if manual_response is None:
            raise ValueError("Manual provider requires --manual-response for parsing.")
        stage_ref["stage"] = "json_parse"
        raw_text = manual_response.read_text(encoding="utf-8")
        return StoryboardJsonParser().parse_storyboard(raw_text)

    if sub_genre is None:
        raise ValueError("--sub-genre is required for this provider.")

    if provider_name == "mock":
        stage_ref["stage"] = "model_generate"
        return generate_storyboard(
            sub_genre=sub_genre,
            duration_sec=duration_sec,
        )

    stage_ref["stage"] = "prompt_build"
    prompt = PromptBuilder().build_rule_horror_prompt(
        sub_genre=sub_genre,
        duration_sec=duration_sec,
    )

    if provider_name == "openai":
        stage_ref["stage"] = "budget_guard"
        run_budget_guard(
            prompt=prompt,
            model_name=model or DEFAULT_MODEL,
            cost_ref=cost_ref,
            ignore_budget_guard=ignore_budget_guard,
        )

    stage_ref["stage"] = "model_generate"
    provider = build_model_provider(provider_name=provider_name, model=model)
    raw_text = provider.generate_text(prompt)

    stage_ref["stage"] = "json_parse"
    return StoryboardJsonParser().parse_storyboard(raw_text)


def write_manual_prompt_file(
    sub_genre: str,
    duration_sec: int,
    output_path: Path,
) -> None:
    """Write a prompt for manual copy/paste generation."""
    prompt = PromptBuilder().build_rule_horror_prompt(
        sub_genre=sub_genre,
        duration_sec=duration_sec,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt, encoding="utf-8")


def print_manual_prompt_instructions(output_path: Path) -> None:
    """Print manual provider next-step instructions."""
    print(f"Manual prompt written to: {output_path}")
    print("Next steps:")
    print("1. 請把 manual_prompt.txt 的內容貼到 ChatGPT / Claude / Gemini")
    print("2. 請模型只回傳 JSON")
    print("3. 將回傳結果存成 output/manual_response.json")
    print("4. 再執行 manual response parse 指令")


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
        choices=["mock", "openai", "local", "manual"],
        default="mock",
        help="Generation provider. Default: mock.",
    )
    parser.add_argument(
        "--sub-genre",
        default=None,
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
        "--manual-response",
        type=Path,
        default=None,
        help="Manual provider response file to parse into Storyboard JSON.",
    )
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Apply deterministic local fixes after a failed evaluator run.",
    )
    parser.add_argument(
        "--forbidden-words-file",
        type=Path,
        default=None,
        help="Custom forbidden-word replacement JSON file.",
    )
    parser.add_argument(
        "--ignore-budget-guard",
        action="store_true",
        help="Warn but do not block OpenAI runs that exceed budget guard checks.",
    )
    parser.add_argument(
        "--print-prompt",
        action="store_true",
        help="Print the assembled rule horror prompt without calling a model.",
    )
    parser.add_argument(
        "--export-render-input",
        action="store_true",
        help="Export render-friendly JSON next to the storyboard output.",
    )
    parser.add_argument(
        "--list-generation-modes",
        action="store_true",
        help="Print UI-ready generation mode metadata and exit.",
    )
    parser.add_argument(
        "--print-ui-contract",
        action="store_true",
        help="Print the minimal web UI contract and exit.",
    )
    return parser.parse_args()


def resolve_provider_name(args: argparse.Namespace) -> ProviderName:
    """Resolve provider selection, including the legacy --use-api alias."""
    if args.use_api:
        return "openai"
    return args.provider


def resolve_model_name(provider_name: ProviderName, model: str | None) -> str:
    """Resolve the model name used in run metadata."""
    if provider_name == "mock":
        return "local-mock-v0.1"
    if provider_name == "local":
        return model or LOCAL_PROVIDER_MODEL
    if provider_name == "manual":
        return "manual"
    return model or DEFAULT_MODEL


def list_generation_modes_payload() -> list[dict[str, Any]]:
    """Return UI-ready generation mode metadata as JSON-safe dictionaries."""
    return [
        mode_info.model_dump(mode="json")
        for mode_info in GenerationModeRegistry.list_modes()
    ]


def ui_contract_payload() -> dict[str, Any]:
    """Return the UI contract as a JSON-safe dictionary."""
    return UIContractLoader.load_contract().model_dump(mode="json")


def get_generation_mode_info_for_provider(
    provider_name: ProviderName,
) -> GenerationModeInfo | None:
    """Return public mode metadata for manual/openai providers."""
    try:
        mode = GenerationMode(provider_name)
    except ValueError:
        return None
    return GenerationModeRegistry.get_mode_info(mode)


def require_sub_genre(sub_genre: str | None) -> str:
    """Require sub-genre for prompt-producing flows."""
    if not sub_genre:
        raise ValueError("--sub-genre is required for this command.")
    return sub_genre


def initialize_story_memory(storyboard: Storyboard) -> dict[str, bool | int | str]:
    """Ensure long-form memory scaffolding exists on a storyboard."""
    if not _has_story_bible(storyboard.story_bible):
        storyboard.story_bible = build_initial_story_bible(storyboard)
    ensure_story_bible_arc_metadata(storyboard)

    if not _has_memory_summary(storyboard.memory_summary):
        storyboard.memory_summary = build_initial_memory_summary(storyboard)
    ensure_memory_summary_arc_metadata(storyboard)

    if not storyboard.foreshadowing:
        storyboard.foreshadowing = ForeshadowTracker().build_initial_foreshadowing(
            storyboard,
        )

    if not _has_arc_plan(storyboard.arc_plan):
        storyboard.arc_plan = build_initial_arc_plan(storyboard)

    return {
        "story_bible_initialized": _has_story_bible(storyboard.story_bible),
        "memory_summary_initialized": _has_memory_summary(storyboard.memory_summary),
        "foreshadow_initialized": bool(storyboard.foreshadowing),
        "unresolved_foreshadow_count": count_unresolved_foreshadow(storyboard),
        "arc_plan_initialized": _has_arc_plan(storyboard.arc_plan),
        "arc_count": get_arc_count(storyboard),
        "active_arc_id": get_active_arc_id(storyboard),
    }


def _has_story_bible(value: StoryBible) -> bool:
    """Return whether Story Bible data is present and usable."""
    return bool(value.characters or value.world_rules)


def _has_memory_summary(value: MemorySummary) -> bool:
    """Return whether memory summary data is present and usable."""
    return bool(value.current_arc_summary or value.known_rules)


def _has_arc_plan(value: ArcPlan | None) -> bool:
    """Return whether arc plan data is present and usable."""
    return bool(value and value.arcs)


def ensure_story_bible_arc_metadata(storyboard: Storyboard) -> None:
    """Fill missing Arc metadata on Story Bible values."""
    if not storyboard.story_bible.arc_summary:
        storyboard.story_bible.arc_summary = (
            "A01 世界建立啟動，主角正在接觸第一批規則。"
        )
    if not storyboard.story_bible.active_arc_id:
        storyboard.story_bible.active_arc_id = "A01"
    if not storyboard.story_bible.current_story_stage:
        storyboard.story_bible.current_story_stage = "世界建立"


def ensure_memory_summary_arc_metadata(storyboard: Storyboard) -> None:
    """Fill missing Arc metadata on Memory Summary values."""
    active_foreshadow_ids = sorted(
        {
            foreshadow_ref
            for scene in storyboard.scenes
            for foreshadow_ref in scene.foreshadow_refs
        }
    )

    if not storyboard.memory_summary.current_arc_id:
        storyboard.memory_summary.current_arc_id = "A01"
    if not storyboard.memory_summary.current_arc_goal:
        storyboard.memory_summary.current_arc_goal = (
            "建立世界、主角處境與第一規則。"
        )
    if not storyboard.memory_summary.latest_payoff:
        storyboard.memory_summary.latest_payoff = "尚未發生"
    if not storyboard.memory_summary.active_foreshadow_ids:
        storyboard.memory_summary.active_foreshadow_ids = active_foreshadow_ids


def count_unresolved_foreshadow(storyboard: Storyboard) -> int:
    """Count foreshadowing entries that still need payoff."""
    return sum(
        1
        for item in storyboard.foreshadowing
        if item.status == "setup_only"
    )


def build_render_output_path(output_path: Path) -> Path:
    """Build render input path next to a storyboard output path."""
    if output_path.suffix:
        return output_path.with_suffix(".render.json")
    return output_path / "render_input.json"


def export_render_input(
    storyboard: Storyboard,
    storyboard_output_path: Path,
) -> tuple[RenderProject, Path]:
    """Export a render-friendly JSON file derived from a storyboard."""
    render_project = RenderAdapter().storyboard_to_render_project(storyboard)
    render_output_path = build_render_output_path(storyboard_output_path)
    write_json(
        payload=render_project.model_dump(mode="json"),
        output_path=render_output_path,
    )
    return render_project, render_output_path


def build_render_metadata(render_project: RenderProject | None) -> dict[str, int | bool]:
    """Build safe render metadata without storing full render payload."""
    if render_project is None:
        return {
            "render_input_exported": False,
            "render_scene_count": 0,
            "render_total_duration_sec": 0,
        }

    return {
        "render_input_exported": True,
        "render_scene_count": len(render_project.scenes),
        "render_total_duration_sec": render_project.total_duration_sec,
    }


def get_arc_count(storyboard: Storyboard) -> int:
    """Return the current arc count without exposing full arc content."""
    if storyboard.arc_plan is None:
        return 0
    return len(storyboard.arc_plan.arcs)


def get_active_arc_id(storyboard: Storyboard) -> str:
    """Return the active arc id from Story Bible or Arc Plan metadata."""
    if storyboard.story_bible.active_arc_id:
        return storyboard.story_bible.active_arc_id

    if storyboard.arc_plan is not None:
        for arc in storyboard.arc_plan.arcs:
            if arc.status == "active":
                return arc.id

    return ""


def utc_now_text() -> str:
    """Return a UTC timestamp for run metadata."""
    return datetime.now(UTC).isoformat()


def build_generation_record(
    run_id: str,
    created_at: str,
    provider_name: ProviderName,
    model_name: str,
    args: argparse.Namespace,
    eval_result: dict[str, Any] | None,
    eval_output_path: Path | None,
    storyboard: Storyboard,
    auto_fix_applied: bool,
    final_eval_passed: bool | None,
    forbidden_words_source: str,
    cost_ref: dict[str, float | int],
    memory_init_result: dict[str, bool | int | str],
    render_metadata: dict[str, int | bool],
) -> dict[str, Any]:
    """Build safe generation metadata without prompt or raw model output."""
    rule_check = eval_result.get("rule_check", {}) if eval_result else {}
    forbidden_check = eval_result.get("forbidden_word_check", {}) if eval_result else {}
    generation_mode_info = get_generation_mode_info_for_provider(provider_name)

    return {
        "run_id": run_id,
        "created_at": created_at,
        "provider": provider_name,
        "model": model_name,
        "sub_genre": args.sub_genre or storyboard.sub_genre,
        "duration_sec": args.duration,
        "output_path": str(args.output),
        "eval_path": str(eval_output_path) if eval_output_path else None,
        "success": True,
        "eval_passed": eval_result.get("passed") if eval_result else None,
        "error_type": None,
        "error_message": None,
        "scene_count": len(storyboard.scenes),
        "rule_check_passed": rule_check.get("passed") if eval_result else None,
        "forbidden_word_check_passed": (
            forbidden_check.get("passed") if eval_result else None
        ),
        "auto_fix_applied": auto_fix_applied,
        "final_eval_passed": final_eval_passed,
        "forbidden_words_source": forbidden_words_source,
        "estimated_cost_usd": cost_ref.get("estimated_cost_usd", 0.0),
        "estimated_input_tokens": cost_ref.get("estimated_input_tokens", 0),
        "estimated_output_tokens": cost_ref.get("estimated_output_tokens", 0),
        "story_bible_initialized": memory_init_result.get(
            "story_bible_initialized",
            False,
        ),
        "memory_summary_initialized": memory_init_result.get(
            "memory_summary_initialized",
            False,
        ),
        "foreshadow_initialized": memory_init_result.get(
            "foreshadow_initialized",
            False,
        ),
        "unresolved_foreshadow_count": memory_init_result.get(
            "unresolved_foreshadow_count",
            0,
        ),
        "arc_plan_initialized": memory_init_result.get(
            "arc_plan_initialized",
            False,
        ),
        "arc_count": memory_init_result.get("arc_count", 0),
        "active_arc_id": memory_init_result.get("active_arc_id", ""),
        "render_input_exported": render_metadata.get("render_input_exported", False),
        "render_scene_count": render_metadata.get("render_scene_count", 0),
        "render_total_duration_sec": render_metadata.get(
            "render_total_duration_sec",
            0,
        ),
        "generation_mode": (
            generation_mode_info.mode if generation_mode_info is not None else ""
        ),
        "generation_mode_display_name": (
            generation_mode_info.display_name
            if generation_mode_info is not None
            else ""
        ),
        "used_manual_pipeline": provider_name == "manual",
        "used_api_pipeline": provider_name == "openai",
    }


def build_failure_record(
    run_id: str,
    created_at: str,
    provider_name: ProviderName,
    model_name: str,
    args: argparse.Namespace,
    error: Exception,
    stage: str,
) -> dict[str, Any]:
    """Build safe failure metadata without prompt or raw model output."""
    return {
        "run_id": run_id,
        "created_at": created_at,
        "provider": provider_name,
        "model": model_name,
        "sub_genre": args.sub_genre or "",
        "duration_sec": args.duration,
        "error_type": error.__class__.__name__,
        "error_message": sanitize_log_error_message(error=error, stage=stage),
        "stage": stage,
    }


def sanitize_log_error_message(error: Exception, stage: str) -> str:
    """Keep raw prompt/model/manual response content out of logs."""
    if stage in {"json_parse", "schema_validate"}:
        return (
            f"{error.__class__.__name__} during {stage}; "
            "raw content omitted from logs."
        )
    lower_message = str(error).lower()
    if "api key" in lower_message or "openai_api_key" in lower_message:
        return (
            f"{error.__class__.__name__} during {stage}; "
            "credential detail omitted from logs."
        )
    return str(error)


def load_forbidden_words_config(
    custom_path: Path | None,
) -> tuple[dict[str, str], str]:
    """Load default or default+custom forbidden-word config."""
    defaults = ForbiddenWordConfig.load_default()
    if custom_path is None:
        return defaults, "default"

    custom = ForbiddenWordConfig.load_custom(custom_path)
    return ForbiddenWordConfig.merge(defaults=defaults, custom=custom), "default+custom"


def run_budget_guard(
    prompt: str,
    model_name: str,
    cost_ref: dict[str, float | int],
    ignore_budget_guard: bool,
) -> None:
    """Estimate and enforce OpenAI budget guard checks."""
    guard = CostGuard()
    estimate = guard.estimate_cost(model=model_name, prompt=prompt)
    cost_ref.update(estimate)

    single_run_check = guard.check_single_run_budget(
        float(estimate["estimated_cost_usd"])
    )
    monthly_check = guard.check_monthly_budget()

    if monthly_check.get("warning_threshold_reached"):
        print(
            f"Budget warning: {monthly_check['message']}",
            file=sys.stderr,
        )

    failed_messages = [
        str(check["message"])
        for check in (single_run_check, monthly_check)
        if not check.get("passed")
    ]
    if not failed_messages:
        return

    message = " ".join(failed_messages)
    if ignore_budget_guard:
        print(f"Budget guard warning ignored: {message}", file=sys.stderr)
        return

    raise RuntimeError(message)


def build_eval_payload(
    before_fix: dict[str, Any],
    after_fix: dict[str, Any] | None,
    auto_fix_applied: bool,
) -> dict[str, Any]:
    """Build eval JSON payload for optional auto-fix runs."""
    if after_fix is None:
        return before_fix

    return {
        "before_fix": before_fix,
        "after_fix": after_fix,
        "auto_fix_applied": auto_fix_applied,
        "final_passed": after_fix.get("passed"),
    }


def get_final_eval_result(eval_payload: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return the final evaluator result from plain or auto-fix eval JSON."""
    if eval_payload is None:
        return None
    if "after_fix" in eval_payload:
        return eval_payload["after_fix"]
    return eval_payload


def main() -> None:
    """Run storyboard generation from a script entry point."""
    args = parse_args()

    try:
        if args.print_ui_contract:
            print(
                json.dumps(
                    ui_contract_payload(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return

        if args.list_generation_modes:
            print(
                json.dumps(
                    list_generation_modes_payload(),
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return

        if args.print_prompt:
            prompt = PromptBuilder().build_rule_horror_prompt(
                sub_genre=require_sub_genre(args.sub_genre),
                duration_sec=args.duration,
            )
            print(prompt)
            return

        provider_name = resolve_provider_name(args)

        if provider_name == "manual" and args.manual_response is None:
            write_manual_prompt_file(
                sub_genre=require_sub_genre(args.sub_genre),
                duration_sec=args.duration,
                output_path=args.output,
            )
            print_manual_prompt_instructions(args.output)
            return
        if args.auto_fix and not args.run_eval:
            raise ValueError("--auto-fix requires --eval.")
    except ValueError as exc:
        print(f"Command failed ({exc.__class__.__name__}): {exc}", file=sys.stderr)
        raise SystemExit(1) from None

    model_name = resolve_model_name(provider_name=provider_name, model=args.model)
    logger = RunLogger()
    run_id = logger.create_run_id()
    created_at = utc_now_text()
    stage_ref = {"stage": "model_generate"}
    auto_fix_applied = False
    final_eval_passed: bool | None = None
    forbidden_words_source = "default"
    cost_ref: dict[str, float | int] = {
        "estimated_cost_usd": 0.0,
        "estimated_input_tokens": 0,
        "estimated_output_tokens": 0,
    }
    memory_init_result: dict[str, bool | int | str] = {
        "story_bible_initialized": False,
        "memory_summary_initialized": False,
        "foreshadow_initialized": False,
        "unresolved_foreshadow_count": 0,
        "arc_plan_initialized": False,
        "arc_count": 0,
        "active_arc_id": "",
    }
    render_project: RenderProject | None = None
    render_metadata = build_render_metadata(render_project)

    try:
        if args.run_eval:
            stage_ref["stage"] = "evaluator"
            forbidden_words, forbidden_words_source = load_forbidden_words_config(
                args.forbidden_words_file,
            )
        else:
            forbidden_words = {}

        storyboard = build_storyboard_without_output(
            provider_name=provider_name,
            sub_genre=args.sub_genre,
            duration_sec=args.duration,
            model=args.model,
            manual_response=args.manual_response,
            stage_ref=stage_ref,
            cost_ref=cost_ref,
            ignore_budget_guard=args.ignore_budget_guard,
        )
        memory_init_result = initialize_story_memory(storyboard)

        stage_ref["stage"] = "output_write"
        write_storyboard_json(storyboard=storyboard, output_path=args.output)
        print(f"{provider_name.capitalize()} storyboard written to: {args.output}")

        if args.export_render_input:
            render_project, render_output_path = export_render_input(
                storyboard=storyboard,
                storyboard_output_path=args.output,
            )
            render_metadata = build_render_metadata(render_project)
            print(f"Render input written to: {render_output_path}")

        eval_payload: dict[str, Any] | None = None
        eval_output_path: Path | None = None
        if args.run_eval:
            stage_ref["stage"] = "evaluator"
            evaluator = StoryboardEvaluator(forbidden_words=forbidden_words)
            before_fix = evaluator.evaluate(
                storyboard=storyboard,
                render_project=render_project,
                provider_name=provider_name,
                cost_guard_enabled=provider_name == "openai",
                render_export_requested=args.export_render_input,
            )
            after_fix: dict[str, Any] | None = None

            if args.auto_fix and not before_fix.get("passed"):
                fixed_storyboard = LocalAutoFixer(
                    forbidden_words=forbidden_words,
                ).fix(storyboard=storyboard, eval_result=before_fix)
                storyboard = fixed_storyboard
                auto_fix_applied = True
                stage_ref["stage"] = "output_write"
                write_storyboard_json(storyboard=storyboard, output_path=args.output)
                if args.export_render_input:
                    render_project, render_output_path = export_render_input(
                        storyboard=storyboard,
                        storyboard_output_path=args.output,
                    )
                    render_metadata = build_render_metadata(render_project)
                    print(f"Render input written to: {render_output_path}")

                stage_ref["stage"] = "evaluator"
                after_fix = evaluator.evaluate(
                    storyboard=storyboard,
                    render_project=render_project,
                    provider_name=provider_name,
                    cost_guard_enabled=provider_name == "openai",
                    render_export_requested=args.export_render_input,
                )
                eval_payload = build_eval_payload(
                    before_fix=before_fix,
                    after_fix=after_fix,
                    auto_fix_applied=auto_fix_applied,
                )
            elif args.auto_fix:
                after_fix = before_fix
                eval_payload = build_eval_payload(
                    before_fix=before_fix,
                    after_fix=after_fix,
                    auto_fix_applied=False,
                )
            else:
                eval_payload = before_fix

            eval_output_path = build_eval_output_path(args.output)
            stage_ref["stage"] = "output_write"
            write_json(payload=eval_payload, output_path=eval_output_path)
            print(f"Evaluation written to: {eval_output_path}")

            final_eval = get_final_eval_result(eval_payload)
            final_eval_passed = (
                bool(final_eval.get("passed")) if final_eval is not None else None
            )

        logger.log_generation(
            build_generation_record(
                run_id=run_id,
                created_at=created_at,
                provider_name=provider_name,
                model_name=model_name,
                args=args,
                eval_result=get_final_eval_result(eval_payload),
                eval_output_path=eval_output_path,
                storyboard=storyboard,
                auto_fix_applied=auto_fix_applied,
                final_eval_passed=final_eval_passed,
                forbidden_words_source=forbidden_words_source,
                cost_ref=cost_ref,
                memory_init_result=memory_init_result,
                render_metadata=render_metadata,
            )
        )
    except Exception as exc:
        failure_record = build_failure_record(
            run_id=run_id,
            created_at=created_at,
            provider_name=provider_name,
            model_name=model_name,
            args=args,
            error=exc,
            stage=stage_ref["stage"],
        )
        try:
            logger.log_failure(failure_record)
        except Exception as log_exc:
            print(
                (
                    "Failed to write failure log "
                    f"({log_exc.__class__.__name__}): {log_exc}"
                ),
                file=sys.stderr,
            )

        print(
            (
                f"Generation failed for provider '{provider_name}' "
                f"({exc.__class__.__name__}): {exc}"
            ),
            file=sys.stderr,
        )
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
