# -*- coding: utf-8 -*-
import os
import sys
import json
import traceback
import time

SCRIPT_DIR = r"D:\aiphxt-app\ai-service"
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
RESULT_FILE = os.path.join(SCRIPT_DIR, "auth_import_test.json")

result = {"steps": []}

def log(step, success=True, data=None, error=None):
    entry = {"step": step, "success": success, "timestamp": time.time()}
    if data:
        entry["data"] = data
    if error:
        entry["error"] = error
    result["steps"].append(entry)
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[{step}] {'OK' if success else 'FAILED'}")

# Test 1: app.auth.__init__
try:
    import app.auth
    log("test_1_auth_init", True)
except Exception as e:
    log("test_1_auth_init", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Test 2: jwt_handler
try:
    from app.auth.jwt_handler import get_jwt_handler
    log("test_2_jwt_handler", True)
except Exception as e:
    log("test_2_jwt_handler", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Test 3: rbac
try:
    from app.auth.rbac import Role
    log("test_3_rbac", True, {"roles": [r.value for r in Role]})
except Exception as e:
    log("test_3_rbac", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Test 4: auth.py itself
try:
    from app.api.routes.auth import register, RegisterRequest
    log("test_4_auth_module", True)
except Exception as e:
    log("test_4_auth_module", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

result["final_status"] = "completed"
with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("Done!")
