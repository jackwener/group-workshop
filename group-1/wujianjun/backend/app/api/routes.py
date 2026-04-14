"""
Route 层 - API 端点实现
对齐 09-API接口规格 §1 端点总览（6 个端点）
职责：参数校验、HTTP 状态码、traceId（禁止直接读写文件、调用 LLM）

端点列表：
1. GET  /capabilities          - 能力探测
2. POST /ask                   - 问答提交
3. GET  /sessions              - 会话列表
4. POST /sessions              - 新建会话
5. DELETE /sessions/<id>       - 删除会话
6. GET  /sessions/<id>/records - 问答记录
"""
import uuid
from flask import request, jsonify

from app.api import agent_bp
from app.core.storage import Storage
from app.services.agent import CoPawAgent


# ==================== 工具函数 ====================

def generate_trace_id() -> str:
    """生成 traceId: tr_{uuid.hex}（32 位十六进制）"""
    return f"tr_{uuid.uuid4().hex}"


def success_response(data: dict, trace_id: str) -> tuple:
    """统一成功响应格式"""
    return jsonify({
        "traceId": trace_id,
        "data": data
    })


def error_response(code: str, message: str, trace_id: str, details: dict = None, status_code: int = 400) -> tuple:
    """统一错误响应格式"""
    response = {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "traceId": trace_id
        }
    }
    return jsonify(response), status_code


# 初始化服务（教学版使用单例）
storage = Storage()
agent = CoPawAgent()


# ==================== 1. GET /capabilities - 能力探测 ====================

@agent_bp.route("/capabilities", methods=["GET"])
def get_capabilities():
    """
    能力探测端点
    对齐 09-API接口规格 §3
    """
    trace_id = generate_trace_id()
    
    caps = agent.get_capabilities()
    return success_response(caps, trace_id), 200


# ==================== 2. POST /ask - 问答提交 ====================

@agent_bp.route("/ask", methods=["POST"])
def post_ask():
    """
    问答提交端点
    对齐 09-API接口规格 §4
    """
    trace_id = generate_trace_id()
    
    # 获取请求体
    body = request.get_json() or {}
    query = body.get("query", "").strip()
    session_id = body.get("session_id", "").strip()
    
    # 参数校验：query 为空
    if not query:
        return error_response(
            "EMPTY_QUERY",
            "请输入问题",
            trace_id,
            status_code=400
        )
    
    # 参数校验：query 超过 500 字符
    if len(query) > 500:
        return error_response(
            "INVALID_QUERY",
            "问题长度超过限制",
            trace_id,
            {"max_length": 500, "actual": len(query)},
            status_code=400
        )
    
    # 参数校验：session_id 不存在
    if not session_id:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            trace_id,
            {"session_id": session_id},
            status_code=400
        )
    
    # 检查会话是否存在
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            trace_id,
            {"session_id": session_id},
            status_code=404
        )
    
    # 调用 Agent 进行问答
    result = agent.ask(query, session_id)
    
    # 保存问答记录
    record = storage.add_record(
        session_id=session_id,
        query=query,
        answer=result["answer"],
        llm_used=result["llm_used"],
        model=result["model"],
        response_time_ms=result["response_time_ms"],
        answer_source=result["answer_source"]
    )
    
    # 组装响应
    response_data = {
        "answer": result["answer"],
        "llm_used": result["llm_used"],
        "model": result["model"],
        "response_time_ms": result["response_time_ms"],
        "answer_source": result["answer_source"],
        "record_id": record["record_id"]
    }
    
    return success_response(response_data, trace_id), 200


# ==================== 3. GET /sessions - 会话列表 ====================

@agent_bp.route("/sessions", methods=["GET"])
def get_sessions():
    """
    会话列表端点
    对齐 09-API接口规格 §6
    """
    trace_id = generate_trace_id()
    
    # 获取分页参数
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    
    # 约束范围
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    
    # 获取所有会话
    all_sessions = storage.get_sessions()
    total = len(all_sessions)
    
    # 分页
    paginated = all_sessions[offset:offset + limit]
    
    return success_response({
        "sessions": paginated,
        "total": total
    }, trace_id), 200


# ==================== 4. POST /sessions - 新建会话 ====================

@agent_bp.route("/sessions", methods=["POST"])
def post_sessions():
    """
    新建会话端点
    对齐 09-API接口规格 §5
    """
    trace_id = generate_trace_id()
    
    # 获取请求体
    body = request.get_json() or {}
    title = body.get("title", "新会话").strip()
    
    # 参数校验：标题长度
    if len(title) > 100:
        return error_response(
            "INVALID_QUERY",
            "会话标题过长",
            trace_id,
            {"max_length": 100, "actual": len(title)},
            status_code=400
        )
    
    # 生成 session_id
    session_id = f"sess_{uuid.uuid4().hex[:16]}"
    
    # 创建会话
    session = storage.create_session(session_id, title)
    
    return success_response(session, trace_id), 201


# ==================== 5. DELETE /sessions/<id> - 删除会话 ====================

@agent_bp.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id: str):
    """
    删除会话端点
    对齐 09-API接口规格 §7
    """
    trace_id = generate_trace_id()
    
    # 检查会话是否存在
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            trace_id,
            {"session_id": session_id},
            status_code=404
        )
    
    # 删除会话（级联删除关联记录）
    deleted_records_count = storage.delete_session(session_id)
    
    return success_response({
        "message": "会话删除成功",
        "deleted_session_id": session_id,
        "deleted_records_count": deleted_records_count
    }, trace_id), 200


# ==================== 6. GET /sessions/<id>/records - 问答记录 ====================

@agent_bp.route("/sessions/<session_id>/records", methods=["GET"])
def get_session_records(session_id: str):
    """
    问答记录端点
    对齐 09-API接口规格 §8
    """
    trace_id = generate_trace_id()
    
    # 检查会话是否存在
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            trace_id,
            {"session_id": session_id},
            status_code=404
        )
    
    # 获取分页参数
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)
    
    # 约束范围
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    
    # 获取记录
    all_records = storage.get_records_by_session(session_id)
    total = len(all_records)
    
    # 分页
    paginated = all_records[offset:offset + limit]
    
    return success_response({
        "session_id": session_id,
        "records": paginated,
        "total": total
    }, trace_id), 200
