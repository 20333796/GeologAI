@echo off
REM GeologAI Test Start Script
cd /d D:\GeologAI

echo Starting GeologAI Frontend for Testing...
echo.
echo Frontend will open at: http://localhost:8501
echo.
echo Note: Make sure backend is running on port 8001
echo Run this command in another terminal:
echo   conda run -n geologai uvicorn backend.app.main:app --host 0.0.0.0 --port 8001
echo.

conda run -n geologai streamlit run web/frontend/app.py --server.port 8501
