import os
import sys
import json

script_dir = r"D:\aiphxt-app\ai-service"
os.chdir(script_dir)
sys.path.insert(0, script_dir)

output = []
output.append("=== FastAPI TestClient Test ===")
output.append(f"Working dir: {os.getcwd()}")

try:
    from fastapi.testclient import TestClient
    from app.core.app import app
    output.append("TestClient and app imported OK")

    client = TestClient(app)

    # 1. Test health check
    output.append("\n=== Test 1: Health Check ===")
    try:
        response = client.get("/health")
        output.append(f"Status: {response.status_code}")
        output.append(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        output.append(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        output.append(traceback.format_exc())

    # 2. Test register
    output.append("\n=== Test 2: Register ===")
    try:
        import time
        username = f"testuser_{int(time.time())}"
        phone = f"138{int(time.time()) % 100000000:08d}"

        register_data = {
            "username": username,
            "password": "password123",
            "email": f"{username}@test.com",
            "phone": phone,
            "role": "student"
        }
        output.append(f"Request: {json.dumps(register_data, ensure_ascii=False)}")

        response = client.post("/api/user/register", json=register_data)
        output.append(f"Status: {response.status_code}")
        output.append(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        output.append(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        output.append(traceback.format_exc())

    # 3. Test /api/v1/auth/register
    output.append("\n=== Test 3: /api/v1/auth/register ===")
    try:
        import time
        username = f"testuser_v1_{int(time.time())}"
        phone = f"139{int(time.time()) % 100000000:08d}"

        register_data = {
            "username": username,
            "password": "password123",
            "email": f"{username}@test.com",
            "phone": phone,
            "role": "student"
        }
        output.append(f"Request: {json.dumps(register_data, ensure_ascii=False)}")

        response = client.post("/api/v1/auth/register", json=register_data)
        output.append(f"Status: {response.status_code}")
        output.append(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        output.append(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        output.append(traceback.format_exc())

except Exception as e:
    output.append(f"CRITICAL ERROR: {type(e).__name__}: {e}")
    import traceback
    output.append(traceback.format_exc())

output.append("\n=== TEST END ===")

with open(os.path.join(script_dir, "fastapi_test_results.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("Test complete. Results written to fastapi_test_results.txt")
