@echo off
REM Investment Research QA Assistant - Start Script (Windows)

echo ====================================
echo   投研问答助手 - 启动脚本
echo ====================================

REM Create data directory
if not exist "backend\data" mkdir backend\data

REM Start Flask backend
echo [1/2] 启动 Flask 后端 (端口 5000)...
start "Flask Backend" cmd /c "cd backend && python app.py"

REM Wait for backend to start
timeout /t 2 /nobreak >nul

REM Start Vite frontend
echo [2/2] 启动 Vite 前端 (端口 5173)...
start "Vite Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo ====================================
echo   前端: http://localhost:5173
echo   后端: http://localhost:5000
echo ====================================
echo   按任意键关闭此窗口（服务继续运行）
pause >nul
