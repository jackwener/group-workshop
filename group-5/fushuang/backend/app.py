"""
Flask 应用主入口
研报智能分析助手 - M5-RA
"""
import os
import uuid
import time
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from storage import Storage
from report_agent import get_agent
from pdf_parser import parse_file
import threading

# 加载环境变量
load_dotenv()

# 初始化 Agent
agent = get_agent()

app = Flask(__name__)
CORS(app)  # 允许跨域

# 初始化存储
storage = Storage(data_dir=os.getenv("DATA_DIR", "./data"))


def generate_trace_id() -> str:
    """生成 traceId"""
    return f"tr_{uuid.uuid4().hex}"


def success_response(data: dict, trace_id: str = None, status_code: int = 200):
    """成功响应包装"""
    if trace_id is None:
        trace_id = generate_trace_id()
    response_data = {"traceId": trace_id, **data}
    return jsonify(response_data), status_code


def error_response(code: str, message: str, status: int = 400, details: dict = None) -> tuple:
    """错误响应包装"""
    trace_id = generate_trace_id()
    error_body = {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "traceId": trace_id
        }
    }
    return jsonify(error_body), status


# ==================== 健康检查 API ====================

@app.route('/api/v1/capabilities', methods=['GET'])
def get_capabilities():
    """获取系统能力状态"""
    caps = agent.get_capabilities()
    return success_response(caps)


# ==================== 会话管理 API ====================

@app.route('/api/v1/sessions', methods=['GET'])
def get_sessions():
    """获取会话列表"""
    sessions = storage.get_sessions()
    return success_response({"sessions": sessions})


@app.route('/api/v1/sessions', methods=['POST'])
def create_session():
    """创建新会话"""
    data = request.get_json() or {}
    title = data.get("title", "新会话")
    
    session = storage.create_session(title=title)
    return success_response(session, status_code=201)


@app.route('/api/v1/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """删除会话"""
    # 检查会话是否存在
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            404,
            {"session_id": session_id}
        )
    
    # 级联删除
    deleted_records = storage.delete_records_by_session(session_id)
    storage.delete_session(session_id)
    
    return success_response({
        "deleted": True,
        "deleted_records": deleted_records
    })


@app.route('/api/v1/sessions/<session_id>/records', methods=['GET'])
def get_session_records(session_id):
    """获取会话的问答记录"""
    # 检查会话是否存在
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            404,
            {"session_id": session_id}
        )
    
    records = storage.get_records_by_session(session_id)
    return success_response({"records": records})


# ==================== 文件上传 API ====================

@app.route('/api/v1/files/upload', methods=['POST'])
def upload_file():
    """上传研报文件"""
    session_id = request.form.get("session_id")
    
    if not session_id:
        return error_response(
            "INVALID_SESSION_ID",
            "缺少 session_id",
            400
        )
    
    # 检查会话是否存在
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            404,
            {"session_id": session_id}
        )
    
    # 检查文件
    if "file" not in request.files:
        return error_response(
            "EMPTY_FILE",
            "未上传文件",
            400
        )
    
    file = request.files["file"]
    if file.filename == "":
        return error_response(
            "EMPTY_FILE",
            "文件名为空",
            400
        )
    
    # 检查文件类型
    allowed_extensions = {".pdf", ".doc", ".docx"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return error_response(
            "FILE_TYPE_INVALID",
            "仅支持 PDF/Word 格式",
            400,
            {"allowed_types": ["pdf", "doc", "docx"]}
        )
    
    # 检查文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    max_size = 100 * 1024 * 1024  # 100MB
    if file_size > max_size:
        return error_response(
            "FILE_TOO_LARGE",
            "文件大小超过100MB限制",
            400,
            {"max_size": max_size}
        )
    
    # 保存文件
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}{file_ext}"
    file_path = os.path.join(upload_dir, file_name)
    file.save(file_path)
    
    # 保存元数据
    file_info = storage.save_file(
        session_id=session_id,
        file_name=file.filename,
        file_size=file_size,
        file_type=file_ext[1:],  # 去掉点号
        file_path=file_path
    )
    
    # 异步启动文件解析
    def parse_async():
        try:
            storage.update_parse_status(
                file_info["file_id"],
                "parsing",
                parse_progress=0
            )
            
            def progress_callback(progress):
                storage.update_parse_status(
                    file_info["file_id"],
                    "parsing",
                    parse_progress=progress
                )
            
            result = parse_file(file_path, file_ext[1:], progress_callback)
            
            if result.get("success"):
                storage.update_parse_status(
                    file_info["file_id"],
                    "completed",
                    parse_progress=100,
                    parse_result=result
                )
            else:
                storage.update_parse_status(
                    file_info["file_id"],
                    "failed",
                    parse_result={"error": result.get("error")}
                )
        except Exception as e:
            storage.update_parse_status(
                file_info["file_id"],
                "failed",
                parse_result={"error": str(e)}
            )
    
    thread = threading.Thread(target=parse_async)
    thread.daemon = True
    thread.start()
    
    return success_response(file_info, status_code=201)


@app.route('/api/v1/files/<file_id>/status', methods=['GET'])
def get_file_status(file_id):
    """获取文件解析状态"""
    file_info = storage.get_file(file_id)
    if not file_info:
        return error_response(
            "FILE_NOT_FOUND",
            "文件不存在",
            404,
            {"file_id": file_id}
        )
    
    return success_response({
        "file_id": file_info["file_id"],
        "parse_status": file_info["parse_status"],
        "parse_progress": file_info.get("parse_progress"),
        "parse_result": file_info.get("parse_result")
    })


# ==================== 问答提交 API ====================

@app.route('/api/v1/ask', methods=['POST'])
def ask_question():
    """提交问答"""
    data = request.get_json() or {}
    
    query = data.get("query", "").strip()
    session_id = data.get("session_id")
    file_id = data.get("file_id")
    
    # 参数校验
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
    
    if not session_id:
        return error_response(
            "INVALID_QUERY",
            "缺少 session_id",
            400
        )
    
    # 检查会话是否存在
    session = storage.get_session(session_id)
    if not session:
        return error_response(
            "SESSION_NOT_FOUND",
            "会话不存在",
            404,
            {"session_id": session_id}
        )
    
    # 获取文件内容（如果有）
    file_content = None
    if file_id:
        file_info = storage.get_file(file_id)
        if file_info and file_info.get("parse_result"):
            file_content = file_info["parse_result"].get("text_preview", "")
    
    # 调用 Agent（三级降级策略）
    start_time = time.time()
    answer, llm_used, model, answer_source = agent.ask(query, file_content)
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # 保存记录
    storage.add_record(
        session_id=session_id,
        query=query,
        answer=answer,
        llm_used=llm_used,
        model=model,
        response_time_ms=response_time_ms,
        answer_source=answer_source,
        file_id=file_id
    )
    
    return success_response({
        "answer": answer,
        "llm_used": llm_used,
        "model": model,
        "response_time_ms": response_time_ms,
        "answer_source": answer_source
    })


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return error_response(
        "NOT_FOUND",
        "接口不存在",
        404
    )


@app.errorhandler(500)
def internal_error(error):
    return error_response(
        "UPSTREAM_ERROR",
        "服务器内部错误",
        500
    )


if __name__ == '__main__':
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
