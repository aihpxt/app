# -*- coding: utf-8 -*-
import os
import sys
import json

SCRIPT_DIR = r"D:\aiphxt-app\ai-service"
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from app.core.database_pool import DatabaseManager, Base
from app.models.user import User

RESULT_FILE = os.path.join(SCRIPT_DIR, "db_check_result.json")
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

# Step 1: Check current database
try:
    db_manager = DatabaseManager()
    log("step_1_db_manager", True)
    
    # Check database file location
    log("step_2_db_path", True, {"database_url": str(db_manager.database_url)})
    
    # Step 3: Check existing users table structure
    with db_manager.engine.connect() as conn:
        try:
            # Try to query users table
            from sqlalchemy import text
            result_proxy = conn.execute(text("PRAGMA table_info(users)"))
            columns = []
            for row in result_proxy:
                columns.append({
                    "cid": row[0],
                    "name": row[1],
                    "type": row[2],
                    "notnull": row[3],
                    "dflt_value": row[4],
                    "pk": row[5]
                })
            log("step_3_check_users_table", True, {"columns": columns})
        except Exception as e:
            log("step_3_check_users_table", False, error=str(e))
except Exception as e:
    log("step_1_db_manager", False, error=str(e))

# Step 4: Recreate users table with correct structure
try:
    # Drop existing users table (if exists) and recreate
    with db_manager.engine.connect() as conn:
        try:
            conn.execute(text("DROP TABLE IF EXISTS users"))
            conn.commit()
            log("step_4_drop_table", True)
        except Exception as e:
            log("step_4_drop_table", False, error=str(e))
        
        # Create new users table
        Base.metadata.create_all(bind=db_manager.engine, tables=[User.__table__])
        log("step_5_create_table", True)
        
        # Verify new table structure
        result_proxy = conn.execute(text("PRAGMA table_info(users)"))
        new_columns = []
        for row in result_proxy:
            new_columns.append({
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": row[3],
                "dflt_value": row[4],
                "pk": row[5]
            })
        log("step_6_verify_new_table", True, {"columns": new_columns})
except Exception as e:
    import traceback
    log("step_recreate_error", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

# Step 7: Test register with new database
try:
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    from app.api.routes.auth import router as auth_router, login, register
    from fastapi import APIRouter
    
    test_app = FastAPI()
    test_app.include_router(auth_router)
    
    user_router = APIRouter(prefix="/api/user", tags=["用户"])
    user_router.add_api_route("/login", login, methods=["POST"])
    user_router.add_api_route("/register", register, methods=["POST"])
    test_app.include_router(user_router)
    
    client = TestClient(test_app)
    
    import time as t
    username = f"db_test_{int(t.time())}"
    phone = f"137{int(t.time()) % 100000000:08d}"
    
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
        resp_data = {"text": response.text[:300]}
    
    log("step_7_test_register", True, {
        "status_code": response.status_code,
        "response": resp_data
    })
    
    # Test login
    response2 = client.post("/api/user/login", json={
        "username": username,
        "password": "test123456"
    })
    
    try:
        resp_data2 = response2.json()
    except:
        resp_data2 = {"text": response2.text[:300]}
    
    log("step_8_test_login", True, {
        "status_code": response2.status_code,
        "response": resp_data2
    })
except Exception as e:
    import traceback
    log("step_test_error", False, error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

result["final_status"] = "completed"
with open(RESULT_FILE, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n=== DB Check Complete ===")
