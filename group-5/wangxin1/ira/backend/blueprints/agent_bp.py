"""
Agent API 蓝图
实现所有 API 端点
对齐 09-API接口规格
"""
import uuid
from flask import Blueprint, request, jsonify
from storage import get_storage
from agent import get_agent

# 创建蓝图
agent_bp = Blueprint('agent', __name__, url_prefix='/api/v1/agent')


def generate_trace_id() -> str:
    """生成 traceId"""
    return f"tr_{uuid.uuid4().hex}"


def success_response(data: dict, trace_id: str = None) -> tuple:
    """构建成功响应"""
    if trace_id is None:
        trace_id = generate_trace_id()
    return jsonify({
        "traceId": trace_id,
        **data
    })


def error_response(code: str, message: str, http_status: int = 400, details: dict = None) -> tuple:
    """构建错误响应"""
    error_body = {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "traceId": generate_trace_id()
        }
    }
    return jsonify(error_body), http_status


# ==================== 能力探测与健康检查 ====================

@agent_bp.route('/capabilities', methods=['GET'])
def get_capabilities():
    """
    获取系统能力配置状态
    返回 CoPaw、百炼、Demo 模式的配置状态
    """
    agent = get_agent()
    caps = agent.get_capabilities()
    
    return success_response({
        "capabilities": caps
    })


@agent_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查与降级级别查询
    返回系统健康状态和当前降级级别 (normal/degraded/demo)
    """
    agent = get_agent()
    caps = agent.get_capabilities()
    
    # 确定当前降级级别
    if caps["copaw_configured"]:
        level = "normal"
    elif caps["bailian_configured"]:
        level = "degraded"
    else:
        level = "demo"
    
    return success_response({
        "status": "healthy",
        "copaw_available": caps["copaw_configured"],
        "bailian_available": caps["bailian_configured"],
        "demo_available": True,
        "current_level": level
    })


# ==================== 问答 API ====================

@agent_bp.route('/ask', methods=['POST'])
def ask():
    """
    提交投研问答
    接收用户问题和会话ID，返回AI回答
    请求体: {"query": "问题内容", "session_id": "会话ID"}
    """
    data = request.get_json() or {}
    
    # 参数校验
    query = data.get('query', '').strip()
    session_id = data.get('session_id', '').strip()
    
    if not query:
        return error_response("EMPTY_QUERY", "请输入问题", 400)
    
    if len(query) > 500:
        return error_response("INVALID_QUERY", "问题过长，最多500字符", 400, {"max_length": 500})
    
    if not session_id:
        return error_response("INVALID_QUERY", "缺少 session_id", 400)
    
    # 验证 session 是否存在
    storage = get_storage()
    session = storage.get_session_by_id(session_id)
    if not session:
        return error_response("SESSION_NOT_FOUND", "会话不存在", 404, {"session_id": session_id})
    
    # 调用 Agent 进行问答
    agent = get_agent()
    result = agent.ask(query, session_id)
    
    # 保存记录
    storage.add_record(
        session_id=session_id,
        query=query,
        answer=result["answer"],
        llm_used=result["llm_used"],
        model=result["model"],
        answer_source=result["answer_source"],
        response_time_ms=result["response_time_ms"]
    )
    
    return success_response({
        "answer": result["answer"],
        "llm_used": result["llm_used"],
        "model": result["model"],
        "response_time_ms": result["response_time_ms"],
        "answer_source": result["answer_source"]
    })


# ==================== 会话管理 API ====================

@agent_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """
    获取会话列表
    返回所有会话的列表，按更新时间倒序排序
    """
    storage = get_storage()
    sessions = storage.get_sessions()
    
    # 格式化响应
    formatted_sessions = []
    for s in sessions:
        formatted_sessions.append({
            "session_id": s["session_id"],
            "title": s["title"],
            "created_at": s["created_at"],
            "updated_at": s["updated_at"],
            "query_count": s["query_count"]
        })
    
    return success_response({
        "sessions": formatted_sessions
    })


@agent_bp.route('/sessions', methods=['POST'])
def create_session():
    """
    创建新会话
    可选请求体: {"title": "会话标题"}，默认为"新会话"
    """
    data = request.get_json() or {}
    title = data.get('title', '新会话').strip()
    
    # 校验标题长度
    if len(title) > 23:
        return error_response("INVALID_TITLE", "标题过长，最多23字符", 400)
    
    storage = get_storage()
    session = storage.create_session(title)
    
    return success_response({
        "session_id": session["session_id"],
        "title": session["title"],
        "created_at": session["created_at"],
        "updated_at": session["updated_at"],
        "query_count": session["query_count"]
    }), 201


@agent_bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    删除会话
    删除指定会话及其所有问答记录
    """
    if not session_id:
        return error_response("SESSION_NOT_FOUND", "会话ID不能为空", 404)
    
    storage = get_storage()
    success = storage.delete_session(session_id)
    
    if not success:
        return error_response("SESSION_NOT_FOUND", "会话不存在", 404, {"session_id": session_id})
    
    return success_response({
        "success": True,
        "deleted_session_id": session_id
    })


# ==================== 问答记录 API ====================

@agent_bp.route('/sessions/<session_id>/records', methods=['GET'])
def get_session_records(session_id):
    """
    获取会话问答记录
    返回指定会话的所有问答历史记录
    """
    if not session_id:
        return error_response("SESSION_NOT_FOUND", "会话ID不能为空", 404)
    
    # 验证 session 是否存在
    storage = get_storage()
    session = storage.get_session_by_id(session_id)
    if not session:
        return error_response("SESSION_NOT_FOUND", "会话不存在", 404, {"session_id": session_id})
    
    records = storage.get_records_by_session(session_id)
    
    # 格式化响应
    formatted_records = []
    for r in records:
        formatted_records.append({
            "id": r["id"],
            "query": r["query"],
            "answer": r["answer"],
            "llm_used": r["llm_used"],
            "model": r["model"],
            "answer_source": r["answer_source"],
            "response_time_ms": r["response_time_ms"],
            "timestamp": r["timestamp"]
        })
    
    return success_response({
        "records": formatted_records
    })
