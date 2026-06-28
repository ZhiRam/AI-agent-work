"""赛博意境 — AI 艺术卡片生成器"""

import streamlit as st
import os
from agent import generate_card
from prompts import STYLE_COLORS, STYLE_PROMPTS
from llm_client import check_api_key, reset_client

# ──────────────────────────────────────────────
st.set_page_config(page_title="赛博意境", page_icon="🎨", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&display=swap');

    .main .block-container { padding: 2rem 1rem; max-width: 800px; }
    #MainMenu, footer { visibility: hidden; }

    .card {
        padding: 40px 36px;
        border-radius: 20px;
        margin: 20px 0;
        min-height: 320px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
        transition: all 0.4s ease;
        box-shadow: 0 8px 40px rgba(0,0,0,0.12);
    }
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 60px rgba(0,0,0,0.18);
    }

    .card-title {
        font-size: 2.4em;
        font-weight: 700;
        margin-bottom: 24px;
        letter-spacing: 0.08em;
        line-height: 1.3;
    }
    .card-text {
        font-size: 1.3em;
        line-height: 2;
        margin-bottom: 28px;
        opacity: 0.9;
        flex-grow: 1;
    }
    .card-footer {
        font-size: 0.95em;
        opacity: 0.6;
        letter-spacing: 0.05em;
        border-top: 1px solid;
        padding-top: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .emotion-tag {
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 0.85em;
        letter-spacing: 0.05em;
        border: 1px solid;
        opacity: 0.7;
    }

    /* 装饰元素 */
    .card::before {
        content: '';
        position: absolute;
        top: -60px;
        right: -60px;
        width: 200px;
        height: 200px;
        border-radius: 50%;
        opacity: 0.06;
        pointer-events: none;
    }
    .card.ink::before { background: #3d3226; }
    .card.cyber::before { background: #00ffcc; }
    .card.minimal::before { background: #999; }
    .card.retro::before { background: #8b6914; }

    /* 入场动画 */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .card { animation: fadeUp 0.6s ease-out; }

    /* 输入区 */
    .input-section {
        text-align: center;
        margin-bottom: 30px;
    }
    .big-input input {
        font-size: 1.3em !important;
        text-align: center !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# API Key
# ──────────────────────────────────────────────
if not check_api_key():
    with st.expander("🔑 配置 API Key", expanded=True):
        api_key = st.text_input("输入 SiliconFlow API Key", type="password", placeholder="sk-...")
        if api_key:
            os.environ["DEEPSEEK_API_KEY"] = api_key
            import config
            config.DEEPSEEK_API_KEY = api_key
            reset_client()
            st.success("✅ 已设置！")
            st.rerun()
        st.stop()

# ──────────────────────────────────────────────
# 主界面
# ──────────────────────────────────────────────

st.markdown("""
<div style="text-align:center; margin-bottom:10px;">
    <h1 style="font-size:3em; font-weight:800; letter-spacing:0.1em; margin-bottom:0;">赛 博 意 境</h1>
    <p style="color:#888; font-size:1em;">输入一个词，AI 为你造一张诗意卡片</p>
</div>
""", unsafe_allow_html=True)

# 输入区
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    keyword = st.text_input(
        "你的关键词",
        placeholder="比如：夏天、暗恋、失眠、故乡、自由...",
        label_visibility="collapsed",
        key="keyword_input",
    )
with col2:
    style = st.selectbox(
        "风格",
        list(STYLE_PROMPTS.keys()),
        label_visibility="collapsed",
    )
with col3:
    generate_btn = st.button("✨ 生成卡片", use_container_width=True, type="primary")

# ──────────────────────────────────────────────
# 示例关键词
# ──────────────────────────────────────────────
examples = ["夏天", "暗恋", "失眠", "故乡", "自由", "孤独", "毕业", "远方", "初恋", "月亮"]

if not generate_btn and not st.session_state.get("cards"):
    st.markdown("<div style='text-align:center; margin:16px 0;'>", unsafe_allow_html=True)
    st.caption("💡 试试这些关键词：")
    cols = st.columns(len(examples))
    for i, ex in enumerate(examples):
        with cols[i]:
            if st.button(ex, key=f"ex_{ex}", use_container_width=True):
                st.session_state.keyword = ex
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Session State
# ──────────────────────────────────────────────
if "cards" not in st.session_state:
    st.session_state.cards = {}  # {style: card_dict}

# 预填充输入框
if "keyword" in st.session_state:
    # 用 js 没法改，手动提示
    pass

# ──────────────────────────────────────────────
# 生成卡片
# ──────────────────────────────────────────────
actual_keyword = keyword or st.session_state.get("keyword", "")

if generate_btn and actual_keyword.strip():
    with st.spinner(f"🎨 正在为你创作「{style}」风格卡片..."):
        try:
            card = generate_card(actual_keyword.strip(), style)
            st.session_state.cards[style] = card
            st.session_state.keyword = actual_keyword.strip()
        except Exception as e:
            st.error(f"生成失败：{e}")

# ──────────────────────────────────────────────
# 显示卡片
# ──────────────────────────────────────────────
if st.session_state.cards:
    st.divider()

    styles_to_show = list(st.session_state.cards.keys())

    for s in styles_to_show:
        card = st.session_state.cards[s]
        colors = STYLE_COLORS[s]
        css_class = {"水墨": "ink", "赛博朋克": "cyber", "极简": "minimal", "复古": "retro"}.get(s, "")

        # 生成卡片 HTML
        st.markdown(f"""
        <div class="card {css_class}" style="
            background: {colors['bg']};
            color: {colors['text']};
            font-family: {colors['font']};
        ">
            <div class="card-title">{card.get('title', '')}</div>
            <div class="card-text">{card.get('text', '')}</div>
            <div class="card-footer" style="border-color:{colors['accent']};">
                <span>— {card.get('footer', '')}</span>
                <span class="emotion-tag" style="border-color:{colors['accent']};">{card.get('emotion', '')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.caption(f"🎨 风格：{' | '.join(styles_to_show)} | 📸 截图保存即可分享")

# ──────────────────────────────────────────────
# 底部：多风格一键生成
# ──────────────────────────────────────────────
if st.session_state.cards:
    st.divider()
    st.markdown("### 🎭 换风格再看看？")
    remaining = [s for s in STYLE_PROMPTS.keys() if s not in st.session_state.cards]
    if remaining:
        cols = st.columns(len(remaining))
        for i, s in enumerate(remaining):
            with cols[i]:
                if st.button(f"生成「{s}」风格", key=f"style_{s}", use_container_width=True):
                    with st.spinner(f"创作中..."):
                        kw = st.session_state.get("keyword", "")
                        card = generate_card(kw, s)
                        st.session_state.cards[s] = card
                    st.rerun()

    if st.button("🔄 清空重新开始", use_container_width=True):
        st.session_state.cards = {}
        st.session_state.keyword = ""
        st.rerun()
