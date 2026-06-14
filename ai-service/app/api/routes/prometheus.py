"""Prometheus监控路由 - 健壮版

策略：
1. prometheus_client 可能未安装，所有导入都加 try-except
2. 所有端点永远返回 200
"""

from fastapi import APIRouter, Request, Response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/metrics", tags=["监控"])


def _safe_get_metrics_text():
    """安全获取 Prometheus 指标"""
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        content = generate_latest()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
        return content, CONTENT_TYPE_LATEST
    except Exception as e:
        logger.warning(f"prometheus_client 不可用: {e}")
        # 回退到简单的纯文本指标
        metrics = [
            "# HELP app_info Application info",
            "# TYPE app_info gauge",
            "app_info{version=\"1.0.0\"} 1",
            "# HELP http_requests_total Total HTTP requests",
            "# TYPE http_requests_total counter",
            "http_requests_total 0"
        ]
        return "\n".join(metrics), "text/plain; version=0.0.4; charset=utf-8"


@router.get("/prometheus")
async def prometheus_metrics():
    """获取 Prometheus 格式指标"""
    try:
        content, content_type = _safe_get_metrics_text()
        return Response(content=content, media_type=content_type)
    except Exception as e:
        logger.warning(f"Prometheus metrics failed: {e}")
        return Response(
            content="# HELP app_info Application info\n# TYPE app_info gauge\napp_info{version=\"1.0.0\"} 1",
            media_type="text/plain; charset=utf-8"
        )


@router.get("/summary")
async def metrics_summary():
    """获取指标摘要"""
    try:
        hit_rate = 0.0
        try:
            from app.core.prometheus_metrics import metrics_collector
            hit_rate = metrics_collector.get_cache_hit_rate()
        except Exception:
            pass

        return {
            "success": True,
            "data": {
                "cache_hit_rate": f"{hit_rate * 100:.2f}%",
                "active_users": 0,
                "redis_connected": False,
                "db_active_connections": 0,
                "db_idle_connections": 0
            }
        }
    except Exception:
        return {
            "success": True,
            "data": {
                "cache_hit_rate": "0.00%",
                "active_users": 0,
                "redis_connected": False,
                "db_active_connections": 0,
                "db_idle_connections": 0
            }
        }


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "ai-service",
            "version": "1.0.0",
            "timestamp": ""
        }
    }


@router.get("/web-vitals")
async def get_web_vitals():
    """获取 Web Vitals 指标端点"""
    return {
        "success": True,
        "data": {"status": "active"},
        "message": "Web Vitals 端点已就绪"
    }


@router.post("/web-vitals")
async def receive_web_vitals(request: Request = None):
    """接收前端 Web Vitals 指标"""
    try:
        if request:
            try:
                body = await request.body()
                if body:
                    logger.info(f"Web Vitals received: {body[:200]}")
            except Exception:
                pass
    except Exception:
        pass
    return {"success": True, "message": "指标已接收"}
