# 09 — API 接口规格

---

| 项 | 值 |
|---|---|
| 模块编号 | SR (StockResearch) |
| 模块名称 | 投研分析平台 |
| 文档版本 | v1.0 |
| 阶段 | Design（How — 契约真源） |
| Base URL | `/api/v1` |

---

> **本文是全部 API 端点的契约真源**。`05` 定义"用户要什么"，**09（本文）定义"后端必须返回什么"**，`13` 的测试断言以本文为准。

## 1. 端点总览

| # | 端点 | 方法 | 功能 | 成功码 | 蓝图 |
|---|------|------|------|--------|------|
| 1 | `/api/v1/stock/search?keyword=` | GET | 股票搜索 | 200 | stock_bp |
| 2 | `/api/v1/stock/quote?secid=` | GET | 实时行情 | 200 | stock_bp |
| 3 | `/api/v1/stock/profile?secid=` | GET | 公司概况 | 200 | stock_bp |
| 4 | `/api/v1/stock/change-analysis?secid=` | GET | 涨跌原因分析 | 200 | stock_bp |
| 5 | `/api/v1/finance/quarterly?secid=&years=3` | GET | 季度财务数据 | 200 | finance_bp |
| 6 | `/api/v1/ai/chat` | POST | 发送消息 | 200 | ai_bp |
| 7 | `/api/v1/ai/sessions?stock_code=` | GET | 列出会话 | 200 | ai_bp |
| 8 | `/api/v1/ai/sessions/:id` | GET | 获取会话历史 | 200 | ai_bp |
| 9 | `/api/v1/ai/sessions/:id` | DELETE | 删除会话 | 200 | ai_bp |

## 2. 统一响应规范

### 成功响应

```json
{ "success": true, /* 业务字段 */ }
```

### 错误响应

```json
{ "success": false, "error": { "code": "PARAM_ERROR", "message": "缺少必填参数 secid" } }
```

### 错误码清单

| HTTP | error.code | 触发条件 |
|------|-----------|----------|
| 400 | `PARAM_ERROR` | 缺少必填参数或参数格式不正确 |
| 404 | `NOT_FOUND` | 股票代码不存在或会话 ID 无效 |
| 500 | `UPSTREAM_ERROR` | 东方财富 API 调用失败 |
| 500 | `LLM_ERROR` | DashScope API 调用失败 |
| 504 | `TIMEOUT` | 外部 API 调用超时 |

## 3. GET /stock/search — 股票搜索

**请求参数**：

| 参数 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `keyword` | string | **是** | 1–50 字符 | 搜索关键词（名称或代码） |

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | true |
| `results` | array | 搜索结果列表 |
| `results[].name` | string | 股票名称 |
| `results[].code` | string | 股票代码 |
| `results[].secid` | string | 东方财富证券 ID（如 1.600519） |
| `results[].market` | string | 市场（沪/深） |

## 4. GET /stock/quote — 实时行情

**请求参数**：

| 参数 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `secid` | string | **是** | 格式 `{market}.{code}` | 东方财富证券 ID |

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | true |
| `name` | string | 股票名称 |
| `code` | string | 股票代码 |
| `price` | float | 最新价格 |
| `changePercent` | float | 涨跌幅（%） |
| `changeAmount` | float | 涨跌额 |
| `volume` | integer | 成交量（手） |
| `turnover` | float | 成交额（元） |
| `marketCap` | float | 总市值（元） |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `open` | float | 开盘价 |
| `prevClose` | float | 昨收价 |

## 5. GET /stock/profile — 公司概况

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `secid` | string | **是** | 东方财富证券 ID |

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | true |
| `name` | string | 公司名称 |
| `industry` | string | 行业分类 |
| `listDate` | string | 上市日期 |
| `registeredCapital` | string | 注册资本 |
| `employees` | integer | 员工人数 |
| `mainBusiness` | string | 主营业务 |
| `introduction` | string | 公司简介 |

## 6. GET /stock/change-analysis — 涨跌原因分析

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `secid` | string | **是** | 东方财富证券 ID |

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | true |
| `analysis` | string | AI 生成的涨跌分析文本 |
| `news` | array | 相关新闻列表 |
| `news[].title` | string | 新闻标题 |
| `news[].source` | string | 新闻来源 |
| `news[].time` | string | 发布时间 |
| `news[].url` | string | 新闻链接 |

## 7. GET /finance/quarterly — 季度财务数据

**请求参数**：

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `secid` | string | **是** | — | 东方财富证券 ID |
| `years` | integer | 否 | 3 | 查询年数（1~10） |

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | true |
| `quarters` | array | 季度数据列表（按时间倒序） |
| `quarters[].period` | string | 季度标识（如 2024Q3） |
| `quarters[].revenue` | float | 营业收入（元） |
| `quarters[].profit` | float | 净利润（元） |
| `quarters[].revenueYoy` | float\|null | 营收同比增长率（%） |
| `quarters[].profitYoy` | float\|null | 利润同比增长率（%） |
| `quarters[].revenueQoq` | float\|null | 营收环比增长率（%） |
| `quarters[].profitQoq` | float\|null | 利润环比增长率（%） |

## 8. POST /ai/chat — AI 对话

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `message` | string | **是** | 1–2000 字符 | 用户消息内容 |
| `session_id` | string | 否 | — | 会话 ID，空则新建 |
| `stock_code` | string | **是** | — | 关联股票代码 |

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | true |
| `reply` | string | AI 回复内容 |
| `session_id` | string | 会话 ID |
| `model` | string | 使用的模型名称（qwen-plus） |

## 9. GET /ai/sessions — 会话列表

**请求参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `stock_code` | string | 否 | 按股票筛选会话 |

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | true |
| `sessions` | array | 会话列表 |
| `sessions[].id` | string | 会话 ID |
| `sessions[].title` | string | 会话标题（首条消息摘要） |
| `sessions[].stock_code` | string | 关联股票代码 |
| `sessions[].created_at` | string (ISO-8601) | 创建时间 |
| `sessions[].message_count` | integer | 消息数量 |

## 10. GET /ai/sessions/:id — 会话历史

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 会话 ID |

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | true |
| `session` | object | 会话信息 |
| `messages` | array | 消息列表 |
| `messages[].role` | string | 角色（user / assistant） |
| `messages[].content` | string | 消息内容 |
| `messages[].timestamp` | string (ISO-8601) | 发送时间 |

## 11. DELETE /ai/sessions/:id — 删除会话

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `id` | string | 会话 ID |

**成功响应**（200）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | true |
| `message` | string | "会话已删除" |

**副作用**：级联删除会话关联的所有消息记录。

## 12. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| GET /stock/search | `keyword` | 非空，1~50 字符 | 400 | `PARAM_ERROR` |
| GET /stock/quote | `secid` | 非空，格式 `{d}.{d+}` | 400 | `PARAM_ERROR` |
| GET /stock/profile | `secid` | 非空 | 400 | `PARAM_ERROR` |
| GET /stock/change-analysis | `secid` | 非空 | 400 | `PARAM_ERROR` |
| GET /finance/quarterly | `secid` | 非空 | 400 | `PARAM_ERROR` |
| GET /finance/quarterly | `years` | 1~10 正整数 | 400 | `PARAM_ERROR` |
| POST /ai/chat | `message` | 非空，1~2000 字符 | 400 | `PARAM_ERROR` |
| POST /ai/chat | `stock_code` | 非空 | 400 | `PARAM_ERROR` |
| DELETE /ai/sessions/:id | `id` | 会话必须存在 | 404 | `NOT_FOUND` |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-04-14 | 首版发布 |
