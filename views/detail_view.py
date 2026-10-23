"""
プレゼンテーション層: セッション詳細＆全講演要旨フルビュー
各セッションの深い情報（全講演アブストラクト、登壇者、タグ、参考文献、前後ナビゲーション）をレンダリングします。
"""

import streamlit as st

from domain.models import SessionDetailResult
from domain.policies import CategoryVisualPolicy


def render_detail_view(result: SessionDetailResult):
    """セッション詳細画面を描画"""

    # 1. 境界防御: セッションが見つからない場合
    if not result.is_found or result.session is None:
        st.error(result.error_message or "指定されたセッションが見つかりませんでした。")
        if st.button("← タイムライン一覧に戻る", type="primary"):
            st.query_params.clear()
            st.rerun()
        return

    session = result.session
    navigation = result.navigation

    # 2. 上部ナビゲーションバー (戻るボタン & 前後リンク)
    col_back, col_nav = st.columns([1, 2])
    with col_back:
        if st.button("← タイムラインに戻る", key="btn_back_top"):
            st.query_params.clear()
            st.rerun()

    with col_nav:
        sub_c1, sub_c2 = st.columns(2)
        with sub_c1:
            if navigation and navigation.previous_session:
                prev_s = navigation.previous_session
                if st.button(f"◀ {prev_s.title[:12]}...", key="btn_prev_top", help=prev_s.title):
                    st.query_params["session"] = prev_s.session_id
                    st.rerun()
        with sub_c2:
            if navigation and navigation.next_session:
                next_s = navigation.next_session
                if st.button(f"{next_s.title[:12]}... ▶", key="btn_next_top", help=next_s.title):
                    st.query_params["session"] = next_s.session_id
                    st.rerun()

    style = CategoryVisualPolicy.get_style(session.category)
    accent_hex = style["accent_hex"]

    # 3. セッションヘッダーカード
    organizer_html = (
        f"<div style='margin-top: 8px; font-size: 13px; color: #475569;'><strong>オーガナイザー:</strong> {session.organizer}</div>"
        if session.organizer
        else ""
    )

    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-top: 4px solid {accent_hex}; border-radius: 8px; padding: 20px; margin-top: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(15,23,42,0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 6px;">
                <span style="background-color: #f1f5f9; color: {accent_hex}; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; text-transform: uppercase;">
                    {style["label"]}
                </span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #0f172a; font-weight: 600; background: #e2e8f0; padding: 2px 8px; border-radius: 4px;">
                    {session.track.full_label}
                </span>
            </div>
            <h1 style="font-family: 'Inter', sans-serif; font-size: 22px; font-weight: 700; color: #0f172a; margin: 4px 0 10px 0; line-height: 1.35;">
                {session.title}
            </h1>
            <div style="display: flex; align-items: center; gap: 14px; font-size: 13px; color: #475569; font-family: 'JetBrains Mono', monospace; flex-wrap: wrap;">
                <span>⏱️ {session.start_time} – {session.end_time} ({session.duration_minutes}分)</span>
                <span>📅 {session.day_label}</span>
            </div>
            {organizer_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4. セッション趣旨・概要 (セッション全体のもの)
    if session.abstract:
        st.markdown("#### 📌 セッション趣旨・背景")
        st.markdown(
            f"""
            <div style="background: #f8fafc; border-left: 3px solid {accent_hex}; padding: 14px 16px; font-size: 14px; line-height: 1.7; color: #334155; border-radius: 0 6px 6px 0; margin-bottom: 24px;">
                {session.abstract}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # 5. 各講演の要旨フル表示
    if session.talks:
        st.markdown(f"#### 📖 講演・発表一覧 ({len(session.talks)}件)")

        for idx, talk in enumerate(session.talks):
            with st.container():
                st.markdown(
                    f"""
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 18px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(15,23,42,0.04);">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; color: #2563eb;">
                                講演 {idx + 1} • {talk.start_time} - {talk.end_time}
                            </span>
                        </div>
                        <h2 style="font-family: 'Inter', sans-serif; font-size: 17px; font-weight: 700; color: #0f172a; margin: 4px 0 8px 0; line-height: 1.35;">
                            {talk.title}
                        </h2>
                        <div style="font-size: 13.5px; color: #1e293b; margin-bottom: 10px;">
                            <strong>登壇者:</strong> {talk.speaker.name} <span style="color: #64748b;">({talk.speaker.affiliation})</span>
                        </div>
                    """,
                    unsafe_allow_html=True,
                )

                # タグ表示
                if talk.tags:
                    tags_html = " ".join(
                        f"<span style='background:#f1f5f9; color:#475569; padding:2px 8px; border-radius:4px; font-size:11px; font-family:monospace; margin-right:4px;'>#{t}</span>"
                        for t in talk.tags
                    )
                    st.markdown(
                        f"<div style='margin-bottom: 12px;'>{tags_html}</div>",
                        unsafe_allow_html=True,
                    )

                # 要旨全文
                if talk.abstract:
                    st.markdown(
                        f"""
                        <div style="font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 4px;">【要旨 (Abstract)】</div>
                        <div style="background: #faf8ff; border: 1px solid #e2e7ff; padding: 14px; border-radius: 6px; font-size: 13.5px; line-height: 1.75; color: #1e293b; margin-bottom: 10px;">
                            {talk.abstract}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # 参考文献
                if talk.citations:
                    citations_html = "".join(
                        f"<li style='margin-bottom: 4px;'>{c}</li>" for c in talk.citations
                    )
                    st.markdown(
                        f"""
                        <div style="margin-top: 10px; font-size: 12px; color: #64748b;">
                            <strong>参考文献:</strong>
                            <ul style="padding-left: 20px; margin-top: 4px;">
                                {citations_html}
                            </ul>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("このセッションには個別の登録講演はありません。")

    # 6. 下部ナビゲーションバー
    st.divider()
    c_back_bottom, c_nav_bottom = st.columns([1, 2])
    with c_back_bottom:
        if st.button("← タイムラインに戻る", key="btn_back_bottom"):
            st.query_params.clear()
            st.rerun()

    with c_nav_bottom:
        bot_c1, bot_c2 = st.columns(2)
        with bot_c1:
            if navigation and navigation.previous_session:
                prev_s = navigation.previous_session
                if st.button(f"◀ 前: {prev_s.title[:10]}...", key="btn_prev_bot"):
                    st.query_params["session"] = prev_s.session_id
                    st.rerun()
        with bot_c2:
            if navigation and navigation.next_session:
                next_s = navigation.next_session
                if st.button(f"次: {next_s.title[:10]}... ▶", key="btn_next_bot"):
                    st.query_params["session"] = next_s.session_id
                    st.rerun()
