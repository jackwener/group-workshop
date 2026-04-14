# 投研问答助手 (Research QA Assistant)

基于 Flask + React 的智能投研问答系统，支持会话管理、问答对话、研报管理和导出功能。

## 项目结构

```
zhaoyunjian/
├── backend/          # Flask后端
│   ├── app/
│   │   ├── api/v1/   # API路由
│   │   ├── core/     # 核心配置和错误处理
│   │   └── services/ # 业务逻辑和存储层
│   ├── tests/        # 测试用例
│   ├── data/         # 数据存储目录
│   ├── requirements.txt
│   └── run.py        # 启动入口
├── frontend/         # React前端
│   ├── src/
│   │   ├── components/  # UI组件
│   │   └── services/    # API客户端
│   ├── package.json
│   └── vite.config.js
└── spec/             # 需求规格文档
```

## 功能特性

### Sprint 1: 会话管理 (已完成)
- ✅ Flask项目结构初始化
- ✅ Storage层实现（JSON文件存储）
- ✅ 会话管理API（创建、列表、删除）
- ✅ 统一错误响应和traceId注入
- ✅ React + Vite前端项目初始化
- ✅ 页面布局组件（Header、Sidebar、MainContent、InputArea）
- ✅ HTTP客户端封装
- ✅ pytest测试框架

### Sprint 2: 问答核心 (基础实现)
- ✅ 问答提交API（三级降级：CoPaw → 百炼 → Demo）
- ✅ 问答记录查询
- ✅ 前端三态渲染（空状态/常见问题/对话历史）

### Sprint 3: 研报管理 (基础实现)
- ✅ 研报上传/列表/删除API
- ✅ 研报分析接口（异步任务框架预留）

### Sprint 4: 高级功能 (基础实现)
- ✅ 健康检查API
- ✅ 导出功能API框架

## 快速开始

### 后端启动

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选）
copy .env.example .env

# 启动服务
python run.py
```

后端服务将在 http://localhost:5000 启动

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动

### 运行测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_storage.py
pytest tests/test_api.py
```

## API端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/agent/capabilities` | GET | 能力探测 |
| `/api/v1/agent/sessions` | GET | 会话列表 |
| `/api/v1/agent/sessions` | POST | 新建会话 |
| `/api/v1/agent/sessions/<id>` | DELETE | 删除会话 |
| `/api/v1/agent/sessions/<id>/records` | GET | 问答记录 |
| `/api/v1/agent/ask` | POST | 问答提交 |
| `/api/v1/agent/reports` | GET | 研报列表 |
| `/api/v1/agent/reports` | POST | 上传研报 |
| `/api/v1/agent/reports/<id>` | DELETE | 删除研报 |
| `/api/v1/agent/reports/<id>/analyze` | POST | 分析研报 |
| `/api/v1/agent/health` | GET | 健康检查 |
| `/api/v1/agent/export` | POST | 导出对比结果 |

## 技术栈

### 后端
- **框架**: Flask 3.0.3
- **存储**: JSON文件存储
- **测试**: pytest
- **CORS**: flask-cors

### 前端
- **框架**: React 18
- **构建工具**: Vite
- **样式**: CSS Modules
- **HTTP客户端**: Fetch API

## 配置说明

### 环境变量 (.env)

```env
# Flask配置
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
PORT=5000

# 数据目录
DATA_DIR=./data

# CoPaw配置（可选）
COPAW_API_KEY=
COPAW_API_URL=

# 百炼DashScope配置（可选）
BAILIAN_API_KEY=
BAILIAN_MODEL=qwen-max

# 上传文件配置
MAX_CONTENT_LENGTH=52428800
UPLOAD_FOLDER=./data/uploads
```

## 开发规范

### 代码风格
- Python: 遵循PEP 8规范
- JavaScript: 使用ESLint规则

### 提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- test: 测试相关
- refactor: 代码重构

## 测试覆盖

### Storage层单元测试 (TC-M01-050~063)
- ✅ 会话管理（创建、查询、更新、删除）
- ✅ 问答记录管理（添加、查询、删除）
- ✅ 级联删除验证

### API集成测试 (TC-M01-020~084)
- ✅ 能力探测API
- ✅ 会话管理API
- ✅ 问答提交API
- ✅ 健康检查API

## 许可证

MIT License
