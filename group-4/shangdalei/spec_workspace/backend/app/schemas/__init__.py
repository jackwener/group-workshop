"""
Pydantic模式定义
基于 09-API接口规格.md
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ============ 会话相关 ============

class SessionCreate(BaseModel):
    """创建会话请求"""
    name: Optional[str] = Field(None, max_length=255, description="会话名称")


class SessionResponse(BaseModel):
    """会话响应"""
    session_id: str
    name: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """会话列表响应"""
    sessions: List[SessionResponse]
    total: int


# ============ 问答相关 ============

class QARequest(BaseModel):
    """问答请求"""
    session_id: str = Field(..., description="会话ID")
    query: str = Field(..., min_length=1, max_length=500, description="用户问题")


class Reference(BaseModel):
    """引用来源"""
    source: str = Field(..., description="研报名称")
    snippet: str = Field(..., description="引用片段")


class QAResponse(BaseModel):
    """问答响应"""
    answer: str
    answer_source: str  # openai, demo, fallback
    references: List[Reference] = []
    created_at: datetime


class QARecordResponse(BaseModel):
    """问答记录响应"""
    query: str
    answer: str
    answer_source: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class QAHistoryResponse(BaseModel):
    """问答历史响应"""
    records: List[QARecordResponse]
    total: int
    page: int
    page_size: int


# ============ 健康检查相关 ============

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str  # healthy, degraded, unhealthy
    dependencies: dict


# ============ 通用响应 ============

class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    message: str


class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = True
