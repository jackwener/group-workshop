"""
Flask 应用主入口 - 研报智能分析助手 M5-RA
集成 Swagger 文档 (flask-restx)
"""
import os
import uuid
import time
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, Namespace
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

# 全局 CORS 处理 - 覆盖所有响应（用赋值而非add，防止重复）
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,OPTIONS'
    return response

# 处理所有 OPTIONS 预检请求
@app.route('/api/v1/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = app.make_response('')
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE,OPTIONS'
    return response

# 初始化 Flask-RESTX Api（不使用 prefix，手动加路径）
api = Api(
    app,
    version='1.0',
    title='研报智能分析助手 API',
    description='研报智能分析助手 - 支持会话管理、文件上传、智能问答',
    doc='/swagger'
)

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


# ==================== API 模型定义 ====================

# 错误响应模型
error_model = api.model('Error', {
    'code': fields.String(description='错误码'),
    'message': fields.String(description='错误信息'),
    'details': fields.Raw(description='详细错误信息'),
    'traceId': fields.String(description='链路追踪ID')
})

# 会话模型
session_model = api.model('Session', {
    'session_id': fields.String(description='会话唯一标识'),
    'title': fields.String(description='会话标题'),
    'created_at': fields.String(description='创建时间(ISO-8601)'),
    'updated_at': fields.String(description='最后更新时间(ISO-8601)'),
    'query_count': fields.Integer(description='累计问答次数'),
    'status': fields.String(description='状态: active/archived/deleted')
})

# 问答记录模型
record_model = api.model('QARecord', {
    'id': fields.String(description='记录唯一标识'),
    'session_id': fields.String(description='所属会话ID'),
    'file_id': fields.String(description='关联文件ID'),
    'query': fields.String(description='用户提问原文'),
    'answer': fields.String(description='AI回答内容'),
    'llm_used': fields.Boolean(description='是否使用真实LLM'),
    'model': fields.String(description='模型标识'),
    'response_time_ms': fields.Integer(description='响应耗时(毫秒)'),
    'answer_source': fields.String(description='回答来源: copaw/bailian/demo'),
    'timestamp': fields.String(description='记录时间(ISO-8601)')
})

# 文件信息模型
file_model = api.model('ReportFile', {
    'file_id': fields.String(description='文件唯一标识'),
    'session_id': fields.String(description='所属会话ID'),
    'file_name': fields.String(description='原始文件名'),
    'file_size': fields.Integer(description='文件大小(字节)'),
    'file_type': fields.String(description='文件类型: pdf/doc/docx'),
    'parse_status': fields.String(description='解析状态: pending/parsing/completed/failed'),
    'parse_progress': fields.Integer(description='解析进度 0-100'),
    'parse_result': fields.Raw(description='解析结果'),
    'created_at': fields.String(description='上传时间(ISO-8601)'),
    'updated_at': fields.String(description='更新时间(ISO-8601)')
})

# 能力状态模型
capability_model = api.model('Capability', {
    'traceId': fields.String(description='链路追踪ID'),
    'copaw_configured': fields.Boolean(description='CoPaw是否已配置'),
    'bailian_configured': fields.Boolean(description='百炼是否已配置'),
    'model': fields.String(description='当前使用的模型名')
})

# 问答请求模型
ask_request_model = api.model('AskRequest', {
    'query': fields.String(required=True, description='用户提问原文(1-500字符)'),
    'session_id': fields.String(required=True, description='目标会话ID'),
    'file_id': fields.String(description='关联研报文件ID(可选)')
})

# 问答响应模型
ask_response_model = api.model('AskResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'answer': fields.String(description='答案文本'),
    'llm_used': fields.Boolean(description='是否使用真实LLM'),
    'model': fields.String(description='模型标识'),
    'response_time_ms': fields.Integer(description='响应耗时(毫秒)'),
    'answer_source': fields.String(description='回答来源: copaw/bailian/demo')
})


# ==================== Namespace 定义 ====================

ns_capabilities = api.namespace('api/v1/capabilities', description='系统能力探测')
ns_sessions = api.namespace('api/v1/sessions', description='会话管理')
ns_files = api.namespace('api/v1/files', description='文件管理')
ns_ask = api.namespace('api/v1/ask', description='问答提交')


# ==================== 健康检查 API ====================

@ns_capabilities.route('/')
class Capabilities(Resource):
    @ns_capabilities.doc('get_capabilities')
    @ns_capabilities.marshal_with(capability_model)
    def get(self):
        """获取系统能力状态"""
        caps = agent.get_capabilities()
        return {'traceId': generate_trace_id(), **caps}


# ==================== 会话管理 API ====================

@ns_sessions.route('/')
class SessionList(Resource):
    @ns_sessions.doc('list_sessions')
    @ns_sessions.marshal_with(api.model('SessionList', {
        'traceId': fields.String,
        'sessions': fields.List(fields.Nested(session_model))
    }))
    def get(self):
        """获取会话列表"""
        sessions = storage.get_sessions()
        return {'traceId': generate_trace_id(), 'sessions': sessions}

    @ns_sessions.doc('create_session')
    @ns_sessions.expect(api.model('CreateSessionRequest', {
        'title': fields.String(description='会话标题', default='新会话')
    }))
    @ns_sessions.marshal_with(session_model, code=201)
    def post(self):
        """创建新会话"""
        data = request.get_json() or {}
        title = data.get("title", "新会话")
        session = storage.create_session(title=title)
        session['traceId'] = generate_trace_id()
        return session, 201


@ns_sessions.route('/<string:session_id>')
@ns_sessions.param('session_id', '会话ID')
class SessionDetail(Resource):
    @ns_sessions.doc('delete_session')
    @ns_sessions.marshal_with(api.model('DeleteResponse', {
        'traceId': fields.String,
        'deleted': fields.Boolean,
        'deleted_records': fields.Integer
    }))
    def delete(self, session_id):
        """删除会话（级联删除问答记录）"""
        session = storage.get_session(session_id)
        if not session:
            api.abort(404, '会话不存在', code='SESSION_NOT_FOUND')
        
        deleted_records = storage.delete_records_by_session(session_id)
        storage.delete_session(session_id)
        
        return {
            'traceId': generate_trace_id(),
            'deleted': True,
            'deleted_records': deleted_records
        }


@ns_sessions.route('/<string:session_id>/records')
@ns_sessions.param('session_id', '会话ID')
class SessionRecords(Resource):
    @ns_sessions.doc('get_session_records')
    @ns_sessions.marshal_with(api.model('RecordsResponse', {
        'traceId': fields.String,
        'records': fields.List(fields.Nested(record_model))
    }))
    def get(self, session_id):
        """获取会话的问答记录"""
        session = storage.get_session(session_id)
        if not session:
            api.abort(404, '会话不存在', code='SESSION_NOT_FOUND')
        
        records = storage.get_records_by_session(session_id)
        return {'traceId': generate_trace_id(), 'records': records}


# ==================== 文件上传 API ====================

@ns_files.route('/upload')
class FileUpload(Resource):
    @ns_files.doc('upload_file')
    @ns_files.expect(api.parser()
        .add_argument('session_id', required=True, help='所属会话ID')
        .add_argument('file', type='FileStorage', location='files', required=True, help='PDF/Word文件'))
    @ns_files.marshal_with(file_model, code=201)
    def post(self):
        """上传研报文件"""
        session_id = request.form.get("session_id")
        
        if not session_id:
            api.abort(400, '缺少 session_id', code='INVALID_SESSION_ID')
        
        session = storage.get_session(session_id)
        if not session:
            api.abort(404, '会话不存在', code='SESSION_NOT_FOUND')
        
        if "file" not in request.files:
            api.abort(400, '未上传文件', code='EMPTY_FILE')
        
        file = request.files["file"]
        if file.filename == "":
            api.abort(400, '文件名为空', code='EMPTY_FILE')
        
        # 检查文件类型
        allowed_extensions = {".pdf", ".doc", ".docx"}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            api.abort(400, '仅支持 PDF/Word 格式', code='FILE_TYPE_INVALID')
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            api.abort(400, '文件大小超过100MB限制', code='FILE_TOO_LARGE')
        
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
            file_type=file_ext[1:],
            file_path=file_path
        )
        
        # 异步启动文件解析
        def parse_async():
            try:
                storage.update_parse_status(file_info["file_id"], "parsing", parse_progress=0)
                
                def progress_callback(progress):
                    storage.update_parse_status(file_info["file_id"], "parsing", parse_progress=progress)
                
                result = parse_file(file_path, file_ext[1:], progress_callback)
                
                if result.get("success"):
                    storage.update_parse_status(
                        file_info["file_id"], "completed",
                        parse_progress=100, parse_result=result
                    )
                else:
                    storage.update_parse_status(
                        file_info["file_id"], "failed",
                        parse_result={"error": result.get("error")}
                    )
            except Exception as e:
                storage.update_parse_status(
                    file_info["file_id"], "failed",
                    parse_result={"error": str(e)}
                )
        
        thread = threading.Thread(target=parse_async)
        thread.daemon = True
        thread.start()
        
        file_info['traceId'] = generate_trace_id()
        return file_info, 201


@ns_files.route('/<string:file_id>/status')
@ns_files.param('file_id', '文件ID')
class FileStatus(Resource):
    @ns_files.doc('get_file_status')
    @ns_files.marshal_with(api.model('FileStatusResponse', {
        'traceId': fields.String,
        'file_id': fields.String,
        'parse_status': fields.String,
        'parse_progress': fields.Integer,
        'parse_result': fields.Raw
    }))
    def get(self, file_id):
        """获取文件解析状态"""
        file_info = storage.get_file(file_id)
        if not file_info:
            api.abort(404, '文件不存在', code='FILE_NOT_FOUND')
        
        return {
            'traceId': generate_trace_id(),
            'file_id': file_info["file_id"],
            'parse_status': file_info["parse_status"],
            'parse_progress': file_info.get("parse_progress"),
            'parse_result': file_info.get("parse_result")
        }


# ==================== 问答提交 API ====================

@ns_ask.route('/')
class AskQuestion(Resource):
    @ns_ask.doc('ask_question')
    @ns_ask.expect(ask_request_model)
    @ns_ask.marshal_with(ask_response_model)
    def post(self):
        """提交问答"""
        data = request.get_json() or {}
        
        query = data.get("query", "").strip()
        session_id = data.get("session_id")
        file_id = data.get("file_id")
        
        # 参数校验
        if not query:
            api.abort(400, '请输入问题', code='EMPTY_QUERY')
        
        if len(query) > 500:
            api.abort(400, '问题过长，最多500字符', code='INVALID_QUERY')
        
        if not session_id:
            api.abort(400, '缺少 session_id', code='INVALID_QUERY')
        
        session = storage.get_session(session_id)
        if not session:
            api.abort(404, '会话不存在', code='SESSION_NOT_FOUND')
        
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
        
        return {
            'traceId': generate_trace_id(),
            'answer': answer,
            'llm_used': llm_used,
            'model': model,
            'response_time_ms': response_time_ms,
            'answer_source': answer_source
        }


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return error_response("NOT_FOUND", "接口不存在", 404)


@app.errorhandler(500)
def internal_error(error):
    return error_response("UPSTREAM_ERROR", "服务器内部错误", 500)


if __name__ == '__main__':
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
