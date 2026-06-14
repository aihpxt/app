"""Prometheus监控中间件"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.prometheus_metrics import (
    metrics_collector,
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress
)
import time

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Prometheus监控中间件"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/api/metrics/prometheus":
            return await call_next(request)

        method = request.method
        path = request.url.path

        http_requests_in_progress.labels(method=method, endpoint=path).inc()

        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code

        except Exception as e:
            status_code = 500
            raise

        finally:
            duration = time.time() - start_time
            metrics_collector.record_request(method, path, status_code, duration)
            http_requests_in_progress.labels(method=method, endpoint=path).dec()

        return response
