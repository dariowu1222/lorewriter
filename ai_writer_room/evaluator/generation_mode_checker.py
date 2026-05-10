"""Warning-only checks for generation mode metadata and workflow contracts."""

from __future__ import annotations

from ai_writer_room.generator.generation_mode import (
    GenerationMode,
    GenerationModeRegistry,
)


class GenerationModeChecker:
    """Validate UI-facing generation mode workflow compatibility."""

    def check(
        self,
        provider_name: str | None = None,
        cost_guard_enabled: bool | None = None,
        render_export_requested: bool = False,
    ) -> dict[str, object]:
        """Check whether a provider maps cleanly to a public generation mode."""
        warnings: list[str] = []
        mode = self._mode_from_provider(provider_name)
        mode_info = (
            GenerationModeRegistry.get_mode_info(mode) if mode is not None else None
        )

        if provider_name is None:
            warnings.append("generation provider context was not supplied.")
        elif mode is None:
            warnings.append(
                f"provider '{provider_name}' is not a public generation mode."
            )

        if mode == GenerationMode.MANUAL:
            if mode_info and mode_info.requires_api_key:
                warnings.append("manual mode should not require an API key.")
            if cost_guard_enabled:
                warnings.append("manual mode should not use cost guard.")

        if mode == GenerationMode.OPENAI:
            if cost_guard_enabled is False:
                warnings.append("openai mode should enable cost guard.")

        if render_export_requested and mode_info and not mode_info.supports_render_export:
            warnings.append(f"{mode.value} mode does not support render export.")

        return {
            "passed": not warnings,
            "warnings": warnings,
            "stats": {
                "provider": provider_name or "",
                "generation_mode": mode.value if mode is not None else "",
                "requires_api_key": (
                    mode_info.requires_api_key if mode_info is not None else None
                ),
                "supports_auto_fix": (
                    mode_info.supports_auto_fix if mode_info is not None else None
                ),
                "supports_render_export": (
                    mode_info.supports_render_export if mode_info is not None else None
                ),
                "supports_cost_guard": (
                    mode_info.supports_cost_guard if mode_info is not None else None
                ),
                "render_export_requested": render_export_requested,
                "cost_guard_enabled": cost_guard_enabled,
            },
        }

    def _mode_from_provider(self, provider_name: str | None) -> GenerationMode | None:
        """Map a provider name to a public generation mode when possible."""
        if provider_name == GenerationMode.MANUAL.value:
            return GenerationMode.MANUAL
        if provider_name == GenerationMode.OPENAI.value:
            return GenerationMode.OPENAI
        return None
