"""期末突击教练 — Streamlit App"""

import streamlit as st
import os
import io
from PyPDF2 import PdfReader
from agent import TutorAgent
from llm_client import check_api_key, reset_client

# ──────────────────────────────────────────────
# PDF 工具函数
# ──────────────────────────────────────────────
def extract_pdf_text(uploaded_file) -> str:
    """从上传的 PDF 文件中提取文本"""
    reader = PdfReader(uploaded_file)
    text_parts = []
    total_chars = 0
    max_chars = 10000  # 最多提取10000字
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
            total_chars += len(page_text)
            if total_chars > max_chars:
                break
    return "\n\n".join(text_parts)

# ──────────────────────────────────────────────
st.set_page_config(
    page_title="期末突击教练",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main .block-container { padding-top: 1rem; }
    .stButton button { font-weight: 600; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .big-score { font-size: 48px; font-weight: 800; text-align: center; }
    .pass-tag { padding: 4px 12px; border-radius: 20px; font-weight: 700; display: inline-block; }
    .pass-tag.safe { background: #d4edda; color: #155724; }
    .pass-tag.risky { background: #fff3cd; color: #856404; }
    .pass-tag.dead { background: #f8d7da; color: #721c24; }
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
        st.info("💡 从 https://cloud.siliconflow.cn 获取")
        st.stop()

# ──────────────────────────────────────────────
# Session State
# ──────────────────────────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = TutorAgent()
if "page" not in st.session_state:
    st.session_state.page = 0
if "course_done" not in st.session_state:
    st.session_state.course_done = False
if "diagnostic_questions" not in st.session_state:
    st.session_state.diagnostic_questions = ""
if "diagnostic_done" not in st.session_state:
    st.session_state.diagnostic_done = False
if "plan_done" not in st.session_state:
    st.session_state.plan_done = False
if "mock_questions" not in st.session_state:
    st.session_state.mock_questions = ""
if "mock_done" not in st.session_state:
    st.session_state.mock_done = False

agent: TutorAgent = st.session_state.agent
mem = agent.memory

PAGES = ["📋 课程设置", "🔍 知识点诊断", "📅 突击计划", "📝 模拟考试"]

# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.title("🏥 期末突击教练")
    st.caption("专治期末来不及复习")
    st.divider()

    # 进度指示器
    for i, name in enumerate(PAGES):
        done = False
        if i == 0:
            done = st.session_state.course_done
        elif i == 1:
            done = st.session_state.diagnostic_done
        elif i == 2:
            done = st.session_state.plan_done
        elif i == 3:
            done = st.session_state.mock_done

        icon = "✅" if done else ("📍" if i == st.session_state.page else "⬜")
        st.markdown(f"{icon} {name}")

    st.divider()
    if mem.course_info:
        st.caption(f"📚 {mem.course_info.get('name', '')}")
        st.caption(f"⏰ 剩余 {mem.course_info.get('hours', '?')} 小时")
        if mem.total_score:
            st.caption(f"📊 诊断得分：{mem.total_score}/100")

    st.divider()
    if st.button("🔄 重新开始", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ──────────────────────────────────────────────
# Page 0: 课程设置
# ──────────────────────────────────────────────
if st.session_state.page == 0:
    st.title("📋 告诉我你的情况")
    st.caption("越详细，突击计划越精准")

    col1, col2 = st.columns(2)
    with col1:
        course_name = st.text_input("课程名称", placeholder="例如：计算机网络、高等数学、毛概...")
        exam_date = st.text_input("考试日期", placeholder="例如：7月5日 或 3天后")
        available_hours = st.number_input("你能投入多少小时复习？", min_value=1, max_value=100, value=10)

    with col2:
        uploaded_files = st.file_uploader(
            "📄 上传课件 PDF（自动提取知识点）",
            type="pdf",
            accept_multiple_files=True,
            help="支持同时上传多个PDF，自动合并分析",
        )
        topics = st.text_area(
            "或者手动输入知识点（也可和PDF一起用，互相补充）",
            placeholder="随便列，想到什么写什么。\n\n例如：\n- TCP/IP协议\n- 子网划分\n- 路由算法\n- 应用层协议...",
            height=130,
        )

    # 预览 PDF 提取内容
    pdf_text = ""
    if uploaded_files:
        with st.expander(f"📄 已上传 {len(uploaded_files)} 个 PDF，点击预览提取内容"):
            for f in uploaded_files:
                text = extract_pdf_text(f)
                pdf_text += text + "\n\n"
                st.caption(f"**{f.name}** — 提取 {len(text)} 字")
                with st.container(height=120):
                    st.text(text[:500] + ("..." if len(text) > 500 else ""))

    has_content = bool(course_name.strip()) and (bool(topics.strip()) or bool(pdf_text))

    if st.button("🚀 开始分析", use_container_width=True, type="primary", disabled=not has_content):
        with st.spinner("🏥 急救王老师正在分析..."):
            source = topics.strip() if topics.strip() else ""
            if pdf_text:
                source += ("\n\n[PDF课件内容]\n" + pdf_text[:8000])

            mem.course_info = {
                "name": course_name.strip(),
                "exam_date": exam_date.strip() or "未知",
                "hours": available_hours,
                "topics": source or "（未提供）",
                "has_pdf": bool(pdf_text),
            }

            if pdf_text and not topics.strip():
                # 纯 PDF 上传：用 PDF 专用分析
                result = agent.analyze_pdf(
                    course_name=course_name.strip(),
                    pdf_text=pdf_text,
                    exam_date=exam_date.strip() or "未知",
                    available_hours=available_hours,
                )
            else:
                # 手动输入或混合：用通用分析
                result = agent.analyze_course(
                    course_name=course_name.strip(),
                    topics=source or "未提供",
                    exam_date=exam_date.strip() or "未知",
                    available_hours=available_hours,
                )

            mem.knowledge_map = result
            st.session_state.course_done = True
            st.session_state.page = 1
            st.rerun()

# ──────────────────────────────────────────────
# Page 1: 知识点诊断
# ──────────────────────────────────────────────
elif st.session_state.page == 1:
    st.title("🔍 知识点诊断")

    tab1, tab2 = st.tabs(["📊 知识地图", "📝 诊断测试"])

    with tab1:
        st.markdown(mem.knowledge_map)
        if st.button("👉 开始诊断测试", type="primary"):
            pass  # just scroll to tab2

    with tab2:
        if not st.session_state.diagnostic_questions:
            if st.button("🩺 生成诊断题", type="primary", use_container_width=True):
                with st.spinner("出题中..."):
                    questions = agent.generate_diagnostic_quiz(
                        mem.course_info["name"],
                        mem.knowledge_map,
                    )
                    st.session_state.diagnostic_questions = questions
                st.rerun()
        else:
            st.markdown(st.session_state.diagnostic_questions)

            user_answers = st.text_area(
                "✍️ 你的作答（逐题写上你的答案）",
                placeholder="第1题：我选 C\n第2题：我选 A\n第3题：...\n第4题：...",
                height=200,
            )

            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("📤 提交批改", type="primary", use_container_width=True,
                            disabled=not user_answers.strip()):
                    with st.spinner("批改中..."):
                        result = agent.grade_diagnostic(
                            mem.course_info["name"],
                            st.session_state.diagnostic_questions,
                            user_answers.strip(),
                        )
                        mem.weak_points = result
                        st.session_state.diagnostic_done = True
                        # Parse score
                        import re
                        score_match = re.search(r'总分[：:]\s*(\d+)', result)
                        if score_match:
                            mem.total_score = int(score_match.group(1))
                    st.rerun()
            with col2:
                if st.button("🔄 重新出题", use_container_width=True):
                    st.session_state.diagnostic_questions = ""
                    st.rerun()

            if st.session_state.diagnostic_done:
                st.divider()
                st.subheader("📊 诊断结果")
                if mem.total_score:
                    level = "稳" if mem.total_score >= 70 else ("悬" if mem.total_score >= 40 else "危")
                    color = "#155724" if mem.total_score >= 70 else ("#856404" if mem.total_score >= 40 else "#721c24")
                    bg = "#d4edda" if mem.total_score >= 70 else ("#fff3cd" if mem.total_score >= 40 else "#f8d7da")
                    st.markdown(
                        f"<div style='text-align:center;padding:16px;background:{bg};border-radius:16px;'>"
                        f"<span style='font-size:48px;font-weight:800;color:{color};'>{mem.total_score}</span>"
                        f"<span style='font-size:20px;color:{color};'> / 100</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown(mem.weak_points)
                if st.button("📅 下一步：生成突击计划 →", type="primary"):
                    st.session_state.page = 2
                    st.rerun()

# ──────────────────────────────────────────────
# Page 2: 突击计划
# ──────────────────────────────────────────────
elif st.session_state.page == 2:
    st.title("📅 极限突击计划")

    if not st.session_state.plan_done:
        with st.spinner("🏥 正在为你量身定制突击计划..."):
            plan = agent.generate_cram_plan(
                mem.course_info["name"],
                mem.course_info["hours"],
                mem.weak_points,
                mem.knowledge_map,
            )
            mem.study_plan = plan
            st.session_state.plan_done = True
        st.rerun()

    st.markdown(mem.study_plan)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 返回诊断", use_container_width=True):
            st.session_state.page = 1
            st.rerun()
    with col2:
        if st.button("📝 下一步：模拟考试 →", type="primary", use_container_width=True):
            st.session_state.page = 3
            st.rerun()

# ──────────────────────────────────────────────
# Page 3: 模拟考试
# ──────────────────────────────────────────────
elif st.session_state.page == 3:
    st.title("📝 考前模拟")

    if not st.session_state.mock_questions:
        if st.button("🎲 生成模拟卷", type="primary", use_container_width=True):
            with st.spinner("出卷中..."):
                exam = agent.generate_mock_exam(
                    mem.course_info["name"],
                    mem.weak_points,
                )
                st.session_state.mock_questions = exam
            st.rerun()
    elif not st.session_state.mock_done:
        st.markdown(st.session_state.mock_questions)

        user_answers = st.text_area(
            "✍️ 你的作答",
            placeholder="第1题：...\n第2题：...\n第3题：...",
            height=200,
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("📤 提交批改", type="primary", use_container_width=True,
                        disabled=not user_answers.strip()):
                with st.spinner("批改中..."):
                    result = agent.grade_mock_exam(
                        st.session_state.mock_questions,
                        user_answers.strip(),
                    )
                    st.session_state.mock_done = True
                    # Store result in memory for display
                    import re
                    score_match = re.search(r'总分[：:]\s*(\d+)', result)
                    if score_match:
                        mem.total_score = int(score_match.group(1))
                    # Store result text
                    st.session_state.mock_result = result
                st.rerun()
        with col2:
            if st.button("🔄 换一套卷", use_container_width=True):
                st.session_state.mock_questions = ""
                st.rerun()
    else:
        st.subheader("🎯 模拟考成绩")
        result_text = st.session_state.get("mock_result", "")
        st.markdown(result_text)

        if st.button("🔙 回头复习计划", use_container_width=True):
            st.session_state.page = 2
            st.rerun()

        st.divider()
        st.success("""
        ### 🎉 训练完成！

        你已经完成了完整的突击流程：
        1. ✅ 知识地图分析
        2. ✅ 薄弱点诊断
        3. ✅ 个性化突击计划
        4. ✅ 模拟考试

        **按左侧「🔄 重新开始」可以换一门课继续突击！**
        """)
