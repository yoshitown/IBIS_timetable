"""
ドメインモデル層: 学術カンファレンス (IBIS2026) のビジネスデータ構造と振る舞いをカプセル化
設計原則: 貧血ドメインモデルの回避、ファーストクラスコレクション、値オブジェクトの導入
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class Track:
    """会場・トラックを表す値オブジェクト (コード、会場名、ソート順序をカプセル化)"""

    code: str  # 例: "Track A", "Track B", "Track C"
    name: str  # 例: "メインホール (2F)", "国際会議室 (3F)", "市民ギャラリー (1F)"
    sort_order: int = 1  # 1: Track A, 2: Track B, 3: Track C, 99: Other

    @property
    def full_label(self) -> str:
        return f"{self.code}: {self.name}"


@dataclass(frozen=True)
class Speaker:
    """登壇者情報"""

    name: str
    affiliation: str

    def matches(self, keyword: str) -> bool:
        kw = keyword.lower()
        return kw in self.name.lower() or kw in self.affiliation.lower()


@dataclass(frozen=True)
class Talk:
    """セッション内の個別講演情報"""

    title: str
    speaker: Speaker
    start_time: str
    end_time: str
    abstract: Optional[str] = None
    citations: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def matches(self, keyword: str) -> bool:
        kw = keyword.lower()
        in_title = kw in self.title.lower()
        in_speaker = self.speaker.matches(kw)
        in_abstract = self.abstract is not None and kw in self.abstract.lower()
        in_tags = any(kw in t.lower() for t in self.tags)
        return in_title or in_speaker or in_abstract or in_tags


@dataclass(frozen=True)
class Session:
    """タイムテーブル上の個別セッション枠"""

    session_id: str
    day: str  # "2026-10-27"
    day_label: str  # "Day 2: 10/27 (火)"
    title: str
    track: Track
    category: str  # "os" | "invited" | "tutorial" | "poster" | "panel" | "general"
    start_time: str  # "10:00"
    end_time: str  # "12:00"
    start_minutes: int  # 600
    end_minutes: int  # 720
    organizer: Optional[str] = None
    talks: List[Talk] = field(default_factory=list)
    abstract: Optional[str] = None
    url: Optional[str] = None

    @property
    def duration_minutes(self) -> int:
        return self.end_minutes - self.start_minutes

    @property
    def primary_speaker_names(self) -> str:
        if not self.talks:
            return ""
        return " • ".join(t.speaker.name for t in self.talks)

    def is_ongoing(self, minutes: int) -> bool:
        """注入された時刻（分）において進行中であるかを判定"""
        return self.start_minutes <= minutes < self.end_minutes

    def matches_keyword(self, keyword: str) -> bool:
        if not keyword:
            return True
        kw = keyword.lower()
        in_title = kw in self.title.lower()
        in_abstract = self.abstract is not None and kw in self.abstract.lower()
        in_organizer = self.organizer is not None and kw in self.organizer.lower()
        in_track = kw in self.track.name.lower() or kw in self.track.code.lower()
        in_talks = any(talk.matches(kw) for talk in self.talks)
        return in_title or in_abstract or in_organizer or in_track or in_talks


@dataclass(frozen=True)
class TimeBlock:
    """
    ファーストクラスコレクション: 同一時間帯に並行開催されるセッション群
    UIコンポーネントでのグルーピング処理を排除し、Track A → B → C 順に整列された不変リストを提供
    """

    start_time: str
    end_time: str
    start_minutes: int
    end_minutes: int
    sessions: List[Session]  # Track.sort_order 順に整列済み

    @property
    def parallel_count(self) -> int:
        return len(self.sessions)

    def is_ongoing(self, minutes: int) -> bool:
        return self.start_minutes <= minutes < self.end_minutes


@dataclass(frozen=True)
class DaySchedule:
    """
    ファーストクラスコレクション: 1日分の全タイムブロックコレクション
    """

    date: str
    label: str
    time_blocks: List[TimeBlock]

    def ongoing_block(self, current_minutes: int) -> Optional[TimeBlock]:
        """現在時刻（分）において進行中のタイムブロックを返却"""
        for block in self.time_blocks:
            if block.is_ongoing(current_minutes):
                return block
        return None


@dataclass(frozen=True)
class SessionNavigation:
    """前後のセッションへのナビゲーションリンク"""

    previous_session: Optional[Session] = None
    next_session: Optional[Session] = None


@dataclass(frozen=True)
class SessionDetailResult:
    """セッション詳細検索結果（境界防御と明示的な型）"""

    session: Optional[Session] = None
    navigation: Optional[SessionNavigation] = None
    is_found: bool = True
    error_message: Optional[str] = None


@dataclass(frozen=True)
class RoomGuide:
    """各部屋・トラックの所在および行き方ガイド値オブジェクト"""

    track_code: str
    room_name: str
    building: str
    floor: str
    access_instruction: str
    note: Optional[str] = None


@dataclass(frozen=True)
class VenueGuide:
    """会場全体・フロアマップ情報のドメインエンティティ"""

    name: str
    address: str
    station_access: str
    map_images: dict[str, str]
    rooms: List[RoomGuide]

    def get_room_guide(self, track_code: str) -> Optional[RoomGuide]:
        """トラックコードまたは部屋名の一部から該当する部屋ガイドを取得"""
        norm_code = track_code.lower()
        for r in self.rooms:
            if r.track_code.lower() in norm_code or norm_code in r.track_code.lower():
                return r
        return None
