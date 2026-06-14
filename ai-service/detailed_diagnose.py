# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import traceback
import logging

SCRIPT_DIR = r"D:\aiphxt-app\ai-service"
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
RESULT_FILE = os.path.join(SCRIPT_DIR, "detailed_diagnose.json")

logger = logging.getLogger(__name__)

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

# Step 1: FastAPI basic imports
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    log("step_1_fastapi", True)
except Exception as e:
    log("step_1_fastapi", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 2: rate_limit_middleware
try:
    from app.api.middlewares.rate_limit import rate_limit_middleware
    log("step_2_rate_limit", True)
except Exception as e:
    log("step_2_rate_limit", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 3: config
try:
    from app.core.config import APP_NAME, APP_VERSION, DEBUG, ALLOWED_ORIGINS
    log("step_3_config", True)
except Exception as e:
    log("step_3_config", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 4: trace_middleware
try:
    from app.core.trace_middleware import TraceMiddleware
    log("step_4_trace_middleware", True)
except Exception as e:
    log("step_4_trace_middleware", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 5: logging
try:
    import app.core.logging
    log("step_5_logging", True)
except Exception as e:
    log("step_5_logging", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 6: agents (with try-except)
try:
    log("step_6_start_agents", True)
    try:
        from agents.agent_registration import register_all_agents
        register_all_agents()
        log("step_6_agents", True)
    except Exception as e:
        log("step_6_agents", True, {"note": f"agents failed but continuing: {e}"})
except Exception as e:
    log("step_6_agents", True, {"note": f"agents failed: {e}"})

# Step 7: Create app instance
try:
    app = FastAPI(title="test", version="1.0")
    log("step_7_create_app", True)
except Exception as e:
    log("step_7_create_app", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# Step 8: audit_middleware
try:
    from app.core.audit_middleware import AuditMiddleware
    log("step_8_audit", True)
except Exception as e:
    log("step_8_audit", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Step 9: prometheus_middleware
try:
    from app.core.prometheus_middleware import PrometheusMiddleware
    log("step_9_prometheus", True)
except Exception as e:
    log("step_9_prometheus", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Step 10: register_routes
try:
    log("step_10_start_routes", True)
    from app.api.routes import register_routes
    log("step_10_import_routes", True)
    register_routes(app)
    log("step_10_register_routes", True, {"routes_count": len(app.routes)})
except Exception as e:
    log("step_10_routes", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Step 11: exception_handlers
try:
    from app.core.exception_handlers import register_exception_handlers
    register_exception_handlers(app)
    log("step_11_exception", True)
except Exception as e:
    log("step_11_exception", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Step 12: Test register endpoint
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    import time as t
    username = f"final_test_{int(t.time())}"
    phone = f"135{int(t.time()) % 100000000:08d}"
    
    response = client.post("/api/user/register", json={
        "username": username,
        "password": "test123456",
        "email": f"{username}@test.com",
        "phone": phone,
        "role": "student"
    })
    
    try:
        resp_json = response.json()
    except:
        resp_json = response.text
    
    log("step_12_test_register", True, {
        "status_code": response.status_code,
        "response": resp_json
    })
except Exception as e:
    log("step_12_test_register", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

result["final_status"] = "completed"
with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n=== Diagnosis Complete ===")
