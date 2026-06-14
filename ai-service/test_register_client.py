import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=== Testing Register Function ===")
print(f"Working directory: {os.getcwd()}")
print()

try:
    from app.core.app import app
    print("App imported successfully")
except Exception as e:
    print(f"ERROR importing app: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

from fastapi.testclient import TestClient
import time

client = TestClient(app)

# Test 1: Health check
print("Test 1: Health check")
try:
    response = client.get("/health")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text[:200]}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
print()

# Test 2: Register new user
print("Test 2: Register new user")
username = f"test_user_{int(time.time())}"
phone = f"139{int(time.time()) % 100000000:08d}"
email = f"{username}@example.com"
password = "test123456"

register_data = {
    "username": username,
    "password": password,
    "email": email,
    "phone": phone,
    "role": "student"
}
print(f"  Request data: {register_data}")

try:
    response = client.post(
        "/api/user/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text[:500]}")
    
    try:
        json_response = response.json()
        print(f"  JSON parsed: success={json_response.get('success')}, message={json_response.get('message')}")
        if json_response.get('success'):
            print(f"  User data: {json_response.get('data')}")
    except Exception as json_err:
        print(f"  JSON parse error: {json_err}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
print()

# Test 3: Register duplicate user
print("Test 3: Register duplicate user (same username)")
try:
    response = client.post(
        "/api/user/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text[:500]}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
print()

# Test 4: Login with new user
print("Test 4: Login with new user")
login_data = {
    "username": username,
    "password": password
}
print(f"  Request data: {login_data}")
try:
    response = client.post(
        "/api/user/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text[:500]}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()
print("=== All Tests Complete ===")
