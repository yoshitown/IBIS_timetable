"""
ドメインモデルおよびポリシー層の単体テスト
設計原則: 貧血ドメインモデル回避、ファーストクラスコレクション、値オブジェクトの検証
"""

from domain.models import Session, Speaker, Talk, TimeBlock, Track
from domain.policies import TimePolicy


def test_track_value_object():
    t1 = Track(code="Track A", name="メインホール (2F)", sort_order=1)
    t2 = Track(code="Track B", name="国際会議室 (3F)", sort_order=2)
    assert t1.full_label == "Track A: メインホール (2F)"
    assert t1.sort_order < t2.sort_order


def test_time_policy():
    assert TimePolicy.time_str_to_minutes("10:00") == 600
    assert TimePolicy.time_str_to_minutes("14:30") == 870
    assert TimePolicy.minutes_to_time_str(600) == "10:00"
    assert TimePolicy.minutes_to_time_str(870) == "14:30"


def test_session_and_talk_matching():
    speaker = Speaker(name="高橋 昂", affiliation="東京大学")
    talk = Talk(
        title="レプリカ解析による学習の理解",
        speaker=speaker,
        start_time="10:00",
        end_time="10:30",
        abstract="統計力学のレプリカ法を用いた擬似ラベル解析。",
        tags=["Replica", "Statistical Physics"],
    )
    track = Track(code="Track A", name="メインホール (2F)", sort_order=1)
    session = Session(
        session_id="os-1",
        day="2026-10-27",
        day_label="Day 2: 10/27 (火)",
        title="企画セッション1: 物理学と機械学習理論",
        track=track,
        category="os",
        start_time="10:00",
        end_time="12:00",
        start_minutes=600,
        end_minutes=720,
        organizer="今泉 允聡",
        talks=[talk],
    )

    # 外部からの時刻値注入による進行中判定
    assert session.is_ongoing(599) is False
    assert session.is_ongoing(600) is True
    assert session.is_ongoing(719) is True
    assert session.is_ongoing(720) is False

    # キーワード判定
    assert session.matches_keyword("物理学") is True
    assert session.matches_keyword("高橋") is True
    assert session.matches_keyword("メインホール") is True
    assert session.matches_keyword("存在しない単語") is False


def test_time_block_first_class_collection():
    track_a = Track(code="Track A", name="メインホール", sort_order=1)
    track_b = Track(code="Track B", name="国際会議室", sort_order=2)

    s1 = Session(
        session_id="s1",
        day="2026-10-27",
        day_label="Day 2",
        title="OS1",
        track=track_a,
        category="os",
        start_time="10:00",
        end_time="12:00",
        start_minutes=600,
        end_minutes=720,
    )
    s2 = Session(
        session_id="s2",
        day="2026-10-27",
        day_label="Day 2",
        title="Tutorial B",
        track=track_b,
        category="tutorial",
        start_time="10:00",
        end_time="12:00",
        start_minutes=600,
        end_minutes=720,
    )

    block = TimeBlock(
        start_time="10:00",
        end_time="12:00",
        start_minutes=600,
        end_minutes=720,
        sessions=[s1, s2],
    )

    assert block.parallel_count == 2
    assert block.is_ongoing(650) is True
    assert block.is_ongoing(750) is False
    # ソート順序の維持
    assert block.sessions[0].track.sort_order < block.sessions[1].track.sort_order
