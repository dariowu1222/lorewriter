"""High-level planning for short and long-form story structure."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

from ai_writer_room.generator.rule_engine import RuleEngine
from ai_writer_room.memory.foreshadow_tracker import ForeshadowTracker
from ai_writer_room.memory.memory_summary import MemorySummary
from ai_writer_room.memory.story_bible import (
    CharacterProfile,
    StoryBible,
    WorldRule,
)
from ai_writer_room.schemas.scene_schema import DialogueLine, Scene
from ai_writer_room.schemas.storyboard_schema import Storyboard


MOCK_SCENE_FUNCTIONS: tuple[str, ...] = (
    "主角進場",
    "第一規則",
    "規則驗證",
    "第二規則",
    "第一異常",
    "規則衝突",
    "主角懷疑",
    "中段反轉",
    "世界崩壞",
    "真相接近",
    "主反轉",
    "尾刀",
)


def _format_timestamp(total_seconds: int) -> str:
    """Format seconds as MM:SS for storyboard time ranges."""
    minutes, seconds = divmod(max(total_seconds, 0), 60)
    return f"{minutes:02d}:{seconds:02d}"


def _build_scene_time_ranges(duration_sec: int, scene_count: int) -> list[str]:
    """Build evenly distributed scene time ranges."""
    safe_duration = max(duration_sec, scene_count)
    base_duration = safe_duration // scene_count
    remainder = safe_duration % scene_count
    ranges: list[str] = []
    start = 0

    for index in range(scene_count):
        scene_duration = base_duration + (1 if index < remainder else 0)
        end = start + scene_duration
        ranges.append(f"{_format_timestamp(start)}-{_format_timestamp(end)}")
        start = end

    return ranges


def build_mock_rule_horror_storyboard(
    sub_genre: str,
    duration_sec: int = 180,
) -> Storyboard:
    """Build a local mock rule horror storyboard without calling an AI API."""
    target_duration_sec = max(duration_sec, len(MOCK_SCENE_FUNCTIONS))
    time_ranges = _build_scene_time_ranges(
        target_duration_sec,
        len(MOCK_SCENE_FUNCTIONS),
    )
    moods = (
        "日常偏移",
        "冷靜警告",
        "壓抑驗證",
        "低頻威脅",
        "異常滲入",
        "規則失衡",
        "疑心升高",
        "認知翻轉",
        "秩序崩壞",
        "真相逼近",
        "絕望揭露",
        "餘韻反噬",
    )
    bgm_intensities = (1, 1, 2, 2, 3, 3, 3, 4, 5, 4, 5, 2)
    rule_refs_by_scene = (
        [],
        ["R01"],
        ["R01"],
        ["R02"],
        ["R03"],
        ["R01", "R04"],
        ["R02"],
        ["R05"],
        ["R03", "R04", "R05"],
        ["R04"],
        ["R01", "R05"],
        ["R02", "R03"],
    )
    foreshadow_refs_by_scene = (
        ["F01"],
        ["F01"],
        ["F02"],
        ["F02"],
        ["F03"],
        ["F01", "F03"],
        ["F04"],
        ["F04"],
        ["F02", "F03"],
        ["F04"],
        ["F01", "F04"],
        ["F03"],
    )

    scenes: list[Scene] = []
    for index, scene_function in enumerate(MOCK_SCENE_FUNCTIONS):
        scene_id = f"S{index + 1:02d}"
        scenes.append(
            Scene(
                id=scene_id,
                title=scene_function,
                function=scene_function,
                mood=moods[index],
                bgm_intensity=bgm_intensities[index],
                time_in_story=time_ranges[index],
                narration_zh=(
                    f"{scene_id}「{scene_function}」：在{sub_genre}的規則框架中，"
                    "主角逐步理解提示、誤判限制，最後被自己的選擇推回核心陷阱。"
                ),
                dialogue_lines=[
                    DialogueLine(
                        speaker="主角",
                        text=f"這班{sub_genre}的規則不是提醒，它像是在安排我的下一步。",
                    ),
                    DialogueLine(
                        speaker="陌生人",
                        text="照著紙上寫的做，至少你還能保留選擇。",
                    ),
                ],
                rule_refs=list(rule_refs_by_scene[index]),
                foreshadow_refs=list(foreshadow_refs_by_scene[index]),
            )
        )

    storyboard = Storyboard(
        title=f"{sub_genre}規則怪談",
        sub_genre=sub_genre,
        target_duration_sec=target_duration_sec,
        generated_at=datetime.now(UTC).isoformat(),
        model="local-mock-v0.1",
        cost_usd=0.0,
        prologue=(
            f"主角搭上與{sub_genre}相關的最後一班路線，"
            "發現車廂裡貼著一張只給乘客看的規則表。"
        ),
        story_bible={},
        scenes=scenes,
        memory_summary={},
        foreshadowing=[],
    )
    storyboard.story_bible = build_initial_story_bible(storyboard)
    storyboard.memory_summary = build_initial_memory_summary(storyboard)
    storyboard.foreshadowing = ForeshadowTracker().build_initial_foreshadowing(
        storyboard,
    )
    return storyboard


def build_initial_story_bible(storyboard: Storyboard) -> StoryBible:
    """Build initial Story Bible state from a storyboard."""
    rules = RuleEngine().build_mock_rules(
        sub_genre=storyboard.sub_genre,
        rules_count=5,
    )
    world_rules = [
        WorldRule(
            id=rule.id,
            text=rule.text,
            category=rule.category,
            introduced_scene_id=rule.expected_scene_ids[0]
            if rule.expected_scene_ids
            else "S01",
            verified_scene_ids=_scene_ids_using_rule(storyboard, rule.id),
            broken_scene_ids=["S06"] if rule.id == "R04" else [],
            is_contradictory=rule.id in {"R04", "R05"},
        )
        for rule in rules
    ]

    return StoryBible(
        title=storyboard.title,
        sub_genre=storyboard.sub_genre,
        protagonist_name="主角",
        world_summary=(
            f"{storyboard.sub_genre}被一套會誘導乘客犯錯的規則支配，"
            "每條規則既像保護，也像篩選。"
        ),
        tone_keywords=["規則怪談", "壓迫", "反轉", "日常崩壞"],
        core_theme="真正危險的不是違規，而是不知道誰制定了規則。",
        characters=[
            CharacterProfile(
                id="C01",
                name="主角",
                role="第一人稱敘事者",
                traits=["謹慎", "疲憊", "願意驗證規則"],
                secrets=["曾經看過相同的廣播詞"],
                introduced_scene_id="S01",
                status="active",
                suspicion_level=3,
            )
        ],
        world_rules=world_rules,
        major_questions=[
            "規則表是誰貼上的？",
            "陌生人是否真的想救主角？",
            "末班車的終點是否存在於現實？",
        ],
        hidden_truths=[
            "規則可能不是保護乘客，而是在挑選能留下的人。",
            "主角的記憶和廣播系統之間有未揭露的連結。",
        ],
    )


def build_initial_memory_summary(storyboard: Storyboard) -> MemorySummary:
    """Build initial memory summary state from a storyboard."""
    known_rules = sorted(
        {
            rule_ref
            for scene in storyboard.scenes
            for rule_ref in scene.rule_refs
        }
    )
    last_scene = storyboard.scenes[-1] if storyboard.scenes else None
    last_major_event = (
        f"{last_scene.id} {last_scene.function}" if last_scene else "尚未開始"
    )

    return MemorySummary(
        current_arc_summary=(
            f"{storyboard.title}目前完成短篇 storyboard，主角已接觸規則、"
            "驗證部分規則，並走向尾端反轉。"
        ),
        protagonist_goal="找出規則的來源，並離開異常空間。",
        protagonist_status="仍在規則系統內，尚未確認是否能逃離。",
        known_rules=known_rules,
        unresolved_questions=[
            "誰制定了規則？",
            "陌生人的真實身分是什麼？",
            "主角是否已經成為規則的一部分？",
        ],
        current_threat_level=4,
        emotional_curve="困惑 -> 警覺 -> 驗證 -> 失衡 -> 反轉",
        last_major_event=last_major_event,
    )


def _scene_ids_using_rule(storyboard: Storyboard, rule_id: str) -> list[str]:
    """Return scene ids that reference a rule."""
    return [scene.id for scene in storyboard.scenes if rule_id in scene.rule_refs]


@dataclass(slots=True)
class StoryPlanRequest:
    """Input used to create a story plan."""

    premise: str
    target_minutes: int = 3
    tone: str = "rule_horror"
    constraints: list[str] = field(default_factory=list)


@dataclass(slots=True)
class StoryPlanner:
    """Plan story arcs, scene slots, and pacing targets."""

    def create_outline(self, request: StoryPlanRequest) -> list[str]:
        """Create a high-level outline for storyboard generation."""
        # TODO: Add short-form arc planning for v0.1.
        pass

    def allocate_pacing(self, request: StoryPlanRequest) -> dict[str, int]:
        """Allocate target seconds for each planned story segment."""
        # TODO: Map target runtime into setup, escalation, reveal, and ending.
        pass

