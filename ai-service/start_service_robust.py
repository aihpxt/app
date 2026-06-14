#!/usr/bin/env python3
"""
启动服务脚本 - 使用循环确保服务持续运行
"""

import os
import sys
import subprocess
import time
import signal

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
    
    # 从配置文件中获取主机和端口配置
    import importlib.util
    try:
        spec = importlib.util.spec_from_file_location("config", os.path.join(os.path.dirname(__file__), "app", "core", "config.py"))
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        host = config.HOST
        port = config.PORT
    except Exception as e:
        print(f"读取配置失败: {e}")
        host = "0.0.0.0"
        port = 8001
    
    process = None
    
    while True:
        try:
            print(f"启动 uvicorn 服务于 {host}:{port}...")
            
            # 创建新进程
            process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.core.app:app", "--host", host, "--port", str(port), "--log-level", "info"],
                cwd=os.path.dirname(__file__),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            print(f"服务进程 PID: {process.pid}")
            
            # 持续监控服务输出
            while process.poll() is None:
                try:
                    line = process.stdout.readline()
                    if line:
                        print(line.strip())
                except:
                    break
            
            # 如果进程退出，等待一下再重启
            return_code = process.poll() if process else None
            if return_code is not None:
                print(f"服务意外退出，退出码: {return_code}")
                print("5秒后重新启动...")
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n接收到停止信号，正在关闭服务...")
            if process and process.poll() is None:
                process.terminate()
                process.wait(timeout=5)
            sys.exit(0)
        except Exception as e:
            print(f"服务启动失败: {e}")
            print("5秒后重新启动...")
            time.sleep(5)

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
