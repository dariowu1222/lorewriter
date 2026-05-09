"""High-level planning for short and long-form story structure."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from ai_writer_room.generator.rule_engine import RuleEngine
from ai_writer_room.memory.arc_planner import ArcPhase, ArcPlan
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
        "冷靜觀察",
        "秩序壓迫",
        "試探規則",
        "資訊增加",
        "異常逼近",
        "邏輯打結",
        "信任動搖",
        "認知翻轉",
        "世界失序",
        "答案逼近",
        "核心揭露",
        "餘韻反咬",
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
                    f"{scene_id}：我在{sub_genre}的規則裡前進，"
                    f"這一幕負責{scene_function}，讓規則從文字變成代價。"
                ),
                dialogue_lines=[
                    DialogueLine(
                        speaker="我",
                        text=f"如果{sub_genre}的告示是真的，我現在只能照做。",
                    ),
                    DialogueLine(
                        speaker="廣播",
                        text="請依照規則停留在原位，下一段行程將重新確認乘客身分。",
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
            f"我搭上{sub_genre}後，才發現車廂裡的告示不是提醒，"
            "而是已經被驗證過的生存方式。"
        ),
        story_bible={},
        scenes=scenes,
        memory_summary={},
        foreshadowing=[],
        arc_plan=None,
    )
    storyboard.story_bible = build_initial_story_bible(storyboard)
    storyboard.memory_summary = build_initial_memory_summary(storyboard)
    storyboard.foreshadowing = ForeshadowTracker().build_initial_foreshadowing(
        storyboard,
    )
    storyboard.arc_plan = build_initial_arc_plan(storyboard)
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
        protagonist_name="我",
        world_summary=(
            f"{storyboard.sub_genre}是一個以公共秩序包裝生存條件的封閉空間，"
            "規則會保護遵守者，也會標記違規者。"
        ),
        tone_keywords=["規則怪談", "壓迫", "反轉", "秩序失效"],
        core_theme="當規則是真的，自由意志會變成最危險的錯覺。",
        arc_summary="A01 世界建立啟動，主角正在接觸第一批規則。",
        active_arc_id="A01",
        current_story_stage="世界建立",
        characters=[
            CharacterProfile(
                id="C01",
                name="我",
                role="第一人稱主角",
                traits=["謹慎", "觀察力強", "會驗證規則"],
                secrets=["曾經在類似規則中失去關鍵記憶"],
                introduced_scene_id="S01",
                status="active",
                suspicion_level=3,
            )
        ],
        world_rules=world_rules,
        major_questions=[
            "規則是誰寫下的？",
            "廣播中的管理者是否仍是人？",
            "主角是否早已被納入規則系統？",
        ],
        hidden_truths=[
            "規則不是警告，而是空間維持自身的方法。",
            "主角的選擇會決定下一版規則如何改寫。",
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
    active_foreshadow_ids = sorted(
        {
            foreshadow_ref
            for scene in storyboard.scenes
            for foreshadow_ref in scene.foreshadow_refs
        }
    )
    last_scene = storyboard.scenes[-1] if storyboard.scenes else None
    last_major_event = (
        f"{last_scene.id} {last_scene.function}" if last_scene else "尚未開始"
    )

    return MemorySummary(
        current_arc_summary=(
            f"{storyboard.title}目前完成短篇 storyboard 初始化，"
            "長篇版本仍停留在 Arc 1 的世界建立階段。"
        ),
        protagonist_goal="確認規則來源並找到離開封閉空間的方法。",
        protagonist_status="仍能行動，但已被規則系統辨識。",
        current_arc_id="A01",
        current_arc_goal="建立世界、主角處境與第一規則。",
        latest_payoff="尚未發生",
        known_rules=known_rules,
        unresolved_questions=[
            "規則來源是否可信？",
            "廣播背後的身分是什麼？",
            "主角是否已經違反過真正的規則？",
        ],
        active_foreshadow_ids=active_foreshadow_ids,
        current_threat_level=4,
        emotional_curve="觀察 -> 試探 -> 懷疑 -> 翻轉 -> 餘韻",
        last_major_event=last_major_event,
    )


def build_initial_arc_plan(storyboard: Storyboard) -> ArcPlan:
    """Build the fixed six-arc long-form structure for v0.1."""
    arcs = [
        ArcPhase(
            id="A01",
            name="世界建立",
            purpose="建立主角處境、封閉空間、第一規則與基本代價。",
            emotional_goal="讓觀眾理解表面秩序，同時感到規則正在收緊。",
            threat_level=2,
            target_scene_range="S01-S02",
            setup_requirements=["主角進場", "第一規則", "空間限制"],
            payoff_targets=[],
            twist_type="無",
            status="active",
        ),
        ArcPhase(
            id="A02",
            name="異常擴大",
            purpose="驗證規則有效，擴大異常，安排第一個小 payoff。",
            emotional_goal="把懷疑推向確認，讓主角開始依賴規則。",
            threat_level=4,
            target_scene_range="S03-S05",
            setup_requirements=["規則驗證", "第二規則", "第一異常"],
            payoff_targets=["F02"],
            twist_type="小 payoff",
            status="pending",
        ),
        ArcPhase(
            id="A03",
            name="中段反轉",
            purpose="讓規則互相衝突，迫使主角懷疑自己的身分與記憶。",
            emotional_goal="把安全感轉成不確定，讓觀眾重新解讀前半段。",
            threat_level=6,
            target_scene_range="S06-S08",
            setup_requirements=["規則衝突", "身份懷疑"],
            payoff_targets=["F04"],
            twist_type="中段反轉",
            status="pending",
        ),
        ArcPhase(
            id="A04",
            name="世界真相擴張",
            purpose="揭露空間運作邏輯，安排大型 foreshadow setup。",
            emotional_goal="讓恐懼從個人危機擴大成世界規則。",
            threat_level=7,
            target_scene_range="S09-S10",
            setup_requirements=["世界崩壞", "真相接近"],
            payoff_targets=["F02"],
            twist_type="世界觀擴張",
            status="pending",
        ),
        ArcPhase(
            id="A05",
            name="主反轉",
            purpose="集中回收伏筆並揭露主角和規則系統的真正關係。",
            emotional_goal="把答案變成新的困境，讓觀眾意識到逃生代價。",
            threat_level=9,
            target_scene_range="S11",
            setup_requirements=["主反轉", "payoff 爆發", "真相揭露"],
            payoff_targets=["F01", "F04"],
            twist_type="主反轉",
            status="pending",
        ),
        ArcPhase(
            id="A06",
            name="尾刀",
            purpose="留下餘韻並暗示新規則，讓結尾反咬前文。",
            emotional_goal="讓故事看似結束，實際上把規則傳到下一位讀者。",
            threat_level=6,
            target_scene_range="S12",
            setup_requirements=["尾刀", "餘韻", "新規則暗示"],
            payoff_targets=["F03"],
            twist_type="尾刀",
            status="pending",
        ),
    ]

    return ArcPlan(
        title=f"{storyboard.sub_genre}六段式長篇 Arc Plan",
        total_arcs=len(arcs),
        genre="rule_horror",
        pacing_style="fixed_six_arc_v0.1",
        protagonist_final_goal="理解規則來源，並在不成為新規則的前提下逃離。",
        core_theme="規則越真實，選擇越昂貴。",
        arcs=arcs,
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
        raise NotImplementedError

    def allocate_pacing(self, request: StoryPlanRequest) -> dict[str, int]:
        """Allocate target seconds for each planned story segment."""
        # TODO: Map target runtime into setup, escalation, reveal, and ending.
        raise NotImplementedError
