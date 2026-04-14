"""Agent Blueprint - all API endpoints under /api/v1/agent."""

import os
import uuid
import time

from flask import Blueprint, request, jsonify, current_app
from storage import Storage

agent_bp = Blueprint("agent_bp", __name__)


def _get_storage():
    data_dir = current_app.config.get("DATA_DIR", "data")
    return Storage(data_dir=data_dir)


def _trace_id():
    """T-008: Generate traceId - reuse X-Trace-Id header or create new."""
    existing = request.headers.get("X-Trace-Id")
    if existing:
        return existing
    return f"tr_{uuid.uuid4().hex}"


def _ok(data, status=200):
    """Build success response with traceId."""
    data["traceId"] = _trace_id()
    return jsonify(data), status


def _error(code, message, http_status=400, details=None):
    """Build error response."""
    return jsonify({
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "traceId": _trace_id(),
        }
    }), http_status


# ── T-027: GET /capabilities ──

@agent_bp.route("/capabilities", methods=["GET"])
def get_capabilities():
    copaw_configured = bool(os.environ.get("IRA_COPAW_CHAT_URL"))
    bailian_configured = bool(os.environ.get("DASHSCOPE_API_KEY"))
    return _ok({
        "copaw_configured": copaw_configured,
        "bailian_configured": bailian_configured,
    })


# ── T-009: POST /sessions ──

@agent_bp.route("/sessions", methods=["POST"])
def create_session():
    body = request.get_json(silent=True) or {}
    title = body.get("title", "新会话")

    if len(title) > 100:
        return _error("INVALID_TITLE", "标题过长，最多100字符")

    storage = _get_storage()
    session_id = str(uuid.uuid4())
    session = storage.create_session(session_id, title)

    return _ok({
        "session_id": session["session_id"],
        "title": session["title"],
        "created_at": session["created_at"],
        "query_count": session["query_count"],
    }, 201)


# ── T-010: GET /sessions ──

@agent_bp.route("/sessions", methods=["GET"])
def get_sessions():
    storage = _get_storage()
    sessions = storage.get_sessions()
    return _ok({
        "sessions": [
            {
                "id": s["session_id"],
                "title": s["title"],
                "created_at": s["created_at"],
                "updated_at": s["updated_at"],
                "query_count": s["query_count"],
            }
            for s in sessions
        ],
        "total": len(sessions),
    })


# ── T-011: DELETE /sessions/<id> ──

@agent_bp.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    storage = _get_storage()
    session = storage.get_session_by_id(session_id)
    if not session:
        return _error("NOT_FOUND", "会话不存在", 404, {"resource": "session"})

    storage.delete_session(session_id)
    return _ok({
        "deleted": True,
        "session_id": session_id,
    })


# ── T-028: POST /ask ──

@agent_bp.route("/ask", methods=["POST"])
def ask():
    body = request.get_json(silent=True) or {}
    query = body.get("query", "")
    session_id = body.get("session_id", "")
    report_id = body.get("report_id")

    # Validate query
    if not query or not query.strip():
        return _error("EMPTY_QUERY", "请输入问题")
    if len(query) > 500:
        return _error("INVALID_QUERY", "问题过长，最多500字符", 400, {"max_length": 500})

    # Validate session
    storage = _get_storage()
    session = storage.get_session_by_id(session_id)
    if not session:
        return _error("INVALID_SESSION", "会话不存在或已失效")

    # Call agent
    from agent import Agent
    agent = Agent()
    start_time = time.time()
    result = agent.ask(query, session_id)
    elapsed_ms = int((time.time() - start_time) * 1000)

    # Write record
    record = storage.add_record(
        session_id=session_id,
        query=query,
        answer=result["answer"],
        llm_used=result["llm_used"],
        model=result["model"],
        response_time_ms=elapsed_ms,
        answer_source=result["answer_source"],
    )

    from storage import Storage
    now = Storage._now_iso()

    return _ok({
        "answer": result["answer"],
        "llm_used": result["llm_used"],
        "model": result["model"],
        "response_time_ms": elapsed_ms,
        "answer_source": result["answer_source"],
        "session_id": session_id,
        "timestamp": now,
    })


# ── T-029: GET /sessions/<id>/records ──

@agent_bp.route("/sessions/<session_id>/records", methods=["GET"])
def get_records(session_id):
    storage = _get_storage()
    session = storage.get_session_by_id(session_id)
    if not session:
        return _error("NOT_FOUND", "会话不存在", 404, {"resource": "session"})

    records = storage.get_records_by_session(session_id)
    return _ok({
        "session_id": session_id,
        "records": [
            {
                "id": r["id"],
                "query": r["query"],
                "answer": r["answer"],
                "timestamp": r["timestamp"],
                "llm_used": r["llm_used"],
                "answer_source": r["answer_source"],
            }
            for r in records
        ],
    })


# ── T-049: POST /reports ──

@agent_bp.route("/reports", methods=["POST"])
def upload_report():
    storage = _get_storage()

    # Validate file
    if "file" not in request.files:
        return _error("INVALID_FILE_FORMAT", "请上传研报文件", 400,
                       {"supported_formats": ["pdf", "html"]})

    file = request.files["file"]
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ("pdf", "html"):
        return _error("INVALID_FILE_FORMAT", "仅支持PDF或HTML格式研报", 400,
                       {"supported_formats": ["pdf", "html"]})

    # Check file size (10MB limit)
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    if file_size > 10 * 1024 * 1024:
        return _error("FILE_TOO_LARGE", "文件过大，请上传小于10MB的文件", 400,
                       {"max_size": "10MB"})

    # Validate session
    session_id = request.form.get("session_id", "")
    if not session_id:
        return _error("INVALID_SESSION", "会话不存在或已失效")

    session = storage.get_session_by_id(session_id)
    if not session:
        return _error("INVALID_SESSION", "会话不存在或已失效")

    # Save uploaded file
    upload_dir = os.path.join(storage.data_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    report_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{report_id}.{ext}")
    file.save(file_path)

    # Parse report
    from report_parser import ReportParser
    parser = ReportParser()
    try:
        if ext == "pdf":
            parsed = parser.parse_pdf(file_path)
        else:
            parsed = parser.parse_html(file_path)

        file_data = {
            "title": parsed.get("title", filename),
            "rating": parsed.get("rating", ""),
            "target_price": parsed.get("target_price", ""),
            "core_views": parsed.get("core_views", []),
            "full_content": parsed.get("full_content", ""),
            "file_path": file_path,
        }

        report = storage.create_report(report_id, session_id, file_data)
        # Update status to completed
        storage.update_report(report_id, status="completed")
        report["status"] = "completed"
    except Exception:
        file_data = {
            "title": filename,
            "rating": "",
            "target_price": "",
            "core_views": [],
            "full_content": "",
            "file_path": file_path,
        }
        report = storage.create_report(report_id, session_id, file_data)
        storage.update_report(report_id, status="failed")
        report["status"] = "failed"

    return _ok({
        "report_id": report["report_id"],
        "title": report["title"],
        "rating": report["rating"],
        "target_price": report["target_price"],
        "core_views": report["core_views"],
        "parsed_at": report["parsed_at"],
        "status": report["status"],
    }, 201)


# ── T-050: GET /reports ──

@agent_bp.route("/reports", methods=["GET"])
def get_reports():
    storage = _get_storage()
    keyword = request.args.get("keyword")
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)

    if keyword and len(keyword) > 100:
        return _error("INVALID_QUERY", "搜索关键词过长，最多100字符")

    result = storage.get_reports(keyword=keyword, page=page, page_size=page_size)
    return _ok({
        "reports": [
            {
                "id": r["report_id"],
                "title": r["title"],
                "rating": r["rating"],
                "target_price": r["target_price"],
                "parsed_at": r["parsed_at"],
            }
            for r in result["reports"]
        ],
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
    })


# ── T-051: GET /reports/<id> ──

@agent_bp.route("/reports/<report_id>", methods=["GET"])
def get_report(report_id):
    storage = _get_storage()
    report = storage.get_report_by_id(report_id)
    if not report:
        return _error("NOT_FOUND", "研报不存在", 404, {"resource": "report"})

    return _ok({
        "report_id": report["report_id"],
        "title": report["title"],
        "rating": report["rating"],
        "target_price": report["target_price"],
        "core_views": report["core_views"],
        "full_content": report["full_content"],
        "parsed_at": report["parsed_at"],
        "session_id": report["session_id"],
    })


# ── T-052: DELETE /reports/<id> ──

@agent_bp.route("/reports/<report_id>", methods=["DELETE"])
def delete_report(report_id):
    storage = _get_storage()
    report = storage.get_report_by_id(report_id)
    if not report:
        return _error("NOT_FOUND", "研报不存在", 404, {"resource": "report"})

    storage.delete_report(report_id)
    return _ok({
        "deleted": True,
        "report_id": report_id,
    })
