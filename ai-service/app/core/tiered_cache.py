"""
多级缓存管理器
实现L1本地缓存 + L2 Redis分布式缓存的分层架构
"""

import time
import hashlib
import json
import logging
from typing import Optional, Dict, Any, List
from collections import OrderedDict
import threading

logger = logging.getLogger(__name__)

class L1Cache:
    """L1本地缓存 - 基于LRU策略的高速内存缓存"""

    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl
        self._cache = OrderedDict()  # LRU缓存
        self._timestamps = {}
        self._lock = threading.RLock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
            "expired": 0
        }

    def _generate_key(self, key: str) -> str:
        """生成缓存键"""
        return f"l1:{hashlib.md5(str(key).encode()).hexdigest()}"

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        cache_key = self._generate_key(key)

        with self._lock:
            if cache_key in self._cache:
                value, timestamp = self._cache[cache_key]

                # 检查是否过期
                if time.time() - timestamp < self.ttl:
                    # 移动到末尾（LRU）
                    self._cache.move_to_end(cache_key)
                    self._timestamps[cache_key] = time.time()
                    self.stats["hits"] += 1
                    return value
                else:
                    # 已过期，删除
                    del self._cache[cache_key]
                    del self._timestamps[cache_key]
                    self.stats["expired"] += 1
                    self.stats["misses"] += 1
            else:
                self.stats["misses"] += 1

            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        cache_key = self._generate_key(key)
        actual_ttl = ttl or self.ttl

        with self._lock:
            # 如果缓存已存在，更新值
            if cache_key in self._cache:
                self._cache[cache_key] = (value, time.time())
                self._cache.move_to_end(cache_key)
            else:
                # 如果缓存已满，移除最久未使用的
                if len(self._cache) >= self.max_size:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                    if oldest_key in self._timestamps:
                        del self._timestamps[oldest_key]
                    self.stats["evictions"] += 1

                # 添加新缓存
                self._cache[cache_key] = (value, time.time())
                self._timestamps[cache_key] = time.time()

            self.stats["sets"] += 1

    def delete(self, key: str) -> None:
        """删除缓存"""
        cache_key = self._generate_key(key)

        with self._lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
            if cache_key in self._timestamps:
                del self._timestamps[cache_key]

    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self.stats = {
                "hits": 0,
                "misses": 0,
                "sets": 0,
                "evictions": 0,
                "expired": 0
            }

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total if total > 0 else 0

        return {
            **self.stats,
            "hit_rate": hit_rate,
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl": self.ttl
        }


class TieredCacheManager:
    """多级缓存管理器 - 协调L1和L2缓存"""

    def __init__(self, l1_size: int = 1000, l1_ttl: int = 300, l2_ttl: int = 3600):
        self.l1_cache = L1Cache(max_size=l1_size, ttl=l1_ttl)
        self.l2_cache = None  # Redis缓存将在初始化时设置
        self.l2_ttl = l2_ttl
        self.redis_client = None
        self.redis_available = False
        self._init_redis()

        self.stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "total_requests": 0
        }

        logger.info(f"多级缓存管理器初始化完成: L1={l1_size}, L1_TTL={l1_ttl}s, L2_TTL={l2_ttl}s")

    def _init_redis(self):
        """初始化Redis连接"""
        try:
            import redis
            from app.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB

            max_retries = 3
            for i in range(max_retries):
                try:
                    self.redis_client = redis.Redis(
                        host=REDIS_HOST,
                        port=REDIS_PORT,
                        db=REDIS_DB,
                        socket_connect_timeout=5,
                        socket_timeout=5,
                        retry_on_timeout=True,
                        decode_responses=True
                    )
                    self.redis_client.ping()
                    self.redis_available = True
                    self.l2_cache = self.redis_client
                    logger.info("Redis缓存连接成功")
                    break
                except Exception as e:
                    if i < max_retries - 1:
                        time.sleep(1)
                    else:
                        logger.warning(f"Redis缓存不可用: {e}")
                        self.redis_available = False

        except ImportError:
            logger.warning("Redis库未安装")
            self.redis_available = False

    def get(self, key: str) -> Optional[Any]:
        """获取缓存 - L1 -> L2 -> None"""
        self.stats["total_requests"] += 1

        # 1. 先查询L1缓存
        value = self.l1_cache.get(key)
        if value is not None:
            self.stats["l1_hits"] += 1
            return value

        # 2. L1未命中，查询L2缓存
        if self.redis_available and self.l2_cache:
            try:
                cache_key = f"l2:{hashlib.md5(str(key).encode()).hexdigest()}"
                value = self.l2_cache.get(cache_key)

                if value is not None:
                    self.stats["l2_hits"] += 1
                    # 回填到L1缓存
                    self.l1_cache.set(key, value)
                    return value

            except Exception as e:
                logger.error(f"L2缓存读取失败: {e}")

        # 3. L2也未命中
        self.stats["misses"] += 1
        return None

    def set(self, key: str, value: Any, l1_ttl: Optional[int] = None, l2_ttl: Optional[int] = None) -> None:
        """设置缓存 - 同时写入L1和L2"""
        # 写入L1缓存
        self.l1_cache.set(key, value, l1_ttl)

        # 写入L2缓存
        if self.redis_available and self.l2_cache:
            try:
                cache_key = f"l2:{hashlib.md5(str(key).encode()).hexdigest()}"
                actual_ttl = l2_ttl or self.l2_ttl
                self.l2_cache.setex(cache_key, actual_ttl, json.dumps(value))
            except Exception as e:
                logger.error(f"L2缓存写入失败: {e}")

    def delete(self, key: str) -> None:
        """删除缓存 - 同时删除L1和L2"""
        self.l1_cache.delete(key)

        if self.redis_available and self.l2_cache:
            try:
                cache_key = f"l2:{hashlib.md5(str(key).encode()).hexdigest()}"
                self.l2_cache.delete(cache_key)
            except Exception as e:
                logger.error(f"L2缓存删除失败: {e}")

    def clear(self) -> None:
        """清空所有缓存"""
        self.l1_cache.clear()

        if self.redis_available and self.l2_cache:
            try:
                # 只清除l2:前缀的键
                keys = self.l2_cache.keys("l2:*")
                if keys:
                    self.l2_cache.delete(*keys)
            except Exception as e:
                logger.error(f"L2缓存清空失败: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        l1_stats = self.l1_cache.get_stats()

        total = self.stats["total_requests"]
        if total > 0:
            overall_hit_rate = (self.stats["l1_hits"] + self.stats["l2_hits"]) / total
            l1_hit_rate = self.stats["l1_hits"] / total
            l2_hit_rate = self.stats["l2_hits"] / total
        else:
            overall_hit_rate = l1_hit_rate = l2_hit_rate = 0

        return {
            "total_requests": total,
            "l1_hits": self.stats["l1_hits"],
            "l2_hits": self.stats["l2_hits"],
            "misses": self.stats["misses"],
            "overall_hit_rate": round(overall_hit_rate * 100, 2),
            "l1_hit_rate": round(l1_hit_rate * 100, 2),
            "l2_hit_rate": round(l2_hit_rate * 100, 2),
            "l1_cache": l1_stats,
            "redis_available": self.redis_available
        }


class CacheWarmupManager:
    """缓存预热管理器"""

    def __init__(self, tiered_cache: TieredCacheManager):
        self.cache = tiered_cache
        self.warmup_history = []
        self._lock = threading.Lock()

    def warmup_hot_data(self, data_loader: callable, keys: List[str]) -> Dict[str, Any]:
        """预热热门数据"""
        start_time = time.time()
        success_count = 0
        fail_count = 0
        failed_keys = []

        for key in keys:
            try:
                # 从数据源加载数据
                value = data_loader(key)

                if value is not None:
                    # 写入缓存
                    self.cache.set(key, value)
                    success_count += 1
                else:
                    fail_count += 1
                    failed_keys.append(key)

            except Exception as e:
                logger.error(f"预热失败 {key}: {e}")
                fail_count += 1
                failed_keys.append(key)

        elapsed_time = time.time() - start_time

        result = {
            "total_keys": len(keys),
            "success_count": success_count,
            "fail_count": fail_count,
            "failed_keys": failed_keys,
            "elapsed_time": round(elapsed_time, 2)
        }

        with self._lock:
            self.warmup_history.append({
                "timestamp": datetime.now().isoformat(),
                **result
            })

        logger.info(f"缓存预热完成: 成功{success_count}/{len(keys)}, 耗时{elapsed_time:.2f}s")
        return result


class CacheMonitor:
    """缓存监控器"""

    def __init__(self, tiered_cache: TieredCacheManager):
        self.cache = tiered_cache
        self.alert_thresholds = {
            "hit_rate_low": 50.0,  # 命中率低于50%告警
            "miss_rate_high": 30.0,  # 未命中率高于30%告警
            "l1_full": 90.0  # L1缓存使用率高于90%告警
        }
        self.alerts = []

    def check_health(self) -> Dict[str, Any]:
        """检查缓存健康状态"""
        stats = self.cache.get_stats()

        alerts = []
        warnings = []

        # 检查整体命中率
        if stats["overall_hit_rate"] < self.alert_thresholds["hit_rate_low"]:
            alerts.append(f"缓存命中率过低: {stats['overall_hit_rate']}%")

        # 检查未命中率
        miss_rate = (stats["misses"] / stats["total_requests"] * 100) if stats["total_requests"] > 0 else 0
        if miss_rate > self.alert_thresholds["miss_rate_high"]:
            warnings.append(f"缓存未命中率较高: {miss_rate:.2f}%")

        # 检查L1缓存使用率
        l1_usage = (stats["l1_cache"]["size"] / stats["l1_cache"]["max_size"] * 100) if stats["l1_cache"]["max_size"] > 0 else 0
        if l1_usage > self.alert_thresholds["l1_full"]:
            warnings.append(f"L1缓存使用率较高: {l1_usage:.2f}%")

        return {
            "status": "healthy" if not alerts else "unhealthy",
            "alerts": alerts,
            "warnings": warnings,
            "metrics": stats
        }

    def get_recommendations(self) -> List[str]:
        """获取优化建议"""
        stats = self.cache.get_stats()
        recommendations = []

        # 基于命中率建议
        if stats["overall_hit_rate"] < 70:
            recommendations.append("考虑增加缓存容量或延长TTL")
            recommendations.append("检查数据访问模式，优化缓存键设计")

        # 基于L1命中率建议
        if stats["l1_hit_rate"] < 50:
            recommendations.append("L1缓存命中率较低，考虑增大L1缓存容量")

        # 基于Redis可用性建议
        if not stats["redis_available"]:
            recommendations.append("Redis不可用，建议检查Redis服务状态")

        return recommendations


from datetime import datetime

# 全局缓存管理器实例
_tiered_cache_manager = None
_cache_warmup_manager = None
_cache_monitor = None


def get_tiered_cache_manager() -> TieredCacheManager:
    """获取多级缓存管理器实例"""
    global _tiered_cache_manager
    if _tiered_cache_manager is None:
        from app.core.optimization_config import MemoryOptimizationConfig
        config = MemoryOptimizationConfig()
        _tiered_cache_manager = TieredCacheManager(
            l1_size=config.CACHE_MAX_SIZE,
            l1_ttl=300,  # 5分钟
            l2_ttl=config.CACHE_TTL
        )
    return _tiered_cache_manager


def get_cache_warmup_manager() -> CacheWarmupManager:
    """获取缓存预热管理器实例"""
    global _cache_warmup_manager
    if _cache_warmup_manager is None:
        _cache_warmup_manager = CacheWarmupManager(get_tiered_cache_manager())
    return _cache_warmup_manager


def get_cache_monitor() -> CacheMonitor:
    """获取缓存监控器实例"""
    global _cache_monitor
    if _cache_monitor is None:
        _cache_monitor = CacheMonitor(get_tiered_cache_manager())
    return _cache_monitor
