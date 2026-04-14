"""路由蓝图模块"""
import os
import uuid
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from app.storage import storage
from app.llm_provider import llm_chain
from app.stock_provider import stock_chain
from app.config import config


# 创建蓝图
research_bp = Blueprint('research', __name__, url_prefix='/api/v1/research')


def generate_trace_id() -> str:
    """生成链路追踪ID"""
    return f"tr_{uuid.uuid4().hex}"


def success_response(data, trace_id: str = None):
    """成功响应格式"""
    return jsonify({
        'traceId': trace_id or generate_trace_id(),
        'success': True,
        'data': data,
    })


def error_response(code: str, message: str, http_status: int = 400, details: dict = None):
    """错误响应格式"""
    return jsonify({
        'success': False,
        'error': {
            'code': code,
            'message': message,
            'details': details or {},
            'traceId': generate_trace_id(),
        }
    }), http_status


def allowed_file(filename: str) -> bool:
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


# ==================== 研报管理 ====================

@research_bp.route('/reports', methods=['POST'])
def upload_report():
    """
    上传并解析研报
    ---
    tags:
      - 研报管理
    summary: 上传并解析研报PDF文件
    description: 上传研报PDF文件，使用LLM解析提取关键信息（标题、作者、股票代码、评级等）
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: 研报PDF文件（最大20MB）
    responses:
      201:
        description: 研报上传并解析成功
        schema:
          type: object
          properties:
            traceId:
              type: string
            success:
              type: boolean
            data:
              type: object
              properties:
                id:
                  type: string
                title:
                  type: string
                subject_name:
                  type: string
                subject_code:
                  type: string
                author:
                  type: string
                rating:
                  type: string
                trend:
                  type: string
                target_price:
                  type: number
                summary:
                  type: string
                parse_status:
                  type: string
                  enum: [success, partial, failed]
                created_at:
                  type: string
      400:
        description: 请求参数错误（空文件、格式不支持、文件过大）
      500:
        description: 研报解析失败
    """
    trace_id = generate_trace_id()
    
    # 检查文件
    if 'file' not in request.files:
        return error_response('EMPTY_FILE', '请上传研报文件')
    
    file = request.files['file']
    if file.filename == '':
        return error_response('EMPTY_FILE', '请选择研报文件')
    
    if not allowed_file(file.filename):
        return error_response('INVALID_FILE_TYPE', '仅支持 PDF 格式', details={'supported_types': ['pdf']})
    
    # 检查文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > config.MAX_CONTENT_LENGTH:
        return error_response('FILE_TOO_LARGE', '文件大小不能超过 20MB', details={'max_size_mb': 20})
    
    try:
        # 保存文件
        filename = secure_filename(file.filename)
        report_id = f"rpt_{uuid.uuid4().hex[:12]}"
        file_path = config.UPLOAD_DIR / f"{report_id}.pdf"
        config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        file.save(file_path)
        
        # 提取文本内容
        content = extract_pdf_text(file_path)
        
        # 调用LLM解析
        parse_result = llm_chain.parse_report(content)
        
        # 判定解析状态
        parse_status = determine_parse_status(parse_result)
        
        # 保存研报记录
        report = storage.create_report({
            'title': parse_result.get('title', filename),
            'subject_name': parse_result.get('subject_name', ''),
            'subject_code': parse_result.get('subject_code', ''),
            'author': parse_result.get('author', ''),
            'rating': parse_result.get('rating', ''),
            'trend': parse_result.get('trend', 'neutral'),
            'target_price': parse_result.get('target_price'),
            'summary': parse_result.get('summary', ''),
            'file_path': str(file_path),
            'parse_status': parse_status,
        })
        
        return success_response(report, trace_id), 201
        
    except Exception as e:
        return error_response('PARSE_FAILED', f'研报解析失败: {str(e)}', http_status=500)


@research_bp.route('/reports', methods=['GET'])
def get_reports():
    """
    获取研报列表
    ---
    tags:
      - 研报管理
    summary: 分页获取研报列表
    description: 支持分页、按股票代码、作者、关键词筛选研报
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: 页码（从1开始）
      - name: page_size
        in: query
        type: integer
        default: 20
        description: 每页数量（1-100）
      - name: subject_code
        in: query
        type: string
        description: 股票代码筛选（6位数字）
      - name: author
        in: query
        type: string
        description: 作者筛选
      - name: keyword
        in: query
        type: string
        description: 关键词搜索（标题、摘要）
    responses:
      200:
        description: 研报列表获取成功
        schema:
          type: object
          properties:
            traceId:
              type: string
            success:
              type: boolean
            data:
              type: object
              properties:
                items:
                  type: array
                  items:
                    type: object
                total:
                  type: integer
                page:
                  type: integer
                page_size:
                  type: integer
                total_pages:
                  type: integer
    """
    trace_id = generate_trace_id()
    
    filters = {
        'page': request.args.get('page', 1, type=int),
        'page_size': request.args.get('page_size', 20, type=int),
        'subject_code': request.args.get('subject_code', ''),
        'author': request.args.get('author', ''),
        'keyword': request.args.get('keyword', ''),
    }
    
    # 参数校验
    if filters['page'] < 1:
        filters['page'] = 1
    if filters['page_size'] < 1 or filters['page_size'] > 100:
        filters['page_size'] = 20
    
    result = storage.get_reports(filters)
    return success_response(result, trace_id)


@research_bp.route('/reports/<report_id>', methods=['GET'])
def get_report(report_id: str):
    """
    获取研报详情
    ---
    tags:
      - 研报管理
    summary: 根据ID获取研报详情
    parameters:
      - name: report_id
        in: path
        type: string
        required: true
        description: 研报ID
    responses:
      200:
        description: 研报详情获取成功
        schema:
          type: object
          properties:
            traceId:
              type: string
            success:
              type: boolean
            data:
              type: object
              properties:
                id:
                  type: string
                title:
                  type: string
                subject_name:
                  type: string
                subject_code:
                  type: string
                author:
                  type: string
                rating:
                  type: string
                trend:
                  type: string
                target_price:
                  type: number
                summary:
                  type: string
                parse_status:
                  type: string
                created_at:
                  type: string
      404:
        description: 研报不存在
    """
    trace_id = generate_trace_id()
    
    report = storage.get_report(report_id)
    if not report:
        return error_response('REPORT_NOT_FOUND', '研报不存在', http_status=404)
    
    return success_response(report, trace_id)


@research_bp.route('/reports/<report_id>', methods=['DELETE'])
def delete_report(report_id: str):
    """
    删除研报
    ---
    tags:
      - 研报管理
    summary: 根据ID删除研报
    parameters:
      - name: report_id
        in: path
        type: string
        required: true
        description: 研报ID
    responses:
      200:
        description: 研报删除成功
        schema:
          type: object
          properties:
            traceId:
              type: string
            success:
              type: boolean
            data:
              type: object
              properties:
                deleted_id:
                  type: string
                message:
                  type: string
      404:
        description: 研报不存在
    """
    trace_id = generate_trace_id()
    
    report = storage.get_report(report_id)
    if not report:
        return error_response('REPORT_NOT_FOUND', '研报不存在', http_status=404)
    
    storage.delete_report(report_id)
    
    return success_response({
        'deleted_id': report_id,
        'message': '研报已删除',
    }, trace_id)


@research_bp.route('/reports/compare', methods=['POST'])
def compare_reports():
    """
    研报对比
    ---
    tags:
      - 研报对比
    summary: 同一股票多份研报横向对比
    description: 对比同一上市公司的多份研报，分析评级、目标价、趋势等差异
    consumes:
      - application/json
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - subject_code
          properties:
            subject_code:
              type: string
              description: 股票代码（6位数字）
            report_ids:
              type: array
              items:
                type: string
              description: 指定对比的研报ID列表（2-10个），不传则自动选择最新5份
    responses:
      200:
        description: 对比分析成功
        schema:
          type: object
          properties:
            traceId:
              type: string
            success:
              type: boolean
            data:
              type: object
              properties:
                subject_code:
                  type: string
                subject_name:
                  type: string
                reports:
                  type: array
                  items:
                    type: object
                compare_fields:
                  type: array
                  items:
                    type: string
                latest_price:
                  type: number
      400:
        description: 参数错误（股票代码格式错误、研报数量不符）
    """
    trace_id = generate_trace_id()
    
    data = request.get_json() or {}
    subject_code = data.get('subject_code', '')
    report_ids = data.get('report_ids')
    
    # 参数校验
    if not subject_code or len(subject_code) != 6 or not subject_code.isdigit():
        return error_response('INVALID_STOCK_CODE', '请输入正确的股票代码（6位数字）')
    
    if report_ids is not None:
        if not isinstance(report_ids, list) or len(report_ids) < 2 or len(report_ids) > 10:
            return error_response('INVALID_PARAM', '对比研报数量需为2-10个')
    
    result = storage.compare_reports(subject_code, report_ids)
    return success_response(result, trace_id)


# ==================== 股价查询 ====================

@research_bp.route('/stock/price', methods=['GET'])
def get_stock_price():
    """
    股票价格查询
    ---
    tags:
      - 股价查询
    summary: 查询股票实时价格
    description: 支持三级降级策略（新浪→腾讯→Mock），返回股票实时行情数据
    parameters:
      - name: code
        in: query
        type: string
        required: true
        description: 股票代码（6位数字，如000001）
    responses:
      200:
        description: 股价查询成功
        schema:
          type: object
          properties:
            traceId:
              type: string
            success:
              type: boolean
            data:
              type: object
              properties:
                code:
                  type: string
                name:
                  type: string
                price:
                  type: number
                change:
                  type: number
                change_percent:
                  type: number
                open:
                  type: number
                high:
                  type: number
                low:
                  type: number
                volume:
                  type: number
                updated_at:
                  type: string
                source:
                  type: string
                  enum: [sina, tencent, mock]
      400:
        description: 股票代码格式错误
      503:
        description: 股价服务暂不可用
    """
    trace_id = generate_trace_id()
    
    code = request.args.get('code', '')
    
    # 参数校验
    if not code or len(code) != 6 or not code.isdigit():
        return error_response('INVALID_STOCK_CODE', '请输入正确的股票代码（6位数字）')
    
    try:
        result = stock_chain.get_price(code)
        return success_response(result, trace_id)
    except Exception as e:
        return error_response('STOCK_SERVICE_UNAVAILABLE', '股价服务暂不可用', http_status=503)


# ==================== 辅助函数 ====================

def extract_pdf_text(file_path: Path) -> str:
    """提取PDF文本内容"""
    try:
        import PyPDF2
        text_parts = []
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages[:10]:  # 最多读取前10页
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        return '\n'.join(text_parts)
    except Exception:
        return ''


def determine_parse_status(result: dict) -> str:
    """判定解析状态"""
    required = ['title', 'subject_name', 'subject_code', 'author']
    optional = ['rating', 'trend', 'target_price', 'summary']
    
    required_ok = all(result.get(f) for f in required)
    if not required_ok:
        return 'failed'
    
    optional_ok = all(result.get(f) is not None for f in optional)
    return 'success' if optional_ok else 'partial'
