# 09 — API 接口规格（引导版模板）

---

| 项 | 值 |
|---|---|
| 模块编号 | M4-RA |
| 模块名称 | 研报聚合分析助手 |
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
| 5 | `/api/v1/agent/sessions/<id>` | PUT | 更新会话 | 200 |
| 6 | `/api/v1/agent/sessions/<id>` | DELETE | 删除会话 | 200 |
| 7 | `/api/v1/agent/sessions/<id>/records` | GET | 问答记录 | 200 |
| 8 | `/api/v1/agent/reports` | POST | 研报上传 | 201 |
| 9 | `/api/v1/agent/reports` | GET | 研报列表 | 200 |
| 10 | `/api/v1/agent/reports/<id>` | GET | 研报详情 | 200 |
| 11 | `/api/v1/agent/reports/<id>` | DELETE | 删除研报 | 200 |
| 12 | `/api/v1/agent/reports/<id>/mark` | PUT | 标记研报 | 200 |
| 13 | `/api/v1/agent/reports/<id>/parse` | POST | 研报解析 | 200 |
| 14 | `/api/v1/agent/reports/compare` | POST | 研报对比 | 200 |

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
| 400 | `INVALID_SESSION_ID` | session_id 为空或格式错误 | `{}` |
| 400 | `INVALID_FILE_TYPE` | 研报文件非 PDF/HTML 格式 | `{"supported_types":["pdf","html"]}` |
| 400 | `FILE_TOO_LARGE` | 研报文件超过 50MB | `{"max_size":"50MB"}` |
| 404 | `SESSION_NOT_FOUND` | 会话不存在 | `{"session_id":"xxx"}` |
| 404 | `REPORT_NOT_FOUND` | 研报不存在 | `{"report_id":"xxx"}` |
| 500 | `PARSE_ERROR` | 研报解析失败 | `{"report_id":"xxx"}` |
| 503 | `LLM_UNAVAILABLE` | LLM 服务不可用 | `{"fallback":"demo"}` |

## 3. GET /capabilities — 能力探测

> 返回当前系统配置的 LLM 能力状态，前端用于渲染能力芯片。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `copaw_configured` | boolean | 是 | CoPaw 是否已配置 |
| `bailian_configured` | boolean | 是 | 百炼是否已配置 |
| `bailian_model` | string\|null | 是 | 百炼模型名称，未配置时为 null |

**响应示例**：
```json
{
  "traceId": "tr_abc123",
  "copaw_configured": true,
  "bailian_configured": true,
  "bailian_model": "qwen-plus"
}
```

## 4. ★ 示例：POST /ask — 问答提交

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

## 5. POST /sessions — 新建会话（请填写）

**请求体**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `title` | string | 否 | "新会话" | 会话标题 |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 会话唯一标识 UUID |
| `title` | string | 是 | 会话标题 |
| `created_at` | string | 是 | 创建时间 ISO8601 格式 |
| `query_count` | integer | 是 | 当前会话问答次数，初始为 0 |

## 6. GET /sessions — 会话列表

> 无请求体，返回 sessions 数组。每个 session 至少包含 id、title、created_at、query_count。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `sessions` | array | 是 | 会话列表，按时间倒序排列 |
| `sessions[].session_id` | string | 是 | 会话唯一标识 |
| `sessions[].title` | string | 是 | 会话标题 |
| `sessions[].created_at` | string | 是 | 创建时间 ISO8601 格式 |
| `sessions[].query_count` | integer | 是 | 该会话问答次数 |
| `total` | integer | 是 | 总会话数 |

**响应示例**：
```json
{
  "traceId": "tr_abc123",
  "sessions": [
    {
      "session_id": "sess_001",
      "title": "新会话",
      "created_at": "2026-04-14T10:30:00Z",
      "query_count": 5
    }
  ],
  "total": 1
}
```

## 7. DELETE /sessions/<id> — 删除会话

> 路径参数 session_id，无请求体，返回确认消息。注意级联删除关联记录。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `deleted` | boolean | 是 | 是否删除成功 |
| `session_id` | string | 是 | 被删除的会话 ID |

**副作用**：级联删除该会话下的所有问答记录（qa_records）

**响应示例**：
```json
{
  "traceId": "tr_abc123",
  "deleted": true,
  "session_id": "sess_001"
}
```

## 8. PUT /sessions/<id> — 更新会话

> 路径参数 session_id，更新会话标题。对齐 `06` §3.1 会话重命名。

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `title` | string | **是** | ≤ 100 字符 | 新标题 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 会话 ID |
| `title` | string | 是 | 更新后的标题 |
| `updated_at` | string | 是 | 更新时间 ISO8601 格式 |

**响应示例**：
```json
{
  "traceId": "tr_abc123",
  "session_id": "sess_001",
  "title": "贵州茅台研报分析",
  "updated_at": "2026-04-14T11:00:00Z"
}
```

## 9. GET /sessions/<id>/records — 问答记录

> 路径参数 session_id，返回 records 数组。每条记录含 query、answer、timestamp 等。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 会话 ID |
| `records` | array | 是 | 问答记录列表，按时间正序排列 |
| `records[].record_id` | string | 是 | 记录唯一标识 |
| `records[].query` | string | 是 | 用户提问 |
| `records[].answer` | string | 是 | 系统回答 |
| `records[].answer_source` | string | 是 | 答案来源：copaw / bailian / demo |
| `records[].timestamp` | string | 是 | 回答时间 ISO8601 格式 |
| `records[].citations` | array | 否 | 原文引用列表，仅研报问答时有 |
| `records[].citations[].text` | string | 否 | 引用原文片段 |
| `records[].citations[].source_report_id` | string | 否 | 来源研报 ID |

**响应示例**：
```json
{
  "traceId": "tr_abc123",
  "session_id": "sess_001",
  "records": [
    {
      "record_id": "rec_001",
      "query": "这家公司的评级是什么？",
      "answer": "根据研报分析，该公司评级为买入...",
      "answer_source": "copaw",
      "timestamp": "2026-04-14T10:35:00Z",
      "citations": [
        {
          "text": "维持买入评级，目标价 50 元",
          "source_report_id": "rep_001"
        }
      ]
    }
  ]
}
```

## 10. 研报相关端点详细规格

### 10.1 POST /reports — 研报上传

**请求体**（multipart/form-data）：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `file` | file | **是** | PDF/HTML 格式，≤ 50MB | 研报文件 |
| `title` | string | 否 | ≤ 200 字符 | 研报标题，默认为文件名 |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `report_id` | string | 是 | 研报唯一标识 UUID |
| `title` | string | 是 | 研报标题 |
| `file_type` | string | 是 | 文件类型：pdf / html |
| `file_size` | integer | 是 | 文件大小（字节） |
| `uploaded_at` | string | 是 | 上传时间 ISO8601 格式 |
| `status` | string | 是 | 解析状态：pending / parsing / completed / failed |

**响应示例**：
```json
{
  "traceId": "tr_abc123",
  "report_id": "rep_001",
  "title": "某公司2026年Q1研报",
  "file_type": "pdf",
  "file_size": 2048576,
  "uploaded_at": "2026-04-14T10:30:00Z",
  "status": "pending"
}
```

---

### 10.2 GET /reports — 研报列表

> 无请求体，支持查询参数：`?keyword=xxx&rating=买入&page=1&size=20`

**查询参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `keyword` | string | 否 | 按标题关键词搜索 |
| `rating` | string | 否 | 按评级筛选：买入/增持/中性/减持 |
| `page` | integer | 否 | 页码，默认 1 |
| `size` | integer | 否 | 每页数量，默认 20，最大 100 |
| `sort_by` | string | 否 | 排序字段：uploaded_at / title，默认 uploaded_at |
| `sort_order` | string | 否 | 排序方向：asc / desc，默认 desc |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `reports` | array | 是 | 研报列表 |
| `reports[].report_id` | string | 是 | 研报唯一标识 |
| `reports[].title` | string | 是 | 研报标题 |
| `reports[].file_type` | string | 是 | 文件类型 |
| `reports[].rating` | string | 否 | 评级，解析完成后有值 |
| `reports[].target_price` | string | 否 | 目标价，解析完成后有值 |
| `reports[].status` | string | 是 | 解析状态 |
| `reports[].uploaded_at` | string | 是 | 上传时间 |
| `reports[].is_marked` | boolean | 是 | 是否被标记为重点 |
| `total` | integer | 是 | 总研报数 |
| `page` | integer | 是 | 当前页码 |
| `size` | integer | 是 | 每页数量 |

**响应示例**：
```json
{
  "traceId": "tr_abc123",
  "reports": [
    {
      "report_id": "rep_001",
      "title": "某公司2026年Q1研报",
      "file_type": "pdf",
      "rating": "买入",
      "target_price": "50元",
      "status": "completed",
      "uploaded_at": "2026-04-14T10:30:00Z",
      "is_marked": true
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20
}
```

---

### 10.3 GET /reports/<id> — 研报详情

> 路径参数 report_id，返回研报完整信息及解析结果

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `report_id` | string | 是 | 研报唯一标识 |
| `title` | string | 是 | 研报标题 |
| `file_type` | string | 是 | 文件类型 |
| `file_size` | integer | 是 | 文件大小（字节） |
| `status` | string | 是 | 解析状态 |
| `uploaded_at` | string | 是 | 上传时间 |
| `is_marked` | boolean | 是 | 是否被标记为重点 |
| `parsed_result` | object | 否 | 解析结果，status=completed 时必有 |
| `parsed_result.title` | string | 否 | 提取的标题 |
| `parsed_result.rating` | string | 否 | 评级 |
| `parsed_result.target_price` | string | 否 | 目标价 |
| `parsed_result.core_views` | array | 否 | 核心观点列表 |
| `parsed_result.data_forecast` | object | 否 | 数据预测 |
| `file_url` | string | 否 | 原文文件下载链接 |

**响应示例**：
```json
{
  "traceId": "tr_abc123",
  "report_id": "rep_001",
  "title": "某公司2026年Q1研报",
  "file_type": "pdf",
  "file_size": 2048576,
  "status": "completed",
  "uploaded_at": "2026-04-14T10:30:00Z",
  "is_marked": true,
  "parsed_result": {
    "title": "某公司2026年第一季度业绩点评",
    "rating": "买入",
    "target_price": "50元",
    "core_views": [
      "业绩超预期，营收同比增长30%",
      "毛利率提升至35%，盈利能力增强"
    ],
    "data_forecast": {
      "revenue_growth": "30%",
      "pe_ratio": "15倍"
    }
  },
  "file_url": "/api/v1/agent/reports/rep_001/download"
}
```

---

### 10.4 DELETE /reports/<id> — 删除研报

> 路径参数 report_id，删除研报及其解析结果

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `deleted` | boolean | 是 | 是否删除成功 |
| `report_id` | string | 是 | 被删除的研报 ID |

**副作用**：级联删除该研报的所有解析结果和相关问答引用

**响应示例**：
```json
{
  "traceId": "tr_abc123",
  "deleted": true,
  "report_id": "rep_001"
}
```

---

### 10.5 PUT /reports/<id>/mark — 标记研报

> 路径参数 report_id，切换研报标记状态。对齐 `06` §3.2 研报标记。

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `mark_status` | string | **是** | 枚举：none / important / read | 标记状态 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `report_id` | string | 是 | 研报 ID |
| `mark_status` | string | 是 | 更新后的标记状态 |
| `is_marked` | boolean | 是 | 是否为重点（mark_status=important 时 true） |

**响应示例**：
```json
{
  "traceId": "tr_abc123",
  "report_id": "rep_001",
  "mark_status": "important",
  "is_marked": true
}
```

### 10.6 POST /reports/<id>/parse — 研报解析

> 路径参数 report_id，触发研报解析流程（通常在上传后自动触发，也可手动调用）

**请求体**：无

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `report_id` | string | 是 | 研报 ID |
| `status` | string | 是 | 解析状态：parsing / completed / failed |
| `parsed_result` | object | 否 | 解析结果，status=completed 时必有 |
| `parsed_result.title` | string | 否 | 提取的标题 |
| `parsed_result.rating` | string | 否 | 评级：买入/增持/中性/减持 |
| `parsed_result.target_price` | string | 否 | 目标价 |
| `parsed_result.core_views` | array | 否 | 核心观点列表 |
| `parsed_result.data_forecast` | object | 否 | 数据预测（营收增速、PE等） |
| `parse_time_ms` | integer | 否 | 解析耗时（毫秒） |

**响应示例**（解析完成）：
```json
{
  "traceId": "tr_abc123",
  "report_id": "rep_001",
  "status": "completed",
  "parsed_result": {
    "title": "某公司2026年第一季度业绩点评",
    "rating": "买入",
    "target_price": "50元",
    "core_views": [
      "业绩超预期，营收同比增长30%",
      "毛利率提升至35%，盈利能力增强",
      "市场份额持续扩大"
    ],
    "data_forecast": {
      "revenue_growth": "30%",
      "gross_margin": "35%",
      "pe_ratio": "15倍",
      "pb_ratio": "2.5倍"
    }
  },
  "parse_time_ms": 3500
}
```

---

### 10.7 POST /reports/compare — 研报对比

> 对比多份研报的关键指标，生成对比表

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `report_ids` | array | **是** | 2-10 个 UUID | 要比对的研报 ID 列表 |
| `compare_fields` | array | 否 | 默认全部 | 对比字段：rating / target_price / core_views / data_forecast |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `compare_id` | string | 是 | 对比任务 ID |
| `report_count` | integer | 是 | 参与对比的研报数量 |
| `compare_time_ms` | integer | 是 | 对比耗时（毫秒） |
| `comparison` | object | 是 | 对比结果 |
| `comparison.headers` | array | 是 | 表头：字段名 + 各研报标题 |
| `comparison.rows` | array | 是 | 对比数据行 |
| `comparison.rows[].field` | string | 是 | 字段名 |
| `comparison.rows[].values` | array | 是 | 各研报该字段的值 |
| `export_url` | string | 否 | Excel 导出链接 |

**响应示例**：
```json
{
  "traceId": "tr_abc123",
  "compare_id": "cmp_001",
  "report_count": 3,
  "compare_time_ms": 2500,
  "comparison": {
    "headers": ["字段", "研报A", "研报B", "研报C"],
    "rows": [
      {
        "field": "评级",
        "values": ["买入", "增持", "买入"]
      },
      {
        "field": "目标价",
        "values": ["50元", "48元", "52元"]
      },
      {
        "field": "核心观点",
        "values": [
          "业绩超预期，营收增长30%",
          "毛利率提升，盈利能力增强",
          "市场份额扩大，竞争优势明显"
        ]
      }
    ]
  },
  "export_url": "/api/v1/agent/reports/compare/cmp_001/export"
}
```

---

## 11. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 非空/格式为 UUID | 400 | `INVALID_SESSION_ID` |
| POST /ask | `session_id` | 会话存在 | 404 | `SESSION_NOT_FOUND` |
| POST /sessions | `title` | ≤ 100 字符 | 400 | `INVALID_QUERY` |
| PUT /sessions/<id> | `title` | 非空，≤ 100 字符 | 400 | `INVALID_QUERY` |
| PUT /sessions/<id> | `id` (路径参数) | 会话存在 | 404 | `SESSION_NOT_FOUND` |
| GET /sessions/<id>/records | `id` (路径参数) | 会话存在 | 404 | `SESSION_NOT_FOUND` |
| DELETE /sessions/<id> | `id` (路径参数) | 会话存在 | 404 | `SESSION_NOT_FOUND` |
| POST /reports | `file` | 非空 | 400 | `EMPTY_QUERY` |
| POST /reports | `file` | 格式为 PDF/HTML | 400 | `INVALID_FILE_TYPE` |
| POST /reports | `file` | 大小 ≤ 50MB | 400 | `FILE_TOO_LARGE` |
| GET /reports/<id> | `id` (路径参数) | 研报存在 | 404 | `REPORT_NOT_FOUND` |
| DELETE /reports/<id> | `id` (路径参数) | 研报存在 | 404 | `REPORT_NOT_FOUND` |
| POST /reports/<id>/parse | `id` (路径参数) | 研报存在 | 404 | `REPORT_NOT_FOUND` |
| POST /reports/compare | `report_ids` | 非空，2-10 个 ID | 400 | `INVALID_REPORT_SELECTION` |
| PUT /reports/<id>/mark | `mark_status` | 枚举：none/important/read | 400 | `INVALID_QUERY` |
| PUT /reports/<id>/mark | `id` (路径参数) | 研报存在 | 404 | `REPORT_NOT_FOUND` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 首版填写，基于 03/04/05 文档完成 API 接口规格 |
