from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
response = client.post(
    "/api/v1/auth/register",
    json={
        "username": "newuser",
        "email": "new@example.com",
        "password": "NewPass123!",
        "full_name": "New User"
    }
)

print(f"Status: {response.status_code}")
print(f"Response text: {response.text}")
try:
    print(f"Response JSON: {response.json()}")
except Exception as e:
    print(f"Could not parse JSON: {e}")
