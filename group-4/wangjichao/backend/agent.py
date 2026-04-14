import logging
from copaw_bridge import CoPawBridge
from bailian_qa import BailianQA

logger = logging.getLogger(__name__)


class CoPawAgent:
    """三级降级编排：CoPaw → 百炼 → Demo"""

    def __init__(self):
        self.copaw = CoPawBridge()
        self.bailian = BailianQA()

    def ask(self, query: str, session_id: str = "") -> dict:
        """
        三级降级编排：
        1. CoPaw（if configured）→ answer_source='copaw', llm_used=True
        2. 百炼（if configured）→ answer_source='bailian', llm_used=True
        3. Demo（always available）→ answer_source='demo', llm_used=False

        返回：
        {
            "answer": str,
            "answer_source": "copaw" | "bailian" | "demo",
            "llm_used": bool,
            "model": str | None
        }

        降级规则：
        - 不可跳级：必须按 1→2→3 顺序
        - 静默降级：每级失败时自动尝试下一级，不抛异常
        - Demo 始终可用，永不失败
        """

        # 第一级：CoPaw
        if self.copaw.is_configured():
            try:
                result = self.copaw.ask(query, session_id)
                if result and result.get("answer"):
                    logger.info("CoPaw answered successfully")
                    return {
                        "answer": result["answer"],
                        "answer_source": "copaw",
                        "llm_used": True,
                        "model": result.get("model", "copaw"),
                    }
            except Exception as e:
                logger.warning(f"CoPaw failed, degrading to Bailian: {e}")

        # 第二级：百炼
        if self.bailian.is_configured():
            try:
                result = self.bailian.ask(query)
                if result and result.get("answer"):
                    logger.info("Bailian answered successfully")
                    return {
                        "answer": result["answer"],
                        "answer_source": "bailian",
                        "llm_used": True,
                        "model": result.get("model", "qwen-plus"),
                    }
            except Exception as e:
                logger.warning(f"Bailian failed, degrading to Demo: {e}")

        # 第三级：Demo（始终可用）
        logger.info("Using Demo mode")
        return {
            "answer": f"【离线演示】您询问了：{query}。这是一个演示回复，实际使用请配置 LLM 服务。",
            "answer_source": "demo",
            "llm_used": False,
            "model": None,
        }
