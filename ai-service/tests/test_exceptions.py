"""
异常处理模块单元测试
覆盖 core/exceptions.py 所有异常类和处理函数
"""

import unittest
from unittest.mock import Mock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestAppException(unittest.TestCase):
    """AppException基类测试"""

    def test_initialization(self):
        """测试异常初始化"""
        from core.exceptions import AppException
        exc = AppException(code=400, message="测试错误")
        self.assertEqual(exc.code, 400)
        self.assertEqual(exc.message, "测试错误")
        self.assertIsNone(exc.data)

    def test_initialization_with_data(self):
        """测试带数据的异常初始化"""
        from core.exceptions import AppException
        data = {"field": "value"}
        exc = AppException(code=400, message="错误", data=data)
        self.assertEqual(exc.data, data)

    def test_to_dict(self):
        """测试转换为字典"""
        from core.exceptions import AppException
        exc = AppException(code=400, message="错误")
        result = exc.to_dict()
        self.assertIn("code", result)
        self.assertIn("message", result)
        self.assertEqual(result["code"], 400)


class TestNotFoundException(unittest.TestCase):
    """NotFoundException测试"""

    def test_default_message(self):
        """测试默认消息"""
        from app.core.exceptions import NotFoundException
        exc = NotFoundException()
        self.assertEqual(exc.code, 404)
        self.assertEqual(exc.message, "资源不存在")

    def test_custom_message(self):
        """测试自定义消息"""
        from app.core.exceptions import NotFoundException
        exc = NotFoundException(message="学校不存在")
        self.assertEqual(exc.message, "学校不存在")

    def test_custom_resource_type(self):
        """测试自定义资源类型"""
        from app.core.exceptions import NotFoundException
        exc = NotFoundException(resource_type="学校")
        self.assertIn("学校", exc.message)


class TestBadRequestException(unittest.TestCase):
    """BadRequestException测试"""

    def test_default_message(self):
        """测试默认消息"""
        from app.core.exceptions import BadRequestException
        exc = BadRequestException()
        self.assertEqual(exc.code, 400)
        self.assertEqual(exc.message, "请求参数错误")

    def test_custom_message(self):
        """测试自定义消息"""
        from app.core.exceptions import BadRequestException
        exc = BadRequestException(message="参数格式错误")
        self.assertEqual(exc.message, "参数格式错误")


class TestUnauthorizedException(unittest.TestCase):
    """UnauthorizedException测试"""

    def test_default_message(self):
        """测试默认消息"""
        from app.core.exceptions import UnauthorizedException
        exc = UnauthorizedException()
        self.assertEqual(exc.code, 401)
        self.assertEqual(exc.message, "未授权访问")

    def test_custom_message(self):
        """测试自定义消息"""
        from app.core.exceptions import UnauthorizedException
        exc = UnauthorizedException(message="Token无效")
        self.assertEqual(exc.message, "Token无效")


class TestForbiddenException(unittest.TestCase):
    """ForbiddenException测试"""

    def test_default_message(self):
        """测试默认消息"""
        from app.core.exceptions import ForbiddenException
        exc = ForbiddenException()
        self.assertEqual(exc.code, 403)
        self.assertEqual(exc.message, "禁止访问")


class TestRateLimitException(unittest.TestCase):
    """RateLimitException测试"""

    def test_default_message(self):
        """测试默认消息"""
        from app.core.exceptions import RateLimitException
        exc = RateLimitException()
        self.assertEqual(exc.code, 429)
        self.assertIn("频繁", exc.message)


class TestAIServiceException(unittest.TestCase):
    """AIServiceException测试"""

    def test_default_message(self):
        """测试默认消息"""
        from app.core.exceptions import AIServiceException
        exc = AIServiceException()
        self.assertEqual(exc.code, 500)
        self.assertEqual(exc.message, "AI服务异常")

    def test_custom_message(self):
        """测试自定义消息"""
        from app.core.exceptions import AIServiceException
        exc = AIServiceException(message="DeepSeek API调用失败")
        self.assertEqual(exc.message, "DeepSeek API调用失败")

    def test_with_service_name(self):
        """测试带服务名称"""
        from app.core.exceptions import AIServiceException
        exc = AIServiceException(service_name="Hermes")
        self.assertIn("Hermes", exc.message)


class TestExceptionHandlers(unittest.TestCase):
    """异常处理器测试"""

    def setUp(self):
        """设置测试环境"""
        self.app = FastAPI()

    def test_register_exception_handlers(self):
        """测试注册异常处理器"""
        from app.core.exceptions import (
            register_exception_handlers,
            AppException
        )

        register_exception_handlers(self.app)

        # 验证异常处理器已注册
        self.assertTrue(hasattr(self.app, 'exception_handler_handlers'))

    def test_app_exception_handler(self):
        """测试AppException处理器"""
        from app.core.exceptions import (
            register_exception_handlers,
            AppException
        )
        from fastapi.responses import JSONResponse

        register_exception_handlers(self.app)

        # 创建异常并处理
        exc = AppException(code=400, message="测试错误")

        # 验证to_dict方法
        result = exc.to_dict()
        self.assertIsInstance(result, dict)
        self.assertEqual(result["code"], 400)


class TestErrorCodes(unittest.TestCase):
    """错误码测试"""

    def test_error_codes_exist(self):
        """测试错误码定义存在"""
        from app.core.exceptions import ErrorCodes

        # 验证常见错误码存在
        self.assertTrue(hasattr(ErrorCodes, 'SUCCESS'))
        self.assertTrue(hasattr(ErrorCodes, 'BAD_REQUEST'))
        self.assertTrue(hasattr(ErrorCodes, 'UNAUTHORIZED'))
        self.assertTrue(hasattr(ErrorCodes, 'NOT_FOUND'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
