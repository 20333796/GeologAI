@echo off
REM GeologAI Backend Start Script
cd /d D:\GeologAI\backend

echo Starting GeologAI Backend Server...
echo.
echo Backend will be available at: http://localhost:8001
echo API Docs: http://localhost:8001/docs
echo.

conda run -n geologai uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
