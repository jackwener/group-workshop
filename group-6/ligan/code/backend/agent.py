import os
import time
from backend.bailian_qa import BailianQA
from backend.copaw_bridge import CoPawBridge


class CoPawAgent:
    def __init__(self, storage):
        self.storage = storage
        self.copaw = CoPawBridge()
        self.bailian = BailianQA()

    def _demo_answer(self, query):
        return {
            "answer": f"[离线演示] 您询问了：{query}。当前为演示模式，请配置 LLM 密钥获取真实回答。",
            "llm_used": False,
            "model": None,
            "answer_source": "demo",
        }

    def ask(self, query, session_id):
        start = time.time()

        # [1] CoPaw
        result = self.copaw.ask(query, session_id) if self.copaw.configured else None

        # [2] Bailian
        if result is None:
            result = self.bailian.ask(query) if self.bailian.configured else None

        # [3] Demo
        if result is None:
            result = self._demo_answer(query)

        result["response_time_ms"] = int((time.time() - start) * 1000)

        # Persist record
        self.storage.add_record(
            session_id=session_id,
            query=query,
            answer=result["answer"],
            llm_used=result["llm_used"],
            model=result["model"],
            response_time_ms=result["response_time_ms"],
            answer_source=result["answer_source"],
        )
        return result
