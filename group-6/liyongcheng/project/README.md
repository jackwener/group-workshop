# 研报阅读系统

基于 Flask + React 的研报阅读系统，支持研报解析、对比和股价查询。

## 快速开始

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境变量配置
cp .env.example .env

# 启动服务
python -m app.main
# 或
flask --app wsgi run --port 5000
```

后端服务将在 http://localhost:5000 启动。

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖（使用 pnpm 或 npm）
pnpm install
# 或 npm install

# 启动开发服务器
pnpm dev
# 或 npm run dev
```

前端服务将在 http://localhost:5173 启动。

## 功能特性

### 1. 研报解析
- 上传 PDF 研报文件
- 自动提取核心数据：标题、研究对象、券商、评级、目标价、核心观点
- 支持三级降级：CoPaw → 百炼 → Demo

### 2. 研报对比
- 选择同一上市公司的多份研报
- 横向对比不同券商观点
- 表格化展示评级、目标价、核心观点

### 3. 股价查询
- 输入股票代码实时查询股价
- 支持多数据源降级：新浪 → 腾讯 → Mock
- 展示当前价、涨跌幅、成交量等信息

## API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v1/research/reports` | GET | 获取研报列表 |
| `/api/v1/research/reports` | POST | 上传研报 |
| `/api/v1/research/reports/<id>` | GET | 获取研报详情 |
| `/api/v1/research/reports/<id>` | DELETE | 删除研报 |
| `/api/v1/research/reports/compare` | POST | 研报对比 |
| `/api/v1/research/stock/price` | GET | 股价查询 |

## 运行测试

```bash
# 后端测试
cd backend
pytest tests/ -v

# 后端测试 + 覆盖率
pytest tests/ -v --cov=app --cov-report=term-missing
```

## 技术栈

- **后端**: Python 3.10+, Flask 3.0, pytest
- **前端**: React 18, TypeScript, Vite 5, Tailwind CSS
- **存储**: JSON 文件（教学版）
