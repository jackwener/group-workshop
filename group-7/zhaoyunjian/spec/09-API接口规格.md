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

| # | 端点 | 方法 | 功能 | 成功码 |
|---|------|------|------|--------|
| 1 | `/api/v1/agent/capabilities` | GET | 能力探测 | 200 |
| 2 | `/api/v1/agent/ask` | POST | 问答提交 | 200 |
| 3 | `/api/v1/agent/sessions` | GET | 会话列表 | 200 |
| 4 | `/api/v1/agent/sessions` | POST | 新建会话 | 201 |
| 5 | `/api/v1/agent/sessions/<id>` | DELETE | 删除会话 | 200 |
| 6 | `/api/v1/agent/sessions/<id>/records` | GET | 问答记录 | 200 |
| 7 | `/api/v1/agent/reports` | POST | 上传研报 | 201 |
| 8 | `/api/v1/agent/reports` | GET | 研报列表 | 200 |
| 9 | `/api/v1/agent/reports/<id>` | DELETE | 删除研报 | 200 |
| 10 | `/api/v1/agent/reports/<id>/analyze` | POST | 分析研报 | 200 |
| 11 | `/api/v1/agent/health` | GET | 健康检查 | 200 |
| 12 | `/api/v1/agent/export` | POST | 导出对比结果 | 200 |

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
| 400 | `EMPTY_SESSION_ID` | session_id 为空/null | `{}` |
| 400 | `INVALID_SESSION_ID` | session_id 格式非法 | `{"format":"UUID"}` |
| 404 | `SESSION_NOT_FOUND` | 会话不存在 | `{"session_id":"xxx"}` |
| 400 | `EMPTY_FILE` | 上传文件为空 | `{}` |
| 400 | `INVALID_FILE_TYPE` | 文件类型不支持 | `{"supported":["pdf","doc","docx"]}` |
| 404 | `REPORT_NOT_FOUND` | 研报不存在 | `{"report_id":"xxx"}` |
| 500 | `LLM_UNAVAILABLE` | LLM服务不可用 | `{"fallback":"demo"}` |
| 500 | `ANALYSIS_FAILED` | 研报分析失败 | `{"report_id":"xxx"}` |

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
| `title` | string | 否 | "新会话" | 会话标题，最大100字符 |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 会话唯一标识（UUID） |
| `title` | string | 是 | 会话标题 |
| `created_at` | string | 是 | 创建时间（ISO 8601格式） |
| `query_count` | integer | 是 | 当前会话问答次数，初始为0 |

**响应示例**：
```json
{
  "traceId": "tr_abc123def456",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "新会话",
  "created_at": "2025-04-14T10:30:00Z",
  "query_count": 0
}
```

## 5. GET /sessions — 会话列表

> 无请求体，返回 sessions 数组。

**查询参数**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | integer | 否 | 1 | 页码，从1开始 |
| `page_size` | integer | 否 | 20 | 每页数量，最大100 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `total` | integer | 是 | 总会话数 |
| `page` | integer | 是 | 当前页码 |
| `page_size` | integer | 是 | 每页数量 |
| `sessions` | array | 是 | 会话列表 |
| `sessions[].session_id` | string | 是 | 会话唯一标识 |
| `sessions[].title` | string | 是 | 会话标题 |
| `sessions[].created_at` | string | 是 | 创建时间 |
| `sessions[].updated_at` | string | 是 | 最后更新时间 |
| `sessions[].query_count` | integer | 是 | 问答次数 |

**响应示例**：
```json
{
  "traceId": "tr_abc123def456",
  "total": 15,
  "page": 1,
  "page_size": 20,
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "新能源行业分析",
      "created_at": "2025-04-14T10:30:00Z",
      "updated_at": "2025-04-14T11:00:00Z",
      "query_count": 5
    }
  ]
}
```

## 6. DELETE /sessions/<id> — 删除会话

> 路径参数 session_id，无请求体。

**路径参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 会话ID（UUID） |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `deleted` | boolean | 是 | 是否删除成功 |
| `session_id` | string | 是 | 被删除的会话ID |

**副作用**：级联删除该会话下的所有问答记录（records）。

**响应示例**：
```json
{
  "traceId": "tr_abc123def456",
  "deleted": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## 7. GET /sessions/<id>/records — 问答记录

> 路径参数 session_id，返回该会话的问答记录数组。

**路径参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 会话ID（UUID） |

**查询参数**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 20 | 每页数量 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 会话ID |
| `total` | integer | 是 | 总记录数 |
| `records` | array | 是 | 问答记录列表 |
| `records[].record_id` | string | 是 | 记录唯一标识 |
| `records[].query` | string | 是 | 用户提问 |
| `records[].answer` | string | 是 | 系统回答 |
| `records[].timestamp` | string | 是 | 回答时间 |
| `records[].llm_used` | boolean | 是 | 是否使用真实LLM |
| `records[].model` | string\|null | 是 | 模型标识 |
| `records[].answer_source` | string | 是 | copaw / bailian / demo |

**响应示例**：
```json
{
  "traceId": "tr_abc123def456",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "total": 5,
  "records": [
    {
      "record_id": "rec_123456789",
      "query": "分析宁德时代2024年财报",
      "answer": "宁德时代2024年营收同比增长15%...",
      "timestamp": "2025-04-14T10:35:00Z",
      "llm_used": true,
      "model": "gpt-4",
      "answer_source": "copaw"
    }
  ]
}
```

## 8. POST /reports — 上传研报

**请求体**（multipart/form-data）：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | file | **是** | 研报文件，支持pdf/doc/docx，最大50MB |
| `title` | string | 否 | 研报标题，默认使用文件名 |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `report_id` | string | 是 | 研报唯一标识 |
| `title` | string | 是 | 研报标题 |
| `filename` | string | 是 | 原始文件名 |
| `file_size` | integer | 是 | 文件大小（字节） |
| `uploaded_at` | string | 是 | 上传时间 |
| `status` | string | 是 | pending / analyzing / analyzed / failed |

**响应示例**：
```json
{
  "traceId": "tr_abc123def456",
  "report_id": "rep_789xyz",
  "title": "宁德时代2024年深度研报",
  "filename": "宁德时代2024研报.pdf",
  "file_size": 2048576,
  "uploaded_at": "2025-04-14T10:30:00Z",
  "status": "pending"
}
```

## 9. GET /reports — 研报列表

**查询参数**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 20 | 每页数量 |
| `status` | string | 否 | - | 按状态筛选：pending/analyzing/analyzed/failed |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `total` | integer | 是 | 总研报数 |
| `reports` | array | 是 | 研报列表 |
| `reports[].report_id` | string | 是 | 研报ID |
| `reports[].title` | string | 是 | 研报标题 |
| `reports[].filename` | string | 是 | 文件名 |
| `reports[].status` | string | 是 | 分析状态 |
| `reports[].uploaded_at` | string | 是 | 上传时间 |
| `reports[].analyzed_at` | string\|null | 是 | 分析完成时间 |

## 10. DELETE /reports/<id> — 删除研报

**路径参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 研报ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `deleted` | boolean | 是 | 是否删除成功 |
| `report_id` | string | 是 | 被删除的研报ID |

## 11. POST /reports/<id>/analyze — 分析研报

**路径参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 研报ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `report_id` | string | 是 | 研报ID |
| `status` | string | 是 | analyzing / analyzed |
| `analysis` | object\|null | 是 | 分析结果（仅status=analyzed时有值） |
| `analysis.company` | string | 否 | 公司名称 |
| `analysis.key_metrics` | array | 否 | 关键指标数组 |
| `analysis.summary` | string | 否 | 研报摘要 |

## 12. GET /health — 健康检查

> 无请求体，返回系统健康状态。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `status` | string | 是 | healthy / degraded / unhealthy |
| `timestamp` | string | 是 | 检查时间 |
| `services` | object | 是 | 各服务状态 |
| `services.llm` | object | 是 | LLM服务状态 |
| `services.llm.status` | string | 是 | available / unavailable |
| `services.llm.provider` | string | 否 | copaw / bailian / demo |
| `services.database` | string | 是 | ok / error |
| `metrics` | object | 是 | 运行指标 |
| `metrics.active_sessions` | integer | 是 | 活跃会话数 |
| `metrics.total_queries` | integer | 是 | 总查询次数 |
| `metrics.avg_response_time_ms` | integer | 是 | 平均响应时间 |

**响应示例**：
```json
{
  "traceId": "tr_abc123def456",
  "status": "healthy",
  "timestamp": "2025-04-14T10:30:00Z",
  "services": {
    "llm": {
      "status": "available",
      "provider": "copaw"
    },
    "database": "ok"
  },
  "metrics": {
    "active_sessions": 12,
    "total_queries": 156,
    "avg_response_time_ms": 1200
  }
}
```

## 13. POST /export — 导出对比结果

**请求体**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `report_ids` | array | **是** | 要对比的研报ID数组，至少2个 |
| `format` | string | **是** | 导出格式：pdf / excel |
| `company` | string | **是** | 对比的公司名称 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `export_id` | string | 是 | 导出任务ID |
| `status` | string | 是 | processing / completed |
| `download_url` | string\|null | 是 | 下载链接（仅completed时有值） |
| `expires_at` | string\|null | 是 | 链接过期时间 |

## 14. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 非空 | 400 | `EMPTY_SESSION_ID` |
| POST /ask | `session_id` | UUID格式 | 400 | `INVALID_SESSION_ID` |
| POST /sessions | `title` | ≤ 100 字符 | 400 | `INVALID_TITLE` |
| GET /sessions/<id>/records | `id` | 会话存在 | 404 | `SESSION_NOT_FOUND` |
| DELETE /sessions/<id> | `id` | 会话存在 | 404 | `SESSION_NOT_FOUND` |
| POST /reports | `file` | 非空 | 400 | `EMPTY_FILE` |
| POST /reports | `file` | 类型为pdf/doc/docx | 400 | `INVALID_FILE_TYPE` |
| DELETE /reports/<id> | `id` | 研报存在 | 404 | `REPORT_NOT_FOUND` |
| POST /reports/<id>/analyze | `id` | 研报存在 | 404 | `REPORT_NOT_FOUND` |
| POST /export | `report_ids` | 数组长度≥2 | 400 | `INVALID_REPORT_COUNT` |
| POST /export | `format` | 值为pdf/excel | 400 | `INVALID_FORMAT` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2025-04-14 | 首版填写 |
