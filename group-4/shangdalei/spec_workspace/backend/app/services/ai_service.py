"""
AI服务模块
基于 08-系统架构与技术选型.md
支持三级降级：OpenAI -> Demo模式
"""
import logging
from typing import Tuple
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """AI服务 - 支持三级降级"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
    
    async def get_answer(self, query: str) -> Tuple[str, str]:
        """
        获取回答
        返回: (answer, source)
        source: openai | demo | fallback
        """
        # 尝试调用OpenAI
        if self.api_key:
            try:
                return await self._call_openai(query)
            except Exception as e:
                logger.warning(f"OpenAI调用失败: {e}")
        
        # 降级到演示模式
        return self._demo_answer(query), "demo"
    
    async def _call_openai(self, query: str) -> Tuple[str, str]:
        """调用OpenAI API"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的研报分析助手，帮助用户分析研报内容。"},
                    {"role": "user", "content": query}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            return answer, "openai"
            
        except ImportError:
            logger.warning("openai包未安装，使用演示模式")
            return self._demo_answer(query), "demo"
        except Exception as e:
            logger.error(f"OpenAI API调用异常: {e}")
            raise
    
    def _demo_answer(self, query: str) -> str:
        """演示模式回答"""
        return f"[演示模式] 感谢您的提问。这是一个演示回答。\n\n您的问题是：{query}\n\n请配置OPENAI_API_KEY以启用真实AI回答功能。"
