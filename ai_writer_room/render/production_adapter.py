"""Build local production handoff packages from render input."""

from __future__ import annotations

from ai_writer_room.render.production_schema import (
    ImagePromptItem,
    ImagePromptProject,
    ShotItem,
    ShotStoryboardProject,
    VideoManifestProject,
    VideoManifestScene,
    VoiceLine,
    VoiceProject,
)
from ai_writer_room.render.render_schema import RenderProject, RenderScene


class ProductionAdapter:
    """Convert render input into next-step production JSON packages."""

    def build_voice_project(self, render_project: RenderProject) -> VoiceProject:
        """Prepare a TTS script package without generating audio files."""
        lines = [
            VoiceLine(
                scene_id=scene.scene_id,
                title=scene.title,
                speaker="narrator",
                text=scene.tts_text,
                duration_sec=scene.duration_sec,
                voice_style=self._voice_style_for_scene(scene),
                output_filename=f"voice_{scene.scene_id.lower()}.wav",
            )
            for scene in render_project.scenes
        ]
        return VoiceProject(
            project_title=render_project.project_title,
            total_duration_sec=render_project.total_duration_sec,
            lines=lines,
            notes=[
                "v0.1 only prepares TTS script metadata.",
                "No audio file is generated in this step.",
            ],
        )

    def build_image_prompt_project(
        self,
        render_project: RenderProject,
    ) -> ImagePromptProject:
        """Prepare image prompts without calling an image-generation model."""
        items = [
            ImagePromptItem(
                scene_id=scene.scene_id,
                title=scene.title,
                prompt=scene.image_prompt,
                negative_prompt="low quality, blurry, watermark, unreadable text",
                visual_style=scene.visual_style or render_project.visual_theme,
                aspect_ratio=self._aspect_ratio(render_project.target_resolution),
                output_filename=f"image_{scene.scene_id.lower()}.png",
            )
            for scene in render_project.scenes
        ]
        return ImagePromptProject(
            project_title=render_project.project_title,
            total_images=len(items),
            items=items,
            notes=[
                "v0.1 only prepares image prompt metadata.",
                "No image file is generated in this step.",
            ],
        )

    def build_shot_storyboard(
        self,
        render_project: RenderProject,
    ) -> ShotStoryboardProject:
        """Prepare a one-shot-per-scene storyboard plan."""
        shots = [
            ShotItem(
                shot_id=f"SH{index:02d}",
                scene_id=scene.scene_id,
                title=scene.title,
                duration_sec=scene.duration_sec,
                camera_style=scene.camera_style,
                visual_style=scene.visual_style or render_project.visual_theme,
                image_prompt=scene.image_prompt,
                subtitle_text=scene.subtitle_text,
                transition_type=scene.transition_type,
            )
            for index, scene in enumerate(render_project.scenes, start=1)
        ]
        return ShotStoryboardProject(
            project_title=render_project.project_title,
            total_shots=len(shots),
            shots=shots,
            notes=[
                "v0.1 creates one storyboard shot per scene.",
                "Future versions can split scenes into multiple shots.",
            ],
        )

    def build_video_manifest(
        self,
        render_project: RenderProject,
    ) -> VideoManifestProject:
        """Prepare a video assembly manifest without invoking ffmpeg."""
        scenes = [
            VideoManifestScene(
                scene_id=scene.scene_id,
                duration_sec=scene.duration_sec,
                image_asset=f"image_{scene.scene_id.lower()}.png",
                voice_asset=f"voice_{scene.scene_id.lower()}.wav",
                subtitle_text=scene.subtitle_text,
                transition_type=scene.transition_type,
                bgm_intensity=scene.bgm_intensity,
            )
            for scene in render_project.scenes
        ]
        return VideoManifestProject(
            project_title=render_project.project_title,
            target_resolution=render_project.target_resolution,
            fps=render_project.fps,
            total_duration_sec=render_project.total_duration_sec,
            visual_theme=render_project.visual_theme,
            scenes=scenes,
            notes=[
                "v0.1 only prepares a video assembly manifest.",
                "No mp4 file is generated in this step.",
            ],
        )

    def _voice_style_for_scene(self, scene: RenderScene) -> str:
        """Map mood and intensity into a simple voice direction."""
        if scene.bgm_intensity >= 5 or "混亂" in scene.mood:
            return "urgent_low_voice"
        if "壓迫" in scene.mood:
            return "slow_tense_voice"
        if "緊張" in scene.mood:
            return "controlled_whisper"
        return "calm_first_person_narration"

    def _aspect_ratio(self, resolution: str) -> str:
        """Infer aspect ratio text from a WxH resolution string."""
        try:
            width_text, height_text = resolution.lower().split("x", maxsplit=1)
            width = int(width_text)
            height = int(height_text)
        except ValueError:
            return "9:16"

        if width <= 0 or height <= 0:
            return "9:16"
        if width == height:
            return "1:1"
        return "9:16" if height > width else "16:9"
