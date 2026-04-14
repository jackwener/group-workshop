import uuid
import time
from flask import request, jsonify, current_app
from flask_restx import Resource
from app.core.config import Config
from app.core.error_handlers import make_response, APIError
from app.services.storage import get_storage
from app.core.api_docs import agent_ns
from app.core.api_docs import capabilities_response
from app.core.api_docs import create_session_request, create_session_response
from app.core.api_docs import sessions_list_response, delete_session_response
from app.core.api_docs import records_list_response, ask_request, ask_response
from app.core.api_docs import upload_report_response, reports_list_response
from app.core.api_docs import delete_report_response, analyze_report_response
from app.core.api_docs import health_response, export_request, export_response

# ==================== 能力探测 ====================

@agent_ns.route('/capabilities')
class CapabilitiesResource(Resource):
    @agent_ns.doc('get_capabilities', description='获取系统能力配置状态')
    @agent_ns.response(200, '成功', capabilities_response)
    def get(self):
        """GET /api/v1/agent/capabilities - 能力探测接口"""
        caps = Config.get_caps()
        
        response_data = {
            'caps': caps
        }
        
        # 添加百炼模型信息
        if caps['bailian_configured']:
            response_data['caps']['bailian_model'] = Config.BAILIAN_MODEL
        
        return make_response(response_data)


# ==================== 会话管理 ====================

@agent_ns.route('/sessions')
class SessionsResource(Resource):
    @agent_ns.doc('create_session', description='新建会话')
    @agent_ns.expect(create_session_request)
    @agent_ns.response(201, '创建成功', create_session_response)
    @agent_ns.response(400, '参数错误', agent_ns.models.get('Error'))
    def post(self):
        """POST /api/v1/agent/sessions - 新建会话"""
        data = request.get_json() or {}
        title = data.get('title', '新会话')
        
        # 参数校验
        if len(title) > 100:
            raise APIError(
                'INVALID_TITLE',
                '会话标题不能超过100字符',
                400,
                {'max_length': 100}
            )
        
        # 生成session_id
        session_id = str(uuid.uuid4())
        
        # 创建会话
        storage = get_storage()
        session = storage.create_session(session_id, title)
        
        return make_response(session), 201
    
    @agent_ns.doc('get_sessions', description='获取会话列表')
    @agent_ns.param('page', '页码，从1开始', type=int, default=1)
    @agent_ns.param('page_size', '每页数量，最大100', type=int, default=20)
    @agent_ns.response(200, '成功', sessions_list_response)
    def get(self):
        """GET /api/v1/agent/sessions - 会话列表"""
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 限制page_size最大100
        page_size = min(page_size, 100)
        page = max(page, 1)
        
        storage = get_storage()
        
        # 获取所有会话（用于计算总数）
        all_sessions = storage._read_json(storage.sessions_file)
        total = len(all_sessions)
        
        # 获取分页数据
        sessions = storage.get_sessions(page, page_size)
        
        return make_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'sessions': sessions
        })


@agent_ns.route('/sessions/<string:session_id>')
class SessionResource(Resource):
    @agent_ns.doc('delete_session', description='删除会话')
    @agent_ns.param('session_id', '会话ID（UUID格式）', required=True)
    @agent_ns.response(200, '删除成功', delete_session_response)
    @agent_ns.response(400, 'ID格式错误', agent_ns.models.get('Error'))
    @agent_ns.response(404, '会话不存在', agent_ns.models.get('Error'))
    def delete(self, session_id):
        """DELETE /api/v1/agent/sessions/<id> - 删除会话"""
        # 校验session_id格式
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise APIError(
                'INVALID_SESSION_ID',
                '会话ID格式错误',
                400,
                {'format': 'UUID'}
            )
        
        storage = get_storage()
        
        # 检查会话是否存在
        session = storage.get_session_by_id(session_id)
        if session is None:
            raise APIError(
                'SESSION_NOT_FOUND',
                '会话不存在',
                404,
                {'session_id': session_id}
            )
        
        # 删除会话
        deleted = storage.delete_session(session_id)
        
        return make_response({
            'deleted': deleted,
            'session_id': session_id
        })


# ==================== 问答记录 ====================

@agent_ns.route('/sessions/<string:session_id>/records')
class SessionRecordsResource(Resource):
    @agent_ns.doc('get_session_records', description='获取会话的问答记录')
    @agent_ns.param('session_id', '会话ID（UUID格式）', required=True)
    @agent_ns.param('page', '页码，从1开始', type=int, default=1)
    @agent_ns.param('page_size', '每页数量，最大100', type=int, default=20)
    @agent_ns.response(200, '成功', records_list_response)
    @agent_ns.response(400, 'ID格式错误', agent_ns.models.get('Error'))
    @agent_ns.response(404, '会话不存在', agent_ns.models.get('Error'))
    def get(self, session_id):
        """GET /api/v1/agent/sessions/<id>/records - 问答记录"""
        # 校验session_id格式
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise APIError(
                'INVALID_SESSION_ID',
                '会话ID格式错误',
                400,
                {'format': 'UUID'}
            )
        
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 限制page_size最大100
        page_size = min(page_size, 100)
        page = max(page, 1)
        
        storage = get_storage()
        
        # 检查会话是否存在
        session = storage.get_session_by_id(session_id)
        if session is None:
            raise APIError(
                'SESSION_NOT_FOUND',
                '会话不存在',
                404,
                {'session_id': session_id}
            )
        
        # 获取所有记录（用于计算总数）
        all_records = storage._read_json(storage.records_file)
        session_records = [r for r in all_records if r['session_id'] == session_id]
        total = len(session_records)
        
        # 获取分页数据
        records = storage.get_records_by_session(session_id, page, page_size)
        
        return make_response({
            'session_id': session_id,
            'total': total,
            'records': records
        })


# ==================== 问答提交 ====================

@agent_ns.route('/ask')
class AskResource(Resource):
    @agent_ns.doc('ask_question', description='提交问题并获取回答')
    @agent_ns.expect(ask_request)
    @agent_ns.response(200, '成功', ask_response)
    @agent_ns.response(400, '参数错误', agent_ns.models.get('Error'))
    @agent_ns.response(404, '会话不存在', agent_ns.models.get('Error'))
    def post(self):
        """POST /api/v1/agent/ask - 问答提交"""
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        session_id = data.get('session_id', '').strip()
        
        # 参数校验
        if not query:
            raise APIError('EMPTY_QUERY', '请输入问题', 400)
        
        if len(query) > 500:
            raise APIError(
                'INVALID_QUERY',
                '问题过长',
                400,
                {'max_length': 500}
            )
        
        if not session_id:
            raise APIError('EMPTY_SESSION_ID', '会话ID不能为空', 400)
        
        # 校验session_id格式
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise APIError(
                'INVALID_SESSION_ID',
                '会话ID格式错误',
                400,
                {'format': 'UUID'}
            )
        
        storage = get_storage()
        
        # 检查会话是否存在
        session = storage.get_session_by_id(session_id)
        if session is None:
            raise APIError(
                'SESSION_NOT_FOUND',
                '会话不存在',
                404,
                {'session_id': session_id}
            )
        
        # 调用Agent进行问答（三级降级）
        start_time = time.time()
        answer, llm_used, model, answer_source = _ask_with_fallback(query)
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # 保存问答记录
        record = storage.add_record(
            session_id=session_id,
            query=query,
            answer=answer,
            llm_used=llm_used,
            model=model,
            response_time_ms=response_time_ms,
            answer_source=answer_source
        )
        
        return make_response({
            'answer': answer,
            'llm_used': llm_used,
            'model': model,
            'response_time_ms': response_time_ms,
            'answer_source': answer_source
        })


def _ask_with_fallback(query: str):
    """三级降级链：CoPaw -> 百炼 -> Demo"""
    caps = Config.get_caps()
    
    # 第一级：CoPaw
    if caps['copaw_configured']:
        try:
            answer = _call_copaw(query)
            return answer, True, 'copaw-model', 'copaw'
        except Exception:
            pass  # 静默降级
    
    # 第二级：百炼
    if caps['bailian_configured']:
        try:
            answer = _call_bailian(query)
            return answer, True, Config.BAILIAN_MODEL, 'bailian'
        except Exception:
            pass  # 静默降级
    
    # 第三级：Demo兜底
    answer = _call_demo(query)
    return answer, False, None, 'demo'


def _call_copaw(query: str) -> str:
    """调用CoPaw API"""
    # TODO: 实现CoPaw API调用
    raise NotImplementedError("CoPaw API not implemented")


def _call_bailian(query: str) -> str:
    """调用百炼DashScope API"""
    # TODO: 实现百炼API调用
    raise NotImplementedError("Bailian API not implemented")


def _call_demo(query: str) -> str:
    """Demo模式 - 纯字符串拼接"""
    return f"【演示模式】您的问题是：{query}\n\n这是一个演示回答。实际使用时，请配置CoPaw或百炼API Key以获取真实的AI回答。"


# ==================== 研报管理 ====================

@agent_ns.route('/reports')
class ReportsResource(Resource):
    @agent_ns.doc('upload_report', description='上传研报文件')
    @agent_ns.param('file', '研报文件，支持pdf/doc/docx，最大50MB', type='file', required=True)
    @agent_ns.param('title', '研报标题，默认使用文件名', type=str)
    @agent_ns.response(201, '上传成功', upload_report_response)
    @agent_ns.response(400, '文件错误', agent_ns.models.get('Error'))
    def post(self):
        """POST /api/v1/agent/reports - 上传研报"""
        # 检查是否有文件
        if 'file' not in request.files:
            raise APIError('EMPTY_FILE', '请选择要上传的文件', 400)
        
        file = request.files['file']
        
        if file.filename == '':
            raise APIError('EMPTY_FILE', '请选择要上传的文件', 400)
        
        # 检查文件类型
        allowed_extensions = {'pdf', 'doc', 'docx'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            raise APIError(
                'INVALID_FILE_TYPE',
                '仅支持 PDF、DOC、DOCX 格式',
                400,
                {'supported': ['pdf', 'doc', 'docx']}
            )
        
        # 获取标题（可选，默认使用文件名）
        title = request.form.get('title', file.filename)
        
        # 生成report_id
        report_id = f"rep_{uuid.uuid4().hex[:12]}"
        
        # 保存文件
        upload_folder = current_app.config.get('UPLOAD_FOLDER', './data/uploads')
        import os
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = f"{report_id}.{file_ext}"
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 创建研报记录
        storage = get_storage()
        report = storage.create_report(report_id, title, file.filename, file_size)
        
        return make_response(report), 201
    
    @agent_ns.doc('get_reports', description='获取研报列表')
    @agent_ns.param('page', '页码，从1开始', type=int, default=1)
    @agent_ns.param('page_size', '每页数量，最大100', type=int, default=20)
    @agent_ns.param('status', '状态筛选：pending/analyzing/analyzed/failed', type=str)
    @agent_ns.response(200, '成功', reports_list_response)
    def get(self):
        """GET /api/v1/agent/reports - 研报列表"""
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        status = request.args.get('status', None)
        
        # 限制page_size最大100
        page_size = min(page_size, 100)
        page = max(page, 1)
        
        storage = get_storage()
        
        # 获取所有研报（用于计算总数）
        all_reports = storage._read_json(storage.reports_file)
        
        # 状态筛选
        if status:
            all_reports = [r for r in all_reports if r.get('status') == status]
        
        total = len(all_reports)
        
        # 获取分页数据
        reports = storage.get_reports(page, page_size, status)
        
        return make_response({
            'total': total,
            'page': page,
            'page_size': page_size,
            'reports': reports
        })


@agent_ns.route('/reports/<string:report_id>')
class ReportResource(Resource):
    @agent_ns.doc('delete_report', description='删除研报')
    @agent_ns.param('report_id', '研报ID', required=True)
    @agent_ns.response(200, '删除成功', delete_report_response)
    @agent_ns.response(404, '研报不存在', agent_ns.models.get('Error'))
    def delete(self, report_id):
        """DELETE /api/v1/agent/reports/<id> - 删除研报"""
        storage = get_storage()
        
        # 检查研报是否存在
        report = storage.get_report_by_id(report_id)
        if report is None:
            raise APIError(
                'REPORT_NOT_FOUND',
                '研报不存在',
                404,
                {'report_id': report_id}
            )
        
        # 删除文件
        upload_folder = current_app.config.get('UPLOAD_FOLDER', './data/uploads')
        import os
        
        file_ext = report['filename'].rsplit('.', 1)[1].lower() if '.' in report['filename'] else ''
        filename = f"{report_id}.{file_ext}"
        file_path = os.path.join(upload_folder, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 删除记录
        deleted = storage.delete_report(report_id)
        
        return make_response({
            'deleted': deleted,
            'report_id': report_id
        })


@agent_ns.route('/reports/<string:report_id>/analyze')
class AnalyzeReportResource(Resource):
    @agent_ns.doc('analyze_report', description='触发研报分析')
    @agent_ns.param('report_id', '研报ID', required=True)
    @agent_ns.response(200, '成功', analyze_report_response)
    @agent_ns.response(404, '研报不存在', agent_ns.models.get('Error'))
    def post(self, report_id):
        """POST /api/v1/agent/reports/<id>/analyze - 分析研报"""
        storage = get_storage()
        
        # 检查研报是否存在
        report = storage.get_report_by_id(report_id)
        if report is None:
            raise APIError(
                'REPORT_NOT_FOUND',
                '研报不存在',
                404,
                {'report_id': report_id}
            )
        
        # 如果已经分析完成，直接返回缓存结果
        if report.get('status') == 'analyzed' and report.get('analysis'):
            return make_response({
                'report_id': report_id,
                'status': 'analyzed',
                'analysis': report['analysis']
            })
        
        # 更新状态为分析中
        storage.update_report_status(report_id, 'analyzing')
        
        # TODO: 触发异步分析任务
        # 这里简化处理，直接返回分析中状态
        
        return make_response({
            'report_id': report_id,
            'status': 'analyzing',
            'analysis': None
        })


# ==================== 健康检查 ====================

@agent_ns.route('/health')
class HealthResource(Resource):
    @agent_ns.doc('health_check', description='系统健康检查')
    @agent_ns.response(200, '成功', health_response)
    def get(self):
        """GET /api/v1/agent/health - 健康检查"""
        caps = Config.get_caps()
        storage = get_storage()
        
        # 检查LLM服务状态
        llm_status = 'available'
        llm_provider = None
        
        if caps['copaw_configured']:
            llm_provider = 'copaw'
        elif caps['bailian_configured']:
            llm_provider = 'bailian'
        else:
            llm_status = 'unavailable'
        
        # 检查数据库（文件系统）状态
        try:
            storage._read_json(storage.sessions_file)
            db_status = 'ok'
        except Exception:
            db_status = 'error'
        
        # 计算指标
        sessions = storage._read_json(storage.sessions_file)
        records = storage._read_json(storage.records_file)
        
        total_queries = sum(s.get('query_count', 0) for s in sessions)
        
        # 计算平均响应时间（简化处理）
        avg_response_time = 0
        if records:
            response_times = [r.get('response_time_ms', 0) for r in records if r.get('response_time_ms')]
            if response_times:
                avg_response_time = int(sum(response_times) / len(response_times))
        
        # 确定整体状态
        if db_status == 'error':
            status = 'unhealthy'
        elif llm_status == 'unavailable':
            status = 'degraded'
        else:
            status = 'healthy'
        
        from datetime import datetime, timezone
        
        return make_response({
            'status': status,
            'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'services': {
                'llm': {
                    'status': llm_status,
                    'provider': llm_provider
                },
                'database': db_status
            },
            'metrics': {
                'active_sessions': len(sessions),
                'total_queries': total_queries,
                'avg_response_time_ms': avg_response_time
            }
        })


# ==================== 导出功能 ====================

@agent_ns.route('/export')
class ExportResource(Resource):
    @agent_ns.doc('export_reports', description='导出研报对比结果')
    @agent_ns.expect(export_request)
    @agent_ns.response(200, '成功', export_response)
    @agent_ns.response(400, '参数错误', agent_ns.models.get('Error'))
    def post(self):
        """POST /api/v1/agent/export - 导出对比结果"""
        data = request.get_json() or {}
        report_ids = data.get('report_ids', [])
        export_format = data.get('format', 'pdf')
        company = data.get('company', '')
        
        # 参数校验
        if len(report_ids) < 2:
            raise APIError(
                'INVALID_REPORT_COUNT',
                '请至少选择2份研报进行对比',
                400
            )
        
        if export_format not in ['pdf', 'excel']:
            raise APIError(
                'INVALID_FORMAT',
                '仅支持 PDF 或 Excel 格式导出',
                400
            )
        
        # 生成导出任务ID
        export_id = f"exp_{uuid.uuid4().hex[:12]}"
        
        # TODO: 触发异步导出任务
        # 这里简化处理，返回processing状态
        
        from datetime import datetime, timezone, timedelta
        
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        return make_response({
            'export_id': export_id,
            'status': 'processing',
            'download_url': None,
            'expires_at': expires_at
        })
