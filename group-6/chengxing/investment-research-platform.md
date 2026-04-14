# 投研分析平台 (StockResearch) — 实现计划

## Context

用户需要构建一个投研分析平台：输入股票名称/代码，自动搜索展示财务数据、涨跌原因、公司概况，并支持 AI 问答。该项目为全新独立项目，位于 `qoder课程作业/stock-research/`。

## 技术选型

| 层 | 技术 | 说明 |
|----|------|------|
| 前端 | React 18 + Vite + TypeScript + Tailwind CSS | 复用已有技术栈 |
| 后端 | Python Flask | 代理东方财富 API + DashScope 对话 |
| 数据 | 东方财富公开 API | 股票搜索/行情/财报/公司简介/新闻 |
| LLM | DashScope (qwen-plus) | 涨跌分析 + AI 问答 |
| 图表 | Recharts | 财务数据可视化 |
| 主题 | IRA 视觉规范 | 深色主题: 智慧红 #E63946 + AI紫 #7B2FFF |

## 项目结构

```
stock-research/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # create_app() 工厂
│   │   ├── config.py                # 环境变量配置
│   │   ├── blueprints/
│   │   │   ├── stock_bp.py          # 搜索 + 行情 + 概况 + 涨跌分析
│   │   │   ├── finance_bp.py        # 季度财报数据
│   │   │   └── ai_bp.py             # AI 多轮对话
│   │   ├── services/
│   │   │   ├── eastmoney_service.py # 东方财富 API 封装
│   │   │   ├── dashscope_service.py # DashScope 对话封装
│   │   │   ├── session_manager.py   # 内存会话管理
│   │   │   └── cache_service.py     # TTL 内存缓存
│   │   └── utils/
│   │       └── finance_calc.py      # 同比/环比计算
│   ├── requirements.txt
│   └── wsgi.py
│
└── frontend/
    ├── vite.config.ts               # 代理 /api → localhost:5000
    ├── tailwind.config.ts
    └── src/
        ├── index.css                # IRA 设计系统 CSS 变量
        ├── App.tsx                  # 路由: / 和 /stock/:secid
        ├── api/client.ts            # fetch 封装
        ├── types/index.ts
        ├── context/StockContext.tsx  # 全局股票状态
        ├── hooks/
        │   ├── useStockSearch.ts    # 防抖搜索
        │   ├── useFinanceData.ts    # 财务数据获取
        │   └── useChatSession.ts    # AI 对话管理
        ├── pages/
        │   ├── HomePage.tsx         # 搜索入口
        │   └── StockDetail.tsx      # 详情页 (4 Tab)
        └── components/
            ├── layout/              # AppHeader, AppFooter
            ├── ui/                  # Button, Card, Badge, Skeleton, Tabs
            ├── search/              # SearchBar, SearchSuggestion
            ├── finance/             # FinanceTable, FinanceChart, GrowthBadge
            ├── market/              # PriceHeader, ChangeAnalysis
            ├── company/             # CompanyProfile
            └── chat/                # ChatPanel, ChatMessage, ChatInput, SessionList
```

## 后端 API 设计

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/stock/search?keyword=` | GET | 股票搜索 (代理东方财富搜索 API) |
| `/api/v1/stock/quote?secid=` | GET | 实时行情 (价格/涨跌幅/成交量/市值) |
| `/api/v1/stock/profile?secid=` | GET | 公司概况 (主营业务/行业/简介) |
| `/api/v1/stock/change-analysis?secid=` | GET | 涨跌原因分析 (行情+新闻→DashScope) |
| `/api/v1/finance/quarterly?secid=&years=3` | GET | 季度财务数据 (营收/利润+同比/环比) |
| `/api/v1/ai/chat` | POST | 发送消息 (多轮对话) |
| `/api/v1/ai/sessions?stock_code=` | GET | 列出会话 |
| `/api/v1/ai/sessions/:id` | GET | 获取会话历史 |
| `/api/v1/ai/sessions/:id` | DELETE | 删除会话 |

## 东方财富 API 调用要点

1. **股票搜索**: `searchapi.eastmoney.com/api/suggest/get` — token 固定公开值
2. **实时行情**: `push2.eastmoney.com/api/qt/stock/get` — 价格字段需除以100
3. **季度财报**: `datacenter.eastmoney.com/securities/api/data/v1/get` — reportName=RPT_LICO_FN_CPD
4. **公司简介**: 同上，reportName=RPT_F10_ORG_BASICINFO
5. **新闻搜索**: `search-api-web.eastmoney.com/search/jsonp`
6. 统一设置 User-Agent + Referer 请求头；TTL 缓存避免频繁调用

## 前端页面设计

### 首页 (HomePage)
- 居中大搜索框 + 品牌辉光背景
- 输入防抖 300ms → 下拉搜索建议
- 快速入口标签 (热门股票)

### 详情页 (StockDetail) — 4 个 Tab
1. **财务数据**: Recharts 双柱状图(营收红+利润紫) + 同比折线 + 数据表格
2. **涨跌分析**: AI 生成分析卡片 + 相关新闻列表
3. **公司概况**: 基本信息卡片 + 主营业务 + 公司简介
4. **AI 问答**: 左侧会话列表 + 右侧聊天面板 (消息流+输入框)

顶部始终显示: PriceHeader (股票名/代码/实时价格/涨跌幅/成交量/市值)

## AI 对话会话管理

- 内存 dict 存储，按 session_id 隔离
- 系统提示注入股票基本面摘要 (保证 AI 有上下文)
- 滑动窗口: 最近 20 条消息传给 LLM (约 7K tokens，安全在窗口内)
- 2 小时不活动自动清理
- 前端: 左右分栏，左侧会话列表可切换，右侧消息流

## 实现步骤

### Step 1: 项目脚手架
- 创建目录结构
- 初始化前端 (Vite + React + TS + Tailwind + Recharts)
- 初始化后端 (Flask + CORS + 蓝图注册)
- 配置 Vite 代理 /api → localhost:5000
- 移植 IRA 深色主题 CSS 变量

### Step 2: 后端数据服务
- `eastmoney_service.py`: 搜索、行情、财报、概况、新闻 5 个函数
- `cache_service.py`: TTL 缓存
- `finance_calc.py`: 同比/环比计算
- `stock_bp.py` + `finance_bp.py`: REST 端点

### Step 3: 前端核心页面
- UI 原子组件 (Button, Card, Badge, Skeleton, Tabs, Input)
- SearchBar + 自动补全
- HomePage (搜索入口)
- PriceHeader + FinanceChart + FinanceTable
- CompanyProfile
- StockDetail (Tab 布局)

### Step 4: AI 对话功能
- `dashscope_service.py`: 多轮对话
- `session_manager.py`: 会话 CRUD + 上下文窗口
- `ai_bp.py`: 对话端点
- 涨跌分析端点 (行情+新闻→LLM)
- ChatPanel + ChatMessage + ChatInput + SessionList
- ChangeAnalysis 组件

### Step 5: 联调完善
- 骨架屏加载态
- 错误降级 UI
- 免责声明
- 端到端测试

## 验证方式

1. 启动后端: `cd backend && python wsgi.py` (port 5000)
2. 启动前端: `cd frontend && npm run dev` (port 5173)
3. 验证搜索: 输入"贵州茅台" → 下拉建议 → 点击进入详情
4. 验证财务: 详情页"财务数据" Tab → 图表+表格渲染 → 同比/环比数据正确
5. 验证行情: PriceHeader 显示实时价格和涨跌幅
6. 验证概况: "公司概况" Tab 显示主营业务和简介
7. 验证分析: "涨跌分析" Tab → AI 生成分析文本 + 新闻列表
8. 验证问答: "AI 问答" Tab → 新建会话 → 发送问题 → 收到回复 → 切换/删除会话
9. 运行 `npm run build` 确认前端无 TS 错误
