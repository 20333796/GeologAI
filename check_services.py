#!/usr/bin/env python
"""
Phase 5E Test Verification Script
Checks if the application is working correctly
"""

import requests
import time
import sys

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8001/docs", timeout=5)
        if response.status_code == 200:
            print("✓ 后端服务: 运行正常")
            return True
    except:
        pass
    print("✗ 后端服务: 无响应")
    return False

def check_frontend():
    """Check if frontend is running"""
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✓ 前端服务: 运行正常")
            return True
    except:
        pass
    print("✗ 前端服务: 无响应")
    return False

def check_api_endpoints():
    """Check if API endpoints are working"""
    try:
        # Test login endpoint
        response = requests.post(
            "http://localhost:8001/api/v1/auth/login",
            json={"username": "demo_user", "password": "DemoUser123"},
            timeout=5
        )
        if response.status_code == 200:
            print("✓ 登录API: 正常")
            return True
        else:
            print(f"✗ 登录API: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 登录API: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("Phase 5E 应用检查")
    print("=" * 50)
    print()
    
    print("检查后端服务...")
    backend_ok = check_backend()
    print()
    
    print("检查前端服务...")
    frontend_ok = check_frontend()
    print()
    
    if backend_ok:
        print("检查API端点...")
        api_ok = check_api_endpoints()
        print()
    else:
        api_ok = False
    
    print("=" * 50)
    print("检查结果:")
    print("=" * 50)
    print(f"后端服务: {'✓ 正常' if backend_ok else '✗ 异常'}")
    print(f"前端服务: {'✓ 正常' if frontend_ok else '✗ 异常'}")
    print(f"API端点:  {'✓ 正常' if api_ok else '✗ 异常'}")
    print()
    
    if backend_ok and frontend_ok and api_ok:
        print("✓ 所有服务正常运行！")
        print()
        print("访问地址:")
        print("  前端: http://localhost:8501")
        print("  API文档: http://localhost:8001/docs")
        print()
        print("演示账户:")
        print("  用户名: demo_user")
        print("  密码: DemoUser123")
        return 0
    else:
        print("✗ 有服务异常，请检查日志")
        return 1

if __name__ == "__main__":
    sys.exit(main())
