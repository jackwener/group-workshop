# 09 — API 接口规格（引导版模板）

---

| 项 | 值 |
|---|---|
| 模块编号 | M1-QA |
| 模块名称 | 投研问答助手 |
| 文档版本 | v0.1 |
| 阶段 | Design（How — 契约真源） |
| Base URL | `http://localhost:5000/api/v1/agent` |

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
| 7 | `/api/v1/agent/sessions/<id>/export` | GET | 导出会话 | 200 |

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
| 404 | `SESSION_NOT_FOUND` | session_id 不存在 | `{"session_id":"xxx"}` |
| 400 | `INVALID_SESSION_ID` | session_id 格式非法 | `{}` |
| 429 | `RATE_LIMITED` | 请求频率超限 | `{"retry_after":60}` |

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
| `session_id` | string | 是 | 会话唯一标识（UUID） |
| `title` | string | 是 | 会话标题 |
| `created_at` | string | 是 | 创建时间（ISO-8601） |
| `query_count` | integer | 是 | 累计问答次数，初始为 0 |

## 5. GET /sessions — 会话列表（请填写）

> 无请求体，返回 sessions 数组。每个 session 至少包含 id、title、created_at、query_count。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `sessions` | array | 是 | 会话列表，按 updated_at 倒序排列 |

**sessions 数组元素结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `session_id` | string | 会话唯一标识 |
| `title` | string | 会话标题 |
| `created_at` | string | 创建时间（ISO-8601） |
| `updated_at` | string | 最后更新时间（ISO-8601） |
| `query_count` | integer | 累计问答次数 |

## 6. DELETE /sessions/<id> — 删除会话（请填写）

> 路径参数 session_id，无请求体，返回确认消息。注意级联删除关联记录。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `deleted` | boolean | 是 | 是否成功删除 |
| `deleted_records_count` | integer | 是 | 级联删除的问答记录数量 |

**副作用**：删除 Session 后，自动删除该会话下的所有 QARecord（级联删除）。

## 7. GET /sessions/<id>/records — 问答记录（请填写）

> 路径参数 session_id，返回 records 数组。每条记录含 query、answer、timestamp 等。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `records` | array | 是 | 问答记录列表，按 timestamp 正序排列 |

**records 数组元素结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 记录唯一标识（rec_{timestamp}） |
| `query` | string | 用户提问原文 |
| `answer` | string | AI 回答内容 |
| `llm_used` | boolean | 是否使用真实 LLM |
| `model` | string\|null | 模型标识 |
| `response_time_ms` | integer | 响应耗时（毫秒） |
| `answer_source` | string | 回答来源：copaw/bailian/demo |
| `timestamp` | string | 记录时间（ISO-8601） |

## 8. GET /sessions/<id>/export — 导出会话记录（请填写）

> 路径参数 session_id，支持导出格式选择。将会话的所有问答记录导出为指定格式文件。

**查询参数**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `format` | string | 否 | `json` | 导出格式：`json` 或 `txt` |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `download_url` | string | 是 | 临时下载链接（有效期 5 分钟） |
| `filename` | string | 是 | 导出文件名 |
| `record_count` | integer | 是 | 导出的记录数量 |
| `format` | string | 是 | 实际导出格式 |

**错误响应**：

| HTTP | error.code | 触发条件 |
|------|-----------|----------|
| 404 | `SESSION_NOT_FOUND` | session_id 不存在 |
| 400 | `INVALID_FORMAT` | format 参数非法（非 json/txt） |
| 400 | `EMPTY_SESSION` | 会话无问答记录可导出 |

## 9. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 非空 | 400 | `INVALID_QUERY` |
| POST /sessions | `title` | ≤ 23 字符 | 400 | `INVALID_TITLE` |
| DELETE /sessions/<id> | `session_id` | 非空/格式合法 | 404 | `SESSION_NOT_FOUND` |
| GET /sessions/<id>/records | `session_id` | 非空/格式合法 | 404 | `SESSION_NOT_FOUND` |
| GET /sessions/<id>/export | `session_id` | 非空/格式合法 | 404 | `SESSION_NOT_FOUND` |
| GET /sessions/<id>/export | `format` | 枚举：json/txt | 400 | `INVALID_FORMAT` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2025-04-14 | 首版填写 |
