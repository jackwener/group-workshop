"""
投研问答助手 - API 路由层
实现所有 RESTful API 端点
Base URL: /api/v1/agent
"""
import uuid
from flask import Blueprint, request, jsonify, current_app

from .storage import get_storage
from .agent import get_agent

# 创建蓝图
agent_bp = Blueprint("agent", __name__)


def generate_trace_id() -> str:
    """生成链路追踪 ID"""
    return f"tr_{uuid.uuid4().hex[:16]}"


def success_response(data: dict, trace_id: str = None) -> dict:
    """构建成功响应"""
    response = {"traceId": trace_id or generate_trace_id()}
    response.update(data)
    return response


def error_response(code: str, message: str, http_status: int = 400, details: dict = None) -> tuple:
    """构建错误响应"""
    response = {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "traceId": generate_trace_id()
        }
    }
    return jsonify(response), http_status


# ==================== 能力探测 ====================

@agent_bp.route("/capabilities", methods=["GET"])
def get_capabilities():
    """
    获取系统能力状态
    GET /api/v1/agent/capabilities
    ---
    tags:
      - 系统管理
    summary: 获取系统能力状态
    description: 返回系统支持的 LLM 能力和当前状态
    responses:
      200:
        description: 成功返回能力信息
        schema:
          type: object
          properties:
            traceId:
              type: string
              example: tr_abc123def456
            llm:
              type: string
              example: demo
            model:
              type: string
              example: demo-mode
            status:
              type: string
              example: ok
    """
    agent = get_agent()
    caps = agent.get_capabilities()
    return jsonify(success_response(caps))


# ==================== 问答提交 ====================

@agent_bp.route("/ask", methods=["POST"])
def ask():
    """
    提交问题并获取回答
    POST /api/v1/agent/ask
    ---
    tags:
      - 问答接口
    summary: 提交问题并获取回答
    description: 向系统提交问题，返回智能回答
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - query
            - session_id
          properties:
            query:
              type: string
              description: 用户问题（1-500字符）
              example: 贵州茅台的投资价值如何？
            session_id:
              type: string
              description: 会话ID
              example: sess_abc123
    responses:
      200:
        description: 成功返回回答
        schema:
          type: object
          properties:
            traceId:
              type: string
            answer:
              type: string
            llm_used:
              type: string
            model:
              type: string
            response_time_ms:
              type: integer
      400:
        description: 参数错误
      404:
        description: 会话不存在
    """
    data = request.get_json() or {}
    trace_id = generate_trace_id()
    
    # 参数校验
    query = data.get("query", "").strip()
    session_id = data.get("session_id", "").strip()
    
    # 校验 query
    if not query:
        return error_response(
            "EMPTY_QUERY", 
            "请输入问题", 
            400
        )
    
    if len(query) > 500:
        return error_response(
            "INVALID_QUERY", 
            "问题过长，最多500字符", 
            400,
            {"max_length": 500}
        )
    
    # 校验 session_id
    if not session_id:
        return error_response(
            "INVALID_QUERY", 
            "缺少会话ID", 
            400
        )
    
    # 检查会话是否存在
    storage = get_storage(current_app.config["DATA_DIR"])
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND", 
            "会话不存在或已被删除", 
            404,
            {"session_id": session_id}
        )
    
    # 调用 Agent 获取回答
    agent = get_agent()
    result = agent.ask(query, session_id)
    
    # 保存问答记录
    storage.add_record(
        session_id=session_id,
        query=query,
        answer=result["answer"],
        llm_used=result["llm_used"],
        model=result["model"],
        response_time_ms=result["response_time_ms"],
        answer_source=result["answer_source"]
    )
    
    return jsonify(success_response(result, trace_id))


# ==================== 会话管理 ====================

@agent_bp.route("/sessions", methods=["GET"])
def get_sessions():
    """
    获取会话列表
    GET /api/v1/agent/sessions
    ---
    tags:
      - 会话管理
    summary: 获取会话列表
    description: 返回所有会话的列表
    responses:
      200:
        description: 成功返回会话列表
        schema:
          type: object
          properties:
            traceId:
              type: string
            sessions:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  title:
                    type: string
                  created_at:
                    type: string
    """
    storage = get_storage(current_app.config["DATA_DIR"])
    sessions = storage.get_sessions()
    trace_id = generate_trace_id()
    
    return jsonify(success_response({"sessions": sessions}, trace_id))


@agent_bp.route("/sessions", methods=["POST"])
def create_session():
    """
    创建新会话
    POST /api/v1/agent/sessions
    ---
    tags:
      - 会话管理
    summary: 创建新会话
    description: 创建一个新的问答会话
    parameters:
      - name: body
        in: body
        required: false
        schema:
          type: object
          properties:
            title:
              type: string
              description: 会话标题（可选，最多23字符）
              example: 茅台研报分析
    responses:
      201:
        description: 成功创建会话
        schema:
          type: object
          properties:
            traceId:
              type: string
            id:
              type: string
            title:
              type: string
            created_at:
              type: string
    """
    data = request.get_json() or {}
    trace_id = generate_trace_id()
    
    title = data.get("title", "新会话").strip()
    
    # 标题长度截断（超过23字符）
    if len(title) > 23:
        title = title[:23]
    
    storage = get_storage(current_app.config["DATA_DIR"])
    session = storage.create_session(title)
    
    return jsonify(success_response(session, trace_id)), 201


@agent_bp.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id: str):
    """
    删除会话（级联删除关联记录）
    DELETE /api/v1/agent/sessions/<session_id>
    ---
    tags:
      - 会话管理
    summary: 删除会话
    description: 删除指定会话及其所有问答记录
    parameters:
      - name: session_id
        in: path
        type: string
        required: true
        description: 会话ID
    responses:
      200:
        description: 成功删除
      400:
        description: 会话ID无效
      404:
        description: 会话不存在
    """
    trace_id = generate_trace_id()
    
    if not session_id:
        return error_response(
            "INVALID_QUERY", 
            "会话ID不能为空", 
            400
        )
    
    storage = get_storage(current_app.config["DATA_DIR"])
    success = storage.delete_session(session_id)
    
    if not success:
        return error_response(
            "SESSION_NOT_FOUND", 
            "会话不存在或已被删除", 
            404,
            {"session_id": session_id}
        )
    
    return jsonify(success_response({
        "success": True,
        "message": "会话已删除"
    }, trace_id))


@agent_bp.route("/sessions/<session_id>/records", methods=["GET"])
def get_session_records(session_id: str):
    """
    获取会话的问答记录
    GET /api/v1/agent/sessions/<session_id>/records
    ---
    tags:
      - 会话管理
    summary: 获取问答记录
    description: 获取指定会话的所有问答记录
    parameters:
      - name: session_id
        in: path
        type: string
        required: true
        description: 会话ID
    responses:
      200:
        description: 成功返回记录列表
        schema:
          type: object
          properties:
            traceId:
              type: string
            records:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  query:
                    type: string
                  answer:
                    type: string
                  llm_used:
                    type: string
                  created_at:
                    type: string
      400:
        description: 会话ID无效
      404:
        description: 会话不存在
    """
    trace_id = generate_trace_id()
    
    if not session_id:
        return error_response(
            "INVALID_QUERY", 
            "会话ID不能为空", 
            400
        )
    
    # 检查会话是否存在
    storage = get_storage(current_app.config["DATA_DIR"])
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND", 
            "会话不存在或已被删除", 
            404,
            {"session_id": session_id}
        )
    
    records = storage.get_records_by_session(session_id)
    
    return jsonify(success_response({"records": records}, trace_id))


# ==================== 全局错误处理 ====================

@agent_bp.errorhandler(404)
def not_found(error):
    """处理 404 错误"""
    return error_response(
        "NOT_FOUND", 
        "请求的资源不存在", 
        404
    )


@agent_bp.errorhandler(500)
def internal_error(error):
    """处理 500 错误"""
    return error_response(
        "UPSTREAM_ERROR", 
        "服务暂时不可用，请稍后重试", 
        500
    )


@agent_bp.errorhandler(429)
def rate_limit(error):
    """处理速率限制错误"""
    return error_response(
        "RATE_LIMIT_ERROR", 
        "请求过于频繁，请稍后再试", 
        429,
        {"retry_after_seconds": 60}
    )


@agent_bp.errorhandler(408)
def timeout(error):
    """处理超时错误"""
    return error_response(
        "TIMEOUT_ERROR", 
        "请求超时，请稍后重试", 
        408
    )
