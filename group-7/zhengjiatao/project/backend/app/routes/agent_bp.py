from flask import Blueprint, request, jsonify
import uuid
import time
import re
from app.services.storage import get_storage
from app.services.agent import get_agent

agent_bp = Blueprint("agent", __name__)
storage = get_storage()
agent = get_agent()


def generate_trace_id():
    """生成链路追踪ID"""
    return f"tr_{uuid.uuid4().hex[:16]}_{int(time.time())}"


def success_response(data=None, trace_id=None):
    """统一成功响应格式"""
    response = {"traceId": trace_id or generate_trace_id()}
    if data:
        response.update(data)
    return jsonify(response)


def error_response(code, message, details=None, status_code=400):
    """统一错误响应格式"""
    error = {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "traceId": generate_trace_id()
        }
    }
    return jsonify(error), status_code


def is_valid_uuid(value):
    """验证UUID格式"""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, value, re.IGNORECASE))


# ==================== Session API ====================

@agent_bp.route("/sessions", methods=["GET"])
def get_sessions():
    """
    获取会话列表
    GET /api/v1/agent/sessions
    """
    sessions = storage.get_sessions()
    
    # 转换为API响应格式
    response_sessions = []
    for session in sessions:
        response_sessions.append({
            "session_id": session["session_id"],
            "title": session["title"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
            "query_count": session["query_count"]
        })
    
    return success_response({"sessions": response_sessions})


@agent_bp.route("/sessions", methods=["POST"])
def create_session():
    """
    创建新会话
    POST /api/v1/agent/sessions
    
    请求体:
    {
        "title": "会话标题" (可选, 默认"新会话")
    }
    """
    data = request.get_json() or {}
    title = data.get("title", "新会话")
    
    # 验证title长度
    if len(title) > 23:
        return error_response(
            "INVALID_TITLE",
            "会话标题过长",
            {"max_length": 23},
            400
        )
    
    # 创建会话
    session = storage.create_session(title=title)
    
    return success_response({
        "session_id": session["session_id"],
        "title": session["title"],
        "created_at": session["created_at"],
        "query_count": session["query_count"]
    }), 201


@agent_bp.route("/sessions/<session_id>", methods=["PUT"])
def update_session(session_id):
    """
    更新会话标题
    PUT /api/v1/agent/sessions/<session_id>
    
    请求体:
    {
        "title": "新标题" (必填, ≤100字符)
    }
    """
    # 验证session_id格式
    if not session_id or not is_valid_uuid(session_id):
        return error_response(
            "INVALID_SESSION_ID",
            "会话ID格式无效",
            {},
            400
        )
    
    # 检查会话是否存在
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            {"session_id": session_id},
            404
        )
    
    # 获取请求数据
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    
    # 验证title
    if not title:
        return error_response(
            "INVALID_TITLE",
            "会话标题不能为空",
            {},
            400
        )
    
    if len(title) > 100:
        return error_response(
            "INVALID_TITLE",
            "会话标题过长",
            {"max_length": 100},
            400
        )
    
    # 更新会话
    updated_session = storage.update_session(session_id, {"title": title})
    
    return success_response({
        "session_id": updated_session["session_id"],
        "title": updated_session["title"],
        "updated_at": updated_session["updated_at"]
    })


@agent_bp.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    """
    删除会话
    DELETE /api/v1/agent/sessions/<session_id>
    """
    # 验证session_id格式
    if not session_id or not is_valid_uuid(session_id):
        return error_response(
            "INVALID_SESSION_ID",
            "会话ID格式无效",
            {},
            400
        )
    
    # 检查会话是否存在
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            {"session_id": session_id},
            404
        )
    
    # 删除会话（级联删除记录）
    deleted_records_count = storage.delete_session(session_id)
    
    return success_response({
        "deleted": True,
        "session_id": session_id
    })


# ==================== Ask API ====================

@agent_bp.route("/ask", methods=["POST"])
def ask():
    """
    问答提交
    POST /api/v1/agent/ask
    
    请求体:
    {
        "query": "用户问题" (必填, 1-500字符),
        "session_id": "会话ID" (必填, UUID格式)
    }
    """
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    session_id = data.get("session_id", "")
    
    # 参数校验
    if not query:
        return error_response(
            "EMPTY_QUERY",
            "请输入问题",
            {},
            400
        )
    
    if len(query) > 500:
        return error_response(
            "INVALID_QUERY",
            "问题过长",
            {"max_length": 500},
            400
        )
    
    if not session_id:
        return error_response(
            "INVALID_QUERY",
            "缺少session_id",
            {},
            400
        )
    
    if not is_valid_uuid(session_id):
        return error_response(
            "INVALID_SESSION_ID",
            "会话ID格式无效",
            {},
            400
        )
    
    # 检查会话是否存在
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            {"session_id": session_id},
            404
        )
    
    # 调用Agent获取回答
    result = agent.ask(query)
    
    # 保存问答记录
    try:
        storage.add_record(
            session_id=session_id,
            query=query,
            answer=result["answer"],
            llm_used=result["llm_used"],
            model=result["model"],
            response_time_ms=result["response_time_ms"],
            answer_source=result["answer_source"]
        )
    except Exception as e:
        print(f"保存问答记录失败: {e}")
    
    return success_response({
        "answer": result["answer"],
        "llm_used": result["llm_used"],
        "model": result["model"],
        "response_time_ms": result["response_time_ms"],
        "answer_source": result["answer_source"]
    })


# ==================== Capabilities API ====================

@agent_bp.route("/capabilities", methods=["GET"])
def get_capabilities():
    """
    获取系统能力状态
    GET /api/v1/agent/capabilities
    """
    caps = agent.get_capabilities()
    return success_response(caps)


# ==================== System Status API ====================

@agent_bp.route("/system-status", methods=["GET"])
def get_system_status():
    """
    获取系统健康状态和资源监控
    GET /api/v1/agent/system-status
    """
    status = agent.get_system_status()
    return success_response(status)


# ==================== Records API ====================

@agent_bp.route("/sessions/<session_id>/records", methods=["GET"])
def get_records(session_id):
    """
    获取会话的问答记录
    GET /api/v1/agent/sessions/<session_id>/records
    """
    # 验证session_id格式
    if not session_id or not is_valid_uuid(session_id):
        return error_response(
            "INVALID_SESSION_ID",
            "会话ID格式无效",
            {},
            400
        )
    
    # 检查会话是否存在
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            {"session_id": session_id},
            404
        )
    
    # 获取记录
    records = storage.get_records_by_session(session_id)
    
    return success_response({"records": records})


# ==================== Export API ====================

@agent_bp.route("/sessions/<session_id>/export", methods=["GET"])
def export_session(session_id):
    """
    导出会话记录
    GET /api/v1/agent/sessions/<session_id>/export?format=json|txt
    """
    # 获取format参数
    format_type = request.args.get("format", "json").lower()
    
    # 验证format参数
    if format_type not in ["json", "txt"]:
        return error_response(
            "INVALID_FORMAT",
            "导出格式无效，仅支持json或txt",
            {},
            400
        )
    
    # 验证session_id格式
    if not session_id or not is_valid_uuid(session_id):
        return error_response(
            "INVALID_SESSION_ID",
            "会话ID格式无效",
            {},
            400
        )
    
    # 检查会话是否存在
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            {"session_id": session_id},
            404
        )
    
    # 获取记录
    records = storage.get_records_by_session(session_id)
    
    # 检查是否有记录可导出
    if not records:
        return error_response(
            "EMPTY_SESSION",
            "会话无问答记录可导出",
            {},
            400
        )
    
    # 生成导出内容
    import os
    import tempfile
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"session_{session_id[:8]}_{timestamp}.{format_type}"
    
    if format_type == "json":
        # JSON格式
        export_data = {
            "session": {
                "session_id": session["session_id"],
                "title": session["title"],
                "created_at": session["created_at"],
                "query_count": session["query_count"]
            },
            "records": records,
            "exported_at": datetime.now().isoformat()
        }
        content = json.dumps(export_data, ensure_ascii=False, indent=2)
    else:
        # TXT格式
        lines = [
            f"会话: {session['title']}",
            f"会话ID: {session['session_id']}",
            f"创建时间: {session['created_at']}",
            f"问答数量: {session['query_count']}",
            "=" * 50,
            ""
        ]
        
        for i, record in enumerate(records, 1):
            lines.extend([
                f"【问答 {i}】",
                f"时间: {record['timestamp']}",
                f"来源: {record['answer_source']}",
                f"模型: {record.get('model', 'N/A')}",
                f"耗时: {record['response_time_ms']}ms",
                "-" * 30,
                f"问题: {record['query']}",
                "",
                f"回答: {record['answer']}",
                "",
                "=" * 50,
                ""
            ])
        
        content = "\n".join(lines)
    
    # 保存到临时文件
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    # 返回下载链接（简化处理，实际应该使用安全的文件服务）
    # 这里直接返回文件内容
    from flask import send_file
    
    return send_file(
        file_path,
        mimetype="application/json" if format_type == "json" else "text/plain",
        as_attachment=True,
        download_name=filename
    )
