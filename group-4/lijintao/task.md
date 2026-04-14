# 投研问答助手开发计划（MVP 优先）

> **核心目标**：2天内 vibe coding 完成 MVP，可演示"创建会话 → 输入问题 → 流式获取 AI 回答"完整链路
> 技术栈：Next.js 15 + FastAPI + SQLite(MVP) → PostgreSQL + Redis

---

## 优先级定义

| 级别 | 含义 | 时间 |
|------|------|------|
| **MVP** | 2天内必须完成，跑通核心链路 | Day 1-2 |
| **P1** | MVP 后优先，提升体验 | Day 3-5 |
| **P2** | 锦上添花，生产级加固 | Day 6+ |

---

## MVP 架构简化策略

| 维度 | 完整方案 | MVP 简化 |
|------|----------|----------|
| 数据库 | PostgreSQL + Redis | SQLite（零配置） |
| 认证 | JWT + 用户系统 | 跳过，硬编码用户 |
| LLM | 4级降级链 | 单一 Provider |
| 测试 | 4层测试体系 | 手动验证 |
| 部署 | Docker + K8s | 本地 dev 模式 |
| 迁移 | Alembic | SQLAlchemy create_all |

---

## MVP 任务（Day 1-2，约 16h）

> 原则：能跑就行，先不做完美分层，快速出活

### Day 1：后端核心 + 前端骨架（~8h）

#### Task 1: 全栈项目初始化（2h）

- **后端**: FastAPI + SQLite + SQLAlchemy + Pydantic
- **前端**: `npx create-next-app` + Tailwind CSS + shadcn/ui
- **DoD**:
  - [ ] `uvicorn main:app --reload` 可启动
  - [ ] `npm run dev` 可启动
  - [ ] 前端可请求后端 `/api/v1/health`

#### Task 2: 数据模型 + 会话 API（3h）

- 2 张表：`sessions`、`messages`（User 表 MVP 跳过，硬编码 user_id）
- API 实现：
  - `GET /api/v1/sessions` — 会话列表
  - `POST /api/v1/sessions` — 创建会话
  - `DELETE /api/v1/sessions/{id}` — 删除会话
- **DoD**:
  - [ ] Swagger UI 可测通所有 CRUD
  - [ ] 数据正确持久化到 SQLite

#### Task 3: 前端布局 + 会话侧栏（3h）

- 整体布局：Sidebar（240px）+ Main 内容区
- Sidebar 组件：
  - 会话列表展示（标题 + 时间）
  - 新建会话按钮
  - 删除会话（滑动/右键）
- 对接后端会话 API
- 南方基金配色：主色 `#004098`，强调色 `#E72521`
- **DoD**:
  - [ ] 页面可创建/切换/删除会话
  - [ ] Sidebar 会话列表实时更新

### Day 2：问答链路打通（~8h）

#### Task 4: LLM 集成 + 消息 API（4h）

- 单一 LLM Provider（OpenAI 或任一可用 API）
- API 实现：
  - `POST /api/v1/sessions/{id}/messages` — 发送消息，SSE 流式返回
  - `GET /api/v1/sessions/{id}/messages` — 获取历史消息
- 消息持久化：用户消息 + AI 回复均存 DB
- 上下文管理：携带最近 N 条历史消息
- **DoD**:
  - [ ] curl 可获取 SSE 流式 AI 回复
  - [ ] 消息正确存入数据库

#### Task 5: 前端消息展示 + 流式渲染（3h）

- MessageList 组件：
  - 用户消息（右侧蓝色气泡）
  - AI 消息（左侧白色气泡）
  - Markdown 渲染支持
- InputArea 组件：
  - 文本输入框 + 发送按钮
  - Enter 发送 / Shift+Enter 换行
- SSE 流式渲染：
  - EventSource 接收流式数据
  - 逐字显示 AI 回复
  - 打字机效果
- **DoD**:
  - [ ] 完整链路：输入 → 流式显示 AI 回答
  - [ ] 切换会话可加载历史消息

#### Task 6: MVP 联调与打磨（1h）

- 前后端联调修 bug
- 基础样式调整（南方基金配色 `#004098` / `#E72521`）
- 空状态处理（无会话、无消息时的提示）
- 加载态处理（发送中禁用输入）
- **DoD**:
  - [ ] 全链路无阻塞性 bug
  - [ ] 可流畅演示完整问答流程

---

## P1 任务（Day 3-5，体验提升）

#### Task 7: 多 LLM Provider + 降级策略（4h）

- Provider 抽象接口 + 工厂模式
- 降级链：Azure OpenAI → OpenAI → Claude → 本地模型
- 降级时前端显示橙色标签提示
- **关联 Spec**: `08` §LLM 集成、`07` §1.3 降级策略

#### Task 8: 历史消息分页加载（3h）

- 游标分页（cursor-based pagination）
- 前端滚动到顶部自动加载更多
- **关联 Spec**: `09` §3.3 消息接口

#### Task 9: 全文搜索功能（4h）

- 迁移到 PostgreSQL + tsvector 全文搜索
- `GET /api/v1/sessions/search` 搜索接口
- 前端搜索框 + 结果高亮显示
- **关联 Spec**: `09` §3.4 历史搜索接口

#### Task 10: 数据库迁移 SQLite → PostgreSQL（2h）

- 配置 PostgreSQL + asyncpg
- 配置 Alembic 迁移工具
- 数据迁移脚本
- **关联 Spec**: `10` §DDL

#### Task 11: 健康检查 + 状态指示器（2h）

- `/api/v1/health` 完善（DB 连接 + LLM 状态）
- 前端 Header 系统状态芯片
- 降级时显示橙色状态
- **关联 Spec**: `09` §3.1、`06` §2.1

---

## P2 任务（Day 6+，生产级加固）

#### Task 12: 安全加固（4h）

- JWT 认证中间件
- 速率限制（`11` §4.1）
- 敏感信息过滤
- 安全响应头
- **关联 Spec**: `11-安全设计规格.md`

#### Task 13: 性能优化（4h）

- Redis 缓存层
- 数据库查询优化 + 索引
- 连接池调优
- 响应压缩
- **关联 Spec**: `07` §1 性能需求

#### Task 14: 完善测试体系（4h）

- 后端：pytest 单元测试 + 集成测试
- 前端：Jest + React Testing Library
- E2E：Playwright
- 覆盖率目标 ≥ 80%
- **关联 Spec**: `13-测试策略与质量门禁.md`

#### Task 15: 监控与日志（3h）

- 结构化 JSON 日志
- Prometheus 指标暴露
- Grafana 仪表盘配置
- 错误告警通知

---

## 任务状态追踪

| 优先级 | 任务ID | 任务名称 | 预估 | 状态 |
|--------|--------|----------|------|------|
| **MVP** | T1 | 全栈项目初始化 | 2h | 未开始 |
| **MVP** | T2 | 数据模型 + 会话 API | 3h | 未开始 |
| **MVP** | T3 | 前端布局 + 会话侧栏 | 3h | 未开始 |
| **MVP** | T4 | LLM 集成 + 消息 API | 4h | 未开始 |
| **MVP** | T5 | 前端消息展示 + 流式渲染 | 3h | 未开始 |
| **MVP** | T6 | MVP 联调与打磨 | 1h | 未开始 |
| P1 | T7 | 多 Provider + 降级策略 | 4h | 未开始 |
| P1 | T8 | 历史消息分页加载 | 3h | 未开始 |
| P1 | T9 | 全文搜索功能 | 4h | 未开始 |
| P1 | T10 | 迁移到 PostgreSQL | 2h | 未开始 |
| P1 | T11 | 健康检查 + 状态指示器 | 2h | 未开始 |
| P2 | T12 | 安全加固 | 4h | 未开始 |
| P2 | T13 | 性能优化 | 4h | 未开始 |
| P2 | T14 | 完善测试体系 | 4h | 未开始 |
| P2 | T15 | 监控与日志 | 3h | 未开始 |

---

## 文档索引

| 文档 | 用途 |
|------|------|
| `03-立项提案与范围说明.md` | 项目背景与范围 |
| `04-产品需求说明.md` | 需求定义 |
| `05-用户故事与验收标准.md` | US + AC |
| `06-功能规格说明.md` | UI/UX 行为规格 |
| `07-非功能需求与约束.md` | 性能/安全约束 |
| `08-系统架构与技术选型.md` | 技术架构决策 |
| `09-API接口规格.md` | 接口定义 |
| `10-数据模型与存储规格.md` | 数据库设计 |
| `11-安全设计规格.md` | 安全规范 |
| `12-实施计划与里程碑.md` | 里程碑规划 |
| `13-测试策略与质量门禁.md` | 测试用例 |
| `14-需求追踪矩阵.md` | 追溯矩阵 |
