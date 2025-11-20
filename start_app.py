#!/usr/bin/env python
"""
GeologAI 完整应用启动脚本
同时启动后端和前端应用
"""

import subprocess
import time
import sys
import os
import signal
import platform

# 配置
BACKEND_DIR = os.path.join(os.path.dirname(__file__), "backend")
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "web", "frontend")
CONDA_ENV = "geologai"

# 进程列表
processes = []

def print_header():
    """打印头部信息"""
    print("\n")
    print("=" * 60)
    print("  🌍 GeologAI 应用启动器")
    print("=" * 60)
    print("\n")

def print_info(message):
    """打印信息"""
    print(f"[INFO] {message}")

def print_success(message):
    """打印成功信息"""
    print(f"[✓] {message}")

def print_error(message):
    """打印错误信息"""
    print(f"[✗] {message}")

def start_backend():
    """启动后端服务"""
    print_info("启动后端服务...")
    
    if platform.system() == "Windows":
        cmd = f'conda run -n {CONDA_ENV} python run_backend.py'
        proc = subprocess.Popen(
            cmd,
            cwd=BACKEND_DIR,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
        )
    else:
        cmd = ['conda', 'run', '-n', CONDA_ENV, 'python', 'run_backend.py']
        proc = subprocess.Popen(
            cmd,
            cwd=BACKEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    processes.append(('backend', proc))
    time.sleep(3)  # 等待后端启动
    
    # 检查后端是否成功启动
    import requests
    try:
        response = requests.get('http://127.0.0.1:8001/docs', timeout=5)
        if response.status_code == 200:
            print_success("后端服务已启动 (http://127.0.0.1:8001)")
            return True
    except:
        pass
    
    print_error("后端启动失败，请检查日志")
    return False

def start_frontend():
    """启动前端服务"""
    print_info("启动前端服务...")
    
    if platform.system() == "Windows":
        cmd = f'conda run -n {CONDA_ENV} streamlit run app.py --server.port 8501'
        proc = subprocess.Popen(
            cmd,
            cwd=FRONTEND_DIR,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
        )
    else:
        cmd = ['conda', 'run', '-n', CONDA_ENV, 'streamlit', 'run', 'app.py', '--server.port', '8501']
        proc = subprocess.Popen(
            cmd,
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    
    processes.append(('frontend', proc))
    time.sleep(3)  # 等待前端启动
    
    print_success("前端服务已启动 (http://localhost:8501)")

def signal_handler(sig, frame):
    """处理中断信号"""
    print("\n")
    print_info("正在关闭所有服务...")
    
    for name, proc in processes:
        try:
            if platform.system() == "Windows":
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            else:
                proc.terminate()
            print_success(f"{name} 服务已关闭")
        except:
            pass
    
    print_success("所有服务已关闭")
    sys.exit(0)

def main():
    """主函数"""
    print_header()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    
    # 启动后端
    print("\n📡 启动后端服务...")
    if not start_backend():
        print_error("后端启动失败，继续启动前端...")
    
    # 启动前端
    print("\n🎨 启动前端服务...")
    start_frontend()
    
    # 显示启动完成信息
    print("\n")
    print("=" * 60)
    print("✅ 应用启动完成！")
    print("=" * 60)
    print("\n")
    print("  📱 前端地址: http://localhost:8501")
    print("  🔌 后端地址: http://127.0.0.1:8001")
    print("  📚 API文档: http://127.0.0.1:8001/docs")
    print("\n")
    print("  💡 提示：")
    print("    - 使用 Ctrl+C 停止所有服务")
    print("    - 首次运行请注册新账户或使用演示账户")
    print("    - 演示账户: demo_user / DemoUser123")
    print("\n")
    print("=" * 60)
    print("\n")
    
    # 保持进程运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()
