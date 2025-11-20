#!/usr/bin/env python
"""
GeologAI API 测试脚本
用于验证后端API响应格式和前端连接
"""

import requests
import json

# API 基础配置
API_BASE_URL = "http://127.0.0.1:8001"
API_VERSION = "v1"

# 测试用例
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
}

def test_api(method, endpoint, data=None, headers=None, description=""):
    """通用API测试函数"""
    url = f"{API_BASE_URL}/api/{API_VERSION}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"方法: {method}")
    print(f"URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            print("❌ 不支持的方法")
            return None
        
        print(f"状态码: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"响应: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            return response_data
        except:
            print(f"响应: {response.text[:200]}")
            return None
    
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        return None
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return None

def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("🌍 GeologAI API 测试")
    print("="*60)
    
    # 1. 测试注册
    print("\n📝 测试流程: 注册 → 登录 → 创建项目 → 获取项目列表")
    
    # 2. 测试登录
    login_data = {
        "username": "demo",
        "password": "demo123"
    }
    
    login_response = test_api(
        "POST",
        "/auth/login",
        data=login_data,
        description="用户登录"
    )
    
    if not login_response or not login_response.get("access_token"):
        print("\n❌ 登录失败，无法继续测试")
        return
    
    auth_token = login_response.get("access_token")
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    print(f"\n✅ 登录成功！Token: {auth_token[:20]}...")
    
    # 3. 获取项目列表
    projects_response = test_api(
        "GET",
        "/projects/my-projects",
        headers=headers,
        description="获取用户项目列表"
    )
    
    if projects_response:
        projects_data = projects_response.get("data", [])
        print(f"\n✅ 获取项目成功！数量: {len(projects_data)}")
        
        if projects_data:
            print("\n📋 项目列表:")
            for idx, project in enumerate(projects_data, 1):
                print(f"  {idx}. {project.get('name')} (ID: {project.get('id')})")
    
    # 4. 创建项目
    project_data = {
        "name": "测试项目-API验证",
        "description": "通过API测试脚本创建",
        "type": "测井数据分析"
    }
    
    create_response = test_api(
        "POST",
        "/projects",
        data=project_data,
        headers=headers,
        description="创建新项目"
    )
    
    if create_response:
        print("\n✅ 项目创建成功！")
        new_project_id = create_response.get("id")
        print(f"新项目ID: {new_project_id}")
    
    # 5. 获取更新后的项目列表
    test_api(
        "GET",
        "/projects/my-projects",
        headers=headers,
        description="获取更新后的项目列表"
    )
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
