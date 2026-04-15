"""
Swagger / OpenAPI 配置
投研问答助手 (IRA) API 文档
"""

SWAGGER_TEMPLATE = {
    "openapi": "3.0.0",
    "info": {
        "title": "投研问答助手 (IRA) API",
        "description": "Investment Research Assistant - 投研问答助手后端 API 接口文档",
        "version": "1.0.0",
        "contact": {
            "name": "IRA Team"
        }
    },
    "servers": [
        {
            "url": "http://localhost:5001/api/v1/agent",
            "description": "本地开发服务器"
        }
    ],
    "tags": [
        {
            "name": "能力探测",
            "description": "系统能力探测与健康检查"
        },
        {
            "name": "会话管理",
            "description": "会话的创建、查询、删除"
        },
        {
            "name": "问答",
            "description": "投研问答核心功能"
        },
        {
            "name": "记录查询",
            "description": "问答历史记录查询"
        }
    ]
}

# API 文档字符串（用于装饰器）

CAPABILITIES_DOC = """
获取系统能力配置状态
---
tags:
  - 能力探测
responses:
  200:
    description: 成功获取能力配置
    schema:
      type: object
      properties:
        traceId:
          type: string
          example: "tr_a1b2c3d4e5f6"
        capabilities:
          type: object
          properties:
            copaw_configured:
              type: boolean
              description: CoPaw 是否已配置
              example: true
            bailian_configured:
              type: boolean
              description: 百炼是否已配置
              example: false
            demo_available:
              type: boolean
              description: Demo 模式是否可用
              example: true
"""

HEALTH_DOC = """
健康检查与降级级别查询
---
tags:
  - 能力探测
responses:
  200:
    description: 健康状态
    schema:
      type: object
      properties:
        traceId:
          type: string
        status:
          type: string
          example: "healthy"
        copaw_available:
          type: boolean
          example: true
        bailian_available:
          type: boolean
          example: false
        demo_available:
          type: boolean
          example: true
        current_level:
          type: string
          description: 当前降级级别 (normal/degraded/demo)
          example: "normal"
"""

ASK_DOC = """
提交投研问答
---
tags:
  - 问答
parameters:
  - name: body
    in: body
    required: true
    schema:
      type: object
      required:
        - query
        - session_id
      properties:
        query:
          type: string
          description: 用户提问内容
          maxLength: 500
          example: "如何分析财报？"
        session_id:
          type: string
          description: 会话 ID
          example: "sess_abc123"
responses:
  200:
    description: 问答成功
    schema:
      type: object
      properties:
        traceId:
          type: string
        answer:
          type: string
          description: AI 回答内容
          example: "分析财报主要关注以下几个方面：1. 营收增长..."
        llm_used:
          type: boolean
          description: 是否使用了 LLM
          example: true
        model:
          type: string
          description: 使用的模型名称
          example: "gpt-4"
        response_time_ms:
          type: integer
          description: 响应时间（毫秒）
          example: 2345
        answer_source:
          type: string
          description: 回答来源 (copaw/bailian/demo)
          example: "copaw"
  400:
    description: 参数错误
    schema:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
              example: "EMPTY_QUERY"
            message:
              type: string
              example: "请输入问题"
            traceId:
              type: string
  404:
    description: 会话不存在
    schema:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
              example: "SESSION_NOT_FOUND"
            message:
              type: string
              example: "会话不存在"
"""

SESSIONS_GET_DOC = """
获取会话列表
---
tags:
  - 会话管理
responses:
  200:
    description: 成功获取会话列表
    schema:
      type: object
      properties:
        traceId:
          type: string
        sessions:
          type: array
          items:
            type: object
            properties:
              session_id:
                type: string
                example: "sess_abc123"
              title:
                type: string
                example: "新会话"
              created_at:
                type: string
                format: date-time
                example: "2024-01-15T08:30:00Z"
              updated_at:
                type: string
                format: date-time
                example: "2024-01-15T09:15:00Z"
              query_count:
                type: integer
                example: 5
"""

SESSIONS_POST_DOC = """
创建新会话
---
tags:
  - 会话管理
parameters:
  - name: body
    in: body
    required: false
    schema:
      type: object
      properties:
        title:
          type: string
          description: 会话标题
          maxLength: 23
          default: "新会话"
          example: "财报分析"
responses:
  201:
    description: 会话创建成功
    schema:
      type: object
      properties:
        traceId:
          type: string
        session_id:
          type: string
          example: "sess_abc123"
        title:
          type: string
          example: "财报分析"
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time
        query_count:
          type: integer
          example: 0
  400:
    description: 标题过长
    schema:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
              example: "INVALID_TITLE"
"""

SESSION_DELETE_DOC = """
删除会话
---
tags:
  - 会话管理
parameters:
  - name: session_id
    in: path
    type: string
    required: true
    description: 会话 ID
    example: "sess_abc123"
responses:
  200:
    description: 删除成功
    schema:
      type: object
      properties:
        traceId:
          type: string
        success:
          type: boolean
          example: true
        deleted_session_id:
          type: string
          example: "sess_abc123"
  404:
    description: 会话不存在
    schema:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
              example: "SESSION_NOT_FOUND"
"""

RECORDS_GET_DOC = """
获取会话问答记录
---
tags:
  - 记录查询
parameters:
  - name: session_id
    in: path
    type: string
    required: true
    description: 会话 ID
    example: "sess_abc123"
responses:
  200:
    description: 成功获取记录
    schema:
      type: object
      properties:
        traceId:
          type: string
        records:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
                example: "rec_xyz789"
              query:
                type: string
                example: "如何分析财报？"
              answer:
                type: string
                example: "分析财报主要关注以下几个方面..."
              llm_used:
                type: boolean
                example: true
              model:
                type: string
                example: "gpt-4"
              answer_source:
                type: string
                example: "copaw"
              response_time_ms:
                type: integer
                example: 2345
              timestamp:
                type: string
                format: date-time
  404:
    description: 会话不存在
    schema:
      type: object
      properties:
        error:
          type: object
          properties:
            code:
              type: string
              example: "SESSION_NOT_FOUND"
"""
