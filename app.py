"""
プレゼンテーション層: IBIS2026 タイムライン＆アジェンダViewer メインエントリーポイント
三層＋ドメインモデルの原則に基づき、UI描画とユーザーインタラクションに専念します。
"""

from pathlib import Path
import streamlit as st
from application.schedule_service import ScheduleService
from components.detail_drawer import render_session_inspector
from components.timeline import render_timeline_canvas
from domain.policies import TimePolicy
from infrastructure.json_repository import JsonScheduleRepository

# 1. ページ設定 (Stitchデザイン準拠)
st.set_page_config(
    page_title="IBIS2026 タイムライン＆アジェンダViewer",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. 依存性の注入 (DI: Infrastructure -> Application)
DATA_PATH = Path(__file__).parent / "data" / "ibis2026_program.json"
repository = JsonScheduleRepository(DATA_PATH)
service = ScheduleService(repository)

# 3. カスタムスタイル (Inter + JetBrains Mono、微細ボーダー)
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #0f172a;
        }
        .main .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 1600px !important;
        }
        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }
        footer {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# 4. マストヘッド (固定Deep Navyヘッダー)
st.markdown(
    """
    <div style="background-color: #0f172a; color: #f8fafc; border-radius: 8px; padding: 16px 20px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(15,23,42,0.15);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="background: #3525cd; color: white; font-weight: bold; font-family: 'JetBrains Mono', monospace; font-size: 16px; padding: 4px 10px; border-radius: 4px;">
                    IBIS2026
                </div>
                <div>
                    <div style="font-size: 18px; font-weight: 700; line-height: 1.2;">タイムライン＆アジェンダViewer</div>
                    <div style="font-size: 12px; color: #94a3b8; font-family: 'JetBrains Mono', monospace;">
                        2026年10月26日(月)〜10月29日(木) • ソニックシティ（埼玉県さいたま市）
                    </div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 16px; font-family: 'JetBrains Mono', monospace; font-size: 12px;">
                <div style="background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 4px; display: flex; align-items: center; gap: 6px;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981;"></span>
                    <span>JST (UTC+9)</span>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 5. カンファレンス日程タブの取得と選択
days = service.get_days()
day_options = {d["date"]: d["label"] for d in days}

# セッション状態の初期化
if "selected_day" not in st.session_state:
    st.session_state["selected_day"] = "2026-10-27"  # デフォルト: Day 2

# 日付選択タブバー
col_day, col_search = st.columns([3, 2])
with col_day:
    selected_day = st.radio(
        "📅 日程選択",
        options=list(day_options.keys()),
        format_func=lambda x: day_options[x],
        horizontal=True,
        index=list(day_options.keys()).index(st.session_state["selected_day"])
        if st.session_state["selected_day"] in day_options
        else 1,
        key="day_radio",
        label_visibility="collapsed",
    )
    st.session_state["selected_day"] = selected_day

with col_search:
    search_keyword = st.text_input(
        "🔍 登壇者・タイトル・要旨キーワード検索",
        placeholder="例: 今泉, 栗田, 最適化, Physical AI...",
        label_visibility="collapsed",
    )

# 6. コントロールストリップ (カテゴリフィルター & 赤線インジケータースライダー)
with st.container():
    c_cat, c_toggle, c_slider = st.columns([2, 1, 2])

    with c_cat:
        category_options = service.get_category_filters()
        cat_keys = [c["key"] for c in category_options]
        selected_cat = st.selectbox(
            "セッション種別フィルター",
            options=cat_keys,
            format_func=lambda k: next(
                c["label"] for c in category_options if c["key"] == k
            ),
            index=0,
            label_visibility="collapsed",
        )

    with c_toggle:
        show_red_marker = st.checkbox("赤線時刻バー表示", value=True)

    with c_slider:
        simulated_minutes = st.slider(
            "⏱️ 現在時刻シミュレーション (JST)",
            min_value=540,  # 09:00
            max_value=1140,  # 19:00
            value=680,  # 11:20
            step=5,
            format="%d分",
            help="学会当日の現在時刻に対応した赤線インジケーターをシミュレートします",
            label_visibility="collapsed",
        )
        current_time_str = TimePolicy.minutes_to_time_str(simulated_minutes)
        st.caption(f"現在の指定時刻: **{current_time_str} JST**")

# 7. アプリケーション層から絞り込み済みセッションを取得
filtered_sessions = service.get_filtered_schedule(
    day=selected_day,
    category=selected_cat,
    keyword=search_keyword,
)

# 進行中セッションの取得 (あればデフォルト選択候補にする)
ongoing_session = service.get_ongoing_session(
    day=selected_day, minutes=simulated_minutes
)

# 8. メインビューポート: タイムライン (左側 65%) + サイドインスペクター (右側 35%)
col_timeline, col_inspector = st.columns([7, 5])

with col_timeline:
    st.markdown("#### 📊 タイムライン (Gantt Schedule)")
    if ongoing_session:
        st.markdown(
            f"""
            <div style="display: inline-flex; align-items: center; gap: 6px; background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-bottom: 8px;">
                <span style="width: 6px; height: 6px; border-radius: 50%; background: #dc2626;"></span>
                <span>進行中: {ongoing_session.title} ({ongoing_session.start_time} - {ongoing_session.end_time})</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # タイムラインのレンダリング
    selected_id_from_timeline = render_timeline_canvas(
        sessions=filtered_sessions,
        current_minutes=simulated_minutes,
        show_marker=show_red_marker,
        selected_session_id=ongoing_session.session_id if ongoing_session else None,
    )

with col_inspector:
    st.markdown("#### 📖 セッション詳細 & 要旨インスペクター")
    # 選択セッションの決定
    target_session = None
    if selected_id_from_timeline:
        target_session = service.get_session_by_id(selected_id_from_timeline)
    elif ongoing_session:
        target_session = ongoing_session
    elif filtered_sessions:
        target_session = filtered_sessions[0]

    render_session_inspector(
        session=target_session,
        selected_time_str=current_time_str,
    )
