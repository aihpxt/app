"""Prometheus监控路由"""

from fastapi import APIRouter, Request
from app.core.prometheus_metrics import (
    metrics_collector,
    user_active_count,
    redis_connected,
    db_connections_active,
    db_connections_idle
)

router = APIRouter(prefix="/api/metrics", tags=["监控"])

@router.get("/prometheus")
async def prometheus_metrics():
    """获取Prometheus格式的指标"""
    return metrics_collector.get_metrics()

@router.get("/summary")
async def metrics_summary():
    """获取指标摘要"""
    return {
        "cache_hit_rate": f"{metrics_collector.get_cache_hit_rate() * 100:.2f}%",
        "active_users": user_active_count._value.get(),
        "redis_connected": bool(redis_connected._value.get()),
        "db_active_connections": db_connections_active._value.get(),
        "db_idle_connections": db_connections_idle._value.get()
    }

@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "ai-service",
        "version": "1.0.0"
    }

@router.get("/web-vitals")
async def get_web_vitals():
    """获取Web Vitals指标端点"""
    return {"success": True, "data": {"status": "active"}, "message": "Web Vitals端点已就绪"}

@router.post("/web-vitals")
async def receive_web_vitals(request: "Request"):
    """接收前端Web Vitals指标"""
    import logging
    logger = logging.getLogger(__name__)
    try:
        body = await request.body()
        if body:
            body_str = body.decode('utf-8')
            try:
                import json
                data = json.loads(body_str)
                logger.info(f"Web Vitals: {data}")
            except (json.JSONDecodeError, ValueError):
                logger.info(f"Web Vitals (raw): {body_str[:200]}")
    except Exception as e:
        logger.warning(f"接收 Web Vitals 指标出错: {e}")
    return {"success": True, "message": "指标已接收"}
