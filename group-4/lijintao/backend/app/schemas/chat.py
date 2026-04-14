from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """聊天请求"""
    content: str = Field(..., min_length=1, max_length=4000, description="用户消息内容")
    stream: bool = Field(True, description="是否使用流式响应")
    model: str = Field("auto", description="指定模型，auto 表示自动选择")


class ChatResponse(BaseModel):
    """聊天响应（非流式）"""
    message_id: int = Field(..., description="用户消息ID")
    response_id: int = Field(..., description="助手回复消息ID")
    content: str = Field(..., description="回复内容")
    model: str = Field(..., description="使用的模型")
    provider: str = Field(..., description="使用的Provider")
    tokens_input: int = Field(0, description="输入token数")
    tokens_output: int = Field(0, description="输出token数")
    latency_ms: int = Field(0, description="响应延迟（毫秒）")
    is_degraded: bool = Field(False, description="是否使用了降级Provider")


class SSEEvent(BaseModel):
    """SSE 事件"""
    event: str = Field(..., description="事件类型: message_start, content_block_delta, message_stop")
    data: dict = Field(..., description="事件数据")


class ChatStreamEvent(BaseModel):
    """聊天流事件"""
    event: str = Field(..., description="事件类型")
    data: dict = Field(..., description="事件数据")
