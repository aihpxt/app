#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常处理单元测试
覆盖自定义异常等核心功能
"""

import pytest
from app.core.exceptions import (
    AppException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    InternalServerErrorException,
    RateLimitExceededException
)


class TestAppException:
    """应用异常测试"""
    
    def test_app_exception_initialization(self):
        """测试应用异常初始化"""
        exc = AppException(
            status_code=400,
            detail="测试错误",
            error_code="TEST_ERROR"
        )
        
        assert exc.status_code == 400
        assert exc.detail["error"]["code"] == "TEST_ERROR"
        assert exc.detail["error"]["message"] == "测试错误"
    
    def test_bad_request_exception(self):
        """测试400错误"""
        exc = BadRequestException("参数错误")
        assert exc.status_code == 400
        assert exc.detail["error"]["code"] == "BAD_REQUEST"
    
    def test_unauthorized_exception(self):
        """测试401错误"""
        exc = UnauthorizedException("未登录")
        assert exc.status_code == 401
        assert exc.detail["error"]["message"] == "未登录"
    
    def test_forbidden_exception(self):
        """测试403错误"""
        exc = ForbiddenException("无权限")
        assert exc.status_code == 403
        assert exc.detail["error"]["code"] == "FORBIDDEN"
    
    def test_not_found_exception(self):
        """测试404错误"""
        exc = NotFoundException("资源不存在")
        assert exc.status_code == 404
        assert exc.detail["error"]["message"] == "资源不存在"
    
    def test_internal_server_error_exception(self):
        """测试500错误"""
        exc = InternalServerErrorException("服务器错误")
        assert exc.status_code == 500
        assert exc.detail["error"]["code"] == "INTERNAL_SERVER_ERROR"
    
    def test_rate_limit_exception(self):
        """测试速率限制异常"""
        exc = RateLimitExceededException()
        assert exc.status_code == 429
        assert exc.detail["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    
    def test_exception_headers(self):
        """测试异常响应头"""
        exc = UnauthorizedException()
        assert exc.headers is not None
        assert "WWW-Authenticate" in exc.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])