# T02 — Storage 层：会话与问答记录 CRUD

| 项 | 值 |
|---|---|
| 任务ID | T02 |
| 所属 WBS | W2 存储层 |
| 里程碑 | **S1** 会话管理 + **S2** 问答核心 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T01（项目脚手架） |
| 并行关系 | 与 T03 并行；完成后解锁 T05, T06 |
| 产出文件 | `backend/storage.py`（会话+问答部分） |

## 1. 任务目标

实现 Storage 类中会话管理（4个方法）和问答记录管理（3个方法）的完整 CRUD 逻辑，使用 JSON 文件作为持久化存储。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `10` 数据模型 | §2 | JSON 文件存储，UTF-8，RMW 模式 |
| `10` 数据模型 | §3 | Session 实体：session_id, title(≤100), created_at, updated_at, query_count |
| `10` 数据模型 | §4 | QARecord 实体：id, session_id(FK), query(1-500), answer, llm_used, model, response_time_ms, answer_source, citations, timestamp |
| `10` 数据模型 | §7.1 | 会话管理 4 个方法签名 |
| `10` 数据模型 | §7.2 | 问答记录管理 3 个方法签名 |
| `10` 数据模型 | §8 | 首次问答自动命名逻辑 |

## 3. 需要实现的方法

### 3.1 会话管理（对齐 `10` §7.1）

| 方法 | 签名 | 关键行为 | 关联 TC |
|------|------|----------|---------|
| `create_session` | `(session_id, title) → dict` | 创建会话，query_count=0，写入 sessions.json | TC-M01-041 |
| `get_sessions` | `() → list` | 返回全部会话，按 created_at **倒序** | TC-M01-042 |
| `delete_session` | `(session_id) → None` | 删除会话 + **级联删除**关联 qa_records | TC-M01-043 |
| `update_session` | `(session_id, title) → dict` | 更新标题，刷新 updated_at | TC-M01-046 |

### 3.2 问答记录管理（对齐 `10` §7.2）

| 方法 | 签名 | 关键行为 | 关联 TC |
|------|------|----------|---------|
| `add_record` | `(session_id, query, answer, ...) → dict` | 写入记录 + query_count 自动 +1 | TC-M01-044 |
| `get_records_by_session` | `(session_id) → list` | 按 session_id 过滤，时间正序 | TC-M01-045 |
| `delete_records_by_session` | `(session_id) → int` | 删除会话下所有记录，返回删除数量 | TC-M01-047 |

### 3.3 业务逻辑（对齐 `10` §8）

- **首次问答自动命名**：`query_count` 从 0→1 时，`title = query[:20] + "..."`

## 4. 数据文件格式

**sessions.json**：
```json
[
  {
    "session_id": "uuid-string",
    "title": "新会话",
    "created_at": "2026-04-14T10:30:00Z",
    "updated_at": "2026-04-14T10:30:00Z",
    "query_count": 0
  }
]
```

**qa_records.json**：
```json
[
  {
    "id": "rec_1713081600",
    "session_id": "uuid-string",
    "query": "用户提问",
    "answer": "系统回答",
    "llm_used": true,
    "model": "qwen-plus",
    "response_time_ms": 1200,
    "answer_source": "bailian",
    "citations": [],
    "timestamp": "2026-04-14T10:35:00Z"
  }
]
```

## 5. 验收标准（AC）

| # | 验收条件 |
|---|---------|
| AC-01 | `create_session` 返回包含 session_id/title/created_at/query_count=0 的 dict |
| AC-02 | `get_sessions` 按 created_at 倒序返回 |
| AC-03 | `delete_session` 同时删除 qa_records 中关联记录 |
| AC-04 | `update_session` 更新 title 后 updated_at 刷新 |
| AC-05 | `add_record` 后 session 的 query_count 自动 +1 |
| AC-06 | `add_record` 首次问答(query_count 0→1)触发自动命名 |
| AC-07 | `get_records_by_session` 无记录时返回空列表 |
| AC-08 | 所有写操作后 JSON 文件持久化（RMW 模式） |
