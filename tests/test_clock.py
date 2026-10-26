"""
Clock (Strategy) / ClockFactory の単体テスト
"""

import logging
from datetime import datetime, timezone

import pytest

from domain.clock import JST, FixedClock, SystemClock, parse_clock_override
from infrastructure.clock_factory import ClockFactory


def test_system_clock_returns_jst_aware_now():
    clock = SystemClock()
    now = clock.now()
    assert now.tzinfo is not None
    assert now.utcoffset() == datetime.now(JST).utcoffset()
    assert clock.is_simulated is False


def test_fixed_clock_returns_fixed_time():
    fixed = datetime(2026, 10, 27, 11, 20, tzinfo=JST)
    clock = FixedClock(fixed)
    assert clock.now() == fixed
    assert clock.is_simulated is True


def test_parse_with_date():
    assert parse_clock_override("2026-10-27 11:20") == datetime(2026, 10, 27, 11, 20, tzinfo=JST)


def test_parse_time_only_uses_today_date():
    today = datetime(2026, 10, 28, 3, 0, tzinfo=JST)
    assert parse_clock_override(" 11:20 ", today=today) == datetime(
        2026, 10, 28, 11, 20, tzinfo=JST
    )


def test_parse_time_only_converts_today_to_jst():
    # UTC 10/27 20:00 は JST では 10/28
    today = datetime(2026, 10, 27, 20, 0, tzinfo=timezone.utc)
    assert parse_clock_override("09:05", today=today) == datetime(2026, 10, 28, 9, 5, tzinfo=JST)


@pytest.mark.parametrize("value", [None, "", "   ", "abc", "25:00", "2026-13-01 10:00"])
def test_parse_invalid_returns_none(value):
    assert parse_clock_override(value) is None


def test_factory_without_env_returns_system_clock():
    assert isinstance(ClockFactory.from_environ({}), SystemClock)
    assert isinstance(ClockFactory.from_environ({"IBIS_DEBUG_NOW": "  "}), SystemClock)


def test_factory_with_valid_env_returns_fixed_clock():
    clock = ClockFactory.from_environ({"IBIS_DEBUG_NOW": "2026-10-27 11:20"})
    assert isinstance(clock, FixedClock)
    assert clock.now() == datetime(2026, 10, 27, 11, 20, tzinfo=JST)


def test_factory_with_invalid_env_falls_back_and_warns(caplog):
    with caplog.at_level(logging.WARNING):
        clock = ClockFactory.from_environ({"IBIS_DEBUG_NOW": "bad"})
    assert isinstance(clock, SystemClock)
    assert "IBIS_DEBUG_NOW" in caplog.text
