#!/usr/bin/env python3
"""
服务监控脚本
用于监控服务的运行状态，并在服务停止时自动重启
"""

import os
import sys
import subprocess
import time
import logging
import psutil

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(__file__), 'logs', 'monitor.log'),
    filemode='a'
)

# 服务配置
SERVICE_DIR = os.path.dirname(__file__)
CHECK_INTERVAL = 60  # 检查间隔，单位：秒
MAX_RESTARTS = 3  # 最大重启次数
RESTART_INTERVAL = 120  # 重启间隔，单位：秒

# 从配置文件中获取主机和端口配置
import importlib.util
config_path = os.path.join(os.path.dirname(__file__), "app", "core", "config.py")
if os.path.exists(config_path):
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    AI_SERVICE_PORT = config.PORT
else:
    AI_SERVICE_PORT = 8001

# 服务列表
SERVICES = [
    {
        "name": "AI Service",
        "command": [sys.executable, "start_service.py"],
        "check_port": AI_SERVICE_PORT,
        "check_pattern": "uvicorn.*app.core.app:app"
    },
    {
        "name": "Hermes Service",
        "command": [sys.executable, "hermes_server.py"],
        "check_port": 8888,
        "check_pattern": "uvicorn.*hermes_server:app"
    }
]

# 日志目录
LOG_DIR = os.path.join(SERVICE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

def check_service_running(service):
    """检查服务是否在运行"""
    try:
        # 检查进程是否在运行
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline']:
                    cmdline_str = ' '.join(proc.info['cmdline'])
                    if 'uvicorn' in cmdline_str and service['check_pattern'] in cmdline_str:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
    except Exception as e:
        logging.error(f"检查 {service['name']} 运行状态失败: {e}")
        return False

def start_service(service):
    """启动服务"""
    logging.info(f"启动 {service['name']}...")
    try:
        # 启动服务，将输出重定向到日志文件
        log_file = os.path.join(LOG_DIR, f"{service['name'].lower().replace(' ', '_')}.log")
        with open(log_file, 'a') as f:
            process = subprocess.Popen(
                service['command'],
                cwd=SERVICE_DIR,
                stdout=f,
                stderr=subprocess.STDOUT
            )
        logging.info(f"{service['name']} 已启动，进程 ID: {process.pid}")
        return True
    except Exception as e:
        logging.error(f"启动 {service['name']} 失败: {e}")
        return False

def main():
    """主函数"""
    logging.info("开始监控所有服务...")
    
    # 服务重启计数
    service_restart_counts = {}
    last_restart_times = {}
    
    # 初始化重启计数和时间
    for service in SERVICES:
        service_restart_counts[service['name']] = 0
        last_restart_times[service['name']] = 0
    
    while True:
        try:
            # 检查每个服务的运行状态
            for service in SERVICES:
                # 检查服务是否在运行
                if not check_service_running(service):
                    # 检查是否达到最大重启次数
                    current_time = time.time()
                    if service_restart_counts[service['name']] >= MAX_RESTARTS and current_time - last_restart_times[service['name']] < RESTART_INTERVAL:
                        logging.warning(f"{service['name']} 达到最大重启次数 {MAX_RESTARTS}，将在 {RESTART_INTERVAL} 秒后再次尝试")
                        continue
                    
                    # 启动服务
                    if start_service(service):
                        service_restart_counts[service['name']] += 1
                        last_restart_times[service['name']] = current_time
                        logging.info(f"{service['name']} 已重启，重启次数: {service_restart_counts[service['name']]}")
                    else:
                        logging.error(f"启动 {service['name']} 失败，将在 {CHECK_INTERVAL} 秒后再次尝试")
                else:
                    # 服务正常运行，重置重启次数
                    service_restart_counts[service['name']] = 0
                    logging.debug(f"{service['name']} 运行正常")
            
            # 等待下一次检查
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logging.info("监控已停止")
            break
        except Exception as e:
            logging.error(f"监控过程中发生错误: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
