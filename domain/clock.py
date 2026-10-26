"""
ドメイン層: 現在時刻の供給源 (Strategy パターン)
実時刻 (SystemClock) とデバッグ用の固定時刻 (FixedClock) を同一インターフェースで差し替える。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Optional, Protocol
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")

# (書式, 日付を含むか)。先頭から順に試す
_OVERRIDE_FORMATS: tuple[tuple[str, bool], ...] = (
    ("%Y-%m-%d %H:%M", True),
    ("%H:%M", False),
)


class Clock(Protocol):
    """現在時刻 (JST) を返す時計"""

    is_simulated: bool

    def now(self) -> datetime: ...


class SystemClock:
    """実時刻 (JST) を返す時計"""

    is_simulated: ClassVar[bool] = False

    def now(self) -> datetime:
        return datetime.now(JST)


@dataclass(frozen=True)
class FixedClock:
    """常に同じ時刻を返す時計 (デバッグ・リハーサル用)"""

    fixed: datetime
    is_simulated: ClassVar[bool] = True

    def now(self) -> datetime:
        return self.fixed


def parse_clock_override(
    text: Optional[str], today: Optional[datetime] = None
) -> Optional[datetime]:
    """
    デバッグ用の時刻指定を解釈する。
    'YYYY-MM-DD HH:MM' は日付込み、'HH:MM' は today (既定: 実際の今日) の日付で解釈。
    未設定・不正値は None。
    """
    if not text or not text.strip():
        return None
    value = text.strip()
    for fmt, has_date in _OVERRIDE_FORMATS:
        try:
            parsed = datetime.strptime(value, fmt)
        except ValueError:
            continue
        if not has_date:
            base = today.astimezone(JST) if today else SystemClock().now()
            parsed = parsed.replace(year=base.year, month=base.month, day=base.day)
        return parsed.replace(tzinfo=JST)
    return None
