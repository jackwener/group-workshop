"""
Swagger API文档配置
使用Flask-RESTX提供Swagger UI
"""
from flask_restx import Api, Namespace, fields

# 创建API实例
api = Api(
    version='1.0',
    title='投研问答助手 API',
    description='投研问答助手后端API接口文档',
    doc='/swagger/',  # Swagger UI路径
    prefix='/api/v1',
    validate=True
)

# 定义命名空间
agent_ns = Namespace('agent', description='投研问答助手相关接口')

# ============ 数据模型定义 ============

# 错误响应模型
error_model = agent_ns.model('Error', {
    'code': fields.String(required=True, description='错误码'),
    'message': fields.String(required=True, description='错误信息'),
    'details': fields.Raw(description='错误详情'),
    'traceId': fields.String(required=True, description='链路追踪ID')
})

# 能力配置模型
caps_model = agent_ns.model('Capabilities', {
    'copaw_configured': fields.Boolean(description='CoPaw是否已配置'),
    'bailian_configured': fields.Boolean(description='百炼是否已配置'),
    'demo_mode': fields.Boolean(description='是否为演示模式'),
    'bailian_model': fields.String(description='百炼模型名称')
})

capabilities_response = agent_ns.model('CapabilitiesResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'caps': fields.Nested(caps_model, description='能力配置')
})

# 会话模型
session_model = agent_ns.model('Session', {
    'session_id': fields.String(required=True, description='会话ID'),
    'title': fields.String(required=True, description='会话标题'),
    'created_at': fields.String(description='创建时间'),
    'updated_at': fields.String(description='更新时间'),
    'query_count': fields.Integer(description='问答次数')
})

create_session_request = agent_ns.model('CreateSessionRequest', {
    'title': fields.String(description='会话标题，默认"新会话"', max_length=100)
})

create_session_response = agent_ns.model('CreateSessionResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'session_id': fields.String(description='会话ID'),
    'title': fields.String(description='会话标题'),
    'created_at': fields.String(description='创建时间'),
    'query_count': fields.Integer(description='问答次数')
})

sessions_list_response = agent_ns.model('SessionsListResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'total': fields.Integer(description='总会话数'),
    'page': fields.Integer(description='当前页码'),
    'page_size': fields.Integer(description='每页数量'),
    'sessions': fields.List(fields.Nested(session_model), description='会话列表')
})

delete_session_response = agent_ns.model('DeleteSessionResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'deleted': fields.Boolean(description='是否删除成功'),
    'session_id': fields.String(description='被删除的会话ID')
})

# 问答记录模型
record_model = agent_ns.model('QARecord', {
    'record_id': fields.String(required=True, description='记录ID'),
    'query': fields.String(required=True, description='用户提问'),
    'answer': fields.String(required=True, description='系统回答'),
    'timestamp': fields.String(description='回答时间'),
    'llm_used': fields.Boolean(description='是否使用真实LLM'),
    'model': fields.String(description='模型标识'),
    'answer_source': fields.String(description='回答来源：copaw/bailian/demo'),
    'response_time_ms': fields.Integer(description='响应耗时（毫秒）')
})

records_list_response = agent_ns.model('RecordsListResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'session_id': fields.String(description='会话ID'),
    'total': fields.Integer(description='总记录数'),
    'records': fields.List(fields.Nested(record_model), description='问答记录列表')
})

# 问答请求/响应模型
ask_request = agent_ns.model('AskRequest', {
    'query': fields.String(required=True, description='用户问题，1-500字符', min_length=1, max_length=500),
    'session_id': fields.String(required=True, description='会话ID（UUID格式）')
})

ask_response = agent_ns.model('AskResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'answer': fields.String(description='答案文本'),
    'llm_used': fields.Boolean(description='是否使用真实LLM'),
    'model': fields.String(description='模型标识'),
    'response_time_ms': fields.Integer(description='响应耗时（毫秒）'),
    'answer_source': fields.String(description='回答来源：copaw/bailian/demo')
})

# 研报模型
report_model = agent_ns.model('Report', {
    'report_id': fields.String(required=True, description='研报ID'),
    'title': fields.String(required=True, description='研报标题'),
    'filename': fields.String(required=True, description='原始文件名'),
    'file_size': fields.Integer(description='文件大小（字节）'),
    'uploaded_at': fields.String(description='上传时间'),
    'analyzed_at': fields.String(description='分析完成时间'),
    'status': fields.String(description='状态：pending/analyzing/analyzed/failed'),
    'analysis': fields.Raw(description='分析结果')
})

upload_report_response = agent_ns.model('UploadReportResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'report_id': fields.String(description='研报ID'),
    'title': fields.String(description='研报标题'),
    'filename': fields.String(description='原始文件名'),
    'file_size': fields.Integer(description='文件大小'),
    'uploaded_at': fields.String(description='上传时间'),
    'status': fields.String(description='状态')
})

reports_list_response = agent_ns.model('ReportsListResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'total': fields.Integer(description='总研报数'),
    'page': fields.Integer(description='当前页码'),
    'page_size': fields.Integer(description='每页数量'),
    'reports': fields.List(fields.Nested(report_model), description='研报列表')
})

delete_report_response = agent_ns.model('DeleteReportResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'deleted': fields.Boolean(description='是否删除成功'),
    'report_id': fields.String(description='被删除的研报ID')
})

analysis_model = agent_ns.model('Analysis', {
    'company': fields.String(description='公司名称'),
    'key_metrics': fields.List(fields.Raw, description='关键指标数组'),
    'summary': fields.String(description='研报摘要')
})

analyze_report_response = agent_ns.model('AnalyzeReportResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'report_id': fields.String(description='研报ID'),
    'status': fields.String(description='状态：analyzing/analyzed'),
    'analysis': fields.Nested(analysis_model, description='分析结果')
})

# 健康检查模型
llm_service_model = agent_ns.model('LLMService', {
    'status': fields.String(description='状态：available/unavailable'),
    'provider': fields.String(description='提供商：copaw/bailian/demo')
})

services_model = agent_ns.model('Services', {
    'llm': fields.Nested(llm_service_model, description='LLM服务状态'),
    'database': fields.String(description='数据库状态：ok/error')
})

metrics_model = agent_ns.model('Metrics', {
    'active_sessions': fields.Integer(description='活跃会话数'),
    'total_queries': fields.Integer(description='总查询次数'),
    'avg_response_time_ms': fields.Integer(description='平均响应时间（毫秒）')
})

health_response = agent_ns.model('HealthResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'status': fields.String(description='状态：healthy/degraded/unhealthy'),
    'timestamp': fields.String(description='检查时间'),
    'services': fields.Nested(services_model, description='各服务状态'),
    'metrics': fields.Nested(metrics_model, description='运行指标')
})

# 导出模型
export_request = agent_ns.model('ExportRequest', {
    'report_ids': fields.List(fields.String, required=True, description='要对比的研报ID数组，至少2个'),
    'format': fields.String(required=True, description='导出格式：pdf/excel'),
    'company': fields.String(required=True, description='对比的公司名称')
})

export_response = agent_ns.model('ExportResponse', {
    'traceId': fields.String(description='链路追踪ID'),
    'export_id': fields.String(description='导出任务ID'),
    'status': fields.String(description='状态：processing/completed'),
    'download_url': fields.String(description='下载链接'),
    'expires_at': fields.String(description='链接过期时间')
})

# 将命名空间添加到API
api.add_namespace(agent_ns, path='/agent')
