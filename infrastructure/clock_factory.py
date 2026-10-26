"""
インフラ層: 環境変数から Clock を組み立てるファクトリ
"""

import logging
from typing import Mapping

from domain.clock import Clock, FixedClock, SystemClock, parse_clock_override

logger = logging.getLogger(__name__)


class ClockFactory:
    """IBIS_DEBUG_NOW が有効なら FixedClock、それ以外は SystemClock を生成"""

    ENV_KEY = "IBIS_DEBUG_NOW"

    @classmethod
    def from_environ(cls, environ: Mapping[str, str]) -> Clock:
        raw = environ.get(cls.ENV_KEY, "")
        if not raw.strip():
            return SystemClock()

        override = parse_clock_override(raw)
        if override is None:
            logger.warning("%s の値を解釈できないため実時刻を使用します: %r", cls.ENV_KEY, raw)
            return SystemClock()
        return FixedClock(override)
