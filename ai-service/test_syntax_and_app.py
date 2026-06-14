# -*- coding: utf-8 -*-
import os
import sys
import json
import traceback
import time

SCRIPT_DIR = r"D:\aiphxt-app\ai-service"
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
RESULT_FILE = os.path.join(SCRIPT_DIR, "syntax_and_app_test.json")

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

# Test 1: Compile auth.py
try:
    auth_path = os.path.join(SCRIPT_DIR, "app", "api", "routes", "auth.py")
    with open(auth_path, "r", encoding="utf-8") as f:
        code = f.read()
    compile(code, auth_path, "exec")
    log("test_1_auth_syntax", True, {"lines": len(code.splitlines())})
except Exception as e:
    log("test_1_auth_syntax", False, error=f"{type(e).__name__}: {e}")

# Test 2: Import each component separately
try:
    import app.core.config
    log("test_2_config", True)
except Exception as e:
    log("test_2_config", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

try:
    import app.core.logging
    log("test_3_logging", True)
except Exception as e:
    log("test_3_logging", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

try:
    from agents.agent_registration import register_all_agents
    log("test_4_agents", True)
except Exception as e:
    log("test_4_agents", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

try:
    from app.api.routes import register_routes
    log("test_5_routes_init", True)
except Exception as e:
    log("test_5_routes_init", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Test 6: Import auth module directly
try:
    log("test_6_start_import_auth", True)
    import app.api.routes.auth
    log("test_6_import_auth", True)
except Exception as e:
    log("test_6_import_auth", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Test 7: Import app
try:
    log("test_7_start_import_app", True)
    import app.core.app
    log("test_7_import_app", True, {"routes": len(app.core.app.app.routes)})
except Exception as e:
    log("test_7_import_app", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

result["final_status"] = "completed"
with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("Done!")
