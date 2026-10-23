"""
インフラストラクチャ層 (JsonScheduleRepository) の単体テスト
"""

import json
from pathlib import Path

from domain.models import Session, Track
from infrastructure.json_repository import JsonScheduleRepository


def test_load_real_program_json():
    """実ファイル data/ibis2026_program.json のロードと整合性検証"""
    repo_root = Path(__file__).parent.parent
    json_path = repo_root / "data" / "ibis2026_program.json"
    assert json_path.exists(), "data/ibis2026_program.json が見つかりません"

    repo = JsonScheduleRepository(json_path)

    # 日程データのロード検証
    days = repo.load_days()
    assert len(days) == 4
    assert [d["id"] for d in days] == ["day-1", "day-2", "day-3", "day-4"]
    assert [d["date"] for d in days] == [
        "2026-10-26",
        "2026-10-27",
        "2026-10-28",
        "2026-10-29",
    ]

    # 全セッションデータのロード検証
    sessions = repo.load_all_sessions()
    assert len(sessions) == 31

    # ドメインモデルの属性検証
    valid_dates = {"2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29"}
    for s in sessions:
        assert isinstance(s, Session)
        assert s.session_id
        assert s.day in valid_dates
        assert isinstance(s.track, Track)
        assert s.track.code in ["Track A", "Track B", "Track C"]
        assert s.track.sort_order in [1, 2, 3]
        assert s.start_minutes < s.end_minutes
        for talk in s.talks:
            assert talk.title
            assert talk.speaker is not None


def test_repository_non_existent_file(tmp_path: Path):
    """存在しないファイルパスが指定された場合のハンドリング"""
    non_existent = tmp_path / "does_not_exist.json"
    repo = JsonScheduleRepository(non_existent)

    assert repo.load_all_sessions() == []
    assert repo.load_days() == []


def test_repository_corrupt_json(tmp_path: Path):
    """構文エラーのあるJSONファイルが指定された場合の安全なハンドリング"""
    corrupt_file = tmp_path / "corrupt.json"
    corrupt_file.write_text("{ this is invalid json syntax : [", encoding="utf-8")
    repo = JsonScheduleRepository(corrupt_file)

    assert repo.load_all_sessions() == []
    assert repo.load_days() == []


def test_repository_track_string_fallback(tmp_path: Path):
    """track が文字列として定義されている場合のフォールバックパース検証"""
    sample_data = {
        "days": [{"day": "Day 1", "date": "2026-10-27"}],
        "sessions": [
            {
                "session_id": "test-b",
                "day": "Day 1",
                "title": "国際セッション",
                "track": "国際会議室 (Track B)",
                "category": "os",
                "start_time": "10:00",
                "end_time": "12:00",
                "talks": [],
            },
            {
                "session_id": "test-c",
                "day": "Day 1",
                "title": "ポスターセッション",
                "track": "市民ホール (Track C)",
                "category": "poster",
                "start_time": "10:00",
                "end_time": "12:00",
                "talks": [],
            },
            {
                "session_id": "test-a",
                "day": "Day 1",
                "title": "メインセッション",
                "track": "メインホール",
                "category": "invited",
                "start_time": "10:00",
                "end_time": "12:00",
                "talks": [],
            },
        ],
    }

    test_file = tmp_path / "test_program.json"
    test_file.write_text(json.dumps(sample_data, ensure_ascii=False), encoding="utf-8")
    repo = JsonScheduleRepository(test_file)
    sessions = repo.load_all_sessions()

    assert len(sessions) == 3
    s_b = next(s for s in sessions if s.session_id == "test-b")
    s_c = next(s for s in sessions if s.session_id == "test-c")
    s_a = next(s for s in sessions if s.session_id == "test-a")

    assert s_b.track.code == "Track B"
    assert s_b.track.sort_order == 2
    assert s_c.track.code == "Track C"
    assert s_c.track.sort_order == 3
    assert s_a.track.code == "Track A"
    assert s_a.track.sort_order == 1


def test_repository_empty_or_minimal_session(tmp_path: Path):
    """トークや登壇者が空の最小限のセッションでも安全にパースされること"""
    sample_data = {
        "sessions": [
            {
                "session_id": "minimal-1",
                "day": "Day 1",
                "title": "休憩",
            }
        ]
    }
    test_file = tmp_path / "minimal.json"
    test_file.write_text(json.dumps(sample_data), encoding="utf-8")
    repo = JsonScheduleRepository(test_file)
    sessions = repo.load_all_sessions()

    assert len(sessions) == 1
    session = sessions[0]
    assert session.session_id == "minimal-1"
    assert session.start_time == "09:00"
    assert session.end_time == "10:00"
    assert session.start_minutes == 540
    assert session.end_minutes == 600
    assert session.talks == []
