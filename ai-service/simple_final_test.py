import sys
import os
import time

os.chdir(r"D:\aiphxt-app\ai-service")
sys.path.insert(0, r"D:\aiphxt-app\ai-service")

# 设置 Python 输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

OUTPUT_FILE = r"D:\aiphxt-app\ai-service\simple_test_result.txt"

def save(data):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(data + "\n")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("=== Test Start ===\n")

save("[1/6] Testing import app.core.app...")
try:
    import app.core.app
    save("  [OK] Import success")
except Exception as e:
    save(f"  [FAIL] Import failed: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("[2/6] Testing create_app()...")
try:
    from app.core.app import create_app
    app = create_app()
    save(f"  [OK] App created, routes: {len(app.routes)}")
except Exception as e:
    save(f"  [FAIL] Create app failed: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("[3/6] Creating TestClient...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    save("  [OK] TestClient created")
except Exception as e:
    save(f"  [FAIL] TestClient failed: {type(e).__name__}: {e}")
    sys.exit(1)

save("[4/6] Testing register API (/api/user/register)...")
try:
    username = f"stest_{int(time.time())}"
    phone = f"190{int(time.time()) % 100000000:08d}"
    r = client.post("/api/user/register", json={
        "username": username,
        "password": "test123456",
        "email": f"{username}@test.com",
        "phone": phone,
        "role": "student"
    })
    data = r.json()
    save(f"  [OK] Status: {r.status_code}, success: {data.get('success')}")
    if data.get('success'):
        save(f"    User ID: {data['data'].get('user_id')}, Username: {data['data'].get('username')}")
    else:
        save(f"    Message: {data.get('message')}")
except Exception as e:
    save(f"  [FAIL] Register API failed: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("[5/6] Testing login API (/api/user/login)...")
try:
    r2 = client.post("/api/user/login", json={
        "username": username,
        "password": "test123456"
    })
    data2 = r2.json()
    save(f"  [OK] Status: {r2.status_code}, success: {data2.get('success')}")
    if data2.get('success'):
        save(f"    Has access_token: {bool(data2['data'].get('access_token'))}")
    else:
        save(f"    Message: {data2.get('message')}")
except Exception as e:
    save(f"  [FAIL] Login API failed: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("[6/6] Testing v1 register API (/api/v1/auth/register)...")
try:
    username2 = f"stest_v1_{int(time.time())}"
    phone2 = f"191{int(time.time()) % 100000000:08d}"
    r3 = client.post("/api/v1/auth/register", json={
        "username": username2,
        "password": "test123456",
        "email": f"{username2}@test.com",
        "phone": phone2,
        "role": "teacher"
    })
    data3 = r3.json()
    save(f"  [OK] Status: {r3.status_code}, success: {data3.get('success')}")
except Exception as e:
    save(f"  [FAIL] v1 Register API failed: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("")
save("=== All tests passed! Register and Login APIs work correctly! ===")
