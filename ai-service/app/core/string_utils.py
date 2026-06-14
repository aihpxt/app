"""字符串和文本工具"""

import re
import uuid
import hashlib
from typing import List, Optional
from urllib.parse import urlencode

class StringUtils:
    """字符串工具"""

    @staticmethod
    def generate_uuid() -> str:
        """生成UUID"""
        return str(uuid.uuid4())

    @staticmethod
    def generate_id(prefix: str = "") -> str:
        """生成唯一ID"""
        uid = str(uuid.uuid4()).replace("-", "")
        return f"{prefix}{uid}" if prefix else uid

    @staticmethod
    def hash_string(text: str, algorithm: str = "sha256") -> str:
        """哈希字符串"""
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(text.encode("utf-8"))
        return hash_obj.hexdigest()

    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """截断字符串"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def strip_html(text: str) -> str:
        """去除HTML标签"""
        clean = re.compile(r'<.*?>')
        return re.sub(clean, '', text)

    @staticmethod
    def slugify(text: str, separator: str = "-") -> str:
        """生成URL友好的字符串"""
        text = re.sub(r'[^\w\s-]', '', text.lower())
        return re.sub(r'[-\s]+', separator, text).strip(separator)

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """提取邮箱"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return re.findall(pattern, text)

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """提取URL"""
        pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s<>]*'
        return re.findall(pattern, text)

    @staticmethod
    def mask_email(email: str, show_chars: int = 2) -> str:
        """掩码邮箱"""
        if "@" not in email:
            return email
        name, domain = email.split("@", 1)
        if len(name) <= show_chars:
            return f"{name}***@{domain}"
        return f"{name[:show_chars]}***@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """掩码手机号"""
        if len(phone) != 11:
            return phone
        return f"{phone[:3]}****{phone[-4:]}"

    @staticmethod
    def build_url_params(params: dict) -> str:
        """构建URL参数"""
        return urlencode(params)

    @staticmethod
    def random_string(length: int, chars: str = "abcdefghijklmnopqrstuvwxyz0123456789") -> str:
        """生成随机字符串"""
        import random
        return "".join(random.choice(chars) for _ in range(length))

    @staticmethod
    def capitalize_each_word(text: str) -> str:
        """每个单词首字母大写"""
        return " ".join(word.capitalize() for word in text.split())

    @staticmethod
    def snake_to_camel(text: str) -> str:
        """蛇形转驼峰"""
        words = text.split("_")
        return words[0] + "".join(word.capitalize() for word in words[1:])

    @staticmethod
    def camel_to_snake(text: str) -> str:
        """驼峰转蛇形"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def is_empty(text: Optional[str]) -> bool:
        """判断是否为空"""
        return text is None or not str(text).strip()

    @staticmethod
    def is_not_empty(text: Optional[str]) -> bool:
        """判断是否不为空"""
        return not StringUtils.is_empty(text)

    @staticmethod
    def safe_string(text: Optional[str], default: str = "") -> str:
        """安全字符串转换"""
        if text is None:
            return default
        return str(text)

# 全局字符串工具实例
_string_utils = StringUtils()

def get_string_utils() -> StringUtils:
    """获取字符串工具实例"""
    return _string_utils
