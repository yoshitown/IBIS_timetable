"""
プレゼンテーション層: IBIS2026 モバイル最適化 垂直タイムライン＆アジェンダViewer
ルーティング責務: URLクエリパラメータ (?session=...) に基づき一覧と詳細画面を切り替えます。
"""

import logging
import os
from pathlib import Path

import streamlit as st

from application.schedule_service import ScheduleService
from components.mobile_timeline import render_mobile_timeline
from domain.policies import TimePolicy
from infrastructure.json_repository import JsonScheduleRepository
from views.detail_view import render_detail_view
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

DEBUG_NOW_ENV = "IBIS_DEBUG_NOW"
REFRESH_INTERVAL = "60s"
FALLBACK_DAY = "2026-10-27"  # 会期外アクセス時の既定日: Day 2

logger = logging.getLogger(__name__)


def resolve_now():
    """
    現在時刻 (JST) を返す。環境変数 IBIS_DEBUG_NOW が有効ならデバッグ時刻を優先。
    返り値: (datetime, is_debug)
    """
    raw = os.environ.get(DEBUG_NOW_ENV)
    debug_now = TimePolicy.parse_debug_now(raw)
    if debug_now is not None:
        return debug_now, True
    if raw and raw.strip():
        logger.warning("%s の値を解釈できないため実時刻を使用します: %r", DEBUG_NOW_ENV, raw)
    return TimePolicy.now_jst(), False


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
    # 日程と現在時刻の解決（デバッグ指定があれば優先）
    days = service.get_days()
    day_options = {d["date"]: d["label"] for d in days}
    now_dt, _ = resolve_now()
    today_str = now_dt.strftime("%Y-%m-%d")

    if "selected_day" not in st.session_state:
        # 会期中ならその日、会期外は Day 2 を既定とする
        st.session_state["selected_day"] = today_str if today_str in day_options else FALLBACK_DAY

    header_day = st.session_state.get("mobile_day_radio", st.session_state["selected_day"])
    header_day_label = day_options.get(header_day, "").split(":")[0] or "Live"

    # モバイルヘッダー
    st.markdown(
        f"""
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
                    <span>{header_day_label} Live</span>
                </div>
            </div>
            <div style="font-size: 11px; color: #94a3b8; margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                10/26(月)〜10/29(木) • ソニックシティ（埼玉県さいたま市）
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 会場地図・部屋の行き方専用ページへの画面遷移ボタン
    if st.button("🗺️ 会場地図・各部屋への行き方 (大宮ソニックシティ) ➔", use_container_width=True):
        st.query_params["page"] = "venue"
        st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 日程タブの選択
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

    # 検索（時刻は実時刻 JST。デバッグ時のみ環境変数 IBIS_DEBUG_NOW で上書き）
    with st.expander("🔍 検索", expanded=False):
        search_keyword = st.text_input(
            "🔍 登壇者・タイトル・要旨検索",
            placeholder="例: 今泉, 因果推論, Physical AI, 最適化...",
            label_visibility="collapsed",
        )

    @st.fragment(run_every=REFRESH_INTERVAL)
    def render_timeline(date: str, keyword: str | None) -> None:
        """1分ごとに現在時刻を取り直してタイムライン部のみ再描画"""
        now, is_debug = resolve_now()
        # ライブ表示は「表示中の日 = 現在日付」のときだけ (他の日は None で非表示)
        is_today = date == now.strftime("%Y-%m-%d")
        live_minutes = TimePolicy.datetime_to_minutes(now) if is_today else None

        if is_debug:
            st.caption(f"⚠ デバッグ時刻: {now.strftime('%Y-%m-%d %H:%M')} JST")

        # アプリケーション層から特定日のスケジュール (DaySchedule: ファーストクラスコレクション) を取得
        schedule = service.get_day_schedule(date=date, keyword=keyword)
        ongoing_session = (
            service.get_ongoing_session(date=date, current_minutes=live_minutes)
            if live_minutes is not None
            else None
        )

        # 並行3トラック統合 垂直タイムラインのレンダリング
        render_mobile_timeline(
            schedule=schedule,
            current_minutes=live_minutes,
            ongoing_session=ongoing_session,
        )

    render_timeline(selected_day, search_keyword)
