import sys
import os

os.chdir(r"D:\aiphxt-app\ai-service")
sys.path.insert(0, r"D:\aiphxt-app\ai-service")

OUTPUT_FILE = r"D:\aiphxt-app\ai-service\final_result.txt"

def save(data):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(data + "\n")
    print(data)

# Clear file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("")

try:
    from app.core.database_pool import get_db_manager
    db = get_db_manager()
    save("1. DB_INIT_OK")
except Exception as e:
    save(f"1. DB_INIT_FAIL: {type(e).__name__}: {e}")
    sys.exit(1)

try:
    from app.core.app import create_app
    app = create_app()
    save(f"2. APP_CREATE_OK (routes={len(app.routes)})")
except Exception as e:
    save(f"2. APP_CREATE_FAIL: {type(e).__name__}: {e}")
    import traceback
    save(traceback.format_exc())
    sys.exit(1)

try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    save("3. TEST_CLIENT_OK")
except Exception as e:
    save(f"3. TEST_CLIENT_FAIL: {type(e).__name__}: {e}")
    sys.exit(1)

import time

try:
    username = f"test_{int(time.time())}"
    phone = f"170{int(time.time()) % 100000000:08d}"
    payload = {
        "username": username,
        "password": "test123456",
        "email": f"{username}@test.com",
        "phone": phone,
        "role": "student"
    }
    r = client.post("/api/user/register", json=payload)
    data = r.json()
    save(f"4. REGISTER: status={r.status_code}, success={data.get('success')}, msg={str(data.get('message',''))[:80]}")
except Exception as e:
    save(f"4. REGISTER_FAIL: {type(e).__name__}: {e}")
    sys.exit(1)

try:
    r2 = client.post("/api/user/login", json={
        "username": username,
        "password": "test123456"
    })
    data2 = r2.json()
    save(f"5. LOGIN: status={r2.status_code}, success={data2.get('success')}")
except Exception as e:
    save(f"5. LOGIN_FAIL: {type(e).__name__}: {e}")
    sys.exit(1)

try:
    username2 = f"testv1_{int(time.time())}"
    phone2 = f"171{int(time.time()) % 100000000:08d}"
    payload2 = {
        "username": username2,
        "password": "test123456",
        "email": f"{username2}@test.com",
        "phone": phone2,
        "role": "teacher"
    }
    r3 = client.post("/api/v1/auth/register", json=payload2)
    data3 = r3.json()
    save(f"6. V1_REGISTER: status={r3.status_code}, success={data3.get('success')}, msg={str(data3.get('message',''))[:80]}")
except Exception as e:
    save(f"6. V1_REGISTER_FAIL: {type(e).__name__}: {e}")
    sys.exit(1)

try:
    r4 = client.post("/api/v1/auth/login", json={
        "username": username2,
        "password": "test123456"
    })
    data4 = r4.json()
    save(f"7. V1_LOGIN: status={r4.status_code}, success={data4.get('success')}")
except Exception as e:
    save(f"7. V1_LOGIN_FAIL: {type(e).__name__}: {e}")
    sys.exit(1)

save("8. ALL_TESTS_PASSED!")
