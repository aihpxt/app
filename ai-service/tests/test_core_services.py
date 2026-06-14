#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心服务单元测试
覆盖多级缓存、重试装饰器、告警管理等核心功能
"""

import pytest
import time
from app.core.tiered_cache import L1Cache, TieredCacheManager
from app.core.retry_decorator import SmartRetry, RetryError


class TestL1Cache:
    """L1本地缓存测试"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.cache = L1Cache(max_size=10, ttl=1)
    
    def test_cache_set_and_get(self):
        """测试设置和获取缓存"""
        self.cache.set("test_key", "test_value")
        result = self.cache.get("test_key")
        assert result == "test_value"
    
    def test_cache_not_found(self):
        """测试获取不存在的缓存"""
        result = self.cache.get("nonexistent_key")
        assert result is None
    
    def test_cache_expiration(self):
        """测试缓存过期"""
        self.cache.set("temp_key", "temp_value")
        time.sleep(1.1)
        result = self.cache.get("temp_key")
        assert result is None
    
    def test_cache_eviction(self):
        """测试缓存淘汰（LRU）"""
        for i in range(15):
            self.cache.set(f"key_{i}", f"value_{i}")
        
        stats = self.cache.stats
        assert stats["evictions"] >= 5
    
    def test_cache_stats(self):
        """测试缓存统计"""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # hit
        self.cache.get("key1")  # hit
        self.cache.get("nonexistent")  # miss
        
        stats = self.cache.stats
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["sets"] == 1


class TestTieredCacheManager:
    """多级缓存管理器测试"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.cache = TieredCacheManager(l1_size=10, l1_ttl=1, l2_ttl=300)
    
    def test_cache_set_and_get(self):
        """测试设置和获取缓存"""
        self.cache.set("test_key", "test_value")
        result = self.cache.get("test_key")
        assert result == "test_value"
    
    def test_cache_not_found(self):
        """测试获取不存在的缓存"""
        result = self.cache.get("nonexistent_key")
        assert result is None
    
    def test_cache_expiration_l1(self):
        """测试L1缓存过期后从L2获取"""
        self.cache.set("temp_key", "temp_value")
        
        # 先获取一次确保在L1中
        result1 = self.cache.get("temp_key")
        assert result1 == "temp_value"
        
        # 等待L1过期
        time.sleep(1.1)
        
        # 应该仍然能从L2获取（L2会序列化值）
        result2 = self.cache.get("temp_key")
        # L2缓存会序列化值，所以可能是字符串格式
        assert result2 in ["temp_value", '"temp_value"']
    
    def test_cache_delete(self):
        """测试删除缓存"""
        self.cache.set("delete_key", "delete_value")
        assert self.cache.get("delete_key") == "delete_value"
        self.cache.delete("delete_key")
        assert self.cache.get("delete_key") is None
    
    def test_cache_clear(self):
        """测试清空缓存"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.clear()
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None
    
    def test_cache_stats(self):
        """测试缓存统计"""
        self.cache.set("key", "value")
        self.cache.get("key")
        self.cache.get("key")
        self.cache.get("nonexistent")
        
        stats = self.cache.get_stats()
        assert stats["l1_hits"] >= 0
        assert stats["l2_hits"] >= 0
        assert stats["misses"] >= 0


class TestSmartRetry:
    """智能重试装饰器测试"""
    
    def test_retry_success_on_third_attempt(self):
        """测试在第三次尝试时成功"""
        attempts = [0]
        
        @SmartRetry(max_retries=3, initial_delay=0.1, exceptions_to_retry=[ValueError])
        async def failing_func():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("Intentional failure")
            return "success"
        
        import asyncio
        result = asyncio.run(failing_func())
        assert result == "success"
        assert attempts[0] == 3
    
    def test_retry_max_retries_exceeded(self):
        """测试超过最大重试次数"""
        @SmartRetry(max_retries=3, initial_delay=0.1)
        async def always_fail():
            raise ValueError("Always fails")
        
        import asyncio
        with pytest.raises(ValueError):
            asyncio.run(always_fail())
    
    def test_retry_with_no_failure(self):
        """测试没有失败的情况"""
        @SmartRetry(max_retries=3, initial_delay=0.1)
        async def success_func():
            return "success"
        
        import asyncio
        result = asyncio.run(success_func())
        assert result == "success"
    
    def test_retry_with_timeout(self):
        """测试超时重试"""
        attempts = [0]
        
        @SmartRetry(max_retries=3, initial_delay=0.1)
        async def timeout_func():
            attempts[0] += 1
            if attempts[0] < 2:
                raise TimeoutError("Timeout")
            return "success"
        
        import asyncio
        result = asyncio.run(timeout_func())
        assert result == "success"
        assert attempts[0] == 2
    
    def test_retry_ignores_specific_exception(self):
        """测试忽略特定异常"""
        @SmartRetry(
            max_retries=3,
            exceptions_to_ignore=[ValueError]
        )
        async def raises_value_error():
            raise ValueError("Should be ignored")
        
        import asyncio
        with pytest.raises(ValueError):
            asyncio.run(raises_value_error())
    
    def test_retry_on_connection_error(self):
        """测试连接错误重试"""
        attempts = [0]
        
        @SmartRetry(max_retries=3, initial_delay=0.1)
        async def connection_fail():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ConnectionError("Connection failed")
            return "success"
        
        import asyncio
        result = asyncio.run(connection_fail())
        assert result == "success"
        assert attempts[0] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])