import urllib.request
import urllib.parse
import json
import sys

BASE_URL = 'http://localhost:8000'

print('=== 测试 /api/user/register ===')

# 模拟前端发送的注册请求
data = {
    'username': 'test_http_' + str(sys.argv[1]) if len(sys.argv) > 1 else 'test_http_1',
    'password': 'test123456',
    'email': 'test_http@example.com',
    'phone': '13900000001',
    'role': 'student'
}

json_data = json.dumps(data).encode('utf-8')
print('请求数据:', json.dumps(data, ensure_ascii=False, indent=2))

req = urllib.request.Request(
    BASE_URL + '/api/user/register',
    data=json_data,
    headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    },
    method='POST'
)

try:
    response = urllib.request.urlopen(req, timeout=10)
    print('\n状态码:', response.status)
    body = response.read().decode('utf-8')
    print('响应内容:', body)
    print()
    
    try:
        parsed = json.loads(body)
        print('解析为 JSON 成功:', json.dumps(parsed, ensure_ascii=False, indent=2))
    except Exception as e:
        print('解析 JSON 失败:', e)
        
except urllib.error.HTTPError as e:
    print(f'\nHTTP 错误 {e.code}:')
    error_body = e.read().decode('utf-8')
    print('错误响应:', error_body)
    try:
        parsed = json.loads(error_body)
        print('解析为 JSON:', json.dumps(parsed, ensure_ascii=False, indent=2))
    except:
        pass
except Exception as e:
    print(f'\n其他错误: {e}')
    import traceback
    traceback.print_exc()

print()
print('=== 测试 /api/v1/auth/register ===')

data2 = {
    'username': 'test_auth_2',
    'password': 'test123456',
    'email': 'test_auth@example.com',
    'phone': '13900000002',
    'role': 'student'
}

req2 = urllib.request.Request(
    BASE_URL + '/api/v1/auth/register',
    data=json.dumps(data2).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    response2 = urllib.request.urlopen(req2, timeout=10)
    print('状态码:', response2.status)
    body2 = response2.read().decode('utf-8')
    print('响应内容:', body2)
except urllib.error.HTTPError as e:
    print(f'HTTP 错误 {e.code}:')
    error_body = e.read().decode('utf-8')
    print('错误响应:', error_body)
except Exception as e:
    print(f'其他错误: {e}')
