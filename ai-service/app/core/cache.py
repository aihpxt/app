"""缓存模块"""

import time
import hashlib
import json
from typing import Optional, Dict, Any, Callable

class Cache:
    """内存缓存"""
    def __init__(self, maxsize=2000, ttl=3600):
        self.cache = {}
        self.maxsize = maxsize
        self.ttl = ttl
        self.access_times = {}  # 访问时间，用于LRU缓存
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
            "expired": 0
        }
        self.prefix = "cache:"
    
    def generate_key(self, key: str) -> str:
        """生成缓存键"""
        return f"{self.prefix}{hashlib.md5(key.encode()).hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        # 生成缓存键
        cache_key = self.generate_key(key)
        
        # 检查缓存是否存在且未过期
        if cache_key in self.cache:
            value, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.ttl:
                # 更新访问时间
                self.access_times[cache_key] = time.time()
                self.stats["hits"] += 1
                return value
            else:
                # 缓存已过期，删除
                del self.cache[cache_key]
                if cache_key in self.access_times:
                    del self.access_times[cache_key]
                self.stats["expired"] += 1
                self.stats["misses"] += 1
        else:
            self.stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        # 生成缓存键
        cache_key = self.generate_key(key)
        
        # 更新缓存
        if len(self.cache) >= self.maxsize:
            # 移除最久未使用的缓存
            oldest_key = min(self.access_times, key=lambda k: self.access_times.get(k, 0))
            if oldest_key in self.cache:
                del self.cache[oldest_key]
            if oldest_key in self.access_times:
                del self.access_times[oldest_key]
            self.stats["evictions"] += 1
        
        # 保存缓存和访问时间
        actual_ttl = ttl or self.ttl
        self.cache[cache_key] = (value, time.time())
        self.access_times[cache_key] = time.time()
        self.stats["sets"] += 1
    
    def delete(self, key: str) -> None:
        """删除缓存"""
        # 生成缓存键
        cache_key = self.generate_key(key)
        if cache_key in self.cache:
            del self.cache[cache_key]
        if cache_key in self.access_times:
            del self.access_times[cache_key]
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
            "expired": 0
        }
    
    def get_stats(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        return self.stats
    
    def get_hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self.stats["hits"] + self.stats["misses"]
        return self.stats["hits"] / total if total > 0 else 0
    
    def warmup(self, items: Dict[str, Any]) -> None:
        """缓存预热"""
        for key, value in items.items():
            self.set(key, value)

# Redis缓存（可选，需要安装redis库）
try:
    import redis
    import time
    from app.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB
    # 尝试多次连接Redis，提高连接成功率
    max_retries = 3
    retry_delay = 1
    redis_client = None
    for i in range(max_retries):
        try:
            redis_client = redis.Redis(
                host=REDIS_HOST, 
                port=REDIS_PORT, 
                db=REDIS_DB,
                socket_connect_timeout=10,
                socket_timeout=10,
                retry_on_timeout=True,
                health_check_interval=60,
                decode_responses=True
            )
            # 测试Redis连接
            redis_client.ping()
            redis_available = True
            print("Redis缓存可用")
            break
        except Exception as e:
            print(f"Redis连接尝试 {i+1}/{max_retries} 失败: {e}")
            if i < max_retries - 1:
                time.sleep(retry_delay)
            else:
                redis_client = None
                redis_available = False
                print(f"Redis缓存不可用: {e}")
except Exception as e:
    redis_client = None
    redis_available = False
    print(f"Redis缓存不可用: {e}")

class RedisCache:
    """Redis缓存"""
    def __init__(self, ttl=3600):
        self.ttl = ttl
        self.client = redis_client
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0,
            "expired": 0
        }
        self.prefix = "cache:"
        self.max_retries = 3
        self.retry_delay = 0.5
    
    def generate_key(self, key: str) -> str:
        """生成缓存键"""
        return f"{self.prefix}{hashlib.md5(key.encode()).hexdigest()}"
    
    def _retry_operation(self, operation, *args, **kwargs):
        """重试操作"""
        for i in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if i < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise e
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            if not self.client:
                self.stats["misses"] += 1
                return None
            
            def _get_operation():
                cache_key = self.generate_key(key)
                value = self.client.get(cache_key)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        # 旧格式数据，无法安全解析，返回None
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Cache key {cache_key} contains non-JSON data, skipping")
                        return None
                return None
            
            value = self._retry_operation(_get_operation)
            if value:
                self.stats["hits"] += 1
                return value
            else:
                self.stats["misses"] += 1
                return None
        except Exception as e:
            print(f"Redis get error: {e}")
            self.stats["errors"] += 1
            self.stats["misses"] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存"""
        try:
            if not self.client:
                return
            
            def _set_operation():
                cache_key = self.generate_key(key)
                actual_ttl = ttl or self.ttl
                self.client.setex(cache_key, actual_ttl, json.dumps(value))
            
            self._retry_operation(_set_operation)
            self.stats["sets"] += 1
        except Exception as e:
            print(f"Redis set error: {e}")
            self.stats["errors"] += 1
    
    def delete(self, key: str) -> None:
        """删除缓存"""
        try:
            if not self.client:
                return
            
            def _delete_operation():
                cache_key = self.generate_key(key)
                self.client.delete(cache_key)
            
            self._retry_operation(_delete_operation)
        except Exception as e:
            print(f"Redis delete error: {e}")
            self.stats["errors"] += 1
    
    def clear(self) -> None:
        """清空缓存"""
        try:
            if not self.client:
                return
            
            def _clear_operation():
                # 只删除带前缀的键
                keys = self.client.keys(f"{self.prefix}*")
                if keys:
                    self.client.delete(*keys)
                self.stats = {
                    "hits": 0,
                    "misses": 0,
                    "sets": 0,
                    "errors": 0,
                    "expired": 0
                }
            
            self._retry_operation(_clear_operation)
        except Exception as e:
            print(f"Redis clear error: {e}")
            self.stats["errors"] += 1
    
    def get_stats(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        return self.stats
    
    def get_hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self.stats["hits"] + self.stats["misses"]
        return self.stats["hits"] / total if total > 0 else 0
    
    def warmup(self, items: Dict[str, Any]) -> None:
        """缓存预热"""
        for key, value in items.items():
            self.set(key, value)

# 缓存配置
CACHE_TTL = {
    "api": 14400,  # API响应缓存4小时
    "school": 259200,  # 学校信息缓存72小时
    "policy": 259200,  # 政策信息缓存72小时
    "user": 7200,  # 用户信息缓存2小时
    "session": 7200  # 会话信息缓存2小时
}

# 创建全局缓存实例
if redis_available:
    api_cache = RedisCache(ttl=CACHE_TTL["api"])
    school_cache = RedisCache(ttl=CACHE_TTL["school"])
    policy_cache = RedisCache(ttl=CACHE_TTL["policy"])
    user_cache = RedisCache(ttl=CACHE_TTL["user"])
    session_cache = RedisCache(ttl=CACHE_TTL["session"])
    print("使用Redis缓存")
else:
    api_cache = Cache(maxsize=3000, ttl=CACHE_TTL["api"])
    school_cache = Cache(maxsize=1500, ttl=CACHE_TTL["school"])
    policy_cache = Cache(maxsize=1500, ttl=CACHE_TTL["policy"])
    user_cache = Cache(maxsize=1500, ttl=CACHE_TTL["user"])
    session_cache = Cache(maxsize=1500, ttl=CACHE_TTL["session"])
    print("使用内存缓存")

# 缓存预热数据
PRE_WARM_DATA = {
    "school:popular": ["云南大学附属中学", "昆明黄冈实验学校", "昆明市第一中学", "昆明市第三中学", "昆明市第十中学"],
    "policy:latest": ["昆明市2026年初中学校学区划分", "昆明市2026年小升初时间节点", "昆明市2026年中考政策", "昆明市2026年高中录取分数线"],
    "api:health": {"status": "ok", "timestamp": time.time()},
    "api:cache": {"status": "ok", "timestamp": time.time()},
    "api:system": {"status": "ok", "timestamp": time.time()}
}

class SessionCacheManager:
    """会话缓存管理器 - 提供会话数据的高级管理功能"""

    def __init__(self, cache_instance):
        self.cache = cache_instance
        self.active_sessions = {}
        self.session_stats = {
            "total_created": 0,
            "total_updated": 0,
            "total_active": 0,
            "total_expired": 0
        }
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5分钟清理一次过期会话
        self.max_active_sessions = 500

    def get_session(self, session_id: str):
        """获取会话数据，同时更新活跃会话跟踪"""
        key = f"session:{session_id}"
        data = self.cache.get(key)
        if data:
            self.active_sessions[session_id] = time.time()
            self.session_stats["total_updated"] += 1
        return data

    def save_session(self, session_id: str, data: dict, ttl: int = 7200):
        """保存会话数据"""
        key = f"session:{session_id}"
        self.cache.set(key, data, ttl=ttl)
        was_new = session_id not in self.active_sessions  # 正确检查是否是新会话
        self.active_sessions[session_id] = time.time()
        if was_new:
            self.session_stats["total_created"] += 1

    def cleanup_expired_sessions(self):
        """清理过期会话"""
        now = time.time()
        expired = []
        for sid, last_access in list(self.active_sessions.items()):
            if now - last_access > 7200:
                expired.append(sid)

        for sid in expired:
            self.cache.delete(f"session:{sid}")
            del self.active_sessions[sid]
            self.session_stats["total_expired"] += 1

        if len(self.active_sessions) > self.max_active_sessions:
            sorted_sessions = sorted(self.active_sessions.items(), key=lambda x: x[1])
            excess = len(self.active_sessions) - self.max_active_sessions
            for sid, _ in sorted_sessions[:excess]:
                self.cache.delete(f"session:{sid}")
                del self.active_sessions[sid]
                self.session_stats["total_expired"] += 1

        self.last_cleanup = now
        self.session_stats["total_active"] = len(self.active_sessions)

    def warmup_sessions(self, recent_session_ids: list = None):
        """预热会话缓存"""
        if recent_session_ids:
            loaded = 0
            for sid in recent_session_ids:
                key = f"session:{sid}"
                if self.cache.get(key):
                    self.active_sessions[sid] = time.time()
                    loaded += 1
            print(f"会话缓存预热完成，加载了{loaded}个会话")
        else:
            print("会话缓存预热：无历史会话数据，跳过")

    def get_session_stats(self) -> dict:
        """获取会话统计信息"""
        self.cleanup_expired_sessions()
        return {
            **self.session_stats,
            "total_active": len(self.active_sessions),
            "cache_hit_rate": self.cache.get_hit_rate() if hasattr(self.cache, 'get_hit_rate') else 0
        }

    def get_recent_active_sessions(self, count: int = 10) -> list:
        """获取最近活跃的会话ID列表"""
        sorted_sessions = sorted(self.active_sessions.items(), key=lambda x: x[1], reverse=True)
        return [sid for sid, _ in sorted_sessions[:count]]

session_cache_manager = SessionCacheManager(session_cache)

def warmup_cache():
    """执行缓存预热"""
    for key, value in PRE_WARM_DATA.items():
        if key.startswith("school:"):
            school_cache.set(key, value)
        elif key.startswith("policy:"):
            policy_cache.set(key, value)
        else:
            api_cache.set(key, value)

    session_cache_manager.warmup_sessions()
    print("缓存预热完成")

warmup_cache()

