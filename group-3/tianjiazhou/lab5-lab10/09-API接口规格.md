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
| 400 | `EMPTY_QUERY` | query 为空/null/空白 | `{}` |
| 400 | `INVALID_QUERY` | query 超 500 字符 或 缺少 session_id | `{"max_length":500}` |
| 404 | `SESSION_NOT_FOUND` | session_id 不存在 | `{"session_id":"..."}` |
| 500 | `UPSTREAM_ERROR` | Agent 编排内部异常 | `{"source":"..."}` |

## 3. GET /capabilities — 能力探测

**请求**：无参数

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `copaw_configured` | boolean | 是 | CoPaw 桥接是否已配置 |
| `bailian_configured` | boolean | 是 | 百炼是否已配置 |
| `bailian_model` | string\|null | 是 | 百炼模型标识，未配置时为 null |

**响应示例**：

```json
{
  "traceId": "tr_a1b2c3d4e5f6...",
  "copaw_configured": false,
  "bailian_configured": true,
  "bailian_model": "qwen-turbo"
}
```

## 4. POST /ask — 问答提交

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
| `model` | string\|null | 是 | 模型标识，Demo 模式为 null |
| `response_time_ms` | integer | 是 | 响应耗时（毫秒） |
| `answer_source` | string | 是 | copaw / bailian / demo |

**响应示例**：

```json
{
  "traceId": "tr_d4e5f6a1b2c3...",
  "answer": "根据近期多份医药行业研报分析，共同观点包括...",
  "llm_used": true,
  "model": "qwen-turbo",
  "response_time_ms": 2340,
  "answer_source": "bailian"
}
```

## 5. POST /sessions — 新建会话

**请求体**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `title` | string | 否 | "新会话" | 会话标题 |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 新建会话的 UUID |
| `title` | string | 是 | 会话标题 |
| `created_at` | string | 是 | ISO-8601 创建时间 |
| `query_count` | integer | 是 | 初始值 0 |

**响应示例**：

```json
{
  "traceId": "tr_f6a1b2c3d4e5...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "新会话",
  "created_at": "2026-04-14T10:30:00Z",
  "query_count": 0
}
```

## 6. GET /sessions — 会话列表

**请求**：无参数

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `sessions` | array | 是 | 会话列表 |
| `sessions[].session_id` | string | 是 | 会话 UUID |
| `sessions[].title` | string | 是 | 会话标题 |
| `sessions[].created_at` | string | 是 | ISO-8601 创建时间 |
| `sessions[].query_count` | integer | 是 | 累计问答次数 |

**响应示例**：

```json
{
  "traceId": "tr_b2c3d4e5f6a1...",
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "医药行业观点分析...",
      "created_at": "2026-04-14T10:30:00Z",
      "query_count": 5
    }
  ]
}
```

## 7. DELETE /sessions/<id> — 删除会话

**路径参数**：`session_id`（UUID）

**请求体**：无

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `message` | string | 是 | 确认消息 |
| `deleted_records` | integer | 是 | 级联删除的问答记录数 |

**副作用**：级联删除该会话关联的所有 QARecord。

**响应示例**：

```json
{
  "traceId": "tr_c3d4e5f6a1b2...",
  "message": "会话已删除",
  "deleted_records": 3
}
```

## 8. GET /sessions/<id>/records — 问答记录

**路径参数**：`session_id`（UUID）

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `records` | array | 是 | 问答记录列表（按时间正序） |
| `records[].id` | string | 是 | 记录 ID（`rec_{ts}`） |
| `records[].session_id` | string | 是 | 所属会话 ID |
| `records[].query` | string | 是 | 用户提问 |
| `records[].answer` | string | 是 | AI 回答 |
| `records[].llm_used` | boolean | 是 | 是否使用 LLM |
| `records[].model` | string\|null | 是 | 模型标识 |
| `records[].response_time_ms` | integer | 是 | 响应耗时 |
| `records[].answer_source` | string | 是 | copaw / bailian / demo |
| `records[].timestamp` | string | 是 | ISO-8601 记录时间 |

**响应示例**：

```json
{
  "traceId": "tr_e5f6a1b2c3d4...",
  "records": [
    {
      "id": "rec_1713089400",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "query": "近期医药行业有哪些共同观点？",
      "answer": "根据最近发布的多份研报...",
      "llm_used": true,
      "model": "qwen-turbo",
      "response_time_ms": 2100,
      "answer_source": "bailian",
      "timestamp": "2026-04-14T10:35:00Z"
    }
  ]
}
```

## 9. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 非空 | 400 | `INVALID_QUERY` |
| DELETE /sessions/<id> | `session_id` | 路径参数存在 | 404 | `SESSION_NOT_FOUND` |
| GET /sessions/<id>/records | `session_id` | 路径参数存在 | 404 | `SESSION_NOT_FOUND` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 首版填写 |
