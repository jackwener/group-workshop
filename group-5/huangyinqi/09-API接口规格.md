# 09 — API 接口规格

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
| 7 | `/api/v1/agent/reports` | POST | 研报上传解析 | 201 |
| 8 | `/api/v1/agent/reports` | GET | 研报列表查询 | 200 |
| 9 | `/api/v1/agent/reports/<id>` | GET | 研报详情查看 | 200 |
| 10 | `/api/v1/agent/reports/<id>` | DELETE | 研报删除 | 200 |

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
| 400 | `INVALID_SESSION` | session_id 不存在 | `{}` |
| 400 | `INVALID_FILE_FORMAT` | 文件格式非PDF/HTML | `{"supported_formats":["pdf","html"]}` |
| 400 | `FILE_TOO_LARGE` | 文件超过大小限制 | `{"max_size":"10MB"}` |
| 401 | `UNAUTHORIZED` | 用户未登录 | `{}` |
| 404 | `NOT_FOUND` | 资源不存在 | `{"resource":"session"}` |
| 500 | `LLM_UNAVAILABLE` | LLM服务不可用 | `{"fallback":"demo"}` |

## 3. POST /ask — 问答提交

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `query` | string | **是** | 1–500 字符 | 用户提问原文 |
| `session_id` | string | **是** | UUID | 目标会话 ID |
| `report_id` | string | 否 | UUID | 关联研报ID（可选） |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `answer` | string | 是 | 答案文本 |
| `llm_used` | boolean | 是 | 是否使用真实 LLM |
| `model` | string\|null | 是 | 模型标识 |
| `response_time_ms` | integer | 是 | 响应耗时（毫秒） |
| `answer_source` | string | 是 | copaw / bailian / demo |
| `session_id` | string | 是 | 会话ID |
| `timestamp` | string | 是 | 响应时间戳 |

## 4. POST /sessions — 新建会话

**请求体**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `title` | string | 否 | "新会话" | 会话标题 |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 会话唯一标识 |
| `title` | string | 是 | 会话标题 |
| `created_at` | string | 是 | 创建时间（ISO 8601） |
| `query_count` | integer | 是 | 当前问答次数（初始为0） |

## 5. GET /sessions — 会话列表

> 无请求体，返回 sessions 数组。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `sessions` | array | 是 | 会话列表 |
| `sessions[].id` | string | 是 | 会话ID |
| `sessions[].title` | string | 是 | 会话标题 |
| `sessions[].created_at` | string | 是 | 创建时间 |
| `sessions[].updated_at` | string | 是 | 最后更新时间 |
| `sessions[].query_count` | integer | 是 | 问答次数 |
| `total` | integer | 是 | 总会话数 |

## 6. DELETE /sessions/<id> — 删除会话

> 路径参数 session_id，无请求体。

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 会话ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `deleted` | boolean | 是 | 是否删除成功 |
| `session_id` | string | 是 | 被删除的会话ID |

**副作用**：级联删除该会话下的所有问答记录。

## 7. GET /sessions/<id>/records — 问答记录

> 路径参数 session_id，返回 records 数组。

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 会话ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 会话ID |
| `records` | array | 是 | 问答记录列表 |
| `records[].id` | string | 是 | 记录ID |
| `records[].query` | string | 是 | 用户提问 |
| `records[].answer` | string | 是 | 系统回答 |
| `records[].timestamp` | string | 是 | 提问时间 |
| `records[].llm_used` | boolean | 是 | 是否使用真实LLM |
| `records[].answer_source` | string | 是 | 答案来源 |

## 8. POST /reports — 研报上传解析

**请求体**（multipart/form-data）：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `file` | file | **是** | PDF/HTML格式，≤10MB | 研报文件 |
| `session_id` | string | **是** | UUID | 目标会话ID |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `report_id` | string | 是 | 研报唯一标识 |
| `title` | string | 是 | 研报标题 |
| `rating` | string | 是 | 评级 |
| `target_price` | string | 是 | 目标价 |
| `core_views` | array | 是 | 核心观点列表 |
| `parsed_at` | string | 是 | 解析时间 |
| `status` | string | 是 | parsing/completed/failed |

## 9. GET /reports — 研报列表查询

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `keyword` | string | 否 | 模糊搜索关键词（标题/评级/目标价/观点） |
| `page` | integer | 否 | 页码，默认1 |
| `page_size` | integer | 否 | 每页条数，默认20 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `reports` | array | 是 | 研报列表 |
| `reports[].id` | string | 是 | 研报ID |
| `reports[].title` | string | 是 | 研报标题 |
| `reports[].rating` | string | 是 | 评级 |
| `reports[].target_price` | string | 是 | 目标价 |
| `reports[].parsed_at` | string | 是 | 解析时间 |
| `total` | integer | 是 | 总条数 |
| `page` | integer | 是 | 当前页码 |
| `page_size` | integer | 是 | 每页条数 |

## 10. GET /reports/<id> — 研报详情查看

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 研报ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `report_id` | string | 是 | 研报ID |
| `title` | string | 是 | 研报标题 |
| `rating` | string | 是 | 评级 |
| `target_price` | string | 是 | 目标价 |
| `core_views` | array | 是 | 核心观点列表 |
| `full_content` | string | 是 | 完整解析内容 |
| `parsed_at` | string | 是 | 解析时间 |
| `session_id` | string | 是 | 所属会话ID |

## 11. DELETE /reports/<id> — 研报删除

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 研报ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `deleted` | boolean | 是 | 是否删除成功 |
| `report_id` | string | 是 | 被删除的研报ID |

## 12. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 非空 | 400 | `INVALID_SESSION` |
| POST /sessions | `title` | ≤ 100 字符 | 400 | `INVALID_TITLE` |
| DELETE /sessions/<id> | `id` | 有效UUID格式 | 404 | `NOT_FOUND` |
| GET /sessions/<id>/records | `id` | 会话存在 | 404 | `NOT_FOUND` |
| POST /reports | `file` | PDF/HTML格式 | 400 | `INVALID_FILE_FORMAT` |
| POST /reports | `file` | ≤ 10MB | 400 | `FILE_TOO_LARGE` |
| POST /reports | `session_id` | 非空 | 400 | `INVALID_SESSION` |
| GET /reports | `keyword` | ≤ 100 字符 | 400 | `INVALID_QUERY` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 首版填写 |
