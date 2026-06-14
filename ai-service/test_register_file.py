import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

output_lines = []
output_lines.append("=== Testing Register Function ===")
output_lines.append(f"Working directory: {os.getcwd()}")
output_lines.append("")

try:
    from app.core.app import app
    output_lines.append("App imported successfully")
except Exception as e:
    output_lines.append(f"ERROR importing app: {type(e).__name__}: {e}")
    import traceback
    output_lines.append(traceback.format_exc())
    with open("test_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    sys.exit(1)

output_lines.append("")

from fastapi.testclient import TestClient
import time

client = TestClient(app)

# Test 1: Health check
output_lines.append("Test 1: Health check")
try:
    response = client.get("/health")
    output_lines.append(f"  Status: {response.status_code}")
    output_lines.append(f"  Response: {response.text[:200]}")
except Exception as e:
    output_lines.append(f"  ERROR: {type(e).__name__}: {e}")
output_lines.append("")

# Test 2: Register new user
output_lines.append("Test 2: Register new user")
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
output_lines.append(f"  Request data: {register_data}")

try:
    response = client.post(
        "/api/user/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    output_lines.append(f"  Status: {response.status_code}")
    output_lines.append(f"  Response: {response.text[:500]}")

    try:
        json_response = response.json()
        output_lines.append(f"  JSON parsed: success={json_response.get('success')}, message={json_response.get('message')}")
        if json_response.get('success'):
            output_lines.append(f"  User data: {json_response.get('data')}")
    except Exception as json_err:
        output_lines.append(f"  JSON parse error: {json_err}")
except Exception as e:
    output_lines.append(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    output_lines.append(traceback.format_exc())
output_lines.append("")

# Test 3: Register duplicate user
output_lines.append("Test 3: Register duplicate user (same username)")
try:
    response = client.post(
        "/api/user/register",
        json=register_data,
        headers={"Content-Type": "application/json"}
    )
    output_lines.append(f"  Status: {response.status_code}")
    output_lines.append(f"  Response: {response.text[:500]}")
except Exception as e:
    output_lines.append(f"  ERROR: {type(e).__name__}: {e}")
output_lines.append("")

# Test 4: Login with new user
output_lines.append("Test 4: Login with new user")
login_data = {
    "username": username,
    "password": password
}
output_lines.append(f"  Request data: {login_data}")
try:
    response = client.post(
        "/api/user/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    output_lines.append(f"  Status: {response.status_code}")
    output_lines.append(f"  Response: {response.text[:500]}")
except Exception as e:
    output_lines.append(f"  ERROR: {type(e).__name__}: {e}")
    import traceback
    output_lines.append(traceback.format_exc())

output_lines.append("")
output_lines.append("=== All Tests Complete ===")

with open("test_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print("Tests complete. Output written to test_output.txt")
