#!/usr/bin/env python
"""Test login endpoint"""
import sys
import json
import time
import subprocess
import requests
from pathlib import Path

# Start backend server
backend_dir = Path("d:/GeologAI/backend").absolute()
sys.path.insert(0, str(backend_dir))

print("🚀 Starting backend server...")
server_proc = subprocess.Popen(
    [sys.executable, str(backend_dir / "start_server.py")],
    cwd=backend_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Wait for server to start
print("⏳ Waiting for server to be ready...")
time.sleep(5)

try:
    # First register a user
    print("\n📝 Registering test user...")
    reg_payload = {
        "username": "logintest",
        "email": "logintest@example.com",
        "password": "LoginTest123",
        "real_name": "Login Test User"
    }
    
    reg_response = requests.post(
        "http://127.0.0.1:8001/api/v1/auth/register",
        json=reg_payload,
        timeout=10
    )
    print(f"✅ Registration Status: {reg_response.status_code}")
    
    # Now test login
    print("\n🔐 Testing login endpoint...")
    login_payload = {
        "username": "logintest",
        "password": "LoginTest123"
    }
    
    response = requests.post(
        "http://127.0.0.1:8001/api/v1/auth/login",
        json=login_payload,
        timeout=10
    )
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"📦 Response:")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if response.status_code == 200:
        print("\n✅ Login successful!")
        if "access_token" in result:
            print(f"🔑 Access Token (first 50 chars): {result['access_token'][:50]}...")
        if "refresh_token" in result:
            print(f"🔄 Refresh Token (first 50 chars): {result['refresh_token'][:50]}...")
    else:
        print(f"\n❌ Login failed with status {response.status_code}")
        
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
