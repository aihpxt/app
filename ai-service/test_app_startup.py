# -*- coding: utf-8 -*-
import os
import sys
import json
import time

SCRIPT_DIR = r"D:\aiphxt-app\ai-service"
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
RESULT_FILE = os.path.join(SCRIPT_DIR, "app_test_result.json")

result = {"steps": [], "final_status": "unknown"}

def log(step, success=True, data=None, error=None):
    entry = {"step": step, "success": success, "timestamp": time.time()}
    if data:
        entry["data"] = data
    if error:
        entry["error"] = error[:1500] if isinstance(error, str) else str(error)[:1500]
    result["steps"].append(entry)
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[{step}] {'OK' if success else 'FAILED'}")

# Step 1: Import app
try:
    log("step_1_start_import_app", True)
    from app.core.app import app
    log("step_1_import_app", True, {"routes_count": len(app.routes), "app_title": app.title})
except Exception as e:
    import traceback
    log("step_1_import_app", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    result["final_status"] = "failed"
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    sys.exit(1)

# Step 2: Create TestClient
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    log("step_2_testclient", True)
except Exception as e:
    import traceback
    log("step_2_testclient", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 3: Health check
try:
    response = client.get("/health")
    log("step_3_health", True, {
        "status_code": response.status_code,
        "response": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
    })
except Exception as e:
    log("step_3_health", False, error=f"{type(e).__name__}: {e}")

# Step 4: Test register
try:
    username = f"test_user_{int(time.time())}"
    phone = f"138{int(time.time()) % 100000000:08d}"
    
    register_data = {
        "username": username,
        "password": "test123456",
        "email": f"{username}@example.com",
        "phone": phone,
        "role": "student"
    }
    
    response = client.post("/api/user/register", json=register_data)
    
    try:
        resp_json = response.json()
    except:
        resp_json = {"raw_text": response.text[:500]}
    
    log("step_4_register", True, {
        "status_code": response.status_code,
        "request_data": register_data,
        "response": resp_json
    })
except Exception as e:
    import traceback
    log("step_4_register", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Step 5: List all routes
try:
    all_routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            all_routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else []
            })
    
    register_routes = [r for r in all_routes if 'register' in r['path'].lower()]
    login_routes = [r for r in all_routes if 'login' in r['path'].lower()]
    
    log("step_5_routes", True, {
        "total_routes": len(all_routes),
        "register_routes": register_routes,
        "login_routes": login_routes
    })
except Exception as e:
    log("step_5_routes", False, error=f"{type(e).__name__}: {e}")

result["final_status"] = "completed"
with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n=== Test Complete ===")
print(f"Results: {RESULT_FILE}")
