from pydantic import BaseModel, ConfigDict
from typing import TypeVar, Generic, Optional
from datetime import datetime

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """统一响应基类"""
    model_config = ConfigDict(from_attributes=True)
    
    traceId: str
    data: T
    timestamp: datetime


class ErrorDetail(BaseModel):
    """错误详情"""
    model_config = ConfigDict(from_attributes=True)
    
    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    model_config = ConfigDict(from_attributes=True)
    
    error: ErrorDetail
    traceId: str
    timestamp: datetime
