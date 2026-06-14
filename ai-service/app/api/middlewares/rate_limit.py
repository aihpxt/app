"""增强的速率限制中间件 - 令牌桶算法实现"""

import time
import threading
from typing import Dict, Optional
from collections import defaultdict
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import RateLimitExceededException
from app.core.optimization_config import optimization_config

class TokenBucket:
    """令牌桶算法实现"""

    def __init__(self, rate: float, capacity: int):
        """
        初始化令牌桶

        Args:
            rate: 每秒生成的令牌数
            capacity: 桶的容量
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        尝试消费令牌

        Args:
            tokens: 要消费的令牌数

        Returns:
            bool: 是否消费成功
        """
        with self.lock:
            # 更新令牌数
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now

            # 尝试消费令牌
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def get_available_tokens(self) -> float:
        """获取当前可用令牌数"""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            return min(self.capacity, self.tokens + elapsed * self.rate)

class RateLimiter:
    """增强的速率限制器"""

    def __init__(self):
        self.config = optimization_config.rate_limit
        self.enabled = self.config.ENABLED

        if self.enabled:
            # 初始化令牌桶
            self.global_bucket = TokenBucket(
                rate=self.config.PER_MINUTE / 60.0,  # 转换为每秒令牌数
                capacity=self.config.BURST
            )

            # 初始化每个IP的令牌桶
            self.ip_buckets: Dict[str, TokenBucket] = {}
            self.ip_buckets_lock = threading.Lock()

            # 初始化每个端点的令牌桶
            self.endpoint_buckets: Dict[str, TokenBucket] = {}
            self.endpoint_buckets_lock = threading.Lock()

            # 初始化统计信息
            self.stats = {
                "total_requests": 0,
                "blocked_requests": 0,
                "allowed_requests": 0,
                "by_ip": defaultdict(int),
                "by_endpoint": defaultdict(int)
            }
            self.stats_lock = threading.Lock()

    def get_ip_bucket(self, ip: str) -> TokenBucket:
        """获取或创建IP的令牌桶"""
        with self.ip_buckets_lock:
            if ip not in self.ip_buckets:
                # 使用全局配置的速率
                self.ip_buckets[ip] = TokenBucket(
                    rate=self.config.PER_MINUTE / 60.0,
                    capacity=self.config.BURST
                )
            return self.ip_buckets[ip]

    def get_endpoint_bucket(self, endpoint: str) -> TokenBucket:
        """获取或创建端点的令牌桶"""
        with self.endpoint_buckets_lock:
            if endpoint not in self.endpoint_buckets:
                # 使用端点特定的配置
                endpoint_config = self.config.ENDPOINT_LIMITS.get(endpoint, {})
                per_minute = endpoint_config.get("per_minute", self.config.PER_MINUTE)
                burst = endpoint_config.get("burst", self.config.BURST)

                self.endpoint_buckets[endpoint] = TokenBucket(
                    rate=per_minute / 60.0,
                    capacity=burst
                )
            return self.endpoint_buckets[endpoint]

    def is_allowed(self, ip: str, endpoint: str) -> tuple[bool, Optional[str]]:
        """
        检查请求是否允许

        Args:
            ip: 客户端IP
            endpoint: 请求端点

        Returns:
            tuple: (是否允许, 拒绝原因)
        """
        if not self.enabled:
            return True, None

        with self.stats_lock:
            self.stats["total_requests"] += 1

        # 检查IP白名单
        if ip in self.config.IP_WHITE_LIST:
            with self.stats_lock:
                self.stats["allowed_requests"] += 1
            return True, None

        # 检查IP黑名单
        if ip in self.config.IP_BLACK_LIST:
            with self.stats_lock:
                self.stats["blocked_requests"] += 1
            return False, "IP已被列入黑名单"

        # 全局限流检查
        if not self.global_bucket.consume():
            with self.stats_lock:
                self.stats["blocked_requests"] += 1
            return False, "全局请求频率超限"

        # IP限流检查
        ip_bucket = self.get_ip_bucket(ip)
        if not ip_bucket.consume():
            with self.stats_lock:
                self.stats["blocked_requests"] += 1
                self.stats["by_ip"][ip] += 1
            return False, "IP请求频率超限"

        # 端点限流检查
        endpoint_bucket = self.get_endpoint_bucket(endpoint)
        if not endpoint_bucket.consume():
            with self.stats_lock:
                self.stats["blocked_requests"] += 1
                self.stats["by_endpoint"][endpoint] += 1
            return False, f"端点{endpoint}请求频率超限"

        with self.stats_lock:
            self.stats["allowed_requests"] += 1

        return True, None

    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self.stats_lock:
            return {
                **self.stats,
                "block_rate": self.stats["blocked_requests"] / max(1, self.stats["total_requests"]),
                "top_blocked_ips": sorted(
                    self.stats["by_ip"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                "top_blocked_endpoints": sorted(
                    self.stats["by_endpoint"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }

    def reset_stats(self):
        """重置统计信息"""
        with self.stats_lock:
            self.stats = {
                "total_requests": 0,
                "blocked_requests": 0,
                "allowed_requests": 0,
                "by_ip": defaultdict(int),
                "by_endpoint": defaultdict(int)
            }

# 全局限流器实例
rate_limiter = RateLimiter()

# 旧的速率限制存储（用于兼容）
rate_limit_store: Dict[str, list] = {}

async def rate_limit_middleware(request: Request, call_next):
    """增强的速率限制中间件"""
    client_ip = request.client.host
    endpoint = request.url.path
    current_time = time.time()

    # 使用新的限流器
    if rate_limiter.enabled:
        allowed, reason = rate_limiter.is_allowed(client_ip, endpoint)

        if not allowed:
            # 记录限流日志
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Rate limit exceeded for IP {client_ip} on {endpoint}: {reason}")

            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "请求过于频繁",
                    "detail": reason,
                    "retry_after": 60
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(rate_limiter.config.PER_MINUTE),
                    "X-RateLimit-Remaining": str(int(rate_limiter.get_ip_bucket(client_ip).get_available_tokens())),
                }
            )

    # 旧版限流逻辑（用于兼容）- 仅在限流启用时执行
    if rate_limiter.enabled:
        if client_ip in rate_limit_store:
            rate_limit_store[client_ip] = [t for t in rate_limit_store[client_ip] if current_time - t < 60]
        else:
            rate_limit_store[client_ip] = []

        from app.core.config import RATE_LIMIT
        if len(rate_limit_store[client_ip]) >= RATE_LIMIT:
            raise RateLimitExceededException()

        rate_limit_store[client_ip].append(current_time)

    # 执行请求
    start_time = time.time()
    response = await call_next(request)

    # 记录响应时间
    response_time = time.time() - start_time
    response.headers["x-process-time"] = str(response_time)

    # 添加限流响应头
    if rate_limiter.enabled:
        response.headers["X-RateLimit-Limit"] = str(rate_limiter.config.PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(int(rate_limiter.get_ip_bucket(client_ip).get_available_tokens()))

    return response
