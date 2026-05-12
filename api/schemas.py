"""API request and response schemas for the web prototype."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GeneratedRule(BaseModel):
    """Creator-provided or locally generated rule metadata."""

    id: str
    text: str
    category: str = ""


class CreatorContextMixin(BaseModel):
    """Shared creator-facing generation controls."""

    generated_rules: list[GeneratedRule] = Field(default_factory=list)
    world_setting: str | None = None
    horror_style: str | None = None
    pacing_style: str | None = None
    ending_style: str | None = None
    protagonist_type: str | None = None
    object_focus: str | None = None
    visual_style: str | None = None


class GenerateRulesRequest(BaseModel):
    """Request to generate editable rule-horror rules."""

    sub_genre: str
    horror_style: str | None = None
    pacing_style: str | None = None
    ending_style: str | None = None
    rule_count: int = Field(default=5, ge=3, le=10)


class GeneratePromptRequest(BaseModel):
    """Request to generate a manual copy/paste prompt."""

    sub_genre: str
    duration: int
    forbidden_words_text: str | None = None
    generated_rules: list[GeneratedRule] = Field(default_factory=list)
    world_setting: str | None = None
    horror_style: str | None = None
    pacing_style: str | None = None
    ending_style: str | None = None
    protagonist_type: str | None = None
    object_focus: str | None = None
    visual_style: str | None = None


class ManualParseRequest(BaseModel):
    """Request to parse a manually pasted model response."""

    manual_response_text: str
    enable_eval: bool = True
    enable_auto_fix: bool = False
    export_render_input: bool = True
    forbidden_words_text: str | None = None
    generated_rules: list[GeneratedRule] = Field(default_factory=list)
    world_setting: str | None = None
    horror_style: str | None = None
    pacing_style: str | None = None
    ending_style: str | None = None
    protagonist_type: str | None = None
    object_focus: str | None = None
    visual_style: str | None = None


class OpenAIGenerateRequest(BaseModel):
    """Request to generate a storyboard through OpenAI."""

    sub_genre: str
    duration: int
    model: str = "gpt-4o-mini"
    enable_eval: bool = True
    enable_auto_fix: bool = False
    export_render_input: bool = True
    ignore_budget_guard: bool = False
    forbidden_words_text: str | None = None
    generated_rules: list[GeneratedRule] = Field(default_factory=list)
    world_setting: str | None = None
    horror_style: str | None = None
    pacing_style: str | None = None
    ending_style: str | None = None
    protagonist_type: str | None = None
    object_focus: str | None = None
    visual_style: str | None = None


class ProductionRequest(BaseModel):
    """Request to build next-step local production payloads."""

    storyboard: dict | None = None
    render_project: dict | None = None
    visual_style: str | None = None


class ManualEvalPromptRequest(BaseModel):
    """Request to build a copy/paste prompt for free manual evaluation."""

    storyboard: dict
    eval_result: dict | None = None
    forbidden_words_text: str | None = None


class ManualEvalImportRequest(BaseModel):
    """Request to import a manually pasted judge response."""

    manual_eval_text: str


class ApiResponse(BaseModel):
    """Consistent API response envelope."""

    success: bool
    message: str
    data: dict | None = Field(default=None)
    error: str | None = Field(default=None)
