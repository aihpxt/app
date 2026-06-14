#!/usr/bin/env python3
"""
启动所有服务脚本
用于启动应用服务、监控服务、备份服务、缓存预热服务和日志分析服务
"""

import os
import sys
import subprocess
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(__file__), 'logs', 'start_all_services.log'),
    filemode='a'
)

# 服务配置
SERVICE_DIR = os.path.dirname(__file__)
SERVICES = [
    {
        "name": "AI Service",
        "command": [sys.executable, "start_service.py"],
        "log_file": "service.log"
    },
    {
        "name": "Hermes Service",
        "command": [sys.executable, "hermes_server.py"],
        "log_file": "hermes.log"
    },
    {
        "name": "Service Monitor",
        "command": [sys.executable, "monitor_service.py"],
        "log_file": "monitor.log"
    },
    {
        "name": "Database Backup",
        "command": [sys.executable, "backup_database.py"],
        "log_file": "backup.log"
    },
    {
        "name": "Cache Warmer",
        "command": [sys.executable, "cache_warmer.py"],
        "log_file": "cache_warmer.log"
    },
    {
        "name": "Log Analyzer",
        "command": [sys.executable, "log_analyzer.py"],
        "log_file": "log_analyzer.log"
    },
    {
        "name": "Crawler Scheduler",
        "command": [sys.executable, "crawler_scheduler.py"],
        "log_file": "crawler_scheduler.log"
    }
]

# 日志目录
LOG_DIR = os.path.join(SERVICE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

def start_service(service):
    """启动服务"""
    try:
        logging.info(f"启动 {service['name']}...")
        log_file = os.path.join(LOG_DIR, service['log_file'])
        with open(log_file, 'a') as f:
            process = subprocess.Popen(
                service['command'],
                cwd=SERVICE_DIR,
                stdout=f,
                stderr=subprocess.STDOUT
            )
        logging.info(f"{service['name']} 已启动，进程 ID: {process.pid}")
        return process
    except Exception as e:
        logging.error(f"启动 {service['name']} 失败: {e}")
        return None

def main():
    """主函数"""
    logging.info("开始启动所有服务...")
    
    # 启动所有服务
    processes = []
    for service in SERVICES:
        process = start_service(service)
        if process:
            processes.append(process)
        # 避免启动过于频繁
        time.sleep(2)
    
    logging.info("所有服务启动完成")
    
    # 监控服务运行状态
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logging.info("正在停止所有服务...")
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=10)
            except Exception as e:
                logging.error(f"停止服务失败: {e}")
        logging.info("所有服务已停止")

if __name__ == "__main__":
    main()
