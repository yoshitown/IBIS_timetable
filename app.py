"""
プレゼンテーション層: IBIS2026 モバイル最適化 垂直タイムライン＆アジェンダViewer
三層＋ドメインモデルの原則を適用し、スマートフォンの片手縦スクロールに特化したUIを提供します。
"""

from pathlib import Path

import streamlit as st

from application.schedule_service import ScheduleService
from components.mobile_timeline import render_mobile_timeline
from domain.policies import TimePolicy
from infrastructure.json_repository import JsonScheduleRepository

# 1. ページ設定 (モバイル優先・レスポンシブ)
st.set_page_config(
    page_title="IBIS2026 モバイルタイムライン",
    page_icon="📱",
    layout="centered",  # スマホ画面・片手閲覧に最適な中央集約レイアウト
    initial_sidebar_state="collapsed",
)

# 2. 依存性の注入 (DI: Infrastructure -> Application)
DATA_PATH = Path(__file__).parent / "data" / "ibis2026_program.json"
repository = JsonScheduleRepository(DATA_PATH)
service = ScheduleService(repository)

# 3. モバイル特化スタイル設定
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #0f172a;
        }
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            max-width: 720px !important;
        }
        header[data-testid="stHeader"] {
            display: none !important;
        }
        footer {
            display: none !important;
        }
        iframe {
            border: none !important;
            width: 100% !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# 4. モバイルヘッダー
st.markdown(
    """
    <div style="background-color: #0f172a; color: #f8fafc; border-radius: 12px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(15,23,42,0.12);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; items-center; gap: 8px;">
                <span style="background: #3525cd; color: white; font-weight: bold; font-family: 'JetBrains Mono', monospace; font-size: 14px; padding: 3px 8px; border-radius: 4px;">
                    IBIS2026
                </span>
                <span style="font-size: 16px; font-weight: 700; line-height: 1.4;">タイムライン</span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px; font-family: 'JetBrains Mono', monospace; font-size: 11px; background: rgba(255,255,255,0.1); padding: 3px 8px; border-radius: 12px;">
                <span style="width: 7px; height: 7px; border-radius: 50%; background: #10b981;"></span>
                <span>Day 2 Live</span>
            </div>
        </div>
        <div style="font-size: 11px; color: #94a3b8; margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
            10/26(月)〜10/29(木) • ソニックシティ（埼玉県さいたま市）
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 5. カンファレンス日程タブの選択
days = service.get_days()
day_options = {d["date"]: d["label"] for d in days}

if "selected_day" not in st.session_state:
    st.session_state["selected_day"] = "2026-10-27"  # デフォルト: Day 2

# 水平日程セレクター (スマホでも押しやすいタブ)
selected_day = st.radio(
    "日程選択",
    options=list(day_options.keys()),
    format_func=lambda x: (
        day_options[x].split(":")[0] + " " + day_options[x].split(":")[1].split("(")[0].strip()
    ),
    horizontal=True,
    index=list(day_options.keys()).index(st.session_state["selected_day"])
    if st.session_state["selected_day"] in day_options
    else 1,
    key="mobile_day_radio",
    label_visibility="collapsed",
)
st.session_state["selected_day"] = selected_day

# 6. コントロールバー (トラック/カテゴリフィルター & 検索 & 時刻シミュレーション)
search_keyword = None
selected_cat = "all"
simulated_minutes = 680  # 11:20
current_time_str = "11:20"

with st.expander("⚙️ フィルター & 時刻シミュレーション", expanded=False):
    search_keyword = st.text_input(
        "🔍 登壇者・タイトル・要旨検索",
        placeholder="例: 今泉, 最適化, Physical AI...",
        label_visibility="collapsed",
    )

    c_cat, c_time = st.columns([1, 1])
    with c_cat:
        category_options = service.get_category_filters()
        cat_keys = [c["key"] for c in category_options]
        selected_cat = st.selectbox(
            "種別フィルター",
            options=cat_keys,
            format_func=lambda k: next(c["label"] for c in category_options if c["key"] == k),
            index=0,
            label_visibility="collapsed",
        )

    with c_time:
        simulated_minutes = st.slider(
            "現在時刻 (JST)",
            min_value=540,  # 09:00
            max_value=1140,  # 19:00
            value=680,  # 11:20
            step=5,
            format="%d分",
            label_visibility="collapsed",
        )
        current_time_str = TimePolicy.minutes_to_time_str(simulated_minutes)
        st.caption(f"シミュレーション時刻: **{current_time_str} JST**")


# 7. アプリケーション層から絞り込み済みセッションを取得
filtered_sessions = service.get_filtered_schedule(
    day=selected_day,
    category=selected_cat,
    keyword=search_keyword,
)

ongoing_session = service.get_ongoing_session(
    day=selected_day,
    minutes=simulated_minutes,
)

# 8. モバイル最適化 垂直タイムラインのレンダリング
render_mobile_timeline(
    sessions=filtered_sessions,
    current_minutes=simulated_minutes,
    selected_day_label=day_options.get(selected_day, "Day 2"),
    ongoing_session=ongoing_session,
)
