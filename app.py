"""赛博意境 — AI 诗意卡片"""

import streamlit as st
import os
from agent import generate_card
from prompts import STYLES
from llm_client import check_api_key, reset_client

# ── Page Config ─────────────────────────────────
st.set_page_config(page_title="赛博意境", page_icon="⚡", layout="centered")

# ── Fonts & Base CSS ────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700&family=Noto+Serif+SC:wght@400;600;700&family=Orbitron:wght@400;700&display=swap');

    * { box-sizing: border-box; }
    .main .block-container { padding: 3rem 1.5rem; max-width: 720px; }
    #MainMenu, footer, .stAppDeployButton { visibility: hidden; }
    .stButton button { transition: all 0.2s ease; }

    /* ═══════════════════════════════════════
       HEADER
       ═══════════════════════════════════════ */
    .hero {
        text-align: center;
        margin-bottom: 3rem;
        padding-top: 1rem;
    }
    .hero h1 {
        font-family: 'Noto Serif SC', serif;
        font-size: 3.2rem;
        font-weight: 600;
        letter-spacing: 0.25em;
        margin: 0 0 0.5rem 0;
        background: linear-gradient(135deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero .sub {
        font-size: 0.95rem;
        color: #999;
        letter-spacing: 0.15em;
        font-weight: 300;
    }

    /* ═══════════════════════════════════════
       INPUT AREA
       ═══════════════════════════════════════ */
    .input-row {
        display: flex;
        gap: 12px;
        align-items: center;
        justify-content: center;
        margin-bottom: 1.5rem;
    }
    .input-row > div { flex: 1; }
    .stTextInput > div > div > input {
        font-size: 1.15rem !important;
        text-align: center !important;
        border-radius: 16px !important;
        border: 2px solid #e5e7eb !important;
        padding: 14px 20px !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 0 4px rgba(168,85,247,0.1) !important;
    }

    /* ═══════════════════════════════════════
       STYLE PILLS
       ═══════════════════════════════════════ */
    .style-pills {
        display: flex;
        gap: 8px;
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: 2rem;
    }
    .style-pill {
        padding: 8px 20px;
        border-radius: 100px;
        font-size: 0.85rem;
        cursor: pointer;
        border: 1.5px solid #e5e7eb;
        background: white;
        color: #666;
        transition: all 0.25s ease;
        user-select: none;
    }
    .style-pill.active {
        background: #1a1a2e;
        color: white;
        border-color: #1a1a2e;
    }

    /* ═══════════════════════════════════════
       CARD
       ═══════════════════════════════════════ */
    .art-card {
        padding: 3rem 2.5rem;
        border-radius: 24px;
        margin: 2rem auto;
        max-width: 520px;
        min-height: 380px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
        animation: cardIn 0.7s cubic-bezier(0.16, 1, 0.3, 1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .art-card:hover {
        transform: translateY(-4px);
    }

    @keyframes cardIn {
        from { opacity: 0; transform: translateY(40px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .card-title {
        font-size: 2.6rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        margin-bottom: 1.8rem;
        line-height: 1.25;
        position: relative;
        z-index: 2;
    }
    .card-body {
        font-size: 1.15rem;
        line-height: 2.2;
        flex-grow: 1;
        position: relative;
        z-index: 2;
    }
    .card-foot {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 1.5rem;
        margin-top: 1rem;
        font-size: 0.9rem;
        opacity: 0.65;
        position: relative;
        z-index: 2;
    }
    .card-seal {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        border: 2px solid;
        opacity: 0.55;
        flex-shrink: 0;
    }

    /* ── Ink Decorations ── */
    .decor-ink-ring {
        position: absolute;
        border-radius: 50%;
        border: 1.5px solid;
        opacity: 0.12;
        pointer-events: none;
    }
    .decor-ink-dot {
        position: absolute;
        border-radius: 50%;
        opacity: 0.08;
        pointer-events: none;
    }

    /* ── Cyber Decorations ── */
    .decor-scanline {
        position: absolute;
        left: 0; right: 0;
        height: 2px;
        opacity: 0.15;
        pointer-events: none;
    }
    .decor-glitch-block {
        position: absolute;
        border-radius: 4px;
        opacity: 0.06;
        pointer-events: none;
    }

    /* ── Minimal Decorations ── */
    .decor-thin-line {
        position: absolute;
        opacity: 0.15;
        pointer-events: none;
    }

    /* ── Retro Decorations ── */
    .decor-stamp {
        position: absolute;
        border: 2px dashed;
        border-radius: 8px;
        opacity: 0.2;
        pointer-events: none;
    }

    /* ═══════════════════════════════════════
       EXAMPLE CHIPS
       ═══════════════════════════════════════ */
    .example-chip {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 100px;
        font-size: 0.85rem;
        color: #888;
        cursor: pointer;
        border: 1px solid #eee;
        transition: all 0.2s ease;
    }
    .example-chip:hover { border-color: #a855f7; color: #a855f7; }

    /* ═══════════════════════════════════════
       DIVIDER
       ═══════════════════════════════════════ */
    .art-divider {
        text-align: center;
        margin: 2rem 0;
        color: #ddd;
        font-size: 0.8rem;
        letter-spacing: 0.3em;
    }
</style>
""", unsafe_allow_html=True)

# ── API Key Check ───────────────────────────────
if not check_api_key():
    with st.expander("🔑 API Key", expanded=True):
        k = st.text_input("SiliconFlow Key", type="password", placeholder="sk-...")
        if k:
            os.environ["DEEPSEEK_API_KEY"] = k
            import config; config.DEEPSEEK_API_KEY = k
            reset_client()
            st.rerun()
        st.stop()

# ── Session State ───────────────────────────────
if "cards" not in st.session_state:
    st.session_state.cards = {}
if "active_style" not in st.session_state:
    st.session_state.active_style = "禅意水墨"
if "keyword" not in st.session_state:
    st.session_state.keyword = ""

# ── Header ──────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>赛 博 意 境</h1>
    <p class="sub">输 入 一 个 词 · AI 为 你 造 一 首 诗</p>
</div>
""", unsafe_allow_html=True)

# ── Input Row ───────────────────────────────────
ci, cs = st.columns([5, 2])
kw = st.session_state.keyword.strip()
active = st.session_state.active_style
with ci:
    keyword = st.text_input(
        "关键词",
        value=st.session_state.keyword,
        placeholder="夏天 / 暗恋 / 故乡 / 自由 / 失眠 / 远方 …",
        label_visibility="collapsed",
    )
    if keyword != st.session_state.keyword:
        st.session_state.keyword = keyword
with cs:
    if st.button("⚡ 生成", use_container_width=True, type="primary", key="gen_btn"):
        kw_temp = st.session_state.keyword.strip()
        if kw_temp:
            st.session_state._trigger = active
            st.session_state.keyword = kw_temp
            st.rerun()

# ── Style Pills ─────────────────────────────────
pill_cols = st.columns(len(STYLES))
clicked_style = None
for i, (sname, sinfo) in enumerate(STYLES.items()):
    with pill_cols[i]:
        is_active = st.session_state.active_style == sname
        label = f"{'● ' if is_active else ''}{sname}"
        if st.button(label, key=f"pill_{sname}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.active_style = sname
            st.rerun()

# ── Example Words ───────────────────────────────
if not st.session_state.cards:
    st.markdown("<div style='text-align:center;margin-top:1rem;'>", unsafe_allow_html=True)
    st.caption("试试这些 →")
    examples = ["夏天", "暗恋", "失眠", "故乡", "自由", "孤独", "毕业", "远方", "初恋", "雨夜"]
    ec = st.columns(len(examples))
    for i, ex in enumerate(examples):
        with ec[i]:
            if st.button(ex, key=f"ex_{ex}"):
                st.session_state.keyword = ex
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ── Card Renderer ───────────────────────────────
def render_card(card: dict, style_name: str, style: dict, compact: bool = False):
    """渲染一张艺术卡片"""
    decor = style["decor"]
    seal_color = style["seal_color"]
    text_color = style["text"]
    accent = style["accent"]
    muted = style["muted"]
    title_font = style["font_title"]
    body_font = style["font_body"]

    # Decorative elements
    decor_html = ""
    if decor == "ink":
        decor_html = f"""
        <div class="decor-ink-ring" style="width:180px;height:180px;top:-60px;right:-60px;border-color:{text_color};"></div>
        <div class="decor-ink-ring" style="width:100px;height:100px;bottom:-30px;left:-30px;border-color:{text_color};"></div>
        <div class="decor-ink-dot" style="width:300px;height:300px;top:20%;left:-100px;background:{accent};"></div>"""
    elif decor == "cyber":
        decor_html = f"""
        <div class="decor-scanline" style="top:30%;background:{accent};"></div>
        <div class="decor-scanline" style="top:70%;background:{accent};opacity:0.08;"></div>
        <div class="decor-glitch-block" style="width:120px;height:60px;top:20%;right:-20px;background:{accent};"></div>
        <div class="decor-glitch-block" style="width:80px;height:40px;bottom:25%;left:-15px;background:{text_color};"></div>"""
    elif decor == "minimal":
        decor_html = f"""
        <div class="decor-thin-line" style="top:40px;left:40px;right:40px;height:1px;background:{muted};"></div>
        <div class="decor-thin-line" style="bottom:40px;left:40px;right:40px;height:1px;background:{muted};"></div>"""
    elif decor == "retro":
        decor_html = f"""
        <div class="decor-stamp" style="top:20px;right:30px;width:60px;height:60px;border-color:{accent};transform:rotate(12deg);"></div>
        <div class="decor-ink-ring" style="width:140px;height:140px;bottom:-50px;left:-50px;border-color:{accent};"></div>"""

    # Shadow
    shadow = "0 4px 32px rgba(0,0,0,0.06)" if decor != "cyber" else "0 4px 40px rgba(100,0,200,0.15)"

    h = """<div class="art-card" style="
        background: """ + style["card_bg"] + """;
        color: """ + text_color + """;
        box-shadow: """ + shadow + """;
        """ + ("max-width:480px;min-height:280px;padding:2rem 1.8rem;" if compact else "") + """
    ">""" + decor_html + """
        <div class="card-title" style="font-family:""" + title_font + """!important;">""" + card.get("title", "") + """</div>
        <div class="card-body" style="font-family:""" + body_font + """!important;">""" + card.get("text", "") + """</div>
        <div class="card-foot" style="border-top:1px solid """ + muted + """33;">
            <span>— """ + card.get("footer", "") + """</span>
            <div class="card-seal" style="border-color:""" + seal_color + """;color:""" + seal_color + """;">
                """ + card.get("emotion", "")[:2] + """
            </div>
        </div>
    </div>"""

    st.markdown(h, unsafe_allow_html=True)

# ── Generate ────────────────────────────────────
kw = st.session_state.keyword.strip()

# If user clicked generate button or has keyword + no card yet for this style
should_generate = st.session_state.get("_trigger") == active

if should_generate and kw:
    with st.spinner(""):
        try:
            card = generate_card(kw, active)
            st.session_state.cards[active] = card
            st.session_state._trigger = None
        except Exception as e:
            st.error(f"生成失败：{e}")
            st.session_state._trigger = None

# ── Render Cards ────────────────────────────────
if st.session_state.cards:
    # Show active card first
    active_card = st.session_state.cards.get(active)
    if active_card:
        render_card(active_card, active, STYLES[active])

    # Show other generated styles below
    other_styles = [s for s in st.session_state.cards if s != active]
    if other_styles:
        st.markdown('<div class="art-divider">··· 已生成的其他风格 ···</div>',
                   unsafe_allow_html=True)
        for s in other_styles:
            render_card(st.session_state.cards[s], s, STYLES[s], compact=True)

# ── Quick Generate All ──────────────────────────
if st.session_state.cards:
    st.divider()
    st.caption("✨ 一键补全其他风格：")
    remaining = [s for s in STYLES if s not in st.session_state.cards]
    if remaining:
        rc = st.columns(len(remaining))
        for i, s in enumerate(remaining):
            with rc[i]:
                if st.button(f"生成「{s}」", key=f"gen_{s}", use_container_width=True):
                    with st.spinner(""):
                        card = generate_card(kw, s)
                        st.session_state.cards[s] = card
                    st.rerun()
    if st.button("⟳ 清空重来", use_container_width=True):
        st.session_state.cards = {}
        st.session_state.keyword = ""
        st.rerun()
