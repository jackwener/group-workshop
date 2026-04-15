import time
import logging

import copaw_bridge
import bailian_qa

logger = logging.getLogger(__name__)


class CoPawAgent:
    def __init__(self, storage):
        self.storage = storage

    def ask(self, query, session_id):
        start = time.time()
        answer = None
        answer_source = "demo"
        llm_used = False
        model = None

        # Level 1: CoPaw
        if copaw_bridge.is_available():
            logger.info("Trying CoPaw...")
            result = copaw_bridge.ask(query)
            if result is not None:
                answer = result
                answer_source = "copaw"
                llm_used = True
                model = "copaw"

        # Level 2: Bailian (only if CoPaw didn't succeed)
        if answer is None and bailian_qa.is_available():
            logger.info("CoPaw unavailable, trying Bailian...")
            result = bailian_qa.ask(query)
            if result is not None:
                answer = result
                answer_source = "bailian"
                llm_used = True
                model = "qwen-max"

        # Level 3: Demo (always available)
        if answer is None:
            logger.info("All LLM providers unavailable, using demo mode")
            answer = (
                f"【演示回答】关于「{query}」的分析：\n\n"
                f"这是一个离线演示回答。在实际使用中，系统会通过 AI 大模型为您提供专业的投研分析。\n\n"
                f"当前处于演示模式，您可以通过配置 CoPaw 或百炼 API 密钥来启用在线问答功能。"
            )
            answer_source = "demo"
            llm_used = False
            model = None

        response_time_ms = int((time.time() - start) * 1000)

        # Save record
        record = self.storage.add_record(
            session_id=session_id,
            query=query,
            answer=answer,
            llm_used=llm_used,
            model=model,
            response_time_ms=response_time_ms,
            answer_source=answer_source,
        )

        # Auto-rename on first question
        session = self.storage.get_session_by_id(session_id)
        if session and session.get("query_count") == 1:
            new_title = query[:20] + ("..." if len(query) > 20 else "")
            self.storage.update_session_title(session_id, new_title)

        return {
            "record_id": record["record_id"],
            "answer": answer,
            "llm_used": llm_used,
            "model": model,
            "response_time_ms": response_time_ms,
            "answer_source": answer_source,
            "timestamp": record["timestamp"],
            "sources": record["sources"],
        }
