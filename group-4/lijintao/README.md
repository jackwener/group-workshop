# 投研问答助手 (M1-QA)

AI 驱动的投研问答助手，支持会话管理、流式响应、LLM 降级策略。

## 技术栈

- **前端**: Next.js 15 + TypeScript + Tailwind CSS + Zustand
- **后端**: FastAPI + SQLAlchemy + SQLite
- **LLM**: DashScope (qwen-plus) + Mock Provider 降级

## 快速启动

### Docker 方式（推荐）
```bash
docker-compose up --build
```
- 前端: http://localhost:3000
- 后端: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 本地开发

**后端**:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**前端**:
```bash
cd frontend
npm install
npm run dev
```

## 环境变量

复制 `.env` 文件并配置：
- `OPENAI_API_KEY` - DashScope API Key
- `OPENAI_BASE_URL` - DashScope API 地址
- `OPENAI_MODEL` - 模型名称（默认 qwen-plus）
- `LLM_PROVIDER` - LLM 提供商（openai/mock）

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/health | 健康检查 |
| GET | /api/v1/sessions | 会话列表 |
| POST | /api/v1/sessions | 创建会话 |
| GET | /api/v1/sessions/{id} | 会话详情 |
| DELETE | /api/v1/sessions/{id} | 删除会话 |
| GET | /api/v1/sessions/{id}/messages | 获取消息 |
| POST | /api/v1/sessions/{id}/messages | 发送消息(SSE) |
