"""
アプリケーション層 (ScheduleService) の単体テスト
設計原則: 並行3トラック集約、値注入によるLIVE判定、ルーティング境界防御の検証
"""

from pathlib import Path

import pytest

from application.schedule_service import ScheduleService
from infrastructure.json_repository import JsonScheduleRepository


@pytest.fixture
def service():
    repo = JsonScheduleRepository(Path("data/ibis2026_program.json"))
    return ScheduleService(repo)


def test_parallel_3_tracks_grouping_and_sorting(service: ScheduleService):
    # Day 2 スケジュールの取得
    day2_schedule = service.get_day_schedule(date="2026-10-27")
    assert len(day2_schedule.time_blocks) >= 4

    # 10:00 - 12:00 のタイムブロックを特定
    block_10_12 = next(
        b for b in day2_schedule.time_blocks if b.start_time == "10:00" and b.end_time == "12:00"
    )

    # 並行 3 トラックであること！
    assert block_10_12.parallel_count == 3

    # ドメイン層で Track A → Track B → Track C 順に整列されていること！
    tracks = [s.track.code for s in block_10_12.sessions]
    assert tracks == ["Track A", "Track B", "Track C"]


def test_ongoing_time_injection(service: ScheduleService):
    # 外部から時刻 11:20 (680分) を値として注入して進行中セッションを検証
    ongoing = service.get_ongoing_session(date="2026-10-27", current_minutes=680)
    assert ongoing is not None
    # 10:00-12:00 の代表セッション (Track A: OS1) が取得されること
    assert ongoing.session_id == "d2-os-1"

    # セッション外の早朝 (08:00 = 480分) では None が返ること
    assert service.get_ongoing_session(date="2026-10-27", current_minutes=480) is None


def test_session_detail_and_navigation(service: ScheduleService):
    # 有効なセッション詳細取得
    result = service.get_session_detail("d2-os-1")
    assert result.is_found is True
    assert result.session is not None
    assert "物理学と機械学習理論" in result.session.title
    assert len(result.session.talks) == 4
    # 前後ナビゲーションが正しく設定されていること
    assert result.navigation is not None
    assert result.navigation.previous_session is not None  # オープニング
    assert result.navigation.next_session is not None  # Track B チュートリアル


def test_session_detail_boundary_defense(service: ScheduleService):
    # 存在しない無効なセッションIDに対する境界防御
    result = service.get_session_detail("invalid-session-999")
    assert result.is_found is False
    assert result.session is None
    assert "存在しません" in result.error_message
