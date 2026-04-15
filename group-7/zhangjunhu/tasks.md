# M1-QA 投研问答助手 — 开发任务清单

> 模块编号：M1-QA | 版本：v0.2 | 日期：2026-04-14
> 依据：spec/05(v0.1) · 06(v0.2) · 08(v0.2) · 09(v0.2) · 10(v0.2) · 12(v0.2) · 13(v0.2)

---

## 里程碑总览

| 里程碑 | 演示目标 | 满足需求 | 验证 TC |
|--------|----------|----------|---------|
| S1 | 会话 CRUD + 前端侧栏 | REQ-001 | TC-M01-020～024 |
| S2 | 问答提交（SSE 流式）+ 三级降级 | REQ-002 | TC-M01-001～004 |
| S3 | 历史记录 + 关键词搜索 + 相似性检测 | REQ-003 | TC-M01-030/031/060/061 |
| S4 | 股票标记识别 + 股票信息查询 | REQ-004 | TC-M01-070～072 |

> S1/S2 可并行开发（前后端分离），S3 依赖 S2（需有问答记录），S4 可独立。

---

## 环境准备

- [ ] **ENV-001** 创建后端目录：`code/backend/` — wsgi.py, agent_bp.py, agent.py, storage.py, stock_service.py
- [ ] **ENV-002** 初始化前端：`code/frontend/` — Vite + React 项目
- [ ] **ENV-003** 创建 `.env` + `.gitignore`：IRA_COPAW_*_URL, DASHSCOPE_API_KEY
- [ ] **ENV-004** 创建 `code/backend/data/` 数据目录
- [ ] **ENV-005** 配置 pytest：`code/backend/tests/conftest.py`

---

## S1 — 会话管理（后端 + 前端可并行）

### S1-后端

- [ ] **S1-BE-01** storage.py: `Storage.__init__` — 初始化数据目录（→ TC-M01-040）
- [ ] **S1-BE-02** storage.py: `create_session(session_id, title)` — 写入 sessions.json（→ TC-M01-041）
- [ ] **S1-BE-03** storage.py: `get_sessions()` — 按 created_at 倒序返回（→ TC-M01-042）
- [ ] **S1-BE-04** storage.py: `delete_session(session_id)` — 级联删除记录（→ TC-M01-043）
- [ ] **S1-BE-05** agent_bp.py: 注册 Blueprint + traceId 统一注入（→ spec/09 §2）
- [ ] **S1-BE-06** agent_bp.py: `GET /sessions` → 200（→ TC-M01-020）
- [ ] **S1-BE-07** agent_bp.py: `POST /sessions` → 201, 默认 title="新会话"（→ TC-M01-021/022）
- [ ] **S1-BE-08** agent_bp.py: `DELETE /sessions/<id>` → 200, 不存在→400 SESSION_NOT_FOUND（→ TC-M01-023/024）

### S1-前端（可与 S1-后端并行）

- [ ] **S1-FE-01** 页面布局：Header + Sidebar + Main + InputArea 骨架（→ spec/06 §1）
- [ ] **S1-FE-02** Sidebar 会话列表：GET /sessions 渲染（→ spec/06 §3）
- [ ] **S1-FE-03** "+新建" 按钮：POST /sessions，插入列表头部
- [ ] **S1-FE-04** 删除按钮（×）：确认后 DELETE，从列表移除
- [ ] **S1-FE-05** 会话选中高亮 + currentSession 状态

### S1-测试

- [ ] **S1-TE-01** Storage 单元测试：init/create/get/delete（→ TC-M01-040～043）
- [ ] **S1-TE-02** 会话 API 集成测试（→ TC-M01-020～024）

---

## S2 — 问答核心（后端 + 前端可并行）

### S2-后端

- [ ] **S2-BE-01** storage.py: `add_record(session_id, record)` — 写入 + query_count+1 + 自动命名（→ TC-M01-044, spec/10 §6）
- [ ] **S2-BE-02** storage.py: `get_records_by_session(session_id)` — 正序返回（→ TC-M01-045）
- [ ] **S2-BE-03** agent.py: `DemoAgent.ask(query)` — 纯字符串, answer_source='demo'（→ TC-M01-004）
- [ ] **S2-BE-04** agent.py: `BailianAgent.ask(query)` — DASHSCOPE_API_KEY, 超时120s（→ spec/08 §4）
- [ ] **S2-BE-05** agent.py: `CoPawAgent.ask(query)` — IRA_COPAW_*_URL, 超时20s（→ spec/08 §4）
- [ ] **S2-BE-06** agent.py: `Agent.ask(query, session_id)` — 三级降级 + response_time_ms（→ spec/08 §4）
- [ ] **S2-BE-07** agent.py: `Agent.ask_stream(query, session_id)` — yield SSE 事件流（→ spec/09 §3 SSE）
- [ ] **S2-BE-08** agent_bp.py: `POST /ask` — SSE 流式 + 非流式兼容, 参数校验（→ TC-M01-001～003）

### S2-前端（可与 S2-后端并行）

- [ ] **S2-FE-01** useState 初始化：9 个状态变量（→ spec/06 §7）
- [ ] **S2-FE-02** InputArea：textarea + 发送 + 清空（→ spec/06 §5）
- [ ] **S2-FE-03** 发送逻辑：EventSource 接收 SSE，逐步渲染（→ spec/06 §4.1 流式）
- [ ] **S2-FE-04** Main 三态渲染：空状态 / 新会话 / 对话历史（→ spec/06 §4）
- [ ] **S2-FE-05** 问答卡片：来源标签（copaw/bailian/demo 颜色）（→ spec/06 §4.2）
- [ ] **S2-FE-06** 错误展示：EMPTY_QUERY / INVALID_QUERY / SESSION_NOT_FOUND（→ spec/06 §6）

### S2-测试

- [ ] **S2-TE-01** 问答 API 测试：正常200 / 空query / 超长 / 降级demo（→ TC-M01-001～004）
- [ ] **S2-TE-02** Storage 测试：add_record / get_records_by_session（→ TC-M01-044/045）

---

## S3 — 历史记录 + 搜索（依赖 S2 有记录数据）

### S3-后端

- [ ] **S3-BE-01** agent_bp.py: `GET /sessions/<id>/records` → 200, 无记录返回空数组（→ TC-M01-030/031）
- [ ] **S3-BE-02** storage.py: `search_records(keyword, limit=20)` — 全文匹配 query/answer（→ TC-M01-060）
- [ ] **S3-BE-03** storage.py: `find_similar_records(query)` — 文本相似度匹配（→ TC-M01-061）
- [ ] **S3-BE-04** agent_bp.py: `GET /records/search?keyword=xxx` → 200（→ TC-M01-060）
- [ ] **S3-BE-05** agent_bp.py: `POST /records/similar` → 200（→ TC-M01-061）

### S3-前端

- [ ] **S3-FE-01** useEffect 监听 currentSession 变化加载 records（→ spec/06 §4）
- [ ] **S3-FE-02** 搜索输入框 + 实时搜索调用（→ spec/06 §4.4）
- [ ] **S3-FE-03** 相似性提问检测：提问前检查 + "查看历史/发起新提问" 选择（→ spec/06 §4.5）
- [ ] **S3-FE-04** 会话标题自动更新：首次提问后刷新侧栏（→ spec/10 §6）

### S3-测试

- [ ] **S3-TE-01** 记录/搜索/相似性 API 测试（→ TC-M01-030/031/060/061）

---

## S4 — 股票信息查询（可与 S3 并行）

### S4-后端

- [ ] **S4-BE-01** stock_service.py: `identify_stocks(answer_text)` — 从回答中识别股票名称/代码
- [ ] **S4-BE-02** stock_service.py: `get_stock_info(code)` — 返回股票摘要信息
- [ ] **S4-BE-03** agent_bp.py: `GET /stock/<code>` → 200, 返回股票信息（→ TC-M01-070/071）
- [ ] **S4-BE-04** POST /ask 响应中集成 stocks 字段（→ TC-M01-072）

### S4-前端

- [ ] **S4-FE-01** 回答卡片中股票名称渲染为高亮可点击标签（→ spec/06 §4.3）
- [ ] **S4-FE-02** 点击股票标签：创建新会话 + 自动查询股票信息
- [ ] **S4-FE-03** 同一股票复用已打开窗口，不重复创建（→ US-004 AC-004-02）

### S4-测试 + 收尾

- [ ] **S4-TE-01** 股票查询 API 测试（→ TC-M01-070～072）
- [ ] **S4-TE-02** 能力探测 API 测试（→ TC-M01-050～052）
- [ ] **S4-TE-03** 全量 pytest + 覆盖率（→ spec/13 §四 G-UNIT/G-INT）

---

## 并行开发策略

```
时间线 →  [========= S1 =========]
          [后端 S1-BE] ──┐      [后端 S2-BE] ──┐
          [前端 S1-FE] ──┤      [前端 S2-FE] ──┤
          [测试 S1-TE] ──┘      [测试 S2-TE] ──┘
                               [========= S2 =========]
                                                [后端 S3-BE] [后端 S4-BE]
                                                [前端 S3-FE] [前端 S4-FE]
                                                [==== S3 ====][==== S4 ====]
                                                             [全量测试]
```

**并行点**：
1. S1 内部：后端与前端并行开发
2. S2 内部：后端与前端并行开发
3. S3 与 S4：互不依赖，可并行
4. 前端开发可 mock API 先行

---

## 统计

| 里程碑 | 后端 | 前端 | 测试 | 小计 |
|--------|------|------|------|------|
| 环境准备 | — | — | — | 5 |
| S1 | 8 | 5 | 2 | 15 |
| S2 | 8 | 6 | 2 | 16 |
| S3 | 5 | 4 | 1 | 10 |
| S4 | 4 | 3 | 3 | 10 |
| **合计** | **25** | **18** | **8** | **56** |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.2 | 2026-04-14 | 基于 spec v0.2 生成，含流式/搜索/股票任务 |
