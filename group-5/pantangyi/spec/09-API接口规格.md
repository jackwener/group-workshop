# API 接口说明

## 文档信息

| 字段 | 内容 |
|------|------|
| 模块编号 | M1-QA |
| 模块名称 | 投研问答助手 |
| 文档版本 | v0.1 |
| 阶段 | API Spec |
| 上游 | 03 立项提案、04 PRD、05 US |
| 下游 | 06 FSD、10 Data、13 测试、14 追溯 |

---

## 1. 接口概览

### 1.1 接口清单

| 接口编号 | 接口名称 | 请求方法 | 路径 | 对应US | 说明 |
|----------|----------|----------|------|--------|------|
| API-001 | 创建会话 | POST | /api/v1/sessions | US-001 | 新建问答会话 |
| API-002 | 获取会话列表 | GET | /api/v1/sessions | US-001 | 获取历史会话列表 |
| API-003 | 删除会话 | DELETE | /api/v1/sessions/{id} | US-001 | 删除指定会话 |
| API-004 | 获取会话详情 | GET | /api/v1/sessions/{id} | US-003 | 获取会话完整信息 |
| API-005 | 研报分析 | POST | /api/v1/analysis/report | US-002 | 上传研报并分析 |
| API-006 | 股票查询 | POST | /api/v1/analysis/stock | US-002 | 查询股票分析报告 |
| API-007 | 发送消息 | POST | /api/v1/sessions/{id}/messages | US-002 | 在会话中发送消息 |
| API-008 | 下载报告 | GET | /api/v1/reports/{id}/download | US-004 | 下载分析报告 |
| API-009 | 健康检查 | GET | /api/v1/health | US-004 | 服务健康状态检查 |

### 1.2 接口架构

```
┌─────────────────────────────────────────────────────────┐
│                      API 网关层                          │
├─────────────────────────────────────────────────────────┤
│  会话管理API  │  问答分析API  │  历史记录API  │  工具API  │
├───────────────┼───────────────┼───────────────┼───────────┤
│ POST /session │ POST /report  │ GET /sessions │ GET /health│
│ GET /sessions │ POST /stock   │ GET /session  │ GET /report│
│ DELETE /session│              │               │           │
│ POST /message │               │               │           │
└───────────────┴───────────────┴───────────────┴───────────┘
```

---

## 2. 通用规范

### 2.1 基础信息

- **Base URL**: `http://localhost:5000/api/v1`
- **协议**: HTTP/HTTPS
- **数据格式**: JSON
- **字符编码**: UTF-8

### 2.2 请求规范

| 项目 | 说明 |
|------|------|
| Content-Type | `application/json`（除文件上传外） |
| Authorization | Bearer Token（如需认证） |
| 时间戳 | ISO 8601 格式 |

### 2.3 响应规范

**成功响应格式：**
```json
{
  "code": 200,
  "message": "success",
  "data": { }
}
```

**错误响应格式：**
```json
{
  "code": 400,
  "message": "错误描述",
  "error": "详细错误信息"
}
```

### 2.4 状态码

| HTTP状态码 | 说明 |
|------------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 503 | 服务降级中 |

### 2.5 通用错误码

| 错误码 | 说明 |
|--------|------|
| 400001 | 参数缺失 |
| 400002 | 参数格式错误 |
| 400003 | 文件格式不支持 |
| 404001 | 会话不存在 |
| 404002 | 报告不存在 |
| 500001 | LLM服务不可用 |
| 500002 | 数据源超时 |
| 503001 | 服务降级中 |

---

## 3. 会话管理接口

### 3.1 创建会话 (API-001)

**接口信息**
- **请求方法**: POST
- **请求路径**: `/sessions`
- **对应US**: US-001
- **对应AC**: AC-001-01

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | 否 | 会话标题，默认"新会话" |
| type | string | 否 | 会话类型：report/stock，默认通用 |

**请求示例**
```json
{
  "title": "某公司股票分析",
  "type": "stock"
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | string | 会话唯一标识 |
| title | string | 会话标题 |
| type | string | 会话类型 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

**响应示例**
```json
{
  "code": 201,
  "message": "success",
  "data": {
    "id": "sess_202504140001",
    "title": "某公司股票分析",
    "type": "stock",
    "created_at": "2025-04-14T10:30:00Z",
    "updated_at": "2025-04-14T10:30:00Z"
  }
}
```

---

### 3.2 获取会话列表 (API-002)

**接口信息**
- **请求方法**: GET
- **请求路径**: `/sessions`
- **对应US**: US-001
- **对应AC**: AC-001-03

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| limit | integer | 否 | 返回数量，默认5，最大20 |
| offset | integer | 否 | 偏移量，默认0 |

**请求示例**
```
GET /api/v1/sessions?limit=5&offset=0
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| total | integer | 总会话数 |
| items | array | 会话列表 |
| items[].id | string | 会话ID |
| items[].title | string | 会话标题 |
| items[].type | string | 会话类型 |
| items[].created_at | string | 创建时间 |
| items[].updated_at | string | 更新时间 |

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 15,
    "items": [
      {
        "id": "sess_202504140001",
        "title": "某公司股票分析",
        "type": "stock",
        "created_at": "2025-04-14T10:30:00Z",
        "updated_at": "2025-04-14T10:35:00Z"
      }
    ]
  }
}
```

---

### 3.3 删除会话 (API-003)

**接口信息**
- **请求方法**: DELETE
- **请求路径**: `/sessions/{id}`
- **对应US**: US-001
- **对应AC**: AC-001-02

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 会话ID |

**请求示例**
```
DELETE /api/v1/sessions/sess_202504140001
```

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": null
}
```

---

### 3.4 获取会话详情 (API-004)

**接口信息**
- **请求方法**: GET
- **请求路径**: `/sessions/{id}`
- **对应US**: US-003
- **对应AC**: AC-003-01

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 会话ID |

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| id | string | 会话ID |
| title | string | 会话标题 |
| type | string | 会话类型 |
| messages | array | 消息列表 |
| messages[].role | string | 角色：user/assistant |
| messages[].content | string | 消息内容 |
| messages[].timestamp | string | 时间戳 |
| created_at | string | 创建时间 |

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": "sess_202504140001",
    "title": "某公司股票分析",
    "type": "stock",
    "messages": [
      {
        "role": "user",
        "content": "分析股票000001",
        "timestamp": "2025-04-14T10:30:00Z"
      },
      {
        "role": "assistant",
        "content": "分析报告内容...",
        "timestamp": "2025-04-14T10:31:00Z"
      }
    ],
    "created_at": "2025-04-14T10:30:00Z"
  }
}
```

---

## 4. 问答分析接口

### 4.1 研报分析 (API-005)

**接口信息**
- **请求方法**: POST
- **请求路径**: `/analysis/report`
- **对应US**: US-002
- **对应AC**: AC-002-01
- **Content-Type**: `multipart/form-data`

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | string | 是 | 会话ID |
| files | file/array | 是 | 研报文件，支持PDF/Word |
| extract_keywords | boolean | 否 | 是否提取关键词，默认true |
| compare_reports | boolean | 否 | 是否比对多份研报，默认false |

**请求示例**
```
POST /api/v1/analysis/report
Content-Type: multipart/form-data

session_id: sess_202504140001
files: [file1.pdf, file2.pdf]
extract_keywords: true
compare_reports: true
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| analysis_id | string | 分析任务ID |
| status | string | 状态：processing/completed/failed |
| reports | array | 研报分析结果 |
| reports[].filename | string | 文件名 |
| reports[].title | string | 研报标题 |
| reports[].summary | string | 摘要 |
| reports[].key_points | array | 核心观点 |
| reports[].risk_warnings | array | 风险提示 |
| comparison | object | 比对结果（多份研报时） |
| comparison.similarity | number | 相似度 |
| comparison.consistency | string | 观点一致性 |

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "analysis_id": "ana_202504140001",
    "status": "completed",
    "reports": [
      {
        "filename": "report1.pdf",
        "title": "某公司2025年Q1研报",
        "summary": "公司业绩稳步增长...",
        "key_points": ["营收增长15%", "净利润提升"],
        "risk_warnings": ["市场竞争加剧"]
      }
    ],
    "comparison": {
      "similarity": 0.75,
      "consistency": "观点基本一致"
    }
  }
}
```

---

### 4.2 股票查询 (API-006)

**接口信息**
- **请求方法**: POST
- **请求路径**: `/analysis/stock`
- **对应US**: US-002
- **对应AC**: AC-002-02

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | string | 是 | 会话ID |
| stock_code | string | 是 | 股票代码 |
| stock_name | string | 否 | 股票名称 |
| analysis_type | string | 否 | 分析类型：full/financial/news，默认full |

**请求示例**
```json
{
  "session_id": "sess_202504140001",
  "stock_code": "000001",
  "stock_name": "平安银行",
  "analysis_type": "full"
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| analysis_id | string | 分析任务ID |
| stock_code | string | 股票代码 |
| stock_name | string | 股票名称 |
| financial_indicators | object | 财务指标 |
| financial_indicators.revenue | number | 营收 |
| financial_indicators.profit | number | 净利润 |
| financial_indicators.roe | number | 净资产收益率 |
| report_summary | string | 研报摘要 |
| comprehensive_score | number | 综合评分 |
| risk_level | string | 风险等级：low/medium/high |
| analysis_time | string | 分析时间 |
| accuracy | number | 准确率 |

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "analysis_id": "ana_202504140002",
    "stock_code": "000001",
    "stock_name": "平安银行",
    "financial_indicators": {
      "revenue": 1500000000,
      "profit": 450000000,
      "roe": 12.5
    },
    "report_summary": "多家机构给予买入评级...",
    "comprehensive_score": 85,
    "risk_level": "medium",
    "analysis_time": "2025-04-14T10:35:00Z",
    "accuracy": 0.92
  }
}
```

---

### 4.3 发送消息 (API-007)

**接口信息**
- **请求方法**: POST
- **请求路径**: `/sessions/{id}/messages`
- **对应US**: US-002

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 会话ID |

**请求参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| content | string | 是 | 消息内容 |
| type | string | 否 | 消息类型：text/file，默认text |

**请求示例**
```json
{
  "content": "请分析这只股票的投资价值",
  "type": "text"
}
```

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| message_id | string | 消息ID |
| role | string | 角色：assistant |
| content | string | 回复内容 |
| timestamp | string | 时间戳 |

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "message_id": "msg_202504140001",
    "role": "assistant",
    "content": "根据分析，该股票...",
    "timestamp": "2025-04-14T10:36:00Z"
  }
}
```

---

## 5. 工具接口

### 5.1 下载报告 (API-008)

**接口信息**
- **请求方法**: GET
- **请求路径**: `/reports/{id}/download`
- **对应US**: US-004
- **对应AC**: AC-004-01

**路径参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | string | 是 | 报告ID |

**查询参数**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| format | string | 否 | 格式：pdf/json，默认pdf |

**请求示例**
```
GET /api/v1/reports/ana_202504140001/download?format=pdf
```

**响应**
- Content-Type: `application/pdf` 或 `application/json`
- Content-Disposition: `attachment; filename="report.pdf"`

---

### 5.2 健康检查 (API-009)

**接口信息**
- **请求方法**: GET
- **请求路径**: `/health`
- **对应US**: US-004

**响应参数**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| status | string | 状态：healthy/degraded/unhealthy |
| version | string | API版本 |
| services | object | 各服务状态 |
| services.llm | string | LLM服务状态 |
| services.database | string | 数据库状态 |
| timestamp | string | 检查时间 |

**响应示例**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "healthy",
    "version": "v1.0.0",
    "services": {
      "llm": "available",
      "database": "connected"
    },
    "timestamp": "2025-04-14T10:40:00Z"
  }
}
```

**降级状态示例**
```json
{
  "code": 503,
  "message": "service degraded",
  "data": {
    "status": "degraded",
    "services": {
      "llm": "fallback_to_bailian",
      "database": "connected"
    },
    "fallback_level": 2
  }
}
```

---

## 6. 数据模型

### 6.1 Session (会话)

```json
{
  "id": "string",
  "title": "string",
  "type": "report|stock|general",
  "status": "active|archived|deleted",
  "messages": [Message],
  "created_at": "string",
  "updated_at": "string"
}
```

### 6.2 Message (消息)

```json
{
  "id": "string",
  "session_id": "string",
  "role": "user|assistant|system",
  "content": "string",
  "type": "text|file|analysis",
  "attachments": [Attachment],
  "timestamp": "string"
}
```

### 6.3 AnalysisResult (分析结果)

```json
{
  "id": "string",
  "session_id": "string",
  "type": "report|stock",
  "status": "processing|completed|failed",
  "input_data": {},
  "output_data": {},
  "accuracy": "number",
  "created_at": "string",
  "completed_at": "string"
}
```

### 6.4 Report (研报分析)

```json
{
  "filename": "string",
  "title": "string",
  "summary": "string",
  "key_points": ["string"],
  "risk_warnings": ["string"],
  "industry": "string",
  "rating": "string",
  "target_price": "number"
}
```

### 6.5 StockAnalysis (股票分析)

```json
{
  "stock_code": "string",
  "stock_name": "string",
  "financial_indicators": {
    "revenue": "number",
    "profit": "number",
    "roe": "number",
    "pe": "number",
    "pb": "number"
  },
  "report_summary": "string",
  "comprehensive_score": "number",
  "risk_level": "low|medium|high",
  "recommendation": "buy|hold|sell"
}
```

---

## 7. 错误处理

### 7.1 降级策略

当外部LLM不可用时，系统自动降级：

| 降级级别 | LLM服务 | 响应头 |
|----------|---------|--------|
| 0 | CoPaw | X-LLM-Status: primary |
| 1 | 百炼 | X-LLM-Status: fallback-1 |
| 2 | Demo模式 | X-LLM-Status: demo |

### 7.2 超时处理

| 接口 | 超时时间 | 重试策略 |
|------|----------|----------|
| 研报分析 | 180s | 重试1次 |
| 股票查询 | 60s | 重试2次 |
| 其他接口 | 30s | 不重试 |

---

## 8. 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 【日期】 | 首版填写，包含9个核心接口定义 |
