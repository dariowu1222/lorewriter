"""Convert storyboard schemas into render-friendly JSON payloads."""

from __future__ import annotations

from ai_writer_room.render.render_schema import (
    RenderDialogueLine,
    RenderProject,
    RenderScene,
)
from ai_writer_room.schemas.scene_schema import Scene
from ai_writer_room.schemas.storyboard_schema import Storyboard


DEFAULT_VISUAL_STYLE = "cinematic horror anime"


class RenderAdapter:
    """Adapt Storyboard objects into render pipeline input."""

    def __init__(self) -> None:
        """Create an adapter with per-project conversion context."""
        self._current_sub_genre = ""
        self._scene_ids: list[str] = []

    def storyboard_to_render_project(
        self,
        storyboard: Storyboard,
        resolution: str = "1080x1920",
        fps: int = 30,
    ) -> RenderProject:
        """Convert a Storyboard into a render-friendly project payload."""
        self._current_sub_genre = storyboard.sub_genre
        self._scene_ids = [scene.id for scene in storyboard.scenes]

        render_scenes = [
            self.scene_to_render_scene(scene)
            for scene in storyboard.scenes
        ]

        return RenderProject(
            project_title=storyboard.title,
            provider="storyboard",
            model=storyboard.model,
            target_resolution=resolution,
            fps=fps,
            total_duration_sec=sum(scene.duration_sec for scene in render_scenes),
            visual_theme=DEFAULT_VISUAL_STYLE,
            scenes=render_scenes,
        )

    def scene_to_render_scene(self, scene: Scene) -> RenderScene:
        """Convert a storyboard scene into render-friendly scene data."""
        dialogue_lines = [
            RenderDialogueLine(speaker=line.speaker, text=line.text)
            for line in scene.dialogue_lines
        ]

        return RenderScene(
            scene_id=scene.id,
            title=scene.title,
            narration=scene.narration_zh,
            duration_sec=self._duration_from_time_range(scene.time_in_story),
            mood=scene.mood,
            bgm_intensity=scene.bgm_intensity,
            camera_style=self._camera_style_for_mood(scene.mood),
            visual_style=DEFAULT_VISUAL_STYLE,
            image_prompt=self._build_image_prompt(scene),
            tts_text=self._build_tts_text(scene),
            subtitle_text=scene.narration_zh,
            dialogue_lines=dialogue_lines,
            transition_type=self._transition_type_for_scene(scene.id),
        )

    def _duration_from_time_range(self, time_range: str) -> int:
        """Convert a storyboard time range such as 00:00-00:15 into seconds."""
        try:
            start_text, end_text = time_range.split("-", maxsplit=1)
            duration = self._timestamp_to_seconds(end_text) - self._timestamp_to_seconds(
                start_text,
            )
        except ValueError:
            return 15

        return max(duration, 1)

    def _timestamp_to_seconds(self, timestamp: str) -> int:
        """Convert MM:SS or HH:MM:SS timestamps into seconds."""
        parts = [int(part) for part in timestamp.strip().split(":")]
        if len(parts) == 2:
            minutes, seconds = parts
            return minutes * 60 + seconds
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return hours * 3600 + minutes * 60 + seconds
        raise ValueError(f"Unsupported timestamp: {timestamp}")

    def _camera_style_for_mood(self, mood: str) -> str:
        """Map mood keywords into simple camera-style hints."""
        if "緊張" in mood:
            return "handheld"
        if "壓迫" in mood:
            return "slow_zoom"
        if "混亂" in mood:
            return "shaky"
        if "神秘" in mood:
            return "cinematic_pan"
        return "static"

    def _build_image_prompt(self, scene: Scene) -> str:
        """Build a compact image prompt for future image generation."""
        narration_preview = scene.narration_zh[:100]
        parts = [
            self._current_sub_genre or "rule horror",
            scene.title,
            scene.mood,
            narration_preview,
            DEFAULT_VISUAL_STYLE,
        ]
        return ", ".join(part for part in parts if part)

    def _build_tts_text(self, scene: Scene) -> str:
        """Build TTS text from narration and dialogue."""
        dialogue_text = " ".join(
            f"{line.speaker}：{line.text}"
            for line in scene.dialogue_lines
        )
        return " ".join(part for part in (scene.narration_zh, dialogue_text) if part)

    def _transition_type_for_scene(self, scene_id: str) -> str:
        """Return transition type based on the scene's project position."""
        if not self._scene_ids:
            return "fade_in" if scene_id == "S01" else "hard_cut"

        if scene_id == self._scene_ids[0]:
            return "fade_in"
        if scene_id == self._scene_ids[-1]:
            return "fade_out"
        return "hard_cut"
