import time
import logging
from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy.orm import Session

from app.services.message_service import MessageService
from app.llm.router import llm_router
from app.schemas.chat import ChatResponse

logger = logging.getLogger(__name__)


class ChatService:
    """问答引擎服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.message_service = MessageService(db)
    
    async def chat(self, session_id: int, content: str, stream: bool = True, model: str = "auto"):
        """处理问答请求
        
        Args:
            session_id: 会话ID
            content: 用户消息内容
            stream: 是否使用流式响应
            model: 指定模型
            
        Returns:
            流式：AsyncGenerator 生成 SSE 事件
            非流式：ChatResponse 对象
        """
        start_time = time.time()
        
        # 1. 保存用户消息
        user_msg = self.message_service.create(session_id, "user", content)
        
        # 2. 构建上下文（最近 N 条消息）
        messages = self._build_context(session_id)
        
        # 3. 调用 LLM
        if stream:
            return self._stream_chat(session_id, user_msg.id, messages, model, start_time)
        else:
            return await self._sync_chat(session_id, user_msg.id, messages, model, start_time)
    
    def _build_context(self, session_id: int, max_messages: int = 20) -> list[dict]:
        """构建 LLM 上下文，包含系统提示 + 最近消息
        
        Args:
            session_id: 会话ID
            max_messages: 最大历史消息数
            
        Returns:
            OpenAI 格式的消息列表
        """
        system_prompt = {
            "role": "system", 
            "content": "你是一个专业的投研问答助手，帮助分析师和投资经理解答投研相关问题。请提供专业、准确、有数据支撑的回答。"
        }
        
        # 获取最近的消息
        recent_msgs, _ = self.message_service.get_by_session(
            session_id, 
            page=1, 
            page_size=max_messages
        )
        
        context = [system_prompt]
        for msg in recent_msgs:
            context.append({"role": msg.role, "content": msg.content})
        
        return context
    
    async def _stream_chat(
        self, 
        session_id: int, 
        user_msg_id: int, 
        messages: list[dict],
        model: str,
        start_time: float
    ) -> AsyncGenerator[dict, None]:
        """流式聊天，返回 SSE 事件
        
        事件格式：
        - message_start: 开始生成
        - content_block_delta: 内容片段（多次）
        - message_stop: 完成，包含完整元数据
        """
        full_content = ""
        provider_name = ""
        is_degraded = False
        model_used = model if model != "auto" else "default"
        
        try:
            # 发送开始事件
            yield {
                "event": "message_start",
                "data": {
                    "message_id": user_msg_id,
                    "type": "message"
                }
            }
            
            # 流式生成
            async for event in llm_router.stream_generate(messages, model if model != "auto" else None):
                event_type = event.get("event")
                event_data = event.get("data", {})
                
                if event_type == "provider":
                    # 记录 provider 信息
                    provider_name = event_data.get("provider", "")
                    is_degraded = event_data.get("is_degraded", False)
                    
                elif event_type == "content":
                    # 内容片段
                    content_chunk = event_data.get("content", "")
                    if content_chunk:
                        full_content += content_chunk
                        yield {
                            "event": "content_block_delta",
                            "data": {
                                "type": "content_block_delta",
                                "delta": {
                                    "type": "text",
                                    "text": content_chunk
                                }
                            }
                        }
                        
                elif event_type == "error":
                    # 错误事件
                    yield {
                        "event": "error",
                        "data": {
                            "error": event_data.get("error", "Unknown error")
                        }
                    }
            
            # 计算延迟
            latency_ms = int((time.time() - start_time) * 1000)
            
            # 保存完整的 assistant 消息到数据库
            assistant_msg = self.message_service.create(
                session_id=session_id,
                role="assistant",
                content=full_content,
                model=model_used,
                provider=provider_name,
                latency_ms=latency_ms,
                metadata_={"is_degraded": is_degraded, "user_message_id": user_msg_id}
            )
            
            # 发送结束事件
            yield {
                "event": "message_stop",
                "data": {
                    "type": "message_stop",
                    "message": {
                        "id": assistant_msg.id,
                        "content": full_content,
                        "model": model_used,
                        "provider": provider_name,
                        "is_degraded": is_degraded,
                        "latency_ms": latency_ms
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Stream chat error: {e}")
            yield {
                "event": "error",
                "data": {
                    "error": f"Stream generation failed: {str(e)}"
                }
            }
            raise
    
    async def _sync_chat(
        self, 
        session_id: int, 
        user_msg_id: int, 
        messages: list[dict],
        model: str,
        start_time: float
    ) -> ChatResponse:
        """同步聊天
        
        Args:
            session_id: 会话ID
            user_msg_id: 用户消息ID
            messages: LLM 上下文消息
            model: 指定模型
            start_time: 开始时间
            
        Returns:
            ChatResponse 对象
        """
        # 调用 LLM
        result = await llm_router.generate(messages, model if model != "auto" else None)
        
        # 计算延迟
        latency_ms = int((time.time() - start_time) * 1000)
        
        # 保存 assistant 消息
        assistant_msg = self.message_service.create(
            session_id=session_id,
            role="assistant",
            content=result["content"],
            model=result["model"],
            provider=result["provider"],
            latency_ms=latency_ms,
            metadata_={
                "is_degraded": result.get("is_degraded", False),
                "user_message_id": user_msg_id,
                "tokens_input": result.get("tokens_input", 0),
                "tokens_output": result.get("tokens_output", 0)
            }
        )
        
        return ChatResponse(
            message_id=user_msg_id,
            response_id=assistant_msg.id,
            content=result["content"],
            model=result["model"],
            provider=result["provider"],
            tokens_input=result.get("tokens_input", 0),
            tokens_output=result.get("tokens_output", 0),
            latency_ms=latency_ms,
            is_degraded=result.get("is_degraded", False)
        )
