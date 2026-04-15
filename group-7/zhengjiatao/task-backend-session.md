# Task: 投研问答助手 - 后端会话管理模块

## 任务概述
实现投研问答助手的会话管理后端模块，包含会话的增删改查、问答记录的存储与检索。

## 参考文档
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/04-产品需求说明.md` - SC-01/02/03 场景
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/05-用户故事与验收标准.md` - US-001/002/003/005
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/09-API接口规格.md` - 端点 3/4/5/6/7
- `/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/spec-team/10-数据模型与存储规格.md` - Session/QARecord 实体定义

## 技术栈
- Python + Flask
- JSON 文件存储（sessions.json + qa_records.json）

## 项目路径
`/Users/zhengjiatao/Desktop/Ai-train/group-workshop/group-7/zhengjiatao/project/backend`

## 功能范围

### 1. 数据模型

#### Session 实体
| 字段 | 类型 | 约束 |
|------|------|------|
| session_id | string (UUID) | PK |
| title | string | ≤100字符，默认"新会话" |
| created_at | string (ISO-8601) | UTC |
| updated_at | string (ISO-8601) | UTC |
| query_count | integer | ≥0 |

#### QARecord 实体
| 字段 | 类型 | 约束 |
|------|------|------|
| id | string | PK, `rec_{timestamp}` |
| session_id | string | FK → Session |
| query | string | 1-500字符 |
| answer | string | - |
| llm_used | boolean | - |
| model | string\|null | - |
| response_time_ms | integer | - |
| answer_source | string\|null | copaw/bailian/demo |
| timestamp | string (ISO-8601) | UTC |

### 2. Storage 类方法实现

#### 5.1 会话管理
| 方法 | 签名 | 行为 |
|------|------|------|
| create_session | `(session_id, title) → dict` | 创建新会话，初始 query_count=0 |
| get_sessions | `() → list` | 返回全部会话，按 updated_at 倒序 |
| get_session | `(session_id) → dict\|None` | 根据 ID 获取单个会话 |
| delete_session | `(session_id) → None` | 删除会话，级联删除关联记录 |
| update_session | `(session_id, updates) → dict` | 更新会话字段 |
| increment_query_count | `(session_id) → int` | query_count += 1，更新 updated_at |

#### 5.2 问答记录管理
| 方法 | 签名 | 行为 |
|------|------|------|
| add_record | `(session_id, query, answer, ...) → dict` | 写入记录，更新 query_count |
| get_records_by_session | `(session_id) → list` | 按 session_id 过滤，按时间正序 |
| delete_records_by_session | `(session_id) → int` | 删除指定会话的所有记录 |

### 3. API 端点实现

#### POST /sessions - 新建会话
- 请求： `{ title?: string }`
- 响应： `{ traceId, session_id, title, created_at, query_count }`
- 状态码：201

#### GET /sessions - 会话列表
- 查询参数： `page?, page_size?`
- 响应： `{ traceId, total, page, page_size, sessions[] }`
- 排序：按 updated_at 倒序

#### DELETE /sessions/<id> - 删除会话
- 级联删除该会话下所有 QARecord
- 响应： `{ traceId, deleted, session_id }`

#### PUT /sessions/<id> - 更新会话标题
- 请求： `{ title: string }` (≤100字符)
- 响应： `{ traceId, session_id, title, updated_at }`
- 用于首次问答后自动命名

#### GET /sessions/<id>/records - 问答记录
- 查询参数： `page?, page_size?`
- 响应： `{ traceId, session_id, total, records[] }`
- 排序：按 timestamp 正序

### 4. 关键业务逻辑

#### 首次问答自动命名
```python
if session["query_count"] == 1:
    session["title"] = query[:20] + ("..." if len(query) > 20 else "")
```

#### 级联删除
删除 Session 时，同步删除所有关联 QARecord

#### 时间戳更新
- 新增问答记录时，更新 Session.updated_at
- query_count 自增

### 5. 错误处理
| error.code | HTTP | 触发条件 |
|------------|------|----------|
| SESSION_NOT_FOUND | 404 | 会话不存在 |
| INVALID_TITLE | 400 | 标题超100字符 |
| INVALID_SESSION_ID | 400 | ID 格式非法 |

### 6. 文件存储
- 存储路径：`{DATA_DIR}/sessions.json` + `qa_records.json`
- 编码：UTF-8，缩进2空格
- 读写模式：RMW（全量读入 → 修改 → 全量写回）

## 接口契约

### 统一响应格式
**成功：**
```json
{ "traceId": "tr_xxx", /* 业务字段 */ }
```

**错误：**
```json
{ "error": { "code": "SESSION_NOT_FOUND", "message": "...", "traceId": "tr_xxx" } }
```

## 验收标准
- [ ] Storage 类所有方法实现并通过单元测试
- [ ] 5个 API 端点实现并返回正确格式
- [ ] 会话列表按 updated_at 倒序排列
- [ ] 删除会话时级联删除问答记录
- [ ] 首次问答后自动更新会话标题
- [ ] query_count 正确自增
- [ ] 错误码与 HTTP 状态码对应正确

## 优先级
P0 - 核心功能，必须完成

## 依赖
- 无其他任务依赖，可并行开发
- 被依赖：前端需要调用这些 API
