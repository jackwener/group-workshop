# 09 — API 接口规格

---

| 项 | 值 |
|---|---|
| 模块编号 | M1-IRA |
| 模块名称 | 投研智能问答助手 |
| 文档版本 | v0.1 |
| 阶段 | Design（How — 契约真源） |
| Base URL | `/api/v1/agent`（教学版：`http://localhost:5000`；生产版：`https://{domain}`）|
| 上游 | `05` UserStory 与验收标准 |
| 下游 | → `10` 数据模型 · `13` 测试用例 |

---

> **本文是全部 API 端点的契约真源**。`05` 定义"用户要什么"，**09（本文）定义"后端必须返回什么"**，`13` 的测试断言以本文为准。

## 1. 端点总览

| # | 端点 | 方法 | 功能 | 成功码 | 对齐 US |
|---|------|------|------|--------|----------|
| 1 | `/capabilities` | GET | 能力探测 | 200 | US-004 |
| 2 | `/ask` | POST | 问答提交 | 200 | US-002 |
| 3 | `/sessions` | GET | 会话列表 | 200 | US-001 |
| 4 | `/sessions` | POST | 新建会话 | 201 | US-001 |
| 5 | `/sessions/{id}` | DELETE | 删除会话 | 200 | US-001 |
| 6 | `/sessions/{id}/records` | GET | 问答记录 | 200 | US-003 |

## 2. 统一响应规范

### 成功响应

```json
{
  "traceId": "tr_abc123def456",
  "data": { /* 业务字段 */ }
}
```

### 错误响应

```json
{
  "error": {
    "code": "EMPTY_QUERY",
    "message": "请输入问题",
    "details": {},
    "traceId": "tr_abc123def456"
  }
}
```

### 错误码清单

| HTTP | error.code | 触发条件 | details |
|------|-----------|----------|---------|
| 400 | `EMPTY_QUERY` | query 为空/null/空白 | `{}` |
| 400 | `INVALID_QUERY` | query 超 500 字符 | `{"max_length": 500, "actual": 520}` |
| 400 | `SESSION_NOT_FOUND` | session_id 不存在 | `{"session_id": "xxx"}` |
| 429 | `RATE_LIMIT_EXCEEDED` | 请求频率超限（生产版）| `{"limit": 100, "window": "1min"}` |
| 500 | `UPSTREAM_ERROR` | 外部 LLM 服务异常 | `{"source": "copaw|bailian"}` |

> **注**：教学版无速率限制，不返回 429；生产版启用速率限制后需返回此错误码。

## 3. GET /capabilities — 能力探测

> 对齐 `05` US-004 AC-004-01：系统显示当前可用能力状态

**请求**：无参数

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.copaw_configured` | boolean | 是 | CoPaw 是否已配置 |
| `data.bailian_configured` | boolean | 是 | 百炼是否已配置 |
| `data.model` | string\|null | 是 | 当前使用的模型名称 |
| `data.mode` | string | 是 | 当前模式：`copaw` / `bailian` / `demo` |

**响应示例**：

```json
{
  "traceId": "tr_cap_001",
  "data": {
    "copaw_configured": false,
    "bailian_configured": true,
    "model": "qwen-turbo",
    "mode": "bailian"
  }
}
```

## 4. POST /ask — 问答提交

> 对齐 `05` US-002 AC-002-01~05：研报问答核心能力

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `query` | string | **是** | 1–500 字符，非空白 | 用户提问原文 |
| `session_id` | string | **是** | UUID 格式 | 目标会话 ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.answer` | string | 是 | 答案文本 |
| `data.llm_used` | boolean | 是 | 是否使用真实 LLM |
| `data.model` | string\|null | 是 | 模型标识（如 qwen-turbo）|
| `data.response_time_ms` | integer | 是 | 响应耗时（毫秒）|
| `data.answer_source` | string | 是 | 答案来源：`copaw` / `bailian` / `demo` |
| `data.record_id` | string | 是 | 新生成的问答记录 ID |

**响应示例**：

```json
{
  "traceId": "tr_ask_001",
  "data": {
    "answer": "根据研报分析，该公司的目标价为 45.6 元，评级为\"买入\"...",
    "llm_used": true,
    "model": "qwen-turbo",
    "response_time_ms": 2340,
    "answer_source": "bailian",
    "record_id": "rec_abc123"
  }
}
```

**降级模式响应**（Demo）：

```json
{
  "traceId": "tr_ask_002",
  "data": {
    "answer": "【演示回复】您的问题已收到，这是一个离线演示回复。配置 LLM 密钥后可获得真实答案。",
    "llm_used": false,
    "model": null,
    "response_time_ms": 50,
    "answer_source": "demo",
    "record_id": "rec_def456"
  }
}
```

## 5. POST /sessions — 新建会话

> 对齐 `05` US-001 AC-001-01：用户可创建新会话，系统自动生成 session_id 和默认标题

**请求体**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `title` | string | 否 | "新会话" | 会话标题（最长 100 字符）|

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.session_id` | string | 是 | 新建会话 ID（UUID）|
| `data.title` | string | 是 | 会话标题 |
| `data.created_at` | string | 是 | 创建时间（ISO 8601）|
| `data.updated_at` | string | 是 | 更新时间（ISO 8601）|
| `data.query_count` | integer | 是 | 问答数量（初始为 0）|

**响应示例**：

```json
{
  "traceId": "tr_sess_001",
  "data": {
    "session_id": "sess_abc123def456",
    "title": "新会话",
    "created_at": "2026-04-14T10:30:00Z",
    "updated_at": "2026-04-14T10:30:00Z",
    "query_count": 0
  }
}
```

## 6. GET /sessions — 会话列表

> 对齐 `05` US-001 AC-001-02：用户可查看所有会话列表，按创建时间倒序排列

**请求**：无请求体

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `limit` | integer | 否 | 50 | 返回数量限制（1-100）|
| `offset` | integer | 否 | 0 | 分页偏移量 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.sessions` | array | 是 | 会话列表 |
| `data.total` | integer | 是 | 会话总数 |
| `data.sessions[].session_id` | string | 是 | 会话 ID |
| `data.sessions[].title` | string | 是 | 会话标题 |
| `data.sessions[].created_at` | string | 是 | 创建时间 |
| `data.sessions[].updated_at` | string | 是 | 更新时间 |
| `data.sessions[].query_count` | integer | 是 | 问答数量 |

**响应示例**：

```json
{
  "traceId": "tr_list_001",
  "data": {
    "sessions": [
      {
        "session_id": "sess_abc123",
        "title": "招商银行2025年一季报分析",
        "created_at": "2026-04-14T10:30:00Z",
        "updated_at": "2026-04-14T11:00:00Z",
        "query_count": 5
      },
      {
        "session_id": "sess_def456",
        "title": "宁德时代研报要点...",
        "created_at": "2026-04-13T09:00:00Z",
        "updated_at": "2026-04-13T09:15:00Z",
        "query_count": 3
      }
    ],
    "total": 2
  }
}
```

## 7. DELETE /sessions/{id} — 删除会话

> 对齐 `05` US-001 AC-001-03：用户可删除指定会话，删除后级联删除该会话下所有问答记录

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 会话 ID |

**请求体**：无

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.message` | string | 是 | 删除确认消息 |
| `data.deleted_session_id` | string | 是 | 被删除的会话 ID |
| `data.deleted_records_count` | integer | 是 | 级联删除的问答记录数 |

**响应示例**：

```json
{
  "traceId": "tr_del_001",
  "data": {
    "message": "会话删除成功",
    "deleted_session_id": "sess_abc123",
    "deleted_records_count": 5
  }
}
```

**副作用**：
- 删除 session 记录
- 级联删除该 session 下所有 QARecord

## 8. GET /sessions/{id}/records — 问答记录

> 对齐 `05` US-003 AC-003-01~03：查看历史问答记录

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 会话 ID |

**查询参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `limit` | integer | 否 | 50 | 返回数量限制 |
| `offset` | integer | 否 | 0 | 分页偏移量 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.session_id` | string | 是 | 所属会话 ID |
| `data.records` | array | 是 | 问答记录列表（按时间正序）|
| `data.total` | integer | 是 | 记录总数 |
| `data.records[].id` | string | 是 | 记录 ID |
| `data.records[].query` | string | 是 | 用户问题 |
| `data.records[].answer` | string | 是 | AI 回答 |
| `data.records[].llm_used` | boolean | 是 | 是否使用真实 LLM |
| `data.records[].model` | string\|null | 是 | 模型标识 |
| `data.records[].response_time_ms` | integer | 是 | 响应耗时 |
| `data.records[].answer_source` | string | 是 | 答案来源 |
| `data.records[].timestamp` | string | 是 | 问答时间 |

**响应示例**：

```json
{
  "traceId": "tr_rec_001",
  "data": {
    "session_id": "sess_abc123",
    "records": [
      {
        "id": "rec_001",
        "query": "这份研报的核心观点是什么？",
        "answer": "核心观点是：该公司2025年业绩增长确定性较高...",
        "llm_used": true,
        "model": "qwen-turbo",
        "response_time_ms": 2100,
        "answer_source": "bailian",
        "timestamp": "2026-04-14T10:35:00Z"
      },
      {
        "id": "rec_002",
        "query": "目标价和评级是多少？",
        "answer": "目标价 45.6 元，评级 \"买入\"...",
        "llm_used": true,
        "model": "qwen-turbo",
        "response_time_ms": 1800,
        "answer_source": "bailian",
        "timestamp": "2026-04-14T10:36:00Z"
      }
    ],
    "total": 2
  }
}
```

## 9. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 非空且存在 | 400 | `SESSION_NOT_FOUND` |
| POST /sessions | `title` | ≤ 100 字符 | 400 | `INVALID_QUERY` |
| DELETE /sessions/{id} | `id` | 会话存在 | 404 | `SESSION_NOT_FOUND` |
| GET /sessions/{id}/records | `id` | 会话存在 | 404 | `SESSION_NOT_FOUND` |

## 10. US → API 对齐表

| UserStory | API 端点 | 关联 AC |
|-----------|----------|----------|
| US-001 会话管理 | POST /sessions | AC-001-01 |
| US-001 会话管理 | GET /sessions | AC-001-02 |
| US-001 会话管理 | DELETE /sessions/{id} | AC-001-03 |
| US-002 研报问答 | POST /ask | AC-002-01~05 |
| US-003 问答历史 | GET /sessions/{id}/records | AC-003-01~03 |
| US-004 数据安全 | GET /capabilities | AC-004-01~03 |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 基于03/04/05文档生成首版 |
