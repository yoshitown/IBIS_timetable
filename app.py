"""
プレゼンテーション層: IBIS2026 モバイル最適化 垂直タイムライン＆アジェンダViewer
ルーティング責務: URLクエリパラメータ (?session=...) に基づき一覧と詳細画面を切り替えます。
"""

import os
from pathlib import Path

import streamlit as st

from application.schedule_service import ScheduleService
from infrastructure.clock_factory import ClockFactory
from infrastructure.json_repository import JsonScheduleRepository
from views.detail_view import render_detail_view
from views.timeline_view import render_timeline_view
from views.venue_view import render_venue_view

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
clock = ClockFactory.from_environ(os.environ)

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
# 4. ルーティング (境界防御: session / page パラメータで画面をディスパッチ)
# =========================================================================
current_session_id = st.query_params.get("session")
current_page = st.query_params.get("page")

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

elif current_page == "venue":
    # -------------------------------------------------------------
    # 【会場案内画面】会場地図・各部屋への行き方専用フルビュー
    # -------------------------------------------------------------
    venue_guide = service.get_venue_guide()
    render_venue_view(venue_guide)

else:
    # -------------------------------------------------------------
    # 【一覧画面】並行3トラック統合 垂直タイムラインビュー
    # -------------------------------------------------------------
    render_timeline_view(service, clock)
