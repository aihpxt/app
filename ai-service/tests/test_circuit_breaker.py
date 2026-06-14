"""
熔断器模块单元测试
覆盖 circuit_breaker.py 所有功能
"""

import unittest
import time
from unittest.mock import Mock, patch
from app.core.circuit_breaker import (
    CircuitState,
    CircuitBreaker,
    CircuitBreakerRegistry,
    CircuitBreakerOpenError,
    circuit_breaker
)


class TestCircuitState(unittest.TestCase):
    """CircuitState枚举测试"""

    def test_state_values(self):
        """测试状态值"""
        self.assertEqual(CircuitState.CLOSED.value, "closed")
        self.assertEqual(CircuitState.OPEN.value, "open")
        self.assertEqual(CircuitState.HALF_OPEN.value, "half_open")

    def test_state_count(self):
        """测试状态数量"""
        self.assertEqual(len(CircuitState), 3)


class TestCircuitBreaker(unittest.TestCase):
    """CircuitBreaker类测试"""

    def setUp(self):
        """设置测试环境"""
        self.breaker = CircuitBreaker(
            name="test_breaker",
            failure_threshold=3,
            timeout=10,
            half_open_max_calls=2
        )

    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.breaker.failure_threshold, 3)
        self.assertEqual(self.breaker.timeout, 10)
        self.assertEqual(self.breaker.half_open_max_calls, 2)
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)

    def test_initial_state_is_closed(self):
        """测试初始状态为关闭"""
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)

    def test_record_success_closed_to_half_open(self):
        """测试成功记录不会改变关闭状态"""
        for _ in range(5):
            self.breaker.record_success()
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)

    def test_record_failure_closed_to_open(self):
        """测试失败次数达到阈值时变为打开状态"""
        for _ in range(3):
            self.breaker.record_failure()

        self.assertEqual(self.breaker.state, CircuitState.OPEN)
        self.assertEqual(self.breaker.failure_count, 3)

    def test_can_execute_closed_state(self):
        """测试关闭状态可以执行"""
        can_exec, _ = self.breaker.can_execute()
        self.assertTrue(can_exec)

    def test_can_execute_open_state(self):
        """测试打开状态不能执行"""
        # 触发熔断
        for _ in range(3):
            self.breaker.record_failure()

        self.assertEqual(self.breaker.state, CircuitState.OPEN)
        can_exec, _ = self.breaker.can_execute()
        self.assertFalse(can_exec)

    def test_half_open_after_timeout(self):
        """测试超时后进入半开状态"""
        # 触发熔断
        for _ in range(3):
            self.breaker.record_failure()

        self.assertEqual(self.breaker.state, CircuitState.OPEN)

        # 模拟超时（直接修改last_failure_time）
        self.breaker.last_failure_time = time.time() - 15

        # 检查状态
        can_exec, _ = self.breaker.can_execute()
        self.assertTrue(can_exec)

    def test_half_open_to_closed_on_success(self):
        """测试半开状态成功后变为关闭"""
        # 触发熔断
        for _ in range(3):
            self.breaker.record_failure()

        # 进入半开状态
        self.breaker.last_failure_time = time.time() - 15
        self.breaker.state = CircuitState.HALF_OPEN

        # 成功调用
        self.breaker.record_success()
        self.assertEqual(self.breaker.state, CircuitState.CLOSED)

    def test_half_open_to_open_on_failure(self):
        """测试半开状态失败后重新打开"""
        # 触发熔断
        for _ in range(3):
            self.breaker.record_failure()

        # 进入半开状态
        self.breaker.last_failure_time = time.time() - 15
        self.breaker.state = CircuitState.HALF_OPEN

        # 失败调用
        self.breaker.record_failure()
        self.assertEqual(self.breaker.state, CircuitState.OPEN)

    def test_reset(self):
        """测试重置功能"""
        # 触发熔断
        for _ in range(3):
            self.breaker.record_failure()

        self.breaker.reset()

        self.assertEqual(self.breaker.state, CircuitState.CLOSED)
        self.assertEqual(self.breaker.failure_count, 0)

    def test_get_stats(self):
        """测试获取统计信息"""
        # 记录一些成功和失败
        self.breaker.record_success()
        self.breaker.record_failure()
        self.breaker.record_failure()

        stats = self.breaker.get_stats()

        self.assertIn("state", stats)
        self.assertIn("failure_count", stats)
        self.assertEqual(stats["failure_count"], 2)

    def test_call_decorator_success(self):
        """测试调用装饰器成功"""
        @self.breaker
        def test_function():
            return "success"

        result = test_function()
        self.assertEqual(result, "success")

    def test_call_decorator_failure(self):
        """测试调用装饰器失败"""
        @self.breaker
        def test_function():
            raise Exception("Test error")

        with self.assertRaises(Exception):
            test_function()


class TestCircuitBreakerRegistry(unittest.TestCase):
    """CircuitBreakerRegistry测试"""

    def setUp(self):
        """设置测试环境"""
        self.registry = CircuitBreakerRegistry()

    def test_register(self):
        """测试注册熔断器"""
        breaker = CircuitBreaker()
        self.registry.register("test_service", breaker)

        self.assertIn("test_service", self.registry.get_all_names())

    def test_get_existing(self):
        """测试获取已注册的熔断器"""
        breaker = CircuitBreaker()
        self.registry.register("test_service", breaker)

        retrieved = self.registry.get("test_service")
        self.assertIsNotNone(retrieved)

    def test_get_nonexistent(self):
        """测试获取不存在的熔断器"""
        retrieved = self.registry.get("nonexistent")
        self.assertIsNone(retrieved)

    def test_unregister(self):
        """测试注销熔断器"""
        breaker = CircuitBreaker()
        self.registry.register("test_service", breaker)
        self.registry.unregister("test_service")

        self.assertNotIn("test_service", self.registry.get_all_names())

    def test_get_all_breakers(self):
        """测试获取所有熔断器"""
        breaker1 = CircuitBreaker()
        breaker2 = CircuitBreaker()

        self.registry.register("service1", breaker1)
        self.registry.register("service2", breaker2)

        all_breakers = self.registry.get_all_breakers()
        self.assertEqual(len(all_breakers), 2)

    def test_clear(self):
        """测试清除所有熔断器"""
        breaker = CircuitBreaker()
        self.registry.register("test_service", breaker)
        self.registry.clear()

        self.assertEqual(len(self.registry.get_all_names()), 0)


class TestCircuitBreakerOpenError(unittest.TestCase):
    """CircuitBreakerOpenError测试"""

    def test_initialization(self):
        """测试初始化"""
        error = CircuitBreakerOpenError("test_service")
        self.assertIn("test_service", str(error))
        self.assertIn("open", str(error).lower())

    def test_inheritance(self):
        """测试异常继承"""
        error = CircuitBreakerOpenError("test_service")
        self.assertIsInstance(error, Exception)


class TestCircuitBreakerDecorator(unittest.TestCase):
    """circuit_breaker装饰器测试"""

    def test_decorator_with_custom_params(self):
        """测试带自定义参数的装饰器"""
        @circuit_breaker(failure_threshold=5, timeout=20)
        def test_function():
            return "result"

        result = test_function()
        self.assertEqual(result, "result")


if __name__ == '__main__':
    unittest.main(verbosity=2)
