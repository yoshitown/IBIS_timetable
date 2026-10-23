"""
プレゼンテーション層: セッション詳細＆講演要旨インスペクターコンポーネント
"""

from typing import Optional
import streamlit as st
from domain.models import Session
from domain.policies import CategoryVisualPolicy


def render_session_inspector(session: Optional[Session], selected_time_str: str = "11:20"):
    """画面右側のサイドインスペクターを描画"""
    if not session:
        st.markdown(
            f"""
            <div style="background-color: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 6px; padding: 24px; text-align: center; color: #64748b;">
                <p style="font-weight: 600; margin-bottom: 8px;">セッションが選択されていません</p>
                <p style="font-size: 13px;">左側のタイムライン上のセッションブロックをクリックするか、一覧から選択すると要旨と登壇者詳細が表示されます。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    style = CategoryVisualPolicy.get_style(session.category)
    category_label = style["label"]
    accent_hex = style["accent_hex"]

    # ヘッダー情報
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-top: 4px solid {accent_hex}; border-radius: 6px; padding: 18px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="background-color: #f1f5f9; color: {accent_hex}; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">
                    {category_label}
                </span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #64748b; font-weight: 500;">
                    {session.track}
                </span>
            </div>
            <h3 style="font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 700; color: #0f172a; margin: 0 0 8px 0; line-height: 1.3;">
                {session.title}
            </h3>
            <div style="display: flex; align-items: center; gap: 12px; font-size: 12px; color: #475569; font-family: 'JetBrains Mono', monospace;">
                <span>⏱️ {session.start_time} – {session.end_time} ({session.duration_minutes}分)</span>
                <span>📅 {session.day_label}</span>
            </div>
            {f'<div style="margin-top: 8px; font-size: 12px; color: #64748b;"><strong>Organizer:</strong> {session.organizer}</div>' if session.organizer else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # セッション全体の概要 (もしあれば)
    if session.abstract:
        with st.expander("📌 セッション趣旨・概要", expanded=True):
            st.markdown(
                f"<div style='font-size: 13px; line-height: 1.6; color: #334155;'>{session.abstract}</div>",
                unsafe_allow_html=True,
            )

    # 各講演の要旨リスト
    if session.talks:
        st.markdown(
            f"<div style='font-size: 14px; font-weight: 700; color: #0f172a; margin: 16px 0 8px 0;'>講演・発表一覧 ({len(session.talks)}件)</div>",
            unsafe_allow_html=True,
        )

        for idx, talk in enumerate(session.talks):
            with st.expander(f"【講演{idx+1}】{talk.title}", expanded=(idx == 0)):
                st.markdown(
                    f"""
                    <div style="font-size: 13px; margin-bottom: 6px;">
                        <strong>登壇者:</strong> {talk.speaker.name} <span style="color: #64748b;">({talk.speaker.affiliation})</span>
                    </div>
                    <div style="font-size: 12px; color: #64748b; font-family: 'JetBrains Mono', monospace; margin-bottom: 8px;">
                        時間: {talk.start_time} – {talk.end_time}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if talk.tags:
                    tags_html = " ".join(
                        f"<span style='background:#f1f5f9; color:#475569; padding:2px 6px; border-radius:3px; font-size:10px; font-family:monospace;'>#{t}</span>"
                        for t in talk.tags
                    )
                    st.markdown(f"<div style='margin-bottom: 8px;'>{tags_html}</div>", unsafe_allow_html=True)

                if talk.abstract:
                    st.markdown(
                        f"""
                        <div style="background: #f8fafc; border-left: 3px solid #cbd5e1; padding: 8px 12px; font-size: 12.5px; line-height: 1.6; color: #334155; border-radius: 0 4px 4px 0;">
                            {talk.abstract}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.caption("要旨の記載なし")
    else:
        st.info("このセッションには個別の講演登録はありません（全体進行・オープニングまたはポスターコアタイム等）。")
