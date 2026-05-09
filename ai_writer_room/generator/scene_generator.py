"""Scene-level generation orchestration."""

from __future__ import annotations

from dataclasses import dataclass

from ai_writer_room.generator.api_client import APIClient
from ai_writer_room.schemas.scene_schema import SceneDraft


@dataclass(slots=True)
class SceneGenerator:
    """Generate and revise individual storyboard scenes."""

    api_client: APIClient

    def generate_scene(self, scene_id: str, prompt: str) -> SceneDraft:
        """Generate a single scene draft from a prompt."""
        raise NotImplementedError("Scene generation is planned for v0.2.")

    def revise_scene(self, scene: SceneDraft, feedback: list[str]) -> SceneDraft:
        """Revise a scene using evaluator feedback."""
        raise NotImplementedError("Scene revision is planned for v0.2.")
