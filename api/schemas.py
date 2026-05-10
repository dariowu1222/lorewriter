"""API request and response schemas for the web prototype."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GeneratePromptRequest(BaseModel):
    """Request to generate a manual copy/paste prompt."""

    sub_genre: str
    duration: int
    forbidden_words_text: str | None = None


class ManualParseRequest(BaseModel):
    """Request to parse a manually pasted model response."""

    manual_response_text: str
    enable_eval: bool = True
    enable_auto_fix: bool = False
    export_render_input: bool = True
    forbidden_words_text: str | None = None


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


class ApiResponse(BaseModel):
    """Consistent API response envelope."""

    success: bool
    message: str
    data: dict | None = Field(default=None)
    error: str | None = Field(default=None)
