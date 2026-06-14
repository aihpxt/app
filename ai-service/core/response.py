"""
统一响应模型和错误处理模块
"""

from fastapi import HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, Generic, TypeVar, List

T = TypeVar('T')


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool
    message: str = ""


class DataResponse(BaseResponse, Generic[T]):
    """带数据的响应模型"""
    data: Optional[T] = None


class PaginatedResponse(BaseResponse, Generic[T]):
    """分页响应模型"""
    data: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseResponse):
    """错误响应模型"""
    error_code: int
    error_details: Optional[Dict[str, Any]] = None


class APIError(HTTPException):
    """API错误异常"""
    def __init__(
        self,
        status_code: int,
        error_code: int,
        message: str,
        error_details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.error_details = error_details
        super().__init__(
            status_code=status_code,
            detail={
                "success": False,
                "message": message,
                "error_code": error_code,
                "error_details": error_details
            }
        )


class ErrorCodes:
    """错误代码定义"""
    # 系统错误
    INTERNAL_SERVER_ERROR = 5000
    DATABASE_ERROR = 5001
    CACHE_ERROR = 5002
    
    # 业务错误
    INVALID_PARAMS = 4000
    NOT_FOUND = 4004
    UNAUTHORIZED = 4010
    FORBIDDEN = 4030
    
    # 特定业务错误
    SCHOOL_NOT_FOUND = 4001
    POLICY_NOT_FOUND = 4002
    INVALID_SCORE = 4003
    INVALID_RANK = 4004


def create_success_response(data: Optional[Any] = None, message: str = "操作成功") -> DataResponse:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
    
    Returns:
        DataResponse: 成功响应
    """
    return DataResponse(
        success=True,
        message=message,
        data=data
    )


def create_paginated_response(
    data: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "操作成功"
) -> PaginatedResponse:
    """
    创建分页响应
    
    Args:
        data: 响应数据列表
        total: 总数据量
        page: 当前页码
        page_size: 每页大小
        message: 响应消息
    
    Returns:
        PaginatedResponse: 分页响应
    """
    total_pages = (total + page_size - 1) // page_size
    return PaginatedResponse(
        success=True,
        message=message,
        data=data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


def create_error_response(
    status_code: int,
    error_code: int,
    message: str,
    error_details: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """
    创建错误响应
    
    Args:
        status_code: HTTP状态码
        error_code: 错误代码
        message: 错误消息
        error_details: 错误详情
    
    Returns:
        ErrorResponse: 错误响应
    """
    return ErrorResponse(
        success=False,
        message=message,
        error_code=error_code,
        error_details=error_details
    )


def raise_api_error(
    status_code: int,
    error_code: int,
    message: str,
    error_details: Optional[Dict[str, Any]] = None
) -> None:
    """
    抛出API错误
    
    Args:
        status_code: HTTP状态码
        error_code: 错误代码
        message: 错误消息
        error_details: 错误详情
    """
    raise APIError(
        status_code=status_code,
        error_code=error_code,
        message=message,
        error_details=error_details
    )


def raise_bad_request(
    error_code: int,
    message: str,
    error_details: Optional[Dict[str, Any]] = None
) -> None:
    """
    抛出400错误
    
    Args:
        error_code: 错误代码
        message: 错误消息
        error_details: 错误详情
    """
    raise_api_error(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code=error_code,
        message=message,
        error_details=error_details
    )


def raise_not_found(
    error_code: int,
    message: str,
    error_details: Optional[Dict[str, Any]] = None
) -> None:
    """
    抛出404错误
    
    Args:
        error_code: 错误代码
        message: 错误消息
        error_details: 错误详情
    """
    raise_api_error(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code=error_code,
        message=message,
        error_details=error_details
    )


def raise_internal_error(
    error_code: int,
    message: str,
    error_details: Optional[Dict[str, Any]] = None
) -> None:
    """
    抛出500错误
    
    Args:
        error_code: 错误代码
        message: 错误消息
        error_details: 错误详情
    """
    raise_api_error(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code=error_code,
        message=message,
        error_details=error_details
    )