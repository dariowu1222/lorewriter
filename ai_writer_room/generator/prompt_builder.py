"""Prompt assembly utilities for storyboard generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ai_writer_room.evaluator.forbidden_word_checker import DEFAULT_FORBIDDEN_WORDS


@dataclass(slots=True)
class PromptContext:
    """Structured inputs used to render a generation prompt."""

    premise: str
    target_minutes: int = 3
    genre: str = "rule_horror"
    constraints: list[str] = field(default_factory=list)
    story_bible: str | None = None


class PromptBuilder:
    """Build prompts from local templates and structured context."""

    def __init__(self, prompts_dir: Path | str = Path("prompts")) -> None:
        """Create a prompt builder using a prompt template directory."""
        candidate = Path(prompts_dir)
        if not candidate.is_absolute() and not candidate.exists():
            candidate = Path(__file__).resolve().parents[1] / candidate

        self.prompts_dir = candidate

    def load_template(self, template_name: str) -> str:
        """Load a prompt template by filename."""
        template_path = self.prompts_dir / template_name
        return template_path.read_text(encoding="utf-8")

    def build_rule_horror_prompt(
        self,
        sub_genre: str,
        duration_sec: int = 180,
        rules_count: int = 5,
        scene_count: int = 12,
    ) -> str:
        """Build the v0.1 rule horror storyboard generation prompt."""
        template = self.load_template("rule_horror.tmpl")
        return template.format(
            sub_genre=sub_genre,
            duration_sec=duration_sec,
            rules_count=rules_count,
            scene_count=scene_count,
            scene_structure=self.get_scene_structure_text(),
            golden_rules=self.get_golden_rules_text(),
            twist_templates=self.get_twist_templates_text(),
            forbidden_words=self.get_forbidden_words_text(),
            output_schema_notes=self.get_output_schema_notes(),
        )

    def build_evaluator_prompt(
        self,
        storyboard_json: str,
        eval_rules: str,
    ) -> str:
        """Build a future LLM-as-judge evaluator prompt."""
        template = self.load_template("evaluator.tmpl")
        return template.format(
            storyboard_json=storyboard_json,
            eval_rules=eval_rules,
            forbidden_words=self.get_forbidden_words_text(),
        )

    def build_auto_fix_prompt(
        self,
        storyboard_json: str,
        eval_result_json: str,
        fix_instructions: str,
    ) -> str:
        """Build a future auto-fix prompt from evaluator feedback."""
        template = self.load_template("auto_fix.tmpl")
        return template.format(
            storyboard_json=storyboard_json,
            eval_result_json=eval_result_json,
            fix_instructions=fix_instructions,
        )

    def get_scene_structure_text(self) -> str:
        """Return the fixed S01-S12 short-form storyboard structure."""
        return "\n".join(
            [
                "S01 主角進場",
                "S02 第一規則",
                "S03 規則驗證",
                "S04 第二規則",
                "S05 第一異常",
                "S06 規則衝突",
                "S07 主角懷疑",
                "S08 中段反轉",
                "S09 世界崩壞",
                "S10 真相接近",
                "S11 主反轉",
                "S12 尾刀",
            ]
        )

    def get_golden_rules_text(self) -> str:
        """Return the five golden rules for rule-horror design."""
        return "\n".join(
            [
                "1. 規則必須像安全指示，不像謎語。",
                "2. 規則必須可被行動驗證，不能只停留在氣氛描述。",
                "3. 規則違反後必須產生具體代價。",
                "4. 規則之間至少要有一處壓力或衝突。",
                "5. 最終反轉必須重新定義讀者對規則來源的理解。",
            ]
        )

    def get_twist_templates_text(self) -> str:
        """Return five reusable twist templates for rule horror."""
        return "\n".join(
            [
                "1. 保護規則其實是在篩選受害者。",
                "2. 看似違規的角色其實是唯一遵守真規則的人。",
                "3. 主角以為自己逃離空間，其實只是進入下一層規則。",
                "4. 發布規則的人不是管理者，而是被困最久的前任受害者。",
                "5. 尾刀揭露主角早已成為規則的一部分。",
            ]
        )

    def get_forbidden_words_text(self) -> str:
        """Return the Step 3 forbidden-word list."""
        return "\n".join(f"- {word}" for word in DEFAULT_FORBIDDEN_WORDS)

    def get_output_schema_notes(self) -> str:
        """Return required storyboard JSON field notes."""
        return "\n".join(
            [
                "根物件必須包含 title, sub_genre, target_duration_sec, generated_at, model, cost_usd。",
                "根物件必須包含 prologue, story_bible, scenes, memory_summary, foreshadowing。",
                "story_bible 必須包含 rules，且每條 rule 需要 id, text, category, is_visual, expected_scene_ids。",
                "scenes 必須固定 12 筆，id 從 S01 到 S12。",
                "每個 scene 必須包含 title, function, mood, bgm_intensity, time_in_story, narration_zh。",
                "每個 scene 必須包含 dialogue_lines, rule_refs, foreshadow_refs。",
                "dialogue_lines 每筆必須包含 speaker 與 text。",
                "rule_refs 必須引用 story_bible.rules 中存在的 rule id。",
            ]
        )

