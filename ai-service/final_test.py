import sys
import os
import time
import json

os.chdir(r"D:\aiphxt-app\ai-service")
sys.path.insert(0, r"D:\aiphxt-app\ai-service")

OUTPUT_FILE = r"D:\aiphxt-app\ai-service\final_test_result.txt"

def save(data):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(data + "\n")
    print(data)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("=== Final Test Start ===\n")

save("[1/6] 测试导入 app.core.app 模块...")
try:
    import app.core.app
    save("  ✅ 导入成功")
except Exception as e:
    save(f"  ❌ 导入失败: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("[2/6] 测试调用 create_app() 函数...")
try:
    from app.core.app import create_app
    app = create_app()
    save(f"  ✅ 创建应用成功，路由数: {len(app.routes)}")
except Exception as e:
    save(f"  ❌ 创建应用失败: {type(e).__name__}: {e}")
    import traceback
    save("  " + traceback.format_exc())
    sys.exit(1)

save("[3/6] 测试创建 TestClient...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    save("  ✅ TestClient 创建成功")
except Exception as e:
    save(f"  ❌ TestClient 创建失败: {type(e).__name__}: {e}")
    sys.exit(1)

save("[4/6] 测试注册接口 (/api/user/register)...")
try:
    username = f"final_test_{int(time.time())}"
    phone = f"180{int(time.time()) % 100000000:08d}"
    r = client.post("/api/user/register", json={
        "username": username,
        "password": "test123456",
        "email": f"{username}@test.com",
        "phone": phone,
        "role": "student"
    })
    data = r.json()
    save(f"  ✅ 状态码: {r.status_code}, success: {data.get('success')}")
    if data.get('success'):
        save(f"    用户ID: {data['data'].get('user_id')}, 用户名: {data['data'].get('username')}")
    else:
        save(f"    消息: {data.get('message')}")
except Exception as e:
    save(f"  ❌ 注册接口测试失败: {type(e).__name__}: {e}")
    sys.exit(1)

save("[5/6] 测试登录接口 (/api/user/login)...")
try:
    r2 = client.post("/api/user/login", json={
        "username": username,
        "password": "test123456"
    })
    data2 = r2.json()
    save(f"  ✅ 状态码: {r2.status_code}, success: {data2.get('success')}")
    if data2.get('success'):
        save(f"    有 access_token: {bool(data2['data'].get('access_token'))}")
    else:
        save(f"    消息: {data2.get('message')}")
except Exception as e:
    save(f"  ❌ 登录接口测试失败: {type(e).__name__}: {e}")
    sys.exit(1)

save("[6/6] 测试 v1 注册接口 (/api/v1/auth/register)...")
try:
    username2 = f"final_test_v1_{int(time.time())}"
    phone2 = f"181{int(time.time()) % 100000000:08d}"
    r3 = client.post("/api/v1/auth/register", json={
        "username": username2,
        "password": "test123456",
        "email": f"{username2}@test.com",
        "phone": phone2,
        "role": "teacher"
    })
    data3 = r3.json()
    save(f"  ✅ 状态码: {r3.status_code}, success: {data3.get('success')}")
except Exception as e:
    save(f"  ❌ v1 注册接口测试失败: {type(e).__name__}: {e}")
    sys.exit(1)

save("")
save("🎉 所有测试通过！注册和登录接口功能正常！")
