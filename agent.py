"""Agent 类：单个室友的人格、记忆、回复生成"""

from llm_client import chat
from memory import (
    ShortTermMemory,
    LongTermMemory,
    RelationshipTracker,
    parse_relationship_markers,
    clean_response,
)
from config import CONTEXT_ROUNDS


class Agent:
    """宿舍室友 Agent"""

    def __init__(self, name: str, mbti: str, system_prompt: str, emoji: str, color: str):
        self.name = name
        self.mbti = mbti
        self.system_prompt = system_prompt
        self.emoji = emoji
        self.color = color
        self.emotion = "😊 正常"

        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.relationships: RelationshipTracker | None = None

    def init_relationships(self, other_names: list[str]):
        """初始化好感度矩阵（需在所有 Agent 创建后调用）"""
        self.relationships = RelationshipTracker(self.name, other_names)

    def generate_response(self, recent_history: list[dict], event_context: str | None = None) -> str:
        """生成当前 Agent 的回复

        Args:
            recent_history: 最近对话历史，格式 [{"agent": str, "message": str}, ...]
            event_context: 当前注入的事件（如有）

        Returns:
            Agent 的回复文本（已清理标记）
        """
        messages = [{"role": "system", "content": self.system_prompt}]

        # 1. 注入长期记忆摘要
        ltm = self.long_term.get_summary()
        if ltm:
            messages.append({"role": "system", "content": ltm})

        # 2. 注入短期记忆
        stm = self.short_term.get_context_text(n=10)
        if stm:
            messages.append({"role": "system", "content": stm})

        # 3. 注入好感度上下文
        if self.relationships:
            rel = self.relationships.get_context()
            messages.append({"role": "system", "content": rel})

        # 4. 注入当前事件
        if event_context:
            messages.append({"role": "system", "content": f"⚡【刚刚发生的事】{event_context}\n请在你的回复中自然地对此事做出反应。"})

        # 5. 注入最近的宿舍对话
        context_rounds = recent_history[-(CONTEXT_ROUNDS * 2):]  # 保留最近几轮
        for entry in context_rounds:
            if entry["agent"] == self.name:
                messages.append({"role": "assistant", "content": entry["message"]})
            else:
                messages.append({"role": "user", "content": f"{entry['agent']}说：{entry['message']}"})

        # 6. 发言提示
        messages.append({
            "role": "user",
            "content": f"现在轮到{self.name}说话了。请以你的身份自然地回应（1-3句话），可以接话、开启新话题、或者简短回应。"
        })

        # 调用 LLM
        raw_response = chat(messages)

        # 解析好感度变化
        if self.relationships:
            markers = parse_relationship_markers(raw_response)
            for target_name, delta in markers:
                self.relationships.update(target_name, delta)

        # 清理回复中的标记
        clean = clean_response(raw_response)

        # 存入短期记忆
        self.short_term.add({"type": "speak", "agent": self.name, "content": clean})

        # 判断是否存入长期记忆
        self.long_term.add_if_important(clean)

        # 更新情绪状态（简单规则）
        self._update_emotion(clean)

        return clean

    def hear(self, speaker_name: str, message: str):
        """听到其他 Agent 的发言"""
        self.short_term.add({"type": "hear", "agent": speaker_name, "content": message})
        # 也检查是否需要存入长期记忆
        self.long_term.add_if_important(f"{speaker_name}说：{message}")

    def hear_event(self, event_text: str):
        """感知到事件"""
        self.short_term.add({"type": "event", "agent": "系统", "content": event_text})

    def _update_emotion(self, last_message: str):
        """根据发言内容简单更新情绪标签"""
        positive = any(w in last_message for w in ["哈哈", "开心", "好耶", "nice", "牛逼", "太爽", "喜欢", "谢谢"])
        negative = any(w in last_message for w in ["烦", "无语", "气死", "难受", "崩溃", "算了", "随便", "唉"])
        if positive and not negative:
            self.emotion = "😄 开心"
        elif negative and not positive:
            self.emotion = "😞 低落"
        elif "怼" in last_message or "毒舌" in last_message:
            self.emotion = "😏 嫌弃"
        else:
            self.emotion = "😊 正常"
