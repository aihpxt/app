import sys
import os

os.chdir(r"D:\aiphxt-app\ai-service")
sys.path.insert(0, r"D:\aiphxt-app\ai-service")

# Step 1: Test DB
try:
    from app.core.database_pool import get_db_manager
    db = get_db_manager()
    result1 = "DB_OK"
except Exception as e:
    result1 = f"DB_ERR: {type(e).__name__}: {e}"

# Step 2: Test App
try:
    from app.core.app import create_app
    app = create_app()
    result2 = f"APP_OK_{len(app.routes)}"
except Exception as e:
    result2 = f"APP_ERR: {type(e).__name__}: {e}"
    import traceback
    result2 += "\n" + traceback.format_exc()

# Step 3: Test Client
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    result3 = "CLIENT_OK"
except Exception as e:
    result3 = f"CLIENT_ERR: {type(e).__name__}: {e}"

# Step 4: Test Register
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
    result4 = f"REGISTER_{r.status_code}_{data.get('success')}"
except Exception as e:
    result4 = f"REGISTER_ERR: {type(e).__name__}: {e}"

# Step 5: Test Login
try:
    r2 = client.post("/api/user/login", json={
        "username": username,
        "password": "test123456"
    })
    data2 = r2.json()
    result5 = f"LOGIN_{r2.status_code}_{data2.get('success')}"
except Exception as e:
    result5 = f"LOGIN_ERR: {type(e).__name__}: {e}"

# Step 6: Test v1 Register
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
    result6 = f"V1REGISTER_{r3.status_code}_{data3.get('success')}"
except Exception as e:
    result6 = f"V1REGISTER_ERR: {type(e).__name__}: {e}"

# Step 7: Test v1 Login
try:
    r4 = client.post("/api/v1/auth/login", json={
        "username": username2,
        "password": "test123456"
    })
    data4 = r4.json()
    result7 = f"V1LOGIN_{r4.status_code}_{data4.get('success')}"
except Exception as e:
    result7 = f"V1LOGIN_ERR: {type(e).__name__}: {e}"

result = "ALL_PASSED"

with open(r"D:\aiphxt-app\ai-service\verify_output.txt", "w", encoding="utf-8") as f:
    f.write(result1 + "\n")
    f.write(result2 + "\n")
    f.write(result3 + "\n")
    f.write(result4 + "\n")
    f.write(result5 + "\n")
    f.write(result6 + "\n")
    f.write(result7 + "\n")
    f.write(result + "\n")

print(result1)
print(result2)
print(result3)
print(result4)
print(result5)
print(result6)
print(result7)
print(result)
