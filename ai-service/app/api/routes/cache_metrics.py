"""
缓存统计API路由
提供缓存监控、统计和预热功能
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/cache", tags=["缓存管理"])


class WarmupRequest(BaseModel):
    """预热请求模型"""
    keys: List[str]
    data_source: str = "default"


@router.get("/stats")
async def get_cache_stats():
    """
    获取缓存统计信息

    返回:
        - 总体统计（命中率、未命中率等）
        - L1缓存统计
        - Redis可用性
    """
    try:
        from app.core.tiered_cache import get_tiered_cache_manager

        cache_manager = get_tiered_cache_manager()
        stats = cache_manager.get_stats()

        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")


@router.get("/health")
async def get_cache_health():
    """
    获取缓存健康状态

    返回:
        - 健康状态
        - 告警信息
        - 警告信息
    """
    try:
        from app.core.tiered_cache import get_cache_monitor

        monitor = get_cache_monitor()
        health = monitor.check_health()

        return {
            "success": True,
            "data": health
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存健康状态失败: {str(e)}")


@router.get("/recommendations")
async def get_cache_recommendations():
    """
    获取缓存优化建议

    返回:
        - 优化建议列表
    """
    try:
        from app.core.tiered_cache import get_cache_monitor

        monitor = get_cache_monitor()
        recommendations = monitor.get_recommendations()

        return {
            "success": True,
            "data": {
                "recommendations": recommendations
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取优化建议失败: {str(e)}")


@router.post("/warmup")
async def warmup_cache(request: WarmupRequest):
    """
    触发缓存预热

    请求体:
        - keys: 需要预热的键列表
        - data_source: 数据源标识

    返回:
        - 预热结果统计
    """
    try:
        from app.core.tiered_cache import get_cache_warmup_manager
        from app.core.tiered_cache import get_tiered_cache_manager

        warmup_manager = get_cache_warmup_manager()
        cache_manager = get_tiered_cache_manager()

        # 根据数据源创建数据加载器
        def data_loader(key: str):
            # 这里应该根据实际业务逻辑加载数据
            # 暂时返回None，实际使用时需要实现具体逻辑
            return None

        # 执行预热
        result = warmup_manager.warmup_hot_data(data_loader, request.keys)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"缓存预热失败: {str(e)}")


@router.post("/clear")
async def clear_cache():
    """
    清空所有缓存

    返回:
        - 操作结果
    """
    try:
        from app.core.tiered_cache import get_tiered_cache_manager

        cache_manager = get_tiered_cache_manager()
        cache_manager.clear()

        return {
            "success": True,
            "message": "缓存已清空"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")


@router.delete("/{key}")
async def delete_cache_key(key: str):
    """
    删除指定缓存键

    参数:
        key: 缓存键

    返回:
        - 操作结果
    """
    try:
        from app.core.tiered_cache import get_tiered_cache_manager

        cache_manager = get_tiered_cache_manager()
        cache_manager.delete(key)

        return {
            "success": True,
            "message": f"缓存键 '{key}' 已删除"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除缓存键失败: {str(e)}")


@router.get("/report")
async def get_cache_report():
    """
    获取缓存性能报告

    返回:
        - 详细统计信息
        - 健康状态
        - 优化建议
    """
    try:
        from app.core.tiered_cache import (
            get_tiered_cache_manager,
            get_cache_monitor
        )

        cache_manager = get_tiered_cache_manager()
        monitor = get_cache_monitor()

        stats = cache_manager.get_stats()
        health = monitor.check_health()
        recommendations = monitor.get_recommendations()

        return {
            "success": True,
            "data": {
                "statistics": stats,
                "health": health,
                "recommendations": recommendations
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存报告失败: {str(e)}")
