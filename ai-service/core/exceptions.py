from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Union
import traceback

class AppException(Exception):
    def __init__(self, code: int, message: str, data: Union[dict, list, None] = None):
        self.code = code
        self.message = message
        self.data = data

class NotFoundException(AppException):
    def __init__(self, message: str = "资源不存在", data: Union[dict, list, None] = None):
        super().__init__(code=404, message=message, data=data)

class BadRequestException(AppException):
    def __init__(self, message: str = "请求参数错误", data: Union[dict, list, None] = None):
        super().__init__(code=400, message=message, data=data)

class UnauthorizedException(AppException):
    def __init__(self, message: str = "未授权访问", data: Union[dict, list, None] = None):
        super().__init__(code=401, message=message, data=data)

class ForbiddenException(AppException):
    def __init__(self, message: str = "禁止访问", data: Union[dict, list, None] = None):
        super().__init__(code=403, message=message, data=data)

class RateLimitException(AppException):
    def __init__(self, message: str = "请求过于频繁，请稍后再试", data: Union[dict, list, None] = None):
        super().__init__(code=429, message=message, data=data)

class AIServiceException(AppException):
    def __init__(self, message: str = "AI服务异常", data: Union[dict, list, None] = None):
        super().__init__(code=500, message=message, data=data)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.code if exc.code < 500 else 500,
            content={
                "success": False,
                "code": exc.code,
                "message": exc.message,
                "data": exc.data
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"]
            })
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "code": 400,
                "message": "请求参数验证失败",
                "data": {"errors": errors}
            }
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        from core.logger import logger
        logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "code": 500,
                "message": "服务器内部错误" if app.state.settings.is_production else str(exc),
                "data": None
            }
        )
