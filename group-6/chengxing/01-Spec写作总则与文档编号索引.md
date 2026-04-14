# 01 — Spec 写作总则 & 文档编号索引

---

| 项 | 值 |
|---|---|
| 模块编号 | SR (StockResearch) |
| 模块名称 | 投研分析平台 |
| 文档版本 | v1.0 |
| 文档状态 | Approved |

---

## 一、编号与阶段对照（00 ~ 14）

| 编号 | 阶段 | 分类 | 文档名称 |
|------|------|------|----------|
| `01` | Meta | 编号规范 | Spec 写作规则、RFC 规范词（本文） |
| `02` | Meta | Elicitation | 需求来源与采集记录 |
| `03` | Proposal | Proposal | 立项提案与范围说明 |
| `04` | Proposal | PRD | 产品需求说明 |
| `05` | Spec | UserStory | 用户故事与验收标准 |
| `06` | Spec | FSD | 功能规格说明 |
| `07` | Spec | NFR | 非功能需求与约束 |
| `08` | Design | Architecture | 系统架构与技术选型 |
| `09` | Design | API | 接口规格（契约真源） |
| `10` | Design | Data | 数据模型与存储规格 |
| `11` | Design | Security | 安全设计规格 |
| `12` | Plan | Plan | 实施计划与里程碑 |
| `13` | Test | Test | 测试策略与质量门禁 |
| `14` | Trace | Traceability | 需求追踪矩阵（四向对齐） |

## 二、基本原则

1. **单一真相**：对外行为以 `09` API 与 `10` 数据模型为准
2. **先行为后实现**：先定义 `05` 用户故事，再写 `06/09/10`
3. **可验证**：所有 MUST 条目必须能被测试或监控验证
4. **不混层**：PRD 不写 SQL，API 不写像素，Test 不重复规则
5. **无歧义**：禁止「可选其一 / 建议 / 大概 / 尽量」等表述

## 三、规范词（RFC 风格）

| 词 | 含义 |
|----|------|
| **MUST** | 必须，违反即缺陷 |
| **SHOULD** | 建议，不满足需说明理由 |
| **MAY** | 可选，不影响基线验收 |
| **MUST NOT** | 严禁 |

## 四、术语表（Glossary）

| 缩写 | 英文全称 | 中文含义 |
|------|----------|----------|
| **SR** | StockResearch | 投研分析平台 |
| **LLM** | Large Language Model | 大语言模型 |
| **secid** | Security ID | 东方财富证券代码（如 1.600519） |
| **DashScope** | Alibaba DashScope | 阿里百炼大模型服务 |
| **TTL** | Time To Live | 缓存过期时间 |
| **API** | Application Programming Interface | 应用程序接口 |
| **DTO** | Data Transfer Object | 数据传输对象 |
| **SPA** | Single Page Application | 单页应用 |

## 五、源码目录参考

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
└── frontend/
    ├── vite.config.ts
    ├── tailwind.config.ts
    └── src/
        ├── App.tsx
        ├── api/client.ts
        ├── types/index.ts
        ├── context/StockContext.tsx
        ├── hooks/
        ├── pages/
        └── components/
```

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-04-14 | 首版发布 |
