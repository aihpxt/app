#!/usr/bin/env python3
"""
回滚验证脚本
"""

import requests
import sqlite3
import redis
import time

def check_health():
    """检查服务健康状态"""
    try:
        response = requests.get('http://localhost:8001/api/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data', {}).get('status') == 'healthy':
                return True, "API服务健康检查通过"
            else:
                return False, f"API服务状态异常: {data}"
        else:
            return False, f"API服务响应异常: {response.status_code}"
    except Exception as e:
        return False, f"API服务健康检查失败: {e}"

def check_database():
    """检查数据库连接"""
    try:
        conn = sqlite3.connect('data/school_platform.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM schools")
        count = cursor.fetchone()[0]
        conn.close()
        return True, f"数据库连接正常，包含 {count} 条学校记录"
    except Exception as e:
        return False, f"数据库连接失败: {e}"

def check_redis():
    """检查Redis连接"""
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        response = r.ping()
        if response:
            return True, "Redis连接正常"
        else:
            return False, "Redis连接异常"
    except Exception as e:
        return False, f"Redis连接失败: {e}"

def main():
    print("=== 回滚验证开始 ===")
    
    print("等待服务启动...")
    time.sleep(15)
    
    checks = [
        check_health,
        check_database,
        check_redis
    ]
    
    all_passed = True
    for check in checks:
        success, msg = check()
        print(f"[{check.__name__}] {msg}")
        if not success:
            all_passed = False
    
    print("=== 回滚验证结束 ===")
    
    if all_passed:
        print("✓ 所有验证项均通过")
        return 0
    else:
        print("✗ 部分验证项未通过")
        return 1

if __name__ == "__main__":
    exit(main())
