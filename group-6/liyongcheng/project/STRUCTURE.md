# 研报阅读系统 - 后端
backend/
├── app/
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── storage.py         # 存储层
│   ├── llm_provider.py    # LLM 提供者
│   ├── stock_provider.py  # 股价提供者
│   ├── routes.py          # 路由蓝图
│   └── main.py            # 应用入口
├── tests/
│   ├── conftest.py
│   ├── test_storage.py
│   └── test_api.py
├── data/                   # 数据目录（自动创建）
├── .env.example           # 环境变量示例
├── requirements.txt       # Python 依赖
└── wsgi.py                # WSGI 入口

# 研报阅读系统 - 前端
frontend/
├── src/
│   ├── components/        # React 组件
│   ├── services/          # API 服务
│   ├── types/             # TypeScript 类型
│   ├── App.tsx            # 主应用
│   ├── main.tsx           # 入口
│   └── index.css          # 样式
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
└── vite.config.ts
