"""
アプリケーション層 (ScheduleService) の単体テスト
"""

from pathlib import Path

import pytest

from application.schedule_service import ScheduleService
from infrastructure.json_repository import JsonScheduleRepository


@pytest.fixture
def service():
    repo = JsonScheduleRepository(Path("data/ibis2026_program.json"))
    return ScheduleService(repo)


def test_service_load_and_filter(service: ScheduleService):
    days = service.get_days()
    assert len(days) == 4

    # Day 2 のセッション取得
    day2_sessions = service.get_filtered_schedule(day="2026-10-27")
    assert len(day2_sessions) >= 3

    # キーワード検索
    results = service.get_filtered_schedule(keyword="Christopher")
    assert len(results) >= 1
    assert any(
        "Rackauckas" in s.title or any("Christopher" in t.speaker.name for t in s.talks)
        for s in results
    )


def test_service_ongoing_session(service: ScheduleService):
    # Day 2 の 11:20 (680分) は 企画セッション1 (10:00-12:00) が進行中
    ongoing = service.get_ongoing_session(day="2026-10-27", minutes=680)
    assert ongoing is not None
    assert ongoing.session_id == "os-1"


def test_service_get_by_id(service: ScheduleService):
    session = service.get_session_by_id("os-1")
    assert session is not None
    assert "物理学と機械学習理論" in session.title
    assert len(session.talks) == 4
