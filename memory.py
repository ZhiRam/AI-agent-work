"""记忆系统：追踪学习进度"""


class MemoryStore:
    """存储课程信息、薄弱点、答题历史"""

    def __init__(self):
        self.course_info: dict = {}
        self.knowledge_map: str = ""
        self.weak_points: str = ""
        self.quiz_history: list[dict] = []
        self.study_plan: str = ""
        self.mock_exam_history: list[dict] = []
        self.total_score: int = 0

    def reset(self):
        self.__init__()
