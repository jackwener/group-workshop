import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CoPawBridge:
    """CoPaw 桥接 Provider - 通过 HTTP 调用 CoPaw 外部 API"""

    def __init__(self):
        self.base_url = os.getenv("IRA_COPAW_BASE_URL", "")
        self.ask_url = os.getenv("IRA_COPAW_ASK_URL", "")

    def is_configured(self) -> bool:
        """检测 CoPaw 是否已配置（两个环境变量都非空）"""
        return bool(self.base_url) and bool(self.ask_url)

    def ask(self, query: str, session_id: str = "") -> Optional[dict]:
        """
        调用 CoPaw API 进行问答

        Args:
            query: 用户提问
            session_id: 会话 ID

        Returns:
            {"answer": str, "model": "copaw"} 或 None（失败时静默返回）
        """
        if not self.is_configured():
            return None

        try:
            url = self.ask_url
            payload = {
                "query": query,
                "session_id": session_id
            }
            response = requests.post(url, json=payload, timeout=20)
            response.raise_for_status()

            data = response.json()
            answer = data.get("answer") or data.get("data", {}).get("answer", "")

            if answer:
                return {
                    "answer": answer,
                    "model": "copaw"
                }
            return None

        except Exception as e:
            logger.warning(f"CoPaw call failed: {e}")
            return None
