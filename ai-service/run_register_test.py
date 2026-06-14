# -*- coding: utf-8 -*-
import os
import sys
import json
import traceback

SCRIPT_DIR = r"D:\aiphxt-app\ai-service"
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
RESULT_FILE = os.path.join(SCRIPT_DIR, "test_register_result.json")

result = {
    "status": "running",
    "steps": [],
    "errors": []
}

def log(step, data=None):
    entry = {"step": step, "data": data}
    result["steps"].append(entry)
    save_result()

def save_result():
    try:
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Failed to save result: {e}")

log("start", {"working_dir": os.getcwd()})

try:
    from fastapi.testclient import TestClient
    from app.core.app import app
    log("import_ok", {"message": "TestClient and app imported successfully"})
except Exception as e:
    result["errors"].append(f"Import error: {type(e).__name__}: {e}")
    result["errors"].append(traceback.format_exc())
    result["status"] = "failed"
    save_result()
    sys.exit(1)

client = TestClient(app)

# Test 1: Health check
try:
    response = client.get("/health")
    log("health_check", {
        "status_code": response.status_code,
        "response": response.json()
    })
except Exception as e:
    log("health_check_error", {
        "error": f"{type(e).__name__}: {e}",
        "traceback": traceback.format_exc()
    })

# Test 2: Register
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

    log("register_request", {"data": register_data, "path": "/api/user/register"})

    response = client.post("/api/user/register", json=register_data)
    log("register_response", {
        "status_code": response.status_code,
        "response": response.json()
    })
except Exception as e:
    log("register_error", {
        "error": f"{type(e).__name__}: {e}",
        "traceback": traceback.format_exc()
    })

# Test 3: v1/auth/register
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

    log("register_request_v1", {"data": register_data, "path": "/api/v1/auth/register"})

    response = client.post("/api/v1/auth/register", json=register_data)
    log("register_response_v1", {
        "status_code": response.status_code,
        "response": response.json()
    })
except Exception as e:
    log("register_error_v1", {
        "error": f"{type(e).__name__}: {e}",
        "traceback": traceback.format_exc()
    })

result["status"] = "completed"
save_result()
print(f"Test complete. Results saved to {RESULT_FILE}")
