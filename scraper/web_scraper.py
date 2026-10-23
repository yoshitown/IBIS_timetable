"""
IBIS2026 Webサイトスクレイパー
公式Webサイトからチュートリアル、企画セッション、招待講演等のプログラム詳細・要旨を自動収集します。
"""

import json
import os
import re
import urllib.parse
from typing import Any, Dict, List
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://ibisml.org/ibis2026/"
PROGRAM_URL = "https://ibisml.org/ibis2026/program/"

TARGET_PAGES = [
    {
        "category": "チュートリアル",
        "url": "https://ibisml.org/ibis2026/tutorial/",
    },
    {
        "category": "企画セッション",
        "url": "https://ibisml.org/ibis2026/os/",
    },
    {
        "category": "招待講演",
        "url": "https://ibisml.org/ibis2026/invited/",
    },
]


def clean_text(text: str) -> str:
    """テキストの余計な空白・改行を整理"""
    lines = [line.strip() for line in text.split("\n")]
    clean_lines = []
    prev_empty = False
    for line in lines:
        if line:
            clean_lines.append(line)
            prev_empty = False
        elif not prev_empty:
            clean_lines.append("")
            prev_empty = True
    return "\n".join(clean_lines).strip()


def scrape_session_page(url: str, category: str) -> List[Dict[str, Any]]:
    """セッション詳細ページをスクレイピングしてセッション一覧を取得"""
    res = requests.get(url, timeout=15)
    res.raise_for_status()
    soup = BeautifulSoup(res.content, "html.parser")

    content = soup.find(class_="entry-content") or soup.find("main") or soup.find("article") or soup.body
    if not content:
        return []

    # h2 / h3 タグでセッション・講演が区切られている構造を解析
    sessions = []
    
    # ページ全体のテキストブロック
    full_text = clean_text(content.get_text(separator="\n", strip=True))

    # セクションごとに分割
    # 各h2 (または大きな見出し) がセッション区分になっていることが多い
    h2_elements = content.find_all(["h2", "h3"])
    
    if not h2_elements:
        sessions.append({
            "category": category,
            "title": soup.find("h1").get_text(strip=True) if soup.find("h1") else category,
            "url": url,
            "content": full_text
        })
        return sessions

    current_title = ""
    current_paragraphs: List[str] = []

    for elem in content.children:
        if elem.name in ["h2", "h3"]:
            if current_title:
                sessions.append({
                    "category": category,
                    "title": current_title,
                    "url": url,
                    "content": "\n\n".join(current_paragraphs).strip()
                })
                current_paragraphs = []
            current_title = elem.get_text(strip=True)
        elif elem.name in ["p", "ul", "ol", "div", "blockquote"]:
            txt = elem.get_text(separator="\n", strip=True)
            if txt:
                current_paragraphs.append(txt)

    if current_title:
        sessions.append({
            "category": category,
            "title": current_title,
            "url": url,
            "content": "\n\n".join(current_paragraphs).strip()
        })

    return sessions


def scrape_all_ibis2026_data() -> List[Dict[str, Any]]:
    """全ターゲットページから要旨データを収集"""
    all_data = []

    # プログラム概要ページ
    try:
        res = requests.get(PROGRAM_URL, timeout=15)
        if res.ok:
            soup = BeautifulSoup(res.content, "html.parser")
            main = soup.find(class_="entry-content") or soup.find("main") or soup.body
            if main:
                all_data.append({
                    "category": "プログラム概要",
                    "title": "IBIS2026 プログラム全体概要",
                    "url": PROGRAM_URL,
                    "content": clean_text(main.get_text(separator="\n", strip=True))
                })
    except Exception as e:
        print(f"Error fetching program overview: {e}")

    # 各セッション詳細ページ
    for target in TARGET_PAGES:
        try:
            page_sessions = scrape_session_page(target["url"], target["category"])
            all_data.extend(page_sessions)
        except Exception as e:
            print(f"Error scraping {target['url']}: {e}")

    return all_data


def save_data_json(data: List[Dict[str, Any]], filepath: str = "data/abstracts.json") -> str:
    """構造化データをJSON形式で保存"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filepath


if __name__ == "__main__":
    print("IBIS2026 データの収集を開始...")
    data = scrape_all_ibis2026_data()
    print(f"取得完了: 合計 {len(data)} 件のセッション・要旨を抽出しました。")
    saved_path = save_data_json(data)
    print(f"JSONデータを保存しました: {saved_path}")
