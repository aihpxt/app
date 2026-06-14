# -*- coding: utf-8 -*-
import os
import sys
import json
import traceback
import time

SCRIPT_DIR = r"D:\aiphxt-app\ai-service"
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
RESULT_FILE = os.path.join(SCRIPT_DIR, "debug_step_result.json")

result = {
    "steps": [],
    "final_status": "unknown"
}

def log(step_name, success=True, data=None, error=None):
    entry = {
        "step": step_name,
        "success": success,
        "timestamp": time.time()
    }
    if data:
        entry["data"] = data
    if error:
        entry["error"] = error
    result["steps"].append(entry)
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[{step_name}] {'OK' if success else 'FAILED'}")

# Step 1: Basic Python
log("step_1_python_check", True, {"python_version": sys.version, "working_dir": os.getcwd()})

# Step 2: Import FastAPI
try:
    import fastapi
    log("step_2_import_fastapi", True, {"version": fastapi.__version__})
except Exception as e:
    log("step_2_import_fastapi", False, error=f"{type(e).__name__}: {e}")
    result["final_status"] = "failed"
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    sys.exit(1)

# Step 3: Import database module
try:
    from app.core.database_pool import get_db_manager, DATABASE_URL
    db_manager = get_db_manager()
    log("step_3_database_pool", True, {"database_url": DATABASE_URL})
except Exception as e:
    log("step_3_database_pool", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    result["final_status"] = "failed"
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    sys.exit(1)

# Step 4: Import models
try:
    from app.models.user import User
    log("step_4_import_user_model", True, {"tablename": User.__tablename__})
except Exception as e:
    log("step_4_import_user_model", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    result["final_status"] = "failed"
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    sys.exit(1)

# Step 5: Import auth functions
try:
    from app.api.routes.auth import register, RegisterRequest, Role
    log("step_5_import_auth", True, {"roles": [r.value for r in Role]})
except Exception as e:
    log("step_5_import_auth", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    result["final_status"] = "failed"
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    sys.exit(1)

# Step 6: Test register function directly
try:
    import bcrypt
    from app.core.database_pool import get_db_manager
    from app.models.user import User
    import time as t

    session = None
    username = f"direct_func_test_{int(t.time())}"
    phone = f"136{int(t.time()) % 100000000:08d}"

    # Call the register function directly
    request_data = type('RegisterRequest', (), {
        'username': username,
        'password': 'password123',
        'email': f"{username}@test.com",
        'phone': phone,
        'role': 'student'
    })()

    # Actually create the user using the same logic as register
    db_manager = get_db_manager()
    session = db_manager.get_session()
    password_hash = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(
        username=username,
        password_hash=password_hash,
        email=f"{username}@test.com",
        phone=phone,
        role='student'
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    user_id = new_user.id
    session.close()

    log("step_6_direct_user_creation", True, {
        "created_user": username,
        "user_id": user_id
    })
except Exception as e:
    log("step_6_direct_user_creation", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    if 'session' in dir() and session:
        try:
            session.rollback()
            session.close()
        except:
            pass

# Step 7: Import app
try:
    log("step_7_start_import_app", True)
    from app.core.app import app
    log("step_7_import_app", True, {"routes_count": len(app.routes)})
except Exception as e:
    log("step_7_import_app", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    result["final_status"] = "failed"
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    sys.exit(1)

# Step 8: TestClient
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    log("step_8_test_health", True, {
        "status_code": response.status_code,
        "response": response.json()
    })
except Exception as e:
    log("step_8_test_health", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Step 9: Test register endpoint
try:
    username = f"endpoint_test_{int(time.time())}"
    phone = f"137{int(time.time()) % 100000000:08d}"
    response = client.post("/api/user/register", json={
        "username": username,
        "password": "password123",
        "email": f"{username}@test.com",
        "phone": phone,
        "role": "student"
    })
    try:
        response_json = response.json()
    except:
        response_json = {"raw": response.text}
    log("step_9_test_register", True, {
        "status_code": response.status_code,
        "response": response_json
    })
except Exception as e:
    log("step_9_test_register", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

result["final_status"] = "completed"
with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("All steps completed!")
