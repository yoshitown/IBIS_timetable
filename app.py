import os
import urllib.parse
from bs4 import BeautifulSoup
import requests
import streamlit as st
from scraper.pdf_exporter import create_abstracts_pdf
from scraper.web_scraper import scrape_all_ibis2026_data, save_data_json

st.set_page_config(
    page_title="IBIS2026 要旨まとめ＆PDF生成ツール",
    page_icon="📚",
    layout="wide",
)

st.title("📚 IBIS2026 プログラム・要旨詳細スクレイパー")
st.caption(
    "IBIS2026公式サイトからプログラム一覧・チュートリアル・企画セッション・招待講演の要旨を自動収集し、ローカルにPDF/JSON保存します。"
)

# 保存先パス
PDF_PATH = "data/ibis2026_program_abstracts.pdf"
JSON_PATH = "data/abstracts.json"

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("1. データ収集・抽出")
    st.write(
        "公式サイト（チュートリアル、企画セッション、招待講演、プログラム概要）から最新の要旨データを収集します。"
    )

    if st.button("🚀 最新の要旨データを取得してローカルにPDF保存", type="primary"):
        with st.spinner("IBIS2026の各セッション詳細ページを収集中..."):
            try:
                data = scrape_all_ibis2026_data()
                save_data_json(data, JSON_PATH)
                pdf_file = create_abstracts_pdf(data, PDF_PATH)
                st.session_state["extracted_data"] = data
                st.success(
                    f"✅ 取得＆PDF保存が完了しました！（全 {len(data)} 件のセッション・要旨）"
                )
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")

with col2:
    st.subheader("2. 保存済みファイル")
    if os.path.exists(PDF_PATH):
        pdf_size_kb = os.path.getsize(PDF_PATH) / 1024
        st.info(f"📄 **PDF**: `{PDF_PATH}` ({pdf_size_kb:.1f} KB)")
        with open(PDF_PATH, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label="📥 PDFファイルをダウンロード",
            data=pdf_bytes,
            file_name="IBIS2026_abstracts.pdf",
            mime="application/pdf",
        )
    else:
        st.caption("PDFファイルはまだ作成されていません。")

    if os.path.exists(JSON_PATH):
        json_size_kb = os.path.getsize(JSON_PATH) / 1024
        st.info(f"🗂️ **JSON**: `{JSON_PATH}` ({json_size_kb:.1f} KB)")
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            json_text = f.read()
        st.download_button(
            label="📥 JSONデータをダウンロード",
            data=json_text,
            file_name="IBIS2026_abstracts.json",
            mime="application/json",
        )

# セッションデータの表示
import json

display_data = st.session_state.get("extracted_data")
if not display_data and os.path.exists(JSON_PATH):
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        display_data = json.load(f)

if display_data:
    st.divider()
    st.subheader(f"📑 収集済み要旨一覧 (全 {len(display_data)} 件)")

    # カテゴリごとに分類表示
    categories = sorted(list({item.get("category", "その他") for item in display_data}))
    selected_category = st.selectbox("カテゴリ絞り込み", ["すべて"] + categories)

    filtered = [
        item
        for item in display_data
        if selected_category == "すべて" or item.get("category") == selected_category
    ]

    for idx, item in enumerate(filtered):
        cat = item.get("category", "")
        title = item.get("title", "").replace("\n", " ")
        with st.expander(f"【{cat}】{title}"):
            if item.get("url"):
                st.caption(f"🔗 参照元: [{item['url']}]({item['url']})")
            st.text_area(
                "要旨・詳細内容",
                value=item.get("content", ""),
                height=200,
                key=f"text_{idx}",
                disabled=True,
            )
