import sys
import os
import time

os.chdir(r"D:\aiphxt-app\ai-service")
sys.path.insert(0, r"D:\aiphxt-app\ai-service")

OUTPUT_FILE = r"D:\aiphxt-app\ai-service\step_test.txt"

def save(data):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(data + "\n")
        f.flush()
        os.fsync(f.fileno())

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("=== Step-by-Step Test ===\n")
    f.flush()

save("Step 1: Importing FastAPI...")
try:
    from fastapi import FastAPI
    save("  OK")
except Exception as e:
    save(f"  FAIL: {type(e).__name__}: {e}")
    sys.exit(1)

save("Step 2: Importing CORSMiddleware...")
try:
    from fastapi.middleware.cors import CORSMiddleware
    save("  OK")
except Exception as e:
    save(f"  FAIL: {type(e).__name__}: {e}")
    sys.exit(1)

save("Step 3: Importing database_pool...")
try:
    from app.core.database_pool import get_db_manager
    save("  OK")
except Exception as e:
    save(f"  FAIL: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("Step 4: Creating basic FastAPI app...")
try:
    app = FastAPI(title="Test", version="1.0")
    save(f"  OK, routes: {len(app.routes)}")
except Exception as e:
    save(f"  FAIL: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("Step 5: Initializing DB...")
try:
    get_db_manager()
    save("  OK")
except Exception as e:
    save(f"  FAIL: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("Step 6: Importing auth router...")
try:
    from app.api.routes.auth import router as auth_router
    save("  OK")
except Exception as e:
    save(f"  FAIL: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("Step 7: Including auth router...")
try:
    app.include_router(auth_router)
    save(f"  OK, routes: {len(app.routes)}")
except Exception as e:
    save(f"  FAIL: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("Step 8: Creating TestClient...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    save("  OK")
except Exception as e:
    save(f"  FAIL: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("Step 9: Testing register API...")
try:
    username = f"step_test_{int(time.time())}"
    phone = f"175{int(time.time()) % 100000000:08d}"
    r = client.post("/api/v1/auth/register", json={
        "username": username,
        "password": "test123456",
        "email": f"{username}@test.com",
        "phone": phone,
        "role": "student"
    })
    data = r.json()
    save(f"  OK - Status: {r.status_code}, Success: {data.get('success')}")
    if data.get('success'):
        save(f"     User: {data['data'].get('username')}, ID: {data['data'].get('user_id')}")
    else:
        save(f"     Message: {data.get('message')}")
except Exception as e:
    save(f"  FAIL: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("Step 10: Testing login API...")
try:
    r2 = client.post("/api/v1/auth/login", json={
        "username": username,
        "password": "test123456"
    })
    data2 = r2.json()
    save(f"  OK - Status: {r2.status_code}, Success: {data2.get('success')}")
    if data2.get('success'):
        save(f"     Has access_token: {bool(data2['data'].get('access_token'))}")
except Exception as e:
    save(f"  FAIL: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("")
save("=== All 10 steps completed successfully! ===")
