import uuid
from typing import Any
from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """应用异常基类"""
    def __init__(self, message: str, status_code: int = 500, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        self.trace_id = str(uuid.uuid4())
        super().__init__(self.message)


class NotFoundException(AppException):
    """资源不存在异常"""
    def __init__(self, message: str = "资源不存在", details: Any = None):
        super().__init__(message, status_code=404, details=details)


class ValidationException(AppException):
    """参数校验异常"""
    def __init__(self, message: str = "参数校验失败", details: Any = None):
        super().__init__(message, status_code=422, details=details)


class LLMException(AppException):
    """LLM 服务异常"""
    def __init__(self, message: str = "LLM 服务调用失败", details: Any = None):
        super().__init__(message, status_code=503, details=details)


async def app_exception_handler(request: Request, exc: AppException):
    """统一异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "traceId": exc.trace_id,
            "message": exc.message,
            "details": exc.details,
            "timestamp": str(uuid.uuid4())
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """通用异常处理器"""
    trace_id = str(uuid.uuid4())
    return JSONResponse(
        status_code=500,
        content={
            "traceId": trace_id,
            "message": "服务器内部错误",
            "details": str(exc) if isinstance(exc, Exception) else None,
            "timestamp": str(uuid.uuid4())
        }
    )
