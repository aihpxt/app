"""
智能重试装饰器实现
用于处理临时性故障，提供指数退避重试机制
"""

import time
import asyncio
import logging
from functools import wraps
from typing import Callable, Any, Tuple, List, Optional, Type
from app.core.optimization_config import optimization_config

logger = logging.getLogger(__name__)

class RetryError(Exception):
    """重试失败异常"""
    pass

class SmartRetry:
    """智能重试类"""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 0.5,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
        retry_on_timeout: bool = True,
        retry_on_connection_error: bool = True,
        retry_on_status_codes: Optional[List[int]] = None,
        exceptions_to_retry: Optional[List[Type[Exception]]] = None,
        exceptions_to_ignore: Optional[List[Type[Exception]]] = None
    ):
        """
        初始化智能重试器

        Args:
            max_retries: 最大重试次数
            initial_delay: 初始延迟时间（秒）
            max_delay: 最大延迟时间（秒）
            exponential_base: 指数退避基数
            retry_on_timeout: 是否对超时进行重试
            retry_on_connection_error: 是否对连接错误进行重试
            retry_on_status_codes: 需要重试的HTTP状态码列表
            exceptions_to_retry: 需要重试的异常类型列表
            exceptions_to_ignore: 需要忽略的异常类型列表
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retry_on_timeout = retry_on_timeout
        self.retry_on_connection_error = retry_on_connection_error
        self.retry_on_status_codes = retry_on_status_codes or []
        self.exceptions_to_retry = exceptions_to_retry or []
        self.exceptions_to_ignore = exceptions_to_ignore or []

        # 统计信息
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "retried_calls": 0,
            "total_retries": 0
        }

    def should_retry(self, exception: Exception) -> bool:
        """
        判断是否应该重试

        Args:
            exception: 发生的异常

        Returns:
            bool: 是否应该重试
        """
        # 检查是否应该忽略
        for exc_type in self.exceptions_to_ignore:
            if isinstance(exception, exc_type):
                return False

        # 检查是否应该重试
        for exc_type in self.exceptions_to_retry:
            if isinstance(exception, exc_type):
                return True

        # 检查超时
        if self.retry_on_timeout:
            if isinstance(exception, asyncio.TimeoutError):
                return True
            if "timeout" in str(exception).lower():
                return True

        # 检查连接错误
        if self.retry_on_connection_error:
            error_msg = str(exception).lower()
            if any(keyword in error_msg for keyword in ["connection", "connect", "refused", "reset", "network"]):
                return True

        # 检查HTTP状态码（如果有）
        if hasattr(exception, "response") and hasattr(exception.response, "status_code"):
            if exception.response.status_code in self.retry_on_status_codes:
                return True

        return False

    def calculate_delay(self, attempt: int) -> float:
        """
        计算延迟时间（指数退避）

        Args:
            attempt: 当前重试次数

        Returns:
            float: 延迟时间（秒）
        """
        delay = self.initial_delay * (self.exponential_base ** attempt)
        # 添加随机抖动（0-10%）
        import random
        jitter = delay * random.uniform(0, 0.1)
        return min(self.max_delay, delay + jitter)

    def __call__(self, func: Callable) -> Callable:
        """装饰器模式"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(self.max_retries + 1):
                try:
                    self.stats["total_calls"] += 1
                    result = await func(*args, **kwargs)
                    if attempt > 0:
                        self.stats["retried_calls"] += 1
                        logger.info(f"Retry successful after {attempt} attempts for {func.__name__}")
                    self.stats["successful_calls"] += 1
                    return result
                except Exception as e:
                    last_exception = e

                    if attempt == self.max_retries:
                        logger.error(f"Max retries ({self.max_retries}) reached for {func.__name__}: {e}")
                        self.stats["failed_calls"] += 1
                        raise

                    if not self.should_retry(e):
                        logger.warning(f"Not retrying {func.__name__} for exception: {e}")
                        self.stats["failed_calls"] += 1
                        raise

                    delay = self.calculate_delay(attempt)
                    self.stats["total_retries"] += 1
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries} for {func.__name__} after {delay:.2f}s: {e}")

                    if attempt < self.max_retries:
                        await asyncio.sleep(delay)

            self.stats["failed_calls"] += 1
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(self.max_retries + 1):
                try:
                    self.stats["total_calls"] += 1
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        self.stats["retried_calls"] += 1
                        logger.info(f"Retry successful after {attempt} attempts for {func.__name__}")
                    self.stats["successful_calls"] += 1
                    return result
                except Exception as e:
                    last_exception = e

                    if attempt == self.max_retries:
                        logger.error(f"Max retries ({self.max_retries}) reached for {func.__name__}: {e}")
                        self.stats["failed_calls"] += 1
                        raise

                    if not self.should_retry(e):
                        logger.warning(f"Not retrying {func.__name__} for exception: {e}")
                        self.stats["failed_calls"] += 1
                        raise

                    delay = self.calculate_delay(attempt)
                    self.stats["total_retries"] += 1
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries} for {func.__name__} after {delay:.2f}s: {e}")

                    if attempt < self.max_retries:
                        time.sleep(delay)

            self.stats["failed_calls"] += 1
            raise last_exception

        # 根据函数类型返回合适的装饰器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            **self.stats,
            "success_rate": self.stats["successful_calls"] / max(1, self.stats["total_calls"]),
            "retry_rate": self.stats["retried_calls"] / max(1, self.stats["total_calls"])
        }

def smart_retry(
    max_retries: Optional[int] = None,
    initial_delay: Optional[float] = None,
    max_delay: Optional[float] = None,
    exponential_base: Optional[float] = None,
    retry_on_timeout: Optional[bool] = None,
    retry_on_connection_error: Optional[bool] = None,
    retry_on_status_codes: Optional[List[int]] = None,
    exceptions_to_retry: Optional[List[Type[Exception]]] = None,
    exceptions_to_ignore: Optional[List[Type[Exception]]] = None
):
    """
    智能重试装饰器工厂

    使用全局配置，但允许覆盖特定参数

    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟时间
        max_delay: 最大延迟时间
        exponential_base: 指数退避基数
        retry_on_timeout: 是否对超时进行重试
        retry_on_connection_error: 是否对连接错误进行重试
        retry_on_status_codes: 需要重试的HTTP状态码
        exceptions_to_retry: 需要重试的异常类型
        exceptions_to_ignore: 需要忽略的异常类型

    Returns:
        SmartRetry装饰器实例
    """
    config = optimization_config.retry

    return SmartRetry(
        max_retries=max_retries if max_retries is not None else config.MAX_RETRIES,
        initial_delay=initial_delay if initial_delay is not None else config.INITIAL_DELAY,
        max_delay=max_delay if max_delay is not None else config.MAX_DELAY,
        exponential_base=exponential_base if exponential_base is not None else config.EXPONENTIAL_BASE,
        retry_on_timeout=retry_on_timeout if retry_on_timeout is not None else config.RETRY_ON_TIMEOUT,
        retry_on_connection_error=retry_on_connection_error if retry_on_connection_error is not None else config.RETRY_ON_CONNECTION_ERROR,
        retry_on_status_codes=retry_on_status_codes if retry_on_status_codes is not None else config.RETRY_ON_STATUS_CODES,
        exceptions_to_retry=exceptions_to_retry,
        exceptions_to_ignore=exceptions_to_ignore
    )

# 常用异常类型组合
NETWORK_ERRORS = [
    ConnectionError,
    ConnectionRefusedError,
    ConnectionResetError,
    TimeoutError,
    asyncio.TimeoutError
]

HTTP_SERVER_ERRORS = [500, 502, 503, 504]

def with_retry(
    max_retries: int = 3,
    delay: float = 0.5,
    exponential: bool = True
):
    """
    简化版重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间
        exponential: 是否使用指数退避

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt) if exponential else delay
                        logger.warning(f"Retrying {func.__name__} in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt) if exponential else delay
                        logger.warning(f"Retrying {func.__name__} in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
            raise last_exception

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
