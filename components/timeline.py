"""
プレゼンテーション層: Stitchデザインシステム準拠のGanttタイムライン描画コンポーネント
"""

from typing import List, Optional
import streamlit as st
from domain.models import Session
from domain.policies import CategoryVisualPolicy, TimePolicy


def render_timeline_canvas(
    sessions: List[Session],
    current_minutes: int,
    show_marker: bool = True,
    selected_session_id: Optional[str] = None,
) -> Optional[str]:
    """
    タイムライン（Ganttチャート）を描画する。
    クリックされたセッションIDを返すか、ラジオ/ボタン等で選択可能にする。
    """
    if not sessions:
        st.info("該当するセッションが見つかりませんでした。条件を変更してください。")
        return None

    # トラックごとにグループ化
    tracks = []
    for s in sessions:
        if s.track not in tracks:
            tracks.append(s.track)

    # タイムラインの基準範囲: 09:00 (540分) 〜 19:00 (1140分) = 600分間
    BASE_START_MIN = 540
    BASE_TOTAL_MIN = 600

    # 現在時刻インジケーターの位置計算 (パーセンテージ)
    marker_percent = max(0.0, min(100.0, ((current_minutes - BASE_START_MIN) / BASE_TOTAL_MIN) * 100))

    # 時間軸ヘッダー (09:00 - 19:00)
    time_headers = [f"{h:02d}:00" for h in range(9, 19)]
    cols_html = "".join(f"<div style='flex: 1; text-align: left; padding-left: 2px;'>{t}</div>" for t in time_headers)

    # 赤線インジケーターHTML
    marker_html = ""
    if show_marker and 0 <= marker_percent <= 100:
        time_str = TimePolicy.minutes_to_time_str(current_minutes)
        marker_html = f"""
        <div style="position: absolute; top: 0; bottom: 0; left: calc(180px + (100% - 180px) * {marker_percent / 100}); width: 2px; background: #e11d48; box-shadow: 0 0 8px rgba(225, 29, 72, 0.7); z-index: 30; pointer-events: none;">
            <div style="position: absolute; top: -8px; left: -24px; background: #e11d48; color: white; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: bold; padding: 1px 6px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                {time_str}
            </div>
        </div>
        """

    # 各トラックの行HTML
    tracks_html = ""
    for track in tracks:
        track_sessions = [s for s in sessions if s.track == track]
        cards_html = ""

        for s in track_sessions:
            start_offset = max(0, s.start_minutes - BASE_START_MIN)
            duration = s.duration_minutes
            left_pct = (start_offset / BASE_TOTAL_MIN) * 100
            width_pct = max(3.0, (duration / BASE_TOTAL_MIN) * 100)

            style = CategoryVisualPolicy.get_style(s.category)
            accent = style["accent_hex"]
            is_active = (s.session_id == selected_session_id)
            is_ongoing = s.is_ongoing(current_minutes)

            bg_color = "#ffffff"
            border_style = f"border: 1px solid #e2e8f0; border-left: 4px solid {accent};"
            if is_active:
                bg_color = "#f0f4ff"
                border_style = f"border: 2px solid {accent}; border-left: 5px solid {accent};"

            live_badge = ""
            if is_ongoing:
                live_badge = "<span style='background:#ef4444; color:white; font-size:9px; font-weight:bold; padding:1px 4px; border-radius:2px; margin-right:4px;'>LIVE</span>"

            cards_html += f"""
            <div style="position: absolute; left: {left_pct}%; width: {width_pct}%; top: 6px; bottom: 6px; background: {bg_color}; {border_style} border-radius: 4px; padding: 6px 8px; overflow: hidden; box-shadow: 0 1px 2px rgba(0,0,0,0.05); font-family: 'Inter', sans-serif;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; color: {accent}; display: flex; align-items: center; white-space: nowrap;">
                    {live_badge} {s.start_time}-{s.end_time}
                </div>
                <div style="font-size: 11.5px; font-weight: 600; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px;" title="{s.title}">
                    {s.title}
                </div>
                <div style="font-size: 10.5px; color: #64748b; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{s.primary_speaker_names}">
                    {s.primary_speaker_names}
                </div>
            </div>
            """

        tracks_html += f"""
        <div style="display: flex; border-bottom: 1px solid #e2e8f0; min-height: 72px;">
            <div style="width: 180px; flex-shrink: 0; background: #f8fafc; border-right: 1px solid #e2e8f0; padding: 10px 12px; font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; color: #334155; display: flex; align-items: center;">
                {track}
            </div>
            <div style="flex: 1; position: relative;">
                {cards_html}
            </div>
        </div>
        """

    # 全体コンテナのレンダリング
    full_timeline_html = f"""
    <div style="width: 100%; border: 1px solid #e2e8f0; border-radius: 6px; background: white; overflow-x: auto; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 16px;">
        <div style="min-width: 950px; position: relative;">
            <!-- 時間軸ルーラー -->
            <div style="display: flex; background: #f1f5f9; border-bottom: 2px solid #cbd5e1; height: 32px; align-items: center; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #475569; font-weight: 600;">
                <div style="width: 180px; flex-shrink: 0; padding-left: 12px; border-right: 1px solid #cbd5e1;">VENUE / TRACK</div>
                <div style="flex: 1; display: flex;">
                    {cols_html}
                </div>
            </div>
            <!-- トラック・レーン群 -->
            <div style="position: relative;">
                {tracks_html}
                {marker_html}
            </div>
        </div>
    </div>
    """

    st.markdown(full_timeline_html, unsafe_allow_html=True)

    # ユーザーがインタラクティブにセッションを選択できるようにする選択ウィジェット
    session_options = {s.session_id: f"{s.start_time} - {s.end_time} | {s.title} ({s.track})" for s in sessions}
    current_idx = 0
    if selected_session_id in session_options:
        current_idx = list(session_options.keys()).index(selected_session_id)

    selected_key = st.selectbox(
        "🔍 詳細・要旨を表示するセッションを選択:",
        options=list(session_options.keys()),
        index=current_idx,
        format_func=lambda k: session_options[k],
        key="timeline_session_selector"
    )

    return selected_key
