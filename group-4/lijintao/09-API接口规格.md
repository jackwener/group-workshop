# 09 — API 接口规格

---

| 项 | 值 |
|---|---|
| 模块编号 | M1-QA |
| 模块名称 | 投研问答助手 |
| 文档版本 | v0.1 |
| 阶段 | Design（How — 契约真源） |
| Base URL | `/api/v1` |

---

> **本文是全部 API 端点的契约真源**。`05` 定义"用户要什么"，**09（本文）定义"后端必须返回什么"**，`13` 的测试断言以本文为准。

---

## 1. 端点总览

| # | 端点 | 方法 | 功能 | 成功码 | 来源 |
|---|------|------|------|--------|------|
| 1 | `/health` | GET | 健康检查 | 200 | US-004 |
| 2 | `/health/detailed` | GET | 详细健康状态 | 200 | US-004 |
| 3 | `/sessions` | GET | 会话列表 | 200 | US-001 |
| 4 | `/sessions` | POST | 新建会话 | 201 | US-001 |
| 5 | `/sessions/{id}` | GET | 会话详情 | 200 | US-001 |
| 6 | `/sessions/{id}` | DELETE | 删除会话 | 200 | US-001 |
| 7 | `/sessions/{id}/messages` | GET | 获取会话消息 | 200 | US-003 |
| 8 | `/sessions/{id}/messages` | POST | 发送消息（流式） | 200 | US-002 |
| 9 | `/sessions/{id}/messages/search` | GET | 搜索会话消息 | 200 | US-003 |
| 10 | `/history/search` | GET | 全局历史搜索 | 200 | US-003 |

---

## 2. 统一响应规范

### 2.1 成功响应

```json
{
  "traceId": "tr_abc123def456",
  "data": { /* 业务数据 */ },
  "timestamp": "2026-04-14T10:30:00.000Z"
}
```

### 2.2 错误响应

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {},
    "traceId": "tr_abc123def456",
    "timestamp": "2026-04-14T10:30:00.000Z"
  }
}
```

### 2.3 错误码清单

| HTTP | error.code | 触发条件 | details |
|------|-----------|----------|---------|
| 400 | `EMPTY_QUERY` | query 为空/null | `{}` |
| 400 | `INVALID_QUERY` | query 超 4000 字符 | `{"max_length": 4000, "actual": 4500}` |
| 400 | `INVALID_SESSION_ID` | session_id 格式错误 | `{"expected": "UUID format"}` |
| 400 | `INVALID_PARAMS` | 请求参数校验失败 | `{"field": "title", "reason": "required"}` |
| 401 | `UNAUTHORIZED` | 未登录或 Token 无效 | `{}` |
| 403 | `FORBIDDEN` | 无权限访问该资源 | `{"resource": "session", "id": "xxx"}` |
| 404 | `SESSION_NOT_FOUND` | 会话不存在 | `{"session_id": "xxx"}` |
| 404 | `MESSAGE_NOT_FOUND` | 消息不存在 | `{"message_id": "xxx"}` |
| 429 | `RATE_LIMITED` | 请求过于频繁 | `{"retry_after": 30, "limit": 60}` |
| 500 | `INTERNAL_ERROR` | 服务器内部错误 | `{"detail": "具体错误信息"}` |
| 503 | `LLM_UNAVAILABLE` | LLM 服务不可用 | `{"providers": ["azure", "openai"], "status": "all_failed"}` |
| 503 | `SERVICE_DEGRADED` | 服务降级中 | `{"mode": "local_model", "message": "当前使用本地模型"}` |

---

## 3. 健康检查接口

### 3.1 GET /health — 基础健康检查

**功能**：快速检查服务可用性

**请求参数**：无

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.status` | string | 是 | 状态：`healthy` / `degraded` / `unhealthy` |
| `data.timestamp` | string | 是 | ISO 8601 时间戳 |

**响应示例**：
```json
{
  "traceId": "tr_7f8a9b2c3d4e",
  "data": {
    "status": "healthy",
    "timestamp": "2026-04-14T10:30:00.000Z"
  },
  "timestamp": "2026-04-14T10:30:00.000Z"
}
```

---

### 3.2 GET /health/detailed — 详细健康状态

**功能**：获取系统各组件详细健康状态

**请求参数**：无

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.status` | string | 是 | 整体状态：`healthy` / `degraded` / `unhealthy` |
| `data.components` | object | 是 | 各组件状态 |
| `data.components.database` | object | 是 | 数据库状态 |
| `data.components.database.status` | string | 是 | `healthy` / `unhealthy` |
| `data.components.database.latency_ms` | integer | 是 | 连接延迟（毫秒） |
| `data.components.cache` | object | 是 | Redis 状态 |
| `data.components.cache.status` | string | 是 | `healthy` / `unhealthy` |
| `data.components.cache.latency_ms` | integer | 是 | 连接延迟（毫秒） |
| `data.components.llm` | object | 是 | LLM 服务状态 |
| `data.components.llm.status` | string | 是 | `healthy` / `degraded` / `unhealthy` |
| `data.components.llm.providers` | array | 是 | 各提供商状态列表 |
| `data.timestamp` | string | 是 | ISO 8601 时间戳 |

**响应示例**：
```json
{
  "traceId": "tr_8g9h0i1j2k3l",
  "data": {
    "status": "healthy",
    "components": {
      "database": {
        "status": "healthy",
        "latency_ms": 12
      },
      "cache": {
        "status": "healthy",
        "latency_ms": 3
      },
      "llm": {
        "status": "healthy",
        "providers": [
          {"name": "azure_openai", "status": "healthy", "latency_ms": 245},
          {"name": "openai", "status": "standby", "latency_ms": null},
          {"name": "local", "status": "standby", "latency_ms": null}
        ]
      }
    },
    "timestamp": "2026-04-14T10:30:00.000Z"
  },
  "timestamp": "2026-04-14T10:30:00.000Z"
}
```

---

## 4. 会话管理接口

### 4.1 GET /sessions — 获取会话列表

**功能**：获取当前用户的所有会话列表

**查询参数**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 20 | 每页数量（最大 100） |
| `sort_by` | string | 否 | `updated_at` | 排序字段：`created_at` / `updated_at` / `title` |
| `sort_order` | string | 否 | `desc` | 排序方向：`asc` / `desc` |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.total` | integer | 是 | 总会话数 |
| `data.page` | integer | 是 | 当前页码 |
| `data.page_size` | integer | 是 | 每页数量 |
| `data.sessions` | array | 是 | 会话列表 |
| `data.sessions[].id` | string | 是 | 会话 ID（UUID） |
| `data.sessions[].title` | string | 是 | 会话标题 |
| `data.sessions[].message_count` | integer | 是 | 消息数量 |
| `data.sessions[].created_at` | string | 是 | 创建时间（ISO 8601） |
| `data.sessions[].updated_at` | string | 是 | 最后更新时间（ISO 8601） |

**响应示例**：
```json
{
  "traceId": "tr_a1b2c3d4e5f6",
  "data": {
    "total": 42,
    "page": 1,
    "page_size": 20,
    "sessions": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "项目A投研讨论",
        "message_count": 15,
        "created_at": "2026-04-14T08:00:00.000Z",
        "updated_at": "2026-04-14T10:25:00.000Z"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "title": "新会话",
        "message_count": 0,
        "created_at": "2026-04-14T09:00:00.000Z",
        "updated_at": "2026-04-14T09:00:00.000Z"
      }
    ]
  },
  "timestamp": "2026-04-14T10:30:00.000Z"
}
```

---

### 4.2 POST /sessions — 新建会话

**功能**：创建新的对话会话

**请求体**：

| 字段 | 类型 | 必填 | 默认值 | 约束 | 说明 |
|------|------|------|--------|------|------|
| `title` | string | 否 | "新会话" | 1-200 字符 | 会话标题 |

**请求示例**：
```json
{
  "title": "Q2 财报分析"
}
```

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.id` | string | 是 | 会话 ID（UUID） |
| `data.title` | string | 是 | 会话标题 |
| `data.message_count` | integer | 是 | 消息数量（初始为 0） |
| `data.created_at` | string | 是 | 创建时间（ISO 8601） |
| `data.updated_at` | string | 是 | 更新时间（ISO 8601） |

**响应示例**：
```json
{
  "traceId": "tr_b2c3d4e5f6g7",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "title": "Q2 财报分析",
    "message_count": 0,
    "created_at": "2026-04-14T10:30:00.000Z",
    "updated_at": "2026-04-14T10:30:00.000Z"
  },
  "timestamp": "2026-04-14T10:30:00.000Z"
}
```

---

### 4.3 GET /sessions/{id} — 获取会话详情

**功能**：获取指定会话的详细信息

**路径参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 会话 ID（UUID） |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.id` | string | 是 | 会话 ID |
| `data.title` | string | 是 | 会话标题 |
| `data.message_count` | integer | 是 | 消息数量 |
| `data.created_at` | string | 是 | 创建时间 |
| `data.updated_at` | string | 是 | 最后更新时间 |

---

### 4.4 DELETE /sessions/{id} — 删除会话

**功能**：删除指定会话及其所有消息（级联删除）

**路径参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 会话 ID（UUID） |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.id` | string | 是 | 已删除的会话 ID |
| `data.deleted` | boolean | 是 | 是否成功删除 |
| `data.deleted_messages_count` | integer | 是 | 级联删除的消息数量 |
| `data.message` | string | 是 | 操作结果描述 |

**响应示例**：
```json
{
  "traceId": "tr_c3d4e5f6g7h8",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "deleted": true,
    "deleted_messages_count": 15,
    "message": "会话及其 15 条消息已永久删除"
  },
  "timestamp": "2026-04-14T10:30:00.000Z"
}
```

**副作用**：
- 级联删除该会话下的所有消息记录
- 清除相关缓存数据
- 记录审计日志

---

## 5. 消息接口

### 5.1 GET /sessions/{id}/messages — 获取会话消息

**功能**：获取指定会话的所有消息记录

**路径参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 会话 ID（UUID） |

**查询参数**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 50 | 每页数量（最大 100） |
| `before_id` | string | 否 | - | 获取该 ID 之前的消息（用于向上翻页） |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.session_id` | string | 是 | 会话 ID |
| `data.total` | integer | 是 | 总消息数 |
| `data.messages` | array | 是 | 消息列表（按时间正序） |
| `data.messages[].id` | string | 是 | 消息 ID |
| `data.messages[].role` | string | 是 | 角色：`user` / `assistant` / `system` |
| `data.messages[].content` | string | 是 | 消息内容 |
| `data.messages[].tokens` | integer | 否 | Token 数量 |
| `data.messages[].model` | string | 否 | 使用的模型 |
| `data.messages[].provider` | string | 否 | LLM 提供商 |
| `data.messages[].latency_ms` | integer | 否 | 响应延迟（毫秒） |
| `data.messages[].created_at` | string | 是 | 创建时间 |

**响应示例**：
```json
{
  "traceId": "tr_d4e5f6g7h8i9",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "total": 15,
    "messages": [
      {
        "id": "msg_001",
        "role": "user",
        "content": "分析一下新能源行业的发展趋势",
        "created_at": "2026-04-14T10:00:00.000Z"
      },
      {
        "id": "msg_002",
        "role": "assistant",
        "content": "新能源行业近年来呈现以下发展趋势...",
        "tokens": 856,
        "model": "gpt-4",
        "provider": "azure_openai",
        "latency_ms": 1250,
        "created_at": "2026-04-14T10:00:03.000Z"
      }
    ]
  },
  "timestamp": "2026-04-14T10:30:00.000Z"
}
```

---

### 5.2 POST /sessions/{id}/messages — 发送消息（流式）

**功能**：向指定会话发送消息，获取 AI 流式响应

**路径参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 会话 ID（UUID） |

**请求体**：

| 字段 | 类型 | 必填 | 默认值 | 约束 | 说明 |
|------|------|------|--------|------|------|
| `content` | string | 是 | - | 1-4000 字符 | 用户消息内容 |
| `stream` | boolean | 否 | true | - | 是否启用流式响应 |
| `model` | string | 否 | auto | - | 指定模型，auto 为自动选择 |

**请求示例**：
```json
{
  "content": "总结一下刚才讨论的要点",
  "stream": true,
  "model": "auto"
}
```

**成功响应**（200 - 非流式）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.message_id` | string | 是 | 用户消息 ID |
| `data.response_id` | string | 是 | AI 响应消息 ID |
| `data.content` | string | 是 | AI 响应内容 |
| `data.model` | string | 是 | 实际使用的模型 |
| `data.provider` | string | 是 | LLM 提供商 |
| `data.tokens_input` | integer | 是 | 输入 Token 数 |
| `data.tokens_output` | integer | 是 | 输出 Token 数 |
| `data.latency_ms` | integer | 是 | 响应延迟（毫秒） |
| `data.is_degraded` | boolean | 是 | 是否为降级模式 |
| `data.created_at` | string | 是 | 响应时间 |

**响应示例**（非流式）：
```json
{
  "traceId": "tr_e5f6g7h8i9j0",
  "data": {
    "message_id": "msg_003",
    "response_id": "msg_004",
    "content": "根据我们的讨论，主要要点如下：1. ... 2. ...",
    "model": "gpt-4",
    "provider": "azure_openai",
    "tokens_input": 150,
    "tokens_output": 320,
    "latency_ms": 1250,
    "is_degraded": false,
    "created_at": "2026-04-14T10:30:03.000Z"
  },
  "timestamp": "2026-04-14T10:30:03.000Z"
}
```

**流式响应**（SSE 格式）：

```
Content-Type: text/event-stream

id: 1
event: message_start
data: {"type": "message_start", "message_id": "msg_004", "model": "gpt-4"}

id: 2
event: content_block_delta
data: {"type": "content_block_delta", "delta": {"text": "根据"}}

id: 3
event: content_block_delta
data: {"type": "content_block_delta", "delta": {"text": "我们的"}}

...

id: N
event: message_stop
data: {"type": "message_stop", "usage": {"input_tokens": 150, "output_tokens": 320}, "latency_ms": 1250}
```

**降级响应**（当 LLM 不可用时）：
```json
{
  "traceId": "tr_f6g7h8i9j0k1",
  "data": {
    "message_id": "msg_003",
    "response_id": "msg_004",
    "content": "当前 LLM 服务暂时不可用，已切换至离线模式。请稍后再试或联系管理员。",
    "model": "local",
    "provider": "local",
    "tokens_input": 0,
    "tokens_output": 0,
    "latency_ms": 50,
    "is_degraded": true,
    "degraded_reason": "LLM_SERVICE_UNAVAILABLE",
    "created_at": "2026-04-14T10:30:00.000Z"
  },
  "timestamp": "2026-04-14T10:30:00.000Z"
}
```

---

### 5.3 GET /sessions/{id}/messages/search — 搜索会话消息

**功能**：在指定会话内搜索消息内容

**路径参数**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 会话 ID（UUID） |

**查询参数**：

| 字段 | 类型 | 必填 | 默认值 | 约束 | 说明 |
|------|------|------|--------|------|------|
| `q` | string | 是 | - | 1-100 字符 | 搜索关键词 |
| `role` | string | 否 | all | `user`/`assistant`/`all` | 筛选角色 |
| `page` | integer | 否 | 1 | - | 页码 |
| `page_size` | integer | 否 | 20 | 最大 50 | 每页数量 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.session_id` | string | 是 | 会话 ID |
| `data.query` | string | 是 | 搜索关键词 |
| `data.total` | integer | 是 | 匹配结果数 |
| `data.messages` | array | 是 | 匹配的消息列表 |
| `data.messages[].id` | string | 是 | 消息 ID |
| `data.messages[].role` | string | 是 | 角色 |
| `data.messages[].content` | string | 是 | 消息内容（高亮标记） |
| `data.messages[].highlight_positions` | array | 是 | 高亮位置数组 |
| `data.messages[].created_at` | string | 是 | 创建时间 |

**响应示例**：
```json
{
  "traceId": "tr_g7h8i9j0k1l2",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "query": "预算",
    "total": 3,
    "messages": [
      {
        "id": "msg_010",
        "role": "assistant",
        "content": "根据<mark>预算</mark>报告，本季度...",
        "highlight_positions": [{"start": 2, "end": 4}],
        "created_at": "2026-04-14T09:30:00.000Z"
      }
    ]
  },
  "timestamp": "2026-04-14T10:30:00.000Z"
}
```

---

## 6. 历史记录接口

### 6.1 GET /history/search — 全局历史搜索

**功能**：跨所有会话搜索历史消息

**查询参数**：

| 字段 | 类型 | 必填 | 默认值 | 约束 | 说明 |
|------|------|------|--------|------|------|
| `q` | string | 是 | - | 1-100 字符 | 搜索关键词 |
| `start_date` | string | 否 | - | ISO 8601 | 开始日期 |
| `end_date` | string | 否 | - | ISO 8601 | 结束日期 |
| `page` | integer | 否 | 1 | - | 页码 |
| `page_size` | integer | 否 | 20 | 最大 50 | 每页数量 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `data.query` | string | 是 | 搜索关键词 |
| `data.total` | integer | 是 | 匹配结果数 |
| `data.results` | array | 是 | 搜索结果列表 |
| `data.results[].message_id` | string | 是 | 消息 ID |
| `data.results[].session_id` | string | 是 | 所属会话 ID |
| `data.results[].session_title` | string | 是 | 会话标题 |
| `data.results[].role` | string | 是 | 角色 |
| `data.results[].content` | string | 是 | 消息内容（高亮） |
| `data.results[].created_at` | string | 是 | 创建时间 |

---

## 7. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /sessions | `title` | 1-200 字符 | 400 | `INVALID_PARAMS` |
| POST /sessions/{id}/messages | `content` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /sessions/{id}/messages | `content` | ≤ 4000 字符 | 400 | `INVALID_QUERY` |
| POST /sessions/{id}/messages | `id` (路径) | UUID 格式 | 400 | `INVALID_SESSION_ID` |
| GET /sessions/{id}/messages | `id` (路径) | UUID 格式 | 400 | `INVALID_SESSION_ID` |
| DELETE /sessions/{id} | `id` (路径) | UUID 格式 | 400 | `INVALID_SESSION_ID` |
| GET /sessions/{id}/messages/search | `q` | 1-100 字符 | 400 | `INVALID_PARAMS` |
| GET /history/search | `q` | 1-100 字符 | 400 | `INVALID_PARAMS` |
| 所有接口 | `Authorization` | Bearer Token | 401 | `UNAUTHORIZED` |
| 所有接口 | - | 频率限制 60/分钟 | 429 | `RATE_LIMITED` |

---

## 8. 接口与需求追溯

| 接口 | 方法 | 路径 | 对应 User Story | 验收标准 |
|------|------|------|-----------------|----------|
| 获取会话列表 | GET | /sessions | US-001 | AC-001-02 |
| 新建会话 | POST | /sessions | US-001 | AC-001-01 |
| 删除会话 | DELETE | /sessions/{id} | US-001 | AC-001-03 |
| 发送消息 | POST | /sessions/{id}/messages | US-002 | AC-002-01, AC-002-02, AC-002-03 |
| 获取消息 | GET | /sessions/{id}/messages | US-003 | AC-003-01 |
| 搜索会话消息 | GET | /sessions/{id}/messages/search | US-003 | AC-003-02 |
| 全局历史搜索 | GET | /history/search | US-003 | AC-003-02 |
| 健康检查 | GET | /health | US-004 | AC-004-01 |
| 详细健康状态 | GET | /health/detailed | US-004 | AC-004-01, AC-004-03 |

---

## 9. 版本管理

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 首版，基于 Next.js + FastAPI 架构设计，包含会话管理、问答提交、历史记录、健康检查接口 |

---

## 附录：接口调用示例

### cURL 示例

**创建会话**：
```bash
curl -X POST https://api.example.com/api/v1/sessions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "投研分析"}'
```

**发送消息（非流式）**：
```bash
curl -X POST https://api.example.com/api/v1/sessions/{id}/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "分析一下市场趋势", "stream": false}'
```

**发送消息（流式）**：
```bash
curl -X POST https://api.example.com/api/v1/sessions/{id}/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"content": "分析一下市场趋势", "stream": true}'
```

**搜索消息**：
```bash
curl "https://api.example.com/api/v1/sessions/{id}/messages/search?q=预算" \
  -H "Authorization: Bearer <token>"
```
