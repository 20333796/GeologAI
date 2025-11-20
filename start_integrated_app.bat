@echo off
REM GeologAI 集成应用启动脚本 (Windows)
REM 自动启动后端和前端服务

cls
echo.
echo ============================================================
echo 🌍 GeologAI 集成应用启动器
echo ============================================================
echo.

REM 激活 conda 环境
call conda activate geologai
if errorlevel 1 (
    echo ❌ 无法激活 conda 环境
    pause
    exit /b 1
)

echo ✅ Conda 环境已激活

REM 启动后端（后台进程）
echo.
echo 🚀 正在启动后端服务 (FastAPI port 8001)...
cd /d D:\GeologAI\backend
start "GeologAI Backend" python run_backend.py

REM 等待后端启动
timeout /t 5 /nobreak

REM 启动前端
echo.
echo 🚀 正在启动前端应用 (Streamlit port 8501)...
cd /d D:\GeologAI
streamlit run web/frontend/app.py --server.port 8501 --logger.level=error

echo.
echo 👋 应用已关闭
pause
