import sys
import os

os.chdir(r"D:\aiphxt-app\ai-service")
sys.path.insert(0, r"D:\aiphxt-app\ai-service")

output_lines = []

def log(msg):
    print(msg)
    output_lines.append(msg)

try:
    from app.core.database_pool import get_db_manager
    db = get_db_manager()
    log("DB_OK")
except Exception as e:
    log(f"DB_ERR: {type(e).__name__}: {e}")
    with open(r"D:\aiphxt-app\ai-service\verify_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    sys.exit(1)

try:
    from app.core.app import create_app
    app = create_app()
    log(f"APP_OK_{len(app.routes)}")
except Exception as e:
    log(f"APP_ERR: {type(e).__name__}: {e}")
    import traceback
    log(traceback.format_exc())
    with open(r"D:\aiphxt-app\ai-service\verify_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    sys.exit(1)

try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    log("CLIENT_OK")
except Exception as e:
    log(f"CLIENT_ERR: {type(e).__name__}: {e}")
    with open(r"D:\aiphxt-app\ai-service\verify_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    sys.exit(1)

import time
try:
    username = f"t_{int(time.time())}"
    phone = f"160{int(time.time()) % 100000000:08d}"
    r = client.post("/api/user/register", json={
        "username": username,
        "password": "test123456",
        "email": f"{username}@x.com",
        "phone": phone,
        "role": "student"
    })
    data = r.json()
    log(f"REGISTER_{r.status_code}_{data.get('success')}")
except Exception as e:
    log(f"REGISTER_ERR: {type(e).__name__}: {e}")
    with open(r"D:\aiphxt-app\ai-service\verify_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    sys.exit(1)

try:
    r2 = client.post("/api/user/login", json={
        "username": username,
        "password": "test123456"
    })
    data2 = r2.json()
    log(f"LOGIN_{r2.status_code}_{data2.get('success')}")
except Exception as e:
    log(f"LOGIN_ERR: {type(e).__name__}: {e}")
    with open(r"D:\aiphxt-app\ai-service\verify_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    sys.exit(1)

try:
    username2 = f"tv1_{int(time.time())}"
    phone2 = f"161{int(time.time()) % 100000000:08d}"
    r3 = client.post("/api/v1/auth/register", json={
        "username": username2,
        "password": "test123456",
        "email": f"{username2}@x.com",
        "phone": phone2,
        "role": "teacher"
    })
    data3 = r3.json()
    log(f"V1REGISTER_{r3.status_code}_{data3.get('success')}")
except Exception as e:
    log(f"V1REGISTER_ERR: {type(e).__name__}: {e}")
    with open(r"D:\aiphxt-app\ai-service\verify_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    sys.exit(1)

try:
    r4 = client.post("/api/v1/auth/login", json={
        "username": username2,
        "password": "test123456"
    })
    data4 = r4.json()
    log(f"V1LOGIN_{r4.status_code}_{data4.get('success')}")
except Exception as e:
    log(f"V1LOGIN_ERR: {type(e).__name__}: {e}")
    with open(r"D:\aiphxt-app\ai-service\verify_output.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    sys.exit(1)

log("ALL_PASSED")
with open(r"D:\aiphxt-app\ai-service\verify_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))
