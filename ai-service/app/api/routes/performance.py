"""性能监控路由"""

from fastapi import APIRouter
from app.core.monitoring import get_system_monitor
from app.core.cache import api_cache
from app.core.cache_optimizer import get_cache_optimizer
import time

router = APIRouter(prefix="/api/performance", tags=["性能监控"])

@router.get("/")
async def get_performance_metrics():
    """获取性能指标"""
    system_monitor = get_system_monitor()
    metrics = system_monitor.get_system_metrics()

    cache_optimizer = get_cache_optimizer()

    return {
        "success": True,
        "data": {
            "system": {
                "cpu": metrics["cpu"],
                "memory": metrics["memory"],
                "disk": metrics["disk"],
                "uptime": metrics.get("uptime", 0)
            },
            "cache": cache_optimizer.get_stats(),
            "response_time": {
                "unit": "ms",
                "timestamp": time.time()
            }
        }
    }

@router.get("/cache/stats")
async def get_cache_statistics():
    """获取缓存统计"""
    cache_optimizer = get_cache_optimizer()

    # 获取Redis缓存信息
    redis_info = {}
    try:
        if hasattr(api_cache, 'client') and api_cache.client:
            redis_info = api_cache.client.info()
    except:
        pass

    return {
        "success": True,
        "data": {
            "optimizer_stats": cache_optimizer.get_stats(),
            "redis_info": {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory_human": redis_info.get("used_memory_human", "N/A"),
                "total_connections_received": redis_info.get("total_connections_received", 0),
                "keyspace_hits": redis_info.get("keyspace_hits", 0),
                "keyspace_misses": redis_info.get("keyspace_misses", 0)
            } if redis_info else {}
        }
    }

@router.get("/database/stats")
async def get_database_statistics():
    """获取数据库统计"""
    try:
        from app.core.database_pool import get_db_manager
        db_manager = get_db_manager()

        # 获取连接池状态
        pool_status = {
            "pool_size": db_manager.engine.pool.size() if hasattr(db_manager.engine.pool, 'size') else "N/A",
            "checked_in": db_manager.engine.pool.checkedin() if hasattr(db_manager.engine.pool, 'checkedin') else "N/A",
            "checked_out": db_manager.engine.pool.checkedout() if hasattr(db_manager.engine.pool, 'checkedout') else "N/A",
            "overflow": db_manager.engine.pool.overflow() if hasattr(db_manager.engine.pool, 'overflow') else "N/A"
        }

        return {
            "success": True,
            "data": pool_status
        }
    except Exception as e:
        return {
            "success": True,
            "data": {
                "status": "unavailable",
                "error": str(e)
            }
        }

@router.get("/recommendations")
async def get_performance_recommendations():
    """获取性能优化建议"""
    system_monitor = get_system_monitor()
    metrics = system_monitor.get_system_metrics()

    recommendations = []

    # CPU建议
    if metrics["cpu"]["percent"] > 70:
        recommendations.append({
            "category": "CPU",
            "level": "warning",
            "message": "CPU使用率较高，建议优化计算密集型操作"
        })

    # 内存建议
    if metrics["memory"]["percent"] > 80:
        recommendations.append({
            "category": "Memory",
            "level": "warning",
            "message": "内存使用率较高，建议检查内存泄漏或增加内存"
        })

    # 磁盘建议
    if metrics["disk"]["percent"] > 85:
        recommendations.append({
            "category": "Disk",
            "level": "error",
            "message": "磁盘空间不足，建议清理日志或增加磁盘"
        })

    # 缓存建议
    cache_optimizer = get_cache_optimizer()
    hit_rate = cache_optimizer.calculate_hit_rate()
    if hit_rate < 0.5:
        recommendations.append({
            "category": "Cache",
            "level": "info",
            "message": f"缓存命中率较低({hit_rate*100:.1f}%)，建议优化缓存策略"
        })

    return {
        "success": True,
        "data": {
            "recommendations_count": len(recommendations),
            "recommendations": recommendations
        }
    }
