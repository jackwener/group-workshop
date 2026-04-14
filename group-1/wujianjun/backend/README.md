# 投研智能问答助手 - 后端服务

基于 Flask + JSON 文件存储的投研智能问答系统后端。

## 项目结构

```
backend/
├── app/
│   ├── __init__.py          # Flask 应用工厂
│   ├── api/
│   │   ├── __init__.py      # 蓝图注册
│   │   └── routes.py        # 6 个 API 端点实现
│   ├── core/
│   │   └── storage.py       # Storage 层（JSON 文件 CRUD）
│   └── services/
│       ├── agent.py         # Agent 层（三级降级编排）
│       ├── copaw_bridge.py  # CoPaw Provider
│       └── bailian_qa.py    # 百炼 Provider
├── data/                    # JSON 数据文件目录
├── tests/                   # 测试用例
├── .env.example             # 环境变量模板
├── requirements.txt         # Python 依赖
└── wsgi.py                  # WSGI 入口
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置 API 密钥（可选）
```

### 3. 启动服务

```bash
python wsgi.py
```

服务将在 http://localhost:5000 启动

## API 端点

Base URL: `/api/v1/agent`

| 端点 | 方法 | 功能 |
|------|------|------|
| `/capabilities` | GET | 能力探测 |
| `/ask` | POST | 问答提交 |
| `/sessions` | GET | 会话列表 |
| `/sessions` | POST | 新建会话 |
| `/sessions/<id>` | DELETE | 删除会话 |
| `/sessions/<id>/records` | GET | 问答记录 |

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_storage.py
pytest tests/test_api.py

# 生成覆盖率报告
pytest --cov=app --cov-report=term-missing
```

## 三级降级策略

系统按以下顺序尝试 LLM 服务：

1. **CoPaw** - 内部 LLM 服务（需配置 `IRA_COPAW_API_URL` 和 `IRA_COPAW_API_KEY`）
2. **百炼** - 阿里云 DashScope（需配置 `DASHSCOPE_API_KEY`）
3. **Demo** - 本地演示模式（无需配置，始终可用）

## 文档对齐

- [01-Spec写作总则](../spec/01-Spec写作总则与文档编号索引.md)
- [05-用户故事](../spec/05-用户故事与验收标准.md)
- [08-架构设计](../spec/08-系统架构与技术选型.md)
- [09-API规格](../spec/09-API接口规格.md)
- [10-数据模型](../spec/10-数据模型与存储规格.md)
- [13-测试策略](../spec/13-测试策略与质量门禁.md)

## 技术栈

- **框架**: Flask 3.0+
- **存储**: JSON 文件（UTF-8，缩进 2 空格）
- **测试**: pytest, pytest-cov
- **CORS**: flask-cors（教学版全开放）
