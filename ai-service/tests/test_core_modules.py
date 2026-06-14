#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心模块单元测试
覆盖缓存、验证器、响应格式化等核心功能
"""

import pytest
import time
from app.core.cache import Cache
from app.core.validator import DataValidator
from app.core.response_formatter import ResponseFormatter
from app.core.string_utils import StringUtils


class TestCache:
    """缓存模块测试"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.cache = Cache(maxsize=10, ttl=1)
    
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
        # 使用类默认的ttl=1秒
        self.cache.set("temp_key", "temp_value")
        time.sleep(1.1)
        result = self.cache.get("temp_key")
        assert result is None
    
    def test_cache_eviction(self):
        """测试缓存淘汰（LRU）"""
        for i in range(15):
            self.cache.set(f"key_{i}", f"value_{i}")
        
        stats = self.cache.get_stats()
        assert stats["evictions"] >= 5
    
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
        stats = self.cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert self.cache.get("key1") is None
    
    def test_cache_stats(self):
        """测试缓存统计"""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # hit
        self.cache.get("key1")  # hit
        self.cache.get("nonexistent")  # miss
        
        stats = self.cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["sets"] == 1
    
    def test_cache_hit_rate(self):
        """测试缓存命中率"""
        self.cache.set("key", "value")
        self.cache.get("key")
        self.cache.get("key")
        self.cache.get("nonexistent")
        
        hit_rate = self.cache.get_hit_rate()
        assert hit_rate == 2 / 3


class TestDataValidator:
    """数据验证器测试"""
    
    def test_valid_email(self):
        """测试邮箱验证"""
        assert DataValidator.is_valid_email("test@example.com") is True
        assert DataValidator.is_valid_email("invalid-email") is False
        assert DataValidator.is_valid_email("@missing-local.com") is False
    
    def test_valid_phone(self):
        """测试手机号验证"""
        assert DataValidator.is_valid_phone("13800138000") is True
        assert DataValidator.is_valid_phone("12345678901") is False  # 第二位不是3-9
        assert DataValidator.is_valid_phone("1380013800") is False  # 长度不对
    
    def test_valid_username(self):
        """测试用户名验证"""
        assert DataValidator.is_valid_username("test_user") is True
        assert DataValidator.is_valid_username("ab") is False  # 太短
        assert DataValidator.is_valid_username("test@user") is False  # 包含特殊字符
    
    def test_valid_password(self):
        """测试密码验证"""
        result = DataValidator.is_valid_password("Pass123!")
        assert result["valid"] is True
        assert result["strength"] == 100
        
        weak_result = DataValidator.is_valid_password("weak")
        assert weak_result["valid"] is False
        assert len(weak_result["issues"]) > 0
    
    def test_valid_url(self):
        """测试URL验证"""
        assert DataValidator.is_valid_url("https://www.example.com") is True
        assert DataValidator.is_valid_url("http://example.com/path") is True
        assert DataValidator.is_valid_url("invalid-url") is False
    
    def test_sanitize_string(self):
        """测试字符串清理"""
        result = DataValidator.sanitize_string("  hello world  ", max_length=10)
        assert result == "hello worl"
        assert DataValidator.sanitize_string(None) == ""
    
    def test_valid_int(self):
        """测试整数验证"""
        assert DataValidator.is_valid_int(10) is True
        assert DataValidator.is_valid_int(10, min_val=5, max_val=15) is True
        assert DataValidator.is_valid_int(20, max_val=15) is False


class TestResponseFormatter:
    """响应格式化器测试"""
    
    def test_format_success(self):
        """测试成功响应格式化"""
        data = {"key": "value"}
        result = ResponseFormatter.success(data, "操作成功")
        
        assert result["success"] is True
        assert result["data"] == data
        assert result["message"] == "操作成功"
    
    def test_format_error(self):
        """测试错误响应格式化"""
        result = ResponseFormatter.error("错误信息")
        
        assert result["success"] is False
        assert result["message"] == "错误信息"
    
    def test_format_pagination(self):
        """测试分页响应格式化"""
        items = [1, 2, 3]
        result = ResponseFormatter.paginated(items, page=1, page_size=10, total=100)
        
        assert result["success"] is True
        assert result["data"]["items"] == items
        assert result["data"]["pagination"]["total"] == 100
        assert result["data"]["pagination"]["page"] == 1


class TestStringUtils:
    """字符串工具测试"""
    
    def test_truncate(self):
        """测试字符串截断"""
        result = StringUtils.truncate("Hello World", 5)
        assert result == "He..."  # 包含后缀"..."
        
        result = StringUtils.truncate("Short", 10)
        assert result == "Short"
    
    def test_strip_html(self):
        """测试移除HTML标签"""
        result = StringUtils.strip_html("<p>Hello <b>World</b></p>")
        assert result == "Hello World"
    
    def test_slugify(self):
        """测试生成slug"""
        result = StringUtils.slugify("Hello World!")
        assert result == "hello-world"
    
    def test_generate_uuid(self):
        """测试生成UUID"""
        result = StringUtils.generate_uuid()
        assert len(result) == 36
        assert result.count("-") == 4
    
    def test_generate_id(self):
        """测试生成唯一ID"""
        result = StringUtils.generate_id("test_")
        assert result.startswith("test_")
        assert len(result) == len("test_") + 32
    
    def test_hash_string(self):
        """测试哈希字符串"""
        result = StringUtils.hash_string("test")
        assert len(result) == 64  # SHA256 produces 64 hex characters
    
    def test_extract_emails(self):
        """测试提取邮箱"""
        text = "联系我们: test@example.com 或 support@company.org"
        result = StringUtils.extract_emails(text)
        assert "test@example.com" in result
        assert "support@company.org" in result
    
    def test_extract_urls(self):
        """测试提取URL"""
        text = "访问 https://www.example.com 和 http://test.org/path"
        result = StringUtils.extract_urls(text)
        assert "https://www.example.com" in result
        assert "http://test.org/path" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])