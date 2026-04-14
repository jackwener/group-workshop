import uuid
from flask import jsonify, request

class APIError(Exception):
    """API错误基类"""
    def __init__(self, code, message, http_status=400, details=None):
        self.code = code
        self.message = message
        self.http_status = http_status
        self.details = details or {}
        super().__init__(self.message)

def generate_trace_id():
    """生成链路追踪ID"""
    return f"tr_{uuid.uuid4().hex[:16]}"

def make_response(data=None, trace_id=None):
    """构造统一响应格式"""
    if trace_id is None:
        trace_id = getattr(request, 'trace_id', generate_trace_id())
    
    response_data = {'traceId': trace_id}
    if data is not None:
        response_data.update(data)
    return response_data

def make_error_response(code, message, http_status=400, details=None, trace_id=None):
    """构造错误响应格式"""
    if trace_id is None:
        trace_id = getattr(request, 'trace_id', generate_trace_id())
    
    return jsonify({
        'error': {
            'code': code,
            'message': message,
            'details': details or {},
            'traceId': trace_id
        }
    }), http_status

def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.before_request
    def before_request():
        """每个请求前生成trace_id"""
        request.trace_id = generate_trace_id()
    
    @app.after_request
    def after_request(response):
        """每个响应后注入trace_id"""
        if hasattr(request, 'trace_id'):
            response.headers['X-Trace-Id'] = request.trace_id
        return response
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """处理API错误"""
        return make_error_response(
            error.code,
            error.message,
            error.http_status,
            error.details,
            request.trace_id
        )
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """处理404错误"""
        return make_error_response(
            'NOT_FOUND',
            '请求的资源不存在',
            404,
            {},
            request.trace_id
        )
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """处理500错误"""
        return make_error_response(
            'INTERNAL_ERROR',
            '服务器内部错误',
            500,
            {},
            request.trace_id
        )
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """处理未捕获的异常"""
        return make_error_response(
            'INTERNAL_ERROR',
            str(error),
            500,
            {},
            request.trace_id
        )
