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

| # | 端点 | 方法 | 功能 | 成功码 | 关联 US |
|---|------|------|------|--------|---------|
| 1 | `/api/v1/agent/capabilities` | GET | 能力探测 | 200 | US-007 |
| 2 | `/api/v1/agent/sessions` | GET | 会话列表 | 200 | US-001 |
| 3 | `/api/v1/agent/sessions` | POST | 新建会话 | 201 | US-001 |
| 4 | `/api/v1/agent/sessions/<id>` | DELETE | 删除会话（级联） | 200 | US-001 |
| 5 | `/api/v1/agent/sessions/<id>/records` | GET | 问答记录 | 200 | US-004 |
| 6 | `/api/v1/agent/sessions/<id>/reports` | POST | 上传研报 | 201 | US-002 |
| 7 | `/api/v1/agent/sessions/<id>/reports` | GET | 研报列表 | 200 | US-002 |
| 8 | `/api/v1/agent/reports/<id>` | GET | 研报详情（含状态） | 200 | US-002 |
| 9 | `/api/v1/agent/reports/<id>/summary` | GET | 结构化摘要 | 200 | US-003 |
| 10 | `/api/v1/agent/reports/<id>/reparse` | POST | 失败重试 | 200 | US-002 |
| 11 | `/api/v1/agent/ask` | POST | 问答提交 | 200 | US-004 |
| 12 | `/api/v1/agent/sessions/<id>/compare` | POST | 多研报对比 | 200 | US-005 |
| 13 | `/api/v1/agent/stocks/search` | GET | 股票搜索 | 200 | US-006 |
| 14 | `/api/v1/agent/stocks` | GET | 股票详情 | 200 | US-006 |

## 2. 统一响应规范

### 成功响应

```json
{ "traceId": "tr_abc123...", /* 业务字段 */ }
```

### 错误响应

```json
{
  "error": {
    "code": "EMPTY_QUERY",
    "message": "请输入问题",
    "details": {},
    "traceId": "tr_..."
  }
}
```

### 错误码清单

| HTTP | error.code | 触发条件 | details |
|------|-----------|----------|---------|
| 400 | `EMPTY_QUERY` | query 为空/null | `{}` |
| 400 | `INVALID_QUERY` | query > 500 或缺少 session_id | `{"max_length":500}` |
| 400 | `INVALID_PAYLOAD` | 请求体不合法（JSON/字段缺失） | `{"field":"..."}` |
| 404 | `SESSION_NOT_FOUND` | session_id 不存在 | `{"session_id":"..."}` |
| 404 | `REPORT_NOT_FOUND` | report_id 不存在 | `{"report_id":"..."}` |
| 404 | `STOCK_NOT_FOUND` | 股票代码/名称无匹配 | `{"query":"..."}` |
| 415 | `UNSUPPORTED_FORMAT` | 非 WORD/PPT/PDF/HTML | `{"allowed":["doc","docx","ppt","pptx","pdf","html","htm"]}` |
| 422 | `REPORT_PARSE_FAILED` | 文件解析失败 | `{"reason":"..."}` |
| 500 | `UPSTREAM_ERROR` | Agent 或外部服务异常 | `{}`（不得回传调用栈） |

## 3. POST /ask — 问答提交（US-004）

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `query` | string | 是 | 1–500 字符 | 用户提问原文 |
| `session_id` | string | 是 | UUID | 目标会话 ID |
| `report_ids` | string[] | 否 | 默认为当前会话全部 ready 研报 | 限定问答范围 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `answer` | string | 是 | 答案文本 |
| `llm_used` | boolean | 是 | 是否使用真实 LLM |
| `model` | string\|null | 是 | 模型标识 |
| `response_time_ms` | integer | 是 | 响应耗时 |
| `answer_source` | string | 是 | `copaw \| bailian \| demo` |
| `citations` | object[] | 是 | 原文引用数组（可空，空代表未找到依据） |

**citations 元素**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `report_id` | string | 引用来源研报 |
| `snippet` | string | 原文片段（≤ 300 字符） |
| `location` | string\|null | 页码 / 段落标识 |

**示例响应**：

```json
{
  "traceId": "tr_9a3f...",
  "answer": "该研报给予"买入"评级，目标价 42.5 元，主要依据 Q3 营收同比 +28%。",
  "llm_used": true,
  "model": "qwen-plus",
  "response_time_ms": 1820,
  "answer_source": "bailian",
  "citations": [
    { "report_id": "rpt_001", "snippet": "维持"买入"评级，目标价 42.5 元…", "location": "p.3" }
  ]
}
```

## 4. POST /sessions — 新建会话（US-001）

**请求体**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `title` | string | 否 | `"新会话"` | ≤ 23 字符 |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 |
| `session_id` | string | 是 | UUID |
| `title` | string | 是 | 会话标题 |
| `created_at` | string | 是 | ISO-8601 |
| `updated_at` | string | 是 | ISO-8601 |
| `query_count` | integer | 是 | 初始 0 |

## 5. GET /sessions — 会话列表（US-001）

**成功响应**（200）：

```json
{
  "traceId": "tr_...",
  "sessions": [
    { "session_id": "...", "title": "宁德时代专题", "created_at": "...", "updated_at": "...", "query_count": 4 }
  ]
}
```

## 6. DELETE /sessions/<id> — 删除会话（US-001）

**副作用**：级联删除该 session 的全部 `qa_records`、`reports`、`compare_results`、`files/` 下对应研报文件。

**成功响应**（200）：

```json
{ "traceId": "tr_...", "deleted": true, "session_id": "...", "cascade": { "records": 12, "reports": 3 } }
```

## 7. GET /sessions/<id>/records — 问答记录（US-004）

**成功响应**（200）：

```json
{
  "traceId": "tr_...",
  "records": [
    {
      "id": "rec_1712...",
      "session_id": "...",
      "query": "目标价是多少？",
      "answer": "42.5 元",
      "llm_used": true,
      "model": "qwen-plus",
      "response_time_ms": 1820,
      "answer_source": "bailian",
      "citations": [{ "report_id": "rpt_001", "snippet": "...", "location": "p.3" }],
      "timestamp": "2026-04-14T07:30:22Z"
    }
  ]
}
```

## 8. POST /sessions/<id>/reports — 上传研报（US-002）

**请求**：`multipart/form-data`

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `file` | file | 是 | `.doc/.docx/.ppt/.pptx/.pdf/.html/.htm`，≤ 30 MB |

**成功响应**（201）：

```json
{
  "traceId": "tr_...",
  "report_id": "rpt_...",
  "session_id": "...",
  "filename": "宁德时代-2026Q3点评.pdf",
  "format": "pdf",
  "size_bytes": 1840213,
  "status": "parsing",
  "uploaded_at": "..."
}
```

## 9. GET /sessions/<id>/reports — 研报列表（US-002）

**成功响应**（200）：

```json
{
  "traceId": "tr_...",
  "reports": [
    { "report_id": "rpt_001", "filename": "...", "format": "pdf", "status": "ready", "uploaded_at": "..." }
  ]
}
```

## 10. GET /reports/<id> — 研报详情（US-002）

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `report_id` | string | — |
| `status` | string | `uploading \| parsing \| ready \| failed` |
| `failure_reason` | string\|null | 失败原因（脱敏） |
| `ocr_used` | boolean | 是否启用 OCR |
| `stocks` | string[] | 研报中识别出的股票代码 |

## 11. GET /reports/<id>/summary — 结构化摘要（US-003）

**成功响应**（200）：

```json
{
  "traceId": "tr_...",
  "report_id": "rpt_001",
  "rating": "买入",
  "target_price": "42.5 元",
  "core_views": [
    "Q3 营收同比 +28%",
    "产能利用率提升至 92%"
  ],
  "citations": {
    "rating":       { "snippet": "…", "location": "p.1" },
    "target_price": { "snippet": "…", "location": "p.3" },
    "core_views":   [{ "snippet": "…", "location": "p.5" }]
  }
}
```

无法识别时：`rating = null`，`target_price = null`，`core_views = []`（AC-003-01）。

## 12. POST /reports/<id>/reparse — 失败重试（US-002）

**请求体**：空 或 `{ "force_ocr": true }`。

**成功响应**（200）：`{ "traceId": "...", "report_id": "...", "status": "parsing" }`。

## 13. POST /sessions/<id>/compare — 多研报对比（US-005）

**请求体**：

```json
{ "report_ids": ["rpt_001", "rpt_002", "rpt_003"] }
```

**约束**：`report_ids.length ≥ 2`。

**成功响应**（200）：

```json
{
  "traceId": "tr_...",
  "compare_id": "cmp_...",
  "elapsed_ms": 58230,
  "reports": [
    { "report_id": "rpt_001", "filename": "中信.pdf" },
    { "report_id": "rpt_002", "filename": "国君.pdf" }
  ],
  "fields": [
    {
      "field": "rating",
      "values": [
        { "report_id": "rpt_001", "value": "买入" },
        { "report_id": "rpt_002", "value": null }
      ]
    },
    {
      "field": "target_price",
      "values": [
        { "report_id": "rpt_001", "value": "42.5 元" },
        { "report_id": "rpt_002", "value": "40.0 元" }
      ]
    },
    {
      "field": "core_views",
      "values": [
        { "report_id": "rpt_001", "value": ["..."] },
        { "report_id": "rpt_002", "value": ["..."] }
      ]
    }
  ]
}
```

## 14. GET /stocks/search — 股票搜索（US-006）

**Query**：`q` 必填（代码/名称/关键词，长度 1–20）。

**成功响应**（200）：

```json
{
  "traceId": "tr_...",
  "candidates": [
    { "code": "300750.SZ", "name": "宁德时代", "exchange": "SZ", "industry": "电池" }
  ]
}
```

## 15. GET /stocks — 股票详情（US-006）

**Query**：`code` 必填（如 `300750.SZ`）。

**成功响应**（200）：

```json
{
  "traceId": "tr_...",
  "code": "300750.SZ",
  "name": "宁德时代",
  "latest_price": 220.13,
  "change_pct": 1.85,
  "pe_ttm": 22.4,
  "market_cap": "9680 亿元",
  "updated_at": "..."
}
```

## 16. GET /capabilities — 能力探测（US-007）

**成功响应**（200）：

```json
{
  "traceId": "tr_...",
  "caps": {
    "copaw_configured": true,
    "bailian_configured": true,
    "bailian_model": "qwen-plus",
    "parsers": { "word": true, "ppt": true, "pdf": true, "html": true, "ocr": true },
    "stock_service": true
  }
}
```

## 17. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 非空且存在 | 400 / 404 | `INVALID_QUERY` / `SESSION_NOT_FOUND` |
| POST /sessions | `title` | ≤ 23 字符 | 400 | `INVALID_PAYLOAD` |
| DELETE /sessions/<id> | `id` | 存在 | 404 | `SESSION_NOT_FOUND` |
| POST /sessions/<id>/reports | `file` | 格式/大小 | 415 / 400 | `UNSUPPORTED_FORMAT` / `INVALID_PAYLOAD` |
| POST /sessions/<id>/compare | `report_ids` | 长度 ≥ 2，均存在 | 400 / 404 | `INVALID_PAYLOAD` / `REPORT_NOT_FOUND` |
| GET /stocks/search | `q` | 1–20 字符 | 400 | `INVALID_PAYLOAD` |
| GET /stocks | `code` | 非空 | 400 | `INVALID_PAYLOAD` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 首版填写，覆盖 US-001~007 |
