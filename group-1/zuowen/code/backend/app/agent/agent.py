"""
Agent 编排层 — 对齐 Spec 08 §4 三级降级
CoPaw → 百炼 → Demo 链式降级
"""
import time
import os
from app.agent.copaw_bridge import call_copaw
from app.agent.bailian_qa import call_bailian


def ask(query, session_id=None):
    """
    三级降级编排（对齐 Spec 08 §4）:
      [1] CoPaw  → {source:'copaw',  llm:true}
      [2] 百炼   → {source:'bailian',llm:true}
      [3] Demo   → {source:'demo',   llm:false}
    """
    start = time.time()

    # ── Level 1: CoPaw ──
    if os.environ.get("IRA_COPAW_CHAT_URL"):
        result = call_copaw(query)
        if result is not None:
            elapsed = int((time.time() - start) * 1000)
            return {
                "answer": result["answer"],
                "llm_used": True,
                "model": result.get("model", "copaw"),
                "response_time_ms": elapsed,
                "answer_source": "copaw",
            }

    # ── Level 2: 百炼 DashScope ──
    if os.environ.get("DASHSCOPE_API_KEY"):
        result = call_bailian(query)
        if result is not None:
            elapsed = int((time.time() - start) * 1000)
            return {
                "answer": result["answer"],
                "llm_used": True,
                "model": result.get("model", "qwen-plus"),
                "response_time_ms": elapsed,
                "answer_source": "bailian",
            }

    # ── Level 3: Demo 兜底 ──
    elapsed = int((time.time() - start) * 1000)
    return {
        "answer": _demo_answer(query),
        "llm_used": False,
        "model": None,
        "response_time_ms": elapsed,
        "answer_source": "demo",
    }


def _demo_answer(query):
    """Demo 模式 — 纯字符串拼接，始终可用"""
    return (
        f"【演示回答】您的问题是：「{query}」\n\n"
        "当前处于离线演示模式，未配置任何 LLM 服务。\n"
        "请在 .env 中配置 IRA_COPAW_CHAT_URL 或 DASHSCOPE_API_KEY 以启用真实问答。"
    )


def get_capabilities():
    """能力探测 — 返回当前配置状态"""
    copaw_url = os.environ.get("IRA_COPAW_CHAT_URL", "")
    dashscope_key = os.environ.get("DASHSCOPE_API_KEY", "")
    return {
        "copaw_configured": bool(copaw_url),
        "bailian_configured": bool(dashscope_key),
        "model": "qwen-plus" if dashscope_key else None,
    }
