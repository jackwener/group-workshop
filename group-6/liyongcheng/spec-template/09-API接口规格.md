# 09 — API 接口规格（引导版模板）

---

| 项 | 值 |
|---|---|
| 模块编号 | M1-RS |
| 模块名称 | 研报阅读系统 |
| 文档版本 | v0.1 |
| 阶段 | Design（How — 契约真源） |
| Base URL | `/api/v1/research` |

---

> **本文是全部 API 端点的契约真源**。`05` 定义"用户要什么"，**09（本文）定义"后端必须返回什么"**，`13` 的测试断言以本文为准。

## 1. 端点总览

| # | 端点 | 方法 | 功能 | 成功码 |
|---|------|------|------|--------|
| 1 | `/api/v1/research/reports` | GET | 研报列表 | 200 |
| 2 | `/api/v1/research/reports` | POST | 上传并解析研报 | 201 |
| 3 | `/api/v1/research/reports/<id>` | GET | 研报详情 | 200 |
| 4 | `/api/v1/research/reports/<id>` | DELETE | 删除研报 | 200 |
| 5 | `/api/v1/research/reports/compare` | POST | 研报对比 | 200 |
| 6 | `/api/v1/research/stock/price` | GET | 股票价格查询 | 200 |

## 2. 统一响应规范

### 成功响应

```json
{ 
  "traceId": "tr_abc123...", 
  "success": true,
  "data": { /* 业务数据 */ }
}
```

### 错误响应

```json
{ 
  "success": false,
  "error": { 
    "code": "EMPTY_FILE", 
    "message": "请上传研报文件", 
    "details": {}, 
    "traceId": "tr_..." 
  } 
}
```

### 错误码清单

| HTTP | error.code | 触发条件 | details |
|------|-----------|----------|---------|
| 400 | `EMPTY_FILE` | 上传文件为空 | `{}` |
| 400 | `INVALID_FILE_TYPE` | 文件类型不支持 | `{"supported_types": ["pdf"]}` |
| 400 | `FILE_TOO_LARGE` | 文件超过大小限制 | `{"max_size_mb": 20}` |
| 400 | `INVALID_STOCK_CODE` | 股票代码格式错误 | `{}` |
| 404 | `REPORT_NOT_FOUND` | 研报不存在 | `{}` |
| 404 | `STOCK_NOT_FOUND` | 股票代码不存在 | `{}` |
| 500 | `PARSE_FAILED` | 研报解析失败 | `{"reason": "..."}` |
| 503 | `STOCK_SERVICE_UNAVAILABLE` | 股价服务不可用 | `{}` |

## 3. POST /reports — 上传并解析研报

**请求体**（multipart/form-data）：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `file` | file | **是** | PDF 格式，≤ 20MB | 研报文件 |
| `auto_extract` | boolean | 否 | 默认 true | 是否自动解析核心数据 |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `success` | boolean | 是 | true |
| `data` | object | 是 | 研报数据 |
| `data.id` | string | 是 | 研报唯一 ID（UUID） |
| `data.title` | string | 是 | 研报标题 |
| `data.subject_name` | string | 是 | 研究对象主体名称（上市公司） |
| `data.subject_code` | string | 是 | 研究对象股票代码 |
| `data.author` | string | 是 | 研报作者（券商公司） |
| `data.rating` | string | 是 | 评级（如：买入、增持、中性、减持） |
| `data.trend` | string | 是 | 看涨看跌方向（bullish/bearish/neutral） |
| `data.target_price` | number/null | 是 | 目标价（元） |
| `data.summary` | string | 是 | 核心观点摘要 |
| `data.created_at` | string | 是 | 创建时间（ISO 8601） |
| `data.parse_status` | string | 是 | 解析状态（success/partial/failed） |

**响应示例**：

```json
{
  "traceId": "tr_abc123",
  "success": true,
  "data": {
    "id": "rpt_001",
    "title": "贵州茅台2024年度投资价值分析报告",
    "subject_name": "贵州茅台",
    "subject_code": "600519.SH",
    "author": "中信证券",
    "rating": "买入",
    "trend": "bullish",
    "target_price": 2200.00,
    "summary": "公司业绩稳定增长，品牌护城河深厚，维持买入评级...",
    "created_at": "2026-04-14T10:30:00Z",
    "parse_status": "success"
  }
}
```

## 4. GET /reports — 研报列表

**请求参数**（Query String）：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | integer | 否 | 1 | 页码 |
| `page_size` | integer | 否 | 20 | 每页数量（1-100） |
| `subject_code` | string | 否 | - | 按股票代码筛选 |
| `author` | string | 否 | - | 按券商筛选 |
| `keyword` | string | 否 | - | 关键词搜索（标题） |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `success` | boolean | 是 | true |
| `data` | object | 是 | 分页数据 |
| `data.total` | integer | 是 | 总记录数 |
| `data.page` | integer | 是 | 当前页码 |
| `data.page_size` | integer | 是 | 每页数量 |
| `data.items` | array | 是 | 研报列表 |
| `data.items[].id` | string | 是 | 研报 ID |
| `data.items[].title` | string | 是 | 研报标题 |
| `data.items[].subject_name` | string | 是 | 研究对象名称 |
| `data.items[].subject_code` | string | 是 | 研究对象代码 |
| `data.items[].author` | string | 是 | 券商名称 |
| `data.items[].rating` | string | 是 | 评级 |
| `data.items[].created_at` | string | 是 | 创建时间 |

**响应示例**：

```json
{
  "traceId": "tr_abc124",
  "success": true,
  "data": {
    "total": 45,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": "rpt_001",
        "title": "贵州茅台2024年度投资价值分析报告",
        "subject_name": "贵州茅台",
        "subject_code": "600519.SH",
        "author": "中信证券",
        "rating": "买入",
        "created_at": "2026-04-14T10:30:00Z"
      }
    ]
  }
}
```

## 5. GET /reports/<id> — 研报详情

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 研报 ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `success` | boolean | 是 | true |
| `data` | object | 是 | 研报完整数据（同 POST /reports 响应结构） |

## 6. DELETE /reports/<id> — 删除研报

**路径参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 研报 ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `success` | boolean | 是 | true |
| `data` | object | 是 | 删除确认 |
| `data.deleted_id` | string | 是 | 已删除的研报 ID |
| `data.message` | string | 是 | 删除成功消息 |

**响应示例**：

```json
{
  "traceId": "tr_abc125",
  "success": true,
  "data": {
    "deleted_id": "rpt_001",
    "message": "研报已删除"
  }
}
```

## 7. POST /reports/compare — 研报对比

**请求体**（application/json）：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `subject_code` | string | **是** | 6 位股票代码 | 研究对象股票代码 |
| `report_ids` | array | 否 | 2-10 个 ID | 指定对比的研报 ID 列表（为空则对比该股票全部研报） |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `success` | boolean | 是 | true |
| `data` | object | 是 | 对比数据 |
| `data.subject_name` | string | 是 | 研究对象名称 |
| `data.subject_code` | string | 是 | 研究对象代码 |
| `data.report_count` | integer | 是 | 对比研报数量 |
| `data.comparison` | array | 是 | 对比列表 |
| `data.comparison[].report_id` | string | 是 | 研报 ID |
| `data.comparison[].author` | string | 是 | 券商名称 |
| `data.comparison[].rating` | string | 是 | 评级 |
| `data.comparison[].trend` | string | 是 | 看涨看跌方向 |
| `data.comparison[].target_price` | number/null | 是 | 目标价 |
| `data.comparison[].summary` | string | 是 | 核心观点摘要 |
| `data.comparison[].publish_date` | string | 是 | 发布日期 |

**响应示例**：

```json
{
  "traceId": "tr_abc126",
  "success": true,
  "data": {
    "subject_name": "贵州茅台",
    "subject_code": "600519.SH",
    "report_count": 3,
    "comparison": [
      {
        "report_id": "rpt_001",
        "author": "中信证券",
        "rating": "买入",
        "trend": "bullish",
        "target_price": 2200.00,
        "summary": "业绩稳定增长，品牌护城河深厚",
        "publish_date": "2026-04-10"
      },
      {
        "report_id": "rpt_002",
        "author": "华泰证券",
        "rating": "增持",
        "trend": "bullish",
        "target_price": 2000.00,
        "summary": "渠道改革成效显现，维持增持",
        "publish_date": "2026-04-08"
      },
      {
        "report_id": "rpt_003",
        "author": "招商证券",
        "rating": "中性",
        "trend": "neutral",
        "target_price": 1800.00,
        "summary": "估值偏高，建议观望",
        "publish_date": "2026-04-05"
      }
    ]
  }
}
```

## 8. GET /stock/price — 股票价格查询

**请求参数**（Query String）：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `code` | string | **是** | 6 位股票代码 | 股票代码（如：600519） |
| `market` | string | 否 | SH/SZ | 市场（上海/深圳），可自动推断 |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `success` | boolean | 是 | true |
| `data` | object | 是 | 股价数据 |
| `data.code` | string | 是 | 股票代码 |
| `data.name` | string | 是 | 股票名称 |
| `data.price` | number | 是 | 当前价格（元） |
| `data.change` | number | 是 | 涨跌幅（元） |
| `data.change_percent` | number | 是 | 涨跌幅（%） |
| `data.open` | number | 是 | 开盘价 |
| `data.high` | number | 是 | 最高价 |
| `data.low` | number | 是 | 最低价 |
| `data.volume` | number | 是 | 成交量（手） |
| `data.amount` | number | 是 | 成交额（万元） |
| `data.timestamp` | string | 是 | 数据时间（ISO 8601） |
| `data.source` | string | 是 | 数据来源 |

**响应示例**：

```json
{
  "traceId": "tr_abc127",
  "success": true,
  "data": {
    "code": "600519",
    "name": "贵州茅台",
    "price": 1856.50,
    "change": 28.30,
    "change_percent": 1.55,
    "open": 1830.00,
    "high": 1865.00,
    "low": 1825.00,
    "volume": 32560,
    "amount": 60345.89,
    "timestamp": "2026-04-14T15:00:00Z",
    "source": "sina"
  }
}
```

## 9. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /reports | `file` | 非空 | 400 | `EMPTY_FILE` |
| POST /reports | `file` | PDF 格式 | 400 | `INVALID_FILE_TYPE` |
| POST /reports | `file` | ≤ 20MB | 400 | `FILE_TOO_LARGE` |
| GET /reports | `page` | ≥ 1 | 400 | `INVALID_PARAM` |
| GET /reports | `page_size` | 1-100 | 400 | `INVALID_PARAM` |
| GET /reports/<id> | `id` | 存在 | 404 | `REPORT_NOT_FOUND` |
| DELETE /reports/<id> | `id` | 存在 | 404 | `REPORT_NOT_FOUND` |
| POST /reports/compare | `subject_code` | 6 位数字 | 400 | `INVALID_STOCK_CODE` |
| POST /reports/compare | `report_ids` | 2-10 个 | 400 | `INVALID_PARAM` |
| GET /stock/price | `code` | 6 位数字 | 400 | `INVALID_STOCK_CODE` |
| GET /stock/price | `code` | 存在 | 404 | `STOCK_NOT_FOUND` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 首版填写 |
