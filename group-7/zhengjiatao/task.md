# 投研问答助手 - Qoder开发任务清单

> 基于规格文档拆分的可执行任务，前端基于React，后端基于Python Flask

---

## 项目结构

```
project/
├── backend/                 # Flask后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   └── agent_bp.py      # W1: 路由实现
│   │   ├── services/
│   │   │   ├── agent.py         # W3: Agent编排
│   │   │   ├── storage.py       # W2: 存储层
│   │   │   ├── copaw_bridge.py  # W5: CoPaw Provider
│   │   │   └── bailian_qa.py    # W5: 百炼 Provider
│   │   └── utils/
│   ├── data/                    # JSON数据文件
│   ├── tests/
│   ├── .env
│   ├── requirements.txt
│   └── wsgi.py
│
└── frontend/                # React前端
    ├── src/
    │   ├── components/          # W4: 前端视图组件
    │   │   ├── Header.jsx       # 能力状态芯片
    │   │   ├── Sidebar.jsx      # 会话管理侧栏
    │   │   ├── ChatArea.jsx     # 主内容区
    │   │   ├── InputArea.jsx    # 输入区域
    │   │   └── RecordCard.jsx   # 问答记录卡片
    │   ├── hooks/
    │   ├── services/
    │   │   └── api.js           # API调用封装
    │   ├── App.jsx
    │   └── main.jsx
    ├── package.json
    └── vite.config.js
```

---

## Sprint 1: 会话管理 (S1)

### 后端任务

#### S1-B1: 项目初始化与基础架构
- **优先级**: P0
- **预估工时**: 2h
- **验收标准**:
  - [ ] 创建Flask项目结构
  - [ ] 配置requirements.txt (flask, flask-cors, python-dotenv)
  - [ ] 创建基础wsgi.py启动文件
  - [ ] 配置.env模板文件

#### S1-B2: Storage层实现 - Session管理 (W2)
- **优先级**: P0
- **预估工时**: 3h
- **依赖**: S1-B1
- **验收标准**:
  - [ ] 实现`create_session(session_id, title)`方法
  - [ ] 实现`get_sessions()`方法，返回按updated_at倒序排列的列表
  - [ ] 实现`delete_session(session_id)`方法，支持级联删除
  - [ ] 实现`update_session(session_id, updates)`方法
  - [ ] JSON文件存储实现，UTF-8编码，2空格缩进
  - [ ] 数据模型对齐`10-数据模型与存储规格.md` §3 Session实体

#### S1-B3: 路由实现 - Session API (W1)
- **优先级**: P0
- **预估工时**: 3h
- **依赖**: S1-B2
- **验收标准**:
  - [ ] `GET /api/v1/agent/sessions` - 会话列表
  - [ ] `POST /api/v1/agent/sessions` - 新建会话
  - [ ] `DELETE /api/v1/agent/sessions/<id>` - 删除会话
  - [ ] 参数校验与错误码处理（对齐`09-API接口规格.md` §2错误响应）
  - [ ] 统一响应格式包含traceId

### 前端任务

#### S1-F1: React项目初始化
- **优先级**: P0
- **预估工时**: 1h
- **验收标准**:
  - [ ] 使用Vite创建React项目
  - [ ] 配置package.json依赖
  - [ ] 配置开发代理（vite.config.js proxy到localhost:5000）

#### S1-F2: 前端基础组件与API封装
- **优先级**: P0
- **预估工时**: 2h
- **依赖**: S1-F1
- **验收标准**:
  - [ ] 创建api.js封装fetch调用
  - [ ] 实现Session相关API：getSessions, createSession, deleteSession
  - [ ] 统一错误处理

#### S1-F3: Sidebar组件实现 (W4)
- **优先级**: P0
- **预估工时**: 3h
- **依赖**: S1-F2, S1-B3
- **验收标准**:
  - [ ] 会话列表展示（对齐`06-功能规格说明.md` §3）
  - [ ] "+ 新建"按钮功能
  - [ ] 删除会话按钮（带确认弹窗）
  - [ ] 选中会话高亮显示
  - [ ] 响应式样式（CSS Modules）

#### S1-F4: Header组件实现
- **优先级**: P0
- **预估工时**: 1h
- **依赖**: S1-F1
- **验收标准**:
  - [ ] 应用标题展示
  - [ ] 预留能力状态芯片位置（S4实现）

---

## Sprint 2: 问答核心 (S2)

### 后端任务

#### S2-B1: Storage层扩展 - QARecord管理 (W2)
- **优先级**: P0
- **预估工时**: 2h
- **依赖**: S1-B2
- **验收标准**:
  - [ ] 实现`add_record(session_id, query, answer, ...)`方法
  - [ ] 实现`get_records_by_session(session_id)`方法
  - [ ] 实现`delete_records_by_session(session_id)`方法
  - [ ] query_count自动自增逻辑
  - [ ] 首次问答自动命名逻辑（query前20字）
  - [ ] 数据模型对齐`10-数据模型与存储规格.md` §4 QARecord实体

#### S2-B2: Provider层实现 - Demo模式 (W5)
- **优先级**: P0
- **预估工时**: 1h
- **依赖**: S2-B1
- **验收标准**:
  - [ ] 实现Demo Provider，纯字符串拼接返回
  - [ ] 返回格式包含answer, llm_used=false, model=null, answer_source="demo"

#### S2-B3: Provider层实现 - CoPaw桥接 (W5)
- **优先级**: P0
- **预估工时**: 2h
- **依赖**: S2-B2
- **验收标准**:
  - [ ] 实现copaw_bridge.py
  - [ ] 支持环境变量配置IRA_COPAW_*_URL
  - [ ] 20秒超时设置
  - [ ] 错误时返回None静默降级
  - [ ] 返回格式包含answer_source="copaw", llm_used=true

#### S2-B4: Provider层实现 - 百炼接口 (W5)
- **优先级**: P0
- **预估工时**: 2h
- **依赖**: S2-B2
- **验收标准**:
  - [ ] 实现bailian_qa.py
  - [ ] 支持环境变量配置DASHSCOPE_API_KEY
  - [ ] 120秒超时设置
  - [ ] 多类错误码区分
  - [ ] 返回格式包含answer_source="bailian", llm_used=true

#### S2-B5: Agent编排层实现 (W3)
- **优先级**: P0
- **预估工时**: 3h
- **依赖**: S2-B3, S2-B4
- **验收标准**:
  - [ ] 实现三级降级编排：CoPaw → 百炼 → Demo
  - [ ] 响应时间计算（response_time_ms）
  - [ ] 结果组装与字段填充
  - [ ] 降级链路对齐`08-系统架构与技术选型.md` §4

#### S2-B6: 路由实现 - Ask API (W1)
- **优先级**: P0
- **预估工时**: 2h
- **依赖**: S2-B5
- **验收标准**:
  - [ ] `POST /api/v1/agent/ask` - 问答提交
  - [ ] 参数校验：query非空、1-500字符、session_id有效
  - [ ] 流式响应支持（SSE或chunked）
  - [ ] 错误码：EMPTY_QUERY, INVALID_QUERY, SESSION_NOT_FOUND

### 前端任务

#### S2-F1: API扩展 - Ask接口
- **优先级**: P0
- **预估工时**: 1h
- **依赖**: S1-F2
- **验收标准**:
  - [ ] 实现ask API调用
  - [ ] 支持流式响应处理

#### S2-F2: InputArea组件实现 (W4)
- **优先级**: P0
- **预估工时**: 2h
- **依赖**: S2-F1
- **验收标准**:
  - [ ] textarea输入框（3行，placeholder"请输入您的问题..."）
  - [ ] 发送按钮（loading时disabled，显示"发送中..."）
  - [ ] 清空按钮
  - [ ] 输入长度校验（1-500字符）
  - [ ] 对齐`06-功能规格说明.md` §5

#### S2-F3: ChatArea组件实现 - 空状态与常见问题 (W4)
- **优先级**: P0
- **预估工时**: 2h
- **依赖**: S2-F2
- **验收标准**:
  - [ ] 空状态显示"请创建或选择一个会话开始"
  - [ ] 常见问题网格展示（预设问题如"分析某行业趋势"）
  - [ ] 点击问题自动填入输入框
  - [ ] 对齐`06-功能规格说明.md` §4 状态A、B

#### S2-F4: ChatArea组件实现 - 对话历史与流式展示 (W4)
- **优先级**: P0
- **预估工时**: 3h
- **依赖**: S2-F3
- **验收标准**:
  - [ ] 问答卡片列表展示
  - [ ] 用户问题（上）、AI回答（下）布局
  - [ ] 来源标签显示（CoPaw/百炼/离线演示）
  - [ ] 时间戳显示
  - [ ] 流式响应实时显示
  - [ ] 对齐`06-功能规格说明.md` §4 状态C

#### S2-F5: RecordCard组件实现
- **优先级**: P0
- **预估工时**: 2h
- **依赖**: S2-F4
- **验收标准**:
  - [ ] 单条问答记录展示组件
  - [ ] 来源标签样式（绿色/蓝色/灰色）
  - [ ] 复制按钮功能（复制query+answer）
  - [ ] "已复制"提示

---

## Sprint 3: 历史记录 (S3)

### 后端任务

#### S3-B1: 路由实现 - Records与Export API (W1)
- **优先级**: P0
- **预估工时**: 2h
- **依赖**: S2-B1
- **验收标准**:
  - [ ] `GET /api/v1/agent/sessions/<id>/records` - 问答记录列表
  - [ ] `GET /api/v1/agent/sessions/<id>/export` - 导出会话记录
  - [ ] 支持format参数（json/txt）
  - [ ] 返回临时下载链接（5分钟有效）
  - [ ] 错误码：EMPTY_SESSION, INVALID_FORMAT

### 前端任务

#### S3-F1: API扩展 - Records与Export
- **优先级**: P0
- **预估工时**: 1h
- **依赖**: S3-B1
- **验收标准**:
  - [ ] 实现getRecordsBySession API
  - [ ] 实现exportSession API

#### S3-F2: RecordCard增强 - 复制导出功能
- **优先级**: P0
- **预估工时**: 2h
- **依赖**: S3-F1
- **验收标准**:
  - [ ] 单条记录复制功能（AC-003-02）
  - [ ] 整个会话导出功能（JSON/TXT格式选择）
  - [ ] 下载文件功能
  - [ ] 对齐`06-功能规格说明.md` §4.2

#### S3-F3: Sidebar增强 - 自动命名
- **优先级**: P0
- **预估工时**: 1h
- **依赖**: S3-F2
- **验收标准**:
  - [ ] 首次问答后会话标题自动更新为query前20字
  - [ ] 仅query_count从0→1时触发
  - [ ] 对齐AC-003-04

---

## Sprint 4: 运维监控 (S4)

### 后端任务

#### S4-B1: 路由实现 - Capabilities API (W1)
- **优先级**: P1
- **预估工时**: 1h
- **依赖**: S2-B3, S2-B4
- **验收标准**:
  - [ ] `GET /api/v1/agent/capabilities` - 能力探测
  - [ ] 返回copaw_configured, bailian_configured状态
  - [ ] 对齐`09-API接口规格.md` §1

#### S4-B2: Agent层增强 - 监控集成 (W3)
- **优先级**: P1
- **预估工时**: 2h
- **依赖**: S4-B1
- **验收标准**:
  - [ ] 系统资源监控（CPU、Memory）
  - [ ] 实时或定时记录状态
  - [ ] 对齐AC-004-02

### 前端任务

#### S4-F1: API扩展 - Capabilities
- **优先级**: P1
- **预估工时**: 0.5h
- **依赖**: S4-B1
- **验收标准**:
  - [ ] 实现getCapabilities API

#### S4-F2: Header组件增强 - 能力状态芯片 (W4)
- **优先级**: P1
- **预估工时**: 1.5h
- **依赖**: S4-F1
- **验收标准**:
  - [ ] CoPaw已配置时显示"CoPaw 桥接"芯片
  - [ ] 百炼已配置时显示"百炼 · {model}"芯片
  - [ ] 均未配置时显示"离线演示"芯片
  - [ ] 不同状态不同颜色样式
  - [ ] 对齐`06-功能规格说明.md` §2.1

#### S4-F3: 监控面板组件
- **优先级**: P1
- **预估工时**: 2h
- **依赖**: S4-B2
- **验收标准**:
  - [ ] 系统健康状态显示
  - [ ] CPU/Memory资源监控图表
  - [ ] 对齐AC-004-01, AC-004-02

---

## 测试任务 (W6)

### 单元测试

#### T1: Storage层单元测试
- **优先级**: P0
- **预估工时**: 3h
- **依赖**: S1-B2, S2-B1
- **验收标准**:
  - [ ] Session CRUD测试
  - [ ] QARecord CRUD测试
  - [ ] 级联删除测试
  - [ ] 首次命名逻辑测试

#### T2: Agent层单元测试
- **优先级**: P0
- **预估工时**: 2h
- **依赖**: S2-B5
- **验收标准**:
  - [ ] 三级降级逻辑测试
  - [ ] 降级触发条件测试
  - [ ] 响应时间计算测试

#### T3: Provider层单元测试
- **优先级**: P0
- **预估工时**: 2h
- **依赖**: S2-B3, S2-B4
- **验收标准**:
  - [ ] CoPaw桥接测试（含mock）
  - [ ] 百炼接口测试（含mock）
  - [ ] Demo模式测试

### API集成测试

#### T4: API端点测试
- **优先级**: P0
- **预估工时**: 3h
- **依赖**: S1-B3, S2-B6, S3-B1, S4-B1
- **验收标准**:
  - [ ] 所有7个端点测试覆盖
  - [ ] 参数校验测试
  - [ ] 错误码测试
  - [ ] 对齐`09-API接口规格.md` §9参数校验规则

### 前端测试

#### T5: 组件单元测试
- **优先级**: P1
- **预估工时**: 3h
- **依赖**: S1-F3, S2-F2, S2-F4, S4-F2
- **验收标准**:
  - [ ] Sidebar组件测试
  - [ ] ChatArea组件测试
  - [ ] InputArea组件测试
  - [ ] RecordCard组件测试

#### T6: E2E测试
- **优先级**: P1
- **预估工时**: 4h
- **依赖**: T4, T5
- **验收标准**:
  - [ ] 主路径端到端测试
  - [ ] 会话管理流程测试
  - [ ] 问答提交流程测试
  - [ ] 历史记录流程测试

---

## 依赖关系图

```
S1-B1 → S1-B2 → S1-B3
  ↓       ↓       ↓
S1-F1 → S1-F2 → S1-F3/S1-F4

S1-B2 → S2-B1 → S2-B2 → S2-B3/S2-B4 → S2-B5 → S2-B6
                              ↓
S1-F2 → S2-F1 → S2-F2 → S2-F3 → S2-F4 → S2-F5

S2-B1 → S3-B1
S2-F5 → S3-F1 → S3-F2 → S3-F3

S2-B3/S2-B4 → S4-B1 → S4-B2
S3-F3 → S4-F1 → S4-F2 → S4-F3
```

---

## 里程碑检查点

| 里程碑 | 检查项 | 验收标准 |
|--------|--------|----------|
| **S1完成** | 会话管理 | 可创建/查看/删除会话，会话数据隔离，API测试通过 |
| **S2完成** | 问答核心 | 可向AI提问并获得流式回答，支持三级降级，P0用例通过 |
| **S3完成** | 历史记录 | 可查看历史问答记录，支持复制导出，级联删除正常 |
| **S4完成** | 运维监控 | 可查看系统健康状态和资源监控，集成测试通过 |

---

## 技术栈确认

### 后端
- **框架**: Flask (Python)
- **依赖**: flask, flask-cors, python-dotenv
- **存储**: JSON文件（sessions.json, qa_records.json）
- **外部API**: CoPaw, 百炼(DashScope)

### 前端
- **框架**: React 18+ (Hooks)
- **构建**: Vite 5+
- **状态管理**: useState + useEffect
- **HTTP**: fetch API
- **样式**: CSS Modules

---

## 附录：API端点清单

| # | 端点 | 方法 | Sprint |
|---|------|------|--------|
| 1 | `/api/v1/agent/capabilities` | GET | S4 |
| 2 | `/api/v1/agent/ask` | POST | S2 |
| 3 | `/api/v1/agent/sessions` | GET | S1 |
| 4 | `/api/v1/agent/sessions` | POST | S1 |
| 5 | `/api/v1/agent/sessions/<id>` | DELETE | S1 |
| 6 | `/api/v1/agent/sessions/<id>/records` | GET | S3 |
| 7 | `/api/v1/agent/sessions/<id>/export` | GET | S3 |

---

*文档版本: v1.0*  
*创建日期: 2025-04-14*  
*基于规格文档: 04-产品需求说明.md, 05-用户故事与验收标准.md, 06-功能规格说明.md, 08-系统架构与技术选型.md, 09-API接口规格.md, 10-数据模型与存储规格.md, 12-实施计划与里程碑.md*
