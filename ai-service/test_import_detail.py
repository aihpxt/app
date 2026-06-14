# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import traceback

SCRIPT_DIR = r"D:\aiphxt-app\ai-service"
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
RESULT_FILE = os.path.join(SCRIPT_DIR, "import_diagnose.json")

result = {"steps": []}

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

# Step 1: FastAPI
try:
    from fastapi import FastAPI
    log("step_1_fastapi", True)
except Exception as e:
    log("step_1_fastapi", False, error=f"{type(e).__name__}: {e}")
    sys.exit(1)

# Step 2: Core config
try:
    from app.core.config import APP_NAME, APP_VERSION, DEBUG
    log("step_2_config", True, {"app_name": APP_NAME})
except Exception as e:
    log("step_2_config", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 3: Logging module
try:
    import app.core.logging
    import logging
    logger = logging.getLogger(__name__)
    log("step_3_logging", True)
except Exception as e:
    log("step_3_logging", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 4: Create app
try:
    app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=DEBUG)
    log("step_4_create_app", True)
except Exception as e:
    log("step_4_create_app", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 5: Auth module import
try:
    from app.api.routes.auth import router as auth_router
    from app.api.routes.auth import login, register
    app.include_router(auth_router)
    
    user_router = type(auth_router)(prefix="/api/user", tags=["用户"])
    user_router.add_api_route("/login", login, methods=["POST"])
    user_router.add_api_route("/register", register, methods=["POST"])
    app.include_router(user_router)
    
    log("step_5_auth_module", True, {"auth_routes": len(auth_router.routes)})
except Exception as e:
    log("step_5_auth_module", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 6: Test register endpoint
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    username = f"import_test_{int(time.time())}"
    phone = f"136{int(time.time()) % 100000000:08d}"
    
    response = client.post("/api/user/register", json={
        "username": username,
        "password": "test123456",
        "email": f"{username}@test.com",
        "phone": phone,
        "role": "student"
    })
    
    try:
        resp_data = response.json()
    except:
        resp_data = {"text": response.text[:500]}
    
    log("step_6_test_register", True, {
        "status_code": response.status_code,
        "response": resp_data
    })
except Exception as e:
    log("step_6_test_register", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Step 7: List all routes
try:
    route_paths = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            route_paths.append(f"{list(route.methods)[0] if route.methods else ''} {route.path}")
    
    log("step_7_routes", True, {"total": len(route_paths), "routes": route_paths})
except Exception as e:
    log("step_7_routes", False, error=f"{type(e).__name__}: {e}")

result["final_status"] = "completed"
with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n=== Import Diagnose Complete ===")
