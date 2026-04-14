# T05 — 路由层：会话管理端点

| 项 | 值 |
|---|---|
| 任务ID | T05 |
| 所属 WBS | W1 路由实现 |
| 里程碑 | **S1** 会话管理 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T02（Storage 会话 CRUD）, T04（路由公共模块） |
| 并行关系 | 与 T06, T07 并行（不同端点） |
| 产出文件 | `backend/agent_bp.py`（会话相关端点） |

## 1. 任务目标

实现 5 个会话管理相关 API 端点，包含完整的参数校验和错误处理。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `09` API | §5 | POST /sessions — 新建会话，title 可选，默认 "新会话" |
| `09` API | §6 | GET /sessions — 会话列表，按时间倒序 |
| `09` API | §7 | DELETE /sessions/<id> — 删除会话 + 级联删除 |
| `09` API | §8 | PUT /sessions/<id> — 更新会话标题，title ≤ 100 字符 |
| `09` API | §9 | GET /sessions/<id>/records — 问答记录列表 |
| `09` API | §11 | 参数校验规则：session_id 存在性、title 长度 |

## 3. 端点清单

| # | 端点 | 方法 | 成功码 | 请求体/参数 | 错误码 |
|---|------|------|--------|------------|--------|
| 1 | `/sessions` | POST | 201 | `{title?}` | INVALID_QUERY(title>100) |
| 2 | `/sessions` | GET | 200 | 无 | — |
| 3 | `/sessions/<id>` | PUT | 200 | `{title}` | INVALID_QUERY, SESSION_NOT_FOUND |
| 4 | `/sessions/<id>` | DELETE | 200 | 无 | SESSION_NOT_FOUND |
| 5 | `/sessions/<id>/records` | GET | 200 | 无 | SESSION_NOT_FOUND |

## 4. 关键参数校验（对齐 `09` §11）

| 端点 | 字段 | 规则 | 失败码 |
|------|------|------|--------|
| POST /sessions | title | ≤ 100 字符 | INVALID_QUERY |
| PUT /sessions/<id> | title | 非空，≤ 100 字符 | INVALID_QUERY |
| PUT /sessions/<id> | id | 会话存在 | SESSION_NOT_FOUND |
| DELETE /sessions/<id> | id | 会话存在 | SESSION_NOT_FOUND |
| GET /sessions/<id>/records | id | 会话存在 | SESSION_NOT_FOUND |

## 5. 验收标准（AC）

| # | 验收条件 | 关联 TC |
|---|---------|---------|
| AC-01 | POST /sessions → 201，含 session_id/title/created_at/query_count=0 | TC-M01-021 |
| AC-02 | GET /sessions → 200，sessions 数组按时间倒序 | TC-M01-020 |
| AC-03 | DELETE /sessions/<id> → 200，级联删除 qa_records | TC-M01-022 |
| AC-04 | DELETE 不存在的 session → 404, SESSION_NOT_FOUND | TC-M01-023 |
| AC-05 | PUT /sessions/<id> → 200，title 更新 + updated_at 刷新 | TC-M01-024 |
| AC-06 | PUT title 超 100 字符 → 400, INVALID_QUERY | TC-M01-025 |
| AC-07 | GET /sessions/<id>/records → 200，含 records 数组 | TC-M01-030 |
