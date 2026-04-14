from abc import ABC, abstractmethod
from typing import AsyncGenerator


class LLMProvider(ABC):
    """LLM Provider 抽象基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider 名称"""
        pass
    
    @abstractmethod
    async def generate(self, messages: list[dict], model: str = None) -> dict:
        """同步生成回复
        返回: {"content": str, "model": str, "tokens_input": int, "tokens_output": int}
        """
        pass
    
    @abstractmethod
    async def stream_generate(self, messages: list[dict], model: str = None) -> AsyncGenerator[str, None]:
        """流式生成回复，yield 文本片段"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass
