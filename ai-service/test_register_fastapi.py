import os
import sys

os.chdir(r'D:\aiphxt-app\ai-service')

print('=== 在 FastAPI 应用上下文中测试注册 ===')

# 模拟 FastAPI 启动过程
from app.core.app import app
from fastapi.testclient import TestClient

client = TestClient(app)

# 首先测试健康检查
print('\n1. 测试健康检查 /health')
try:
    response = client.get('/health')
    print(f'   状态: {response.status_code}')
    print(f'   响应: {response.text[:300]}')
except Exception as e:
    print(f'   错误: {e}')

# 测试 /api/user/login 以检查路由是否存在
print('\n2. 测试登录路由')
try:
    response = client.post(
        '/api/user/login',
        json={'username': 'nonexistent', 'password': 'wrong'},
        headers={'Content-Type': 'application/json'}
    )
    print(f'   状态: {response.status_code}')
    print(f'   响应: {response.text[:300]}')
except Exception as e:
    print(f'   错误: {e}')
    import traceback
    traceback.print_exc()

# 测试注册
print('\n3. 测试注册接口 /api/user/register')
import time
username = 'test_fastapi_' + str(int(time.time()))
try:
    response = client.post(
        '/api/user/register',
        json={
            'username': username,
            'password': 'test123456',
            'email': username + '@example.com',
            'phone': '139' + str(int(time.time()))[-8:],
            'role': 'student'
        },
        headers={'Content-Type': 'application/json'}
    )
    print(f'   状态: {response.status_code}')
    print(f'   响应: {response.text[:500]}')
except Exception as e:
    print(f'   错误: {e}')
    import traceback
    traceback.print_exc()

# 检查数据库配置
print('\n4. 检查数据库配置')
from app.core.database_pool import get_db_manager, DATABASE_URL
db_manager = get_db_manager()
print(f'   数据库 URL: {DATABASE_URL}')
print(f'   实际数据库 URL: {db_manager.database_url}')
print(f'   当前工作目录: {os.getcwd()}')

# 打印所有已注册的路由
print('\n5. 检查已注册的路由 (user 相关):')
for route in app.routes:
    path = getattr(route, 'path', '')
    if 'user' in path or 'auth' in path or 'register' in path or 'login' in path:
        methods = getattr(route, 'methods', set())
        print(f'   {list(methods)} {path}')
