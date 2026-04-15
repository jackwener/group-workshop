# 09 — API 接口规格（引导版模板）

---

| 项 | 值 |
|---|---|
| 模块编号 | M1-QA |
| 模块名称 | 投研问答助手 |
| 文档版本 | v0.1 |
| 阶段 | Design（How — 契约真源） |
| Base URL | `/api/v1/agent` |

---

> **本文是全部 API 端点的契约真源**。`05` 定义"用户要什么"，**09（本文）定义"后端必须返回什么"**，`13` 的测试断言以本文为准。

## 1. 端点总览

| # | 端点 | 方法 | 功能 | 成功码 | 对应用户故事 |
|---|------|------|------|--------|-------------|
| 1 | `/api/v1/agent/capabilities` | GET | 能力探测 | 200 | US-005 |
| 2 | `/api/v1/agent/health` | GET | 健康检查 | 200 | US-004 |
| 3 | `/api/v1/agent/sessions` | GET | 会话列表 | 200 | US-001 |
| 4 | `/api/v1/agent/sessions` | POST | 新建会话 | 201 | US-001 |
| 5 | `/api/v1/agent/sessions/<id>` | DELETE | 删除会话 | 200 | US-001 |
| 6 | `/api/v1/agent/sessions/<id>/records` | GET | 问答记录 | 200 | US-003 |
| 7 | `/api/v1/agent/upload` | POST | 上传研报文档 | 200 | US-002 |
| 8 | `/api/v1/agent/ask` | POST | 问答提交 | 200 | US-002 |
| 9 | `/api/v1/agent/research/comparison` | GET | 研报对比查询 | 200 | US-003 |

## 2. 统一响应规范

### 成功响应

```json
{ "traceId": "tr_abc123...", /* 业务字段 */ }
```

### 错误响应

```json
{ "error": { "code": "EMPTY_QUERY", "message": "请输入问题", "details": {}, "traceId": "tr_..." } }
```

### 错误码清单

| HTTP | error.code | 触发条件 | details |
|------|-----------|----------|---------|
| 400 | `EMPTY_QUERY` | query 为空/null | `{}` |
| 400 | `INVALID_QUERY` | query 超 500 字符 | `{"max_length":500}` |
| 400 | `INVALID_TITLE` | session title 超 100 字符 | `{"max_length":100}` |
| 400 | `INVALID_SESSION_ID` | session_id 格式无效 | `{}` |
| 400 | `INVALID_PAGE` | page < 1 | `{"min":1}` |
| 400 | `INVALID_PAGE_SIZE` | page_size 不在 1-100 范围 | `{"min":1,"max":100}` |
| 400 | `FILE_TOO_LARGE` | 上传文件超过 10MB | `{"max_size_mb":10}` |
| 400 | `UNSUPPORTED_FORMAT` | 不支持的文件格式 | `{"supported":["pdf","docx","xlsx"]}` |
| 403 | `PERMISSION_DENIED` | 用户无权限访问 | `{}` |
| 404 | `SESSION_NOT_FOUND` | 会话不存在 | `{"session_id":"<id>"}` |
| 503 | `LLM_UNAVAILABLE` | LLM 服务不可用 | `{"provider":"copaw/bailian"}` |

## 3. ★ 示例：POST /ask — 问答提交

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `query` | string | **是** | 1–500 字符 | 用户提问原文 |
| `session_id` | string | **是** | UUID | 目标会话 ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `answer` | string | 是 | 答案文本 |
| `llm_used` | boolean | 是 | 是否使用真实 LLM |
| `model` | string\|null | 是 | 模型标识 |
| `response_time_ms` | integer | 是 | 响应耗时（毫秒） |
| `answer_source` | string | 是 | copaw / bailian / demo |

## 4. POST /sessions — 新建会话

**请求体**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `title` | string | 否 | "新会话" | 会话标题，≤100 字符 |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 会话 ID（UUID 格式） |
| `title` | string | 是 | 会话标题 |
| `created_at` | string | 是 | 创建时间（ISO 8601） |
| `query_count` | integer | 是 | 问答次数（默认 0） |

**响应示例**：

```json
{
  "traceId": "tr_abc123",
  "session_id": "sess_550e8400-e29b-41d4-a716-446655440000",
  "title": "半导体行业分析",
  "created_at": "2024-01-15T10:30:00Z",
  "query_count": 0
}
```

## 5. GET /sessions — 会话列表

> 无请求体，返回 sessions 数组。每个 session 按 updated_at 降序排列。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `sessions` | array[Session] | 是 | 会话列表 |

**Session 对象字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `session_id` | string | 会话 ID |
| `title` | string | 会话标题 |
| `created_at` | string | 创建时间（ISO 8601） |
| `updated_at` | string | 最后更新时间（ISO 8601） |
| `query_count` | integer | 问答次数 |

**响应示例**：

```json
{
  "traceId": "tr_abc123",
  "sessions": [
    {
      "session_id": "sess_001",
      "title": "半导体行业分析",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T14:20:00Z",
      "query_count": 5
    },
    {
      "session_id": "sess_002",
      "title": "新能源研报对比",
      "created_at": "2024-01-14T09:00:00Z",
      "updated_at": "2024-01-14T16:45:00Z",
      "query_count": 3
    }
  ]
}
```

## 6. DELETE /sessions/<id> — 删除会话

> 路径参数 session_id，无请求体，返回确认消息。注意级联删除关联记录。

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 会话 ID（UUID 格式） |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `message` | string | 是 | "会话已删除" |
| `deleted_session_id` | string | 是 | 已删除的会话 ID |

**副作用说明**：
- 级联删除该会话下所有问答记录（`/sessions/<id>/records`）
- 从会话列表中移除
- 删除关联的上传文件（如果有）

**响应示例**：

```json
{
  "traceId": "tr_abc123",
  "message": "会话已删除",
  "deleted_session_id": "sess_550e8400-e29b-41d4-a716-446655440000"
}
```

**错误响应**：

| HTTP | error.code | 说明 |
|------|-----------|------|
| 404 | `SESSION_NOT_FOUND` | 会话不存在 |
| 400 | `INVALID_SESSION_ID` | session_id 格式无效 |

## 7. GET /sessions/<id>/records — 问答记录

> 路径参数 session_id，返回 records 数组。每条记录含 query、answer、timestamp 等。

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 会话 ID（UUID 格式） |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `records` | array[Record] | 是 | 问答记录列表 |

**Record 对象字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `record_id` | string | 记录 ID |
| `query` | string | 用户提问原文 |
| `answer` | string | AI 回答文本 |
| `answer_source` | string | 答案来源：copaw / bailian / demo |
| `llm_used` | boolean | 是否使用真实 LLM |
| `model` | string/null | 模型标识（如未使用 LLM 则为 null） |
| `response_time_ms` | integer | 响应耗时（毫秒） |
| `timestamp` | string | 记录时间（ISO 8601） |
| `sources` | array[string] | 引用来源列表（可选） |

**响应示例**：

```json
{
  "traceId": "tr_abc123",
  "records": [
    {
      "record_id": "rec_001",
      "query": "半导休行业未来发展趋势如何？",
      "answer": "根据最新研报，半导体行业...",
      "answer_source": "bailian",
      "llm_used": true,
      "model": "qwen-max",
      "response_time_ms": 1250,
      "timestamp": "2024-01-15T14:20:00Z",
      "sources": ["中信证券-半导体行业深度报告"]
    },
    {
      "record_id": "rec_002",
      "query": "推荐哪些半导体股票？",
      "answer": "基于研报分析，建议关注...",
      "answer_source": "copaw",
      "llm_used": true,
      "model": "gpt-4",
      "response_time_ms": 980,
      "timestamp": "2024-01-15T14:25:00Z",
      "sources": ["华泰证券-半导体投资建议"]
    }
  ]
}
```

**错误响应**：

| HTTP | error.code | 说明 |
|------|-----------|------|
| 404 | `SESSION_NOT_FOUND` | 会话不存在 |

## 8. POST /upload — 上传研报文档

> 对应 US-002，支持 PDF/Word/Excel 格式研报上传，最大 10MB。

**请求体**：`multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | file | 是 | PDF/Word/Excel 文件，≤10MB |
| `session_id` | string | 是 | 目标会话 ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `file_id` | string | 是 | 文件 ID |
| `filename` | string | 是 | 原始文件名 |
| `file_size` | integer | 是 | 文件大小（bytes） |
| `file_type` | string | 是 | 文件类型：pdf / docx / xlsx |
| `upload_status` | string | 是 | 上传状态：success / failed |
| `processing_status` | string | 是 | 处理状态：pending / processing / completed |
| `key_points` | object/null | 否 | 提取的重点信息（处理完成后返回） |

**响应示例**：

```json
{
  "traceId": "tr_abc123",
  "file_id": "file_001",
  "filename": "中信证券-半导体行业深度报告.pdf",
  "file_size": 2457600,
  "file_type": "pdf",
  "upload_status": "success",
  "processing_status": "completed",
  "key_points": {
    "rating": "强于大市",
    "target_price": 150.5,
    "core_viewpoints": ["行业景气度回升", "国产替代加速"]
  }
}
```

**错误响应**：

| HTTP | error.code | 说明 |
|------|-----------|------|
| 400 | `FILE_TOO_LARGE` | 文件超过 10MB |
| 400 | `UNSUPPORTED_FORMAT` | 不支持的文件格式 |
| 404 | `SESSION_NOT_FOUND` | 会话不存在 |

## 9. GET /research/comparison — 研报对比查询

> 对应 US-003，支持多维度检索研报，按分页展示。

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `company` | string | 否 | - | 公司名（模糊匹配） |
| `industry` | string | 否 | - | 行业（模糊匹配） |
| `publisher` | string | 否 | - | 发布人/机构（模糊匹配） |
| `start_date` | string | 否 | - | 开始日期（ISO 8601） |
| `end_date` | string | 否 | - | 结束日期（ISO 8601） |
| `page` | integer | 否 | 1 | 页码，≥1 |
| `page_size` | integer | 否 | 10 | 每页数量，1-100 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `total` | integer | 是 | 总数 |
| `page` | integer | 是 | 当前页 |
| `page_size` | integer | 是 | 每页数量 |
| `reports` | array[Report] | 是 | 研报列表 |

**Report 对象字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `report_id` | string | 研报 ID |
| `title` | string | 研报标题 |
| `company` | string | 公司名 |
| `industry` | string | 行业 |
| `publisher` | string | 发布机构 |
| `publish_date` | string | 发布日期（ISO 8601） |
| `rating` | string | 评级（如：强于大市、买入） |
| `target_price` | number/null | 目标价 |
| `score` | number | 综合评分（0-100） |
| `tags` | array[string] | 标签列表 |

**响应示例**：

```json
{
  "traceId": "tr_abc123",
  "total": 25,
  "page": 1,
  "page_size": 10,
  "reports": [
    {
      "report_id": "rpt_001",
      "title": "半导体行业深度报告",
      "company": "中芯国际",
      "industry": "半导体",
      "publisher": "中信证券",
      "publish_date": "2024-01-10",
      "rating": "强于大市",
      "target_price": 150.5,
      "score": 92.5,
      "tags": ["国产替代", "景气度回升"]
    }
  ]
}
```

**错误响应**：

| HTTP | error.code | 说明 |
|------|-----------|------|
| 400 | `INVALID_PAGE` | page < 1 |
| 400 | `INVALID_PAGE_SIZE` | page_size 不在 1-100 范围 |

## 10. GET /health — 健康检查

> 对应 US-004，系统健康检查，返回各组件状态。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `status` | string | 是 | 系统状态：healthy / degraded / unhealthy |
| `timestamp` | string | 是 | 检查时间（ISO 8601） |
| `components` | object | 是 | 组件状态 |
| `uptime_seconds` | integer | 是 | 系统运行时间（秒） |

**Components 对象字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `llm_service` | object | LLM 服务状态 |
| `file_storage` | object | 文件存储状态 |
| `database` | object | 数据库状态 |

**子组件字段**（每个 component）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 状态：healthy / degraded / unhealthy |
| `provider` | string/null | 提供商（如：copaw / bailian / demo） |

**响应示例**：

```json
{
  "traceId": "tr_abc123",
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": {
    "llm_service": {
      "status": "healthy",
      "provider": "bailian"
    },
    "file_storage": {
      "status": "healthy"
    },
    "database": {
      "status": "healthy"
    }
  },
  "uptime_seconds": 86400
}
```

## 11. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 非空 | 400 | `INVALID_SESSION_ID` |
| POST /sessions | `title` | ≤100 字符 | 400 | `INVALID_TITLE` |
| DELETE /sessions/<id> | `id` | 有效 UUID | 400 | `INVALID_SESSION_ID` |
| GET /sessions/<id>/records | `id` | 有效 UUID | 400 | `INVALID_SESSION_ID` |
| POST /upload | `file` | ≤10MB | 400 | `FILE_TOO_LARGE` |
| POST /upload | `file` | pdf/docx/xlsx | 400 | `UNSUPPORTED_FORMAT` |
| POST /upload | `session_id` | 非空 | 400 | `INVALID_SESSION_ID` |
| GET /research/comparison | `page` | ≥1 | 400 | `INVALID_PAGE` |
| GET /research/comparison | `page_size` | 1-100 | 400 | `INVALID_PAGE_SIZE` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 【日期】 | 首版填写 |
