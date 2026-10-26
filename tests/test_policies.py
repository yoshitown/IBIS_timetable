"""
ドメインポリシー層 (TimePolicy, CategoryVisualPolicy, FilterPolicy) の単体テスト
"""

import pytest

from domain.models import Session, Speaker, Talk, Track
from domain.policies import CategoryVisualPolicy, DayPolicy, FilterPolicy, TimePolicy


def test_time_policy_conversion():
    """時刻文字列と通算分の双方向変換の検証"""
    test_cases = [
        ("00:00", 0),
        ("09:00", 540),
        ("10:30", 630),
        ("15:45", 945),
        ("23:59", 1439),
    ]
    for time_str, minutes in test_cases:
        assert TimePolicy.time_str_to_minutes(time_str) == minutes
        assert TimePolicy.minutes_to_time_str(minutes) == time_str

    # 分が省略された形式
    assert TimePolicy.time_str_to_minutes("15") == 900
    # 前後空白
    assert TimePolicy.time_str_to_minutes(" 10:30 ") == 630


def test_category_visual_policy_all_palette_keys():
    """定義されているすべてのカテゴリに対応する配色・ラベルが取得できること"""
    expected_categories = ["os", "invited", "tutorial", "poster", "panel", "general"]
    required_keys = {"label", "badge_bg", "badge_text", "border_color", "card_bg", "accent_hex"}

    for cat in expected_categories:
        style = CategoryVisualPolicy.get_style(cat)
        assert required_keys.issubset(style.keys())
        # 大文字小文字の吸収検証
        style_upper = CategoryVisualPolicy.get_style(cat.upper())
        assert style == style_upper


def test_category_visual_policy_fallback_for_unknown():
    """未知のカテゴリに対するフォールバック（general）の検証"""
    general_style = CategoryVisualPolicy.get_style("general")
    assert CategoryVisualPolicy.get_style("unknown") == general_style
    assert CategoryVisualPolicy.get_style("") == general_style
    assert CategoryVisualPolicy.get_style("keynote") == general_style


@pytest.fixture
def sample_sessions() -> list[Session]:
    """テスト用セッションデータフィクスチャ"""
    return [
        Session(
            session_id="s1",
            day="Day 1",
            day_label="10月27日(火)",
            title="機械学習チュートリアル",
            track=Track(code="Track A", name="メインホール", sort_order=1),
            category="tutorial",
            start_time="09:00",
            end_time="12:00",
            start_minutes=540,
            end_minutes=720,
            talks=[
                Talk(
                    title="基礎から学ぶ機械学習",
                    speaker=Speaker(name="山田 太郎", affiliation="東大"),
                    start_time="09:00",
                    end_time="12:00",
                    abstract="機械学習の基礎理論を解説します。",
                )
            ],
        ),
        Session(
            session_id="s2",
            day="Day 1",
            day_label="10月27日(火)",
            title="深層学習OS",
            track=Track(code="Track B", name="国際会議室", sort_order=2),
            category="os",
            start_time="13:00",
            end_time="15:00",
            start_minutes=780,
            end_minutes=900,
            talks=[
                Talk(
                    title="最新のDiffusionモデル",
                    speaker=Speaker(name="佐藤 花子", affiliation="京大"),
                    start_time="13:00",
                    end_time="15:00",
                    abstract="画像生成モデルの最新動向。",
                )
            ],
        ),
        Session(
            session_id="s3",
            day="Day 2",
            day_label="10月28日(水)",
            title="招待講演: 最適化理論",
            track=Track(code="Track A", name="メインホール", sort_order=1),
            category="invited",
            start_time="10:00",
            end_time="12:00",
            start_minutes=600,
            end_minutes=720,
            talks=[
                Talk(
                    title="大規模最適化の数理",
                    speaker=Speaker(name="鈴木 一郎", affiliation="理研"),
                    start_time="10:00",
                    end_time="12:00",
                    abstract="数理最適化の最前線。",
                )
            ],
        ),
    ]


def test_filter_policy_day(sample_sessions):
    """日程によるフィルタリングの検証"""
    # 指定なし・allは全件
    assert len(FilterPolicy.apply(sample_sessions, day=None)) == 3
    assert len(FilterPolicy.apply(sample_sessions, day="all")) == 3

    # Day 1
    day1_results = FilterPolicy.apply(sample_sessions, day="Day 1")
    assert len(day1_results) == 2
    assert {s.session_id for s in day1_results} == {"s1", "s2"}

    # 日付ラベル部分一致 ("10月28日")
    day2_results = FilterPolicy.apply(sample_sessions, day="10月28日")
    assert len(day2_results) == 1
    assert day2_results[0].session_id == "s3"


def test_filter_policy_category(sample_sessions):
    """カテゴリによるフィルタリングの検証"""
    assert len(FilterPolicy.apply(sample_sessions, category=None)) == 3
    assert len(FilterPolicy.apply(sample_sessions, category="all")) == 3

    # os (大文字小文字問わず)
    os_results = FilterPolicy.apply(sample_sessions, category="OS")
    assert len(os_results) == 1
    assert os_results[0].session_id == "s2"

    # tutorial
    tut_results = FilterPolicy.apply(sample_sessions, category="tutorial")
    assert len(tut_results) == 1
    assert tut_results[0].session_id == "s1"


def test_filter_policy_keyword(sample_sessions):
    """キーワードによる検索の検証（タイトル、登壇者、要旨）"""
    # 空白文字列は無視されて全件返る
    assert len(FilterPolicy.apply(sample_sessions, keyword="   ")) == 3

    # セッションタイトル一致
    res_title = FilterPolicy.apply(sample_sessions, keyword="深層学習")
    assert len(res_title) == 1
    assert res_title[0].session_id == "s2"

    # トーク登壇者名一致
    res_speaker = FilterPolicy.apply(sample_sessions, keyword="山田 太郎")
    assert len(res_speaker) == 1
    assert res_speaker[0].session_id == "s1"

    # トーク要旨一致
    res_abstract = FilterPolicy.apply(sample_sessions, keyword="画像生成")
    assert len(res_abstract) == 1
    assert res_abstract[0].session_id == "s2"

    # 該当なし
    res_none = FilterPolicy.apply(sample_sessions, keyword="存在しないキーワードXYZ")
    assert len(res_none) == 0


def test_filter_policy_combined(sample_sessions):
    """複数条件の複合フィルタリング検証"""
    # Day 1 かつ category="tutorial" かつ keyword="山田"
    res = FilterPolicy.apply(sample_sessions, day="Day 1", category="tutorial", keyword="山田")
    assert len(res) == 1
    assert res[0].session_id == "s1"

    # Day 2 だが category="tutorial" -> ヒットなし
    res_empty = FilterPolicy.apply(sample_sessions, day="Day 2", category="tutorial")
    assert len(res_empty) == 0


DAYS = [
    {"date": "2026-10-26", "label": "Day 1: Oct 26 (Mon)"},
    {"date": "2026-10-27", "label": "Day 2: Oct 27 (Tue)"},
]


def test_day_policy_default_day():
    assert DayPolicy.default_day(DAYS, "2026-10-26") == "2026-10-26"
    # 会期外は Day 2 にフォールバック
    assert DayPolicy.default_day(DAYS, "2026-12-01") == "2026-10-27"


def test_day_policy_labels():
    assert DayPolicy.badge_label(DAYS, "2026-10-27") == "Day 2"
    assert DayPolicy.badge_label(DAYS, "2099-01-01") == "Live"
    assert DayPolicy.tab_label("Day 2: Oct 27 (Tue)") == "Day 2 Oct 27"
