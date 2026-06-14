"""
输入验证模块
提供全面的输入验证功能，防止恶意输入
"""

import re
import html
from typing import Any, List, Optional, Union
from pydantic import BaseModel, validator, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """验证错误异常"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class InputValidator:
    """输入验证器"""

    # SQL注入危险关键字
    SQL_DANGEROUS_KEYWORDS = [
        r'\b(union|select|insert|update|delete|drop|create|alter|truncate)\b',
        r'--', r'/\*', r'\*/', r'xp_', r'sp_',
        r'exec\s*\(', r'execute\s*\(',
        r'<script', r'javascript:',
    ]

    # XSS危险模式
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe',
        r'<object',
        r'<embed',
    ]

    # 邮箱验证正则
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    # 手机号验证正则（中国大陆）
    PHONE_PATTERN = r'^1[3-9]\d{9}$'

    # URL验证正则
    URL_PATTERN = r'^https?://[^\s/$.?#].[^\s]*$'

    @classmethod
    def validate_string_length(
        cls,
        value: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        field_name: str = "field"
    ) -> str:
        """
        验证字符串长度

        Args:
            value: 待验证字符串
            min_length: 最小长度
            max_length: 最大长度
            field_name: 字段名称（用于错误信息）

        Returns:
            验证通过的字符串

        Raises:
            ValidationError: 验证失败时抛出
        """
        if not isinstance(value, str):
            raise ValidationError(field_name, "必须是字符串")

        length = len(value)

        if min_length is not None and length < min_length:
            raise ValidationError(field_name, f"长度不能少于{min_length}个字符")

        if max_length is not None and length > max_length:
            raise ValidationError(field_name, f"长度不能超过{max_length}个字符")

        return value

    @classmethod
    def validate_email(cls, email: str, field_name: str = "email") -> str:
        """
        验证邮箱格式

        Args:
            email: 邮箱地址
            field_name: 字段名称

        Returns:
            验证通过的邮箱

        Raises:
            ValidationError: 验证失败时抛出
        """
        if not email:
            raise ValidationError(field_name, "邮箱不能为空")

        if not re.match(cls.EMAIL_PATTERN, email):
            raise ValidationError(field_name, "邮箱格式不正确")

        return email.lower()

    @classmethod
    def validate_phone(cls, phone: str, field_name: str = "phone") -> str:
        """
        验证手机号格式（中国大陆）

        Args:
            phone: 手机号
            field_name: 字段名称

        Returns:
            验证通过的手机号

        Raises:
            ValidationError: 验证失败时抛出
        """
        if not phone:
            raise ValidationError(field_name, "手机号不能为空")

        if not re.match(cls.PHONE_PATTERN, phone):
            raise ValidationError(field_name, "手机号格式不正确")

        return phone

    @classmethod
    def validate_url(cls, url: str, field_name: str = "url") -> str:
        """
        验证URL格式

        Args:
            url: URL地址
            field_name: 字段名称

        Returns:
            验证通过的URL

        Raises:
            ValidationError: 验证失败时抛出
        """
        if not url:
            raise ValidationError(field_name, "URL不能为空")

        if not re.match(cls.URL_PATTERN, url):
            raise ValidationError(field_name, "URL格式不正确")

        return url

    @classmethod
    def validate_number_range(
        cls,
        value: Union[int, float],
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        field_name: str = "number"
    ) -> Union[int, float]:
        """
        验证数值范围

        Args:
            value: 数值
            min_value: 最小值
            max_value: 最大值
            field_name: 字段名称

        Returns:
            验证通过的数值

        Raises:
            ValidationError: 验证失败时抛出
        """
        if not isinstance(value, (int, float)):
            raise ValidationError(field_name, "必须是数字")

        if min_value is not None and value < min_value:
            raise ValidationError(field_name, f"值不能小于{min_value}")

        if max_value is not None and value > max_value:
            raise ValidationError(field_name, f"值不能大于{max_value}")

        return value

    @classmethod
    def check_sql_injection(cls, value: str, field_name: str = "input") -> str:
        """
        检测SQL注入

        Args:
            value: 待检测字符串
            field_name: 字段名称

        Returns:
            检测通过的字符串

        Raises:
            ValidationError: 检测到SQL注入时抛出
        """
        if not value:
            return value

        value_lower = value.lower()

        for pattern in cls.SQL_DANGEROUS_KEYWORDS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"SQL injection detected in {field_name}: {value}")
                raise ValidationError(
                    field_name,
                    "输入包含可疑的SQL关键字"
                )

        return value

    @classmethod
    def check_xss(cls, value: str, field_name: str = "input") -> str:
        """
        检测XSS攻击

        Args:
            value: 待检测字符串
            field_name: 字段名称

        Returns:
            检测通过的字符串

        Raises:
            ValidationError: 检测到XSS攻击时抛出
        """
        if not value:
            return value

        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"XSS pattern detected in {field_name}: {value}")
                raise ValidationError(
                    field_name,
                    "输入包含可疑的脚本内容"
                )

        return value

    @classmethod
    def sanitize_input(cls, value: str, field_name: str = "input") -> str:
        """
        清洗输入数据

        Args:
            value: 待清洗字符串
            field_name: 字段名称

        Returns:
            清洗后的字符串
        """
        if not value:
            return value

        # HTML转义
        value = html.escape(value)

        # 移除多余的空白字符
        value = re.sub(r'\s+', ' ', value)

        return value.strip()

    @classmethod
    def validate_file_type(
        cls,
        filename: str,
        allowed_types: List[str],
        field_name: str = "file"
    ) -> str:
        """
        验证文件类型

        Args:
            filename: 文件名
            allowed_types: 允许的文件类型列表
            field_name: 字段名称

        Returns:
            验证通过的文件名

        Raises:
            ValidationError: 验证失败时抛出
        """
        if not filename:
            raise ValidationError(field_name, "文件名不能为空")

        # 获取文件扩展名
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

        if ext not in allowed_types:
            raise ValidationError(
                field_name,
                f"不支持的文件类型，仅支持: {', '.join(allowed_types)}"
            )

        return filename

    @classmethod
    def validate_username(cls, username: str) -> str:
        """
        验证用户名

        Args:
            username: 用户名

        Returns:
            验证通过的用户名

        Raises:
            ValidationError: 验证失败时抛出
        """
        # 长度检查
        cls.validate_string_length(
            username,
            min_length=3,
            max_length=20,
            field_name="username"
        )

        # 格式检查：只能包含字母、数字和下划线
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError(
                "username",
                "用户名只能包含字母、数字和下划线"
            )

        # 检查SQL注入
        cls.check_sql_injection(username, "username")

        # 检查XSS
        cls.check_xss(username, "username")

        return username

    @classmethod
    def validate_password(cls, password: str) -> str:
        """
        验证密码强度

        Args:
            password: 密码

        Returns:
            验证通过的密码

        Raises:
            ValidationError: 验证失败时抛出
        """
        if len(password) < 6:
            raise ValidationError("password", "密码长度至少6位")

        if len(password) > 128:
            raise ValidationError("password", "密码长度不能超过128位")

        return password

    @classmethod
    def validate_all(
        cls,
        data: dict,
        rules: dict
    ) -> dict:
        """
        批量验证数据

        Args:
            data: 待验证数据字典
            rules: 验证规则字典

        Returns:
            验证通过的数据字典

        Raises:
            ValidationError: 验证失败时抛出
        """
        validated_data = {}

        for field, rule in rules.items():
            value = data.get(field)

            # 应用验证规则
            if 'type' in rule:
                if rule['type'] == 'string':
                    cls.validate_string_length(
                        value,
                        rule.get('min_length'),
                        rule.get('max_length'),
                        field
                    )
                elif rule['type'] == 'email':
                    value = cls.validate_email(value, field)
                elif rule['type'] == 'phone':
                    value = cls.validate_phone(value, field)
                elif rule['type'] == 'url':
                    value = cls.validate_url(value, field)
                elif rule['type'] == 'number':
                    value = cls.validate_number_range(
                        value,
                        rule.get('min_value'),
                        rule.get('max_value'),
                        field
                    )

            # SQL注入检查
            if rule.get('check_sql', False) and value:
                value = cls.check_sql_injection(value, field)

            # XSS检查
            if rule.get('check_xss', False) and value:
                value = cls.check_xss(value, field)

            # 必填检查
            if rule.get('required', False) and not value:
                raise ValidationError(field, "此字段为必填项")

            validated_data[field] = value

        return validated_data


# Pydantic验证模型
class UsernameField(str):
    """用户名字段"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('必须是字符串')
        return InputValidator.validate_username(v)


class EmailField(str):
    """邮箱字段"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('必须是字符串')
        return InputValidator.validate_email(v)


class PhoneField(str):
    """手机号字段"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('必须是字符串')
        return InputValidator.validate_phone(v)
