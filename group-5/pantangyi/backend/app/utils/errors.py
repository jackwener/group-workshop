"""Error codes and exceptions for the application."""

# Error Code Definitions (aligned with 09-API接口规格.md §2.5)
ERROR_CODES = {
    # 400 - Bad Request
    400001: {"message": "参数缺失", "http_status": 400},
    400002: {"message": "参数格式错误", "http_status": 400},
    400003: {"message": "文件格式不支持", "http_status": 400},
    
    # 404 - Not Found
    404001: {"message": "会话不存在", "http_status": 404},
    404002: {"message": "报告不存在", "http_status": 404},
    
    # 500 - Internal Server Error
    500001: {"message": "LLM服务不可用", "http_status": 500},
    500002: {"message": "数据源超时", "http_status": 500},
    
    # 503 - Service Unavailable (Degraded)
    503001: {"message": "服务降级中", "http_status": 503},
}


class APIError(Exception):
    """Base API Error exception."""
    
    def __init__(self, error_code, detail=None):
        self.error_code = error_code
        self.detail = detail
        error_info = ERROR_CODES.get(error_code, {
            "message": "未知错误",
            "http_status": 500
        })
        self.message = error_info["message"]
        self.http_status = error_info["http_status"]
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error - 400001."""
    def __init__(self, detail=None):
        super().__init__(400001, detail)


class FormatError(APIError):
    """Format error - 400002."""
    def __init__(self, detail=None):
        super().__init__(400002, detail)


class FileTypeError(APIError):
    """File type not supported - 400003."""
    def __init__(self, detail=None):
        super().__init__(400003, detail)


class SessionNotFoundError(APIError):
    """Session not found - 404001."""
    def __init__(self, detail=None):
        super().__init__(404001, detail)


class ReportNotFoundError(APIError):
    """Report not found - 404002."""
    def __init__(self, detail=None):
        super().__init__(404002, detail)


class LLMServiceError(APIError):
    """LLM service unavailable - 500001."""
    def __init__(self, detail=None):
        super().__init__(500001, detail)


class DataSourceTimeoutError(APIError):
    """Data source timeout - 500002."""
    def __init__(self, detail=None):
        super().__init__(500002, detail)


class ServiceDegradedError(APIError):
    """Service degraded - 503001."""
    def __init__(self, detail=None):
        super().__init__(503001, detail)
