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
| 2 | `/api/v1/agent/ask` | POST | 问答提交（SSE 流式） | 200 (text/event-stream) |
| 3 | `/api/v1/agent/sessions` | GET | 会话列表 | 200 |
| 4 | `/api/v1/agent/sessions` | POST | 新建会话 | 201 |
| 5 | `/api/v1/agent/sessions/<id>` | DELETE | 删除会话 | 200 |
| 6 | `/api/v1/agent/sessions/<id>/records` | GET | 问答记录 | 200 |
| 7 | `/api/v1/agent/records/search` | GET | 历史记录搜索 | 200 |
| 8 | `/api/v1/agent/records/similar` | POST | 相似提问检测 | 200 |
| 9 | `/api/v1/agent/stock/<code>` | GET | 股票信息查询 | 200 |

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
| 400 | `SESSION_NOT_FOUND` | session_id 不存在 | `{"session_id":"xxx"}` |
| 500 | `UPSTREAM_ERROR` | LLM 服务异常 | `{"provider":"copaw"}` |

## 3. ★ POST /ask — 问答提交（SSE 流式）

> 对齐 US-002：流式回复研报关键信息。响应为 `text/event-stream`，前端通过 EventSource 接收。

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `query` | string | **是** | 1–500 字符 | 用户提问原文 |
| `session_id` | string | **是** | UUID | 目标会话 ID |

**SSE 事件流**：

| 事件 | data 内容 | 说明 |
|------|------------|------|
| `chunk` | `{"text": "部分回答内容"}` | 每次推送一段回答文本 |
| `done` | `{"traceId":"tr_...", "answer":"...", "llm_used":true, "model":"...", "response_time_ms":1200, "answer_source":"bailian", "stocks":[{"name":"贵州茅台","code":"600519"}]}` | 流式完成，返回完整元数据 |
| `error` | `{"code":"EMPTY_QUERY", "message":"..."}` | 错误事件 |

**兼容非流式模式**：当请求头不包含 `Accept: text/event-stream` 时，回退为普通 JSON 响应（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `answer` | string | 是 | 答案文本 |
| `llm_used` | boolean | 是 | 是否使用真实 LLM |
| `model` | string\|null | 是 | 模型标识 |
| `response_time_ms` | integer | 是 | 响应耗时（毫秒） |
| `answer_source` | string | 是 | copaw / bailian / demo |
| `stocks` | array | 是 | 回答中识别的股票列表 `[{name,code}]` |

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
| `query_count` | integer | 是 | 问答次数，初始为 0 |

## 5. GET /sessions — 会话列表（请填写）

> 无请求体，返回 sessions 数组。每个 session 至少包含 id、title、created_at、query_count。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `sessions` | array | 是 | 会话列表，按时间倒序 |

**sessions 数组元素**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `session_id` | string | 会话唯一标识 |
| `title` | string | 会话标题 |
| `created_at` | string | 创建时间（ISO-8601） |
| `updated_at` | string | 最后更新时间（ISO-8601） |
| `query_count` | integer | 问答次数 |

## 6. DELETE /sessions/<id> — 删除会话（请填写）

> 路径参数 session_id，无请求体，返回确认消息。注意级联删除关联记录。

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 会话 ID（UUID） |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `message` | string | 是 | 删除成功提示 |
| `deleted_records` | integer | 是 | 级联删除的问答记录数 |

**副作用**：删除会话时，级联删除该会话下的所有问答记录。

## 7. GET /sessions/<id>/records — 问答记录（请填写）

> 路径参数 session_id，返回 records 数组。每条记录含 query、answer、timestamp 等。

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 会话 ID（UUID） |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `records` | array | 是 | 问答记录列表，按时间正序 |

**records 数组元素**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 记录唯一标识 |
| `query` | string | 用户提问原文 |
| `answer` | string | 系统回答内容 |
| `llm_used` | boolean | 是否使用真实 LLM |
| `model` | string\|null | 模型标识 |
| `response_time_ms` | integer | 响应耗时（毫秒） |
| `answer_source` | string | 回答来源：copaw/bailian/demo |
| `timestamp` | string | 记录时间（ISO-8601） |

## 8. GET /records/search — 历史记录搜索（对齐 US-003 AC-003-01）

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `keyword` | string | 是 | 搜索关键词，匹配 query 和 answer |
| `limit` | integer | 否 | 返回条数，默认 20 |

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `traceId` | string | 链路追踪 ID |
| `records` | array | 匹配的问答记录，包含 session_id 以便跳转 |

## 9. POST /records/similar — 相似提问检测（对齐 US-003 AC-003-02）

**请求体**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | 是 | 待检测的提问内容 |

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `traceId` | string | 链路追踪 ID |
| `has_similar` | boolean | 是否存在相似提问 |
| `similar_records` | array | 相似的历史记录，包含 session_id |

## 10. GET /stock/<code> — 股票信息查询（对齐 US-004）

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `code` | string | 股票代码（如 600519） |

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `traceId` | string | 链路追踪 ID |
| `code` | string | 股票代码 |
| `name` | string | 股票名称 |
| `summary` | string | 研报摘要信息 |
| `latest_reports` | array | 相关研报列表 |

## 11. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 非空 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 存在有效会话 | 400 | `SESSION_NOT_FOUND` |
| GET /records/search | `keyword` | 非空 | 400 | `EMPTY_QUERY` |
| POST /records/similar | `query` | 非空 | 400 | `EMPTY_QUERY` |
| GET /stock/<code> | `code` | 非空 | 400 | `INVALID_QUERY` |
| DELETE /sessions/<id> | `id` | 存在有效会话 | 400 | `SESSION_NOT_FOUND` |
| GET /sessions/<id>/records | `id` | 存在有效会话 | 400 | `SESSION_NOT_FOUND` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 首版填写 |
| v0.2 | 2026-04-14 | 对齐05修正：POST /ask 改SSE流式、新增搜索/相似/股票端点 |
