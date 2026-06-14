"""
系统优化配置文件
包含连接池、限流、熔断器、重试、内存优化等配置
"""

import os

# ==================== 连接池配置 ====================
class ConnectionPoolConfig:
    """连接池配置"""
    MAX_CONNECTIONS = int(os.getenv("MAX_CONNECTIONS", "100"))  # 最大连接数
    CONNECTION_TIMEOUT = int(os.getenv("CONNECTION_TIMEOUT", "30"))  # 连接超时时间（秒）
    KEEP_ALIVE = os.getenv("KEEP_ALIVE", "True").lower() == "true"  # 保持连接活跃
    POOL_RECYCLE = int(os.getenv("POOL_RECYCLE", "3600"))  # 连接回收时间（秒）
    POOL_PRE_PING = os.getenv("POOL_PRE_PING", "True").lower() == "true"  # 连接前ping
    POOL_SIZE = int(os.getenv("POOL_SIZE", "10"))  # 连接池大小
    MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW", "20"))  # 最大溢出连接数

# ==================== 请求限流配置 ====================
class RateLimitConfig:
    """请求限流配置"""
    ENABLED = os.getenv("RATE_LIMIT_ENABLED", "False").lower() == "true"  # 是否启用限流（性能测试期间禁用）
    PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "1000"))  # 每分钟最大请求数
    BURST = int(os.getenv("RATE_LIMIT_BURST", "200"))  # 突发请求数
    IP_WHITE_LIST = os.getenv("RATE_LIMIT_IP_WHITELIST", "").split(",")  # IP白名单
    IP_BLACK_LIST = os.getenv("RATE_LIMIT_IP_BLACKLIST", "").split(",")  # IP黑名单
    # 不同端点的限流规则
    ENDPOINT_LIMITS = {
        "/api/v1/agents/chat": {"per_minute": 500, "burst": 100},  # 对话接口限制
        "/api/health": {"per_minute": 500, "burst": 100},  # 健康检查接口
        "/api/health/metrics": {"per_minute": 500, "burst": 100},
        "/api/health/services": {"per_minute": 500, "burst": 100},
        "/api/health/cache": {"per_minute": 500, "burst": 100},
    }

# ==================== 熔断器配置 ====================
class CircuitBreakerConfig:
    """熔断器配置"""
    ENABLED = os.getenv("CIRCUIT_BREAKER_ENABLED", "True").lower() == "true"  # 是否启用熔断器
    FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))  # 失败次数阈值
    TIMEOUT = int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "30"))  # 熔断超时时间（秒）
    HALF_OPEN_MAX_CALLS = int(os.getenv("CIRCUIT_BREAKER_HALF_OPEN", "3"))  # 半开状态最大尝试次数
    RECOVERY_TIMEOUT = int(os.getenv("CIRCUIT_BREAKER_RECOVERY", "60"))  # 恢复超时时间（秒）
    # 不同服务的熔断器配置
    SERVICE_CONFIG = {
        "hermes": {
            "failure_threshold": 3,  # Hermes服务更敏感
            "timeout": 20,
            "half_open_max_calls": 2,
        },
        "redis": {
            "failure_threshold": 5,
            "timeout": 30,
            "half_open_max_calls": 3,
        },
        "external_api": {
            "failure_threshold": 5,
            "timeout": 30,
            "half_open_max_calls": 3,
        }
    }

# ==================== 重试机制配置 ====================
class RetryConfig:
    """重试机制配置"""
    ENABLED = os.getenv("RETRY_ENABLED", "True").lower() == "true"  # 是否启用重试
    MAX_RETRIES = int(os.getenv("RETRY_MAX_RETRIES", "3"))  # 最大重试次数
    INITIAL_DELAY = float(os.getenv("RETRY_INITIAL_DELAY", "0.5"))  # 初始延迟（秒）
    MAX_DELAY = float(os.getenv("RETRY_MAX_DELAY", "10.0"))  # 最大延迟（秒）
    EXPONENTIAL_BASE = float(os.getenv("RETRY_EXPONENTIAL_BASE", "2.0"))  # 指数退避基数
    RETRY_ON_TIMEOUT = os.getenv("RETRY_ON_TIMEOUT", "True").lower() == "true"  # 是否对超时进行重试
    RETRY_ON_CONNECTION_ERROR = os.getenv("RETRY_ON_CONNECTION_ERROR", "True").lower() == "true"  # 是否对连接错误进行重试
    RETRY_ON_STATUS_CODES = [500, 502, 503, 504]  # 需要重试的HTTP状态码
    # 不同服务的重试配置
    SERVICE_CONFIG = {
        "hermes": {
            "max_retries": 2,  # Hermes服务重试次数较少
            "timeout": 5,
        },
        "redis": {
            "max_retries": 3,
            "timeout": 2,
        },
        "external_api": {
            "max_retries": 3,
            "timeout": 10,
        }
    }

# ==================== 内存优化配置 ====================
class MemoryOptimizationConfig:
    """内存优化配置"""
    ENABLED = os.getenv("MEMORY_OPT_ENABLED", "True").lower() == "true"  # 是否启用内存优化
    MEMORY_THRESHOLD = float(os.getenv("MEMORY_THRESHOLD", "80.0"))  # 内存使用率告警阈值（%）
    CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "1000"))  # 缓存最大条目数
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 缓存默认TTL（秒）
    CACHE_CLEANUP_INTERVAL = int(os.getenv("CACHE_CLEANUP_INTERVAL", "300"))  # 缓存清理间隔（秒）
    CACHE_EXPIRY_CHECK_INTERVAL = int(os.getenv("CACHE_EXPIRY_CHECK", "60"))  # 缓存过期检查间隔（秒）
    # 数据结构优化
    USE_SLOTS = os.getenv("USE_SLOTS", "True").lower() == "true"  # 是否对类使用__slots__
    LAZY_LOADING = os.getenv("LAZY_LOADING", "True").lower() == "true"  # 是否启用延迟加载
    STREAM_LARGE_RESPONSES = os.getenv("STREAM_LARGE_RESPONSES", "True").lower() == "true"  # 是否流式传输大响应
    LARGE_RESPONSE_THRESHOLD = int(os.getenv("LARGE_RESPONSE_THRESHOLD", "1048576"))  # 大响应阈值（字节，1MB）

# ==================== 性能监控配置 ====================
class PerformanceMonitoringConfig:
    """性能监控配置"""
    ENABLED = os.getenv("PERF_MONITORING_ENABLED", "True").lower() == "true"  # 是否启用性能监控
    METRICS_COLLECTION_INTERVAL = int(os.getenv("METRICS_INTERVAL", "60"))  # 指标收集间隔（秒）
    LOG_SLOW_REQUESTS = os.getenv("LOG_SLOW_REQUESTS", "True").lower() == "true"  # 是否记录慢请求
    SLOW_REQUEST_THRESHOLD = float(os.getenv("SLOW_REQUEST_THRESHOLD", "1.0"))  # 慢请求阈值（秒）
    LOG_PERFORMANCE_METRICS = os.getenv("LOG_PERF_METRICS", "True").lower() == "true"  # 是否记录性能指标
    ENABLE_APM = os.getenv("ENABLE_APM", "False").lower() == "true"  # 是否启用APM

# ==================== 汇总配置 ====================
class OptimizationConfig:
    """优化配置汇总"""
    connection_pool = ConnectionPoolConfig()
    rate_limit = RateLimitConfig()
    circuit_breaker = CircuitBreakerConfig()
    retry = RetryConfig()
    memory_optimization = MemoryOptimizationConfig()
    performance_monitoring = PerformanceMonitoringConfig()

    @classmethod
    def get_all_configs(cls):
        """获取所有配置"""
        return {
            "connection_pool": {
                "max_connections": cls.connection_pool.MAX_CONNECTIONS,
                "timeout": cls.connection_pool.CONNECTION_TIMEOUT,
                "keep_alive": cls.connection_pool.KEEP_ALIVE,
            },
            "rate_limit": {
                "enabled": cls.rate_limit.ENABLED,
                "per_minute": cls.rate_limit.PER_MINUTE,
                "burst": cls.rate_limit.BURST,
            },
            "circuit_breaker": {
                "enabled": cls.circuit_breaker.ENABLED,
                "failure_threshold": cls.circuit_breaker.FAILURE_THRESHOLD,
                "timeout": cls.circuit_breaker.TIMEOUT,
            },
            "retry": {
                "enabled": cls.retry.ENABLED,
                "max_retries": cls.retry.MAX_RETRIES,
                "initial_delay": cls.retry.INITIAL_DELAY,
            },
            "memory_optimization": {
                "enabled": cls.memory_optimization.ENABLED,
                "memory_threshold": cls.memory_optimization.MEMORY_THRESHOLD,
                "cache_max_size": cls.memory_optimization.CACHE_MAX_SIZE,
            },
            "performance_monitoring": {
                "enabled": cls.performance_monitoring.ENABLED,
                "slow_request_threshold": cls.performance_monitoring.SLOW_REQUEST_THRESHOLD,
            }
        }

    @classmethod
    def validate_config(cls):
        """验证配置是否有效"""
        errors = []

        # 验证连接池配置
        if cls.connection_pool.MAX_CONNECTIONS < 1:
            errors.append("连接池最大连接数必须大于0")
        if cls.connection_pool.CONNECTION_TIMEOUT < 1:
            errors.append("连接超时时间必须大于0")

        # 验证限流配置
        if cls.rate_limit.PER_MINUTE < 1:
            errors.append("每分钟限流次数必须大于0")

        # 验证熔断器配置
        if cls.circuit_breaker.FAILURE_THRESHOLD < 1:
            errors.append("熔断器失败阈值必须大于0")
        if cls.circuit_breaker.TIMEOUT < 1:
            errors.append("熔断器超时时间必须大于0")

        # 验证重试配置
        if cls.retry.MAX_RETRIES < 0:
            errors.append("最大重试次数不能为负数")
        if cls.retry.INITIAL_DELAY < 0:
            errors.append("初始延迟不能为负数")

        # 验证内存优化配置
        if cls.memory_optimization.MEMORY_THRESHOLD < 0 or cls.memory_optimization.MEMORY_THRESHOLD > 100:
            errors.append("内存阈值必须在0-100之间")
        if cls.memory_optimization.CACHE_MAX_SIZE < 1:
            errors.append("缓存最大条目数必须大于0")

        return errors

# 验证配置
config_errors = OptimizationConfig.validate_config()
if config_errors:
    import logging
    logger = logging.getLogger(__name__)
    for error in config_errors:
        logger.warning(f"配置验证警告: {error}")

# 导出配置实例
optimization_config = OptimizationConfig()
