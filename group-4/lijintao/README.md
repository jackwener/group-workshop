# 投研问答助手 (M1-QA)

AI 驱动的投研问答助手，支持会话管理、流式响应、LLM 降级策略。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 16 + React 19 + TypeScript + Tailwind CSS + Zustand |
| 后端 | FastAPI + SQLAlchemy + SQLite |
| LLM | DashScope (qwen-plus) / Mock Provider 降级 |

## 项目结构

```
lijintao/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心配置
│   │   ├── db/           # 数据库
│   │   ├── llm/          # LLM 提供商
│   │   ├── models/       # 数据模型
│   │   ├── schemas/      # Pydantic 模式
│   │   ├── services/     # 业务逻辑
│   │   ├── config.py     # 配置管理
│   │   └── main.py       # 入口文件
│   ├── data/             # SQLite 数据库文件
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js App Router
│   │   ├── components/   # React 组件
│   │   ├── hooks/        # 自定义 Hooks
│   │   ├── lib/          # 工具函数
│   │   ├── store/        # Zustand 状态
│   │   └── types/        # TypeScript 类型
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .env
```

## 先决条件

- Python 3.12+
- Node.js 20+
- npm 或 pnpm
- Docker & Docker Compose（可选）

## 本地开发启动流程

### 1. 克隆项目并进入目录

```bash
cd group-4/lijintao
```

### 2. 配置环境变量

确保 `.env` 文件存在（已包含在项目中）：

```env
DATABASE_URL=sqlite:///./data/app.db
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus
APP_ENV=development
```

### 3. 启动后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 创建数据目录
mkdir -p data

# 启动开发服务器
uvicorn app.main:app --reload --port 8000
```

后端启动后：
- API 地址: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 4. 启动前端（新终端窗口）

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端启动后：
- 访问地址: http://localhost:3000

## Docker 启动流程

### 一键启动（推荐）

```bash
cd group-4/lijintao

# 构建并启动所有服务
docker-compose up --build

# 后台运行
docker-compose up -d --build
```

启动后：
- 前端: http://localhost:3000
- 后端: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 停止服务

```bash
docker-compose down

# 同时删除数据卷
docker-compose down -v
```

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | 数据库连接地址 | `sqlite:///./data/app.db` |
| `LLM_PROVIDER` | LLM 提供商 (`openai`/`mock`) | `mock` |
| `OPENAI_API_KEY` | DashScope API Key | - |
| `OPENAI_BASE_URL` | API 基础地址 | DashScope 兼容地址 |
| `OPENAI_MODEL` | 模型名称 | `qwen-plus` |
| `APP_ENV` | 运行环境 | `development` |

> **注意**: 当 `LLM_PROVIDER=mock` 时，系统使用模拟响应，无需配置 API Key。

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health` | 健康检查 |
| GET | `/api/v1/sessions` | 获取会话列表 |
| POST | `/api/v1/sessions` | 创建新会话 |
| GET | `/api/v1/sessions/{id}` | 获取会话详情 |
| DELETE | `/api/v1/sessions/{id}` | 删除会话 |
| GET | `/api/v1/sessions/{id}/messages` | 获取会话消息列表 |
| POST | `/api/v1/sessions/{id}/messages` | 发送消息（SSE 流式响应） |

## 功能特性

- **会话管理**: 创建、切换、删除会话
- **流式响应**: 支持 SSE 实时流式输出
- **LLM 降级**: API 不可用时自动降级到 Mock 模式
- **数据持久化**: SQLite 本地存储，Docker 卷持久化
- **响应式 UI**: 适配桌面和移动端

## 常见问题

**Q: 后端启动报错 `ModuleNotFoundError`？**

```bash
# 确保在虚拟环境中并安装依赖
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

**Q: 前端无法连接后端？**

检查 `.env` 中的 `NEXT_PUBLIC_API_URL` 是否正确设置为 `http://localhost:8000`。

**Q: Docker 构建失败？**

```bash
# 清理后重新构建
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```
