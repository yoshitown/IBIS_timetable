"""
IBIS2026 プログラム・要旨 PDFエクスポートモジュール
収集したセッション情報・要旨を美しい日本語PDFに整形して出力します。
"""

import os
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

# 日本語フォントの登録 (ReportLab標準のUnicode CIDフォント)
FONT_NAME = "HeiseiKakuGo-W5"
pdfmetrics.registerFont(UnicodeCIDFont(FONT_NAME))


class NumberedCanvas(canvas.Canvas):
    """フッターに総ページ数つきのページ番号を付与するカスタムCanvas"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont(FONT_NAME, 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # 1ページ目は表紙なのでヘッダー・フッターを省略
        if self._pageNumber > 1:
            # ヘッダー
            self.drawString(36, A4[1] - 28, "IBIS2026 プログラム・セッション要旨集")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(36, A4[1] - 32, A4[0] - 36, A4[1] - 32)

            # フッター
            self.line(36, 36, A4[0] - 36, 36)
            footer_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(A4[0] - 36, 24, footer_text)
            self.drawString(36, 24, "https://ibisml.org/ibis2026/")

        self.restoreState()


def create_abstracts_pdf(
    data: list[dict[str, Any]],
    output_filepath: str = "data/ibis2026_program_abstracts.pdf",
) -> str:
    """収集データを整形してPDFファイルを生成"""
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46,
    )

    # カスタムスタイル
    cover_title_style = ParagraphStyle(
        "CoverTitle",
        fontName=FONT_NAME,
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#0f172a"),
        alignment=1,  # Center
        spaceAfter=15,
    )

    cover_subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        fontName=FONT_NAME,
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#334155"),
        alignment=1,
        spaceAfter=30,
    )

    cover_meta_style = ParagraphStyle(
        "CoverMeta",
        fontName=FONT_NAME,
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#64748b"),
        alignment=1,
    )

    category_heading_style = ParagraphStyle(
        "CategoryHeading",
        fontName=FONT_NAME,
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=14,
        spaceAfter=10,
        keepWithNext=True,
    )

    session_title_style = ParagraphStyle(
        "SessionTitle",
        fontName=FONT_NAME,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True,
    )

    session_url_style = ParagraphStyle(
        "SessionUrl",
        fontName=FONT_NAME,
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#2563eb"),
        spaceAfter=6,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "SessionBody",
        fontName=FONT_NAME,
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=8,
    )

    story = []

    # ==========================
    # 表紙 (Cover Page)
    # ==========================
    story.append(Spacer(1, 120))
    story.append(Paragraph("IBIS2026", cover_title_style))
    story.append(
        Paragraph(
            "第29回 情報論的学習理論ワークショップ<br/>プログラム概要・講演要旨集",
            cover_title_style,
        )
    )
    story.append(
        HRFlowable(
            width="60%",
            thickness=2,
            color=colors.HexColor("#2563eb"),
            spaceBefore=15,
            spaceAfter=25,
            hAlign="CENTER",
        )
    )
    story.append(
        Paragraph(
            "会期: 2026年10月26日(月) 〜 10月29日(木)<br/>会場: ソニックシティ（埼玉県さいたま市）",
            cover_subtitle_style,
        )
    )
    story.append(Spacer(1, 80))

    now_str = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    meta_text = f"自動収集・生成日時: {now_str}<br/>対象Webサイト: https://ibisml.org/ibis2026/<br/>総収録件数: {len(data)} 件"
    story.append(Paragraph(meta_text, cover_meta_style))
    story.append(PageBreak())

    # ==========================
    # 目次・セッション本文
    # ==========================
    # カテゴリごとにグループ化
    current_category = None

    for item in data:
        cat = item.get("category", "一般")
        if cat != current_category:
            current_category = cat
            story.append(Spacer(1, 10))
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=1.5,
                    color=colors.HexColor("#1e3a8a"),
                    spaceBefore=10,
                    spaceAfter=5,
                )
            )
            story.append(Paragraph(f"■ {current_category}", category_heading_style))

        # 各セッションブロック
        block_items = []
        raw_title = item.get("title", "").replace("\n", " ").strip()
        if not raw_title:
            raw_title = f"{current_category} 詳細"

        # XMLタグやエスケープ
        safe_title = raw_title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        block_items.append(Paragraph(f"● {safe_title}", session_title_style))

        url = item.get("url", "")
        if url:
            block_items.append(Paragraph(f"参照URL: {url}", session_url_style))

        content = item.get("content", "").strip()
        if content:
            # 段落ごとに分割して追加
            paragraphs = content.split("\n\n")
            for p in paragraphs:
                p_clean = p.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                p_clean = p_clean.replace("\n", "<br/>")
                if p_clean:
                    block_items.append(Paragraph(p_clean, body_style))
        else:
            block_items.append(Paragraph("（詳細情報・要旨の記載なし）", body_style))

        block_items.append(Spacer(1, 8))
        story.append(KeepTogether(block_items[:3]))  # タイトルとURLは可能な限り一緒に表示
        for remaining in block_items[3:]:
            story.append(remaining)

    # PDFドキュメントの生成
    doc.build(story, canvasmaker=NumberedCanvas)
    return output_filepath


if __name__ == "__main__":
    import json

    json_path = "data/abstracts.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            scraped_data = json.load(f)
        pdf_path = create_abstracts_pdf(scraped_data)
        print(f"PDF生成完了: {pdf_path}")
    else:
        print("data/abstracts.json が見つかりません。先にスクレイパーを実行してください。")
