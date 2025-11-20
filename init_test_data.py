#!/usr/bin/env python
"""Initialize test data for debugging"""
import sys
import json
import requests
import time
from pathlib import Path

# Start backend server in background
backend_dir = Path("d:/GeologAI/backend").absolute()
sys.path.insert(0, str(backend_dir))

import subprocess

print("🚀 Starting backend server...")
server_proc = subprocess.Popen(
    [sys.executable, str(backend_dir / "run_backend.py")],
    cwd=backend_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Wait for server to start
print("⏳ Waiting for server to be ready...")
time.sleep(5)

API_URL = "http://127.0.0.1:8001"

try:
    # Create test user
    print("\n📝 Creating test user...")
    reg_payload = {
        "username": "demo_user",
        "email": "demo@example.com",
        "password": "DemoUser123",
        "real_name": "Demo User"
    }
    
    reg_response = requests.post(
        f"{API_URL}/api/v1/auth/register",
        json=reg_payload,
        timeout=10
    )
    
    if reg_response.status_code == 201:
        print("✅ Test user created")
        user_data = reg_response.json()
    else:
        print(f"⚠️ User might already exist or error: {reg_response.status_code}")
        # Try to login anyway
        user_data = None
    
    # Login to get token
    print("\n🔐 Logging in...")
    login_payload = {
        "username": "demo_user",
        "password": "DemoUser123"
    }
    
    login_response = requests.post(
        f"{API_URL}/api/v1/auth/login",
        json=login_payload,
        timeout=10
    )
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        token = login_data.get("access_token")
        print("✅ Login successful")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        raise Exception("Cannot login")
    
    # Create test project
    print("\n📁 Creating test project...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    project_payload = {
        "name": "🧪 测试项目 - 调试用",
        "description": "自动创建的测试项目，用于调试和演示",
        "location": "测试钻孔位置",
        "depth_from": 0.0,
        "depth_to": 5000.0,
        "well_diameter": 0.1
    }
    
    project_response = requests.post(
        f"{API_URL}/api/v1/projects",
        json=project_payload,
        headers=headers,
        timeout=10
    )
    
    if project_response.status_code == 201:
        project_data = project_response.json()
        project_id = project_data.get("id")
        print(f"✅ Test project created (ID: {project_id})")
    else:
        print(f"⚠️ Project creation failed: {project_response.status_code}")
        print(project_response.json())
    
    print("\n✅ Initialization complete!")
    print("\n📋 Test Account:")
    print(f"  Username: demo_user")
    print(f"  Password: DemoUser123")
    print(f"  Email: demo@example.com")
    print("\n🎯 Next steps:")
    print("  1. Open http://localhost:8501 in browser")
    print("  2. Login with the test account")
    print("  3. Start debugging!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    print("\n🛑 Stopping server...")
    server_proc.terminate()
    try:
        server_proc.wait(timeout=5)
    except:
        server_proc.kill()
