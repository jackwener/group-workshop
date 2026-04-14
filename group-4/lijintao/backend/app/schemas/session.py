from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List


class SessionCreate(BaseModel):
    """创建会话请求"""
    model_config = ConfigDict(from_attributes=True)
    
    title: str = "新会话"


class SessionResponse(BaseModel):
    """会话响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    message_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SessionListResponse(BaseModel):
    """会话列表响应"""
    model_config = ConfigDict(from_attributes=True)
    
    sessions: List[SessionResponse]
    total: int
    page: int
    page_size: int
