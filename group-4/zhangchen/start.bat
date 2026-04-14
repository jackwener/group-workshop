@echo off
chcp 65001 >nul
echo ==========================================
echo    基金模拟投资大赛系统启动脚本
echo ==========================================
echo.

REM 检查Python环境
echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 检查Node.js环境
echo [2/3] 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请确保Node.js已安装并添加到PATH
    pause
    exit /b 1
)

echo [3/3] 环境检查完成
echo.

REM 检查 uv 环境
echo [3/4] 检查 uv 环境...
uv --version >nul 2>&1
if errorlevel 1 (
    echo 正在安装 uv...
    pip install uv
)

echo [4/4] 环境检查完成
echo.

REM 启动后端服务
echo ==========================================
echo 正在启动后端服务 (FastAPI)...
echo ==========================================
start "后端服务" cmd /k "cd /d "%~dp0backend" && echo 安装依赖... && uv sync && echo 启动服务... && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo 等待后端服务启动...
timeout /t 5 /nobreak >nul

REM 启动前端服务
echo ==========================================
echo 正在启动前端服务 (React + Vite)...
echo ==========================================
start "前端服务" cmd /k "cd /d "%~dp0frontend" && echo 安装依赖... && pnpm install && echo 启动服务... && pnpm dev"

echo.
echo ==========================================
echo 服务启动完成！
echo ==========================================
echo.
echo 后端API地址: http://localhost:8000
echo 前端页面地址: http://localhost:5173
echo API文档地址: http://localhost:8000/docs
echo.
echo 按任意键关闭此窗口（服务将继续在后台运行）
pause >nul
