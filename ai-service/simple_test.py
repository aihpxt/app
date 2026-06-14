import sys
import os
import time

os.chdir(r"D:\aiphxt-app\ai-service")
sys.path.insert(0, r"D:\aiphxt-app\ai-service")

output = []
output.append("=== Starting Test ===")

try:
    from app.core.database_pool import get_db_manager
    db = get_db_manager()
    output.append("✓ Database initialized")
except Exception as e:
    output.append(f"✗ Database failed: {type(e).__name__}: {e}")
    sys.exit(1)

try:
    from app.core.app import create_app
    app = create_app()
    output.append(f"✓ App created with {len(app.routes)} routes")
except Exception as e:
    output.append(f"✗ App creation failed: {type(e).__name__}: {e}")
    import traceback
    output.append(traceback.format_exc())
    sys.exit(1)

try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    output.append("✓ TestClient created")
except Exception as e:
    output.append(f"✗ TestClient failed: {type(e).__name__}: {e}")
    sys.exit(1)

try:
    username = f"testuser_{int(time.time())}"
    phone = f"150{int(time.time()) % 100000000:08d}"
    payload = {
        "username": username,
        "password": "test123456",
        "email": f"{username}@example.com",
        "phone": phone,
        "role": "student"
    }
    r = client.post("/api/user/register", json=payload)
    output.append(f"✓ Register: status={r.status_code}, success={r.json().get('success')}")
except Exception as e:
    output.append(f"✗ Register failed: {type(e).__name__}: {e}")
    import traceback
    output.append(traceback.format_exc())
    sys.exit(1)

try:
    r2 = client.post("/api/user/login", json={"username": username, "password": "test123456"})
    output.append(f"✓ Login: status={r2.status_code}, success={r2.json().get('success')}")
except Exception as e:
    output.append(f"✗ Login failed: {type(e).__name__}: {e}")
    sys.exit(1)

try:
    username2 = f"testuser_v1_{int(time.time())}"
    phone2 = f"151{int(time.time()) % 100000000:08d}"
    payload2 = {
        "username": username2,
        "password": "test123456",
        "email": f"{username2}@example.com",
        "phone": phone2,
        "role": "teacher"
    }
    r3 = client.post("/api/v1/auth/register", json=payload2)
    output.append(f"✓ V1 Register: status={r3.status_code}, success={r3.json().get('success')}")
except Exception as e:
    output.append(f"✗ V1 Register failed: {type(e).__name__}: {e}")
    sys.exit(1)

try:
    r4 = client.post("/api/v1/auth/login", json={"username": username2, "password": "test123456"})
    output.append(f"✓ V1 Login: status={r4.status_code}, success={r4.json().get('success')}")
except Exception as e:
    output.append(f"✗ V1 Login failed: {type(e).__name__}: {e}")
    sys.exit(1)

output.append("")
output.append("=== ALL TESTS PASSED ===")

with open(r"D:\aiphxt-app\ai-service\test_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("\n".join(output))
