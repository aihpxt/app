"""Prometheus监控指标"""

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from typing import Dict, Any

# 请求计数器
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

# 请求延迟直方图
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

# 活跃请求数
http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently in progress",
    ["method", "endpoint"]
)

# 业务指标
business_metrics = Counter(
    "business_operations_total",
    "Total business operations",
    ["operation", "status"]
)

# 缓存命中率
cache_hits_total = Counter(
    "cache_hits_total",
    "Total cache hits"
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total cache misses"
)

# 外部API调用
external_api_calls_total = Counter(
    "external_api_calls_total",
    "Total external API calls",
    ["api", "status"]
)

external_api_duration_seconds = Histogram(
    "external_api_duration_seconds",
    "External API call duration in seconds",
    ["api"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0)
)

# 系统指标
system_info = Info(
    "system",
    "System information"
)

# 数据库连接池
db_connections_active = Gauge(
    "db_connections_active",
    "Number of active database connections"
)

db_connections_idle = Gauge(
    "db_connections_idle",
    "Number of idle database connections"
)

# Redis连接
redis_connected = Gauge(
    "redis_connected",
    "Redis connection status (1=connected, 0=disconnected)"
)

# 自定义业务指标
prediction_requests_total = Counter(
    "prediction_requests_total",
    "Total prediction requests",
    ["status"]
)

user_active_count = Gauge(
    "user_active_count",
    "Number of active users in the last hour"
)

class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self._initialize_system_info()

    def _initialize_system_info(self):
        """初始化系统信息"""
        import platform
        system_info.info({
            "version": "1.0.0",
            "python_version": platform.python_version(),
            "platform": platform.platform()
        })

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """记录HTTP请求"""
        http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

    def record_business_operation(self, operation: str, status: str):
        """记录业务操作"""
        business_metrics.labels(operation=operation, status=status).inc()

    def record_cache_hit(self):
        """记录缓存命中"""
        cache_hits_total.inc()

    def record_cache_miss(self):
        """记录缓存未命中"""
        cache_misses_total.inc()

    def get_cache_hit_rate(self) -> float:
        """获取缓存命中率"""
        hits = cache_hits_total._value.get()
        misses = cache_misses_total._value.get()
        total = hits + misses
        return hits / total if total > 0 else 0.0

    def record_external_api(self, api: str, status: int, duration: float):
        """记录外部API调用"""
        external_api_calls_total.labels(api=api, status=status).inc()
        external_api_duration_seconds.labels(api=api).observe(duration)

    def record_prediction(self, status: str):
        """记录预测请求"""
        prediction_requests_total.labels(status=status).inc()

    def set_active_users(self, count: int):
        """设置活跃用户数"""
        user_active_count.set(count)

    def set_redis_status(self, connected: bool):
        """设置Redis连接状态"""
        redis_connected.set(1 if connected else 0)

    def set_db_connections(self, active: int, idle: int):
        """设置数据库连接状态"""
        db_connections_active.set(active)
        db_connections_idle.set(idle)

    def get_metrics(self) -> Response:
        """获取Prometheus格式的指标"""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )

metrics_collector = MetricsCollector()
