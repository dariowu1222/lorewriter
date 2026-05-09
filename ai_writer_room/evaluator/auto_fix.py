"""Local deterministic auto-fix utilities."""

from __future__ import annotations

from copy import deepcopy

from ai_writer_room.evaluator.forbidden_word_checker import build_forbidden_word_pattern
from ai_writer_room.evaluator.forbidden_word_config import ForbiddenWordConfig
from ai_writer_room.schemas.storyboard_schema import Storyboard


RULE_REF_TARGET_SCENES: dict[str, str] = {
    "R01": "S02",
    "R02": "S04",
    "R03": "S05",
    "R04": "S06",
    "R05": "S08",
}


class LocalAutoFixer:
    """Apply deterministic local fixes without calling any model provider."""

    def __init__(self, forbidden_words: dict[str, str] | None = None) -> None:
        """Create an auto-fixer with configurable forbidden words."""
        self.forbidden_words = (
            forbidden_words
            if forbidden_words is not None
            else ForbiddenWordConfig.load_default()
        )

    def fix(self, storyboard: Storyboard, eval_result: dict) -> Storyboard:
        """Apply all supported local fixes to a storyboard."""
        fixed = self.ensure_basic_metadata(storyboard)
        fixed = self.fix_forbidden_words(
            storyboard=fixed,
            forbidden_word_check=eval_result.get("forbidden_word_check", {}),
        )
        fixed = self.fix_missing_rule_refs(
            storyboard=fixed,
            rule_check=eval_result.get("rule_check", {}),
        )
        return fixed

    def fix_forbidden_words(
        self,
        storyboard: Storyboard,
        forbidden_word_check: dict,
    ) -> Storyboard:
        """Replace configured forbidden words in narration and dialogue text."""
        fixed = self._copy_storyboard(storyboard)
        if not forbidden_word_check.get("hits"):
            return fixed

        for scene in fixed.scenes:
            scene.narration_zh = self._replace_forbidden_words(scene.narration_zh)
            for line in scene.dialogue_lines:
                line.text = self._replace_forbidden_words(line.text)

        return fixed

    def fix_missing_rule_refs(
        self,
        storyboard: Storyboard,
        rule_check: dict,
    ) -> Storyboard:
        """Add missing rule refs to deterministic target scenes."""
        fixed = self._copy_storyboard(storyboard)
        missing_rule_ids = rule_check.get("missing_rule_ids", [])
        if not missing_rule_ids or not fixed.scenes:
            return fixed

        scene_by_id = {scene.id: scene for scene in fixed.scenes}
        for rule_id in missing_rule_ids:
            target_scene_id = RULE_REF_TARGET_SCENES.get(str(rule_id))
            if target_scene_id is None:
                continue

            target_scene = scene_by_id.get(target_scene_id, fixed.scenes[-1])
            if rule_id not in target_scene.rule_refs:
                target_scene.rule_refs.append(rule_id)

        return fixed

    def ensure_basic_metadata(self, storyboard: Storyboard) -> Storyboard:
        """Ensure basic optional metadata has safe defaults."""
        fixed = self._copy_storyboard(storyboard)
        if not fixed.model:
            fixed.model = "unknown"
        if fixed.cost_usd is None:
            fixed.cost_usd = 0.0
        if not fixed.memory_summary:
            fixed.memory_summary = {}
        if not fixed.foreshadowing:
            fixed.foreshadowing = []
        if not fixed.story_bible:
            fixed.story_bible = {}
        return fixed

    def _replace_forbidden_words(self, text: str) -> str:
        """Replace all configured forbidden words in a text field."""
        fixed_text = text
        for word, replacement in self.forbidden_words.items():
            fixed_text = build_forbidden_word_pattern(word).sub(
                replacement,
                fixed_text,
            )
        return fixed_text

    def _copy_storyboard(self, storyboard: Storyboard) -> Storyboard:
        """Deep-copy a storyboard without sharing nested model state."""
        return deepcopy(storyboard)
