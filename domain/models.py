"""
ドメインモデル層: 学術カンファレンス (IBIS2026) のビジネスデータ構造と振る舞いをカプセル化
"""

from dataclasses import dataclass, field
from typing import List, Optional


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
    """タイムテーブル上のセッション枠（チュートリアル、企画セッション、招待講演など）"""
    session_id: str
    day: str  # 例: "2026-10-27"
    day_label: str  # 例: "Day 2: Oct 27 (Tue)"
    title: str
    track: str  # 例: "Main Hall (2F)"
    category: str  # "tutorial" | "os" | "invited" | "poster" | "panel" | "general"
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
        """セッションの所要時間（分）"""
        return self.end_minutes - self.start_minutes

    @property
    def primary_speaker_names(self) -> str:
        """主な登壇者名一覧の文字列"""
        if not self.talks:
            return ""
        return " • ".join(t.speaker.name for t in self.talks)

    def is_ongoing(self, minutes: int) -> bool:
        """指定時刻（0:00からの通算分）に進行中であるかを判定"""
        return self.start_minutes <= minutes < self.end_minutes

    def matches_keyword(self, keyword: str) -> bool:
        """キーワードがタイトル、要旨、オーガナイザー、各講演に含まれるかを判定"""
        if not keyword:
            return True
        kw = keyword.lower()
        in_title = kw in self.title.lower()
        in_abstract = self.abstract is not None and kw in self.abstract.lower()
        in_organizer = self.organizer is not None and kw in self.organizer.lower()
        in_track = kw in self.track.lower()
        in_talks = any(talk.matches(kw) for talk in self.talks)
        return in_title or in_abstract or in_organizer or in_track or in_talks
