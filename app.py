import os
import streamlit as st
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(
    page_title="IBIS2026 Timeline & Agenda Viewer",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Streamlitのデフォルト余白・ヘッダー・フッターを最小化して没入感を高める
st.markdown(
    """
    <style>
        /* Streamlitのデフォルトパディングを最小化 */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        header[data-testid="stHeader"] {
            display: none !important;
        }
        footer {
            display: none !important;
        }
        #MainMenu {
            visibility: hidden !important;
        }
        iframe {
            border: none !important;
            width: 100% !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# HTMLファイルの読み込み
html_file_path = os.path.join(
    os.path.dirname(__file__),
    "stitch_ibis2026_conference_schedule_dashboard",
    "code.html",
)

if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 高密度ダッシュボードの表示 (スクロール対応・十分な高さを確保)
    components.html(html_content, height=1100, scrolling=True)
else:
    st.error("ダッシュボードHTMLファイルが見つかりません。")
