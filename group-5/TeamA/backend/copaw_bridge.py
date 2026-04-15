"""
CoPaw 桥接 Provider — 对齐 Spec 08 §4 [1]
超时 20s，失败返回 None 静默降级
"""

import os
import requests


class CoPawBridge:
    """CoPaw LLM 桥接调用"""

    TIMEOUT = 20  # 对齐 Spec 08 §4

    def ask(self, query, file_content=None):
        base_url = os.environ.get("IRA_COPAW_BASE_URL")
        if not base_url:
            return None

        # TODO: 实现真实 CoPaw API 调用
        # 对齐 Spec 08 §2 Provider 层：HTTP 调用外部 LLM API
        try:
            payload = {"query": query}
            if file_content:
                payload["context"] = file_content

            resp = requests.post(
                f"{base_url}/chat",
                json=payload,
                timeout=self.TIMEOUT,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "answer": data.get("answer", ""),
                "llm_used": True,
                "model": "copaw-bridge",
                "answer_source": "copaw",
            }
        except Exception:
            return None  # 静默降级


# 单例
copaw_bridge = CoPawBridge()
