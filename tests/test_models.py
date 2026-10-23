"""
ドメインモデルおよびポリシー層の単体テスト
"""

import pytest
from domain.models import Session, Speaker, Talk
from domain.policies import CategoryVisualPolicy, FilterPolicy, TimePolicy


def test_time_policy():
    assert TimePolicy.time_str_to_minutes("10:00") == 600
    assert TimePolicy.time_str_to_minutes("14:30") == 870
    assert TimePolicy.minutes_to_time_str(600) == "10:00"
    assert TimePolicy.minutes_to_time_str(870) == "14:30"


def test_speaker_matching():
    speaker = Speaker(name="今泉 允聡", affiliation="東京大学")
    assert speaker.matches("今泉") is True
    assert speaker.matches("東京大学") is True
    assert speaker.matches("京都") is False


def test_session_ongoing_and_matching():
    speaker = Speaker(name="高橋 昂", affiliation="東京大学")
    talk = Talk(
        title="レプリカ解析による学習の理解",
        speaker=speaker,
        start_time="10:00",
        end_time="10:30",
        abstract="統計力学のレプリカ法を用いた擬似ラベル解析。",
        tags=["Replica", "Statistical Physics"]
    )
    session = Session(
        session_id="os-1",
        day="2026-10-27",
        day_label="Day 2: Oct 27 (Tue)",
        title="企画セッション1: 物理学と機械学習理論",
        track="Main Hall",
        category="os",
        start_time="10:00",
        end_time="12:00",
        start_minutes=600,
        end_minutes=720,
        organizer="今泉 允聡",
        talks=[talk]
    )

    # 進行中判定 (10:00〜12:00)
    assert session.is_ongoing(599) is False
    assert session.is_ongoing(600) is True
    assert session.is_ongoing(700) is True
    assert session.is_ongoing(720) is False

    # キーワードマッチング
    assert session.matches_keyword("物理学") is True
    assert session.matches_keyword("高橋") is True
    assert session.matches_keyword("レプリカ") is True
    assert session.matches_keyword("存在しないキーワード") is False


def test_filter_policy():
    s1 = Session(
        session_id="s1",
        day="2026-10-26",
        day_label="Day 1",
        title="チュートリアル1",
        track="Main Hall",
        category="tutorial",
        start_time="11:00",
        end_time="12:30",
        start_minutes=660,
        end_minutes=750
    )
    s2 = Session(
        session_id="s2",
        day="2026-10-27",
        day_label="Day 2",
        title="招待講演1",
        track="Main Hall",
        category="invited",
        start_time="14:00",
        end_time="15:00",
        start_minutes=840,
        end_minutes=900
    )
    sessions = [s1, s2]

    # 日付フィルタ
    day1_res = FilterPolicy.apply(sessions, day="2026-10-26")
    assert len(day1_res) == 1
    assert day1_res[0].session_id == "s1"

    # カテゴリフィルタ
    invited_res = FilterPolicy.apply(sessions, category="invited")
    assert len(invited_res) == 1
    assert invited_res[0].session_id == "s2"

    # All指定
    all_res = FilterPolicy.apply(sessions, category="all")
    assert len(all_res) == 2
