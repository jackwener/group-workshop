import logging
from typing import AsyncGenerator

from app.llm.provider import LLMProvider
from app.llm.mock_provider import MockProvider
from app.llm.openai_provider import OpenAIProvider
from app.config import settings

logger = logging.getLogger(__name__)


class LLMRouter:
    """LLM Provider 路由器，支持降级策略"""
    
    def __init__(self):
        self.providers: list[LLMProvider] = []
        self._init_providers()
    
    def _init_providers(self):
        """根据配置初始化 provider 列表，按优先级排序"""
        # 1. 如果有 OpenAI API Key，添加 OpenAI Provider（DashScope 兼容）
        if settings.OPENAI_API_KEY and settings.OPENAI_BASE_URL:
            try:
                openai_provider = OpenAIProvider()
                self.providers.append(openai_provider)
                logger.info(f"Registered OpenAI provider with base_url: {settings.OPENAI_BASE_URL}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI provider: {e}")
        
        # 2. 始终添加 Mock Provider 作为兜底
        self.providers.append(MockProvider())
        logger.info("Registered Mock provider as fallback")
        
        if not self.providers:
            raise RuntimeError("No LLM providers available")
    
    async def generate(self, messages: list[dict], model: str = None) -> dict:
        """按顺序尝试 provider，返回第一个成功的结果
        
        返回: {
            "content": str, 
            "model": str, 
            "provider": str, 
            "is_degraded": bool, 
            "tokens_input": int, 
            "tokens_output": int
        }
        """
        if not self.providers:
            raise RuntimeError("No LLM providers available")
        
        primary_provider = self.providers[0].name
        
        for i, provider in enumerate(self.providers):
            try:
                result = await provider.generate(messages, model)
                result["provider"] = provider.name
                result["is_degraded"] = (provider.name != primary_provider)
                
                if result["is_degraded"]:
                    logger.warning(f"Using degraded provider: {provider.name}")
                
                return result
                
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                continue
        
        raise Exception("All LLM providers failed")
    
    async def stream_generate(self, messages: list[dict], model: str = None) -> AsyncGenerator[dict, None]:
        """流式版本的降级路由
        
        yield 的事件格式：
        - {"event": "provider", "data": {"provider": str, "is_degraded": bool}}
        - {"event": "content", "data": {"content": str}}
        - {"event": "error", "data": {"error": str}}
        """
        if not self.providers:
            raise RuntimeError("No LLM providers available")
        
        primary_provider = self.providers[0].name
        
        for i, provider in enumerate(self.providers):
            try:
                # 首先发送 provider 信息
                is_degraded = (provider.name != primary_provider)
                yield {
                    "event": "provider",
                    "data": {
                        "provider": provider.name,
                        "is_degraded": is_degraded
                    }
                }
                
                if is_degraded:
                    logger.warning(f"Using degraded provider for streaming: {provider.name}")
                
                # 流式生成内容
                async for chunk in provider.stream_generate(messages, model):
                    yield {
                        "event": "content",
                        "data": {"content": chunk}
                    }
                
                # 成功完成，直接返回
                return
                
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed in stream: {e}")
                
                # 如果不是最后一个 provider，继续尝试下一个
                if i < len(self.providers) - 1:
                    yield {
                        "event": "error",
                        "data": {
                            "error": f"Provider {provider.name} failed, switching to fallback..."
                        }
                    }
                    continue
                else:
                    # 最后一个 provider 也失败了
                    yield {
                        "event": "error",
                        "data": {"error": f"All providers failed: {str(e)}"}
                    }
                    raise
    
    async def health_check(self) -> dict:
        """检查所有 provider 的健康状态"""
        results = {}
        for provider in self.providers:
            try:
                healthy = await provider.health_check()
                results[provider.name] = "healthy" if healthy else "unhealthy"
            except Exception as e:
                results[provider.name] = f"error: {str(e)}"
        return results


# 全局单例
llm_router = LLMRouter()
