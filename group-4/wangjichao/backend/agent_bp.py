import os
import uuid

from flask import Blueprint, current_app, jsonify, request

# 错误码常量
EMPTY_QUERY = "EMPTY_QUERY"
INVALID_QUERY = "INVALID_QUERY"
INVALID_SESSION_ID = "INVALID_SESSION_ID"
INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
FILE_TOO_LARGE = "FILE_TOO_LARGE"
INVALID_REPORT_SELECTION = "INVALID_REPORT_SELECTION"
SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
REPORT_NOT_FOUND = "REPORT_NOT_FOUND"
PARSE_ERROR = "PARSE_ERROR"
UPSTREAM_ERROR = "UPSTREAM_ERROR"
LLM_UNAVAILABLE = "LLM_UNAVAILABLE"

agent_bp = Blueprint('agent', __name__)


def _get_trace_id() -> str:
    """优先复用 X-Trace-Id 请求头，缺省时生成 tr_{uuid.hex}"""
    trace_id = request.headers.get('X-Trace-Id')
    if trace_id:
        return trace_id
    return f"tr_{uuid.uuid4().hex}"


def _ok(data: dict, status=200):
    """统一成功响应，注入 traceId"""
    return jsonify({
        "success": True,
        "data": data,
        "traceId": _get_trace_id()
    }), status


def _err(code: str, message: str, status: int, details=None):
    """统一错误响应"""
    error_body = {
        "code": code,
        "message": message,
        "traceId": _get_trace_id()
    }
    if details:
        error_body["details"] = details
    return jsonify({
        "success": False,
        "error": error_body
    }), status


@agent_bp.route('/capabilities', methods=['GET'])
def get_capabilities():
    """
    ---
    summary: 获取系统能力状态
    description: 返回当前后端对 CoPaw 与百炼模型的配置状态，以及可用的百炼模型名称。
    tags:
      - 能力查询
    responses:
      200:
        description: 查询成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                copaw_configured:
                  type: boolean
                  example: false
                bailian_configured:
                  type: boolean
                  example: true
                bailian_model:
                  type: string
                  nullable: true
                  example: qwen-plus
            traceId:
              type: string
              example: tr_1234567890abcdef
    """
    copaw_configured = bool(os.getenv("IRA_COPAW_BASE_URL")) and bool(os.getenv("IRA_COPAW_ASK_URL"))
    bailian_configured = bool(os.getenv("DASHSCOPE_API_KEY"))
    bailian_model = os.getenv("DASHSCOPE_MODEL", "qwen-plus")

    return _ok({
        "copaw_configured": copaw_configured,
        "bailian_configured": bailian_configured,
        "bailian_model": bailian_model if bailian_configured else None
    })


# ==========================================
# T05: 会话管理端点
# ==========================================


@agent_bp.route('/sessions', methods=['POST'])
def create_session():
    """
    ---
    summary: 创建会话
    description: 创建一个新的问答会话，可选传入自定义标题；未传时默认使用“新会话”。
    tags:
      - 会话管理
    parameters:
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            title:
              type: string
              description: 会话标题，最大 100 个字符
              example: 新能源行业周报讨论
    responses:
      201:
        description: 创建成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                session_id:
                  type: string
                  example: 550e8400-e29b-41d4-a716-446655440000
                title:
                  type: string
                  example: 新能源行业周报讨论
                created_at:
                  type: string
                  example: "2026-04-14T10:00:00Z"
                updated_at:
                  type: string
                  example: "2026-04-14T10:00:00Z"
                query_count:
                  type: integer
                  example: 0
            traceId:
              type: string
              example: tr_1234567890abcdef
      400:
        description: 标题不合法
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: INVALID_QUERY
                message:
                  type: string
                  example: 标题不能超过100个字符
                traceId:
                  type: string
                  example: tr_1234567890abcdef
    """
    data = request.get_json(silent=True) or {}
    title = data.get('title', '新会话')

    # title 校验
    if title and len(title) > 100:
        return _err(INVALID_QUERY, "标题不能超过100个字符", 400)

    session_id = str(uuid.uuid4())
    from storage import Storage
    store = Storage(current_app.config['DATA_DIR'])
    session = store.create_session(session_id, title)
    return _ok(session, 201)


@agent_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """
    ---
    summary: 获取会话列表
    description: 返回当前系统中的所有会话，按创建时间倒序排列。
    tags:
      - 会话管理
    responses:
      200:
        description: 查询成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                sessions:
                  type: array
                  items:
                    type: object
                    properties:
                      session_id:
                        type: string
                        example: 550e8400-e29b-41d4-a716-446655440000
                      title:
                        type: string
                        example: 新能源行业周报讨论
                      created_at:
                        type: string
                        example: "2026-04-14T10:00:00Z"
                      updated_at:
                        type: string
                        example: "2026-04-14T10:30:00Z"
                      query_count:
                        type: integer
                        example: 3
            traceId:
              type: string
              example: tr_1234567890abcdef
    """
    from storage import Storage
    store = Storage(current_app.config['DATA_DIR'])
    sessions = store.get_sessions()
    return _ok({"sessions": sessions})


@agent_bp.route('/sessions/<session_id>', methods=['PUT'])
def update_session(session_id):
    """
    ---
    summary: 更新会话标题
    description: 根据会话 ID 修改会话标题。
    tags:
      - 会话管理
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
        description: 会话 ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
          properties:
            title:
              type: string
              description: 新的会话标题，最大 100 个字符
              example: 券商研报对比讨论
    responses:
      200:
        description: 更新成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                session_id:
                  type: string
                  example: 550e8400-e29b-41d4-a716-446655440000
                title:
                  type: string
                  example: 券商研报对比讨论
                created_at:
                  type: string
                  example: "2026-04-14T10:00:00Z"
                updated_at:
                  type: string
                  example: "2026-04-14T10:30:00Z"
                query_count:
                  type: integer
                  example: 3
            traceId:
              type: string
              example: tr_1234567890abcdef
      400:
        description: 标题为空或不合法
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: INVALID_QUERY
                message:
                  type: string
                  example: 标题不能为空
                traceId:
                  type: string
                  example: tr_1234567890abcdef
      404:
        description: 会话不存在
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: SESSION_NOT_FOUND
                message:
                  type: string
                  example: 会话不存在
                traceId:
                  type: string
                  example: tr_1234567890abcdef
    """
    data = request.get_json(silent=True) or {}
    title = data.get('title')

    if not title:
        return _err(INVALID_QUERY, "标题不能为空", 400)
    if len(title) > 100:
        return _err(INVALID_QUERY, "标题不能超过100个字符", 400)

    from storage import Storage
    store = Storage(current_app.config['DATA_DIR'])
    session = store.update_session(session_id, title)
    if session is None:
        return _err(SESSION_NOT_FOUND, "会话不存在", 404)
    return _ok(session)


@agent_bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    ---
    summary: 删除会话
    description: 删除指定会话，并级联删除该会话下的全部问答记录。
    tags:
      - 会话管理
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
        description: 会话 ID
    responses:
      200:
        description: 删除成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                message:
                  type: string
                  example: 会话已删除
            traceId:
              type: string
              example: tr_1234567890abcdef
      404:
        description: 会话不存在
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: SESSION_NOT_FOUND
                message:
                  type: string
                  example: 会话不存在
                traceId:
                  type: string
                  example: tr_1234567890abcdef
    """
    from storage import Storage
    store = Storage(current_app.config['DATA_DIR'])
    sessions = store.get_sessions()
    exists = any(s['session_id'] == session_id for s in sessions)
    if not exists:
        return _err(SESSION_NOT_FOUND, "会话不存在", 404)

    store.delete_session(session_id)
    return _ok({"message": "会话已删除"})


@agent_bp.route('/sessions/<session_id>/records', methods=['GET'])
def get_session_records(session_id):
    """
    ---
    summary: 获取会话问答记录
    description: 返回指定会话下的全部问答记录，按时间正序排列。
    tags:
      - 会话管理
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
        description: 会话 ID
    responses:
      200:
        description: 查询成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                records:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                        example: rec_1713088800
                      session_id:
                        type: string
                        example: 550e8400-e29b-41d4-a716-446655440000
                      query:
                        type: string
                        example: 总结这份研报的核心观点
                      answer:
                        type: string
                        example: 该研报主要强调行业景气度回升。
                      llm_used:
                        type: boolean
                        example: true
                      model:
                        type: string
                        nullable: true
                        example: qwen-plus
                      response_time_ms:
                        type: integer
                        example: 812
                      answer_source:
                        type: string
                        example: bailian
                      citations:
                        type: array
                        items:
                          type: string
                      timestamp:
                        type: string
                        example: "2026-04-14T10:31:00Z"
            traceId:
              type: string
              example: tr_1234567890abcdef
      404:
        description: 会话不存在
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: SESSION_NOT_FOUND
                message:
                  type: string
                  example: 会话不存在
                traceId:
                  type: string
                  example: tr_1234567890abcdef
    """
    from storage import Storage
    store = Storage(current_app.config['DATA_DIR'])
    sessions = store.get_sessions()
    exists = any(s['session_id'] == session_id for s in sessions)
    if not exists:
        return _err(SESSION_NOT_FOUND, "会话不存在", 404)

    records = store.get_records_by_session(session_id)
    return _ok({"records": records})


# ==========================================
# T06: 问答提交端点
# ==========================================


@agent_bp.route('/ask', methods=['POST'])
def ask():
    """
    ---
    summary: 提交问答
    description: 向智能问答引擎提交问题，系统将按 CoPaw、百炼、Demo 的顺序进行三级降级回答。
    tags:
      - 智能问答
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - query
            - session_id
          properties:
            query:
              type: string
              description: 用户问题内容，长度 1-500
              example: 请总结这份研报的投资评级和目标价
            session_id:
              type: string
              description: 会话 ID
              example: 550e8400-e29b-41d4-a716-446655440000
    responses:
      200:
        description: 问答成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                answer:
                  type: string
                  example: 该研报给出买入评级，目标价为18元。
                llm_used:
                  type: boolean
                  example: true
                model:
                  type: string
                  nullable: true
                  example: qwen-plus
                response_time_ms:
                  type: integer
                  example: 1260
                answer_source:
                  type: string
                  example: bailian
            traceId:
              type: string
              example: tr_1234567890abcdef
      400:
        description: 参数错误
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: EMPTY_QUERY
                message:
                  type: string
                  example: query 不能为空
                traceId:
                  type: string
                  example: tr_1234567890abcdef
      404:
        description: 会话不存在
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: SESSION_NOT_FOUND
                message:
                  type: string
                  example: 会话不存在
                traceId:
                  type: string
                  example: tr_1234567890abcdef
    """
    import time
    data = request.get_json(silent=True) or {}
    query = data.get('query')
    session_id = data.get('session_id')

    if not query or (isinstance(query, str) and not query.strip()):
        return _err(EMPTY_QUERY, "query 不能为空", 400)
    if not isinstance(query, str) or len(query) > 500:
        return _err(INVALID_QUERY, "query 必须为1-500字符的字符串", 400)
    if not session_id or not isinstance(session_id, str) or not session_id.strip():
        return _err(INVALID_SESSION_ID, "session_id 不能为空", 400)

    from storage import Storage
    store = Storage(current_app.config['DATA_DIR'])

    sessions = store.get_sessions()
    exists = any(s['session_id'] == session_id for s in sessions)
    if not exists:
        return _err(SESSION_NOT_FOUND, "会话不存在", 404)

    start_time = time.time()
    from agent import CoPawAgent
    agent = CoPawAgent()
    result = agent.ask(query.strip(), session_id)
    response_time_ms = int((time.time() - start_time) * 1000)

    store.add_record(
        session_id=session_id,
        query=query.strip(),
        answer=result["answer"],
        llm_used=result["llm_used"],
        model=result["model"],
        response_time_ms=response_time_ms,
        answer_source=result["answer_source"],
        citations=result.get("citations", [])
    )

    return _ok({
        "answer": result["answer"],
        "llm_used": result["llm_used"],
        "model": result["model"],
        "response_time_ms": response_time_ms,
        "answer_source": result["answer_source"]
    })


# ==========================================
# T07: 研报管理端点
# ==========================================


@agent_bp.route('/reports', methods=['POST'])
def upload_report():
    """
    ---
    summary: 上传研报
    description: 通过 multipart/form-data 上传 PDF 或 HTML 研报文件，并创建待解析的研报记录。
    consumes:
      - multipart/form-data
    tags:
      - 研报管理
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: 待上传的研报文件，仅支持 PDF 或 HTML
      - in: formData
        name: title
        type: string
        required: false
        description: 自定义研报标题，未传时默认使用文件名
    responses:
      201:
        description: 上传成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                report_id:
                  type: string
                  example: 660e8400-e29b-41d4-a716-446655440000
                title:
                  type: string
                  example: 贵州茅台深度报告.pdf
                file_type:
                  type: string
                  example: pdf
                file_size:
                  type: integer
                  example: 1048576
                file_path:
                  type: string
                  example: /path/to/backend/data/uploads/660e8400-e29b-41d4-a716-446655440000.pdf
                status:
                  type: string
                  example: pending
                uploaded_at:
                  type: string
                  example: "2026-04-14T11:00:00Z"
                is_marked:
                  type: boolean
                  example: false
                mark_status:
                  type: string
                  example: none
                parsed_result:
                  nullable: true
            traceId:
              type: string
              example: tr_1234567890abcdef
      400:
        description: 文件格式错误或大小超限
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: INVALID_FILE_TYPE
                message:
                  type: string
                  example: 仅支持 PDF/HTML 格式
                traceId:
                  type: string
                  example: tr_1234567890abcdef
    """
    if 'file' not in request.files:
        return _err(INVALID_FILE_TYPE, "请上传文件", 400)

    file = request.files['file']
    if not file.filename:
        return _err(INVALID_FILE_TYPE, "文件名不能为空", 400)

    filename = file.filename.lower()
    if filename.endswith('.pdf'):
        file_type = 'pdf'
    elif filename.endswith('.html') or filename.endswith('.htm'):
        file_type = 'html'
    else:
        return _err(INVALID_FILE_TYPE, "仅支持 PDF/HTML 格式", 400)

    file_data = file.read()
    file_size = len(file_data)
    max_size = 50 * 1024 * 1024
    if file_size > max_size:
        return _err(FILE_TOO_LARGE, "文件大小不能超过50MB", 400)

    report_id = str(uuid.uuid4())
    upload_dir = os.path.join(current_app.config['DATA_DIR'], 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{report_id}.{file_type}")
    with open(file_path, 'wb') as f:
        f.write(file_data)

    title = request.form.get('title', '') or file.filename

    from storage import Storage
    store = Storage(current_app.config['DATA_DIR'])
    report = store.create_report(report_id, title, file_type, file_size, file_path)
    return _ok(report, 201)


@agent_bp.route('/reports', methods=['GET'])
def get_reports():
    """
    ---
    summary: 获取研报列表
    description: 支持按标题关键字、评级筛选，并返回分页后的研报列表。
    tags:
      - 研报管理
    parameters:
      - in: query
        name: keyword
        type: string
        required: false
        description: 标题关键字模糊匹配
      - in: query
        name: rating
        type: string
        required: false
        description: 评级精确筛选，仅对已解析研报生效
        enum:
          - 买入
          - 增持
          - 中性
          - 减持
          - 卖出
      - in: query
        name: page
        type: integer
        required: false
        default: 1
        description: 页码，从 1 开始
      - in: query
        name: size
        type: integer
        required: false
        default: 10
        description: 每页数量
    responses:
      200:
        description: 查询成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                items:
                  type: array
                  items:
                    type: object
                    properties:
                      report_id:
                        type: string
                        example: 660e8400-e29b-41d4-a716-446655440000
                      title:
                        type: string
                        example: 贵州茅台深度报告
                      file_type:
                        type: string
                        example: pdf
                      file_size:
                        type: integer
                        example: 1048576
                      status:
                        type: string
                        example: completed
                      uploaded_at:
                        type: string
                        example: "2026-04-14T11:00:00Z"
                      is_marked:
                        type: boolean
                        example: true
                      mark_status:
                        type: string
                        example: important
                      parsed_result:
                        type: object
                        nullable: true
                page:
                  type: integer
                  example: 1
                size:
                  type: integer
                  example: 10
                total:
                  type: integer
                  example: 25
            traceId:
              type: string
              example: tr_1234567890abcdef
    """
    keyword = request.args.get('keyword')
    rating = request.args.get('rating')
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 10, type=int)

    from storage import Storage
    store = Storage(current_app.config['DATA_DIR'])
    result = store.get_reports(keyword=keyword, rating=rating, page=page, size=size)
    return _ok(result)


@agent_bp.route('/reports/<report_id>', methods=['GET'])
def get_report(report_id):
    """
    ---
    summary: 获取研报详情
    description: 根据研报 ID 返回完整的研报记录与解析结果。
    tags:
      - 研报管理
    parameters:
      - in: path
        name: report_id
        type: string
        required: true
        description: 研报 ID
    responses:
      200:
        description: 查询成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                report_id:
                  type: string
                  example: 660e8400-e29b-41d4-a716-446655440000
                title:
                  type: string
                  example: 贵州茅台深度报告
                file_type:
                  type: string
                  example: pdf
                file_size:
                  type: integer
                  example: 1048576
                file_path:
                  type: string
                  example: /path/to/backend/data/uploads/660e8400-e29b-41d4-a716-446655440000.pdf
                status:
                  type: string
                  example: completed
                uploaded_at:
                  type: string
                  example: "2026-04-14T11:00:00Z"
                is_marked:
                  type: boolean
                  example: true
                mark_status:
                  type: string
                  example: important
                parsed_result:
                  type: object
                  nullable: true
            traceId:
              type: string
              example: tr_1234567890abcdef
      404:
        description: 研报不存在
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: REPORT_NOT_FOUND
                message:
                  type: string
                  example: 研报不存在
                traceId:
                  type: string
                  example: tr_1234567890abcdef
    """
    from storage import Storage
    store = Storage(current_app.config['DATA_DIR'])
    report = store.get_report_by_id(report_id)
    if not report:
        return _err(REPORT_NOT_FOUND, "研报不存在", 404)
    return _ok(report)


@agent_bp.route('/reports/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    """
    ---
    summary: 删除研报
    description: 删除指定研报记录，并移除已上传的原始文件。
    tags:
      - 研报管理
    parameters:
      - in: path
        name: report_id
        type: string
        required: true
        description: 研报 ID
    responses:
      200:
        description: 删除成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                message:
                  type: string
                  example: 研报已删除
            traceId:
              type: string
              example: tr_1234567890abcdef
      404:
        description: 研报不存在
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: REPORT_NOT_FOUND
                message:
                  type: string
                  example: 研报不存在
                traceId:
                  type: string
                  example: tr_1234567890abcdef
    """
    from storage import Storage
    store = Storage(current_app.config['DATA_DIR'])
    report = store.get_report_by_id(report_id)
    if not report:
        return _err(REPORT_NOT_FOUND, "研报不存在", 404)

    if report.get('file_path') and os.path.exists(report['file_path']):
        os.remove(report['file_path'])

    store.delete_report(report_id)
    return _ok({"message": "研报已删除"})


@agent_bp.route('/reports/<report_id>/mark', methods=['PUT'])
def mark_report(report_id):
    """
    ---
    summary: 标记研报
    description: 更新研报标记状态，可设置为重要、已读或取消标记。
    tags:
      - 研报管理
    parameters:
      - in: path
        name: report_id
        type: string
        required: true
        description: 研报 ID
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - is_marked
          properties:
            is_marked:
              type: boolean
              description: 是否标记
              example: true
            mark_status:
              type: string
              description: 标记状态，仅支持 none、important、read
              example: important
              enum:
                - none
                - important
                - read
    responses:
      200:
        description: 标记成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                report_id:
                  type: string
                  example: 660e8400-e29b-41d4-a716-446655440000
                is_marked:
                  type: boolean
                  example: true
                mark_status:
                  type: string
                  example: important
            traceId:
              type: string
              example: tr_1234567890abcdef
      400:
        description: 标记参数错误
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: INVALID_QUERY
                message:
                  type: string
                  example: mark_status 必须为 none/important/read
                traceId:
                  type: string
                  example: tr_1234567890abcdef
      404:
        description: 研报不存在
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: REPORT_NOT_FOUND
                message:
                  type: string
                  example: 研报不存在
                traceId:
                  type: string
                  example: tr_1234567890abcdef
    """
    from storage import Storage
    store = Storage(current_app.config['DATA_DIR'])

    report = store.get_report_by_id(report_id)
    if not report:
        return _err(REPORT_NOT_FOUND, "研报不存在", 404)

    data = request.get_json(silent=True) or {}
    is_marked = data.get('is_marked')
    mark_status = data.get('mark_status', 'important')

    if is_marked is None:
        return _err(INVALID_QUERY, "is_marked 字段必填", 400)

    if mark_status not in ('none', 'important', 'read'):
        return _err(INVALID_QUERY, "mark_status 必须为 none/important/read", 400)

    result = store.mark_report(report_id, is_marked, mark_status)
    return _ok(result)


@agent_bp.route('/reports/<report_id>/parse', methods=['POST'])
def parse_report(report_id):
    """
    ---
    summary: 解析研报
    description: 触发对指定研报的结构化解析，提取评级、目标价、核心观点与预测数据。
    tags:
      - 研报管理
    parameters:
      - in: path
        name: report_id
        type: string
        required: true
        description: 研报 ID
    responses:
      200:
        description: 解析成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                report_id:
                  type: string
                  example: 660e8400-e29b-41d4-a716-446655440000
                title:
                  type: string
                  example: 贵州茅台深度报告
                rating:
                  type: string
                  nullable: true
                  example: 买入
                target_price:
                  type: string
                  nullable: true
                  example: 18元
                core_views:
                  type: array
                  items:
                    type: string
                data_forecast:
                  type: object
                  properties:
                    revenue_growth:
                      type: string
                      example: 12%
                    pe:
                      type: string
                      example: 18
                    eps:
                      type: string
                      example: 1.25
                    net_profit:
                      type: string
                      example: 净利润 120 亿
                parse_time_ms:
                  type: integer
                  example: 1680
                parsed_at:
                  type: string
                  example: "2026-04-14T11:10:00Z"
            traceId:
              type: string
              example: tr_1234567890abcdef
      404:
        description: 研报不存在
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: REPORT_NOT_FOUND
                message:
                  type: string
                  example: 研报不存在
                traceId:
                  type: string
                  example: tr_1234567890abcdef
      500:
        description: 解析失败
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: PARSE_ERROR
                message:
                  type: string
                  example: "研报解析失败: 文件内容为空"
                traceId:
                  type: string
                  example: tr_1234567890abcdef
    """
    from storage import Storage
    from report_parser import ReportParser
    from datetime import datetime, timezone

    store = Storage(current_app.config['DATA_DIR'])
    report = store.get_report_by_id(report_id)
    if not report:
        return _err(REPORT_NOT_FOUND, "研报不存在", 404)

    store.update_report_status(report_id, "parsing")

    try:
        parser = ReportParser()
        result = parser.parse(report['file_path'], report['file_type'])

        parsed_result = {
            "report_id": report_id,
            "title": result.get("title", report["title"]),
            "rating": result.get("rating"),
            "target_price": result.get("target_price"),
            "core_views": result.get("core_views", []),
            "data_forecast": result.get("data_forecast", {}),
            "parse_time_ms": result.get("parse_time_ms", 0),
            "parsed_at": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        }

        store.save_parse_result(report_id, parsed_result)
        store.update_report_status(report_id, "completed")

        return _ok(parsed_result)

    except Exception as e:
        store.update_report_status(report_id, "failed")
        return _err(PARSE_ERROR, f"研报解析失败: {str(e)}", 500)


@agent_bp.route('/reports/compare', methods=['POST'])
def compare_reports():
    """
    ---
    summary: 对比研报
    description: 选择 2-10 份研报进行结构化对比，返回统一表头与对比结果行。
    tags:
      - 研报管理
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - report_ids
          properties:
            report_ids:
              type: array
              description: 需要对比的研报 ID 列表，数量 2-10
              minItems: 2
              maxItems: 10
              items:
                type: string
              example:
                - 660e8400-e29b-41d4-a716-446655440000
                - 770e8400-e29b-41d4-a716-446655440000
    responses:
      200:
        description: 对比成功
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            data:
              type: object
              properties:
                headers:
                  type: array
                  items:
                    type: string
                  example:
                    - title
                    - rating
                    - target_price
                    - core_views
                rows:
                  type: array
                  items:
                    type: object
                    properties:
                      report_id:
                        type: string
                        example: 660e8400-e29b-41d4-a716-446655440000
                      title:
                        type: string
                        example: 贵州茅台深度报告
                      rating:
                        type: string
                        nullable: true
                        example: 买入
                      target_price:
                        type: string
                        nullable: true
                        example: 18元
                      core_views:
                        type: array
                        items:
                          type: string
            traceId:
              type: string
              example: tr_1234567890abcdef
      400:
        description: 研报选择数量不合法
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: INVALID_REPORT_SELECTION
                message:
                  type: string
                  example: 研报对比需要2-10份研报
                traceId:
                  type: string
                  example: tr_1234567890abcdef
      404:
        description: 研报不存在
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: object
              properties:
                code:
                  type: string
                  example: REPORT_NOT_FOUND
                message:
                  type: string
                  example: 研报 660e8400-e29b-41d4-a716-446655440000 不存在
                traceId:
                  type: string
                  example: tr_1234567890abcdef
    """
    data = request.get_json(silent=True) or {}
    report_ids = data.get('report_ids', [])

    if not isinstance(report_ids, list) or len(report_ids) < 2 or len(report_ids) > 10:
        return _err(INVALID_REPORT_SELECTION, "研报对比需要2-10份研报", 400)

    from storage import Storage
    store = Storage(current_app.config['DATA_DIR'])

    for rid in report_ids:
        if not store.get_report_by_id(rid):
            return _err(REPORT_NOT_FOUND, f"研报 {rid} 不存在", 404)

    result = store.compare_reports(report_ids)
    return _ok(result)
