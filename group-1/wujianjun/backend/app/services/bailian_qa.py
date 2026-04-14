"""
百炼 (DashScope) Provider
对齐 08-系统架构与技术选型 §4 三级降级编排
职责：HTTP 调用外部百炼 API（禁止操作本地存储）
"""
import os
import time
from typing import Optional, Dict


class BailianProvider:
    """百炼 DashScope LLM 服务桥接"""
    
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY", "")
        self.timeout = 120  # 对齐 08 §4 超时配置
        self.model = "qwen-turbo"  # 默认模型
    
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.api_key)
    
    def ask(self, query: str, session_id: str) -> Optional[Dict]:
        """
        调用百炼 API 进行问答
        返回: {answer, model, response_time_ms} 或 None（降级）
        """
        if not self.is_configured():
            return None
        
        start_time = time.time()
        
        try:
            # TODO: 实现实际的 DashScope API 调用
            # 当前为占位实现，返回 None 触发降级
            # import dashscope
            # dashscope.api_key = self.api_key
            # response = dashscope.Generation.call(
            #     model=self.model,
            #     prompt=query,
            #     timeout=self.timeout
            # )
            
            # 模拟成功响应（实际开发时替换为真实调用）
            # return {
            #     "answer": response.output.text,
            #     "model": self.model,
            #     "response_time_ms": int((time.time() - start_time) * 1000)
            # }
            
            return None  # 当前返回 None 触发降级
            
        except Exception:
            # 任何异常都静默降级
            return None
