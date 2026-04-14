#!/bin/bash
# Investment Research QA Assistant - Start Script (Linux/Mac)

echo "===================================="
echo "  投研问答助手 - 启动脚本"
echo "===================================="

# Create data directory
mkdir -p backend/data

# Start Flask backend
echo "[1/2] 启动 Flask 后端 (端口 5000)..."
cd backend && python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 2

# Start Vite frontend
echo "[2/2] 启动 Vite 前端 (端口 5173)..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "===================================="
echo "  前端: http://localhost:5173"
echo "  后端: http://localhost:5000"
echo "===================================="
echo "  按 Ctrl+C 停止所有服务"

# Trap Ctrl+C to kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
