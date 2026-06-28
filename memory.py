"""记忆系统：短期记忆 + 长期记忆 + 关系追踪"""

import re
from datetime import datetime
from config import SHORT_TERM_SIZE, LONG_TERM_MAX


class ShortTermMemory:
    """短期记忆 — 环形缓冲区，存储最近 N 条事件"""

    def __init__(self, max_size: int = SHORT_TERM_SIZE):
        self.max_size = max_size
        self.memories: list[dict] = []

    def add(self, entry: dict):
        """添加一条记忆
        entry 格式: {"type": "speak"|"hear"|"event", "agent": str, "content": str}
        """
        entry["_time"] = datetime.now().strftime("%H:%M")
        self.memories.append(entry)
        if len(self.memories) > self.max_size:
            self.memories = self.memories[-self.max_size :]

    def get_all(self) -> list[dict]:
        return self.memories

    def get_recent(self, n: int) -> list[dict]:
        return self.memories[-n:]

    def get_context_text(self, n: int = 10) -> str:
        """将最近 n 条记忆格式化为文本"""
        recent = self.get_recent(n)
        if not recent:
            return ""
        lines = ["【你最近的记忆】"]
        for m in recent:
            t = m["_time"]
            if m["type"] == "speak":
                lines.append(f"[{t}] 你说：{m['content']}")
            elif m["type"] == "hear":
                lines.append(f"[{t}] {m['agent']}说：{m['content']}")
            elif m["type"] == "event":
                lines.append(f"[{t}] ⚡{m['content']}")
        return "\n".join(lines)


class LongTermMemory:
    """长期记忆 — 存储被标记为重要的事件"""

    def __init__(self, max_size: int = LONG_TERM_MAX):
        self.max_size = max_size
        self.memories: list[dict] = []

    def add(self, event: str, importance: int = 1, related_agents: list[str] | None = None):
        """添加长期记忆"""
        self.memories.append({
            "event": event,
            "importance": importance,
            "related": related_agents or [],
            "time": datetime.now().strftime("%m-%d %H:%M"),
        })
        # 按重要性排序，超出则淘汰最低分的
        self.memories.sort(key=lambda x: x["importance"], reverse=True)
        if len(self.memories) > self.max_size:
            self.memories = self.memories[:self.max_size]

    def add_if_important(self, message: str):
        """自动判断消息是否值得存入长期记忆"""
        keywords = ["吵架", "感动", "表白", "生日", "分手", "道歉", "秘密", "借钱",
                     "第一次", "终于", "永远", "最好", "最坏", "震惊", "没想到"]
        score = sum(1 for kw in keywords if kw in message)
        if score >= 2:
            self.add(message, importance=score)
            return True
        return False

    def get_summary(self) -> str:
        """返回长期记忆摘要，用于注入 prompt"""
        if not self.memories:
            return ""
        lines = ["【你记忆中的重要事件】"]
        for m in self.memories[:8]:  # 最多取 8 条
            lines.append(f"- [{m['time']}] {m['event']}（重要度:{m['importance']}）")
        return "\n".join(lines)

    def to_dict(self) -> list[dict]:
        return self.memories

    def from_dict(self, data: list[dict]):
        self.memories = data


class RelationshipTracker:
    """好感度追踪器 — 每个 Agent 维护对其他人的好感度"""

    def __init__(self, self_name: str, other_names: list[str]):
        self.self_name = self_name
        self.scores: dict[str, int] = {name: 50 for name in other_names}  # 初始 50，范围 0-100

    def update(self, name: str, delta: int):
        """更新对某人的好感度"""
        if name in self.scores:
            self.scores[name] = max(0, min(100, self.scores[name] + delta))

    def get_score(self, name: str) -> int:
        return self.scores.get(name, 50)

    def get_context(self) -> str:
        """生成好感度上下文文本"""
        lines = ["【你对室友的好感度（0-100）】"]
        for name, score in self.scores.items():
            emoji = "❤️" if score >= 70 else ("💛" if score >= 40 else "💔")
            lines.append(f"- {name}: {score}/100 {emoji}")
        return "\n".join(lines)

    def get_relationship_label(self, name: str) -> str:
        """获取关系标签"""
        s = self.get_score(name)
        if s >= 80:
            return "铁哥们"
        elif s >= 60:
            return "关系不错"
        elif s >= 40:
            return "普通室友"
        elif s >= 20:
            return "有点尴尬"
        else:
            return "水火不容"


def parse_relationship_markers(text: str) -> list[tuple[str, int]]:
    """从文本中解析好感度标记 <!--rel:名字:±N-->"""
    pattern = r"<!--rel:(\S+?):([+-]\d)-->"
    matches = re.findall(pattern, text)
    return [(name, int(delta)) for name, delta in matches]


def clean_response(text: str) -> str:
    """清除回复中的标记"""
    return re.sub(r"<!--rel:.*?-->", "", text).strip()
