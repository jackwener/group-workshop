# T01 — 项目脚手架初始化

| 项 | 值 |
|---|---|
| 任务ID | T01 |
| 所属 WBS | W1 + W2 + W4 |
| 里程碑 | S1 前置 |
| 优先级 | **P0** |
| 状态 | PENDING |
| 依赖 | 无（可最先启动） |
| 并行关系 | 完成后解锁 T02-T14 全部任务 |

## 1. 任务目标

搭建 M4-RA 研报聚合分析助手的完整项目目录结构，安装前后端依赖，确保 `flask run` 和 `npm run dev` 均可启动空白应用。

## 2. Spec 对齐

| Spec | 章节 | 要点 |
|------|------|------|
| `08` 系统架构 | §1.1 | Flask Backend :5000 + React SPA :5173 |
| `08` 系统架构 | §2 | 四层分层：Route → Agent → Provider → Storage |
| `08` 系统架构 | §3 | React 18 + Vite 5 + Tailwind CSS + Headless UI |
| `08` 系统架构 | §6 | 部署端口 5000 / 5173 |
| `07` 非功能 | §6 | Python ≥ 3.10, Node ≥ 16, Flask ≥ 3.0, React ≥ 18 |

## 3. 交付物 — 目录结构

```
backend/
├── wsgi.py                  # Flask 应用入口
├── agent_bp.py              # Route 层（空壳，仅注册蓝图）
├── agent.py                 # Agent 编排（空壳）
├── storage.py               # Storage 层（空壳）
├── copaw_bridge.py          # CoPaw Provider（空壳）
├── bailian_qa.py            # 百炼 Provider（空壳）
├── report_parser.py         # 研报解析引擎（空壳）
├── requirements.txt         # Flask, python-dotenv, pytest, etc.
├── .env.example             # 环境变量模板
├── data/                    # JSON 数据目录
│   ├── sessions.json
│   ├── qa_records.json
│   └── reports.json
└── tests/
    ├── conftest.py          # pytest fixture
    └── __init__.py

frontend/
├── package.json
├── vite.config.js           # proxy → localhost:5000
├── tailwind.config.js
├── index.html
├── src/
│   ├── App.jsx              # 主组件（空壳）
│   ├── main.jsx             # 入口
│   └── index.css            # Tailwind 引入
└── public/
```

## 4. 验收标准（AC）

| # | 验收条件 |
|---|---------|
| AC-01 | `cd backend && python -m flask --app wsgi run --port 5000` 成功启动 |
| AC-02 | `cd frontend && npm run dev` 成功启动，浏览器可访问 :5173 |
| AC-03 | 前端 Vite proxy 配置 `/api` → `http://localhost:5000` |
| AC-04 | `GET /api/v1/agent/capabilities` 返回 200（即使空实现） |
| AC-05 | `backend/data/` 下 3 个 JSON 文件初始化为 `[]` |
| AC-06 | `.env.example` 包含 `IRA_COPAW_*_URL`、`DASHSCOPE_API_KEY` 占位 |
| AC-07 | `pytest tests/` 可运行（0 用例不报错） |
