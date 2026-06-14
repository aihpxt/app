#!/usr/bin/env python3
"""
启动服务脚本
"""

import os
import sys
import subprocess
import time

# 检查数据库表结构
def check_database():
    print("检查数据库表结构...")
    try:
        result = subprocess.run([sys.executable, "fix_database.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        print(result.stdout)
        if result.stderr:
            print(f"数据库检查错误: {result.stderr}")
        return True
    except Exception as e:
        print(f"数据库检查失败: {e}")
        return False

# 检查 Redis 服务
def check_redis():
    print("检查 Redis 服务...")
    try:
        result = subprocess.run([sys.executable, "check_redis.py"], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        print(result.stdout)
        if result.stderr:
            print(f"Redis 检查错误: {result.stderr}")
        return "Redis 服务可用" in result.stdout
    except Exception as e:
        print(f"Redis 检查失败: {e}")
        return False

# 启动服务
def start_service():
    print("启动 FastAPI 服务...")
    try:
        # 从配置文件中获取主机和端口配置
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", os.path.join(os.path.dirname(__file__), "app", "core", "config.py"))
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        # 使用子进程启动 uvicorn 服务，以便查看完整的启动日志
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.core.app:app", "--host", config.HOST, "--port", str(config.PORT), "--log-level", "info"],
            cwd=os.path.dirname(__file__),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        # 持续监控服务输出
        while process.poll() is None:
            line = process.stdout.readline()
            if line:
                print(line.strip())
        
        return True
    except Exception as e:
        print(f"服务启动失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("====================================")
    print("          启动 AI 服务")
    print("====================================")
    
    # 检查数据库
    if not check_database():
        print("数据库检查失败，服务可能无法正常运行！")
    
    # 检查 Redis
    redis_available = check_redis()
    if not redis_available:
        print("[WARN] Redis 服务不可用，系统将使用内存缓存")
        print("[WARN] 建议安装并启动 Redis 服务以获得更好的性能")
        print("[WARN] 请参考 install_redis_guide.md 进行安装配置")
    
    print("====================================")
    print("开始启动服务...")
    print("====================================")
    
    # 启动服务
    start_service()
