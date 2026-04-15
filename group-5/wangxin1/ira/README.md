# 投研问答助手 (IRA)

基于 Flask + React 的智能投研问答系统，支持三级降级策略（CoPaw → 百炼 → Demo）。

## 项目结构

```
ira/
├── backend/                 # Flask 后端
│   ├── app.py              # 应用入口
│   ├── storage.py          # JSON 文件存储层
│   ├── agent.py            # Agent 编排（三级降级）
│   ├── copaw_bridge.py     # CoPaw 桥接
│   ├── bailian_qa.py       # 百炼 DashScope 集成
│   ├── blueprints/
│   │   └── agent_bp.py     # API 路由
│   ├── data/               # 数据目录
│   ├── tests/              # 测试文件
│   ├── requirements.txt    # Python 依赖
│   └── .env.example        # 环境变量示例
├── frontend/               # React 前端
│   ├── src/
│   │   ├── App.jsx         # 主组件
│   │   ├── App.css         # 样式
│   │   └── api.js          # API 客户端
│   ├── package.json
│   └── vite.config.js
├── spec/                   # Spec 文档
│   ├── task.md             # 开发任务清单
│   └── 01-14.md            # 各阶段文档
├── start.sh                # 启动脚本
└── README.md
```

## 快速启动

### 方式一：使用启动脚本（推荐）

```bash
cd /Users/frend/workspace/Git/group-workshop/group-5/wangxin1/ira
chmod +x start.sh
./start.sh
```

### 方式二：手动启动

**1. 启动后端**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 创建环境变量文件
cp .env.example .env

# 启动服务
python app.py
```

**2. 启动前端**

```bash
cd frontend
npm install
npm run dev
```

## 访问地址

- 前端界面: http://localhost:5173
- 后端 API: http://localhost:5000
- 健康检查: http://localhost:5000/api/v1/agent/health

## 功能特性

### 已实现功能

- [x] **会话管理** - 创建、列表、删除会话
- [x] **问答提交** - 基于研报内容的自然语言问答
- [x] **三级降级** - CoPaw → 百炼 → Demo 模式
- [x] **历史记录** - 问答历史自动保存与查看
- [x] **健康检查** - 服务状态与模型可用性检测
- [x] **能力状态展示** - 实时显示当前使用的 LLM 来源

### API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/agent/capabilities` | GET | 能力探测 |
| `/api/v1/agent/health` | GET | 健康检查 |
| `/api/v1/agent/ask` | POST | 问答提交 |
| `/api/v1/agent/sessions` | GET | 会话列表 |
| `/api/v1/agent/sessions` | POST | 新建会话 |
| `/api/v1/agent/sessions/<id>` | DELETE | 删除会话 |
| `/api/v1/agent/sessions/<id>/records` | GET | 问答记录 |

## 配置说明

编辑 `backend/.env` 文件配置 LLM 服务：

```env
# CoPaw 配置
IRA_COPAW_API_URL=https://your-copaw-api.com
IRA_COPAW_API_KEY=your-api-key

# 百炼 DashScope 配置
DASHSCOPE_API_KEY=your-dashscope-key
```

**降级策略**：
- 如果 CoPaw 配置且可用 → 使用 CoPaw
- 否则如果百炼配置且可用 → 使用百炼
- 否则 → 使用 Demo 模式（始终可用）

## 技术栈

- **后端**: Flask 3.0+, Python 3.10+
- **前端**: React 18+, Vite 5+
- **存储**: JSON 文件（教学场景）
- **LLM**: CoPaw / 百炼 DashScope / Demo 模式

## 开发文档

详见 `spec/` 目录：
- `03-立项提案` - 项目背景与范围
- `05-用户故事` - 需求与验收标准
- `09-API接口` - API 规格定义
- `task.md` - 开发任务清单

## 测试

```bash
cd backend
pytest tests/
```

## 许可证

MIT
