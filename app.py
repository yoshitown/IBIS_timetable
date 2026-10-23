"""
プレゼンテーション層: IBIS2026 モバイル最適化 垂直タイムライン＆アジェンダViewer
ルーティング責務: URLクエリパラメータ (?session=...) に基づき一覧と詳細画面を切り替えます。
"""

from pathlib import Path

import streamlit as st

from application.schedule_service import ScheduleService
from components.mobile_timeline import render_mobile_timeline
from components.venue_map_view import render_venue_map_expander
from domain.policies import TimePolicy
from infrastructure.json_repository import JsonScheduleRepository
from views.detail_view import render_detail_view

# 1. ページ設定 (モバイル優先・レスポンシブ)
st.set_page_config(
    page_title="IBIS2026 モバイルタイムライン",
    page_icon="📱",
    layout="centered",
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

# =========================================================================
# 4. ルーティング (境界防御: session パラメータの有無で画面をディスパッチ)
# =========================================================================
current_session_id = st.query_params.get("session")

if current_session_id:
    # -------------------------------------------------------------
    # 【詳細画面】セッション詳細・要旨フルビュー
    # -------------------------------------------------------------
    detail_result = service.get_session_detail(current_session_id)
    room_guide = (
        service.get_room_guide_for_track(detail_result.session.track.code)
        if detail_result.session
        else None
    )
    render_detail_view(detail_result, room_guide=room_guide)

else:
    # -------------------------------------------------------------
    # 【一覧画面】並行3トラック統合 垂直タイムラインビュー
    # -------------------------------------------------------------
    # モバイルヘッダー
    st.markdown(
        """
        <div style="background-color: #0f172a; color: #f8fafc; border-radius: 12px; padding: 14px 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(15,23,42,0.12);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 8px;">
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

    # 会場地図・部屋の行き方アコーディオン
    render_venue_map_expander(service.get_venue_guide())

    # 日程タブの取得と選択
    days = service.get_days()
    day_options = {d["date"]: d["label"] for d in days}

    if "selected_day" not in st.session_state:
        st.session_state["selected_day"] = "2026-10-27"  # デフォルト: Day 2

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

    # 検索・時刻シミュレーション設定
    search_keyword = None
    simulated_minutes = 680  # 11:20
    current_time_str = "11:20"

    with st.expander("⚙️ 検索 & 時刻シミュレーション", expanded=False):
        search_keyword = st.text_input(
            "🔍 登壇者・タイトル・要旨検索",
            placeholder="例: 今泉, 因果推論, Physical AI, 最適化...",
            label_visibility="collapsed",
        )

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

    # アプリケーション層から特定日のスケジュール (DaySchedule: ファーストクラスコレクション) を取得
    schedule = service.get_day_schedule(
        date=selected_day,
        keyword=search_keyword,
    )

    ongoing_session = service.get_ongoing_session(
        date=selected_day,
        current_minutes=simulated_minutes,
    )

    # 並行3トラック統合 垂直タイムラインのレンダリング
    render_mobile_timeline(
        schedule=schedule,
        current_minutes=simulated_minutes,
        ongoing_session=ongoing_session,
    )
