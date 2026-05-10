"""Service layer for the FastAPI web prototype."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from ai_writer_room.config import DEFAULT_MODEL
from ai_writer_room.evaluator.auto_fix import LocalAutoFixer
from ai_writer_room.evaluator.evaluator import StoryboardEvaluator
from ai_writer_room.evaluator.forbidden_word_config import ForbiddenWordConfig
from ai_writer_room.generate_storyboard import (
    initialize_story_memory,
    list_generation_modes_payload,
    run_budget_guard,
    ui_contract_payload,
)
from ai_writer_room.generator.json_parser import StoryboardJsonParser
from ai_writer_room.generator.model_provider import OpenAIModelProvider
from ai_writer_room.generator.prompt_builder import PromptBuilder
from ai_writer_room.render.render_adapter import RenderAdapter
from ai_writer_room.render.render_schema import RenderProject
from ai_writer_room.schemas.storyboard_schema import Storyboard

from api.schemas import (
    ApiResponse,
    GeneratePromptRequest,
    ManualParseRequest,
    OpenAIGenerateRequest,
)


def get_ui_contract() -> dict[str, Any]:
    """Return the minimal UI contract as a JSON-safe dictionary."""
    return ui_contract_payload()


def list_generation_modes() -> list[dict[str, Any]]:
    """Return public generation modes as JSON-safe dictionaries."""
    return list_generation_modes_payload()


def generate_manual_prompt(req: GeneratePromptRequest) -> ApiResponse:
    """Generate a prompt for manual copy/paste workflows."""
    try:
        prompt = PromptBuilder().build_rule_horror_prompt(
            sub_genre=req.sub_genre,
            duration_sec=req.duration,
        )
    except Exception as exc:
        return _failure("Manual prompt generation failed.", exc)

    return ApiResponse(
        success=True,
        message="Manual prompt generated.",
        data={"prompt": prompt},
    )


def parse_manual_response(req: ManualParseRequest) -> ApiResponse:
    """Parse, optionally evaluate/fix, and optionally render a manual response."""
    try:
        storyboard = _parse_storyboard_for_api(req.manual_response_text)
        result = _finalize_storyboard_payload(
            storyboard=storyboard,
            provider_name="manual",
            enable_eval=req.enable_eval,
            enable_auto_fix=req.enable_auto_fix,
            export_render_input=req.export_render_input,
            forbidden_words_text=req.forbidden_words_text,
        )
    except Exception as exc:
        return _failure("Manual response parse failed.", exc)

    return ApiResponse(
        success=True,
        message="Manual response parsed.",
        data=result,
    )


def generate_with_openai(req: OpenAIGenerateRequest) -> ApiResponse:
    """Generate a storyboard through OpenAI and return API-safe payloads."""
    prompt = ""
    cost_ref: dict[str, float | int] = {
        "estimated_cost_usd": 0.0,
        "estimated_input_tokens": 0,
        "estimated_output_tokens": 0,
    }
    try:
        prompt = PromptBuilder().build_rule_horror_prompt(
            sub_genre=req.sub_genre,
            duration_sec=req.duration,
        )
        run_budget_guard(
            prompt=prompt,
            model_name=req.model or DEFAULT_MODEL,
            cost_ref=cost_ref,
            ignore_budget_guard=req.ignore_budget_guard,
        )
        raw_text = OpenAIModelProvider(model=req.model).generate_text(prompt)
        storyboard = _parse_storyboard_for_api(raw_text)
        result = _finalize_storyboard_payload(
            storyboard=storyboard,
            provider_name="openai",
            enable_eval=req.enable_eval,
            enable_auto_fix=req.enable_auto_fix,
            export_render_input=req.export_render_input,
            forbidden_words_text=req.forbidden_words_text,
            estimated_cost=cost_ref,
        )
    except Exception as exc:
        return _failure(
            "OpenAI generation failed.",
            exc,
            data={"estimated_cost": cost_ref} if cost_ref else None,
        )
    finally:
        prompt = ""

    return ApiResponse(
        success=True,
        message="OpenAI storyboard generated.",
        data=result,
    )


def parse_forbidden_words_text(text: str | None) -> dict[str, str]:
    """Parse textarea forbidden-word lines into replacement mappings."""
    parsed: dict[str, str] = {}
    if not text:
        return parsed

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if "=" in line:
            word, replacement = line.split("=", maxsplit=1)
        else:
            word, replacement = line, ""
        word = word.strip()
        if word:
            parsed[word] = replacement.strip()

    return parsed


def _parse_storyboard_for_api(raw_text: str) -> Storyboard:
    """Parse model output, with a forgiving pass for UI/manual workflows."""
    parser = StoryboardJsonParser()
    try:
        return parser.parse_storyboard(raw_text)
    except Exception as strict_error:
        try:
            payload = json.loads(parser.extract_json_text(raw_text))
            normalized_payload = _normalize_storyboard_payload(payload)
            return Storyboard.model_validate(normalized_payload)
        except Exception as relaxed_error:
            raise ValueError(
                "Storyboard response could not be parsed. "
                f"Strict parse: {strict_error}. "
                f"Relaxed parse: {relaxed_error}"
            ) from relaxed_error


def _normalize_storyboard_payload(payload: Any) -> dict[str, Any]:
    """Normalize near-storyboard JSON into the strict v0.1 Storyboard schema."""
    if isinstance(payload, dict) and isinstance(payload.get("storyboard"), dict):
        payload = payload["storyboard"]
    if not isinstance(payload, dict):
        raise ValueError("Storyboard payload must be a JSON object.")

    raw_scenes = payload.get("scenes")
    if not isinstance(raw_scenes, list):
        raise ValueError("Storyboard payload must include a scenes list.")
    if len(raw_scenes) != 12:
        raise ValueError(
            f"Storyboard payload must include exactly 12 scenes; got {len(raw_scenes)}."
        )

    return {
        "title": _text(payload.get("title") or payload.get("name"), "Manual Storyboard"),
        "sub_genre": _text(
            payload.get("sub_genre") or payload.get("genre"),
            "manual",
        ),
        "target_duration_sec": _int(
            payload.get("target_duration_sec") or payload.get("duration_sec"),
            180,
        ),
        "generated_at": _text(
            payload.get("generated_at"),
            datetime.now(UTC).isoformat(),
        ),
        "model": _text(payload.get("model"), "manual"),
        "cost_usd": float(payload.get("cost_usd") or 0.0),
        "prologue": _text(payload.get("prologue"), ""),
        "story_bible": {},
        "scenes": [
            _normalize_scene_payload(scene, index)
            for index, scene in enumerate(raw_scenes, start=1)
        ],
        "memory_summary": {},
        "foreshadowing": [],
        "arc_plan": None,
    }


def _normalize_scene_payload(scene: Any, index: int) -> dict[str, Any]:
    """Normalize one near-scene object into the strict Scene schema."""
    if not isinstance(scene, dict):
        scene = {"narration_zh": str(scene)}

    scene_id = _text(scene.get("id") or scene.get("scene_id"), f"S{index:02d}")
    title = _text(scene.get("title") or scene.get("name"), scene_id)
    narration = _text(
        scene.get("narration_zh")
        or scene.get("narration")
        or scene.get("summary")
        or scene.get("description")
        or scene.get("text"),
        "",
    )

    return {
        "id": scene_id,
        "title": title,
        "function": _text(
            scene.get("function") or scene.get("purpose") or scene.get("role"),
            title,
        ),
        "mood": _text(scene.get("mood"), "神秘"),
        "bgm_intensity": min(max(_int(scene.get("bgm_intensity"), 3), 1), 5),
        "time_in_story": _text(
            scene.get("time_in_story") or scene.get("time_range"),
            _default_time_range(index),
        ),
        "narration_zh": narration,
        "dialogue_lines": _normalize_dialogue_lines(scene.get("dialogue_lines", [])),
        "rule_refs": _string_list(
            scene.get("rule_refs")
            or scene.get("rules")
            or scene.get("rule_signals")
            or []
        ),
        "foreshadow_refs": _string_list(
            scene.get("foreshadow_refs")
            or scene.get("foreshadows")
            or scene.get("foreshadowing")
            or []
        ),
    }


def _normalize_dialogue_lines(value: Any) -> list[dict[str, str]]:
    """Normalize dialogue lines to speaker/text dicts."""
    if not isinstance(value, list):
        return []

    lines: list[dict[str, str]] = []
    for item in value:
        if isinstance(item, dict):
            lines.append(
                {
                    "speaker": _text(item.get("speaker"), "旁白"),
                    "text": _text(item.get("text") or item.get("line"), ""),
                }
            )
        else:
            lines.append({"speaker": "旁白", "text": str(item)})
    return lines


def _string_list(value: Any) -> list[str]:
    """Normalize loose list/string values into a string list."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if not isinstance(value, list):
        return [str(value)]
    return [
        str(item.get("id") or item.get("rule_id") or item.get("text") or item)
        if isinstance(item, dict)
        else str(item)
        for item in value
        if item is not None
    ]


def _default_time_range(index: int) -> str:
    """Return a 15-second default scene time range."""
    start = (index - 1) * 15
    end = index * 15
    return f"{start // 60:02d}:{start % 60:02d}-{end // 60:02d}:{end % 60:02d}"


def _text(value: Any, default: str) -> str:
    """Return a safe string value."""
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _int(value: Any, default: int) -> int:
    """Return a safe integer value."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _finalize_storyboard_payload(
    storyboard: Storyboard,
    provider_name: str,
    enable_eval: bool,
    enable_auto_fix: bool,
    export_render_input: bool,
    forbidden_words_text: str | None,
    estimated_cost: dict[str, float | int] | None = None,
) -> dict[str, Any]:
    """Initialize memory, run optional eval/fix/render, and serialize payloads."""
    initialize_story_memory(storyboard)
    forbidden_words = _load_forbidden_words(forbidden_words_text)
    render_project: RenderProject | None = None
    eval_result: dict[str, Any] | None = None

    if export_render_input:
        render_project = RenderAdapter().storyboard_to_render_project(storyboard)

    if enable_eval:
        evaluator = StoryboardEvaluator(forbidden_words=forbidden_words)
        eval_result = evaluator.evaluate(
            storyboard=storyboard,
            render_project=render_project,
            provider_name=provider_name,
            cost_guard_enabled=provider_name == "openai",
            render_export_requested=export_render_input,
        )

        if enable_auto_fix and not eval_result.get("passed"):
            storyboard = LocalAutoFixer(forbidden_words=forbidden_words).fix(
                storyboard=storyboard,
                eval_result=eval_result,
            )
            initialize_story_memory(storyboard)
            if export_render_input:
                render_project = RenderAdapter().storyboard_to_render_project(
                    storyboard,
                )
            after_fix = evaluator.evaluate(
                storyboard=storyboard,
                render_project=render_project,
                provider_name=provider_name,
                cost_guard_enabled=provider_name == "openai",
                render_export_requested=export_render_input,
            )
            eval_result = {
                "before_fix": eval_result,
                "after_fix": after_fix,
                "auto_fix_applied": True,
                "final_passed": after_fix.get("passed"),
            }

    payload: dict[str, Any] = {
        "storyboard": storyboard.model_dump(mode="json"),
        "eval_result": eval_result,
        "render_project": (
            render_project.model_dump(mode="json")
            if render_project is not None
            else None
        ),
    }
    if estimated_cost is not None:
        payload["estimated_cost"] = dict(estimated_cost)

    return payload


def _load_forbidden_words(text: str | None) -> dict[str, str]:
    """Load default forbidden words merged with textarea overrides."""
    defaults = ForbiddenWordConfig.load_default()
    custom = parse_forbidden_words_text(text)
    return ForbiddenWordConfig.merge(defaults=defaults, custom=custom)


def _failure(
    message: str,
    error: Exception,
    data: dict[str, Any] | None = None,
) -> ApiResponse:
    """Return a sanitized failure response."""
    return ApiResponse(
        success=False,
        message=message,
        data=data,
        error=_sanitize_error(error),
    )


def _sanitize_error(error: Exception) -> str:
    """Avoid exposing API keys, key-file paths, prompts, or raw model output."""
    text = str(error)
    lowered = text.lower()
    if "api key" in lowered or "openai_api_key" in lowered:
        return (
            f"{error.__class__.__name__}: OpenAI API key not found or invalid. "
            "Set OPENAI_API_KEY or OPENAI_API_KEY_FILE on the backend."
        )
    if "sk-" in text:
        return f"{error.__class__.__name__}: credential detail omitted."
    return f"{error.__class__.__name__}: {text}"
