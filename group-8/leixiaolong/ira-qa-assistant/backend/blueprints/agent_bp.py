from flask import Blueprint, request, current_app

from response_helper import ok, error
from storage import Storage
from agent import CoPawAgent

agent_bp = Blueprint("agent", __name__)


def get_storage():
    data_dir = current_app.config["DATA_DIR"]
    return Storage(data_dir)


# ─── S1: Session Management ──────────────────────────────────

@agent_bp.route("/sessions", methods=["GET"])
def list_sessions():
    storage = get_storage()
    sessions = storage.get_sessions()
    return ok(sessions=sessions)


@agent_bp.route("/sessions", methods=["POST"])
def create_session():
    storage = get_storage()
    data = request.get_json(silent=True) or {}
    title = data.get("title", "新会话")

    max_title = current_app.config.get("MAX_TITLE_LENGTH", 100)
    if len(title) > max_title:
        return error("INVALID_TITLE", "会话标题不能超过100字符",
                      {"max_length": max_title}, 400)

    session = storage.create_session(title=title)
    return ok(status_code=201,
              session_id=session["session_id"],
              title=session["title"],
              created_at=session["created_at"],
              updated_at=session["updated_at"],
              query_count=session["query_count"])


@agent_bp.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    storage = get_storage()

    if not Storage.is_valid_uuid(session_id):
        return error("INVALID_SESSION_ID", "无效的会话ID格式", {}, 400)

    if storage.get_session_by_id(session_id) is None:
        return error("SESSION_NOT_FOUND", "会话不存在",
                      {"session_id": session_id}, 404)

    storage.delete_session(session_id)
    return ok(message="会话已删除", deleted_session_id=session_id)


# ─── S2: Q&A Core ────────────────────────────────────────────

@agent_bp.route("/ask", methods=["POST"])
def ask_question():
    storage = get_storage()
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    session_id = data.get("session_id", "")

    # Validate query
    if not query or not query.strip():
        return error("EMPTY_QUERY", "请输入问题", {}, 400)

    max_query = current_app.config.get("MAX_QUERY_LENGTH", 500)
    if len(query) > max_query:
        return error("INVALID_QUERY", "问题过长",
                      {"max_length": max_query}, 400)

    # Validate session_id
    if not session_id or not Storage.is_valid_uuid(session_id):
        return error("INVALID_SESSION_ID", "无效的会话ID格式", {}, 400)

    if storage.get_session_by_id(session_id) is None:
        return error("SESSION_NOT_FOUND", "会话不存在",
                      {"session_id": session_id}, 404)

    agent = CoPawAgent(storage)
    result = agent.ask(query, session_id)
    return ok(**result)


@agent_bp.route("/sessions/<session_id>/records", methods=["GET"])
def get_records(session_id):
    storage = get_storage()

    if not Storage.is_valid_uuid(session_id):
        return error("INVALID_SESSION_ID", "无效的会话ID格式", {}, 400)

    if storage.get_session_by_id(session_id) is None:
        return error("SESSION_NOT_FOUND", "会话不存在",
                      {"session_id": session_id}, 404)

    records = storage.get_records_by_session(session_id)
    return ok(records=records)
