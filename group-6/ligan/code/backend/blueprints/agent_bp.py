import uuid
from flask import Blueprint, request, jsonify

agent_bp = Blueprint("agent_bp", __name__, url_prefix="/api/v1/agent")

# Will be set by app.py
storage = None
agent = None


def init_bp(s, a):
    global storage, agent
    storage = s
    agent = a


# ========== traceId Utilities (T-003) ==========

def generate_trace_id():
    return f"tr_{uuid.uuid4().hex}"


def get_trace_id(req):
    return req.headers.get("X-Trace-Id") or generate_trace_id()


def _ok(data, trace_id, status=200):
    data["traceId"] = trace_id
    return jsonify(data), status


def _error(code, message, trace_id, http_status=400, details=None):
    body = {
        "error": {
            "code": code,
            "message": message,
            "traceId": trace_id,
        }
    }
    if details:
        body["error"]["details"] = details
    return jsonify(body), http_status


# ========== GET /capabilities (T-026) ==========

@agent_bp.route("/capabilities", methods=["GET"])
def get_capabilities():
    trace_id = get_trace_id(request)
    from backend.bailian_qa import BailianQA
    from backend.copaw_bridge import CoPawBridge
    copaw = CoPawBridge()
    bailian = BailianQA()
    return _ok({
        "copaw_configured": copaw.configured,
        "bailian_configured": bailian.configured,
        "model": "qwen-max" if bailian.configured else None,
    }, trace_id)


# ========== POST /sessions (T-012) ==========

@agent_bp.route("/sessions", methods=["POST"])
def create_session():
    trace_id = get_trace_id(request)
    data = request.get_json(silent=True) or {}
    title = data.get("title", "新会话")
    if len(title) > 100:
        return _error("INVALID_SESSION_TITLE", "会话标题过长，最多100字符", trace_id, 400)
    session_id = str(uuid.uuid4())
    session = storage.create_session(session_id, title)
    return _ok({
        "session_id": session["session_id"],
        "title": session["title"],
        "created_at": session["created_at"],
        "query_count": session["query_count"],
    }, trace_id, 201)


# ========== GET /sessions (T-012) ==========

@agent_bp.route("/sessions", methods=["GET"])
def get_sessions():
    trace_id = get_trace_id(request)
    sessions = storage.get_sessions()
    return _ok({"sessions": sessions}, trace_id)


# ========== DELETE /sessions/<id> (T-012) ==========

@agent_bp.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    trace_id = get_trace_id(request)
    session = storage.get_session(session_id)
    if not session:
        return _error("SESSION_NOT_FOUND", "会话不存在", trace_id, 404)
    deleted_records = storage.delete_session(session_id)
    return _ok({
        "message": "会话已删除",
        "deleted_records": deleted_records,
    }, trace_id)


# ========== POST /ask (T-024) ==========

@agent_bp.route("/ask", methods=["POST"])
def ask_question():
    trace_id = get_trace_id(request)
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    session_id = data.get("session_id", "")

    # Validation
    if not session_id or not session_id.strip():
        return _error("MISSING_SESSION_ID", "缺少 session_id", trace_id, 400)
    if not query or not query.strip():
        return _error("EMPTY_QUERY", "请输入问题", trace_id, 400)
    if len(query) > 500:
        return _error("INVALID_QUERY", "问题过长，请控制在500字符以内", trace_id, 400)

    session = storage.get_session(session_id)
    if not session:
        return _error("SESSION_NOT_FOUND", "会话不存在", trace_id, 404)

    result = agent.ask(query.strip(), session_id)
    return _ok({
        "answer": result["answer"],
        "llm_used": result["llm_used"],
        "model": result["model"],
        "response_time_ms": result["response_time_ms"],
        "answer_source": result["answer_source"],
    }, trace_id)


# ========== GET /sessions/<id>/records (T-025) ==========

@agent_bp.route("/sessions/<session_id>/records", methods=["GET"])
def get_records(session_id):
    trace_id = get_trace_id(request)
    session = storage.get_session(session_id)
    if not session:
        return _error("SESSION_NOT_FOUND", "会话不存在", trace_id, 404)
    records = storage.get_records_by_session(session_id)
    return _ok({
        "session_id": session_id,
        "records": records,
    }, trace_id)
