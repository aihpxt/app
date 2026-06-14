#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能服务网关
统一管理所有智能模块的通信，实现负载均衡、熔断和请求路由
"""

import time
import json
import logging
from typing import Dict, Any, Optional, Callable
from threading import Lock
from collections import defaultdict
from enum import Enum
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """服务状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNAVAILABLE = "unavailable"


class CircuitBreakerState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 正常工作
    OPEN = "open"          # 熔断中
    HALF_OPEN = "half_open"  # 尝试恢复


class CircuitBreaker:
    """熔断器实现"""
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 30):
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.last_failure_time = 0
        self.lock = Lock()
    
    def allow_request(self) -> bool:
        """判断是否允许请求通过"""
        with self.lock:
            if self.state == CircuitBreakerState.OPEN:
                # 检查是否过了重置时间
                if time.time() - self.last_failure_time >= self.reset_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    return True
                return False
            return True
    
    def record_success(self):
        """记录成功请求"""
        with self.lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
    
    def record_failure(self):
        """记录失败请求"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"熔断器已触发，服务暂时不可用")


class ServiceEndpoint:
    """服务端点"""
    
    def __init__(self, name: str, host: str, port: int, path: str = "/"):
        self.name = name
        self.host = host
        self.port = port
        self.path = path
        self.status = ServiceStatus.HEALTHY
        self.response_times: list = []
        self.error_count = 0
        self.circuit_breaker = CircuitBreaker()
        self.last_health_check = 0
    
    @property
    def url(self):
        return f"http://{self.host}:{self.port}{self.path}"
    
    @property
    def avg_response_time(self):
        if not self.response_times:
            return float('inf')
        return sum(self.response_times) / len(self.response_times)
    
    def record_response(self, response_time: float, success: bool):
        """记录响应时间"""
        self.response_times.append(response_time)
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]
        
        if success:
            self.circuit_breaker.record_success()
            self.error_count = 0
        else:
            self.circuit_breaker.record_failure()
            self.error_count += 1


class SmartServiceGateway:
    """智能服务网关"""
    
    def __init__(self):
        self.services: Dict[str, list] = {}  # service_type -> [ServiceEndpoint]
        self.service_locks: Dict[str, Lock] = defaultdict(Lock)
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.total_requests = 0
        self.total_errors = 0
        self.lock = Lock()
        
        # 注册默认服务
        self._register_default_services()
    
    def _register_default_services(self):
        """注册默认服务端点"""
        # Hermes服务
        self.register_service("hermes", ServiceEndpoint(
            "hermes-primary", "localhost", 8888, "/v1/agent"
        ))
        
        # AI服务
        self.register_service("ai", ServiceEndpoint(
            "ai-primary", "localhost", 8001, "/api/v1/agent/chat"
        ))
        
        # 数据同步服务
        self.register_service("sync", ServiceEndpoint(
            "sync-primary", "localhost", 8001, "/api/v1/sync"
        ))
        
        # 缓存服务
        self.register_service("cache", ServiceEndpoint(
            "cache-primary", "localhost", 6379, ""
        ))
    
    def register_service(self, service_type: str, endpoint: ServiceEndpoint):
        """注册服务端点"""
        with self.service_locks[service_type]:
            if service_type not in self.services:
                self.services[service_type] = []
            self.services[service_type].append(endpoint)
            logger.info(f"服务已注册: {service_type} -> {endpoint.name}")
    
    def get_healthy_endpoint(self, service_type: str) -> Optional[ServiceEndpoint]:
        """获取健康的服务端点（负载均衡）"""
        with self.service_locks[service_type]:
            endpoints = self.services.get(service_type, [])
            if not endpoints:
                logger.error(f"未找到服务类型: {service_type}")
                return None
            
            # 过滤健康且熔断器允许的端点
            healthy_endpoints = [
                ep for ep in endpoints 
                if ep.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]
                and ep.circuit_breaker.allow_request()
            ]
            
            if not healthy_endpoints:
                logger.warning(f"{service_type} 服务暂时不可用")
                return None
            
            # 加权轮询：优先选择响应时间短的
            healthy_endpoints.sort(key=lambda ep: ep.avg_response_time)
            return healthy_endpoints[0]
    
    def route_request(self, service_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """路由请求到指定服务"""
        start_time = time.time()
        endpoint = self.get_healthy_endpoint(service_type)
        
        if not endpoint:
            with self.lock:
                self.total_errors += 1
            return {
                "success": False,
                "error": f"服务不可用: {service_type}"
            }
        
        try:
            response = self._call_service(endpoint, payload)
            response_time = time.time() - start_time
            endpoint.record_response(response_time, success=True)
            
            with self.lock:
                self.total_requests += 1
                self.request_counts[service_type] += 1
            
            return {
                "success": True,
                "data": response,
                "response_time": round(response_time, 3),
                "service": endpoint.name
            }
        except Exception as e:
            response_time = time.time() - start_time
            endpoint.record_response(response_time, success=False)
            
            with self.lock:
                self.total_requests += 1
                self.total_errors += 1
            
            logger.error(f"服务调用失败 {service_type}: {e}")
            return {
                "success": False,
                "error": str(e),
                "response_time": round(response_time, 3)
            }
    
    def _call_service(self, endpoint: ServiceEndpoint, payload: Dict[str, Any]) -> Any:
        """实际调用服务"""
        import requests
        
        try:
            if endpoint.port == 6379:
                # Redis服务
                import redis
                r = redis.Redis(host=endpoint.host, port=endpoint.port)
                return {"status": "connected"}
            else:
                # HTTP服务
                response = requests.post(
                    endpoint.url,
                    json=payload,
                    timeout=10
                )
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP请求失败: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取网关状态"""
        status = {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": round(self.total_errors / max(self.total_requests, 1) * 100, 2),
            "services": {}
        }
        
        for service_type, endpoints in self.services.items():
            service_status = []
            for ep in endpoints:
                service_status.append({
                    "name": ep.name,
                    "status": ep.status.value,
                    "avg_response_time": round(ep.avg_response_time, 3),
                    "error_count": ep.error_count,
                    "circuit_breaker": ep.circuit_breaker.state.value
                })
            status["services"][service_type] = service_status
        
        return status


# 全局网关实例
_gateway = None

def get_gateway() -> SmartServiceGateway:
    """获取全局网关实例"""
    global _gateway
    if _gateway is None:
        _gateway = SmartServiceGateway()
    return _gateway


if __name__ == "__main__":
    gateway = get_gateway()
    
    # 测试网关
    print("=== 智能服务网关测试 ===")
    print(f"初始状态: {json.dumps(gateway.get_status(), indent=2, ensure_ascii=False)}")
    
    # 测试路由
    result = gateway.route_request("hermes", {"data": {"input": "测试"}, "type": "emotion"})
    print(f"\nHermes路由测试: {result}")
    
    print("\n=== 测试完成 ===")