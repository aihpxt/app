#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控模块
提供系统资源监控和健康检查功能
"""

import psutil
import time
import logging
from typing import Dict, Any
import requests
from datetime import datetime
import redis
import threading
from app.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB, HERMES_URL

# 构建Redis URL
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

logger = logging.getLogger(__name__)

class SystemMonitor:
    """系统监控类"""
    
    def __init__(self):
        """初始化监控器"""
        self.start_time = time.time()
        self.redis_available = False
        self.hermes_available = False
        # 启动后台线程检查服务状态
        self._start_service_checks()
    
    def _start_service_checks(self):
        """启动后台线程检查服务状态"""
        # 立即检查一次服务状态
        self._check_services_in_background()
        # 启动定时检查服务状态的线程
        self.service_check_thread = threading.Thread(target=self._service_check_loop, daemon=True)
        self.service_check_thread.start()
    
    def _service_check_loop(self):
        """服务检查循环"""
        while True:
            time.sleep(60)  # 每60秒检查一次服务状态
            self._check_services_in_background()
    
    def _check_services_in_background(self):
        """在后台线程中检查服务状态"""
        thread = threading.Thread(target=self._check_all_services, daemon=True)
        thread.start()
    
    def _check_all_services(self):
        """检查所有服务状态"""
        self._check_redis()
        self._check_hermes()
    
    def _check_redis(self):
        """检查Redis连接"""
        try:
            if REDIS_URL:
                max_retries = 3
                retry_delay = 0.5
                for i in range(max_retries):
                    try:
                        r = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2, socket_timeout=2)
                        r.ping()
                        self.redis_available = True
                        break
                    except Exception as e:
                        if i < max_retries - 1:
                            time.sleep(retry_delay)
                        else:
                            logger.warning(f"Redis连接失败: {e}")
                            self.redis_available = False
        except Exception as e:
            logger.warning(f"Redis连接失败: {e}")
            self.redis_available = False
    
    def _check_hermes(self):
        """检查Hermes服务"""
        try:
            if HERMES_URL:
                max_retries = 3
                retry_delay = 1
                for i in range(max_retries):
                    try:
                        # 确保 URL 格式正确，添加 /health 路径
                        health_url = HERMES_URL.rstrip('/') + '/health'
                        response = requests.get(health_url, timeout=5)  # 增加超时时间到5秒
                        if response.status_code == 200:
                            self.hermes_available = True
                            break
                    except Exception as e:
                        if i < max_retries - 1:
                            time.sleep(retry_delay)
                        else:
                            logger.warning(f"Hermes服务不可用: {e}")
                            self.hermes_available = False
        except Exception as e:
            logger.warning(f"Hermes服务不可用: {e}")
            self.hermes_available = False
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            # CPU使用率（使用interval=0.05减少阻塞时间）
            cpu_percent = psutil.cpu_percent(interval=0.05)
            cpu_count = psutil.cpu_count(logical=True)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_used = memory.used / (1024 ** 3)  # GB
            memory_total = memory.total / (1024 ** 3)  # GB
            memory_percent = memory.percent
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_used = disk.used / (1024 ** 3)  # GB
            disk_total = disk.total / (1024 ** 3)  # GB
            disk_percent = disk.percent
            
            # 网络使用情况
            network = psutil.net_io_counters()
            network_sent = network.bytes_sent / (1024 ** 2)  # MB
            network_recv = network.bytes_recv / (1024 ** 2)  # MB
            
            # 系统运行时间
            uptime = time.time() - self.start_time
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "used": round(memory_used, 2),
                    "total": round(memory_total, 2),
                    "percent": memory_percent
                },
                "disk": {
                    "used": round(disk_used, 2),
                    "total": round(disk_total, 2),
                    "percent": disk_percent
                },
                "network": {
                    "sent": round(network_sent, 2),
                    "recv": round(network_recv, 2)
                },
                "uptime": round(uptime, 2),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return {"error": str(e)}
    
    def get_service_status(self, recheck=False) -> Dict[str, Any]:
        """获取服务状态"""
        # 只有在需要时才重新检查服务状态
        if recheck:
            self._check_services_in_background()
        
        return {
            "redis": {
                "available": self.redis_available,
                "url": REDIS_URL if REDIS_URL else "未配置"
            },
            "hermes": {
                "available": self.hermes_available,
                "url": HERMES_URL if HERMES_URL else "未配置"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        system_metrics = self.get_system_metrics()
        service_status = self.get_service_status()
        
        # 评估健康状态
        is_healthy = True
        issues = []
        
        # 检查系统资源
        if "cpu" in system_metrics and system_metrics["cpu"]["percent"] > 90:
            is_healthy = False
            issues.append("CPU使用率过高")
        
        if "memory" in system_metrics and system_metrics["memory"]["percent"] > 90:
            is_healthy = False
            issues.append("内存使用率过高")
        
        if "disk" in system_metrics and system_metrics["disk"]["percent"] > 90:
            is_healthy = False
            issues.append("磁盘使用率过高")
        
        # 检查服务状态（非核心服务，仅记录为问题，不影响健康状态）
        if not service_status["redis"]["available"]:
            issues.append("Redis服务不可用，已降级为内存缓存")
        
        if not service_status["hermes"]["available"]:
            issues.append("Hermes服务不可用，部分高级功能可能受限")
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "issues": issues,
            "system": system_metrics,
            "services": service_status
        }

# 全局监控实例
system_monitor = None

def get_system_monitor() -> SystemMonitor:
    """获取系统监控实例"""
    global system_monitor
    if system_monitor is None:
        system_monitor = SystemMonitor()
    return system_monitor
