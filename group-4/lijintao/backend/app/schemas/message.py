from pydantic import BaseModel, ConfigDict, computed_field
from datetime import datetime
from typing import List, Optional


class MessageResponse(BaseModel):
    """消息响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    session_id: int
    role: str
    content: str
    tokens: Optional[int] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    latency_ms: Optional[int] = None
    created_at: datetime
    
    @computed_field
    @property
    def is_degraded(self) -> bool:
        """根据 metadata 判断是否降级"""
        # 通过 model_config 的 from_attributes 会传递 ORM 对象
        # 这里我们通过检查是否有 metadata_ 属性来判断
        metadata = getattr(self, 'metadata_', {}) or {}
        return metadata.get('is_degraded', False)


class MessageListResponse(BaseModel):
    """消息列表响应"""
    model_config = ConfigDict(from_attributes=True)
    
    messages: List[MessageResponse]
    total: int
    page: int
    page_size: int
