"""统一异常处理模块"""

import logging
import uuid
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


async def _get_trace_id(request: Request) -> str:
    """从 request.state 获取 trace_id，若无则生成新的"""
    trace_id = getattr(request.state, "trace_id", None)
    if trace_id is None:
        trace_id = str(uuid.uuid4())
    return trace_id


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """处理 AppException 及其子类异常"""
    trace_id = await _get_trace_id(request)

    # exc.detail 已是 {"success": False, "error": {"code": ..., "message": ...}} 格式
    error_body = dict(exc.detail)
    error_body["error"]["trace_id"] = trace_id

    return JSONResponse(
        status_code=exc.status_code,
        content=error_body,
        headers=exc.headers,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理所有未被捕获的异常"""
    trace_id = await _get_trace_id(request)

    logger.error(
        "Unhandled exception occurred | trace_id=%s | path=%s",
        trace_id,
        request.url.path,
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "服务器内部错误，请稍后再试",
                "trace_id": trace_id,
            },
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)