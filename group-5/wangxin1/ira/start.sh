#!/bin/bash

# 投研问答助手 (IRA) 启动脚本

echo "================================"
echo "  投研问答助手 (IRA) 启动脚本"
echo "================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 Python
echo "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python 3.10+"
    exit 1
fi

# 检查 Node.js
echo "检查 Node.js 环境..."
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 Node.js，请先安装 Node.js 16+"
    exit 1
fi

# 安装后端依赖
echo ""
echo "安装后端依赖..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# 创建 .env 文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "创建 .env 配置文件..."
    cp .env.example .env
fi

cd ..

# 安装前端依赖
echo ""
echo "安装前端依赖..."
cd frontend
npm install
cd ..

# 启动后端
echo ""
echo "启动后端服务 (Flask)..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

echo "后端服务 PID: $BACKEND_PID"
echo "后端地址: http://localhost:5000"

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo "启动前端服务 (Vite)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "前端服务 PID: $FRONTEND_PID"
echo "前端地址: http://localhost:5173"

echo ""
echo "================================"
echo "  服务启动成功！"
echo "================================"
echo ""
echo "访问地址:"
echo "  - 前端界面: http://localhost:5173"
echo "  - 后端 API: http://localhost:5000"
echo "  - 健康检查: http://localhost:5000/api/v1/agent/health"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
