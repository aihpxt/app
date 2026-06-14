"""数据验证工具"""

import re
from typing import Optional, List, Dict, Any
from datetime import datetime

class DataValidator:
    """数据验证器"""

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """验证手机号格式（中国）"""
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def is_valid_username(username: str, min_length: int = 3, max_length: int = 20) -> bool:
        """验证用户名"""
        if len(username) < min_length or len(username) > max_length:
            return False
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, username))

    @staticmethod
    def is_valid_password(password: str, min_length: int = 8, require_special: bool = True) -> Dict[str, Any]:
        """验证密码强度"""
        issues: List[str] = []

        if len(password) < min_length:
            issues.append(f"密码长度至少{min_length}位")

        if not re.search(r'[a-z]', password):
            issues.append("需要包含小写字母")

        if not re.search(r'[A-Z]', password):
            issues.append("需要包含大写字母")

        if not re.search(r'\d', password):
            issues.append("需要包含数字")

        if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("需要包含特殊字符")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "strength": (4 - len(issues)) / 4 * 100
        }

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """验证URL格式"""
        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return bool(re.match(pattern, url))

    @staticmethod
    def sanitize_string(text: str, max_length: int = 500) -> str:
        """清理字符串"""
        if not text:
            return ""
        cleaned = text.strip()
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
        return cleaned

    @staticmethod
    def is_valid_int(value: Any, min_val: Optional[int] = None, max_val: Optional[int] = None) -> bool:
        """验证整数"""
        try:
            num = int(value)
            if min_val is not None and num < min_val:
                return False
            if max_val is not None and num > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_valid_float(value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
        """验证浮点数"""
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                return False
            if max_val is not None and num > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_dict(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """验证字典数据"""
        errors: Dict[str, str] = {}
        cleaned: Dict[str, Any] = {}

        for field, rules in schema.items():
            value = data.get(field)
            required = rules.get('required', False)
            field_type = rules.get('type')
            default = rules.get('default')

            if value is None:
                if required:
                    errors[field] = "字段必填"
                else:
                    cleaned[field] = default
                continue

            try:
                if field_type == str:
                    value = str(value)
                    if 'max_length' in rules and len(value) > rules['max_length']:
                        errors[field] = f"长度不能超过{rules['max_length']}"
                    if 'min_length' in rules and len(value) < rules['min_length']:
                        errors[field] = f"长度不能少于{rules['min_length']}"
                elif field_type == int:
                    value = int(value)
                    if 'min' in rules and value < rules['min']:
                        errors[field] = f"不能小于{rules['min']}"
                    if 'max' in rules and value > rules['max']:
                        errors[field] = f"不能大于{rules['max']}"
                elif field_type == float:
                    value = float(value)
                    if 'min' in rules and value < rules['min']:
                        errors[field] = f"不能小于{rules['min']}"
                    if 'max' in rules and value > rules['max']:
                        errors[field] = f"不能大于{rules['max']}"
                elif field_type == list:
                    value = list(value)
                    if 'min_items' in rules and len(value) < rules['min_items']:
                        errors[field] = f"最少需要{rules['min_items']}个项目"
                    if 'max_items' in rules and len(value) > rules['max_items']:
                        errors[field] = f"最多{rules['max_items']}个项目"

                cleaned[field] = value
            except (ValueError, TypeError):
                errors[field] = f"类型错误，需要{field_type}"

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "data": cleaned
        }

# 全局验证器实例
_validator = DataValidator()

def get_validator() -> DataValidator:
    """获取验证器实例"""
    return _validator
