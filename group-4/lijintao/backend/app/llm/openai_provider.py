import json
import logging
from typing import AsyncGenerator

import httpx

from app.llm.provider import LLMProvider
from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI/DashScope 兼容 Provider"""
    
    def __init__(self):
        self._name = "openai"
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL.rstrip("/") if settings.OPENAI_BASE_URL else ""
        self.default_model = settings.OPENAI_MODEL or "gpt-4"
        
        # 初始化 HTTP 客户端
        timeout = httpx.Timeout(60.0, connect=10.0)
        self.client = httpx.AsyncClient(timeout=timeout)
    
    @property
    def name(self) -> str:
        return self._name
    
    def _get_headers(self) -> dict:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _get_model(self, model: str = None) -> str:
        """获取模型名称"""
        return model or self.default_model
    
    async def generate(self, messages: list[dict], model: str = None) -> dict:
        """同步生成回复"""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        
        if not self.base_url:
            raise ValueError("OPENAI_BASE_URL is not configured")
        
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self._get_model(model),
            "messages": messages,
            "stream": False
        }
        
        try:
            response = await self.client.post(
                url,
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            # 解析响应
            choice = data["choices"][0]
            message = choice["message"]
            usage = data.get("usage", {})
            
            return {
                "content": message["content"],
                "model": data.get("model", model or self.default_model),
                "tokens_input": usage.get("prompt_tokens", 0),
                "tokens_output": usage.get("completion_tokens", 0)
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"OpenAI API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"OpenAI API request error: {e}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"OpenAI API unexpected error: {e}")
            raise
    
    async def stream_generate(self, messages: list[dict], model: str = None) -> AsyncGenerator[str, None]:
        """流式生成回复，解析 SSE 响应"""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        
        if not self.base_url:
            raise ValueError("OPENAI_BASE_URL is not configured")
        
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self._get_model(model),
            "messages": messages,
            "stream": True
        }
        
        try:
            async with self.client.stream(
                "POST",
                url,
                headers=self._get_headers(),
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    
                    # SSE 格式: data: {...}
                    if line.startswith("data: "):
                        data_str = line[6:]  # 去掉 "data: " 前缀
                        
                        # 流结束标记
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            choice = data.get("choices", [{}])[0]
                            delta = choice.get("delta", {})
                            
                            # 获取内容片段
                            content = delta.get("content", "")
                            if content:
                                yield content
                                
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse SSE data: {data_str}")
                            continue
                        
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenAI API streaming HTTP error: {e.response.status_code}")
            raise Exception(f"OpenAI API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"OpenAI API streaming request error: {e}")
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"OpenAI API streaming unexpected error: {e}")
            raise
    
    async def health_check(self) -> bool:
        """健康检查 - 尝试调用 models 列表或简单请求"""
        if not self.api_key or not self.base_url:
            return False
        
        try:
            # 尝试获取模型列表
            url = f"{self.base_url}/models"
            response = await self.client.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                return True
            
            # 如果 models 接口不可用，尝试一个简单的 completion 请求
            url = f"{self.base_url}/chat/completions"
            payload = {
                "model": self.default_model,
                "messages": [{"role": "user", "content": "hi"}],
                "max_tokens": 5
            }
            response = await self.client.post(url, headers=self._get_headers(), json=payload)
            return response.status_code == 200
            
        except Exception as e:
            logger.warning(f"OpenAI health check failed: {e}")
            return False
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.client.aclose()
