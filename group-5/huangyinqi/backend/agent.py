"""Agent - Three-level degradation chain: CoPaw -> Bailian -> Demo."""

from copaw_bridge import CoPawBridge
from bailian_qa import BailianQA


class Agent:
    """T-026: Agent with three-level degradation chain."""

    def __init__(self):
        self.copaw = CoPawBridge()
        self.bailian = BailianQA()

    def ask(self, query, session_id=None):
        """
        Try CoPaw -> Bailian -> Demo in order.
        Returns dict with answer, llm_used, model, answer_source.
        """
        # Level 1: CoPaw
        if self.copaw.configured:
            result = self.copaw.ask(query, session_id)
            if result:
                return {
                    "answer": result["answer"],
                    "llm_used": True,
                    "model": result["model"],
                    "answer_source": "copaw",
                }

        # Level 2: Bailian
        if self.bailian.configured:
            result = self.bailian.ask(query, session_id)
            if result:
                return {
                    "answer": result["answer"],
                    "llm_used": True,
                    "model": result["model"],
                    "answer_source": "bailian",
                }

        # Level 3: Demo (always available)
        return self._demo_answer(query)

    @staticmethod
    def _demo_answer(query):
        """Demo mode - pure string concatenation, no external dependency."""
        answer = (
            f"[离线演示模式] 您的问题是：「{query}」\n\n"
            "当前系统未配置AI服务（CoPaw/百炼），正在使用离线演示模式。\n"
            "请配置 IRA_COPAW_CHAT_URL 或 DASHSCOPE_API_KEY 环境变量以启用AI问答功能。\n\n"
            "以下是模拟回答：\n"
            "根据相关研究报告分析，该问题涉及多个方面的考量。"
            "建议关注以下几个要点：\n"
            "1. 市场趋势与行业动态\n"
            "2. 公司基本面分析\n"
            "3. 风险因素评估\n"
            "4. 投资建议与目标价预测"
        )
        return {
            "answer": answer,
            "llm_used": False,
            "model": None,
            "answer_source": "demo",
        }
