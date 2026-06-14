#!/usr/bin/env python3
"""
服务重启脚本
"""

import subprocess
import time
import os

def stop_service(process_name):
    """停止服务"""
    try:
        result = subprocess.run(['pkill', '-f', process_name], capture_output=True)
        if result.returncode == 0:
            print(f"已停止服务: {process_name}")
        return result.returncode == 0
    except Exception as e:
        print(f"停止服务失败 {process_name}: {e}")
        return False

def start_service(service_cmd, log_file):
    """启动服务"""
    try:
        log_path = os.path.join('logs', log_file)
        with open(log_path, 'w') as f:
            subprocess.Popen(service_cmd, stdout=f, stderr=subprocess.STDOUT)
        print(f"已启动服务: {service_cmd[0]}")
        return True
    except Exception as e:
        print(f"启动服务失败 {service_cmd[0]}: {e}")
        return False

def main():
    services_to_stop = [
        "uvicorn main:app",
        "hermes_server.py",
        "monitor_service.py",
        "cache_warmer.py"
    ]
    
    for service in services_to_stop:
        stop_service(service)
    
    time.sleep(5)
    
    services_to_start = [
        (['python', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8001', '--workers', '4'], 'app.log'),
        (['python', 'hermes_server.py'], 'hermes.log'),
        (['python', 'monitor_service.py'], 'monitor.log'),
        (['python', 'cache_warmer.py'], 'cache_warmer.log')
    ]
    
    for cmd, log_file in services_to_start:
        start_service(cmd, log_file)
        time.sleep(3)
    
    print("所有服务已重启")

if __name__ == "__main__":
    main()
