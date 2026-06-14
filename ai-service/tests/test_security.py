"""
安全模块单元测试
测试输入验证和CSRF防护功能
"""

import unittest


class TestInputValidator(unittest.TestCase):
    """输入验证器测试"""

    def setUp(self):
        """设置测试环境"""
        from app.security.input_validator import InputValidator
        self.validator = InputValidator()

    def test_validate_string_length_valid(self):
        """测试有效字符串长度验证"""
        result = self.validator.validate_string_length(
            "test",
            min_length=1,
            max_length=10,
            field_name="test_field"
        )
        self.assertEqual(result, "test")

    def test_validate_string_length_too_short(self):
        """测试字符串长度过短"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.validate_string_length(
                "ab",
                min_length=3,
                field_name="test_field"
            )

    def test_validate_string_length_too_long(self):
        """测试字符串长度过长"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.validate_string_length(
                "a" * 20,
                max_length=10,
                field_name="test_field"
            )

    def test_validate_email_valid(self):
        """测试有效邮箱验证"""
        result = self.validator.validate_email("test@example.com")
        self.assertEqual(result, "test@example.com")

    def test_validate_email_invalid(self):
        """测试无效邮箱验证"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.validate_email("invalid-email")

    def test_validate_phone_valid(self):
        """测试有效手机号验证"""
        result = self.validator.validate_phone("13800138000")
        self.assertEqual(result, "13800138000")

    def test_validate_phone_invalid(self):
        """测试无效手机号验证"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.validate_phone("1234567890")

    def test_validate_url_valid(self):
        """测试有效URL验证"""
        result = self.validator.validate_url("https://example.com")
        self.assertEqual(result, "https://example.com")

    def test_validate_url_invalid(self):
        """测试无效URL验证"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.validate_url("not-a-url")

    def test_validate_number_range_valid(self):
        """测试有效数值范围验证"""
        result = self.validator.validate_number_range(50, min_value=0, max_value=100)
        self.assertEqual(result, 50)

    def test_validate_number_range_too_low(self):
        """测试数值过低"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.validate_number_range(-1, min_value=0)

    def test_validate_number_range_too_high(self):
        """测试数值过高"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.validate_number_range(101, max_value=100)

    def test_check_sql_injection_clean(self):
        """测试无SQL注入"""
        result = self.validator.check_sql_injection("normal text")
        self.assertEqual(result, "normal text")

    def test_check_sql_injection_detected(self):
        """测试SQL注入检测"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.check_sql_injection("'; DROP TABLE users; --")

    def test_check_xss_clean(self):
        """测试无XSS攻击"""
        result = self.validator.check_xss("normal text")
        self.assertEqual(result, "normal text")

    def test_check_xss_detected(self):
        """测试XSS攻击检测"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.check_xss("<script>alert('xss')</script>")

    def test_validate_username_valid(self):
        """测试有效用户名验证"""
        result = self.validator.validate_username("valid_user123")
        self.assertEqual(result, "valid_user123")

    def test_validate_username_invalid_chars(self):
        """测试用户名包含无效字符"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.validate_username("user@name")

    def test_validate_username_too_short(self):
        """测试用户名过短"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.validate_username("ab")

    def test_validate_password_valid(self):
        """测试有效密码验证"""
        result = self.validator.validate_password("password123")
        self.assertEqual(result, "password123")

    def test_validate_password_too_short(self):
        """测试密码过短"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.validate_password("12345")

    def test_validate_file_type_valid(self):
        """测试有效文件类型验证"""
        result = self.validator.validate_file_type(
            "document.pdf",
            ["pdf", "doc", "docx"]
        )
        self.assertEqual(result, "document.pdf")

    def test_validate_file_type_invalid(self):
        """测试无效文件类型验证"""
        from app.security.input_validator import ValidationError
        with self.assertRaises(ValidationError):
            self.validator.validate_file_type(
                "script.exe",
                ["pdf", "doc", "docx"]
            )


class TestCSRFTokenManager(unittest.TestCase):
    """CSRF Token管理器测试"""

    def setUp(self):
        """设置测试环境"""
        from app.security.csrf_protection import CSRFTokenManager
        self.csrf_manager = CSRFTokenManager()

    def test_generate_token(self):
        """测试生成Token"""
        token = self.csrf_manager.generate_token("session_123")
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

    def test_verify_token_valid(self):
        """测试验证有效Token"""
        session_id = "session_123"
        token = self.csrf_manager.generate_token(session_id)

        result = self.csrf_manager.verify_token(session_id, token)
        self.assertTrue(result)

    def test_verify_token_invalid(self):
        """测试验证无效Token"""
        session_id = "session_123"
        token = self.csrf_manager.generate_token(session_id)

        result = self.csrf_manager.verify_token(session_id, "wrong_token")
        self.assertFalse(result)

    def test_verify_token_no_session(self):
        """测试Session不存在"""
        result = self.csrf_manager.verify_token("nonexistent_session", "token")
        self.assertFalse(result)

    def test_remove_token(self):
        """测试移除Token"""
        session_id = "session_123"
        token = self.csrf_manager.generate_token(session_id)

        # 验证Token存在
        self.assertTrue(self.csrf_manager.verify_token(session_id, token))

        # 移除Token
        self.csrf_manager.remove_token(session_id)

        # 验证Token已不存在
        self.assertFalse(self.csrf_manager.verify_token(session_id, token))


class TestCSRFProtection(unittest.TestCase):
    """CSRF保护功能测试"""

    def test_generate_csrf_token(self):
        """测试生成CSRF Token便捷函数"""
        from app.security.csrf_protection import generate_csrf_token

        token = generate_csrf_token("session_123")
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)


if __name__ == '__main__':
    unittest.main(verbosity=2)
