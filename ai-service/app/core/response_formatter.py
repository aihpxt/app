"""响应格式化工具"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime

class ResponseFormatter:
    """响应格式化器"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        status_code: int = 200
    ) -> Dict[str, Any]:
        """成功响应格式"""
        result = {
            "success": True,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }

        if data is not None:
            result["data"] = data

        return result

    @staticmethod
    def error(
        message: str = "操作失败",
        errors: Optional[Dict[str, Any]] = None,
        status_code: int = 400,
        code: Optional[str] = None
    ) -> Dict[str, Any]:
        """错误响应格式"""
        result = {
            "success": False,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }

        if errors:
            result["errors"] = errors

        if code:
            result["code"] = code

        return result

    @staticmethod
    def paginated(
        items: List[Any],
        page: int,
        page_size: int,
        total: int,
        message: str = "获取成功"
    ) -> Dict[str, Any]:
        """分页响应格式"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        return {
            "success": True,
            "message": message,
            "data": {
                "items": items,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            },
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def validation_error(errors: Dict[str, str], message: str = "数据验证失败") -> Dict[str, Any]:
        """验证错误响应"""
        return ResponseFormatter.error(
            message=message,
            errors=errors,
            status_code=422,
            code="VALIDATION_ERROR"
        )

    @staticmethod
    def not_found(resource: str = "资源", message: Optional[str] = None) -> Dict[str, Any]:
        """未找到响应"""
        msg = message or f"{resource}不存在"
        return ResponseFormatter.error(
            message=msg,
            status_code=404,
            code="NOT_FOUND"
        )

    @staticmethod
    def unauthorized(message: str = "未授权访问") -> Dict[str, Any]:
        """未授权响应"""
        return ResponseFormatter.error(
            message=message,
            status_code=401,
            code="UNAUTHORIZED"
        )

    @staticmethod
    def forbidden(message: str = "没有权限") -> Dict[str, Any]:
        """禁止访问响应"""
        return ResponseFormatter.error(
            message=message,
            status_code=403,
            code="FORBIDDEN"
        )

    @staticmethod
    def conflict(message: str = "资源冲突") -> Dict[str, Any]:
        """冲突响应"""
        return ResponseFormatter.error(
            message=message,
            status_code=409,
            code="CONFLICT"
        )

    @staticmethod
    def internal_error(message: str = "服务器内部错误") -> Dict[str, Any]:
        """服务器错误响应"""
        return ResponseFormatter.error(
            message=message,
            status_code=500,
            code="INTERNAL_ERROR"
        )

    @staticmethod
    def created(data: Any = None, message: str = "创建成功") -> Dict[str, Any]:
        """创建成功响应"""
        return ResponseFormatter.success(data=data, message=message, status_code=201)

    @staticmethod
    def accepted(data: Any = None, message: str = "请求已接受") -> Dict[str, Any]:
        """请求已接受响应"""
        return ResponseFormatter.success(data=data, message=message, status_code=202)

# 全局格式化器实例
_formatter = ResponseFormatter()

def get_formatter() -> ResponseFormatter:
    """获取格式化器实例"""
    return _formatter

# 快捷函数
def success_response(data: Any = None, message: str = "操作成功"):
    return _formatter.success(data, message)

def error_response(message: str = "操作失败", errors: Optional[Dict] = None, status_code: int = 400):
    return _formatter.error(message, errors, status_code)

def paginated_response(items: List[Any], page: int, page_size: int, total: int):
    return _formatter.paginated(items, page, page_size, total)
