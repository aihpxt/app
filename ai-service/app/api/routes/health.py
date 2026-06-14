#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查路由 - Liveness / Readiness / Dependency probes
"""

import time
from datetime import datetime, timezone
from fastapi import APIRouter, Response
from app.core.database_pool import get_db_manager
from app.core.cache import redis_available, api_cache

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """简单健康检查端点"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "ai-service",
            "version": "1.0.0"
        },
        "message": "服务运行正常"
    }

def _format_timestamp():
    return datetime.now(timezone.utc).isoformat()

def _check_database():
    """检查数据库连接状态"""
    try:
        start = time.perf_counter()
        db_manager = get_db_manager()
        session = db_manager.get_session()
        session.execute("SELECT 1")
        session.close()
        latency = (time.perf_counter() - start) * 1000
        return "ok", round(latency, 2)
    except Exception as e:
        return "error", str(e)

def _check_cache():
    """检查缓存状态"""
    try:
        cache_type = "redis" if redis_available else "memory"
        test_val = api_cache.get("health_check")
        return "ok", cache_type
    except Exception as e:
        return "error", str(e)

def _check_deepseek():
    """检查 DeepSeek API 连通性（可选）"""
    try:
        from app.core.config import DEEPSEEK_CONFIG
        api_key = DEEPSEEK_CONFIG.get("api_key", "")
        if not api_key:
            return "degraded", "API key not configured"
        return "ok", "configured"
    except Exception as e:
        return "error", str(e)


@router.get("/health/live")
async def health_live():
    """存活探针：进程存活即返回 OK"""
    return {"status": "ok", "timestamp": _format_timestamp()}


@router.get("/health/ready")
async def health_ready(response: Response):
    """就绪探针：检查数据库 + 缓存，任一不可用返回 503"""
    db_status, db_detail = _check_database()
    cache_status, cache_detail = _check_cache()
    
    deps = {
        "database": db_status,
        "cache": cache_status,
    }
    
    healthy = db_status == "ok" and cache_status == "ok"
    
    if not healthy:
        response.status_code = 503
    
    result = {"status": "healthy" if healthy else "unhealthy", "dependencies": deps, "timestamp": _format_timestamp()}
    if not healthy:
        result["details"] = {"database": db_detail, "cache": cache_detail}
    
    return result


@router.get("/health/deps")
async def health_deps():
    """详细依赖检查：数据库、缓存、DeepSeek API"""
    db_status, db_latency = _check_database()
    cache_status, cache_type = _check_cache()
    ds_status, ds_detail = _check_deepseek()
    
    return {
        "dependencies": {
            "database": {"status": db_status, "latency_ms": db_latency},
            "cache": {"status": cache_status, "type": cache_type},
            "deepseek": {"status": ds_status, "detail": ds_detail}
        },
        "timestamp": _format_timestamp()
    }