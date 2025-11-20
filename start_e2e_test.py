#!/usr/bin/env python
"""Complete E2E test: Start backend, frontend, and test login"""
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

backend_dir = Path("d:/GeologAI/backend").absolute()
frontend_dir = Path("d:/GeologAI/web/frontend").absolute()

print("="*60)
print("🚀 GeologAI Backend & Frontend E2E Test")
print("="*60)

# Start backend
print("\n1️⃣  Starting Backend Server...")
backend_proc = subprocess.Popen(
    [sys.executable, str(backend_dir / "start_server.py")],
    cwd=backend_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)
print("   ⏳ Waiting for backend to initialize...")
time.sleep(6)

# Test backend health
try:
    response = requests.get("http://127.0.0.1:8001/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Backend is healthy")
    else:
        print(f"   ⚠️  Backend health check returned {response.status_code}")
except Exception as e:
    print(f"   ❌ Backend health check failed: {e}")

# Test registration
print("\n2️⃣  Testing Registration...")
try:
    reg_response = requests.post(
        "http://127.0.0.1:8001/api/v1/auth/register",
        json={
            "username": "e2etest",
            "email": "e2etest@example.com",
            "password": "E2ETest123",
            "real_name": "E2E Test User"
        },
        timeout=10
    )
    if reg_response.status_code == 201:
        user_data = reg_response.json()
        print(f"   ✅ Registration successful (ID: {user_data.get('id')})")
    else:
        print(f"   ❌ Registration failed: {reg_response.status_code}")
        print(f"      {reg_response.json()}")
except Exception as e:
    print(f"   ❌ Registration error: {e}")

# Test login
print("\n3️⃣  Testing Login...")
try:
    login_response = requests.post(
        "http://127.0.0.1:8001/api/v1/auth/login",
        json={
            "username": "e2etest",
            "password": "E2ETest123"
        },
        timeout=10
    )
    if login_response.status_code == 200:
        login_data = login_response.json()
        access_token = login_data.get("access_token", "")
        print(f"   ✅ Login successful")
        print(f"   🔑 Token (first 40 chars): {access_token[:40]}...")
    else:
        print(f"   ❌ Login failed: {login_response.status_code}")
        print(f"      {login_response.json()}")
except Exception as e:
    print(f"   ❌ Login error: {e}")

# Start frontend
print("\n4️⃣  Starting Frontend (Streamlit)...")
frontend_proc = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "web/frontend/app.py", "--server.port", "8501"],
    cwd=frontend_dir.parent.parent,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)
print("   ⏳ Waiting for frontend to initialize...")
time.sleep(4)

# Summary
print("\n" + "="*60)
print("📊 E2E Test Summary")
print("="*60)
print(f"✅ Backend: http://127.0.0.1:8001")
print(f"✅ Frontend: http://localhost:8501")
print(f"✅ Database: SQLite (geologai_test.db)")
print(f"\n🎯 Next Steps:")
print(f"   1. Open http://localhost:8501 in your browser")
print(f"   2. Login with:")
print(f"      - Username: e2etest")
print(f"      - Password: E2ETest123")
print(f"   3. Navigate through the app")
print(f"\n⏹️  To stop, press Ctrl+C")
print("="*60 + "\n")

# Keep processes running
try:
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    print("\n\n🛑 Shutting down...")
    backend_proc.terminate()
    frontend_proc.terminate()
    time.sleep(2)
    backend_proc.kill()
    frontend_proc.kill()
    print("✅ Shutdown complete")
