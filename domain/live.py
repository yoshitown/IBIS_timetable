"""
ドメイン層: 「現在ライブ中か」の文脈 (Null Object パターン)
表示中の日が現在日付のときだけ ActiveLive、それ以外は NoLive を用いることで、
UI 側から「ライブ中か」の分岐を排除する。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol

from domain.models import DaySchedule, Session, TimeBlock
from domain.policies import TimePolicy


class LiveContext(Protocol):
    """ライブ表示に必要な問い合わせの集合"""

    @property
    def label(self) -> str: ...

    def marker_precedes(self, block: TimeBlock) -> bool: ...

    def is_ongoing(self, session: Session) -> bool: ...

    def remaining_minutes(self, session: Session) -> int: ...

    def ongoing_session(self, schedule: DaySchedule) -> Optional[Session]: ...


@dataclass(frozen=True)
class ActiveLive:
    """表示中の日が今日: 現在時刻（分）に基づきライブ状態を答える"""

    minutes: int

    @property
    def label(self) -> str:
        return TimePolicy.minutes_to_time_str(self.minutes)

    def marker_precedes(self, block: TimeBlock) -> bool:
        return self.minutes <= block.end_minutes

    def is_ongoing(self, session: Session) -> bool:
        return session.is_ongoing(self.minutes)

    def remaining_minutes(self, session: Session) -> int:
        return max(0, session.end_minutes - self.minutes)

    def ongoing_session(self, schedule: DaySchedule) -> Optional[Session]:
        block = schedule.ongoing_block(self.minutes)
        if block and block.sessions:
            return block.sessions[0]
        return None


class NoLive:
    """表示中の日が今日ではない: 常に非ライブ (Null Object)"""

    label = ""

    def marker_precedes(self, block: TimeBlock) -> bool:
        return False

    def is_ongoing(self, session: Session) -> bool:
        return False

    def remaining_minutes(self, session: Session) -> int:
        return 0

    def ongoing_session(self, schedule: DaySchedule) -> Optional[Session]:
        return None


def live_context_for_day(now: datetime, date: str) -> LiveContext:
    """現在日付が表示中の日と一致すれば ActiveLive、そうでなければ NoLive"""
    if date != now.strftime("%Y-%m-%d"):
        return NoLive()
    return ActiveLive(now.hour * 60 + now.minute)
