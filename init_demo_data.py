#!/usr/bin/env python
"""
Phase 5D - 演示数据初始化脚本
自动创建测试用户和演示项目
"""

import requests
import time
import sys

# API配置
API_BASE_URL = "http://127.0.0.1:8001"
AUTH_ENDPOINT = f"{API_BASE_URL}/api/v1/auth"
PROJECTS_ENDPOINT = f"{API_BASE_URL}/api/v1/projects"

# 测试数据
TEST_USER = {
    "username": "demo_user",
    "email": "demo@example.com",
    "password": "DemoUser123"
}

TEST_PROJECT = {
    "name": "🧪 演示项目",
    "description": "用于展示平台功能的演示项目",
    "location": "演示位置"
}

def print_header():
    """打印头部"""
    print("\n")
    print("=" * 60)
    print("  🌍 GeologAI 演示数据初始化")
    print("=" * 60)
    print("\n")

def print_info(msg):
    """打印信息"""
    print(f"[INFO] {msg}")

def print_success(msg):
    """打印成功"""
    print(f"[✓] {msg}")

def print_error(msg):
    """打印错误"""
    print(f"[✗] {msg}")

def check_backend():
    """检查后端是否运行"""
    print_info("检查后端连接...")
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print_success("后端已连接")
            return True
    except Exception as e:
        print_error(f"后端连接失败: {e}")
        print_info("请先运行后端: python backend/run_backend.py")
        return False

def register_user():
    """注册测试用户"""
    print_info(f"创建用户: {TEST_USER['username']}")
    
    try:
        response = requests.post(
            f"{AUTH_ENDPOINT}/register",
            json=TEST_USER,
            timeout=10
        )
        
        if response.status_code == 201:
            print_success(f"用户 {TEST_USER['username']} 创建成功")
            return True
        elif response.status_code == 400:
            error_data = response.json()
            if "already registered" in str(error_data):
                print_info("用户已存在，跳过创建")
                return True
            else:
                print_error(f"创建失败: {error_data}")
                return False
        else:
            print_error(f"创建失败 (状态码: {response.status_code})")
            print_error(f"响应: {response.text}")
            return False
    except Exception as e:
        print_error(f"请求失败: {e}")
        return False

def login_user():
    """登录用户"""
    print_info(f"登录用户: {TEST_USER['username']}")
    
    try:
        response = requests.post(
            f"{AUTH_ENDPOINT}/login",
            json={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print_success("登录成功，获得JWT令牌")
            return token
        else:
            print_error(f"登录失败 (状态码: {response.status_code})")
            return None
    except Exception as e:
        print_error(f"请求失败: {e}")
        return None

def create_project(token):
    """创建演示项目"""
    print_info(f"创建项目: {TEST_PROJECT['name']}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            PROJECTS_ENDPOINT,
            json=TEST_PROJECT,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            project_data = response.json()
            project_id = project_data.get("id")
            print_success(f"项目创建成功 (ID: {project_id})")
            return project_id
        else:
            print_error(f"创建失败 (状态码: {response.status_code})")
            print_error(f"响应: {response.text}")
            return None
    except Exception as e:
        print_error(f"请求失败: {e}")
        return None

def main():
    """主函数"""
    print_header()
    
    # 检查后端
    if not check_backend():
        print("\n" + "=" * 60)
        print("❌ 初始化失败")
        print("=" * 60 + "\n")
        sys.exit(1)
    
    print("\n")
    
    # 注册用户
    if not register_user():
        print("\n" + "=" * 60)
        print("❌ 初始化失败")
        print("=" * 60 + "\n")
        sys.exit(1)
    
    print("\n")
    
    # 登录用户
    token = login_user()
    if not token:
        print("\n" + "=" * 60)
        print("❌ 初始化失败")
        print("=" * 60 + "\n")
        sys.exit(1)
    
    print("\n")
    
    # 创建项目
    project_id = create_project(token)
    
    print("\n")
    print("=" * 60)
    print("✅ 初始化完成！")
    print("=" * 60)
    print("\n")
    print("  📊 演示账户信息:")
    print(f"    用户名: {TEST_USER['username']}")
    print(f"    密码: {TEST_USER['password']}")
    print(f"    邮箱: {TEST_USER['email']}")
    print("\n")
    
    if project_id:
        print(f"  📁 演示项目:")
        print(f"    项目名: {TEST_PROJECT['name']}")
        print(f"    项目ID: {project_id}")
    
    print("\n")
    print("  🚀 后续步骤:")
    print("    1. 启动前端: streamlit run web/frontend/app.py --server.port 8501")
    print("    2. 打开浏览器: http://localhost:8501")
    print("    3. 使用演示账户登录")
    print("    4. 开始使用平台！")
    print("\n")
    print("=" * 60)
    print("\n")

if __name__ == "__main__":
    main()
