# 投研问答助手（M1-QA）开发任务清单

---

| 项 | 值 |
|---|---|
| 模块编号 | M1-QA |
| 模块名称 | 投研问答助手 |
| 技术栈 | 后端 Flask + JSON 文件存储 · 前端 React + Vite · pytest 测试 |
| 里程碑 | S1 会话管理 → S2 问答核心 → S3 研报解析 → S4 发布准备 |
| 依据文档 | `08` 架构 · `09` API · `10` 数据模型 · `12` 实施计划 · `13` 测试策略 |

---

## S1 — 会话管理（可演示：会话 CRUD + 前端侧栏）

> **演示目标**：用户可在页面上创建、列表、删除、切换会话。
> **满足需求**：需求-M1-001（会话管理 CRUD）、需求-M1-010（级联删除）

### W2-S1 存储层 — 会话 CRUD

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 TC |
|--------|----------|----------|----------------|---------|
| T-001 | 初始化 Storage 类 | 创建 `storage.py`，实现 `Storage.__init__`：自动创建 `{DATA_DIR}` 目录，初始化 `sessions.json`、`qa_records.json`、`reports.json` 空文件；编码 UTF-8，缩进 2 空格 | 目录不存在时自动创建，文件不存在时初始化为空数组 `[]`（对齐 `10` §2） | TC-M01-040 |
| T-002 | 实现 create_session | `create_session(session_id, title) → dict`：写入 session_id/title/created_at/updated_at/query_count(初始0)，title 默认 "新会话" | 返回字典含 5 个字段，created_at 为 ISO-8601 UTC 格式（对齐 `10` §3） | TC-M01-041 |
| T-003 | 实现 get_sessions | `get_sessions() → list`：读取全部会话，按 `updated_at` 倒序排列 | 返回列表，空时返回 `[]`（对齐 `10` §5.1） | TC-M01-042 |
| T-004 | 实现 delete_session | `delete_session(session_id) → None`：删除指定会话 + **级联删除**该会话下所有 QARecord | 会话删除后 get_sessions 不含该条；关联记录同步清除（对齐 `10` §6 级联删除） | TC-M01-043 |
| T-005 | 实现 update_session | `update_session(session_id, **kwargs) → dict`：更新 title/updated_at/query_count 等字段 | 返回更新后的完整会话字典（对齐 `10` §5.1） | TC-M01-046 |
| T-006 | 实现 delete_records_by_session | `delete_records_by_session(session_id) → int`：删除指定会话的所有记录，返回删除条数 | 返回整数，delete_session 内部调用此方法（对齐 `10` §5.2） | TC-M01-047 |

### W1-S1 路由层 — 会话 API

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 TC |
|--------|----------|----------|----------------|---------|
| T-007 | 创建 Flask 应用入口 | 创建 `app.py`，注册 `agent_bp` Blueprint，Base URL `/api/v1/agent`，配置 CORS 全开放 | Flask 可启动在 5000 端口，`/api/v1/agent/` 前缀可访问（对齐 `08` §6） | — |
| T-008 | 实现 traceId 中间件 | 每个请求生成 `tr_{uuid.hex}`（32 位十六进制），优先复用 `X-Trace-Id` 请求头；注入所有响应顶层 | 所有成功/错误响应含 traceId 字段（对齐 `07` §3.1） | TC-M01-006 |
| T-009 | POST /sessions 端点 | 请求体 `{title?: string}`，默认 "新会话"；调用 `Storage.create_session`；返回 201 + session_id/title/created_at/query_count/traceId | title ≤100 字符校验，超长返回 400 INVALID_TITLE（对齐 `09` §4） | TC-M01-021, 022, 026 |
| T-010 | GET /sessions 端点 | 无请求体；调用 `Storage.get_sessions`；返回 200 + sessions[]/total/traceId | sessions 数组按 updated_at 倒序（对齐 `09` §5） | TC-M01-020, 025 |
| T-011 | DELETE /sessions/<id> 端点 | 路径参数 id；调用 `Storage.delete_session`；返回 200 + deleted=true/session_id/traceId；级联删除关联记录 | id 不存在返回 404 NOT_FOUND（对齐 `09` §6） | TC-M01-023, 024 |

### W4-S1 前端 — 会话侧栏

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 FSD |
|--------|----------|----------|----------------|----------|
| T-012 | 初始化 React + Vite 项目 | `npm create vite@latest`，安装依赖，配置 proxy 到 `localhost:5000` | `npm run dev` 启动在 5173 端口，可访问首页（对齐 `08` §3/§6） | — |
| T-013 | 实现页面布局骨架 | Header + Sidebar + Main + Input Area 四区布局，CSS Modules 样式隔离 | 页面结构与 `06` §1 ASCII 图一致（对齐 `06` §1） | `06` §1 |
| T-014 | 实现 Sidebar 会话列表 | 页面加载调用 `GET /sessions` 渲染列表；默认选中第一个会话；点击会话高亮切换 | 列表含 title、query_count；选中态背景色变化（对齐 `06` §3） | `06` §3 |
| T-015 | 实现新建会话按钮 | 点击 "+ 新建" 调用 `POST /sessions`；新会话插入列表头部并自动选中 | title 默认 "新会话"（对齐 `06` §3） | `06` §3 |
| T-016 | 实现删除会话功能 | 点击 × 弹出确认弹窗；确认后调用 `DELETE /sessions/<id>`；从列表移除 | 删除后若为当前选中会话，自动切换到下一个（对齐 `06` §3） | `06` §3 |
| T-017 | 实现 Main 区 A 空状态 | `currentSession === null` 时显示 "请创建或选择一个会话开始" | 文案和居中样式正确（对齐 `06` §4） | `06` §4 |

### W6-S1 测试 — S1 Fixture + 会话测试

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 TC |
|--------|----------|----------|----------------|---------|
| T-018 | 搭建 pytest 测试框架 | 创建 `tests/` 目录结构：`unit/`、`integration/`、`contract/`；编写 `conftest.py` 含 Flask test_client fixture、临时 Storage fixture | `python -m pytest tests/ -q` 可运行（对齐 `13` 执行命令） | — |
| T-019 | 编写 Storage 会话单元测试 | TC-M01-040~043, 046, 047 共 6 条：init/create/get/delete/update/delete_records | 全部通过，覆盖级联删除场景（对齐 `13` §3.5） | TC-M01-040~043,046,047 |
| T-020 | 编写会话 API 集成测试 | TC-M01-020~024 共 5 条：GET/POST/DELETE 正常+异常路径 | 全部通过，含 404 NOT_FOUND 场景（对齐 `13` §3.2） | TC-M01-020~024 |
| T-021 | 编写会话 API 契约测试 | TC-M01-025~026 共 2 条：GET/POST sessions 响应 schema 验证 | 字段名、类型与 `09` §4-§5 完全一致（对齐 `13` §3.2） | TC-M01-025, 026 |

---

## S2 — 问答核心（可演示：提问 + 三级降级 + 历史记录）

> **演示目标**：用户在会话中提问获得回答，支持三级降级，可查看历史记录。
> **满足需求**：需求-M1-002（问答提交）、需求-M1-003（历史记录）、需求-M1-005（输入校验）、需求-M1-009（能力状态）、需求-M1-011（优雅降级）、需求-M1-012（自动命名）
> **前置条件**：S1 会话管理全部完成；CoPaw 或百炼至少一个 API Key 配置完成

### W2-S2 存储层 — 问答记录

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 TC |
|--------|----------|----------|----------------|---------|
| T-022 | 实现 add_record | `add_record(session_id, query, answer, llm_used, model, response_time_ms, answer_source) → dict`：写入 QARecord（id 格式 `rec_{ts}`）；自动 query_count+1、updated_at 刷新；首次问答自动命名 title=query[:20]+"..." | 返回完整记录字典；query_count 递增正确；首次命名触发（对齐 `10` §4/§5.2/§6） | TC-M01-044 |
| T-023 | 实现 get_records_by_session | `get_records_by_session(session_id) → list`：按 session_id 过滤返回记录列表 | 正确过滤，空时返回 `[]`（对齐 `10` §5.2） | TC-M01-045 |

### W3-S2 Agent 编排 — 三级降级

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 TC |
|--------|----------|----------|----------------|---------|
| T-024 | 实现 CoPaw 桥接 | 创建 `copaw_bridge.py`：检测 `IRA_COPAW_*_URL` 环境变量；HTTP 调用 CoPaw API；超时 20s；失败返回 None 静默降级 | 配置存在时正常调用；未配置或超时时返回 None（对齐 `08` §4） | TC-M01-004 |
| T-025 | 实现百炼集成 | 创建 `bailian_qa.py`：检测 `DASHSCOPE_API_KEY` 环境变量；调用 DashScope API；超时 120s；区分错误码 | 配置存在时正常调用；未配置或超时时返回 None（对齐 `08` §4） | TC-M01-004 |
| T-026 | 实现 Agent 三级降级链 | 创建 `agent.py`：`ask(query, session_id)` 按 CoPaw→百炼→Demo 顺序尝试；不可跳级；Demo 模式纯字符串拼接始终可用 | 降级顺序正确；每级返回正确的 answer_source 和 llm_used；Demo 无外部依赖（对齐 `08` §4、`07` §1.2） | TC-M01-001, 004 |

### W1-S2 路由层 — 问答 + 记录 + 能力 API

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 TC |
|--------|----------|----------|----------------|---------|
| T-027 | GET /capabilities 端点 | 返回 200 + copaw_configured(bool)/bailian_configured(bool)/traceId；检测环境变量判定 | 字段类型正确，无配置时均为 false（对齐 `09` §1 端点 1） | TC-M01-001 |
| T-028 | POST /ask 端点 | 请求体 query(必填1-500)/session_id(必填UUID)/report_id(可选)；校验：空→EMPTY_QUERY，超长→INVALID_QUERY，无效session→INVALID_SESSION；调用 Agent.ask；写入 Storage.add_record；返回 200 + answer/llm_used/model/response_time_ms/answer_source/session_id/timestamp/traceId | 全部参数校验通过；响应含 8 个业务字段 + traceId（对齐 `09` §3） | TC-M01-001~006 |
| T-029 | GET /sessions/<id>/records 端点 | 路径参数 id；校验会话存在→404 NOT_FOUND；调用 `Storage.get_records_by_session`；返回 200 + session_id/records[]/traceId | records 数组元素含 id/query/answer/timestamp/llm_used/answer_source（对齐 `09` §7） | TC-M01-030~033 |

### W4-S2 前端 — 提问区 + 历史展示

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 FSD |
|--------|----------|----------|----------------|----------|
| T-030 | 实现 Header 能力状态芯片 | 页面加载调用 `GET /capabilities`；根据 copaw/bailian 配置状态显示不同芯片文案和颜色 | CoPaw→绿色、百炼→蓝色、离线→灰色（对齐 `06` §2.1） | `06` §2.1 |
| T-031 | 实现 Input Area 输入区 | textarea 3行 + 发送按钮 + 清空按钮；空输入时发送置灰；超500字符红色提示；未选会话时发送置灰 | 校验逻辑完整（对齐 `06` §5） | `06` §5 |
| T-032 | 实现问答提交流程 | 点击发送→isLoading=true→调用 `POST /ask`→追加到 records→isLoading=false→清空输入框；loading 时按钮 disabled + "发送中…" | 请求成功后记录立即显示在对话区（对齐 `06` §5） | `06` §5 |
| T-033 | 实现 Main 区 B 常见问题 | 有会话但无记录时显示 6 个常见问题卡片网格；点击卡片自动填入输入框并触发发送 | 6 个卡片内容与 `06` §4.1 一致（对齐 `06` §4.1） | `06` §4.1 |
| T-034 | 实现 Main 区 C 对话历史 | 有记录时按时间倒序显示问答卡片：用户头像+query、AI头像+answer(Markdown渲染)、来源标签、响应时间、时间戳、复制按钮 | 来源标签逻辑：copaw→绿色、bailian→蓝色、demo→灰色（对齐 `06` §4.2/§4.3） | `06` §4.2/§4.3 |
| T-035 | 实现错误处理展示 | 后端返回错误码时，前端匹配展示对应中文提示；8 种错误码全覆盖 | 错误提示文案与 `06` §6 完全一致（对齐 `06` §6） | `06` §6 |
| T-036 | 实现状态管理 | 9 个 React useState：sessions/currentSession/records/inputValue/isLoading/error/capabilities/reports/uploading | 初始值与 `06` §7 一致（对齐 `06` §7） | `06` §7 |

### W6-S2 测试 — P0 用例

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 TC |
|--------|----------|----------|----------------|---------|
| T-037 | 编写 Storage 记录单元测试 | TC-M01-044, 045 共 2 条：add_record（含自动命名/计数递增）、get_records_by_session | 全部通过（对齐 `13` §3.5） | TC-M01-044, 045 |
| T-038 | 编写问答 API 集成测试 | TC-M01-001~005 共 5 条：成功提问、空query、超长query、降级demo、无效session | 全部通过，响应字段正确（对齐 `13` §3.1） | TC-M01-001~005 |
| T-039 | 编写问答 API 契约测试 | TC-M01-006：验证响应字段类型 llm_used=bool, answer_source∈枚举, traceId 格式 | 与 `09` §3 完全一致（对齐 `13` §3.1） | TC-M01-006 |
| T-040 | 编写记录 API 集成测试 | TC-M01-030~032 共 3 条：正常返回、空记录、无效session | 全部通过（对齐 `13` §3.3） | TC-M01-030~032 |
| T-041 | 编写记录 API 契约测试 | TC-M01-033：records 数组元素 schema 验证 | 字段类型与 `09` §7 一致（对齐 `13` §3.3） | TC-M01-033 |

---

## S3 — 研报解析（可演示：上传 / 解析 / 列表 / 搜索 / 详情）

> **演示目标**：用户上传 PDF/HTML 研报，系统解析提取四要素，支持列表查看和模糊搜索。
> **满足需求**：需求-M1-004（研报上传与解析）、需求-M1-006（研报列表搜索）、需求-M1-007（研报详情）、需求-M1-008（研报删除）
> **前置条件**：S2 问答核心全部完成；PDF 解析库（如 PyPDF2）安装就绪

### W2-S3 存储层 — 研报 CRUD

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 TC |
|--------|----------|----------|----------------|---------|
| T-042 | 实现 create_report | `create_report(report_id, session_id, file_data) → dict`：写入 Report 实体（report_id/session_id/title/rating/target_price/core_views/full_content/parsed_at/status/file_path），状态初始 `parsing` | 返回完整字典，parsed_at 为 ISO-8601 UTC（对齐 `10` §5.3/§8） | TC-M01-048 |
| T-043 | 实现 get_reports | `get_reports(keyword=None, page=1, page_size=20) → list`：查询研报列表，支持 keyword 模糊搜索匹配标题/评级/目标价/核心观点；分页默认 20 条，最大 100 条 | 搜索匹配正确；分页参数有效（对齐 `10` §5.3/§6） | TC-M01-049 |
| T-044 | 实现 get_report_by_id | `get_report_by_id(report_id) → dict|None`：获取单条研报详情，不存在返回 None | 返回含 full_content 的完整详情（对齐 `10` §5.3） | TC-M01-050 |
| T-045 | 实现 delete_report | `delete_report(report_id) → bool`：删除研报记录，返回是否成功 | 删除后 get_report_by_id 返回 None（对齐 `10` §5.3） | TC-M01-051 |

### W5-S3 研报解析器

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 TC |
|--------|----------|----------|----------------|---------|
| T-046 | 实现 PDF 解析器 | 创建 `report_parser.py`：解析 PDF 文件，提取标题、评级、目标价、核心观点四要素；返回结构化字典 | PDF 解析成功率 ≥ 90%；四要素字段非空（对齐 `04` §6 准确率要求） | TC-M01-050 |
| T-047 | 实现 HTML 解析器 | 扩展 `report_parser.py`：解析 HTML 格式研报，提取同样四要素 | HTML 解析成功返回同结构字典（对齐 `09` §8） | TC-M01-051 |
| T-048 | 实现解析状态流转 | 文件上传后 status=`parsing`；解析成功→`completed`；解析失败→`failed`；更新 Storage | 状态枚举值正确（对齐 `10` §6 解析状态流转） | TC-M01-050 |

### W1-S3 路由层 — 研报 API

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 TC |
|--------|----------|----------|----------------|---------|
| T-049 | POST /reports 端点 | multipart/form-data：file(必填 PDF/HTML ≤10MB) + session_id(必填UUID)；校验格式→INVALID_FILE_FORMAT、大小→FILE_TOO_LARGE、session→INVALID_SESSION；调用解析器→写入 Storage；返回 201 + report_id/title/rating/target_price/core_views/parsed_at/status/traceId | 全部校验通过；响应含 8 字段（对齐 `09` §8） | TC-M01-050~053 |
| T-050 | GET /reports 端点 | 查询参数 keyword(可选 ≤100字符)/page(默认1)/page_size(默认20)；调用 `Storage.get_reports`；返回 200 + reports[]/total/page/page_size/traceId | 模糊搜索正确；分页字段完整（对齐 `09` §9） | TC-M01-054, 055 |
| T-051 | GET /reports/<id> 端点 | 路径参数 id；不存在→404 NOT_FOUND；返回 200 + 完整详情含 full_content/session_id/traceId | 9 个字段完整（对齐 `09` §10） | TC-M01-056 |
| T-052 | DELETE /reports/<id> 端点 | 路径参数 id；不存在→404 NOT_FOUND；返回 200 + deleted=true/report_id/traceId | 删除后 GET 返回 404（对齐 `09` §11） | TC-M01-057 |

### W4-S3 前端 — 研报上传与展示

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 FSD |
|--------|----------|----------|----------------|----------|
| T-053 | 实现研报上传按钮 | Header 区域上传按钮；点击弹出文件选择框限制 PDF/HTML；选择后调用 `POST /reports`；uploading 状态管理 | 上传中显示加载状态；成功后展示解析结果（对齐 `06` §2.2） | `06` §2.2 |
| T-054 | 实现研报列表展示 | 调用 `GET /reports` 展示研报卡片列表；显示 title/rating/target_price/parsed_at | 分页正确（对齐 `06` §4） | `06` §4 |
| T-055 | 实现研报模糊搜索 | 输入关键词调用 `GET /reports?keyword=xxx`；实时或防抖搜索 | 搜索结果与关键词匹配（对齐 `06` §4） | `06` §4 |
| T-056 | 实现研报详情查看 | 点击研报调用 `GET /reports/<id>`；展示完整内容含四要素 | full_content 完整渲染（对齐 `06` §4.2） | `06` §4.2 |

### W6-S3 测试 — 研报测试

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 TC |
|--------|----------|----------|----------------|---------|
| T-057 | 编写 Storage 研报单元测试 | TC-M01-048~051 共 4 条：create/get_reports/get_by_id/delete | 全部通过（对齐 `13` §3.5） | TC-M01-048~051 |
| T-058 | 编写研报 API 集成测试 | TC-M01-050~057 共 8 条：PDF上传、HTML上传、格式错误、文件过大、列表、搜索、详情、删除 | 全部通过（对齐 `13` §3.4） | TC-M01-050~057 |
| T-059 | 编写研报 API 契约测试 | TC-M01-058：研报相关响应 schema 验证 | 字段类型与 `09` §8~§11 一致（对齐 `13` §3.4） | TC-M01-058 |

---

## S4 — 发布准备（可演示：完整端到端 + 质量门禁 + 文档收口）

> **演示目标**：种子数据 ≥ 10 条下，主路径 + 历史 + 能力状态 3 分钟内演示完毕。
> **满足需求**：US-001~US-006 全部；需求-M1-001~013 全量验证
> **前置条件**：S1~S3 全部完成；演示数据目录可读写，种子数据 ≥ 10 条

### W6-S4 测试 — 全量回归 + E2E

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 TC |
|--------|----------|----------|----------------|---------|
| T-060 | E2E: 新建会话并提问 | TC-M01-070：新建会话 → 输入问题 → 获得回答 → 验证回答落库 | 全流程 3 分钟内完成（对齐 `04` §6 可演示标准） | TC-M01-070 |
| T-061 | E2E: 上传研报并解析 | TC-M01-071：上传 PDF 研报 → 解析成功 → 展示标题/评级/目标价/核心观点四要素 | 四要素完整展示（对齐 `04` §6 解析准确率） | TC-M01-071 |
| T-062 | E2E: 切换会话 | TC-M01-072：创建多个会话 → 切换会话 → 加载历史记录 → 上下文保持连续 | 切换无状态丢失（对齐 `04` §6 并发支持） | TC-M01-072 |
| T-063 | E2E: 模糊搜索研报 | TC-M01-073：输入关键词 → 模糊搜索 → 查看研报详情 | 搜索结果匹配、详情完整（对齐 `04` SC-04） | TC-M01-073 |
| T-064 | E2E: 删除会话级联 | TC-M01-074：删除会话 → 确认级联删除关联数据 | 关联 QARecord 一并清除（对齐需求-M1-010） | TC-M01-074 |
| T-065 | E2E: 降级场景 | TC-M01-075：无 API Key 时自动切换至 demo 模式 | answer_source='demo'，llm_used=False（对齐需求-M1-011） | TC-M01-075 |
| T-066 | 全量回归测试 | 运行 TC-M01-001~075 全部 45 条测试用例 | P0 用例 100% 通过；整体通过率 ≥ 95%（对齐 `13` §4 G-UNIT/G-INT） | 全量 TC |

### W4-S4 前端 — Polish

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 FSD |
|--------|----------|----------|----------------|----------|
| T-067 | UI 样式优化 | 响应式布局微调；Loading 动画；Markdown 渲染优化；复制按钮交互反馈 | 首屏加载 < 3000ms（对齐 `07` §1.1） | `06` 全文 |
| T-068 | 错误兜底与边界处理 | 网络超时提示；JSON 解析异常兜底；文件上传进度条 | 无白屏无未捕获异常（对齐 `06` §6） | `06` §6 |

### W7-S4 部署脚本

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 Spec |
|--------|----------|----------|----------------|-----------|
| T-069 | 编写一键启动脚本 | 创建 `start.bat`（Windows）和 `start.sh`（Linux/Mac）：启动 Flask 5000 + Vite 5173；自动创建 data 目录 | 双击/执行脚本后前后端均可访问（对齐 `08` §6） | `08` §6 |
| T-070 | 准备种子数据 | 在 `data/` 目录准备 ≥ 10 条种子数据：sessions.json + qa_records.json + reports.json | 启动后列表有数据可演示（对齐 `04` §6 种子数据要求） | `04` §6 |
| T-071 | 编写 .env.example | 列出所有环境变量：`IRA_COPAW_*_URL`、`DASHSCOPE_API_KEY` 等；注释说明用途 | 密钥不入代码仓库（对齐 `11` §1/`07` §4.1） | `11` §1 |

### 质量门禁验收

| 任务ID | 任务名称 | 具体内容 | DoD（验收标准） | 关联 Gate |
|--------|----------|----------|----------------|-----------|
| T-072 | G-LINT 代码格式检查 | `black --check` + `flake8` 通过 | 零警告（对齐 `13` §4 G-LINT） | G-LINT |
| T-073 | G-UNIT 单元测试门禁 | L1 Unit 测试通过率 100% | TC-M01-040~051 全绿（对齐 `13` §4 G-UNIT） | G-UNIT |
| T-074 | G-INT 集成测试门禁 | L2 Integration 测试通过率 ≥ 95%，P0 用例 100% | TC-M01-001~057 P0 全绿（对齐 `13` §4 G-INT） | G-INT |
| T-075 | G-CONTRACT 契约测试门禁 | L3 Contract 测试通过率 100% | TC-M01-006,025,026,033,058 全绿（对齐 `13` §4 G-CONTRACT） | G-CONTRACT |
| T-076 | G-COVERAGE 覆盖率检查 | `pytest --cov` 行覆盖率 ≥ 80% | 覆盖率报告输出（对齐 `13` §4 G-COVERAGE） | G-COVERAGE |
| T-077 | G-PERF 性能检查 | 问答 P95 延迟 < 5000ms；会话管理 < 500ms；列表查询 < 200ms | 性能指标达标（对齐 `07` §1.1） | G-PERF |

---

## 任务统计

| 阶段 | 任务数 | 涵盖 WBS |
|------|--------|----------|
| **S1** 会话管理 | 21 条（T-001 ~ T-021） | W1, W2, W4, W6 |
| **S2** 问答核心 | 20 条（T-022 ~ T-041） | W1, W2, W3, W4, W6 |
| **S3** 研报解析 | 18 条（T-042 ~ T-059） | W1, W2, W4, W5, W6 |
| **S4** 发布准备 | 18 条（T-060 ~ T-077） | W4, W6, W7 |
| **合计** | **77 条** | W1 ~ W7 全覆盖 |

### 关键路径

```
S1 会话管理（T-001~T-021）
    ↓ 依赖：Storage + 会话 API 完成
S2 问答核心（T-022~T-041）
    ↓ 依赖：Agent 降级链 + 问答 API 完成
S3 研报解析（T-042~T-059）
    ↓ 依赖：解析器 + 研报 API 完成
S4 发布准备（T-060~T-077）
    ↓ 全量回归 + E2E + 门禁
```

### TC 覆盖映射

| TC 范围 | 数量 | 对应任务 |
|---------|------|----------|
| TC-M01-001~006（问答 API） | 6 | T-038, T-039 |
| TC-M01-020~026（会话 API） | 7 | T-020, T-021 |
| TC-M01-030~033（记录 API） | 4 | T-040, T-041 |
| TC-M01-040~051（Storage） | 12 | T-019, T-037, T-057 |
| TC-M01-050~058（研报 API） | 9 | T-058, T-059 |
| TC-M01-070~075（E2E） | 6 | T-060~T-065 |
| **合计** | **45 条** | 全部有对应实现任务 |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 基于 01~14 Spec 文档生成，77 条任务全链路覆盖 |
