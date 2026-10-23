"""
プレゼンテーション層: モバイル最適化 垂直タイムライン (Vertical Timeline Stream) コンポーネント
スマートフォンでの片手操作・縦スクロールに特化したUIをレンダリングします。
"""

import streamlit as st
import streamlit.components.v1 as components

from domain.models import Session
from domain.policies import CategoryVisualPolicy, TimePolicy


def render_mobile_timeline(
    sessions: list[Session],
    current_minutes: int,
    selected_day_label: str = "Day 2: 10/27 (火)",
    ongoing_session: Session | None = None,
):
    """
    ユーザー提示のStitchモバイルUIデザインに準拠した垂直タイムラインを生成・レンダリング
    """
    if not sessions:
        st.info("該当するセッションが見つかりませんでした。条件を変更してください。")
        return

    current_time_str = TimePolicy.minutes_to_time_str(current_minutes)

    # セッションを開始時刻順にソート
    sorted_sessions = sorted(sessions, key=lambda s: s.start_minutes)

    # タイムラインブロックの生成
    timeline_blocks_html = ""
    marker_placed = False

    for s in sorted_sessions:
        is_ongoing = s.is_ongoing(current_minutes)

        # 現在時刻マーカー (進行中セッションの手前、または時間帯の間に挿入)
        if not marker_placed and current_minutes <= s.end_minutes:
            marker_html = f"""
            <!-- CURRENT TIME LASER INDICATOR ({current_time_str} JST) -->
            <div class="relative pl-10 pr-1 py-1 -my-1 z-20" id="live-marker">
                <div class="flex items-center gap-2">
                    <div class="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-error text-on-error shadow-[0_0_12px_rgba(186,26,26,0.45)]">
                        <span class="w-1.5 h-1.5 rounded-full bg-on-error animate-ping"></span>
                        <span class="font-label-sm text-label-sm tracking-wider font-bold">{current_time_str} LIVE</span>
                    </div>
                    <div class="h-0.5 flex-1 bg-gradient-to-r from-error via-error to-transparent shadow-[0_0_8px_rgba(186,26,26,0.6)]"></div>
                </div>
            </div>
            """
            timeline_blocks_html += marker_html
            marker_placed = True

        # スタイル設定
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

        # 残り時間計算 (進行中の場合)
        status_badge_html = ""
        if is_ongoing:
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
            <span class="px-2 py-0.5 rounded bg-surface-container text-on-surface-variant font-label-sm text-label-sm">
                {style["label"]}
            </span>
            """

        # 登壇者チップス
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
                <span class="material-symbols-outlined text-[16px] text-outline">person</span>
                <span class="font-medium text-on-surface">{s.organizer}</span>
            </div>
            """

        # 要旨アコーディオン
        abstract_html = ""
        if s.abstract:
            abstract_html = f"""
            <div class="mt-2 p-2.5 rounded-lg bg-surface-container-low/70">
                <details class="group">
                    <summary class="font-label-sm text-label-sm text-primary font-medium cursor-pointer list-none flex items-center justify-between">
                        <span>セッション要旨・理論的射程を展開</span>
                        <span class="material-symbols-outlined text-[16px] transition-transform group-open:rotate-180">expand_more</span>
                    </summary>
                    <p class="font-body-sm text-body-sm text-on-surface-variant pt-2 leading-relaxed">
                        {s.abstract.replace(chr(10), "<br/>")}
                    </p>
                </details>
            </div>
            """

        # セッションカード
        card_html = f"""
        <!-- Session Block: {s.title} -->
        <div class="relative flex items-start gap-space-md">
            <!-- Time Marker Node -->
            <div class="w-12 pt-1 flex flex-col items-end flex-shrink-0">
                <span class="font-label-md text-label-md {"text-primary font-bold" if is_ongoing else "text-on-surface font-semibold"}">{s.start_time}</span>
                <span class="font-label-sm text-label-sm text-outline">{s.end_time}</span>
            </div>
            <div class="w-3 h-3 rounded-full {"bg-primary ring-4 ring-primary-fixed" if is_ongoing else "bg-surface-container-highest"} mt-2 flex-shrink-0 z-10"></div>

            <!-- Card Body -->
            <div class="flex-1 min-w-0">
                <div class="relative rounded-xl bg-surface-container-lowest p-space-md shadow-sm hover:shadow-md transition-shadow flex flex-col gap-space-xs overflow-hidden border border-outline-variant/30">
                    <div class="absolute left-0 top-0 bottom-0 w-1.5 {border_color_class}"></div>

                    <div class="flex items-center justify-between gap-2">
                        <div class="flex items-center gap-1.5">
                            {status_badge_html}
                        </div>
                        <span class="font-label-sm text-label-sm text-on-surface-variant font-medium bg-surface-container-high px-2 py-0.5 rounded">
                            {s.track}
                        </span>
                    </div>

                    <div class="pt-0.5">
                        <h2 class="font-headline-md text-headline-md text-on-surface leading-snug font-bold">
                            {s.title}
                        </h2>
                    </div>

                    {speakers_chips_html}
                    {abstract_html}
                </div>
            </div>
        </div>
        """
        timeline_blocks_html += card_html

    # もし全セッション終了後なら末尾にマーカーを挿入
    if not marker_placed:
        timeline_blocks_html += f"""
        <div class="relative pl-10 pr-1 py-1 -my-1 z-20" id="live-marker">
            <div class="flex items-center gap-2">
                <div class="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-error text-on-error">
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
    <body class="bg-surface font-body-md text-on-surface antialiased p-2 sm:p-4">
        <!-- Real-time Alert & Jump Bar -->
        <div class="sticky top-0 z-30 bg-surface/95 backdrop-blur-md pb-2 pt-1">
            <div class="flex items-center justify-between px-space-md py-2 rounded-xl bg-surface-container-lowest shadow-sm border border-outline-variant/30">
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
                <button class="flex items-center gap-1 px-3 py-1 rounded-lg bg-primary-fixed text-on-primary-fixed font-label-sm text-label-sm font-semibold active:scale-95 transition-transform flex-shrink-0 shadow-xs cursor-pointer" onclick="document.getElementById('live-marker').scrollIntoView({{ behavior: 'smooth', block: 'center' }})">
                    <span class="material-symbols-outlined text-[15px]">my_location</span>
                    現在位置へ
                </button>
            </div>
        </div>

        <!-- Vertical Timeline Matrix -->
        <div class="relative w-full px-2 pt-4">
            <!-- Continuous Timeline Axis Bar -->
            <div class="absolute left-[62px] top-6 bottom-4 w-0.5 bg-surface-container-highest"></div>

            <div class="flex flex-col gap-y-6">
                {timeline_blocks_html}
            </div>
        </div>

        <!-- Floating Bottom Status Pill -->
        <div class="mt-8 mb-4 flex justify-center">
            <div class="flex items-center gap-3 px-4 py-2 rounded-full bg-inverse-surface/90 text-inverse-on-surface shadow-md text-label-sm font-label-sm">
                <span class="flex items-center gap-1 text-tertiary-fixed font-semibold">
                    <span class="w-2 h-2 rounded-full bg-tertiary-fixed"></span> {selected_day_label}
                </span>
                <span class="opacity-40">|</span>
                <button class="flex items-center gap-0.5 hover:text-primary-fixed transition-colors cursor-pointer" onclick="window.scrollTo({{ top: 0, behavior: 'smooth' }})">
                    <span class="material-symbols-outlined text-[15px]">arrow_upward</span>
                    トップへ
                </button>
            </div>
        </div>
    </body>
    </html>
    """

    # 動的な高さ計算 (各カード約160px〜220px)
    calculated_height = max(600, 140 + len(sorted_sessions) * 190)

    # components.html で安全かつ美しくレンダリング
    components.html(full_html, height=calculated_height, scrolling=False)
