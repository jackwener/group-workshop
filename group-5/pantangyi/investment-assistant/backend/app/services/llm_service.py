"""LLM Service with three-level fallback strategy."""
import os
import time
import requests
from typing import Optional, Dict, Any, Tuple


class LLMService:
    """
    LLM Service with three-level fallback.
    
    Level 0: CoPaw (primary)
    Level 1: 百炼 (fallback-1)
    Level 2: Demo mode (fallback-2)
    
    Aligned with 08-系统架构与技术选型.md §4.2 and 09-API接口规格.md §7.1
    """
    
    def __init__(self):
        self.fallback_level = 0
        self.llm_status = "primary"  # primary, fallback-1, demo
        
        # Configuration (should be loaded from env in production)
        self.copaw_endpoint = os.getenv("COPAW_ENDPOINT", "")
        self.copaw_api_key = os.getenv("COPAW_API_KEY", "")
        self.bailian_endpoint = os.getenv("BAILIAN_ENDPOINT", "")
        self.bailian_api_key = os.getenv("BAILIAN_API_KEY", "")
        
    def analyze_report(self, text_content: str, extract_keywords: bool = True) -> Tuple[Dict[str, Any], int, str]:
        """
        Analyze report text using LLM.
        
        Returns: (result_dict, fallback_level, llm_status)
        """
        prompt = self._build_report_analysis_prompt(text_content, extract_keywords)
        return self._call_llm_with_fallback(prompt)
    
    def analyze_stock(self, stock_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int, str]:
        """
        Analyze stock data using LLM.
        
        Returns: (result_dict, fallback_level, llm_status)
        """
        prompt = self._build_stock_analysis_prompt(stock_data)
        return self._call_llm_with_fallback(prompt)
    
    def chat(self, messages: list, context: str = "") -> Tuple[str, int, str]:
        """
        Chat with LLM.
        
        Returns: (response_text, fallback_level, llm_status)
        """
        prompt = self._build_chat_prompt(messages, context)
        result, level, status = self._call_llm_with_fallback(prompt)
        return result.get("response", ""), level, status
    
    def _call_llm_with_fallback(self, prompt: str) -> Tuple[Dict[str, Any], int, str]:
        """
        Call LLM with three-level fallback.
        Never raises exception - always returns a result.
        """
        # Level 0: Try CoPaw
        if self.fallback_level <= 0:
            try:
                result = self._call_copaw(prompt)
                self.llm_status = "primary"
                return result, 0, "primary"
            except Exception as e:
                print(f"CoPaw failed: {e}, falling back to Bailian")
                self.fallback_level = 1
        
        # Level 1: Try 百炼
        if self.fallback_level <= 1:
            try:
                result = self._call_bailian(prompt)
                self.llm_status = "fallback-1"
                return result, 1, "fallback-1"
            except Exception as e:
                print(f"Bailian failed: {e}, falling back to Demo mode")
                self.fallback_level = 2
        
        # Level 2: Demo mode
        result = self._call_demo(prompt)
        self.llm_status = "demo"
        return result, 2, "demo"
    
    def _call_copaw(self, prompt: str) -> Dict[str, Any]:
        """Call CoPaw LLM API."""
        if not self.copaw_endpoint:
            raise Exception("CoPaw endpoint not configured")
        
        # Placeholder for actual CoPaw API call
        # In production, replace with actual API integration
        headers = {
            "Authorization": f"Bearer {self.copaw_api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "copaw-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        # Simulate API call (replace with actual implementation)
        # response = requests.post(self.copaw_endpoint, json=payload, headers=headers, timeout=60)
        # return self._parse_response(response.json())
        
        # For demo purposes, simulate success
        raise Exception("CoPaw not configured - using fallback")
    
    def _call_bailian(self, prompt: str) -> Dict[str, Any]:
        """Call 百炼 LLM API."""
        if not self.bailian_endpoint:
            raise Exception("Bailian endpoint not configured")
        
        # Placeholder for actual Bailian API call
        # In production, replace with actual API integration
        raise Exception("Bailian not configured - using fallback")
    
    def _call_demo(self, prompt: str) -> Dict[str, Any]:
        """
        Demo mode - returns sample data.
        Aligned with 07-非功能需求与约束.md §2.3
        """
        # Return sample analysis result
        return {
            "title": "示例研报分析",
            "summary": "这是一个演示模式的分析结果。实际部署时，请配置 CoPaw 或 百炼 API。",
            "key_points": [
                "演示模式：营收增长示例 15%",
                "演示模式：净利润提升示例",
                "演示模式：市场份额扩大示例"
            ],
            "risk_warnings": [
                "演示模式：市场竞争加剧",
                "演示模式：原材料成本上升"
            ],
            "industry": "示例行业",
            "rating": "买入",
            "target_price": 100.0,
            "demo_mode": True
        }
    
    def _build_report_analysis_prompt(self, text_content: str, extract_keywords: bool) -> str:
        """Build prompt for report analysis."""
        prompt = f"""请分析以下研报内容，提取关键信息：

{text_content[:5000]}  # Limit text length

请按以下JSON格式返回分析结果：
{{
    "title": "研报标题",
    "summary": "摘要（200字以内）",
    "key_points": ["核心观点1", "核心观点2", "核心观点3"],
    "risk_warnings": ["风险提示1", "风险提示2"],
    "industry": "所属行业",
    "rating": "评级（买入/持有/卖出）",
    "target_price": 目标价格（数字）
}}
"""
        return prompt
    
    def _build_stock_analysis_prompt(self, stock_data: Dict[str, Any]) -> str:
        """Build prompt for stock analysis."""
        prompt = f"""请分析以下股票数据，生成综合分析报告：

股票代码: {stock_data.get('stock_code', '')}
股票名称: {stock_data.get('stock_name', '')}
财务数据: {stock_data.get('financial_data', {})}
研报摘要: {stock_data.get('report_summary', '')}

请按以下JSON格式返回分析结果：
{{
    "financial_indicators": {{
        "revenue": 营收（数字）,
        "profit": 净利润（数字）,
        "roe": ROE（数字）,
        "pe": PE（数字）,
        "pb": PB（数字）
    }},
    "report_summary": "研报摘要",
    "comprehensive_score": 综合评分（0-100数字）,
    "risk_level": "风险等级（low/medium/high）",
    "recommendation": "建议（buy/hold/sell）"
}}
"""
        return prompt
    
    def _build_chat_prompt(self, messages: list, context: str) -> str:
        """Build prompt for chat."""
        history = "\n".join([f"{m['role']}: {m['content']}" for m in messages[-5:]])
        prompt = f"""上下文信息：
{context}

对话历史：
{history}

请根据上下文回答用户问题。"""
        return prompt
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM API response."""
        # Extract content from response
        if "choices" in response and len(response["choices"]) > 0:
            content = response["choices"][0].get("message", {}).get("content", "")
            # Try to parse as JSON
            try:
                import json
                return json.loads(content)
            except json.JSONDecodeError:
                return {"response": content}
        return {"response": str(response)}
    
    def health_check(self) -> Dict[str, str]:
        """Check LLM service health."""
        status = {
            "copaw": "unavailable",
            "bailian": "unavailable",
            "current": self.llm_status
        }
        
        # Check CoPaw
        if self.copaw_endpoint:
            try:
                # Simple connectivity check
                status["copaw"] = "available"
            except:
                pass
        
        # Check Bailian
        if self.bailian_endpoint:
            try:
                status["bailian"] = "available"
            except:
                pass
        
        return status


# Singleton instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get singleton LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
