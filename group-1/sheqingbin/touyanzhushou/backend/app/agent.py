"""
投研问答助手 - Agent 编排层
实现三级降级链：CoPaw → 百炼 → Demo
"""
import os
import time
from typing import Optional, Dict, Any, Tuple


class Agent:
    """
    LLM Agent 编排器
    负责三级降级链的调度和结果组装
    """
    
    def __init__(self):
        self.copaw_configured = self._check_copaw_config()
        self.bailian_configured = self._check_bailian_config()
    
    def _check_copaw_config(self) -> bool:
        """检查 CoPaw 是否已配置"""
        return bool(
            os.environ.get("IRA_COPAW_API_URL") and 
            os.environ.get("IRA_COPAW_API_KEY")
        )
    
    def _check_bailian_config(self) -> bool:
        """检查百炼是否已配置"""
        return bool(os.environ.get("DASHSCOPE_API_KEY"))
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        获取系统能力状态
        
        Returns:
            能力配置信息
        """
        return {
            "copaw_configured": self.copaw_configured,
            "bailian_configured": self.bailian_configured,
            "demo_available": True,  # Demo 始终可用
            "features": [
                "session_management",
                "qa_with_fallback",
                "report_comparison"
            ],
            "version": "0.1.0"
        }
    
    def ask(self, query: str, session_id: str) -> Dict[str, Any]:
        """
        提交问题并获取回答（带三级降级）
        
        Args:
            query: 用户问题
            session_id: 会话 ID
            
        Returns:
            回答结果，包含 answer, llm_used, model, response_time_ms, answer_source
        """
        start_time = time.time()
        
        # 第一级：CoPaw
        if self.copaw_configured:
            result = self._call_copaw(query, session_id)
            if result is not None:
                result["response_time_ms"] = int((time.time() - start_time) * 1000)
                return result
        
        # 第二级：百炼
        if self.bailian_configured:
            result = self._call_bailian(query, session_id)
            if result is not None:
                result["response_time_ms"] = int((time.time() - start_time) * 1000)
                return result
        
        # 第三级：Demo（兜底）
        result = self._call_demo(query, session_id)
        result["response_time_ms"] = int((time.time() - start_time) * 1000)
        return result
    
    def _call_copaw(self, query: str, session_id: str) -> Optional[Dict[str, Any]]:
        """
        调用 CoPaw 服务
        
        Args:
            query: 用户问题
            session_id: 会话 ID
            
        Returns:
            回答结果，失败返回 None（静默降级）
        """
        try:
            import requests
            
            url = os.environ.get("IRA_COPAW_API_URL")
            api_key = os.environ.get("IRA_COPAW_API_KEY")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": query,
                "session_id": session_id
            }
            
            response = requests.post(
                url, 
                headers=headers, 
                json=payload, 
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "answer": data.get("answer", ""),
                    "llm_used": True,
                    "model": data.get("model", "copaw-default"),
                    "answer_source": "copaw"
                }
            
            return None
            
        except Exception:
            # 静默降级
            return None
    
    def _call_bailian(self, query: str, session_id: str) -> Optional[Dict[str, Any]]:
        """
        调用百炼（DashScope）服务
        
        Args:
            query: 用户问题
            session_id: 会话 ID
            
        Returns:
            回答结果，失败返回 None（静默降级）
        """
        try:
            import requests
            
            api_key = os.environ.get("DASHSCOPE_API_KEY")
            model = os.environ.get("DASHSCOPE_MODEL", "qwen-turbo")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "input": {
                    "messages": [
                        {"role": "system", "content": "你是一个专业的投研助手，擅长分析研报和回答投资相关问题。"},
                        {"role": "user", "content": query}
                    ]
                }
            }
            
            response = requests.post(
                "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                output = data.get("output", {})
                text = output.get("text", "")
                
                return {
                    "answer": text,
                    "llm_used": True,
                    "model": model,
                    "answer_source": "bailian"
                }
            
            return None
            
        except Exception:
            # 静默降级
            return None
    
    def _call_demo(self, query: str, session_id: str) -> Dict[str, Any]:
        """
        Demo 模式（离线演示）
        当所有 LLM 都不可用时返回模拟回答
        
        Args:
            query: 用户问题
            session_id: 会话 ID
            
        Returns:
            模拟回答结果
        """
        # 简单的关键词匹配生成模拟回答
        query_lower = query.lower()
        
        if "对比" in query or "比较" in query:
            answer = self._generate_comparison_demo(query)
        elif "分析" in query or "怎么样" in query:
            answer = self._generate_analysis_demo(query)
        else:
            answer = self._generate_general_demo(query)
        
        return {
            "answer": answer,
            "llm_used": False,
            "model": None,
            "answer_source": "demo"
        }
    
    def _generate_comparison_demo(self, query: str) -> str:
        """生成对比类模拟回答"""
        return """【离线演示模式】

根据您的对比需求，我为您整理了以下信息：

| 券商 | 评级 | 目标价 | 关键观点 |
|------|------|--------|----------|
| 中信证券 | 买入 | ¥158.00 | 业绩超预期，新能源业务增长强劲 |
| 华泰证券 | 增持 | ¥152.00 | 毛利率改善，市场份额稳步提升 |
| 中金公司 | 推荐 | ¥155.00 | 技术壁垒高，长期成长逻辑清晰 |

**综合观点**：
多数券商看好该公司发展前景，平均目标价约 ¥155。主要关注点集中在：
1. 新能源业务的高速增长
2. 毛利率持续改善
3. 技术壁垒带来的竞争优势

> ⚠️ 此为演示数据，实际分析请配置 LLM 服务后获取真实研报对比结果。"""
    
    def _generate_analysis_demo(self, query: str) -> str:
        """生成分析类模拟回答"""
        return """【离线演示模式】

基于您的问题，我为您提供以下分析：

**核心观点**：
1. **行业地位**：该公司在细分领域处于龙头地位，市场份额约 25%
2. **财务表现**：近三年营收复合增长率 18%，净利润率稳定在 12% 左右
3. **成长驱动**：主要受益于新能源政策支持和下游需求增长

**风险提示**：
- 原材料价格波动风险
- 行业竞争加剧风险
- 政策变化风险

**投资建议**：
建议关注公司季度业绩发布，以及新产能投放进度。

> ⚠️ 此为演示回答，实际分析请配置 LLM 服务后获取真实研报解读。"""
    
    def _generate_general_demo(self, query: str) -> str:
        """生成通用模拟回答"""
        return """【离线演示模式】

您好！我已收到您的问题：

**"{}"**

目前系统处于离线演示模式，可以回答一些基础的投研问题。主要功能包括：

1. **研报对比**：支持多家券商研报观点对比
2. **投资分析**：提供公司基本面分析框架
3. **市场解读**：解读行业趋势和政策影响

如需获取真实研报分析和数据，请配置以下服务之一：
- CoPaw 桥接服务
- 阿里云百炼（DashScope）API

> ⚠️ 此为演示回答，配置 LLM 服务后可获取基于真实研报的智能回答。""".format(query)


# 全局 Agent 实例（单例模式）
_agent_instance: Optional[Agent] = None


def get_agent() -> Agent:
    """获取 Agent 实例（单例）"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = Agent()
    return _agent_instance
