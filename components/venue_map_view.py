"""
プレゼンテーション層: 会場地図・フロア平面図・部屋アクセスガイドコンポーネント
大宮ソニックシティのアクセス図・館内平面図・部屋別案内をレスポンシブに描画します。
"""

from pathlib import Path

import streamlit as st

from domain.models import RoomGuide, VenueGuide


def render_venue_map_expander(venue: VenueGuide):
    """
    タイムライン画面上部に折りたたみ可能な会場地図・アクセスガイドを描画
    """
    repo_root = Path(__file__).parent.parent

    with st.expander("🗺️ 会場地図・各部屋への行き方 (大宮ソニックシティ)", expanded=False):
        st.markdown(
            f"""
            <div style="font-size: 13px; color: #475569; margin-bottom: 8px;">
                <strong>📍 会場:</strong> {venue.name}（{venue.address}）<br/>
                <strong>🚶 アクセス:</strong> {venue.station_access}
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_route, tab_floor, tab_rooms, tab_building = st.tabs(
            [
                "🚶 大宮駅からの道順",
                "🏢 館内フロア平面図",
                "🚪 部屋別ガイド",
                "🏙️ 全体立体図",
            ]
        )

        with tab_route:
            st.caption("JR大宮駅西口を出て歩行者デッキを直進（徒歩約3分）")
            route_img_path = repo_root / venue.map_images.get("route", "")
            if route_img_path.exists():
                st.image(str(route_img_path), use_container_width=True)

            st.markdown(
                """
                <div style="font-size: 12px; color: #334155; line-height: 1.6; background: #f8fafc; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0;">
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
            st.caption("ホール棟 1F/2F・ビル棟 2F の連絡通路とエレベーター位置")
            floor_img_path = repo_root / venue.map_images.get("floor", "")
            if floor_img_path.exists():
                st.image(str(floor_img_path), use_container_width=True)

            st.markdown(
                """
                <div style="font-size: 12px; color: #334155; line-height: 1.6; background: #f8fafc; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0;">
                    • <strong>大ホール入口 (2F)</strong>: 歩行者デッキ直結の北口エントランスすぐ<br/>
                    • <strong>国際会議室 (4F)</strong>: 案内図奥のエレベーターを利用して4階へ<br/>
                    • <strong>館内設備</strong>: タリーズコーヒー、ファミリーマート、ATM、多機能トイレあり
                </div>
                """,
                unsafe_allow_html=True,
            )

        with tab_rooms:
            st.caption("各トラック・会場の所在とアクセス方法一覧")
            for room in venue.rooms:
                _render_room_card(room)

        with tab_building:
            st.caption("ソニックシティ全体（ビル棟・ホール棟・ホテル）の立体見取り図")
            building_img_path = repo_root / venue.map_images.get("building", "")
            if building_img_path.exists():
                st.image(str(building_img_path), use_container_width=True)


def render_room_inline_badge(room: RoomGuide):
    """セッション詳細画面用の部屋行き方インラインカード"""
    st.markdown(
        f"""
        <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #3b82f6; border-radius: 6px; padding: 10px 12px; margin-top: 10px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 12px; font-weight: 700; color: #1e3a8a;">📍 会場: {room.room_name}</span>
                <span style="background: #dbeafe; color: #1e40af; font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 4px;">{room.building} {room.floor}</span>
            </div>
            <div style="font-size: 12px; color: #475569; line-height: 1.5;">
                {room.access_instruction}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_room_card(room: RoomGuide):
    """部屋ガイド個別カード"""
    badge_bg = "#e0e7ff"
    badge_color = "#3730a3"
    if "B" in room.track_code:
        badge_bg = "#fef3c7"
        badge_color = "#92400e"
    elif "C" in room.track_code:
        badge_bg = "#ccfbf1"
        badge_color = "#115e59"

    note_html = (
        f'<div style="font-size: 11px; color: #64748b; margin-top: 4px;">※ {room.note}</div>'
        if room.note
        else ""
    )

    st.markdown(
        f"""
        <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; background: white;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="background: {badge_bg}; color: {badge_color}; font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 4px;">
                    {room.track_code}
                </span>
                <span style="font-size: 12px; font-weight: 600; color: #1e293b;">
                    {room.building} {room.floor}
                </span>
            </div>
            <div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">
                {room.room_name}
            </div>
            <div style="font-size: 12px; color: #475569; line-height: 1.4;">
                {room.access_instruction}
            </div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
