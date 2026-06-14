"""工具API路由"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.core.validator import get_validator
from app.core.response_formatter import get_formatter
from app.core.time_utils import get_time_utils
from app.core.string_utils import get_string_utils

router = APIRouter(prefix="/api/utils", tags=["工具"])

# 验证器
validator = get_validator()
formatter = get_formatter()
time_utils = get_time_utils()
string_utils = get_string_utils()

# 请求模型
class EmailValidationRequest(BaseModel):
    email: str

class PhoneValidationRequest(BaseModel):
    phone: str

class PasswordValidationRequest(BaseModel):
    password: str
    min_length: int = 8

class TextSanitizeRequest(BaseModel):
    text: str
    max_length: int = 500

# 邮箱验证端点
@router.post("/validate/email")
async def validate_email(request: EmailValidationRequest):
    """验证邮箱格式"""
    is_valid = validator.is_valid_email(request.email)
    return formatter.success(
        data={
            "valid": is_valid,
            "email": request.email,
            "masked": string_utils.mask_email(request.email)
        },
        message="邮箱验证完成"
    )

# 手机号验证端点
@router.post("/validate/phone")
async def validate_phone(request: PhoneValidationRequest):
    """验证手机号格式"""
    is_valid = validator.is_valid_phone(request.phone)
    return formatter.success(
        data={
            "valid": is_valid,
            "phone": request.phone,
            "masked": string_utils.mask_phone(request.phone)
        },
        message="手机号验证完成"
    )

# 密码强度验证端点
@router.post("/validate/password")
async def validate_password(request: PasswordValidationRequest):
    """验证密码强度"""
    result = validator.is_valid_password(request.password, request.min_length)
    return formatter.success(
        data=result,
        message="密码强度验证完成"
    )

# 文本清理端点
@router.post("/sanitize/text")
async def sanitize_text(request: TextSanitizeRequest):
    """清理文本"""
    cleaned = validator.sanitize_string(request.text, request.max_length)
    return formatter.success(
        data={
            "original": request.text,
            "sanitized": cleaned,
            "length": len(cleaned)
        },
        message="文本清理完成"
    )

# 时间工具端点
@router.get("/time/current")
async def get_current_time():
    """获取当前时间"""
    now = time_utils.get_current_time()
    return formatter.success(
        data={
            "datetime": time_utils.format_datetime(now),
            "timestamp": time_utils.get_timestamp(),
            "date": time_utils.format_datetime(now, "%Y-%m-%d"),
            "time": time_utils.format_datetime(now, "%H:%M:%S")
        },
        message="获取当前时间成功"
    )

@router.get("/time/relative")
async def get_relative_time(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0
):
    """获取相对时间"""
    try:
        from datetime import datetime
        dt = datetime(year, month, day, hour, minute, second)
        return formatter.success(
            data={
                "datetime": time_utils.format_datetime(dt),
                "relative": time_utils.get_relative_time(dt),
                "is_today": time_utils.is_today(dt),
                "is_this_week": time_utils.is_this_week(dt),
                "is_this_month": time_utils.is_this_month(dt)
            },
            message="相对时间计算成功"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 字符串工具端点
@router.get("/string/uuid")
async def generate_uuid():
    """生成UUID"""
    return formatter.success(
        data={
            "uuid": string_utils.generate_uuid(),
            "short_id": string_utils.generate_id()
        },
        message="UUID生成成功"
    )

@router.get("/string/hash")
async def hash_string(
    text: str,
    algorithm: str = Query("sha256", description="哈希算法")
):
    """哈希字符串"""
    return formatter.success(
        data={
            "original": text,
            "hash": string_utils.hash_string(text, algorithm),
            "algorithm": algorithm
        },
        message="哈希完成"
    )

@router.get("/string/truncate")
async def truncate_string(
    text: str,
    max_length: int = Query(50, description="最大长度"),
    suffix: str = Query("...", description="省略符号")
):
    """截断字符串"""
    return formatter.success(
        data={
            "original": text,
            "truncated": string_utils.truncate(text, max_length, suffix),
            "original_length": len(text),
            "truncated_length": len(string_utils.truncate(text, max_length, suffix))
        },
        message="字符串截断完成"
    )

@router.get("/string/slugify")
async def slugify_string(text: str):
    """生成URL友好的字符串"""
    return formatter.success(
        data={
            "original": text,
            "slug": string_utils.slugify(text)
        },
        message="URL化完成"
    )

@router.get("/extract/emails")
async def extract_emails(text: str):
    """提取文本中的邮箱"""
    emails = string_utils.extract_emails(text)
    return formatter.success(
        data={
            "count": len(emails),
            "emails": emails
        },
        message="邮箱提取完成"
    )

@router.get("/extract/urls")
async def extract_urls(text: str):
    """提取文本中的URL"""
    urls = string_utils.extract_urls(text)
    return formatter.success(
        data={
            "count": len(urls),
            "urls": urls
        },
        message="URL提取完成"
    )

# 工具使用说明
@router.get("/")
async def get_tools_info():
    """获取所有工具信息"""
    return formatter.success(
        data={
            "validation": [
                "POST /api/utils/validate/email - 验证邮箱",
                "POST /api/utils/validate/phone - 验证手机号",
                "POST /api/utils/validate/password - 验证密码强度",
                "POST /api/utils/sanitize/text - 清理文本"
            ],
            "time": [
                "GET /api/utils/time/current - 获取当前时间",
                "GET /api/utils/time/relative - 获取相对时间"
            ],
            "string": [
                "GET /api/utils/string/uuid - 生成UUID",
                "GET /api/utils/string/hash - 哈希字符串",
                "GET /api/utils/string/truncate - 截断字符串",
                "GET /api/utils/string/slugify - URL化字符串",
                "GET /api/utils/extract/emails - 提取邮箱",
                "GET /api/utils/extract/urls - 提取URL"
            ]
        },
        message="工具API信息"
    )
