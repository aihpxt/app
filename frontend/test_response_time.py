import requests
import time

# 测试前端的响应时间
start_time = time.time()
try:
    response = requests.get("http://localhost:3000/")
    end_time = time.time()
    response_time = end_time - start_time
    print(f"响应时间: {response_time} 秒")
    print(f"状态码: {response.status_code}")
except Exception as e:
    end_time = time.time()
    response_time = end_time - start_time
    print(f"响应时间: {response_time} 秒")
    print(f"错误: {str(e)}")
