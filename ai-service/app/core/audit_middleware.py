"""审计日志中间件"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.audit_logger import audit_logger, AuditAction, AuditLevel
import time
import json

class AuditMiddleware(BaseHTTPMiddleware):
    """审计中间件 - 记录所有API请求"""

    def __init__(self, app: ASGIApp, excluded_paths: list = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/metrics"
        ]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return await call_next(request)

        start_time = time.time()

        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        method = request.method
        path = request.url.path
        query_params = str(request.query_params)

        try:
            response = await call_next(request)

            duration = time.time() - start_time
            status_code = response.status_code

            action = self._get_action_from_method(method)
            level = self._get_level_from_status(status_code)

            audit_logger.log(
                action=action,
                level=level,
                resource=path,
                details={
                    "method": method,
                    "query_params": query_params,
                    "status_code": status_code,
                    "duration": round(duration, 3)
                },
                ip_address=client_ip,
                user_agent=user_agent,
                status="SUCCESS" if status_code < 400 else "FAILURE"
            )

            return response

        except Exception as e:
            duration = time.time() - start_time

            audit_logger.log(
                action=AuditAction.SECURITY_EVENT,
                level=AuditLevel.ERROR,
                resource=path,
                details={
                    "method": method,
                    "query_params": query_params,
                    "error": str(e),
                    "duration": round(duration, 3)
                },
                ip_address=client_ip,
                user_agent=user_agent,
                status="ERROR"
            )
            raise

    def _get_action_from_method(self, method: str) -> AuditAction:
        """根据HTTP方法获取操作类型"""
        method_map = {
            "GET": AuditAction.API_ACCESS,
            "POST": AuditAction.DATA_CREATE,
            "PUT": AuditAction.DATA_UPDATE,
            "PATCH": AuditAction.DATA_UPDATE,
            "DELETE": AuditAction.DATA_DELETE
        }
        return method_map.get(method, AuditAction.API_ACCESS)

    def _get_level_from_status(self, status_code: int) -> AuditLevel:
        """根据状态码获取日志级别"""
        if status_code >= 500:
            return AuditLevel.ERROR
        elif status_code >= 400:
            return AuditLevel.WARNING
        return AuditLevel.INFO
