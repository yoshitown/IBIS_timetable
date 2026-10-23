"""
プレゼンテーション層: モバイル最適化 並行3トラック統合タイムライン (Vertical Timeline Stream) コンポーネント
Streamlit ネイティブ描画により、iframe隔離を解消し即時画面遷移とスクロール問題を根本解決します。
"""

from typing import Optional

import streamlit as st

from domain.models import DaySchedule, Session
from domain.policies import CategoryVisualPolicy, TimePolicy


def render_mobile_timeline(
    schedule: DaySchedule,
    current_minutes: int,
    ongoing_session: Optional[Session] = None,
):
    """
    ドメイン層で整列済みの DaySchedule を受け取り、並行3トラックを垂直タイムラインとして描画
    """
    if not schedule.time_blocks:
        st.info("該当するセッションが見つかりませんでした。検索条件を変更してください。")
        return

    current_time_str = TimePolicy.minutes_to_time_str(current_minutes)

    # タイムライン共通カスタムスタイル
    st.markdown(
        """
        <style>
            .time-marker-container {
                display: flex;
                align-items: center;
                gap: 8px;
                margin: 16px 0 12px 0;
            }
            .time-badge {
                background: #1e1b4b;
                color: #e0e7ff;
                font-family: 'JetBrains Mono', monospace;
                font-weight: 700;
                font-size: 14px;
                padding: 4px 10px;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            .parallel-badge {
                background: #e0e7ff;
                color: #3730a3;
                font-size: 12px;
                font-weight: 700;
                padding: 3px 8px;
                border-radius: 6px;
            }
            .live-indicator {
                background: #ef4444;
                color: white;
                font-family: 'JetBrains Mono', monospace;
                font-size: 12px;
                font-weight: 700;
                padding: 3px 10px;
                border-radius: 20px;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                box-shadow: 0 0 10px rgba(239,68,68,0.5);
            }
            .live-line {
                flex: 1;
                height: 2px;
                background: linear-gradient(to right, #ef4444, rgba(239,68,68,0));
            }
            .timeline-card {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 14px 16px;
                margin-bottom: 8px;
                position: relative;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }
            .timeline-card:hover {
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }
            .card-accent-bar {
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 5px;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
            .speaker-chip {
                background: #f1f5f9;
                color: #334155;
                font-size: 12px;
                padding: 2px 8px;
                border-radius: 4px;
                display: inline-block;
                margin: 2px 4px 2px 0;
            }
            .track-pill {
                background: #f8fafc;
                border: 1px solid #cbd5e1;
                color: #1e293b;
                font-size: 11px;
                font-weight: 600;
                padding: 2px 8px;
                border-radius: 4px;
            }
            /* ボタンのスタイリング調整 */
            div[data-testid="stButton"] > button {
                border-radius: 8px;
                font-weight: 600;
                transition: all 0.15s ease;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 進行中セッションのサマリ通知（存在する場合）
    if ongoing_session:
        st.markdown(
            f"""
            <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px; padding: 10px 14px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #ef4444;"></span>
                    <span style="font-size: 13px; font-weight: 700; color: #991b1b;">現在進行中 ({current_time_str})</span>
                    <span style="font-size: 13px; color: #7f1d1d;">{ongoing_session.title[:24]}...</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    marker_placed = False

    for block in schedule.time_blocks:
        # 現在時刻レーザーインジケータ（該当ブロックの直前に挿入）
        if not marker_placed and current_minutes <= block.end_minutes:
            st.markdown(
                f"""
                <div class="time-marker-container">
                    <div class="live-indicator">
                        <span>●</span> {current_time_str} LIVE
                    </div>
                    <div class="live-line"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            marker_placed = True

        # 時間帯ヘッダー
        parallel_badge = (
            f'<span class="parallel-badge">並行 {block.parallel_count} トラック</span>'
            if block.parallel_count > 1
            else ""
        )
        st.markdown(
            f"""
            <div class="time-marker-container">
                <span class="time-badge">{block.start_time} - {block.end_time}</span>
                {parallel_badge}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ブロック内のセッション一覧 (Track A → Track B → Track C 順)
        for s in block.sessions:
            is_session_ongoing = s.is_ongoing(current_minutes)
            style = CategoryVisualPolicy.get_style(s.category)
            accent_hex = style["accent_hex"]

            # ステータスバッジ
            if is_session_ongoing:
                remaining_mins = max(0, s.end_minutes - current_minutes)
                status_badge = f'<span style="background: #fef2f2; color: #b91c1c; font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 4px; border: 1px solid #f87171;">● LIVE (残{remaining_mins}分)</span>'
            else:
                status_badge = f'<span style="background: #f1f5f9; color: #475569; font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">{style["label"]}</span>'

            # 登壇者チップ
            speakers_html = ""
            if s.talks:
                chips = [
                    f'<span class="speaker-chip">{idx + 1}. {t.speaker.name} ({t.speaker.affiliation})</span>'
                    for idx, t in enumerate(s.talks[:4])
                ]
                speakers_html = f"""
                <div style="margin-top: 6px; margin-bottom: 8px;">
                    <span style="font-size: 11px; color: #64748b; font-weight: 600;">登壇者 ({len(s.talks)}件):</span><br/>
                    {"".join(chips)}
                </div>
                """
            elif s.organizer:
                speakers_html = f"""
                <div style="margin-top: 6px; margin-bottom: 8px; font-size: 12px; color: #475569;">
                    <span style="color: #64748b; font-weight: 600;">企画・進行:</span> {s.organizer}
                </div>
                """

            # カードの外枠コンテナ
            with st.container():
                st.markdown(
                    f"""
                    <div class="timeline-card">
                        <div class="card-accent-bar" style="background-color: {accent_hex};"></div>
                        <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 6px;">
                            <div>{status_badge}</div>
                            <div class="track-pill">{s.track.full_label}</div>
                        </div>
                        <div style="font-size: 16px; font-weight: 700; color: #0f172a; line-height: 1.4; margin-bottom: 4px;">
                            {s.title}
                        </div>
                        {speakers_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # ネイティブ遷移ボタン (即座にURLクエリパラメータを更新し詳細画面へ遷移)
                col_space, col_btn = st.columns([1, 2])
                with col_btn:
                    talk_count_label = f" ({len(s.talks)}件の要旨)" if s.talks else ""
                    if st.button(
                        f"詳細・要旨を見る{talk_count_label} ➔",
                        key=f"btn_detail_{s.session_id}",
                        use_container_width=True,
                    ):
                        st.query_params["session"] = s.session_id
                        st.rerun()

                st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
