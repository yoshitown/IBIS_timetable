"""
アプリケーション層 (ScheduleService) の単体テスト
設計原則: 並行3トラック集約、全日程の網羅、値注入によるLIVE判定、ルーティング境界防御の検証
"""

from pathlib import Path

import pytest

from application.schedule_service import ScheduleService
from domain.models import Session, Track
from infrastructure.json_repository import JsonScheduleRepository


@pytest.fixture
def service():
    repo_root = Path(__file__).parent.parent
    repo = JsonScheduleRepository(repo_root / "data" / "ibis2026_program.json")
    return ScheduleService(repo)


def test_get_days(service: ScheduleService):
    """開催日程一覧の取得検証"""
    days = service.get_days()
    assert len(days) == 4
    dates = [d["date"] for d in days]
    assert dates == ["2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29"]


@pytest.mark.parametrize(
    "date, expected_min_blocks, expected_date",
    [
        ("2026-10-26", 2, "2026-10-26"),  # Day 1: チュートリアル
        ("2026-10-27", 4, "2026-10-27"),  # Day 2: 3トラック並行
        ("2026-10-28", 3, "2026-10-28"),  # Day 3: 国際セッション
        ("2026-10-29", 3, "2026-10-29"),  # Day 4: 3トラック並行
    ],
)
def test_all_conference_days_schedule(
    service: ScheduleService, date: str, expected_min_blocks: int, expected_date: str
):
    """Day 1〜Day 4 の各日程におけるタイムブロック構築と整合性の検証"""
    schedule = service.get_day_schedule(date=date)
    assert schedule.date == expected_date
    assert len(schedule.time_blocks) >= expected_min_blocks
    # 各ブロック内のセッションが Track 順 (sort_order) で昇順ソートされていること
    for block in schedule.time_blocks:
        sort_orders = [s.track.sort_order for s in block.sessions]
        assert sort_orders == sorted(sort_orders)


def test_parallel_3_tracks_grouping_and_sorting(service: ScheduleService):
    """Day 2 の 10:00-12:00 における並行3トラックの完全網羅と整列検証"""
    day2_schedule = service.get_day_schedule(date="2026-10-27")
    block_10_12 = next(
        b for b in day2_schedule.time_blocks if b.start_time == "10:00" and b.end_time == "12:00"
    )

    # 並行 3 トラックであること！
    assert block_10_12.parallel_count == 3

    # ドメイン層で Track A → Track B → Track C 順に整列されていること！
    tracks = [s.track.code for s in block_10_12.sessions]
    assert tracks == ["Track A", "Track B", "Track C"]


def test_ongoing_time_injection(service: ScheduleService):
    """時刻注入による進行中セッションの特定と境界値"""
    # 11:20 (680分) -> 10:00-12:00 の代表セッション (Track A: OS1)
    ongoing = service.get_ongoing_session(date="2026-10-27", current_minutes=680)
    assert ongoing is not None
    assert ongoing.session_id == "d2-os-1"
    assert ongoing.track.code == "Track A"

    # 早朝 (08:00 = 480分) -> None
    assert service.get_ongoing_session(date="2026-10-27", current_minutes=480) is None

    # 夜間終了後 (21:00 = 1260分) -> None
    assert service.get_ongoing_session(date="2026-10-27", current_minutes=1260) is None


def test_session_detail_and_navigation(service: ScheduleService):
    """セッション詳細と前後ナビゲーションの取得検証"""
    result = service.get_session_detail("d2-os-1")
    assert result.is_found is True
    assert result.session is not None
    assert "物理学と機械学習理論" in result.session.title
    assert len(result.session.talks) == 4

    assert result.navigation is not None
    assert result.navigation.previous_session is not None
    assert result.navigation.next_session is not None


def test_session_detail_first_and_last_navigation(service: ScheduleService):
    """同一日内の先頭および末尾セッションでの前後ナビゲーション境界値検証"""
    all_sessions = service.get_all_sessions()
    day1_sessions = [s for s in all_sessions if s.day == "2026-10-26"]
    first_session_id = day1_sessions[0].session_id
    last_session_id = day1_sessions[-1].session_id

    # 日内先頭セッション: 前は None, 次は 存在する
    first_result = service.get_session_detail(first_session_id)
    assert first_result.is_found is True
    assert first_result.navigation is not None
    assert first_result.navigation.previous_session is None
    assert first_result.navigation.next_session is not None

    # 日内末尾セッション: 前は 存在する, 次は None
    last_result = service.get_session_detail(last_session_id)
    assert last_result.is_found is True
    assert last_result.navigation is not None
    assert last_result.navigation.previous_session is not None
    assert last_result.navigation.next_session is None


def test_session_detail_single_session_repository():
    """セッションが1件しかない場合の前後ナビゲーション（両方 None）"""
    single_session = Session(
        session_id="only-one",
        day="2026-10-26",
        day_label="Day 1",
        title="唯一のセッション",
        track=Track(code="Track A", name="メイン", sort_order=1),
        category="general",
        start_time="10:00",
        end_time="11:00",
        start_minutes=600,
        end_minutes=660,
    )

    class MockRepo:
        def load_all_sessions(self):
            return [single_session]

        def load_days(self):
            return []

    mock_service = ScheduleService(MockRepo())  # type: ignore
    result = mock_service.get_session_detail("only-one")
    assert result.is_found is True
    assert result.navigation is not None
    assert result.navigation.previous_session is None
    assert result.navigation.next_session is None


def test_session_detail_boundary_defense(service: ScheduleService):
    """存在しない無効なセッションIDに対する境界防御"""
    result = service.get_session_detail("invalid-session-999")
    assert result.is_found is False
    assert result.session is None
    assert result.navigation is None
    assert "存在しません" in result.error_message


def test_filter_sessions(service: ScheduleService):
    """ScheduleService 経由でのフィルタリング検証"""
    # カテゴリ絞り込み
    invited_sessions = service.filter_sessions(category="invited")
    assert len(invited_sessions) > 0
    assert all(s.category == "invited" for s in invited_sessions)

    # 日付絞り込み
    d1_sessions = service.filter_sessions(day="2026-10-26")
    assert len(d1_sessions) > 0
    assert all(s.day == "2026-10-26" for s in d1_sessions)

    # 検索キーワード
    ml_sessions = service.filter_sessions(keyword="強化学習")
    assert len(ml_sessions) > 0
