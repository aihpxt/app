# -*- coding: utf-8 -*-
import os
import sys
import json
import time

SCRIPT_DIR = r"D:\aiphxt-app\ai-service"
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
RESULT_FILE = os.path.join(SCRIPT_DIR, "auth_test_result.json")

result = {"steps": []}

def log(step, success=True, data=None, error=None):
    entry = {"step": step, "success": success, "timestamp": time.time()}
    if data:
        entry["data"] = data
    if error:
        entry["error"] = error[:1000] if isinstance(error, str) else str(error)[:1000]
    result["steps"].append(entry)
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[{step}] {'OK' if success else 'FAILED'}")

# Step 1: Test basic auth import
try:
    from app.api.routes.auth import register, login
    log("step_1_auth_import", True)
except Exception as e:
    import traceback
    log("step_1_auth_import", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 2: Create minimal FastAPI app with only auth routes
try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    app = FastAPI()
    
    # Register only auth routes
    from app.api.routes import auth
    from app.api.routes.auth import router as auth_router
    
    # Register user routes
    from fastapi import APIRouter
    user_router = APIRouter(prefix="/api/user", tags=["用户"])
    user_router.add_api_route("/login", auth.login, methods=["POST"])
    user_router.add_api_route("/register", auth.register, methods=["POST"])
    app.include_router(user_router)
    
    # Also register /api/v1/auth routes
    app.include_router(auth_router, prefix="/api/v1")
    
    log("step_2_create_app", True, {"routes": [r.path for r in app.routes]})
except Exception as e:
    import traceback
    log("step_2_create_app", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 3: Test register endpoint
try:
    client = TestClient(app)
    
    username = f"auth_test_{int(time.time())}"
    phone = f"139{int(time.time()) % 100000000:08d}"
    
    # Test 1: Valid registration
    response = client.post("/api/user/register", json={
        "username": username,
        "password": "test123456",
        "email": f"{username}@example.com",
        "phone": phone,
        "role": "student"
    })
    
    try:
        resp_json = response.json()
    except:
        resp_json = {"text": response.text}
    
    log("step_3_register", True, {
        "status_code": response.status_code,
        "response": resp_json
    })
    
    # Test 2: Duplicate username
    response2 = client.post("/api/user/register", json={
        "username": username,
        "password": "test123456",
        "email": f"{username}_dup@example.com",
        "phone": f"138{int(time.time()) % 100000000:08d}",
        "role": "student"
    })
    
    try:
        resp_json2 = response2.json()
    except:
        resp_json2 = {"text": response2.text}
    
    log("step_4_duplicate", True, {
        "status_code": response2.status_code,
        "response": resp_json2
    })
    
    # Test 3: Login with new user
    response3 = client.post("/api/user/login", json={
        "username": username,
        "password": "test123456"
    })
    
    try:
        resp_json3 = response3.json()
    except:
        resp_json3 = {"text": response3.text}
    
    log("step_5_login", True, {
        "status_code": response3.status_code,
        "response": resp_json3
    })
    
except Exception as e:
    import traceback
    log("step_test_error", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

result["final_status"] = "completed"
with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n=== Auth Test Complete ===")
