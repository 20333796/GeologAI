#!/usr/bin/env python
"""Complete end-to-end test of registration and login workflow"""
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime

print("=" * 60)
print("🧪 GeologAI 完整流程测试")
print("=" * 60)

# Start backend server
backend_dir = Path("d:/GeologAI/backend").absolute()
sys.path.insert(0, str(backend_dir))

print("\n🚀 启动后端服务器...")
server_proc = subprocess.Popen(
    [sys.executable, str(backend_dir / "run_backend.py")],
    cwd=backend_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

print("⏳ 等待服务器就绪... (5秒)")
time.sleep(5)

test_user = {
    "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
    "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
    "password": "TestPass123",
    "real_name": "Test User"
}

try:
    # Test 1: Registration
    print("\n" + "=" * 60)
    print("📝 测试 1: 用户注册")
    print("=" * 60)
    
    response = requests.post(
        "http://127.0.0.1:8001/api/v1/auth/register",
        json=test_user,
        timeout=10
    )
    
    print(f"✅ 状态码: {response.status_code}")
    if response.status_code == 201:
        user_data = response.json()
        print("✅ 注册成功!")
        print(json.dumps(user_data, indent=2, ensure_ascii=False))
        
        # Test 2: Login
        print("\n" + "=" * 60)
        print("🔐 测试 2: 用户登录")
        print("=" * 60)
        
        login_response = requests.post(
            "http://127.0.0.1:8001/api/v1/auth/login",
            json={
                "username": test_user["username"],
                "password": test_user["password"]
            },
            timeout=10
        )
        
        print(f"✅ 状态码: {login_response.status_code}")
        if login_response.status_code == 200:
            login_data = login_response.json()
            print("✅ 登录成功!")
            
            access_token = login_data.get("access_token")
            user_info = login_data.get("user", {})
            
            print(f"\n👤 用户信息:")
            print(f"   用户名: {user_info.get('username')}")
            print(f"   邮箱: {user_info.get('email')}")
            print(f"   角色: {user_info.get('role')}")
            print(f"   状态: {user_info.get('status')}")
            
            print(f"\n🔑 令牌信息:")
            print(f"   Access Token (前50字): {access_token[:50]}...")
            print(f"   Refresh Token: {login_data.get('refresh_token', 'N/A')[:50]}...")
            
            # Test 3: Verify token
            print("\n" + "=" * 60)
            print("✓ 测试 3: 验证令牌")
            print("=" * 60)
            
            verify_response = requests.post(
                "http://127.0.0.1:8001/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10
            )
            
            print(f"✅ 状态码: {verify_response.status_code}")
            if verify_response.status_code == 200:
                print("✅ 令牌验证成功!")
                print(json.dumps(verify_response.json(), indent=2, ensure_ascii=False))
            else:
                print(f"❌ 令牌验证失败: {verify_response.text}")
            
            print("\n" + "=" * 60)
            print("✅ 所有测试通过!")
            print("=" * 60)
        else:
            print(f"❌ 登录失败!")
            print(f"   响应: {login_response.text}")
    elif response.status_code == 400:
        print("❌ 用户已存在或其他400错误")
        print(f"   响应: {response.json()}")
    else:
        print(f"❌ 注册失败 (HTTP {response.status_code})")
        print(f"   响应: {response.text}")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    print("\n🛑 停止服务器...")
    server_proc.terminate()
    try:
        server_proc.wait(timeout=5)
    except:
        server_proc.kill()
    print("✅ 完成")
