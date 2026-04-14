# 投研问答助手（M1-QA）— 可执行任务清单

> 基于 Spec 01-14 生成，按里程碑 S0→S1→S2→S3→S4 排列，每个任务对齐 WBS、REQ 和 TC。
> 代码目录：`../code/backend/` + `../code/frontend/`

---

## S0 项目脚手架

| ID | 任务 | WBS | 产出文件 | DoD |
|----|------|-----|----------|-----|
| T-001 | 初始化后端项目结构 | — | `backend/wsgi.py`, `backend/app/__init__.py`, `backend/requirements.txt` | `flask run` 启动无报错，返回 404 |
| T-002 | 初始化前端项目（React + Vite） | — | `frontend/` 完整脚手架 | `npm run dev` 启动，浏览器可访问 5173 |
| T-003 | 创建配置文件 | — | `backend/.env.example`, `backend/.flake8`, `.gitignore` | 环境变量模板含 `IRA_COPAW_*_URL`, `DASHSCOPE_API_KEY`, `DATA_DIR` |
| T-004 | 创建后端目录骨架 | — | `backend/app/routes/`, `backend/app/agent/`, `backend/app/storage/`, `backend/tests/` | 目录结构对齐 08 §2 分层架构 |

---

## S1 会话管理（REQ-001 → 可演示：会话 CRUD + 前端侧栏）

### W2 存储层

| ID | 任务 | 产出文件 | DoD | 关联 TC |
|----|------|----------|-----|---------|
| T-101 | 实现 Storage 类初始化 | `app/storage/storage.py` | `DATA_DIR` 不存在时自动创建，初始化空 JSON 文件 | TC-M01-040 |
| T-102 | 实现 `create_session(session_id, title)` | 同上 | 写入 sessions.json，返回含 session_id/title/created_at/query_count 的 dict | TC-M01-041 |
| T-103 | 实现 `get_sessions()` | 同上 | 返回全部会话列表，按 updated_at 倒序 | TC-M01-042 |
| T-104 | 实现 `delete_session(session_id)` + 级联删除 | 同上 | 删除会话 + 关联 QARecord，返回删除记录数 | TC-M01-043 |
| T-105 | 实现 `update_session(session_id, title, query_count)` | 同上 | 更新 title/query_count/updated_at | TC-M01-046 |

### W1 路由层

| ID | 任务 | 产出文件 | DoD | 关联 TC |
|----|------|----------|-----|---------|
| T-111 | 创建 Flask app 工厂 + agent 蓝图注册 | `app/__init__.py`, `app/routes/agent_bp.py` | 蓝图挂载到 `/api/v1/agent`，traceId 中间件就绪 |  |
| T-112 | 实现 `POST /sessions` | `app/routes/agent_bp.py` | 201 + 含 traceId/session_id/title/created_at/query_count | TC-M01-021 |
| T-113 | 实现 `GET /sessions` | 同上 | 200 + sessions 数组 | TC-M01-020 |
| T-114 | 实现 `DELETE /sessions/<id>` | 同上 | 200 + message + deleted_records；不存在→404 SESSION_NOT_FOUND | TC-M01-024, 025 |
| T-115 | 实现 `GET /capabilities` | 同上 | 200 + copaw_configured/bailian_configured/model 字段 | — |
| T-116 | 实现统一错误响应格式 | `app/routes/agent_bp.py` | 所有错误返回 `{error:{code,message,details,traceId}}` | — |

### W4 前端视图（S1 部分）

| ID | 任务 | 产出文件 | DoD |
|----|------|----------|-----|
| T-121 | 搭建 App 布局（Header + Sidebar + Main + InputArea） | `src/App.jsx`, `src/App.module.css` | 四区域正确渲染，响应式布局 |
| T-122 | Header：标题 + 能力状态芯片 | `src/App.jsx` | 调用 GET /capabilities，根据配置显示 CoPaw/百炼/离线演示 芯片 |
| T-123 | Sidebar：会话列表 + 选中高亮 | `src/App.jsx` | 页面加载调 GET /sessions 渲染列表，点击高亮 + 加载 records |
| T-124 | Sidebar：新建会话按钮 | `src/App.jsx` | 点击调 POST /sessions，新会话插入列表头部并自动选中 |
| T-125 | Sidebar：删除会话 | `src/App.jsx` | 点击 × → 确认弹窗 → DELETE → 从列表移除 |
| T-126 | Main：三态渲染骨架 | `src/App.jsx` | A空状态 / B常见问题网格 / C对话历史 正确切换 |

### W6 测试（S1 部分）

| ID | 任务 | 产出文件 | DoD |
|----|------|----------|-----|
| T-131 | Storage 单元测试 | `tests/unit/test_storage.py` | 覆盖 TC-M01-040～045，全绿 |
| T-132 | 会话 API 集成测试 | `tests/integration/test_sessions.py` | 覆盖 TC-M01-020～025，全绿 |

---

## S2 问答核心（REQ-002 → 可演示：提问 + 三级降级 + 回答展示）

### W2 存储层（记录部分）

| ID | 任务 | 产出文件 | DoD | 关联 TC |
|----|------|----------|-----|---------|
| T-201 | 实现 `add_record(session_id, query, answer, ...)` | `app/storage/storage.py` | 写入 qa_records.json + query_count+1 + 首次自动命名 | TC-M01-044 |
| T-202 | 实现 `get_records_by_session(session_id)` | 同上 | 按 session_id 过滤，按 timestamp 正序 | TC-M01-045 |
| T-203 | 实现 `delete_records_by_session(session_id)` | 同上 | 删除指定会话全部记录，返回删除数量 | TC-M01-047 |

### W3 Agent 编排

| ID | 任务 | 产出文件 | DoD |
|----|------|----------|-----|
| T-211 | 实现 Demo 兜底回复 | `app/agent/agent.py` | 无任何配置时返回 `{answer_source:'demo', llm_used:false}` |
| T-212 | 实现 CoPaw 桥接 Provider | `app/agent/copaw_bridge.py` | 检测 `IRA_COPAW_*_URL` → 20s 超时 → 失败返回 None |
| T-213 | 实现百炼 DashScope Provider | `app/agent/bailian_qa.py` | 检测 `DASHSCOPE_API_KEY` → 120s 超时 → 区分错误码 |
| T-214 | 实现 Agent 三级降级编排 | `app/agent/agent.py` | CoPaw→百炼→Demo 链式降级，返回 answer + answer_source + llm_used + model + response_time_ms |

### W1 路由层（问答部分）

| ID | 任务 | 产出文件 | DoD | 关联 TC |
|----|------|----------|-----|---------|
| T-221 | 实现 `POST /ask` | `app/routes/agent_bp.py` | 200 + answer/llm_used/model/response_time_ms/answer_source/traceId | TC-M01-001 |
| T-222 | 实现 `GET /sessions/<id>/records` | 同上 | 200 + records 数组；不存在→404 | TC-M01-030, 031 |
| T-223 | 参数校验：空 query→EMPTY_QUERY / 超500→INVALID_QUERY / session不存在→SESSION_NOT_FOUND | 同上 | 400/404 + 对应 error.code | TC-M01-002, 003 |

### W4 前端视图（S2 部分）

| ID | 任务 | 产出文件 | DoD |
|----|------|----------|-----|
| T-231 | 输入区域：textarea + 发送按钮 + 清空按钮 | `src/App.jsx` | placeholder "请输入您的问题..."，loading 时 disabled |
| T-232 | 提问提交：调用 POST /ask | `src/App.jsx` | 发送 query + session_id → 接收 answer → 追加到记录列表 |
| T-233 | 对话历史列表渲染 | `src/App.jsx` | 每条记录：用户问题 + AI回答 + 来源标签 + 时间戳 |
| T-234 | 来源标签组件 | `src/App.jsx` | copaw→绿色 / bailian→蓝色 / demo→灰色 |

### W5 状态管理

| ID | 任务 | 产出文件 | DoD |
|----|------|----------|-----|
| T-241 | 实现 7 个 State 变量 | `src/App.jsx` | sessions/currentSession/records/query/isLoading/capabilities/error |
| T-242 | 错误处理展示 | `src/App.jsx` | EMPTY_QUERY→"请输入问题" / INVALID_QUERY→"问题过长" / UPSTREAM_ERROR→"服务暂时不可用" |

### W6 测试（S2 部分）

| ID | 任务 | 产出文件 | DoD |
|----|------|----------|-----|
| T-251 | 问答 API 集成测试 | `tests/integration/test_ask.py` | 覆盖 TC-M01-001～004，全绿 |
| T-252 | 记录 API 集成测试 | `tests/integration/test_records.py` | 覆盖 TC-M01-030～031，全绿 |
| T-253 | Storage 记录单元测试 | `tests/unit/test_storage.py` | 补充 TC-M01-044～047，全绿 |

---

## S3 研报摘要与对比（REQ-003 → 可演示：摘要卡片 + 对比表格 + AI总结）

### W3 Agent 编排

| ID | 任务 | 产出文件 | DoD |
|----|------|----------|-----|
| T-301 | 研报摘要提取逻辑 | `app/agent/agent.py` | 从 LLM 回复中解析出多来源研报摘要 |
| T-302 | 多来源对比逻辑 | `app/agent/agent.py` | 按用户指定指标生成对比数据结构，标注研报来源 |
| T-303 | AI 总结生成 | `app/agent/agent.py` | 在摘要 + 对比之后，生成一段总结结论 |

### W4 前端视图（S3 部分）

| ID | 任务 | 产出文件 | DoD |
|----|------|----------|-----|
| T-311 | 研报摘要卡片 | `src/App.jsx` | 多来源研报摘要以卡片形式展示 |
| T-312 | 对比表格组件 | `src/App.jsx` | 表格展示各维度对比，支持溯源标注 |
| T-313 | AI 总结展示 | `src/App.jsx` | 在摘要卡片和对比表格下方展示 AI 生成的总结结论 |

### W6 测试（S3 部分）

| ID | 任务 | 产出文件 | DoD |
|----|------|----------|-----|
| T-321 | 研报摘要功能测试 | `tests/integration/test_summary.py` | 覆盖 TC-M01-010～015 |

---

## S4 发布准备（全部 P0 REQ → 可演示：完整可用系统）

| ID | 任务 | WBS | DoD |
|----|------|-----|-----|
| T-401 | 代码规范检查 | W6 | `black --check` + `flake8` 全通过（G-LINT） |
| T-402 | 单元测试全绿 | W6 | `pytest tests/unit/ -q` 全绿（G-UNIT） |
| T-403 | 集成测试全绿 | W6 | `pytest tests/integration/ -q` 全绿（G-INT） |
| T-404 | P0 验收标准全覆盖 | W6 | 所有 P0 TC 全部通过（G-AC） |
| T-405 | 性能验证 | W6 | `response_time_ms < 5000`（G-PERF） |
| T-406 | 前端交互完善 | W4 | 边界情况处理、UI 美化、常见问题网格 |
| T-407 | CORS 配置 | W1 | Flask-CORS 允许 localhost:5173 |

---

## 附录：任务依赖关系

```
T-001 ──→ T-004 ──→ T-101~105 ──→ T-131（Storage 测试）
                         ↓
T-002 ──→ T-121~126     T-111~116 ──→ T-132（会话 API 测试）
              ↓              ↓
         T-231~234      T-201~203 ──→ T-211~214 ──→ T-221~223 ──→ T-251~253
              ↓                                          ↓
         T-241~242                                  T-301~303 ──→ T-311~313
                                                         ↓
                                                    T-401~407
```

## 附录：REQ → Task 追溯

| REQ | 描述 | 核心 Task | 验证 TC |
|-----|------|-----------|---------|
| REQ-001 | 问答返回正确结果 | T-214, T-221 | TC-M01-001 |
| REQ-002 | 会话管理功能可用 | T-101~105, T-112~114, T-121~125 | TC-M01-020～025 |
| REQ-003 | 研报摘要与对比 | T-301~303, T-311~313 | TC-M01-010～015 |
| REQ-004 | 无密钥时优雅降级 | T-211, T-214 | TC-M01-004 |
| REQ-005 | 输入校验正确 | T-223 | TC-M01-002, 003 |
