"""
Agent 编排模块
实现三级降级策略：CoPaw → 百炼 → Demo
对齐 08-系统架构 §4
"""
import time
from typing import Dict, Any, Tuple
from copaw_bridge import CoPawBridge
from bailian_qa import BailianQA


class Agent:
    """投研问答助手 Agent"""
    
    def __init__(self):
        self.copaw = CoPawBridge()
        self.bailian = BailianQA()
    
    def ask(self, query: str, session_id: str) -> Dict[str, Any]:
        """处理问答请求，实现三级降级
        
        Args:
            query: 用户提问
            session_id: 会话 ID
            
        Returns:
            回答结果，包含 answer_source 标识来源
            {
                "answer": str,
                "llm_used": bool,
                "model": str | None,
                "response_time_ms": int,
                "answer_source": str  # copaw / bailian / demo
            }
        """
        start_time = time.time()
        
        # [1] 尝试 CoPaw
        if self.copaw.is_configured():
            result = self.copaw.ask(query, session_id)
            if result:
                return {
                    "answer": result["answer"],
                    "llm_used": True,
                    "model": result["model"],
                    "response_time_ms": int((time.time() - start_time) * 1000),
                    "answer_source": "copaw"
                }
        
        # [2] CoPaw 失败，尝试百炼
        if self.bailian.is_configured():
            result = self.bailian.ask(query, session_id)
            if result:
                return {
                    "answer": result["answer"],
                    "llm_used": True,
                    "model": result["model"],
                    "response_time_ms": int((time.time() - start_time) * 1000),
                    "answer_source": "bailian"
                }
        
        # [3] 全部失败，使用 Demo 模式兜底
        demo_answer = self._demo_answer(query)
        return {
            "answer": demo_answer,
            "llm_used": False,
            "model": None,
            "response_time_ms": int((time.time() - start_time) * 1000),
            "answer_source": "demo"
        }
    
    def _demo_answer(self, query: str) -> str:
        """生成 Demo 模式回答
        
        Args:
            query: 用户提问
            
        Returns:
            模拟回答
        """
        # 简单的关键词匹配返回模拟回答
        query_lower = query.lower()
        
        if "评级" in query or "rating" in query_lower:
            return "【Demo模式】根据最新研报，该股票评级为**买入**。目标价：¥50.00。主要逻辑：1）业绩稳健增长；2）行业龙头地位稳固；3）估值处于历史低位。\n\n> ⚠️ 当前处于离线演示模式，回答仅供参考。请配置 LLM 服务获取更准确的信息。"
        
        if "目标价" in query or "price target" in query_lower:
            return "【Demo模式】目标价：¥50.00（当前股价 ¥42.00，上涨空间 19%）。\n\n> ⚠️ 当前处于离线演示模式，回答仅供参考。请配置 LLM 服务获取更准确的信息。"
        
        if "对比" in query or "compare" in query_lower:
            return "【Demo模式】研报对比结果：\n\n| 券商 | 评级 | 目标价 | 发布日期 |\n|------|------|--------|----------|\n| 中金公司 | 买入 | ¥52.00 | 2026-04-10 |\n| 中信证券 | 增持 | ¥48.00 | 2026-04-08 |\n| 华泰证券 | 买入 | ¥55.00 | 2026-04-05 |\n\n> ⚠️ 当前处于离线演示模式，回答仅供参考。请配置 LLM 服务获取更准确的信息。"
        
        return f"【Demo模式】您的问题是：\"{query}\"\n\n这是一个演示回答。在实际配置 LLM 服务后，我将基于研报内容为您提供更准确的分析。\n\n> ⚠️ 当前处于离线演示模式，回答仅供参考。请配置 CoPaw 或百炼服务获取真实数据。"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """获取能力状态
        
        Returns:
            各 LLM 服务的可用性状态
        """
        return {
            "copaw_configured": self.copaw.is_configured(),
            "bailian_configured": self.bailian.is_configured(),
            "demo_available": True  # Demo 模式始终可用
        }


# 全局 Agent 实例
_agent_instance = None


def get_agent() -> Agent:
    """获取全局 Agent 实例（单例模式）"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = Agent()
    return _agent_instance
