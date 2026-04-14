"""
CoPaw 桥接 Provider — 对齐 Spec 08 §4
检测 IRA_COPAW_*_URL → 20s 超时 → 失败返回 None 静默降级
"""
import os
import requests


def call_copaw(query):
    """
    调用 CoPaw 桥接服务。
    成功返回 {"answer": ..., "model": ...}
    失败返回 None（静默降级）
    """
    chat_url = os.environ.get("IRA_COPAW_CHAT_URL", "")
    if not chat_url:
        return None

    try:
        resp = requests.post(
            chat_url,
            json={"query": query},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "answer": data.get("answer", ""),
            "model": data.get("model", "copaw"),
        }
    except Exception:
        # 静默降级 — 返回 None
        return None
