"""赛博室友 — Streamlit Web 界面"""

import streamlit as st
import os
from simulator import Simulator
from prompts import AGENT_CONFIGS
from llm_client import check_api_key, reset_client

# ──────────────────────────────────────────────
# 页面配置
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="赛博室友 - 302宿舍",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# 自定义 CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* 整体背景 */
    .main .block-container {
        padding-top: 1rem;
    }

    /* 聊天气泡 */
    .chat-bubble {
        padding: 10px 16px;
        border-radius: 16px;
        margin: 6px 0;
        max-width: 85%;
        animation: fadeIn 0.3s ease-in;
        line-height: 1.6;
    }
    .chat-bubble.left {
        background: #f0f2f6;
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }
    .chat-bubble.right {
        background: #e3f2fd;
        margin-left: auto;
        border-bottom-right-radius: 4px;
        text-align: right;
    }
    .chat-bubble.event {
        background: #fff3e0;
        margin: 8px auto;
        text-align: center;
        border-radius: 20px;
        font-weight: 500;
        max-width: 95%;
    }
    .chat-bubble.user-possession {
        background: #fce4ec;
        border: 2px dashed #e91e63;
    }

    /* Agent 名称 */
    .agent-name {
        font-weight: 700;
        font-size: 13px;
        margin-bottom: 2px;
    }

    /* Agent 卡片 */
    .agent-card {
        background: white;
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border-left: 4px solid #ccc;
    }
    .agent-card .emoji {
        font-size: 28px;
    }

    /* 按钮行 */
    .button-row button {
        margin: 4px;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* 隐藏 Streamlit 默认元素 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* 对话容器自动滚动 */
    .chat-container {
        max-height: 60vh;
        overflow-y: auto;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 标题
# ──────────────────────────────────────────────
st.title("🏠 赛博室友 — 302宿舍直播间")
st.caption("4个 AI Agent 模拟真实大学宿舍生活 | MBTI × 多智能体 | 围观 or 附身")

# ──────────────────────────────────────────────
# API Key 检查
# ──────────────────────────────────────────────
if not check_api_key():
    with st.expander("🔑 请先配置 DeepSeek API Key", expanded=True):
        api_key = st.text_input(
            "输入你的 DeepSeek API Key",
            type="password",
            placeholder="sk-...",
            help="从 https://platform.deepseek.com/api_keys 获取"
        )
        if api_key:
            os.environ["DEEPSEEK_API_KEY"] = api_key
            import config
            config.DEEPSEEK_API_KEY = api_key
            reset_client()  # 强制重建客户端
            st.success("✅ API Key 已设置！刷新中...")
            st.rerun()
        st.info("💡 API Key 仅保存在本次会话中，不会上传到任何地方")
        st.stop()

# ──────────────────────────────────────────────
# 初始化 Session State
# ──────────────────────────────────────────────
if "sim" not in st.session_state:
    st.session_state.sim = Simulator()
if "auto_running" not in st.session_state:
    st.session_state.auto_running = False
if "event_pending" not in st.session_state:
    st.session_state.event_pending = None

sim: Simulator = st.session_state.sim

# ──────────────────────────────────────────────
# 侧边栏 — Agent 信息 + 控制
# ──────────────────────────────────────────────
with st.sidebar:
    st.header("👥 302 宿舍成员")

    # 渲染每个 Agent 卡片
    for name, config in AGENT_CONFIGS.items():
        agent = sim.agents[name]
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"<div style='font-size:36px;text-align:center;'>{config['emoji']}</div>",
                           unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{name}** `{config['mbti']}`")
                st.caption(f"{agent.emotion}")

            # 好感度条
            if agent.relationships:
                for other_name, score in agent.relationships.scores.items():
                    label = agent.relationships.get_relationship_label(other_name)
                    pct = score / 100
                    st.markdown(
                        f"<small>{other_name} {label}</small>",
                        unsafe_allow_html=True,
                    )
                    st.progress(pct)

            st.markdown("<hr style='margin:4px 0'>", unsafe_allow_html=True)

    # ── 控制区 ──
    st.divider()

    # 一轮对话
    col_a, col_b = st.columns([3, 1])
    with col_a:
        if st.button("💬 下一轮对话", use_container_width=True, help="让一位室友自动发言"):
            result = sim.run_turn()
            st.rerun()
    with col_b:
        n_turns = st.number_input("轮数", 1, 10, 5, label_visibility="collapsed")

    if st.button(f"⏩ 快速推进 {n_turns} 轮", use_container_width=True):
        with st.spinner(f"室友们正在聊天...({n_turns}轮)"):
            sim.run_multi_turns(int(n_turns))
        st.rerun()

    # 随机事件
    st.divider()
    if st.button("🎲 触发随机事件", use_container_width=True, type="primary"):
        with st.spinner("事件发酵中..."):
            sim.random_event()
        st.rerun()

    # 附身模式
    st.divider()
    st.subheader("👤 附身发言")
    possession_target = st.selectbox(
        "选择要附身的室友",
        list(AGENT_CONFIGS.keys()),
    )
    possession_msg = st.text_area(
        "以他的身份说点什么...",
        placeholder="比如：兄弟们，我有个大胆的想法！",
        max_chars=200,
        height=80,
    )
    if st.button("📢 发送（附身模式）", use_container_width=True, disabled=not possession_msg.strip()):
        sim.user_speak(possession_target, possession_msg.strip())
        st.rerun()

    # 重置
    st.divider()
    if st.button("🔄 重置宿舍", use_container_width=True):
        st.session_state.sim = Simulator()
        st.session_state.auto_running = False
        st.rerun()

    # 导出
    st.divider()
    st.caption(f"💾 对话轮数: {sim.turn_count}")

# ──────────────────────────────────────────────
# 主面板 — 对话展示
# ──────────────────────────────────────────────

# 欢迎信息
if len(sim.display_history) == 0:
    st.info("""
    👋 **欢迎来到 302 宿舍！**

    这里有 4 位性格迥异的 AI 室友：
    - 🐶 **小明** (ENFP) — 社牛话痨，宿舍气氛组
    - 🦉 **阿哲** (INTJ) — 理性毒舌，年级第一
    - 🌿 **小宇** (ISFP) — 温柔敏感，养生达人
    - 🐒 **老王** (ESTP) — 行动派吃货，社会我王哥

    点击左侧 **「💬 下一轮对话」** 开始围观他们的宿舍生活吧！
    """)

# 对话流
chat_col = st.container()

with chat_col:
    for i, msg in enumerate(sim.display_history):
        agent_name = msg["agent"]
        message = msg["message"]
        emoji = msg["emoji"]
        color = msg["color"]
        is_event = msg.get("is_event", False)
        is_user = msg.get("is_user", False)

        if is_event:
            # 事件消息 — 居中高亮
            st.markdown(f"""
            <div class="chat-bubble event" style="border:2px solid {color}">
                {emoji} {message}
            </div>
            """, unsafe_allow_html=True)
        else:
            # 普通聊天消息
            user_tag = "👤[用户附身]" if is_user else ""
            align_class = "right" if (i % 2 == 0) else "left"
            bubble_style = "user-possession" if is_user else ""

            with st.chat_message(name=agent_name, avatar=emoji):
                st.markdown(f"{message}")
                st.caption(f"{agent_name} · {msg.get('mbti', '')} {user_tag}")

# ──────────────────────────────────────────────
# 底部快捷操作
# ──────────────────────────────────────────────
st.divider()
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("💬 下一轮", use_container_width=True, key="bottom_next"):
        sim.run_turn()
        st.rerun()
with col2:
    if st.button("⏩ 快速5轮", use_container_width=True, key="bottom_fast"):
        with st.spinner("聊天中..."):
            sim.run_multi_turns(5)
        st.rerun()
with col3:
    if st.button("🎲 随机事件", use_container_width=True, key="bottom_event"):
        sim.random_event()
        st.rerun()
with col4:
    if st.button("🔄 重置", use_container_width=True, key="bottom_reset"):
        st.session_state.sim = Simulator()
        st.rerun()
with col5:
    if st.button("📋 导出对话", use_container_width=True, key="bottom_export"):
        export_text = ""
        for msg in sim.display_history:
            export_text += f"[{msg['agent']}] {msg['message']}\n"
        st.download_button(
            "下载对话记录",
            export_text,
            file_name="302宿舍对话记录.txt",
            mime="text/plain",
        )

# ──────────────────────────────────────────────
# 底部自动滚动
# ──────────────────────────────────────────────
st.markdown("""
<script>
    // 自动滚动到最新消息
    const chatContainer = window.parent.document.querySelector('.main');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
</script>
""", unsafe_allow_html=True)
