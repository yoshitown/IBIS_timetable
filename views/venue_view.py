"""
プレゼンテーション層: 会場地図・部屋アクセス専用フルビュー画面
独立したページ (?page=venue) として、大宮ソニックシティの全体構造図、道順、フロア図をフルスクリーンで閲覧できます。
"""

from pathlib import Path

import streamlit as st

from domain.models import RoomGuide, VenueGuide


def render_venue_view(venue: VenueGuide):
    """会場地図・各部屋への行き方専用フルビューを描画"""
    repo_root = Path(__file__).parent.parent

    # 1. 上部ナビゲーションバー
    if st.button("← タイムラインに戻る", key="btn_back_venue_top"):
        st.query_params.clear()
        st.rerun()

    # 2. 会場ヘッダーカード
    st.markdown(
        f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-top: 4px solid #3b82f6; border-radius: 8px; padding: 18px 20px; margin-top: 10px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(15,23,42,0.06);">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="background: #3b82f6; color: white; font-weight: bold; font-family: 'JetBrains Mono', monospace; font-size: 11px; padding: 2px 6px; border-radius: 4px;">
                    VENUE GUIDE
                </span>
                <span style="font-size: 13px; color: #64748b; font-weight: 600;">会場アクセス & フロア案内</span>
            </div>
            <h1 style="font-family: 'Inter', sans-serif; font-size: 22px; font-weight: 700; color: #0f172a; margin: 4px 0 8px 0;">
                {venue.name}
            </h1>
            <div style="font-size: 13px; color: #475569; line-height: 1.5;">
                📍 <strong>所在地:</strong> {venue.address}<br/>
                🚶 <strong>アクセス:</strong> {venue.station_access}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. タブナビゲーション（「🚪 部屋別ガイド」が先頭）
    tab_rooms, tab_route, tab_floor, tab_building = st.tabs(
        [
            "🚪 部屋別ガイド",
            "🚶 大宮駅からの道順",
            "🏢 館内フロア平面図",
            "🏙️ 全体立体図",
        ]
    )

    with tab_rooms:
        st.markdown("#### 🗺️ 全体アクセス・各部屋構造図")
        overview_path = repo_root / venue.map_images.get(
            "overview", "data/maps/overview_diagram.png"
        )
        if overview_path.exists():
            st.image(
                str(overview_path),
                caption="大宮ソニックシティ 全体アクセス・各部屋構造図",
                use_container_width=True,
            )

        st.markdown("#### 🚪 各部屋・トラックへの行き方一覧")
        for room in venue.rooms:
            _render_room_card(room)

    with tab_route:
        st.markdown("#### 🚶 大宮駅西口からの歩行者デッキ道順")
        st.caption("JR・東武 大宮駅西口を出て歩行者デッキを直進（徒歩約3分・2F直結）")
        route_img_path = repo_root / venue.map_images.get("route", "")
        if route_img_path.exists():
            st.image(
                str(route_img_path),
                caption="大宮駅西口〜ソニックシティ道順案内図",
                use_container_width=True,
            )

        st.markdown(
            """
            <div style="font-size: 13px; color: #334155; line-height: 1.6; background: #f8fafc; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0; margin-top: 8px;">
                <strong>【案内図の番号と行き先】</strong><br/>
                • <strong>①〜④</strong>: 大宮駅西口を出て、そごう大宮店を左手に見ながら歩行者デッキを直進<br/>
                • <strong>⑧ ホール棟方面</strong>: <strong>Track A (メインホール 2F)</strong>、<strong>Track B (国際会議室 4F)</strong>、<strong>総合受付</strong><br/>
                • <strong>⑦ ビル棟方面</strong>: <strong>Track C (市民ギャラリー 1F)</strong>、<strong>ポスター会場 (第1展示場 B1F)</strong><br/>
                • <strong>⑥ パレスホテル大宮</strong>: 懇親会会場（デッキ経由で直通）
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab_floor:
        st.markdown("#### 🏢 ホール棟 1F/2F・ビル棟 2F 平面図")
        st.caption("大ホール入口、4階国際会議室行きエレベーター、連絡通路の位置関係")
        floor_img_path = repo_root / venue.map_images.get("floor", "")
        if floor_img_path.exists():
            st.image(
                str(floor_img_path),
                caption="館内移動・フロア平面図",
                use_container_width=True,
            )

        st.markdown(
            """
            <div style="font-size: 13px; color: #334155; line-height: 1.6; background: #f8fafc; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0; margin-top: 8px;">
                • <strong>大ホール入口 (2F)</strong>: 歩行者デッキ直結の北口エントランスすぐ。受付もこのフロアです。<br/>
                • <strong>国際会議室 (4F)</strong>: エントランス奥のエレベーターを利用して4階へ上がってください。<br/>
                • <strong>館内設備</strong>: タリーズコーヒー、ファミリーマート、ATM、多機能トイレがビル2F・1Fにあります。
            </div>
            """,
            unsafe_allow_html=True,
        )

    with tab_building:
        st.markdown("#### 🏙️ ソニックシティ建物全体立体見取り図")
        st.caption("ホール棟・ビル棟（高層）・パレスホテル大宮の全体位置関係")
        building_img_path = repo_root / venue.map_images.get("building", "")
        if building_img_path.exists():
            st.image(
                str(building_img_path),
                caption="ソニックシティ建物全体立体図",
                use_container_width=True,
            )

    # 4. 下部ナビゲーションバー
    st.divider()
    if st.button("← タイムラインに戻る", key="btn_back_venue_bottom"):
        st.query_params.clear()
        st.rerun()


def _render_room_card(room: RoomGuide):
    """部屋ガイド個別カード"""
    badge_bg = "#eff6ff"
    badge_color = "#1e40af"
    border_color = "#93c5fd"
    if "B" in room.track_code:
        badge_bg = "#fffbeb"
        badge_color = "#92400e"
        border_color = "#fde68a"
    elif "C" in room.track_code:
        badge_bg = "#f0fdfa"
        badge_color = "#115e59"
        border_color = "#99f6e4"

    note_html = (
        f'<div style="font-size: 11px; color: #059669; font-weight: 600; margin-top: 6px;">💡 {room.note}</div>'
        if room.note
        else ""
    )

    st.markdown(
        f"""
        <div style="border: 1px solid {border_color}; border-left: 4px solid {badge_color}; border-radius: 8px; padding: 12px 14px; margin-bottom: 10px; background: white; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="background: {badge_bg}; color: {badge_color}; font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 4px;">
                    {room.track_code}
                </span>
                <span style="font-size: 12px; font-weight: 600; color: #1e293b;">
                    {room.building} {room.floor}
                </span>
            </div>
            <div style="font-size: 15px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">
                {room.room_name}
            </div>
            <div style="font-size: 12px; color: #475569; line-height: 1.5;">
                {room.access_instruction}
            </div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
