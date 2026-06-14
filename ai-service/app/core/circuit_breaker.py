"""
熔断器模式实现
用于防止故障传播，提高系统稳定性
"""

import time
import threading
from enum import Enum
from typing import Callable, Any, Optional, Dict
from functools import wraps
from app.core.optimization_config import optimization_config
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 关闭状态，正常工作
    OPEN = "open"          # 打开状态，拒绝请求
    HALF_OPEN = "half_open"  # 半开状态，尝试恢复

class CircuitBreaker:
    """熔断器实现"""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: int = 30,
        half_open_max_calls: int = 3,
        recovery_timeout: int = 60
    ):
        """
        初始化熔断器

        Args:
            name: 熔断器名称
            failure_threshold: 失败次数阈值
            timeout: 熔断超时时间（秒）
            half_open_max_calls: 半开状态最大尝试次数
            recovery_timeout: 恢复超时时间（秒）
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        self.recovery_timeout = recovery_timeout

        # 状态管理
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._last_state_change_time = time.time()
        self._half_open_calls = 0

        # 线程锁
        self._lock = threading.Lock()

        # 统计信息
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "rejected_calls": 0,
            "state_changes": []
        }

    @property
    def state(self) -> CircuitState:
        """获取当前状态"""
        with self._lock:
            if self._state == CircuitState.OPEN:
                # 检查是否应该转换到半开状态
                if time.time() - self._last_state_change_time >= self.recovery_timeout:
                    self._transition_to(CircuitState.HALF_OPEN)
            return self._state

    def _transition_to(self, new_state: CircuitState):
        """转换状态"""
        if self._state == new_state:
            return

        old_state = self._state
        self._state = new_state
        self._last_state_change_time = time.time()

        # 记录状态变更
        self.stats["state_changes"].append({
            "from": old_state.value,
            "to": new_state.value,
            "timestamp": time.time()
        })

        logger.info(f"Circuit breaker '{self.name}' state changed: {old_state.value} -> {new_state.value}")

        if new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
        elif new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0

    def record_success(self):
        """记录成功调用"""
        with self._lock:
            self.stats["successful_calls"] += 1
            self._success_count += 1

            if self._state == CircuitState.HALF_OPEN:
                if self._success_count >= self.half_open_max_calls:
                    self._transition_to(CircuitState.CLOSED)

    def record_failure(self):
        """记录失败调用"""
        with self._lock:
            self.stats["failed_calls"] += 1
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                # 半开状态下失败，立即打开熔断器
                self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    self._transition_to(CircuitState.OPEN)

    def can_execute(self) -> tuple[bool, Optional[str]]:
        """
        检查是否可以执行请求

        Returns:
            tuple: (是否可以执行, 拒绝原因)
        """
        with self._lock:
            self.stats["total_calls"] += 1

            if self._state == CircuitState.OPEN:
                self.stats["rejected_calls"] += 1
                return False, f"Circuit breaker '{self.name}' is OPEN"
            elif self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max_calls:
                    self.stats["rejected_calls"] += 1
                    return False, f"Circuit breaker '{self.name}' in HALF_OPEN, max calls reached"
                self._half_open_calls += 1
                return True, None
            else:  # CLOSED
                return True, None

    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self._lock:
            return {
                **self.stats,
                "current_state": self.state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "last_failure_time": self._last_failure_time,
                "time_in_current_state": time.time() - self._last_state_change_time
            }

    def reset(self):
        """重置熔断器"""
        with self._lock:
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._half_open_calls = 0
            self._last_failure_time = None
            self._last_state_change_time = time.time()
            self.stats = {
                "total_calls": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "rejected_calls": 0,
                "state_changes": []
            }

    def __call__(self, func: Callable) -> Callable:
        """装饰器模式"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            can_execute, reason = self.can_execute()
            if not can_execute:
                logger.warning(f"Circuit breaker rejected call: {reason}")
                raise CircuitBreakerOpenError(reason)

            try:
                result = await func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            can_execute, reason = self.can_execute()
            if not can_execute:
                logger.warning(f"Circuit breaker rejected call: {reason}")
                raise CircuitBreakerOpenError(reason)

            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                raise

        # 根据函数类型返回合适的装饰器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        调用函数，自动处理熔断

        Args:
            func: 要调用的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            函数返回值

        Raises:
            CircuitBreakerOpenError: 熔断器打开时抛出
        """
        can_execute, reason = self.can_execute()
        if not can_execute:
            logger.warning(f"Circuit breaker rejected call: {reason}")
            raise CircuitBreakerOpenError(reason)

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise

class CircuitBreakerOpenError(Exception):
    """熔断器打开异常"""
    pass

class CircuitBreakerRegistry:
    """熔断器注册表"""

    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

    def get_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """
        获取或创建熔断器

        Args:
            name: 熔断器名称
            **kwargs: 熔断器配置参数

        Returns:
            CircuitBreaker实例
        """
        with self._lock:
            if name not in self._breakers:
                # 使用配置或默认值
                config = optimization_config.circuit_breaker.SERVICE_CONFIG.get(name, {})
                self._breakers[name] = CircuitBreaker(
                    name=name,
                    failure_threshold=kwargs.get("failure_threshold", config.get("failure_threshold", optimization_config.circuit_breaker.FAILURE_THRESHOLD)),
                    timeout=kwargs.get("timeout", config.get("timeout", optimization_config.circuit_breaker.TIMEOUT)),
                    half_open_max_calls=kwargs.get("half_open_max_calls", config.get("half_open_max_calls", optimization_config.circuit_breaker.HALF_OPEN_MAX_CALLS)),
                    recovery_timeout=kwargs.get("recovery_timeout", optimization_config.circuit_breaker.RECOVERY_TIMEOUT)
                )
            return self._breakers[name]

    def get_all_stats(self) -> Dict[str, Dict]:
        """获取所有熔断器的统计信息"""
        with self._lock:
            return {
                name: breaker.get_stats()
                for name, breaker in self._breakers.items()
            }

    def reset_all(self):
        """重置所有熔断器"""
        with self._lock:
            for breaker in self._breakers.values():
                breaker.reset()

# 全局熔断器注册表
circuit_breaker_registry = CircuitBreakerRegistry()

def circuit_breaker(name: str, **kwargs):
    """
    熔断器装饰器工厂

    Args:
        name: 熔断器名称
        **kwargs: 熔断器配置参数

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        breaker = circuit_breaker_registry.get_breaker(name, **kwargs)
        return breaker(func)
    return decorator
