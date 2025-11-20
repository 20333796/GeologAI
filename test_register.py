#!/usr/bin/env python
"""Test registration endpoint"""
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

# Test registration
try:
    print("\n📝 Testing registration endpoint...")
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "TestPass123",
        "real_name": "Test User"
    }
    
    response = requests.post(
        "http://127.0.0.1:8001/api/v1/auth/register",
        json=payload,
        timeout=10
    )
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"📦 Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 201:
        print("\n✅ Registration successful!")
    else:
        print(f"\n❌ Registration failed with status {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    print("\n🛑 Stopping server...")
    server_proc.terminate()
    server_proc.wait(timeout=5)
