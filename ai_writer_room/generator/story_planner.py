"""High-level planning for short and long-form story structure."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

from ai_writer_room.generator.rule_engine import RuleEngine
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
    rule_engine = RuleEngine()
    rules = rule_engine.build_mock_rules(sub_genre=sub_genre, rules_count=5)
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

    return Storyboard(
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
        story_bible={
            "setting": sub_genre,
            "rules": [asdict(rule) for rule in rules],
            "protagonist": "一名錯過正常班次的普通上班族",
            "threat": "會利用規則漏洞誘導乘客犯錯的異常空間",
        },
        scenes=scenes,
        memory_summary={
            "current_state": "v0.1 mock storyboard；尚未接入長篇記憶系統。",
            "open_threads": ["月台編號消失", "陌生人是否可信", "規則來源未知"],
        },
        foreshadowing=[
            {
                "id": "F01",
                "setup": "廣播聲音與主角童年記憶相同。",
                "payoff": "主反轉時揭露廣播不是系統，而是另一個自己。",
            },
            {
                "id": "F02",
                "setup": "車窗倒影比現實慢三秒。",
                "payoff": "世界崩壞時倒影先做出逃生手勢。",
            },
            {
                "id": "F03",
                "setup": "空座位上一直放著一張未撕票根。",
                "payoff": "尾刀時票根上出現主角的名字。",
            },
            {
                "id": "F04",
                "setup": "陌生人從不踩到車廂燈光下。",
                "payoff": "真相接近時暗示他不是乘客。",
            },
        ],
    )


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

