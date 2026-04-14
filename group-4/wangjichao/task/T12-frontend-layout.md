# T12 — 前端：项目初始化 + 布局框架 + Header

| 项 | 值 |
|---|---|
| 任务ID | T12 |
| 所属 WBS | W4 前端视图 |
| 里程碑 | **S1** 会话管理 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | T01（项目脚手架）, T04（capabilities 端点） |
| 并行关系 | 与 T02-T11 并行；完成后解锁 T13, T14 |
| 产出文件 | `frontend/src/App.jsx`, `frontend/src/components/Header.jsx` |

## 1. 任务目标

使用 React + Vite + Tailwind CSS 搭建前端整体布局框架（Header + Sidebar + Main），实现 Header 区域的能力状态芯片。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `06` FSD | §1 | 总体布局：Header + Sidebar + Main（多标签页） |
| `06` FSD | §2 | Header 区域：标题 + 能力状态芯片 |
| `06` FSD | §2.1 | 芯片逻辑：copaw_configured / bailian_configured |
| `06` FSD | §7 | 9 个 State 变量定义 |
| `08` 架构 | §3 | React 18 + Vite 5 + Tailwind CSS + Headless UI |

## 3. 布局结构（对齐 `06` §1）

```
┌──────────────────────────────────────────────────────┐
│  Header: 标题 + [能力状态芯片] + [用户信息]            │
├────────────┬─────────────────────────────────────────┤
│  Sidebar   │  Main（多标签页）                        │
│  （T13实现）│  [会话] [研报] [对比]                    │
│            │  （T13/T14 实现）                        │
└────────────┴─────────────────────────────────────────┘
```

## 4. State 变量初始化（对齐 `06` §7）

| State 变量 | 类型 | 初始值 | 用途 |
|------------|------|--------|------|
| `sessions` | `Session[]` | `[]` | 会话列表 |
| `currentSession` | `Session\|null` | `null` | 当前选中会话 |
| `reports` | `Report[]` | `[]` | 研报列表 |
| `currentReport` | `Report\|null` | `null` | 当前查看研报 |
| `qaRecords` | `QARecord[]` | `[]` | 当前会话的问答记录 |
| `activeTab` | `string` | `'session'` | 当前激活标签页 |
| `isLoading` | `boolean` | `false` | 加载状态 |
| `inputValue` | `string` | `''` | 输入框内容 |
| `capabilities` | `object` | `{}` | LLM 能力状态 |

## 5. 能力状态芯片逻辑（对齐 `06` §2.1）

| 条件 | 芯片显示 | 样式 |
|------|----------|------|
| `copaw_configured = true` | CoPaw 桥接 | 绿色/蓝色标签 |
| `bailian_configured = true` | 百炼 · {model} | 绿色/蓝色标签 |
| `bailian_configured = false` | 离线演示 | 灰色标签 |

页面加载时调用 `GET /api/v1/agent/capabilities` 获取能力状态。

## 6. 验收标准（AC）

| # | 验收条件 |
|---|---------|
| AC-01 | 页面三栏布局正确渲染：Header + Sidebar + Main |
| AC-02 | Header 显示系统标题 "研报聚合分析助手" |
| AC-03 | 页面加载时调用 GET /capabilities |
| AC-04 | 根据 capabilities 正确渲染能力芯片 |
| AC-05 | 多标签页切换功能（会话/研报/对比） |
| AC-06 | 9 个 State 变量均已在 App 中声明 |
| AC-07 | Tailwind CSS 样式正常加载 |
