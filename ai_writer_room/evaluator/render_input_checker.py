"""Warning-only checks for render-friendly project payloads."""

from __future__ import annotations

from typing import Any

from ai_writer_room.render.render_schema import RenderProject, RenderScene


class RenderInputChecker:
    """Validate render input payload shape for downstream pipelines."""

    def check(self, render_project: RenderProject | dict[str, Any]) -> dict[str, object]:
        """Check render input and return warning-only results."""
        warnings: list[str] = []
        scenes = self._get_scenes(render_project)
        total_duration_sec = self._get_total_duration(render_project)
        scene_duration_sum = sum(self._get_duration(scene) for scene in scenes)
        missing_required_count = 0
        invalid_duration_count = 0

        if not scenes:
            warnings.append("render input scenes are missing or empty.")

        for index, scene in enumerate(scenes, start=1):
            scene_id = self._get_field(scene, "scene_id") or f"scene_{index}"
            for field_name in (
                "narration",
                "image_prompt",
                "tts_text",
                "subtitle_text",
                "transition_type",
            ):
                if not self._get_field(scene, field_name):
                    missing_required_count += 1
                    warnings.append(f"{scene_id} is missing {field_name}.")

            if self._get_duration(scene) <= 0:
                invalid_duration_count += 1
                warnings.append(f"{scene_id} duration_sec should be greater than 0.")

        if total_duration_sec <= 0:
            warnings.append("render input total_duration_sec should be greater than 0.")
        if scenes and abs(total_duration_sec - scene_duration_sum) > 1:
            warnings.append(
                "render input total_duration_sec should match scene durations."
            )

        return {
            "passed": not warnings,
            "warnings": warnings,
            "stats": {
                "scene_count": len(scenes),
                "total_duration_sec": total_duration_sec,
                "scene_duration_sum": scene_duration_sum,
                "missing_required_count": missing_required_count,
                "invalid_duration_count": invalid_duration_count,
            },
        }

    def _get_scenes(self, render_project: RenderProject | dict[str, Any]) -> list[Any]:
        """Extract render scenes from dataclass or dict payloads."""
        if isinstance(render_project, RenderProject):
            return list(render_project.scenes)
        scenes = render_project.get("scenes", [])
        return list(scenes) if isinstance(scenes, list) else []

    def _get_total_duration(
        self,
        render_project: RenderProject | dict[str, Any],
    ) -> int:
        """Read total duration from dataclass or dict payloads."""
        if isinstance(render_project, RenderProject):
            return int(render_project.total_duration_sec)
        try:
            return int(render_project.get("total_duration_sec", 0))
        except (TypeError, ValueError):
            return 0

    def _get_field(self, scene: Any, field_name: str) -> str:
        """Read a text field from RenderScene or dict values."""
        if isinstance(scene, RenderScene):
            return str(getattr(scene, field_name))
        if isinstance(scene, dict):
            return str(scene.get(field_name, ""))
        return str(getattr(scene, field_name, ""))

    def _get_duration(self, scene: Any) -> int:
        """Read scene duration from RenderScene or dict values."""
        if isinstance(scene, RenderScene):
            value = scene.duration_sec
        elif isinstance(scene, dict):
            value = scene.get("duration_sec", 0)
        else:
            value = getattr(scene, "duration_sec", 0)

        try:
            return int(value)
        except (TypeError, ValueError):
            return 0
