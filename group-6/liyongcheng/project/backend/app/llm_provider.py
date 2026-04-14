"""LLM提供者模块"""
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from app.config import config


class BaseLLMProvider(ABC):
    """LLM提供者基类"""
    
    @abstractmethod
    def parse_report(self, content: str) -> Optional[Dict[str, Any]]:
        """
        解析研报内容
        
        Args:
            content: 研报文本内容
            
        Returns:
            解析结果字典，包含：
            - title: 研报标题
            - subject_name: 研究对象名称
            - subject_code: 研究对象代码
            - author: 券商名称
            - rating: 评级
            - trend: 方向（bullish/bearish/neutral）
            - target_price: 目标价
            - summary: 核心观点
            """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查提供者是否可用"""
        pass
    
    @property
    @abstractmethod
    def source(self) -> str:
        """返回来源标识"""
        pass


class CoPawProvider(BaseLLMProvider):
    """CoPaw API 提供者"""
    
    def __init__(self):
        self.api_url = config.COPAW_API_URL
        self.api_key = config.COPAW_API_KEY
        self.timeout = config.COPAW_TIMEOUT
    
    def is_available(self) -> bool:
        return bool(self.api_url and self.api_key)
    
    @property
    def source(self) -> str:
        return 'copaw'
    
    def parse_report(self, content: str) -> Optional[Dict[str, Any]]:
        if not self.is_available():
            return None
        
        try:
            import requests
            response = requests.post(
                self.api_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={'content': content[:10000]},  # 限制内容长度
                timeout=self.timeout,
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None


class BailianProvider(BaseLLMProvider):
    """百炼（DashScope）API 提供者"""
    
    def __init__(self):
        self.api_key = config.DASHSCOPE_API_KEY
        self.timeout = config.BAILIAN_TIMEOUT
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    @property
    def source(self) -> str:
        return 'bailian'
    
    def parse_report(self, content: str) -> Optional[Dict[str, Any]]:
        if not self.is_available():
            return None
        
        try:
            import requests
            response = requests.post(
                'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': 'qwen-turbo',
                    'input': {
                        'prompt': self._build_prompt(content),
                    },
                    'parameters': {
                        'result_format': 'text',
                    },
                },
                timeout=self.timeout,
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_response(result)
            return None
        except Exception:
            return None
    
    def _build_prompt(self, content: str) -> str:
        """构建解析Prompt"""
        return f"""请分析以下研报内容，提取关键信息并以JSON格式返回：
研报标题、研究对象主体（上市公司名称及股票代码）、研报作者（券商公司）、评级、看涨看跌方向、目标价、核心观点摘要。

研报内容：
{content[:5000]}

请以以下JSON格式返回：
{{"title": "", "subject_name": "", "subject_code": "", "author": "", "rating": "", "trend": "", "target_price": 0, "summary": ""}}
"""
    
    def _parse_response(self, result: Dict) -> Optional[Dict[str, Any]]:
        """解析API响应"""
        try:
            text = result.get('output', {}).get('text', '')
            # 尝试从文本中提取JSON
            import re
            json_match = re.search(r'\{[^{}]*\}', text)
            if json_match:
                return json.loads(json_match.group())
            return None
        except Exception:
            return None


class DemoProvider(BaseLLMProvider):
    """Demo模式提供者（离线演示）"""
    
    def is_available(self) -> bool:
        return True  # 始终可用
    
    @property
    def source(self) -> str:
        return 'demo'
    
    def parse_report(self, content: str) -> Optional[Dict[str, Any]]:
        """返回模拟解析结果"""
        return {
            'title': '示例研报标题',
            'subject_name': '示例上市公司',
            'subject_code': '000000',
            'author': '示例券商',
            'rating': '中性',
            'trend': 'neutral',
            'target_price': None,
            'summary': '这是Demo模式下的模拟解析结果。实际使用时请配置LLM API。',
        }


class LLMProviderChain:
    """LLM提供者降级链"""
    
    def __init__(self):
        self.providers = [
            CoPawProvider(),
            BailianProvider(),
            DemoProvider(),
        ]
    
    def parse_report(self, content: str) -> Dict[str, Any]:
        """
        按顺序尝试解析，返回结果和来源
        
        Returns:
            包含解析结果和来源的字典
        """
        for provider in self.providers:
            if provider.is_available():
                result = provider.parse_report(content)
                if result:
                    result['source'] = provider.source
                    result['llm_used'] = provider.source != 'demo'
                    return result
        
        # 兜底：返回Demo结果
        return {
            'title': '',
            'subject_name': '',
            'subject_code': '',
            'author': '',
            'rating': '',
            'trend': 'neutral',
            'target_price': None,
            'summary': '',
            'source': 'demo',
            'llm_used': False,
        }


# 全局LLM提供者链实例
llm_chain = LLMProviderChain()
