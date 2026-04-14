"""
Route 层 — agent 蓝图
对齐 Spec 09 API 接口规格，6 个端点
Base URL: /api/v1/agent
"""
import uuid
from flask import Blueprint, request, jsonify, current_app
from app.agent import agent as agent_module
from app.storage.storage import Storage

agent_bp = Blueprint("agent", __name__)


def _trace_id():
    return f"tr_{uuid.uuid4().hex[:12]}"


def _error_response(code, message, http_status, details=None):
    """统一错误响应格式 — 对齐 Spec 09 §2"""
    return jsonify({
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "traceId": _trace_id(),
        }
    }), http_status


def _get_storage():
    data_dir = current_app.config.get("DATA_DIR", "./data")
    return Storage(data_dir)


# ── 1. GET /capabilities — 能力探测 ──

@agent_bp.route("/capabilities", methods=["GET"])
def capabilities():
    caps = agent_module.get_capabilities()
    caps["traceId"] = _trace_id()
    return jsonify(caps), 200


# ── 2. POST /ask — 问答提交 ──

@agent_bp.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    session_id = data.get("session_id", "")

    # 参数校验
    if not query or not query.strip():
        return _error_response("EMPTY_QUERY", "请输入问题", 400)

    if len(query) > 500:
        return _error_response("INVALID_QUERY", "问题过长，最多500字符", 400,
                               {"max_length": 500})

    if not session_id:
        return _error_response("INVALID_QUERY", "缺少 session_id", 400)

    storage = _get_storage()
    session = storage.get_session(session_id)
    if not session:
        return _error_response("SESSION_NOT_FOUND", "会话不存在", 400,
                               {"session_id": session_id})

    try:
        result = agent_module.ask(query, session_id)

        # 写入记录
        storage.add_record(
            session_id=session_id,
            query=query,
            answer=result["answer"],
            llm_used=result["llm_used"],
            model=result["model"],
            response_time_ms=result["response_time_ms"],
            answer_source=result["answer_source"],
        )

        result["traceId"] = _trace_id()
        return jsonify(result), 200

    except Exception as e:
        return _error_response("UPSTREAM_ERROR", "服务暂时不可用", 500,
                               {"reason": str(e)})


# ── 3. GET /sessions — 会话列表 ──

@agent_bp.route("/sessions", methods=["GET"])
def get_sessions():
    storage = _get_storage()
    sessions = storage.get_sessions()
    return jsonify({
        "traceId": _trace_id(),
        "sessions": sessions,
    }), 200


# ── 4. POST /sessions — 新建会话 ──

@agent_bp.route("/sessions", methods=["POST"])
def create_session():
    data = request.get_json(silent=True) or {}
    title = data.get("title", "新会话")

    if title and len(title) > 23:
        return _error_response("INVALID_TITLE", "标题过长，最多23字符", 400)

    storage = _get_storage()
    session = storage.create_session(title=title)

    resp = {
        "traceId": _trace_id(),
        "session_id": session["session_id"],
        "title": session["title"],
        "created_at": session["created_at"],
        "query_count": session["query_count"],
    }
    return jsonify(resp), 201


# ── 5. DELETE /sessions/<id> — 删除会话 ──

@agent_bp.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    storage = _get_storage()
    deleted_count = storage.delete_session(session_id)

    if deleted_count is None:
        return _error_response("SESSION_NOT_FOUND", "会话不存在", 404,
                               {"session_id": session_id})

    return jsonify({
        "traceId": _trace_id(),
        "message": "会话已删除",
        "deleted_records": deleted_count,
    }), 200


# ── 6. GET /sessions/<id>/records — 问答记录 ──

@agent_bp.route("/sessions/<session_id>/records", methods=["GET"])
def get_records(session_id):
    storage = _get_storage()

    session = storage.get_session(session_id)
    if not session:
        return _error_response("SESSION_NOT_FOUND", "会话不存在", 404,
                               {"session_id": session_id})

    records = storage.get_records_by_session(session_id)
    return jsonify({
        "traceId": _trace_id(),
        "records": records,
    }), 200
