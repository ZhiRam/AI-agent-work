"""Agent 类：期末突击教练"""

from llm_client import chat, chat_vision
from memory import MemoryStore
from prompts import TUTOR_PROMPT


class TutorAgent:
    """期末突击教练 Agent"""

    def __init__(self):
        self.system_prompt = TUTOR_PROMPT
        self.memory = MemoryStore()

    def _call(self, user_message: str, temperature: float = 0.7) -> str:
        """调用 LLM"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]
        return chat(messages, temperature=temperature, max_tokens=2048)

    # ─── 阶段 0：分析 PDF 课件 ───
    def analyze_pdf(self, course_name: str, pdf_text: str, exam_date: str, available_hours: int) -> str:
        """分析上传的 PDF 课件，自动提取知识点并生成知识地图"""
        # 截断过长文本（保留前8000字）
        text = pdf_text[:8000]
        prompt = f"""学生上传了【{course_name}】的课件 PDF，考试日期：{exam_date}，可用复习时间：约{available_hours}小时。

以下是课件内容：
---
{text}
---

请完成：
1. 从课件中提取所有知识点，整理成树状结构（Markdown列表）
2. 标注每个知识点的：
   - 重要度（⭐⭐⭐必考 / ⭐⭐常考 / ⭐偶尔）——根据课件篇幅和强调程度判断
   - 难度（难/中/易）
3. 指出 3 个"绝对不能丢分"的核心考点
4. 估算总复习时间是否够用

注意：如果课件内容被截断了，请基于已有内容尽力分析。"""
        return self._call(prompt)

    # ─── 阶段 0.5：视觉模型分析图片型 PDF ───
    def analyze_pdf_vision(self, course_name: str, page_images: list[str],
                           exam_date: str, available_hours: int) -> str:
        """用视觉模型分析扫描版 PDF，读取图片内容并提取知识点"""
        text_prompt = f"""这是一份【{course_name}】课件的扫描图片（共{len(page_images)}页），考试日期：{exam_date}，可用复习时间：约{available_hours}小时。

请你像一位经验丰富的大学老师一样，逐页仔细审阅这份课件，然后完成以下工作：

【第一部分：知识点提取】
对每一页，提取其中包含的知识点，整理成树状结构：

### 第1页
- 知识点1：xxx（属于哪个主题）
- 知识点2：xxx
...

【第二部分：图表/电路图/公式专项分析】⚠️ 重点
课件中可能包含电路图、框图、波形图、公式推导等内容。请对每一个图表：
1. 描述图表画了什么（电路结构？信号流向？）
2. 提炼图表对应的考点——考试通常会怎么考这个图
3. 如果图中有公式，解释每个符号的物理含义和公式的适用条件
4. 指出学生容易在这个图上犯的错

【第三部分：知识点总览】
汇总所有知识点，用 Markdown 列表输出，标注：
- 重要度（⭐⭐⭐必考 / ⭐⭐常考 / ⭐偶尔）
- 难度（难/中/易）
- 是否需要看图理解（标注 🔍）

【第四部分：核心考点】
指出 3-5 个"绝对不能丢分"的核心考点，简要说明理由。

【第五部分：复习建议】
根据课件内容量估算复习时间是否够用（学生有{available_hours}小时），给出优先级排序。

注意：
- 手写笔记、打印体、电路符号都要尽力识别
- 某页内容不清晰就跳过，不要瞎猜
- 图表是重点，不要只读文字忽略图"""
        return chat_vision(text_prompt, page_images)

    # ─── 阶段 1：分析课程 ───
    def analyze_course(self, course_name: str, topics: str, exam_date: str, available_hours: int) -> str:
        """分析课程，生成知识地图"""
        prompt = f"""学生要突击复习【{course_name}】，考试日期：{exam_date}，可用复习时间：约{available_hours}小时。

课程涉及的知识范围（学生自己列的）：
{topics}

请完成以下工作：
1. 把这些知识点整理成树状结构（用 Markdown 列表），标注每个知识点的：
   - 重要度（⭐⭐⭐必考 / ⭐⭐常考 / ⭐偶尔）
   - 难度（难/中/易）
   - 建议时间分配
2. 估算总复习时间是否够用，给一个整体判断
3. 指出 3 个"绝对不能丢分"的核心考点"""
        return self._call(prompt)

    # ─── 阶段 2：出诊断题 ───
    def generate_diagnostic_quiz(self, course_name: str, knowledge_map: str, question_count: int = 4) -> str:
        """生成诊断题（自动截断过长的知识地图）"""
        # 截断知识地图避免 token 超限
        km = knowledge_map[:3000] if len(knowledge_map) > 3000 else knowledge_map
        prompt = f"""课程：【{course_name}】
知识点概要（精简自知识地图）：
{km}

请出 {question_count} 道诊断题，用来测试学生对核心考点的掌握程度。

要求：
- 前 2 道选择题（4 个选项），后 2 道简答题
- 覆盖不同难度和知识点
- 如果课程涉及电路图/图表，至少出 1 道读图分析题
- 每题标注【难度】【考点】【分值】
- 答案用 <!--答案:...--> 隐藏

格式：
### 第1题（选择题）【难度：中】【考点：XXX】【分值：10】
题目内容...
A. xxx  B. xxx  C. xxx  D. xxx
<!--答案:B-->
<!--答案:B-->
"""
        return self._call(prompt, temperature=0.8)

    # ─── 阶段 3：批改诊断 ───
    def grade_diagnostic(self, course_name: str, questions: str, user_answers: str) -> str:
        """批改诊断题，输出薄弱点分析"""
        prompt = f"""课程：【{course_name}】

诊断题和正确答案：
{questions}

学生的作答：
{user_answers}

请：
1. 逐题批改，给分，指出对/错在哪里（简洁）
2. 总分统计（满分100）
3. 根据错题分析薄弱知识点，列出"薄弱点清单"
4. 给出针对性建议：哪些知识点必须优先补"""
        return self._call(prompt)

    # ─── 阶段 4：生成突击计划 ───
    def generate_cram_plan(self, course_name: str, available_hours: int, weak_points: str,
                           knowledge_map: str) -> str:
        """生成突击复习计划"""
        km = knowledge_map[:2000] if len(knowledge_map) > 2000 else knowledge_map
        wp = weak_points[:1000] if len(weak_points) > 1000 else weak_points
        prompt = f"""课程：【{course_name}】
可用时间：{available_hours} 小时
知识地图（精简）：
{km}
薄弱点：
{wp}

请制定一份"极限突击计划"，要求：
1. 把{available_hours}小时拆成具体的时间块
2. 每个时间块明确：复习哪个知识点、怎么复习、预期产出
3. 薄弱点分配更多时间，但也要兼顾必考点的巩固
4. 最后留 30 分钟做"考前快速浏览清单"
5. 用 Markdown 表格呈现计划

风格：像学长/学姐帮你划重点，直接、高效。"""
        return self._call(prompt)

    # ─── 阶段 5：模拟考试 ───
    def generate_mock_exam(self, course_name: str, weak_points: str, question_count: int = 3) -> str:
        """生成模拟考题（重点考察薄弱点）"""
        prompt = f"""课程：【{course_name}】
学生薄弱点：{weak_points}

请出 {question_count} 道模拟考题。要求：
- 重点考察学生的薄弱知识点
- 1道选择题 + 1道简答题 + 1道综合应用题
- 题目要有期末考试的真实感
- 每题标注【难度】【考点】【分值】
- 隐藏答案用 <!--答案:...-->

这是考前最后一次检测，题目质量要高！"""
        return self._call(prompt, temperature=0.8)

    def grade_mock_exam(self, questions: str, user_answers: str) -> str:
        """批改模拟考"""
        prompt = f"""模拟考题和答案：
{questions}

学生作答：
{user_answers}

请：
1. 逐题批改打分
2. 总分 + 等级（稳过/有点悬/需要奇迹）
3. 给考前最后3条建议（简洁有力）"""
        return self._call(prompt)
