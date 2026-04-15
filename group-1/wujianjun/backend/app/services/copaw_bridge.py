"""
CoPaw Provider
对齐 08-系统架构与技术选型 §4 三级降级编排
职责：HTTP 调用外部 CoPaw API（禁止操作本地存储）
"""
import os
import time
from typing import Optional, Dict


class CoPawProvider:
    """CoPaw LLM 服务桥接"""
    
    def __init__(self):
        self.api_url = os.getenv("IRA_COPAW_API_URL", "")
        self.api_key = os.getenv("IRA_COPAW_API_KEY", "")
        self.timeout = 20  # 对齐 08 §4 超时配置
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.api_url and self.api_key)
    
    def ask(self, query: str, session_id: str) -> Optional[Dict]:
        """
        调用 CoPaw API 进行问答
        返回: {answer, model, response_time_ms} 或 None（降级）
        """
        if not self.is_configured():
            return None
        
        start_time = time.time()
        
        try:
            # TODO: 实现实际的 CoPaw API 调用
            # 当前为占位实现，返回 None 触发降级
            # import requests
            # response = requests.post(
            #     self.api_url,
            #     headers={"Authorization": f"Bearer {self.api_key}"},
            #     json={"query": query, "session_id": session_id},
            #     timeout=self.timeout
            # )
            # response.raise_for_status()
            # result = response.json()
            
            # 模拟成功响应（实际开发时替换为真实调用）
            # return {
            #     "answer": result.get("answer", ""),
            #     "model": result.get("model", "copaw-default"),
            #     "response_time_ms": int((time.time() - start_time) * 1000)
            # }
            
            return None  # 当前返回 None 触发降级
            
        except Exception:
            # 任何异常都静默降级
            return None
