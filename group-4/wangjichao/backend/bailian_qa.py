import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BailianQA:
    """百炼 DashScope Provider - 调用阿里云百炼大模型 API"""

    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY", "")
        self.model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    def is_configured(self) -> bool:
        """检测百炼是否已配置"""
        return bool(self.api_key)

    def ask(self, query: str) -> Optional[dict]:
        """
        调用百炼 DashScope API 进行问答

        Args:
            query: 用户提问

        Returns:
            {"answer": str, "model": str} 或 None（失败时静默返回）
        """
        if not self.is_configured():
            return None

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "input": {
                    "messages": [
                        {"role": "user", "content": query}
                    ]
                }
            }

            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=120
            )
            response.raise_for_status()

            data = response.json()
            # DashScope 响应格式
            answer = (data.get("output", {}).get("text") or
                      data.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", ""))

            if answer:
                return {
                    "answer": answer,
                    "model": self.model
                }
            return None

        except Exception as e:
            logger.warning(f"Bailian call failed: {e}")
            return None
