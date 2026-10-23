"""
プレゼンテーション層: モバイル最適化 並行3トラック統合タイムライン (Vertical Timeline Stream) コンポーネント
トラック絞り込みフィルターを排除し、並行するTrack A/B/Cのセッションを時系列順に一望できるようにレンダリングします。
"""

from typing import Optional

import streamlit as st
import streamlit.components.v1 as components

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

    timeline_blocks_html = ""
    marker_placed = False

    for block in schedule.time_blocks:
        is_block_ongoing = block.is_ongoing(current_minutes)

        # 現在時刻マーカー (進行中ブロックの手前、または時間帯の間に挿入)
        if not marker_placed and current_minutes <= block.end_minutes:
            marker_html = f"""
            <!-- CURRENT TIME LASER INDICATOR ({current_time_str} JST) -->
            <div class="relative pl-8 sm:pl-10 pr-1 my-3 z-20 scroll-mt-20" id="live-marker">
                <div class="flex items-center gap-2">
                    <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-error text-on-error shadow-[0_0_12px_rgba(186,26,26,0.45)]">
                        <span class="w-1.5 h-1.5 rounded-full bg-on-error animate-ping"></span>
                        <span class="font-label-sm text-label-sm tracking-wider font-bold">{current_time_str} LIVE</span>
                    </div>
                    <div class="h-0.5 flex-1 bg-gradient-to-r from-error via-error to-transparent shadow-[0_0_8px_rgba(186,26,26,0.6)]"></div>
                </div>
            </div>
            """
            timeline_blocks_html += marker_html
            marker_placed = True

        # 並行トラックバッジ
        parallel_badge_html = ""
        if block.parallel_count > 1:
            parallel_badge_html = f"""
            <span class="font-label-sm text-label-sm font-bold px-2 py-0.5 rounded bg-primary-fixed text-on-primary-fixed">
                並行 {block.parallel_count} トラック
            </span>
            """

        # ブロック内の全セッションカード (Track A → B → C 順)
        cards_in_block_html = ""
        for s in block.sessions:
            is_session_ongoing = s.is_ongoing(current_minutes)
            style = CategoryVisualPolicy.get_style(s.category)

            # 左端ボーダー色
            border_color_class = "bg-primary"
            if s.category == "invited":
                border_color_class = "bg-secondary"
            elif s.category == "tutorial":
                border_color_class = "bg-surface-tint"
            elif s.category == "poster":
                border_color_class = "bg-tertiary"
            elif s.category == "panel":
                border_color_class = "bg-inverse-surface"

            # 状態バッジ
            if is_session_ongoing:
                remaining_mins = max(0, s.end_minutes - current_minutes)
                status_badge_html = f"""
                <span class="px-2 py-0.5 rounded bg-tertiary-fixed text-on-tertiary-fixed font-label-sm text-label-sm font-semibold flex items-center gap-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-tertiary-container animate-pulse"></span>
                    LIVE NOW
                </span>
                <span class="px-2 py-0.5 rounded-md bg-secondary-fixed text-on-secondary-fixed font-label-sm text-label-sm font-medium">
                    残り {remaining_mins}分
                </span>
                """
            else:
                status_badge_html = f"""
                <span class="px-2 py-0.5 rounded bg-surface-container text-on-surface-variant font-label-sm text-label-sm font-medium">
                    {style["label"]}
                </span>
                """

            # 登壇者チップ
            speakers_chips_html = ""
            if s.talks:
                chips = []
                for idx, t in enumerate(s.talks[:4]):
                    chips.append(
                        f'<span class="px-2 py-0.5 rounded bg-surface-container text-on-surface-variant font-body-sm text-body-sm">{idx + 1}. {t.speaker.name} ({t.speaker.affiliation})</span>'
                    )
                speakers_chips_html = f"""
                <div class="flex flex-col gap-1 pt-1">
                    <span class="font-label-sm text-label-sm text-on-surface-variant font-medium">登壇者 ({len(s.talks)}件):</span>
                    <div class="flex flex-wrap gap-1.5">
                        {"".join(chips)}
                    </div>
                </div>
                """
            elif s.organizer:
                speakers_chips_html = f"""
                <div class="flex items-center gap-2 py-1 bg-surface-container-low px-2 rounded-lg text-body-sm">
                    <span class="material-symbols-outlined text-[15px] text-outline">person</span>
                    <span class="font-medium text-on-surface truncate">{s.organizer}</span>
                </div>
                """

            # 詳細ページへの遷移ボタン (target="_top" で親ウィンドウを更新)
            detail_link_html = f"""
            <div class="pt-2 flex justify-end">
                <a target="_top" href="?session={s.session_id}" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-surface-container-low hover:bg-surface-container-high text-primary font-label-sm text-label-sm font-bold transition-all shadow-xs active:scale-95 text-decoration-none">
                    <span>詳細・各講演の要旨を見る</span>
                    <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
                </a>
            </div>
            """

            # 個別カードHTML
            cards_in_block_html += f"""
            <div class="relative rounded-xl bg-surface-container-lowest p-3 sm:p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col gap-2 overflow-hidden border border-outline-variant/30 mb-3 last:mb-0">
                <div class="absolute left-0 top-0 bottom-0 w-1.5 {border_color_class}"></div>

                <div class="flex items-center justify-between gap-2">
                    <div class="flex items-center gap-1.5">
                        {status_badge_html}
                    </div>
                    <span class="font-label-sm text-label-sm font-semibold px-2 py-0.5 rounded bg-surface-container-high text-on-surface">
                        {s.track.full_label}
                    </span>
                </div>

                <div class="pt-0.5">
                    <h2 class="font-headline-md text-headline-md text-on-surface leading-snug font-bold">
                        {s.title}
                    </h2>
                </div>

                {speakers_chips_html}
                {detail_link_html}
            </div>
            """

        # タイムブロック全体のHTML
        block_node_html = f"""
        <!-- Time Block: {block.start_time} - {block.end_time} -->
        <div class="relative flex items-start gap-3 sm:gap-4">
            <!-- Time Marker Node -->
            <div class="w-12 pt-1 flex flex-col items-end flex-shrink-0">
                <span class="font-label-md text-label-md {"text-primary font-bold" if is_block_ongoing else "text-on-surface font-semibold"}">{block.start_time}</span>
                <span class="font-label-sm text-label-sm text-outline">{block.end_time}</span>
            </div>
            <div class="w-3 h-3 rounded-full {"bg-primary ring-4 ring-primary-fixed" if is_block_ongoing else "bg-surface-container-highest"} mt-2 flex-shrink-0 z-10"></div>

            <!-- Cards Wrapper (並行トラックカード群) -->
            <div class="flex-1 min-w-0">
                {f'<div class="flex items-center justify-between pb-1.5">{parallel_badge_html}</div>' if parallel_badge_html else ""}
                {cards_in_block_html}
            </div>
        </div>
        """
        timeline_blocks_html += block_node_html

    # もし全セッション終了後なら末尾にマーカーを挿入
    if not marker_placed:
        timeline_blocks_html += f"""
        <div class="relative pl-8 sm:pl-10 pr-1 my-3 z-20 scroll-mt-20" id="live-marker">
            <div class="flex items-center gap-2">
                <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-error text-on-error">
                    <span class="font-label-sm text-label-sm font-bold">{current_time_str} LIVE</span>
                </div>
                <div class="h-0.5 flex-1 bg-error"></div>
            </div>
        </div>
        """

    # 進行中バナーテキスト
    ongoing_text = (
        f"進行中: {ongoing_session.title} ({ongoing_session.start_time}-{ongoing_session.end_time})"
        if ongoing_session
        else f"現在セッション休止中 ({current_time_str})"
    )

    full_html = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="utf-8"/>
        <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" name="viewport"/>
        <link rel="preconnect" href="https://fonts.googleapis.com"/>
        <link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet"/>
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>
        <style>
            @layer base {{
                html, body {{ width: 100%; margin: 0; padding: 0; }}
                body {{ overscroll-behavior: none; }}
            }}
            ::-webkit-scrollbar {{ display: none; }}
        </style>
        <script src="https://cdn.tailwindcss.com"></script>
        <script id="tailwind-config">
        tailwind.config = {{
            darkMode: "class",
            theme: {{
                extend: {{
                    colors: {{
                        "surface": "#faf8ff",
                        "on-surface": "#131b2e",
                        "on-surface-variant": "#464555",
                        "surface-container-lowest": "#ffffff",
                        "surface-container-low": "#f2f3ff",
                        "surface-container": "#eaedff",
                        "surface-container-high": "#e2e7ff",
                        "surface-container-highest": "#dae2fd",
                        "primary": "#3525cd",
                        "primary-container": "#4f46e5",
                        "primary-fixed": "#e2dfff",
                        "on-primary-fixed": "#0f0069",
                        "secondary": "#904d00",
                        "secondary-container": "#fe932c",
                        "secondary-fixed": "#ffdcc3",
                        "on-secondary-fixed": "#2f1500",
                        "tertiary": "#00524b",
                        "tertiary-container": "#006c63",
                        "tertiary-fixed": "#89f5e7",
                        "on-tertiary-fixed": "#00201d",
                        "error": "#ba1a1a",
                        "on-error": "#ffffff",
                        "inverse-surface": "#283044",
                        "inverse-on-surface": "#eef0ff",
                        "outline": "#777587",
                        "outline-variant": "#c7c4d8"
                    }},
                    spacing: {{
                        "gutter-mobile": "0.75rem",
                        "margin-mobile": "0.75rem",
                        "space-xs": "0.25rem",
                        "space-sm": "0.5rem",
                        "space-md": "0.75rem",
                        "space-lg": "1.25rem",
                        "space-xl": "2rem"
                    }},
                    fontFamily: {{
                        "headline-md": ["Inter"],
                        "body-md": ["Inter"],
                        "body-sm": ["Inter"],
                        "label-md": ["JetBrains Mono"],
                        "label-sm": ["JetBrains Mono"]
                    }},
                    fontSize: {{
                        "headline-md": ["16px", {{"lineHeight": "22px", "fontWeight": "600"}}],
                        "body-md": ["13px", {{"lineHeight": "18px", "fontWeight": "400"}}],
                        "body-sm": ["12px", {{"lineHeight": "16px", "fontWeight": "400"}}],
                        "label-md": ["11px", {{"lineHeight": "14px", "fontWeight": "500"}}],
                        "label-sm": ["10px", {{"lineHeight": "12px", "fontWeight": "600"}}]
                    }}
                }}
            }}
        }};
        </script>
    </head>
    <body class="bg-surface font-body-md text-on-surface antialiased p-2 sm:p-4 pb-16">
        <!-- Real-time Alert & Jump Bar (Sticky Top) -->
        <div class="sticky top-0 z-30 bg-surface/95 backdrop-blur-md pb-3 pt-1 border-b border-outline-variant/20 shadow-xs mb-3">
            <div class="flex items-center justify-between px-3 py-2 rounded-xl bg-surface-container-lowest shadow-sm border border-outline-variant/30">
                <div class="flex items-center gap-2 min-w-0">
                    <span class="flex h-2.5 w-2.5 relative flex-shrink-0">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-error opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-error"></span>
                    </span>
                    <div class="flex items-baseline gap-1.5 truncate">
                        <span class="font-label-md text-label-md text-on-surface font-bold">{current_time_str} JST</span>
                        <span class="font-body-sm text-body-sm text-on-surface-variant truncate">{ongoing_text}</span>
                    </div>
                </div>
                <button class="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-primary-fixed text-on-primary-fixed font-label-sm text-label-sm font-semibold active:scale-95 transition-transform flex-shrink-0 shadow-xs cursor-pointer" onclick="scrollToMarker()">
                    <span class="material-symbols-outlined text-[15px]">my_location</span>
                    現在位置へ
                </button>
            </div>
        </div>

        <!-- Vertical Timeline Matrix -->
        <div class="relative w-full px-2 pt-2">
            <!-- Continuous Timeline Axis Bar -->
            <div class="absolute left-[62px] top-4 bottom-4 w-0.5 bg-surface-container-highest"></div>

            <div class="flex flex-col gap-y-6">
                {timeline_blocks_html}
            </div>
        </div>

        <!-- Bottom Status Pill -->
        <div class="mt-8 mb-6 flex justify-center">
            <div class="flex items-center gap-3 px-4 py-2 rounded-full bg-inverse-surface/90 text-inverse-on-surface shadow-md text-label-sm font-label-sm">
                <span class="flex items-center gap-1 text-tertiary-fixed font-semibold">
                    <span class="w-2 h-2 rounded-full bg-tertiary-fixed"></span> {schedule.label}
                </span>
                <span class="opacity-40">|</span>
                <button class="flex items-center gap-0.5 hover:text-primary-fixed transition-colors cursor-pointer" onclick="window.scrollTo({{ top: 0, behavior: 'smooth' }})">
                    <span class="material-symbols-outlined text-[15px]">arrow_upward</span>
                    トップへ
                </button>
            </div>
        </div>

        <script>
        function scrollToMarker() {{
            const marker = document.getElementById('live-marker');
            if (marker) {{
                marker.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
        }}
        </script>
    </body>
    </html>
    """

    # 全体カード数に基づく動的高さ計算
    total_cards = sum(b.parallel_count for b in schedule.time_blocks)
    calculated_height = max(800, 250 + total_cards * 190)

    # components.html で安全かつ美しくレンダリング
    components.html(full_html, height=calculated_height, scrolling=True)
