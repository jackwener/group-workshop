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
| 400 | `EMPTY_QUERY` | query 为空/null | `{}` |
| 400 | `INVALID_QUERY` | query 超 500 字符 或 缺少 session_id | `{"max_length":500}` |
| 404 | `SESSION_NOT_FOUND` | session_id 对应的会话不存在 | `{"session_id":"..."}` |
| 408 | `TIMEOUT_ERROR` | 请求超时（超过 SLO 阈值） | `{}` |
| 429 | `RATE_LIMIT_ERROR` | 请求过于频繁（生产环境） | `{"retry_after_seconds":60}` |
| 500 | `UPSTREAM_ERROR` | Agent 编排内部异常 | `{"detail":"..."}` |

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

## 4. POST /sessions — 新建会话（请填写）

**请求体**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `title` | string | 否 | "新会话" | 会话标题 |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string (UUID) | 是 | 新创建的会话 ID |
| `title` | string | 是 | 会话标题，默认“新会话” |
| `created_at` | string (ISO-8601) | 是 | 创建时间 |
| `updated_at` | string (ISO-8601) | 是 | 最后更新时间 |
| `query_count` | integer | 是 | 累计问答次数，初始为 0 |

## 5. GET /sessions — 会话列表（请填写）

> 无请求体，返回 sessions 数组。每个 session 至少包含 id、title、created_at、query_count。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `sessions` | array | 是 | 会话列表 |
| `sessions[].session_id` | string (UUID) | 是 | 会话 ID |
| `sessions[].title` | string | 是 | 会话标题 |
| `sessions[].created_at` | string (ISO-8601) | 是 | 创建时间 |
| `sessions[].updated_at` | string (ISO-8601) | 是 | 最后更新时间 |
| `sessions[].query_count` | integer | 是 | 累计问答次数 |

## 6. DELETE /sessions/<id> — 删除会话（请填写）

> 路径参数 session_id，无请求体，返回确认消息。注意级联删除关联记录。

**路径参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string (UUID) | **是** | 待删除的会话 ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `success` | boolean | 是 | 是否删除成功 |
| `message` | string | 是 | 操作结果描述 |

**副作用**：
- 级联删除该会话下所有 QARecord 记录
- 会话不存在时返回 404 `SESSION_NOT_FOUND`

## 7. GET /sessions/<id>/records — 问答记录（请填写）

> 路径参数 session_id，返回 records 数组。每条记录含 query、answer、timestamp 等。

**路径参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string (UUID) | **是** | 会话 ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `records` | array | 是 | 问答记录列表 |
| `records[].id` | string | 是 | 记录 ID（`rec_{timestamp_ms}`） |
| `records[].session_id` | string (UUID) | 是 | 所属会话 ID |
| `records[].query` | string | 是 | 用户提问原文 |
| `records[].answer` | string | 是 | AI 回答内容 |
| `records[].llm_used` | boolean | 是 | 是否使用真实 LLM |
| `records[].model` | string\|null | 是 | 模型标识 |
| `records[].response_time_ms` | integer | 是 | 响应耗时（毫秒） |
| `records[].answer_source` | string | 是 | copaw / bailian / demo |
| `records[].timestamp` | string (ISO-8601) | 是 | 记录创建时间 |

## 8. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 非空 | 400 | `INVALID_QUERY` |
| POST /sessions | `title` | ≤ 23 字符（可选，超出截断） | — | 自动截断 |
| DELETE /sessions/\<id\> | `id` | 非空，存在的会话 ID | 404 | `SESSION_NOT_FOUND` |
| GET /sessions/\<id\>/records | `id` | 非空，存在的会话 ID | 404 | `SESSION_NOT_FOUND` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2025-04-14 | 首版填写 |
