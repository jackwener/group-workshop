# 投研问答助手

> 模块编号: M1-QA  
> 基于 Flask + React 的智能投研问答系统

## 项目简介

投研问答助手是一个面向投研分析师的智能问答系统，支持：

- **会话管理**：创建、列表、删除会话
- **智能问答**：支持三级降级策略（CoPaw → 百炼 → Demo）
- **研报对比**：对比不同券商对同一公司的研报观点
- **历史记录**：自动沉淀问答历史，支持随时回看

## 技术架构

```
┌─────────────────────────────────┐
│       用户浏览器 React SPA       │
│       http://localhost:5173     │
└──────────────┬──────────────────┘
               │ HTTP  /api/v1/agent/*
               ▼
┌─────────────────────────────────┐
│     Flask Backend (WSGI)        │
│     http://localhost:5000       │
│  ┌────────────────────────────┐ │
│  │  agent_bp — 6 个 API 端点  │ │
│  │    ↓          ↓         ↓  │ │
│  │ CoPawAgent  Storage  _ok() │ │
│  └────┬──────────┬────────────┘ │
│       ▼          ▼              │
│  ┌────────┐ ┌──────────┐       │
│  │ LLM 层 │ │ 文件系统  │       │
│  │CoPaw   │ │ ./data/  │       │
│  │百炼    │ │ *.json   │       │
│  │Demo    │ └──────────┘       │
│  └────────┘                    │
└─────────────────────────────────┘
```

### 后端技术栈

- **Web 框架**: Flask 2.3+
- **数据存储**: JSON 文件存储
- **HTTP 客户端**: requests
- **测试**: pytest

### 前端技术栈

- **UI 框架**: React 18+
- **构建工具**: Vite 5+
- **状态管理**: React Hooks (useState, useEffect)
- **HTTP 客户端**: 原生 fetch API
- **样式**: CSS Modules / 内联样式

## 快速开始

### 1. 克隆项目

```bash
cd touyanzhushou
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 LLM 服务（可选）

# 启动服务
python wsgi.py
```

后端服务将在 http://localhost:5000 启动

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

## 配置说明

### 环境变量

复制 `backend/.env.example` 为 `backend/.env`，根据需要配置：

```bash
# Flask 配置
FLASK_ENV=development
FLASK_DEBUG=1

# CoPaw 配置（可选）
IRA_COPAW_API_URL=https://your-copaw-api.com
IRA_COPAW_API_KEY=your-api-key

# 百炼配置（可选）
DASHSCOPE_API_KEY=your-dashscope-key
DASHSCOPE_MODEL=qwen-turbo

# 数据存储目录
DATA_DIR=./data
```

### 三级降级策略

系统支持三级降级，确保高可用：

1. **CoPaw**: 内部 LLM 服务（需配置 API URL 和 Key）
2. **百炼**: 阿里云 DashScope 服务（需配置 API Key）
3. **Demo**: 离线演示模式（无需配置，始终可用）

## API 文档

### 端点列表

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/agent/capabilities` | GET | 能力探测 |
| `/api/v1/agent/ask` | POST | 问答提交 |
| `/api/v1/agent/sessions` | GET | 会话列表 |
| `/api/v1/agent/sessions` | POST | 新建会话 |
| `/api/v1/agent/sessions/<id>` | DELETE | 删除会话 |
| `/api/v1/agent/sessions/<id>/records` | GET | 问答记录 |

### 错误码

| HTTP | error.code | 说明 |
|------|-----------|------|
| 400 | `EMPTY_QUERY` | query 为空 |
| 400 | `INVALID_QUERY` | query 超 500 字符或缺少 session_id |
| 404 | `SESSION_NOT_FOUND` | 会话不存在 |
| 408 | `TIMEOUT_ERROR` | 请求超时 |
| 429 | `RATE_LIMIT_ERROR` | 请求过于频繁 |
| 500 | `UPSTREAM_ERROR` | 服务内部异常 |

## 项目结构

```
touyanzhushou/
├── backend/                    # 后端代码
│   ├── app/                   # 应用代码
│   │   ├── __init__.py        # 应用工厂
│   │   ├── routes.py          # API 路由
│   │   ├── storage.py         # 数据存储层
│   │   └── agent.py           # LLM Agent 编排
│   ├── tests/                 # 测试代码
│   │   ├── conftest.py        # 测试配置
│   │   ├── test_storage.py    # Storage 测试
│   │   └── test_api.py        # API 测试
│   ├── data/                  # 数据文件（自动生成）
│   ├── wsgi.py                # WSGI 入口
│   ├── requirements.txt       # 依赖列表
│   └── .env.example           # 环境变量示例
│
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── components/        # React 组件
│   │   │   ├── Header.jsx     # 头部组件
│   │   │   ├── Sidebar.jsx    # 侧边栏组件
│   │   │   ├── ChatArea.jsx   # 聊天区域
│   │   │   ├── InputArea.jsx  # 输入区域
│   │   │   └── Toast.jsx      # 提示组件
│   │   ├── hooks/             # 自定义 Hooks
│   │   │   ├── useApi.js      # API 调用
│   │   │   └── useToast.js    # Toast 提示
│   │   ├── App.jsx            # 主应用组件
│   │   ├── main.jsx           # 入口文件
│   │   ├── index.css          # 全局样式
│   │   └── App.css            # 应用样式
│   ├── public/                # 静态资源
│   ├── index.html             # HTML 模板
│   ├── package.json           # 依赖配置
│   └── vite.config.js         # Vite 配置
│
└── README.md                   # 项目文档
```

## 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/test_storage.py
pytest tests/test_api.py
```

## 开发计划

基于 [tasks.md](./spec/tasks.md) 的开发任务清单：

| 阶段 | 内容 | 状态 |
|------|------|------|
| S1 | 会话管理基础 | ✅ 完成 |
| S2 | 问答核心功能 | ✅ 完成 |
| S3 | 历史记录与研报对比 | ✅ 完成 |
| S4 | 发布准备 | 🔄 进行中 |

## 参考文档

- [03-立项提案与范围说明](./spec/03-立项提案与范围说明.md)
- [04-产品需求说明](./spec/04-产品需求说明.md)
- [05-用户故事与验收标准](./spec/05-用户故事与验收标准.md)
- [06-功能规格说明](./spec/06-功能规格说明.md)
- [08-系统架构与技术选型](./spec/08-系统架构与技术选型.md)
- [09-API接口规格](./spec/09-API接口规格.md)
- [10-数据模型与存储规格](./spec/10-数据模型与存储规格.md)

## License

MIT
