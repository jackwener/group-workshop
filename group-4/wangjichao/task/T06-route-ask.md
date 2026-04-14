# T06 — 路由层：POST /ask 问答提交端点

| 项 | 值 |
|---|---|
| 任务ID | T06 |
| 所属 WBS | W1 路由实现 |
| 里程碑 | **S2** 问答核心 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T02（Storage 记录写入）, T04（路由公共模块）, T08（Agent 降级编排） |
| 并行关系 | 与 T05, T07 并行 |
| 产出文件 | `backend/agent_bp.py`（ask 端点） |

## 1. 任务目标

实现 `POST /ask` 问答提交端点，接收用户提问，调用 Agent 三级降级编排，将结果存入 Storage，返回标准化响应。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `09` API | §4 | POST /ask 请求体：query(1-500, 必填) + session_id(UUID, 必填) |
| `09` API | §4 | 响应：answer, llm_used, model, response_time_ms, answer_source |
| `09` API | §11 | 校验：EMPTY_QUERY / INVALID_QUERY / INVALID_SESSION_ID / SESSION_NOT_FOUND |
| `07` 非功能 | §1.1 | P95 延迟 < 3000ms |
| `07` 非功能 | §1.2 | 三级降级不可跳级，静默执行 |

## 3. 请求/响应规格

**请求体**：
| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `query` | string | 是 | 1–500 字符 |
| `session_id` | string | 是 | UUID 格式 |

**成功响应**（200）：
| 字段 | 类型 | 说明 |
|------|------|------|
| `traceId` | string | 链路追踪 ID |
| `answer` | string | 答案文本 |
| `llm_used` | boolean | 是否使用真实 LLM |
| `model` | string\|null | 模型标识 |
| `response_time_ms` | integer | 响应耗时 |
| `answer_source` | string | copaw / bailian / demo |

## 4. 处理流程

```
1. 参数校验 → query 非空(EMPTY_QUERY) → query ≤500(INVALID_QUERY) → session_id 非空(INVALID_SESSION_ID)
2. 检查 session 存在 → SESSION_NOT_FOUND
3. 计时开始
4. 调用 Agent.ask(query, session_id) → 三级降级
5. 计时结束 → response_time_ms
6. Storage.add_record(session_id, query, answer, ...) → 落库
7. 返回 _ok({answer, llm_used, model, response_time_ms, answer_source})
```

## 5. 验收标准（AC）

| # | 验收条件 | 关联 TC |
|---|---------|---------|
| AC-01 | POST /ask + 有效 query → 200，含 answer/llm_used/answer_source/traceId | TC-M01-001 |
| AC-02 | 空 query → 400, EMPTY_QUERY | TC-M01-002 |
| AC-03 | query > 500 字符 → 400, INVALID_QUERY | TC-M01-003 |
| AC-04 | 无 API Key → answer_source='demo', llm_used=false | TC-M01-004 |
| AC-05 | response_time_ms 字段类型为 integer |  |
| AC-06 | 问答记录已写入 Storage（可通过 GET /records 验证） |  |
