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
| 400 | `INVALID_QUERY` | query 超 500 字符 | `{"max_length":500}` |
| 404 | `SESSION_NOT_FOUND` | session_id 不存在或已软删除 | `{"session_id":"<id>"}` |
| 422 | `MISSING_FIELD` | 必填字段缺失 | `{"field":"<字段名>"}` |
| 503 | `LLM_UNAVAILABLE` | 所有 LLM 层级均不可用，Demo 模式也失败 | `{"degraded":true}` |

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
| `cited_passages` | array\|null | 是 | 原文引用段落列表，Demo 模式下为 null |

**cited_passages 子项结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `text` | string | 引用的原文段落内容 |
| `page` | integer\|null | 来源页码，HTML 格式时为 null |
| `source_file` | string | 来源研报文件名 |

## 4. POST /sessions — 新建会话

**请求体**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `title` | string | 否 | "新会话" | 会话标题，最长 100 字符 |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 新建会话的唯一 UUID |
| `title` | string | 是 | 会话标题（用户传入值或默认值） |
| `created_at` | string | 是 | 创建时间，ISO 8601 格式，如 `2026-04-14T10:00:00Z` |
| `query_count` | integer | 是 | 初始值为 0 |
| `status` | string | 是 | 固定为 `active` |

## 5. GET /sessions — 会话列表

> 无请求体，返回 sessions 数组，按 `created_at` 倒序排列，仅返回 `status=active` 的会话。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `sessions` | array | 是 | 会话对象列表，空时返回 `[]` |
| `sessions[].session_id` | string | 是 | 会话唯一 UUID |
| `sessions[].title` | string | 是 | 会话标题 |
| `sessions[].created_at` | string | 是 | 创建时间，ISO 8601 |
| `sessions[].query_count` | integer | 是 | 该会话累计问答条数 |
| `sessions[].status` | string | 是 | 固定为 `active` |

**响应示例**：

```json
{
  "traceId": "tr_xyz789",
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "宁德时代研报分析",
      "created_at": "2026-04-14T09:30:00Z",
      "query_count": 5,
      "status": "active"
    }
  ]
}
```

## 6. DELETE /sessions/<id> — 删除会话

> 路径参数：`session_id`（UUID）；无请求体。执行软删除，将 `status` 置为 `deleted`，不物理清除数据；关联的 records 记录同步标记为不可访问。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 被删除的会话 UUID |
| `status` | string | 是 | 固定返回 `deleted` |
| `deleted_at` | string | 是 | 删除时间，ISO 8601 |

**副作用**：
- `sessions` 表中该记录 `status` 由 `active` → `deleted`
- 后续 `GET /sessions` 列表不再返回该会话
- 后续访问 `GET /sessions/<id>/records` 返回 404 `SESSION_NOT_FOUND`
- 原始数据保留，不触发物理删除

**响应示例**：

```json
{
  "traceId": "tr_del001",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "deleted",
  "deleted_at": "2026-04-14T11:00:00Z"
}
```

## 7. GET /sessions/<id>/records — 问答记录

> 路径参数：`session_id`（UUID）；无请求体。若会话不存在或已删除，返回 404。记录按 `created_at` 正序排列。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 对应会话 UUID |
| `records` | array | 是 | 问答记录列表，空时返回 `[]` |
| `records[].record_id` | string | 是 | 记录唯一 UUID |
| `records[].query` | string | 是 | 用户提问原文 |
| `records[].answer` | string | 是 | 系统回答文本 |
| `records[].answer_source` | string | 是 | copaw / bailian / demo |
| `records[].cited_passages` | array\|null | 是 | 原文引用段落列表，结构同 §3 |
| `records[].created_at` | string | 是 | 记录时间，ISO 8601 |

**响应示例**：

```json
{
  "traceId": "tr_rec002",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "records": [
    {
      "record_id": "a1b2c3d4-0000-0000-0000-000000000001",
      "query": "这份研报对宁德时代的评级是什么？",
      "answer": "该研报给出"买入"评级，目标价 320 元，核心逻辑为...",
      "answer_source": "copaw",
      "cited_passages": [
        {
          "text": "维持买入评级，目标价 320 元，较当前股价上涨空间约 25%。",
          "page": 3,
          "source_file": "CATL_20260410_招商证券.pdf"
        }
      ],
      "created_at": "2026-04-14T09:35:00Z"
    }
  ]
}
```

## 8. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 非空 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 会话存在且状态为 active | 404 | `SESSION_NOT_FOUND` |
| POST /sessions | `title` | 若传入则 ≤ 100 字符 | 400 | `INVALID_QUERY` |
| DELETE /sessions/<id> | `session_id`（路径） | 会话存在且状态为 active | 404 | `SESSION_NOT_FOUND` |
| GET /sessions/<id>/records | `session_id`（路径） | 会话存在且状态为 active | 404 | `SESSION_NOT_FOUND` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 首版填写 |