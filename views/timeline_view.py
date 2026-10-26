"""
プレゼンテーション層: 並行3トラック統合 垂直タイムライン一覧画面
日程選択・検索・ライブ表示（実時刻 or デバッグ時刻）を組み合わせ、1分ごとに自動更新します。
"""

import streamlit as st

from application.schedule_service import ScheduleService
from components.mobile_timeline import render_mobile_timeline
from domain.clock import Clock
from domain.live import live_context_for_day
from domain.policies import DayPolicy

REFRESH_INTERVAL = "60s"
DAY_RADIO_KEY = "mobile_day_radio"


def render_timeline_view(service: ScheduleService, clock: Clock) -> None:
    """一覧画面全体を描画"""
    days = service.get_days()
    day_dates = [d["date"] for d in days]
    day_labels = {d["date"]: d["label"] for d in days}

    if "selected_day" not in st.session_state:
        st.session_state["selected_day"] = DayPolicy.default_day(
            days, clock.now().strftime("%Y-%m-%d")
        )

    header_day = st.session_state.get(DAY_RADIO_KEY, st.session_state["selected_day"])
    _render_header(DayPolicy.badge_label(days, header_day))
    _render_venue_button()

    selected_day = _render_day_selector(day_dates, day_labels)
    keyword = _render_search()

    _render_live_timeline(service, clock, selected_day, keyword)


def _render_header(day_badge: str) -> None:
    """モバイルヘッダー"""
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
                    <span>{day_badge} Live</span>
                </div>
            </div>
            <div style="font-size: 11px; color: #94a3b8; margin-top: 4px; font-family: 'JetBrains Mono', monospace;">
                10/26(月)〜10/29(木) • ソニックシティ（埼玉県さいたま市）
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_venue_button() -> None:
    """会場地図・部屋の行き方専用ページへの画面遷移ボタン"""
    if st.button("🗺️ 会場地図・各部屋への行き方 (大宮ソニックシティ) ➔", use_container_width=True):
        st.query_params["page"] = "venue"
        st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)


def _render_day_selector(day_dates: list[str], day_labels: dict[str, str]) -> str:
    """日程タブの選択"""
    selected = st.session_state["selected_day"]
    selected_day = st.radio(
        "日程選択",
        options=day_dates,
        format_func=lambda date: DayPolicy.tab_label(day_labels[date]),
        horizontal=True,
        index=day_dates.index(selected) if selected in day_dates else 1,
        key=DAY_RADIO_KEY,
        label_visibility="collapsed",
    )
    st.session_state["selected_day"] = selected_day
    return selected_day


def _render_search() -> str:
    """検索ボックス"""
    with st.expander("🔍 検索", expanded=False):
        return st.text_input(
            "🔍 登壇者・タイトル・要旨検索",
            placeholder="例: 今泉, 因果推論, Physical AI, 最適化...",
            label_visibility="collapsed",
        )


@st.fragment(run_every=REFRESH_INTERVAL)
def _render_live_timeline(
    service: ScheduleService, clock: Clock, date: str, keyword: str | None
) -> None:
    """1分ごとに現在時刻を取り直してタイムライン部のみ再描画"""
    now = clock.now()
    if clock.is_simulated:
        st.caption(f"⚠ デバッグ時刻: {now.strftime('%Y-%m-%d %H:%M')} JST")

    schedule = service.get_day_schedule(date=date, keyword=keyword)
    render_mobile_timeline(schedule=schedule, live=live_context_for_day(now, date))
