"""
プレゼンテーション層: Stitchデザインシステム準拠のGanttタイムライン描画コンポーネント
"""

from typing import List, Optional
import streamlit as st
import streamlit.components.v1 as components
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
    st.components.v1.html を使用することで、Markdownパーサーによるコードブロック誤判定を防ぎ、
    StitchデザインのCSSを完全に適用してレンダリングする。
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
    cols_html = "".join(f'<div class="time-col">{t}</div>' for t in time_headers)

    # 赤線インジケーターHTML
    marker_html = ""
    if show_marker and 0 <= marker_percent <= 100:
        time_str = TimePolicy.minutes_to_time_str(current_minutes)
        marker_html = f"""
        <div class="time-marker" style="left: calc(180px + (100% - 180px) * {marker_percent / 100});">
            <div class="time-marker-badge">{time_str}</div>
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
            width_pct = max(3.5, (duration / BASE_TOTAL_MIN) * 100)

            style = CategoryVisualPolicy.get_style(s.category)
            accent = style["accent_hex"]
            is_active = (s.session_id == selected_session_id)
            is_ongoing = s.is_ongoing(current_minutes)

            card_classes = ["session-card"]
            if is_active:
                card_classes.append("active")
            if is_ongoing:
                card_classes.append("ongoing")

            live_badge = '<span class="badge-live">LIVE</span>' if is_ongoing else ""

            cards_html += f"""
            <div class="{' '.join(card_classes)}" style="left: {left_pct}%; width: {width_pct}%; border-left-color: {accent};">
                <div class="card-time" style="color: {accent};">
                    {live_badge}<span>{s.start_time} - {s.end_time}</span>
                </div>
                <div class="card-title" title="{s.title}">{s.title}</div>
                <div class="card-speakers" title="{s.primary_speaker_names}">{s.primary_speaker_names}</div>
            </div>
            """

        tracks_html += f"""
        <div class="track-row">
            <div class="track-label">{track}</div>
            <div class="track-timeline">
                {cards_html}
            </div>
        </div>
        """

    # 独立したHTMLドキュメントとしてレンダリング (iframe)
    calculated_height = 50 + len(tracks) * 80 + 30
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">
        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: transparent;
                overflow-x: auto;
                padding-bottom: 8px;
            }}
            .timeline-container {{
                min-width: 900px;
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                position: relative;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
            }}
            .time-ruler {{
                display: flex;
                background: #f1f5f9;
                border-bottom: 2px solid #cbd5e1;
                height: 36px;
                align-items: center;
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                font-weight: 600;
                color: #475569;
            }}
            .ruler-label {{
                width: 180px;
                flex-shrink: 0;
                padding-left: 14px;
                border-right: 1px solid #cbd5e1;
                letter-spacing: 0.03em;
            }}
            .ruler-cols {{
                flex: 1;
                display: flex;
            }}
            .time-col {{
                flex: 1;
                text-align: left;
                padding-left: 4px;
                border-left: 1px dashed rgba(203, 213, 225, 0.6);
            }}
            .track-row {{
                display: flex;
                border-bottom: 1px solid #e2e8f0;
                min-height: 76px;
                background: #ffffff;
            }}
            .track-row:last-child {{
                border-bottom: none;
            }}
            .track-label {{
                width: 180px;
                flex-shrink: 0;
                background: #f8fafc;
                border-right: 1px solid #e2e8f0;
                padding: 12px 14px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 12px;
                font-weight: 600;
                color: #334155;
                display: flex;
                align-items: center;
            }}
            .track-timeline {{
                flex: 1;
                position: relative;
                background-image: repeating-linear-gradient(
                    to right,
                    transparent,
                    transparent calc(10% - 1px),
                    rgba(226, 232, 240, 0.5) calc(10% - 1px),
                    rgba(226, 232, 240, 0.5) 10%
                );
            }}
            .session-card {{
                position: absolute;
                top: 7px;
                bottom: 7px;
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-left-width: 4px;
                border-radius: 5px;
                padding: 6px 10px;
                overflow: hidden;
                box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
                display: flex;
                flex-col: column;
                justify-content: space-between;
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }}
            .session-card.active {{
                background: #f8faff;
                border-top-color: #3b82f6;
                border-right-color: #3b82f6;
                border-bottom-color: #3b82f6;
                box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2), 0 2px 4px rgba(15, 23, 42, 0.1);
            }}
            .session-card.ongoing {{
                box-shadow: 0 0 0 1.5px rgba(239, 68, 68, 0.3);
            }}
            .card-time {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 10px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 4px;
                white-space: nowrap;
            }}
            .badge-live {{
                background: #ef4444;
                color: #ffffff;
                font-size: 9px;
                font-weight: 700;
                padding: 1px 4px;
                border-radius: 2px;
                line-height: 1;
            }}
            .card-title {{
                font-size: 11.5px;
                font-weight: 600;
                color: #0f172a;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                margin-top: 2px;
            }}
            .card-speakers {{
                font-size: 10px;
                color: #64748b;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            .time-marker {{
                position: absolute;
                top: 0;
                bottom: 0;
                width: 2px;
                background: #e11d48;
                box-shadow: 0 0 8px rgba(225, 29, 72, 0.7);
                z-index: 40;
                pointer-events: none;
            }}
            .time-marker-badge {{
                position: absolute;
                top: 2px;
                left: -22px;
                background: #e11d48;
                color: #ffffff;
                font-family: 'JetBrains Mono', monospace;
                font-size: 10px;
                font-weight: 700;
                padding: 2px 6px;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }}
        </style>
    </head>
    <body>
        <div class="timeline-container">
            <div class="time-ruler">
                <div class="ruler-label">VENUE / TRACK</div>
                <div class="ruler-cols">{cols_html}</div>
            </div>
            <div style="position: relative;">
                {tracks_html}
                {marker_html}
            </div>
        </div>
    </body>
    </html>
    """

    # components.html で安全に描画
    components.html(full_html, height=calculated_height, scrolling=True)

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
