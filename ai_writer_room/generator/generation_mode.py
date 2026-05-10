"""Generation mode metadata for UI-ready workflows."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class GenerationMode(str, Enum):
    """Public generation modes exposed to future UI flows."""

    MANUAL = "manual"
    OPENAI = "openai"


class GenerationModeInfo(BaseModel):
    """UI-ready metadata for one generation mode."""

    mode: str
    display_name: str
    description: str
    requires_api_key: bool
    supports_auto_fix: bool
    supports_render_export: bool
    supports_cost_guard: bool
    estimated_speed: str
    estimated_cost_level: str
    recommended_for: list[str] = Field(default_factory=list)


class GenerationModeRegistry:
    """Registry for public generation mode metadata."""

    _MODES: dict[GenerationMode, GenerationModeInfo] = {
        GenerationMode.MANUAL: GenerationModeInfo(
            mode=GenerationMode.MANUAL.value,
            display_name="省錢模式",
            description=(
                "產生 prompt 後手動貼到 ChatGPT / Claude / Gemini，再匯回 JSON。"
            ),
            requires_api_key=False,
            supports_auto_fix=True,
            supports_render_export=True,
            supports_cost_guard=False,
            estimated_speed="慢",
            estimated_cost_level="低",
            recommended_for=[
                "個人創作",
                "開發測試",
                "節省 API 成本",
            ],
        ),
        GenerationMode.OPENAI: GenerationModeInfo(
            mode=GenerationMode.OPENAI.value,
            display_name="API 自動模式",
            description="直接呼叫 OpenAI API 自動生成 storyboard。",
            requires_api_key=True,
            supports_auto_fix=True,
            supports_render_export=True,
            supports_cost_guard=True,
            estimated_speed="快",
            estimated_cost_level="中",
            recommended_for=[
                "商業化",
                "大量生成",
                "自動化 pipeline",
            ],
        ),
    }

    @classmethod
    def get_mode_info(cls, mode: GenerationMode) -> GenerationModeInfo:
        """Return metadata for a generation mode."""
        return cls._MODES[mode]

    @classmethod
    def list_modes(cls) -> list[GenerationModeInfo]:
        """Return all public generation modes in stable UI order."""
        return [
            cls._MODES[GenerationMode.MANUAL],
            cls._MODES[GenerationMode.OPENAI],
        ]
