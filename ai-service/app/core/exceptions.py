"""错误处理模块"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any

class AppException(HTTPException):
    """应用异常基类"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "success": False,
                "error": {
                    "code": error_code,
                    "message": detail
                }
            },
            headers=headers
        )

class BadRequestException(AppException):
    """400错误：请求参数错误"""
    def __init__(self, detail: str, error_code: str = "BAD_REQUEST"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )

class UnauthorizedException(AppException):
    """401错误：未授权"""
    def __init__(self, detail: str = "未授权", error_code: str = "UNAUTHORIZED"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers={"WWW-Authenticate": "Bearer"}
        )

class ForbiddenException(AppException):
    """403错误：禁止访问"""
    def __init__(self, detail: str = "禁止访问", error_code: str = "FORBIDDEN"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code
        )

class NotFoundException(AppException):
    """404错误：资源不存在"""
    def __init__(self, detail: str = "资源不存在", error_code: str = "NOT_FOUND"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code
        )

class InternalServerErrorException(AppException):
    """500错误：服务器内部错误"""
    def __init__(self, detail: str = "服务器内部错误", error_code: str = "INTERNAL_SERVER_ERROR"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code
        )

class RateLimitExceededException(AppException):
    """429错误：请求过于频繁"""
    def __init__(self, detail: str = "请求过于频繁，请稍后再试", error_code: str = "RATE_LIMIT_EXCEEDED"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code=error_code
        )
