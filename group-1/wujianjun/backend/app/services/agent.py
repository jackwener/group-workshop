"""
Agent 层 - 三级降级编排
对齐 08-系统架构与技术选型 §4 三级降级编排
职责：降级编排、结果组装（禁止感知 HTTP 请求/响应）

降级链路：
ask(query, session_id)
  ├─[1] CoPaw  → {source:"copaw",  llm:true}
  ├─[2] 百炼   → {source:"bailian",llm:true}
  └─[3] Demo   → {source:"demo",   llm:false}
"""
import time
from typing import Dict, Optional

from app.services.copaw_bridge import CoPawProvider
from app.services.bailian_qa import BailianProvider


class CoPawAgent:
    """
    投研问答 Agent
    实现三级降级：CoPaw → 百炼 → Demo
    """
    
    def __init__(self):
        self.copaw = CoPawProvider()
        self.bailian = BailianProvider()
    
    def get_capabilities(self) -> Dict:
        """
        获取当前能力配置状态
        对齐 09-API接口规格 §3 GET /capabilities
        """
        copaw_configured = self.copaw.is_configured()
        bailian_configured = self.bailian.is_configured()
        
        # 确定当前模式
        if copaw_configured:
            mode = "copaw"
            model = "copaw-model"  # 实际应从配置或检测获取
        elif bailian_configured:
            mode = "bailian"
            model = self.bailian.model
        else:
            mode = "demo"
            model = None
        
        return {
            "copaw_configured": copaw_configured,
            "bailian_configured": bailian_configured,
            "model": model,
            "mode": mode
        }
    
    def ask(self, query: str, session_id: str) -> Dict:
        """
        执行问答，按三级降级顺序尝试
        对齐 09-API接口规格 §4 POST /ask
        
        返回格式：
        {
            "answer": str,
            "llm_used": bool,
            "model": str|None,
            "response_time_ms": int,
            "answer_source": "copaw"|"bailian"|"demo"
        }
        """
        start_time = time.time()
        
        # [1] 尝试 CoPaw
        result = self.copaw.ask(query, session_id)
        if result:
            result["llm_used"] = True
            result["answer_source"] = "copaw"
            return result
        
        # [2] 降级到百炼
        result = self.bailian.ask(query, session_id)
        if result:
            result["llm_used"] = True
            result["answer_source"] = "bailian"
            return result
        
        # [3] 降级到 Demo（始终可用）
        return self._demo_answer(query, start_time)
    
    def _demo_answer(self, query: str, start_time: float) -> Dict:
        """
        Demo 模式回答（纯字符串拼接，无外部依赖）
        对齐 08 §4 Demo 模式始终可用
        """
        demo_response = (
            f"【演示回复】您的问题是：\"{query[:50]}{'...' if len(query) > 50 else ''}\"\n\n"
            "这是一个离线演示回复。系统未配置有效的 LLM API 密钥（CoPaw 或百炼）。\n"
            "配置 API 密钥后可获得基于研报的真实智能回答。"
        )
        
        return {
            "answer": demo_response,
            "llm_used": False,
            "model": None,
            "response_time_ms": int((time.time() - start_time) * 1000),
            "answer_source": "demo"
        }
