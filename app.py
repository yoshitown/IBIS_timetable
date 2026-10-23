import urllib.parse
from bs4 import BeautifulSoup
import requests
import streamlit as st

st.set_page_config(
    page_title="IBIS2026 要旨まとめ＆PDF生成ツール", layout="wide"
)
st.title("IBIS2026 プログラム・要旨詳細スクレイパー")

base_url = "https://ibisml.org/ibis2026/program/"
url_input = st.text_input("対象プログラムURL", value=base_url)

if st.button("詳細・要旨データを取得"):
    with st.spinner("ページ解析および詳細ページの取得中..."):
        try:
            res = requests.get(url_input)
            res.raise_for_status()
            soup = BeautifulSoup(res.content, "html.parser")

            # ページ内のチュートリアル・各セッションへのリンクを抽出
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                full_url = urllib.parse.urljoin(url_input, href)
                # IBIS2026ドメイン内の詳細リンクのみをフィルタリング
                if "ibisml.org/ibis2026" in full_url and full_url not in links:
                    links.append(full_url)

            st.success(f"合計 {len(links)} 件の関連ページ・リンクを検出しました。")

            # 収集データの保持
            extracted_data = []

            for link in links:
                sub_res = requests.get(link)
                sub_soup = BeautifulSoup(sub_res.content, "html.parser")

                # タイトルおよび本文（要旨）の抽出
                page_title = (
                    sub_soup.find("h1").get_text(strip=True)
                    if sub_soup.find("h1")
                    else link
                )

                # メインコンテンツブロックの取得 (サイトのHTML構造に合わせて指定)
                main_content = (
                    sub_soup.find("main")
                    or sub_soup.find("article")
                    or sub_soup.body
                )
                text_content = (
                    main_content.get_text(separator="\n", strip=True)
                    if main_content
                    else ""
                )

                extracted_data.append(
                    {"title": page_title, "url": link, "content": text_content}
                )

            # 画面への表示
            for idx, item in enumerate(extracted_data):
                with st.expander(f"【セッション】{item['title']}"):
                    st.caption(f"URL: {item['url']}")
                    st.text_area(
                        "要旨・詳細内容",
                        value=item["content"],
                        height=250,
                        key=f"text_{idx}",
                    )

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
