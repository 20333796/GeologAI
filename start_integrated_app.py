#!/usr/bin/env python
"""
GeologAI 集成应用快速启动脚本
自动启动后端和前端服务
"""

import subprocess
import time
import sys
import os

def run_command(cmd, description, cwd=None):
    """运行命令并返回进程"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"命令: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        print(f"✅ {description} 已启动")
        return process
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return None

def main():
    """主程序"""
    print("\n" + "="*60)
    print("🌍 GeologAI 集成应用启动器")
    print("="*60)
    
    backend_process = None
    frontend_process = None
    
    try:
        # 启动后端服务
        backend_cmd = [
            sys.executable,
            "D:\\GeologAI\\backend\\run_backend.py"
        ]
        backend_process = run_command(backend_cmd, "后端服务 (FastAPI port 8001)")
        
        # 等待后端启动
        print("\n⏳ 等待后端启动... (5秒)")
        time.sleep(5)
        
        # 启动前端应用
        frontend_cmd = [
            "streamlit",
            "run",
            "D:\\GeologAI\\web\\frontend\\app.py",
            "--server.port", "8501",
            "--logger.level=error"
        ]
        frontend_process = run_command(frontend_cmd, "前端应用 (Streamlit port 8501)")
        
        print("\n" + "="*60)
        print("✅ 应用已启动!")
        print("="*60)
        print("\n📍 访问应用:")
        print("   前端: http://localhost:8501")
        print("   后端: http://localhost:8001")
        print("   API文档: http://localhost:8001/docs")
        print("\n📝 按 Ctrl+C 停止应用\n")
        
        # 等待进程
        if frontend_process:
            frontend_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 正在停止应用...")
    finally:
        # 清理进程
        if backend_process:
            backend_process.terminate()
            print("✅ 后端已停止")
        if frontend_process:
            frontend_process.terminate()
            print("✅ 前端已停止")
        
        print("\n👋 应用已关闭\n")

if __name__ == "__main__":
    main()
