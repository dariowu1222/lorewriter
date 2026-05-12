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
from ai_writer_room.generator.rule_engine import RuleEngine
from ai_writer_room.render.production_adapter import ProductionAdapter
from ai_writer_room.render.render_adapter import RenderAdapter
from ai_writer_room.render.render_schema import RenderProject
from ai_writer_room.schemas.storyboard_schema import Storyboard

from api.schemas import (
    ApiResponse,
    GeneratePromptRequest,
    GenerateRulesRequest,
    ManualEvalImportRequest,
    ManualEvalPromptRequest,
    ManualParseRequest,
    OpenAIGenerateRequest,
    ProductionRequest,
)


def get_ui_contract() -> dict[str, Any]:
    """Return the minimal UI contract as a JSON-safe dictionary."""
    return ui_contract_payload()


def list_generation_modes() -> list[dict[str, Any]]:
    """Return public generation modes as JSON-safe dictionaries."""
    return list_generation_modes_payload()


def generate_rules(req: GenerateRulesRequest) -> ApiResponse:
    """Generate editable mock rules for the rule-first creator workflow."""
    try:
        rules = RuleEngine().build_mock_rules(
            sub_genre=req.sub_genre,
            rules_count=min(req.rule_count, 5),
        )
        while len(rules) < req.rule_count:
            index = len(rules) + 1
            rules.append(
                type(rules[0])(
                    id=f"R{index:02d}",
                    text=f"{req.sub_genre} 的補充規則 {index}：不要相信重複出現的指示。",
                    category="補充規則",
                    is_visual=False,
                    expected_scene_ids=[],
                )
            )
        payload = [
            {
                "id": rule.id,
                "text": rule.text,
                "category": rule.category,
            }
            for rule in rules
        ]
    except Exception as exc:
        return _failure("Rule generation failed.", exc)

    return ApiResponse(
        success=True,
        message="Rules generated.",
        data={"rules": payload},
    )


def generate_manual_prompt(req: GeneratePromptRequest) -> ApiResponse:
    """Generate a prompt for manual copy/paste workflows."""
    try:
        prompt = _build_creator_prompt(req)
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
            creator_request=req,
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
        prompt = _build_creator_prompt(req)
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
            creator_request=req,
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


def generate_manual_eval_prompt(req: ManualEvalPromptRequest) -> ApiResponse:
    """Build a free manual-evaluation prompt without calling any model."""
    try:
        prompt = _build_manual_eval_prompt(req)
    except Exception as exc:
        return _failure("Manual evaluation prompt generation failed.", exc)

    return ApiResponse(
        success=True,
        message="人工評估 Prompt 已產生。",
        data={"manual_eval_prompt": prompt},
    )


def import_manual_eval(req: ManualEvalImportRequest) -> ApiResponse:
    """Parse a manually pasted evaluator response into a stable contract."""
    try:
        manual_eval = _parse_manual_eval_text(req.manual_eval_text)
    except Exception as exc:
        return _failure("Manual evaluation import failed.", exc)

    return ApiResponse(
        success=True,
        message="人工評估已匯入。",
        data={"manual_eval": manual_eval},
    )


def generate_voice_project(req: ProductionRequest) -> ApiResponse:
    """Build a local TTS script package from the current render project."""
    try:
        render_project = _render_project_from_production_request(req)
        voice_project = ProductionAdapter().build_voice_project(render_project)
    except Exception as exc:
        return _failure("Voice package generation failed.", exc)

    return ApiResponse(
        success=True,
        message="語音腳本已產生。",
        data={"voice_project": voice_project.model_dump(mode="json")},
    )


def generate_image_prompt_project(req: ProductionRequest) -> ApiResponse:
    """Build a local image prompt package from the current render project."""
    try:
        render_project = _render_project_from_production_request(req)
        image_project = ProductionAdapter().build_image_prompt_project(render_project)
    except Exception as exc:
        return _failure("Image prompt package generation failed.", exc)

    return ApiResponse(
        success=True,
        message="圖片提示詞已產生。",
        data={"image_prompt_project": image_project.model_dump(mode="json")},
    )


def generate_shot_storyboard(req: ProductionRequest) -> ApiResponse:
    """Build a local shot storyboard package from the current render project."""
    try:
        render_project = _render_project_from_production_request(req)
        shot_storyboard = ProductionAdapter().build_shot_storyboard(render_project)
    except Exception as exc:
        return _failure("Shot storyboard generation failed.", exc)

    return ApiResponse(
        success=True,
        message="分鏡表已產生。",
        data={"shot_storyboard": shot_storyboard.model_dump(mode="json")},
    )


def generate_video_manifest(req: ProductionRequest) -> ApiResponse:
    """Build a local video assembly manifest from the current render project."""
    try:
        render_project = _render_project_from_production_request(req)
        video_manifest = ProductionAdapter().build_video_manifest(render_project)
    except Exception as exc:
        return _failure("Video manifest generation failed.", exc)

    return ApiResponse(
        success=True,
        message="影片組裝清單已產生。",
        data={"video_manifest": video_manifest.model_dump(mode="json")},
    )


def _build_manual_eval_prompt(req: ManualEvalPromptRequest) -> str:
    """Build a detailed judge prompt for copy/paste evaluation workflows."""
    storyboard_json = json.dumps(req.storyboard, ensure_ascii=False, indent=2)
    local_eval_json = json.dumps(req.eval_result or {}, ensure_ascii=False, indent=2)
    forbidden_words = _load_forbidden_words(req.forbidden_words_text)
    forbidden_words_text = "、".join(forbidden_words.keys())

    return f"""你是 AI Writer Room 的故事評估員，請評估以下規則怪談 storyboard。

重要：
- 不要改寫故事。
- 不要輸出 Markdown。
- 只輸出 JSON。
- 請用繁體中文。
- 這是人工免費評估流程，不需要任何 API 工具。

請特別評估：
1. 規則是否真的影響劇情，而不是裝飾。
2. 每條規則是否有驗證、衝突或代價。
3. 中段反轉、主反轉、尾刀是否有力。
4. 主角行動是否清楚。
5. 氣氛是否具體，不要只靠抽象恐怖形容詞。
6. 伏筆是否有 payoff，未 payoff 是否值得保留。
7. 是否有禁忌詞或空泛描述。
8. 是否適合下一步做語音、圖片、分鏡、影片。

禁忌詞參考：
{forbidden_words_text}

本地結構檢查結果：
{local_eval_json}

請只回傳以下 JSON 格式：
{{
  "overall_score": 1,
  "passed": false,
  "summary": "一句話總評",
  "strengths": ["優點 1", "優點 2"],
  "issues": ["問題 1", "問題 2"],
  "suggestions": ["修正建議 1", "修正建議 2"],
  "checks": {{
    "rules": "規則設計評語",
    "pacing": "節奏評語",
    "twist": "反轉評語",
    "atmosphere": "氣氛評語",
    "foreshadowing": "伏筆評語",
    "render_readiness": "製作可行性評語"
  }}
}}

Storyboard JSON：
{storyboard_json}
"""


def _parse_manual_eval_text(raw_text: str) -> dict[str, Any]:
    """Parse manual evaluator JSON, including fenced JSON responses."""
    if not raw_text or not raw_text.strip():
        raise ValueError("Manual evaluation text is empty.")

    parser = StoryboardJsonParser()
    try:
        payload = json.loads(parser.extract_json_text(raw_text))
    except Exception as exc:
        preview = raw_text.strip()[:500]
        raise ValueError(
            "Manual evaluation must be valid JSON. "
            f"Raw text preview: {preview}"
        ) from exc

    if not isinstance(payload, dict):
        raise ValueError("Manual evaluation JSON must be an object.")

    return {
        "overall_score": _clamp_score(payload.get("overall_score")),
        "passed": bool(payload.get("passed", False)),
        "summary": str(payload.get("summary") or ""),
        "strengths": _string_list(payload.get("strengths")),
        "issues": _string_list(payload.get("issues")),
        "suggestions": _string_list(payload.get("suggestions")),
        "checks": _string_dict(payload.get("checks")),
        "source": "manual_paste",
    }


def _clamp_score(value: Any) -> int:
    """Clamp a manual evaluator score to 1-5."""
    try:
        score = int(value)
    except (TypeError, ValueError):
        score = 1
    return max(1, min(5, score))


def _string_list(value: Any) -> list[str]:
    """Normalize arbitrary list-like values into a list of strings."""
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def _string_dict(value: Any) -> dict[str, str]:
    """Normalize arbitrary mapping values into string pairs."""
    if not isinstance(value, dict):
        return {}
    return {str(key): str(item) for key, item in value.items()}


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


def _render_project_from_production_request(
    req: ProductionRequest,
) -> RenderProject:
    """Create or validate render input for next-step local production."""
    if req.render_project:
        render_project = RenderProject.model_validate(req.render_project)
    elif req.storyboard:
        storyboard = Storyboard.model_validate(req.storyboard)
        render_project = RenderAdapter().storyboard_to_render_project(storyboard)
    else:
        raise ValueError("Production step requires storyboard or render_project.")

    if req.visual_style:
        render_project = render_project.model_copy(
            update={
                "visual_theme": req.visual_style,
                "scenes": [
                    scene.model_copy(update={"visual_style": req.visual_style})
                    for scene in render_project.scenes
                ],
            },
        )

    if not render_project.scenes:
        raise ValueError("Production step requires at least one render scene.")
    return render_project


def _build_creator_prompt(req: GeneratePromptRequest | OpenAIGenerateRequest) -> str:
    """Build a generation prompt with creator-facing controls appended."""
    prompt = PromptBuilder().build_rule_horror_prompt(
        sub_genre=req.sub_genre,
        duration_sec=req.duration,
    )
    creator_notes = _creator_context_text(req)
    if not creator_notes:
        return prompt
    return f"{prompt}\n\n創作者設定：\n{creator_notes}"


def _creator_context_text(req: GeneratePromptRequest | OpenAIGenerateRequest) -> str:
    """Serialize creator controls into prompt instructions."""
    lines: list[str] = []
    for label, attr in (
        ("世界觀", "world_setting"),
        ("恐怖類型", "horror_style"),
        ("節奏", "pacing_style"),
        ("結局風格", "ending_style"),
        ("主角類型", "protagonist_type"),
        ("核心物件", "object_focus"),
        ("視覺風格", "visual_style"),
    ):
        value = getattr(req, attr, None)
        if value:
            lines.append(f"- {label}: {value}")

    rules = getattr(req, "generated_rules", [])
    if rules:
        lines.append("- 必須使用以下規則作為 story_bible.world_rules 與 scene.rule_refs 的來源：")
        for rule in rules:
            lines.append(f"  - {rule.id} [{rule.category}]: {rule.text}")

    return "\n".join(lines)


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
    creator_request: ManualParseRequest | OpenAIGenerateRequest | None = None,
) -> dict[str, Any]:
    """Initialize memory, run optional eval/fix/render, and serialize payloads."""
    initialize_story_memory(storyboard)
    if creator_request is not None:
        _apply_creator_metadata(storyboard, creator_request)
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
            if creator_request is not None:
                _apply_creator_metadata(storyboard, creator_request)
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
        "creator_eval_summary": summarize_eval_for_creator(eval_result),
        "render_project": (
            render_project.model_dump(mode="json")
            if render_project is not None
            else None
        ),
    }
    if estimated_cost is not None:
        payload["estimated_cost"] = dict(estimated_cost)

    return payload


def summarize_eval_for_creator(eval_result: dict[str, Any] | None) -> list[str]:
    """Translate evaluator JSON into creator-readable status lines."""
    if not eval_result:
        return []

    result = eval_result.get("after_fix", eval_result)
    forbidden_hits = result.get("forbidden_word_check", {}).get("total_hits", 0)
    unresolved_count = (
        result.get("story_memory_check", {})
        .get("stats", {})
        .get("unresolved_foreshadow_count", 0)
    )

    lines = [
        "✅ 規則完整"
        if result.get("rule_check", {}).get("passed")
        else "⚠ 規則引用仍需檢查",
        "✅ 未偵測到禁忌詞"
        if forbidden_hits == 0
        else f"⚠ 偵測到 {forbidden_hits} 個禁忌詞",
    ]

    if unresolved_count:
        lines.append(f"⚠ 有 {unresolved_count} 個未完成伏筆")
    else:
        lines.append("✅ 伏筆狀態已收斂")

    return lines


def _apply_creator_metadata(
    storyboard: Storyboard,
    req: ManualParseRequest | OpenAIGenerateRequest,
) -> None:
    """Persist creator controls into Story Bible metadata."""
    story_bible = storyboard.story_bible
    story_bible.world_setting = req.world_setting or story_bible.world_setting
    story_bible.horror_style = req.horror_style or story_bible.horror_style
    story_bible.pacing_style = req.pacing_style or story_bible.pacing_style
    story_bible.ending_style = req.ending_style or story_bible.ending_style
    story_bible.protagonist_type = (
        req.protagonist_type or story_bible.protagonist_type
    )
    story_bible.object_focus = req.object_focus or story_bible.object_focus
    story_bible.visual_style = req.visual_style or story_bible.visual_style

    if req.generated_rules:
        story_bible.world_rules = [
            rule
            for rule in story_bible.world_rules
            if rule.id not in {item.id for item in req.generated_rules}
        ]
        from ai_writer_room.memory.story_bible import WorldRule

        story_bible.world_rules.extend(
            [
                WorldRule(
                    id=rule.id,
                    text=rule.text,
                    category=rule.category,
                    introduced_scene_id=_first_scene_id_for_rule(storyboard, rule.id),
                    verified_scene_ids=_scene_ids_for_rule(storyboard, rule.id),
                    broken_scene_ids=[],
                    is_contradictory=False,
                )
                for rule in req.generated_rules
            ]
        )


def _first_scene_id_for_rule(storyboard: Storyboard, rule_id: str) -> str:
    """Return the first scene id referencing a rule."""
    scene_ids = _scene_ids_for_rule(storyboard, rule_id)
    return scene_ids[0] if scene_ids else "S01"


def _scene_ids_for_rule(storyboard: Storyboard, rule_id: str) -> list[str]:
    """Return scene ids that reference a rule."""
    return [
        scene.id
        for scene in storyboard.scenes
        if rule_id in scene.rule_refs
    ]


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
