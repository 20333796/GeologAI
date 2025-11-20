#!/usr/bin/env python
"""
Startup script to run both backend and frontend
"""
import subprocess
import sys
import time
import os

def run_backend():
    """Start backend server"""
    print("Starting backend server on port 8001...")
    cmd = [
        sys.executable, 
        "-m", "uvicorn", 
        "backend.app.main:app",
        "--host", "0.0.0.0",
        "--port", "8001",
        "--reload"
    ]
    return subprocess.Popen(cmd, cwd="d:\\GeologAI", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_frontend():
    """Start frontend server"""
    print("Starting frontend server on port 8501...")
    time.sleep(3)  # Wait for backend to start
    cmd = [
        sys.executable, 
        "-m", "streamlit", 
        "run",
        "web/frontend/app.py",
        "--server.port", "8501",
        "--logger.level=error"
    ]
    return subprocess.Popen(cmd, cwd="d:\\GeologAI")

if __name__ == "__main__":
    print("Starting GeologAI application...")
    
    backend_proc = run_backend()
    frontend_proc = run_frontend()
    
    print("\n✅ Backend running on: http://localhost:8001")
    print("✅ Frontend running on: http://localhost:8501")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait(timeout=5)
        frontend_proc.wait(timeout=5)
        print("Services stopped")
        sys.exit(0)
