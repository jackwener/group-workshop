# 09 — API 接口规格

---

| 项 | 值 |
|---|---|
| 模块编号 | M8-RA |
| 模块名称 | 研报分析助手 |
| 文档版本 | v0.1 |
| 阶段 | Design（How — 契约真源） |
| Base URL | `/api/v1/report` |

---

> **本文是全部 API 端点的契约真源**。`05` 定义"用户要什么"，**09（本文）定义"后端必须返回什么"**，`13` 的测试断言以本文为准。

## 1. 端点总览

| # | 端点 | 方法 | 功能 | 成功码 |
|---|------|------|------|--------|
| 1 | `/api/v1/report/capabilities` | GET | 能力探测 | 200 |
| 2 | `/api/v1/report/upload` | POST | 研报上传 | 201 |
| 3 | `/api/v1/report/ask` | POST | 问答提交 | 200 |
| 4 | `/api/v1/report/compare` | POST | 研报对比 | 200 |
| 5 | `/api/v1/report/sessions` | GET | 会话列表 | 200 |
| 6 | `/api/v1/report/sessions` | POST | 新建会话 | 201 |
| 7 | `/api/v1/report/sessions/<id>` | DELETE | 删除会话 | 200 |
| 8 | `/api/v1/report/sessions/<id>/records` | GET | 问答记录 | 200 |

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
| 400 | `INVALID_FILE_TYPE` | 文件格式非PDF/HTML/Word/PPT且非URL | `{"allowed":["pdf","html","docx","pptx","url"]}` |
| 400 | `FILE_TOO_LARGE` | 文件大小 >50MB | `{"max_size":"50MB"}` |
| 500 | `PARSE_ERROR` | 研报解析失败 | `{}` |
| 500 | `UPSTREAM_ERROR` | Agent 编排内部异常 | `{}` |

## 2.5 GET /capabilities — 能力探测

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `bailian_configured` | boolean | 是 | 百炼是否已配置 |
| `model` | string\|null | 是 | 当前模型标识 |
| `supported_formats` | array | 是 | 支持的文件格式列表 |

## 3. POST /upload — 研报上传

**请求体**（multipart/form-data）：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `file` | File | **否** | PDF/HTML/Word/PPT, ≤50MB | 研报文件（与file和url二选一） |
| `url` | string | **否** | 合法URL | 研报链接（与file和url二选一） |
| `session_id` | string | **是** | UUID | 目标会话 ID |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `report_id` | string | 是 | 研报唯一标识 |
| `title` | string | 是 | 提取的标题 |
| `rating` | string | 是 | 评级 |
| `target_price` | string | 是 | 目标价 |
| `core_view` | string | 是 | 核心观点 |
| `created_at` | string | 是 | ISO-8601 时间 |

## 4. POST /ask — 问答提交

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `query` | string | **是** | 1–500 字符 | 用户提问原文 |
| `report_id` | string | **是** | UUID | 目标研报 ID |
| `session_id` | string | **是** | UUID | 目标会话 ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `answer` | string | 是 | 答案文本 |
| `llm_used` | boolean | 是 | 是否使用真实 LLM |
| `model` | string\|null | 是 | 模型标识 |
| `response_time_ms` | integer | 是 | 响应耗时（毫秒） |
| `answer_source` | `string` | 是 | bailian / demo |

## 5. POST /compare — 研报对比

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `report_ids` | array | **是** | 2-3个UUID | 要比对的研报ID列表 |
| `session_id` | string | **是** | UUID | 目标会话 ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `comparison` | object | 是 | 对比结果 |
| `comparison.reports` | array | 是 | 研报基本信息列表 |
| `comparison.ratings` | array | 是 | 评级对比 |
| `comparison.target_prices` | array | 是 | 目标价对比 |
| `comparison.core_views` | array | 是 | 核心观点对比 |

## 6. POST /sessions — 新建会话

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
| `created_at` | string | 是 | ISO-8601 时间 |
| `query_count` | integer | 是 | 累计问答次数（初始0） |

## 7. GET /sessions — 会话列表

> 无请求体，返回 sessions 数组。每个 session 包含 id、title、created_at、query_count。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `sessions` | array | 是 | 会话列表 |

## 8. DELETE /sessions/<id> — 删除会话

> 路径参数 session_id，无请求体，返回确认消息。注意级联删除关联记录。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `message` | string | 是 | "会话已删除" |

## 9. GET /sessions/<id>/records — 问答记录

> 路径参数 session_id，返回 records 数组。每条记录含 query、answer、timestamp 等。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `records` | array | 是 | 问答记录列表 |

## 10. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `report_id` | 非空 | 400 | `INVALID_QUERY` |
| POST /upload | `file` | PDF/HTML/Word/PPT格式 | 400 | `INVALID_FILE_TYPE` |
| POST /upload | `file` | ≤ 50MB | 400 | `FILE_TOO_LARGE` |
| POST /compare | `report_ids` | 2-3个元素 | 400 | `INVALID_QUERY` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 首版填写 |
