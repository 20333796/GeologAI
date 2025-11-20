#!/usr/bin/env python
"""Create test data - simple version (backend already running)"""
import requests
import json

API_URL = "http://127.0.0.1:8001"

print("📊 Test Data Initialization Script")
print("=" * 50)

# Check if demo_user exists, register if not
print("\n1️⃣ Creating/checking test user...")
reg_payload = {
    "username": "demo_user",
    "email": "demo@example.com",
    "password": "DemoUser123",
    "real_name": "Demo User"
}

try:
    reg_response = requests.post(
        f"{API_URL}/api/v1/auth/register",
        json=reg_payload,
        timeout=5
    )
    
    if reg_response.status_code == 201:
        print("   ✅ New user created")
    elif reg_response.status_code == 400:
        print("   ⚠️  User already exists")
    else:
        print(f"   ❌ Registration failed: {reg_response.status_code}")
        print(reg_response.json())
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Login
print("\n2️⃣ Logging in...")
login_payload = {
    "username": "demo_user",
    "password": "DemoUser123"
}

try:
    login_response = requests.post(
        f"{API_URL}/api/v1/auth/login",
        json=login_payload,
        timeout=5
    )
    
    if login_response.status_code == 200:
        login_data = login_response.json()
        token = login_data.get("access_token")
        print("   ✅ Login successful")
    else:
        print(f"   ❌ Login failed: {login_response.status_code}")
        print(login_response.json())
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Create test project
print("\n3️⃣ Creating test project...")
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

try:
    project_response = requests.post(
        f"{API_URL}/api/v1/projects",
        json=project_payload,
        headers=headers,
        timeout=5
    )
    
    if project_response.status_code == 201:
        project_data = project_response.json()
        print(f"   ✅ Project created successfully!")
        print(f"      ID: {project_data.get('id')}")
        print(f"      Name: {project_data.get('name')}")
        print(f"      Status: {project_data.get('status')}")
    else:
        print(f"   ❌ Project creation failed: {project_response.status_code}")
        print(f"      Response: {project_response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ Initialization complete!")
print("\n📋 Test Credentials:")
print("   Username: demo_user")
print("   Password: DemoUser123")
print("   Email: demo@example.com")
print("\n🌐 Frontend: http://localhost:8501")
print("🔗 Backend: http://127.0.0.1:8001")
