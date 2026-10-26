"""
LiveContext (Null Object) の単体テスト
"""

from datetime import datetime
from pathlib import Path

import pytest

from application.schedule_service import ScheduleService
from domain.clock import JST
from domain.live import ActiveLive, NoLive, live_context_for_day
from infrastructure.json_repository import JsonScheduleRepository

DATA_PATH = Path(__file__).parent.parent / "data" / "ibis2026_program.json"


@pytest.fixture
def service() -> ScheduleService:
    return ScheduleService(JsonScheduleRepository(DATA_PATH))


def test_for_day_returns_active_on_same_date():
    live = live_context_for_day(datetime(2026, 10, 27, 11, 20, tzinfo=JST), "2026-10-27")
    assert isinstance(live, ActiveLive)
    assert live.minutes == 680
    assert live.label == "11:20"


def test_for_day_returns_no_live_on_other_date():
    live = live_context_for_day(datetime(2026, 10, 27, 11, 20, tzinfo=JST), "2026-10-28")
    assert isinstance(live, NoLive)


def test_active_live_queries(service: ScheduleService):
    schedule = service.get_day_schedule(date="2026-10-27")
    live = ActiveLive(680)  # 11:20

    ongoing = live.ongoing_session(schedule)
    assert ongoing is not None and ongoing.session_id == "d2-os-1"
    assert live.is_ongoing(ongoing) is True
    assert live.remaining_minutes(ongoing) == max(0, ongoing.end_minutes - 680)

    first_block = schedule.time_blocks[0]
    assert live.marker_precedes(first_block) == (680 <= first_block.end_minutes)
    assert ActiveLive(1260).ongoing_session(schedule) is None


def test_no_live_is_always_inactive(service: ScheduleService):
    schedule = service.get_day_schedule(date="2026-10-27")
    live = NoLive()
    session = schedule.time_blocks[0].sessions[0]

    assert live.label == ""
    assert live.ongoing_session(schedule) is None
    assert live.is_ongoing(session) is False
    assert live.remaining_minutes(session) == 0
    assert live.marker_precedes(schedule.time_blocks[0]) is False


def test_service_get_live_session(service: ScheduleService):
    assert service.get_live_session("2026-10-27", ActiveLive(680)).session_id == "d2-os-1"
    assert service.get_live_session("2026-10-27", NoLive()) is None
