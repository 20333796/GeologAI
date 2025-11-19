# run.ps1

Write-Host "🚀 启动地球物理测井AI平台..." -ForegroundColor Green

# 获取脚本所在目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 激活conda环境并启动后端
Write-Host "启动后端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", 
    "cd '$scriptDir\web\backend'; python -m uvicorn main:app --reload --port 8000"

# 等待后端启动
Start-Sleep -Seconds 3

# 激活conda环境并启动前端
Write-Host "启动前端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", 
    "cd '$scriptDir\web\frontend'; streamlit run app.py --server.port 8501"

Write-Host ""
Write-Host "✅ 服务启动中..." -ForegroundColor Green
Write-Host "📡 API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🌐 Web界面: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 提示：关闭新打开的窗口可停止对应服务" -ForegroundColor Yellow