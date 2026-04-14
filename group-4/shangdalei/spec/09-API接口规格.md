# 09 — API接口规格

---

| 项 | 值 |
|---|---|
| 模块编号 | M4-QA |
| 模块名称 | 研报问答助手 |
| 文档版本 | v0.1 |
| 阶段 | Design（How） |
| 上游 | `06` FSD · `08` 架构 |
| 下游 | → `10` Data · `13` 测试 |

---

## 1. 会话管理 API

### POST /api/sessions - 创建会话

**请求体**
```json
{
  "name": "可选-会话名称"
}
```

**响应**
```json
{
  "session_id": "uuid-string",
  "name": "会话名称",
  "created_at": "2026-04-14T10:00:00Z"
}
```

**错误响应**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "会话数量已达上限"
}
```

### GET /api/sessions - 获取会话列表

**响应**
```json
{
  "sessions": [
    {
      "session_id": "uuid-string",
      "name": "会话名称",
      "created_at": "2026-04-14T10:00:00Z",
      "updated_at": "2026-04-14T11:00:00Z"
    }
  ],
  "total": 1
}
```

### DELETE /api/sessions/{session_id} - 删除会话

**响应**
```json
{
  "success": true
}
```

## 2. 问答 API

### POST /api/qa/ask - 提交问答

**请求体**
```json
{
  "session_id": "uuid-string",
  "query": "用户问题（1-500字符）"
}
```

**响应**
```json
{
  "answer": "AI生成的回答",
  "answer_source": "openai|demo|fallback",
  "references": [
    {
      "source": "研报名称",
      "snippet": "引用片段"
    }
  ],
  "created_at": "2026-04-14T10:00:00Z"
}
```

**错误响应**
```json
{
  "error": "VALIDATION_ERROR",
  "message": "query长度必须在1-500字符之间"
}
```

### GET /api/qa/history - 获取问答历史

**参数**
- `session_id` (required): 会话ID
- `page` (optional): 页码，默认1
- `page_size` (optional): 每页数量，默认20

**响应**
```json
{
  "records": [
    {
      "query": "用户问题",
      "answer": "AI回答",
      "answer_source": "openai",
      "created_at": "2026-04-14T10:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

## 3. 健康检查 API

### GET /api/health - 健康检查

**响应**
```json
{
  "status": "healthy|degraded|unhealthy",
  "dependencies": {
    "mysql": "up",
    "redis": "up",
    "milvus": "up",
    "llm": "up|down"
  }
}
```

## 4. 通用错误码

| 错误码 | 说明 |
|--------|------|
| VALIDATION_ERROR | 输入验证失败 |
| NOT_FOUND | 资源不存在 |
| INTERNAL_ERROR | 内部错误 |
| SERVICE_UNAVAILABLE | 服务不可用 |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 首版填写 |
