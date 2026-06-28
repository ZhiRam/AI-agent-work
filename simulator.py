"""模拟引擎：多智能体对话调度"""

import random
from agent import Agent
from prompts import AGENT_CONFIGS
from events import get_random_event


class Simulator:
    """宿舍模拟器 — 管理所有 Agent 和对话流"""

    def __init__(self):
        self.agents: dict[str, Agent] = {}
        self.history: list[dict] = []       # 完整对话历史
        self.display_history: list[dict] = [] # 用于展示的历史（含格式信息）
        self.turn_count = 0
        self.current_speaker: str | None = None
        self._init_agents()

    def _init_agents(self):
        """初始化 4 个室友"""
        for name, config in AGENT_CONFIGS.items():
            agent = Agent(
                name=name,
                mbti=config["mbti"],
                system_prompt=config["prompt"],
                emoji=config["emoji"],
                color=config["color"],
            )
            self.agents[name] = agent

        # 建立关系网
        all_names = list(self.agents.keys())
        for name, agent in self.agents.items():
            other_names = [n for n in all_names if n != name]
            agent.init_relationships(other_names)

    def run_turn(self, speaker_name: str | None = None, event_text: str | None = None) -> dict | None:
        """执行一轮对话

        Args:
            speaker_name: 指定发言者，None 则自动选择
            event_text: 注入的事件文本

        Returns:
            {"agent": str, "message": str, "emoji": str, "color": str} 或 None
        """
        # 选择发言者
        if speaker_name and speaker_name in self.agents:
            speaker = self.agents[speaker_name]
        else:
            speaker = self._pick_next_speaker()

        self.current_speaker = speaker.name

        # 生成回复
        response = speaker.generate_response(
            recent_history=self.history,
            event_context=event_text,
        )

        # 存入历史
        entry = {"agent": speaker.name, "message": response}
        self.history.append(entry)

        display_entry = {
            "agent": speaker.name,
            "message": response,
            "emoji": speaker.emoji,
            "color": speaker.color,
            "mbti": speaker.mbti,
            "turn": self.turn_count,
        }
        self.display_history.append(display_entry)

        # 其他 Agent 听到这句话
        for name, agent in self.agents.items():
            if name != speaker.name:
                agent.hear(speaker.name, response)

        self.turn_count += 1
        return display_entry

    def run_multi_turns(self, n: int = 5) -> list[dict]:
        """连续运行 N 轮对话"""
        results = []
        for _ in range(n):
            result = self.run_turn()
            if result:
                results.append(result)
        return results

    def inject_event(self, event_text: str) -> dict | None:
        """注入一个事件，触发一轮对话"""
        # 所有 Agent 感知到事件
        for agent in self.agents.values():
            agent.hear_event(event_text)

        # 事件作为特殊消息展示
        event_display = {
            "agent": "📢 系统",
            "message": f"⚡ {event_text}",
            "emoji": "📢",
            "color": "#FF9800",
            "mbti": "",
            "turn": self.turn_count,
            "is_event": True,
        }
        self.display_history.append(event_display)

        # 触发一轮对话（Agent 对此事件做出反应）
        result = self.run_turn(event_text=event_text)
        return event_display

    def user_speak(self, agent_name: str, message: str) -> dict | None:
        """用户附身某个 Agent 发言"""
        if agent_name not in self.agents:
            return None

        agent = self.agents[agent_name]

        # 作为该 Agent 的发言存入
        entry = {"agent": agent_name, "message": message}
        self.history.append(entry)

        display_entry = {
            "agent": agent_name,
            "message": message,
            "emoji": "👤",  # 用户附身标记
            "color": agent.color,
            "mbti": agent.mbti,
            "turn": self.turn_count,
            "is_user": True,
        }
        self.display_history.append(display_entry)

        # 存入该 Agent 的记忆
        agent.short_term.add({"type": "speak", "agent": agent_name, "content": message})

        # 其他 Agent 听到
        for name, a in self.agents.items():
            if name != agent_name:
                a.hear(agent_name, message)

        self.turn_count += 1
        return display_entry

    def random_event(self) -> dict:
        """触发一个随机事件"""
        event = get_random_event()
        return self.inject_event(event["text"])

    def _pick_next_speaker(self) -> Agent:
        """选择下一个发言者"""
        # 第一轮随机选
        if self.turn_count == 0:
            return random.choice(list(self.agents.values()))

        agent_names = list(self.agents.keys())

        # 简单策略：随机选择，但避免同一个人连续发言
        if self.current_speaker and len(agent_names) > 1:
            pool = [n for n in agent_names if n != self.current_speaker]
            name = random.choice(pool)
        else:
            name = random.choice(agent_names)

        return self.agents[name]

    def get_relationship_matrix(self) -> dict:
        """获取完整的好感度矩阵"""
        matrix = {}
        for name, agent in self.agents.items():
            if agent.relationships:
                matrix[name] = {
                    "scores": agent.relationships.scores.copy(),
                    "labels": {n: agent.relationships.get_relationship_label(n)
                              for n in agent.relationships.scores},
                }
        return matrix

    def reset(self):
        """重置模拟器"""
        self.history = []
        self.display_history = []
        self.turn_count = 0
        self.current_speaker = None
        self._init_agents()
