# -*- coding: utf-8 -*-
import os
import sys
import json

SCRIPT_DIR = r"D:\aiphxt-app\ai-service"
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

RESULT_FILE = os.path.join(SCRIPT_DIR, "final_test_result.json")
result = {"steps": []}

def log(step, success=True, data=None, error=None):
    entry = {"step": step, "success": success}
    if data:
        entry["data"] = data
    if error:
        entry["error"] = str(error)[:500]
    result["steps"].append(entry)
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[{step}] {'OK' if success else 'FAILED'}")

# Step 1: Initialize database
try:
    from app.core.database_pool import get_db_manager
    db_manager = get_db_manager()
    log("step_1_init_db", True)
except Exception as e:
    import traceback
    log("step_1_init_db", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Step 2: Test app creation
try:
    from fastapi import FastAPI
    from app.core.app import create_app
    app = create_app()
    log("step_2_create_app", True)
except Exception as e:
    import traceback
    log("step_2_create_app", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Step 3: Test routes
try:
    routes = []
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else []
            })
    log("step_3_check_routes", True, {"total_routes": len(routes), "routes": routes[:20]})
except Exception as e:
    import traceback
    log("step_3_check_routes", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Step 4: Test register
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    import time as t
    username = f"final_test_{int(t.time())}"
    phone = f"138{int(t.time()) % 100000000:08d}"
    
    response = client.post("/api/user/register", json={
        "username": username,
        "password": "password123",
        "email": f"{username}@test.com",
        "phone": phone,
        "role": "student"
    })
    
    try:
        resp_data = response.json()
    except:
        resp_data = {"text": response.text[:300]}
    
    log("step_4_test_register", True, {
        "status_code": response.status_code,
        "response": resp_data
    })
    
    # Test login
    response2 = client.post("/api/user/login", json={
        "username": username,
        "password": "password123"
    })
    
    try:
        resp_data2 = response2.json()
    except:
        resp_data2 = {"text": response2.text[:300]}
    
    log("step_5_test_login", True, {
        "status_code": response2.status_code,
        "response": resp_data2
    })
    
    # Test /api/v1/auth/register
    import time as t2
    username2 = f"final_test2_{int(t2.time())}"
    phone2 = f"139{int(t2.time()) % 100000000:08d}"
    
    response3 = client.post("/api/v1/auth/register", json={
        "username": username2,
        "password": "password123",
        "email": f"{username2}@test.com",
        "phone": phone2,
        "role": "teacher"
    })
    
    try:
        resp_data3 = response3.json()
    except:
        resp_data3 = {"text": response3.text[:300]}
    
    log("step_6_test_v1_register", True, {
        "status_code": response3.status_code,
        "response": resp_data3
    })
    
    # Test /api/v1/auth/login
    response4 = client.post("/api/v1/auth/login", json={
        "username": username2,
        "password": "password123"
    })
    
    try:
        resp_data4 = response4.json()
    except:
        resp_data4 = {"text": response4.text[:300]}
    
    log("step_7_test_v1_login", True, {
        "status_code": response4.status_code,
        "response": resp_data4
    })
    
except Exception as e:
    import traceback
    log("step_test_error", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

result["final_status"] = "completed"
with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n=== Final Test Complete ===")
print(f"\n测试报告已保存到: {RESULT_FILE}")
