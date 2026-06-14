"""缓存优化配置 - 增强版"""

import os
import json
import time
import hashlib
from typing import Any, Optional, Callable, Dict, List
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta

class AccessPatternDetector:
    """访问模式检测器"""
    
    def __init__(self):
        # 记录每个缓存键的访问时间
        self._access_times: Dict[str, List[float]] = {}
        # 记录访问频率（每分钟）
        self._frequency_buckets: Dict[str, int] = {}
        # 热点缓存键
        self._hot_keys: List[str] = []
        # 冷缓存键
        self._cold_keys: List[str] = []
        # 检测周期（秒）
        self._detection_period = 300
        # 上次检测时间
        self._last_detection = time.time()
        
    def record_access(self, key: str):
        """记录缓存访问"""
        now = time.time()
        if key not in self._access_times:
            self._access_times[key] = []
        self._access_times[key].append(now)
        
        # 清理过期的访问记录（保留最近1小时）
        cutoff = now - 3600
        self._access_times[key] = [t for t in self._access_times[key] if t >= cutoff]
        
        # 更新频率桶
        minute_key = int(now / 60)
        freq_key = f"{key}:{minute_key}"
        self._frequency_buckets[freq_key] = self._frequency_buckets.get(freq_key, 0) + 1
        
        # 定时检测访问模式
        if now - self._last_detection >= self._detection_period:
            self._detect_patterns()
            self._last_detection = now
    
    def _detect_patterns(self):
        """检测访问模式"""
        now = time.time()
        hot_threshold = 10  # 5分钟内访问超过10次为热点
        cold_threshold = 1   # 1小时内访问少于1次为冷数据
        
        self._hot_keys = []
        self._cold_keys = []
        
        for key, times in self._access_times.items():
            # 计算最近5分钟的访问次数
            recent_accesses = [t for t in times if t >= now - 300]
            if len(recent_accesses) >= hot_threshold:
                self._hot_keys.append(key)
            
            # 计算最近1小时的访问次数
            recent_hour = [t for t in times if t >= now - 3600]
            if len(recent_hour) <= cold_threshold:
                self._cold_keys.append(key)
    
    def is_hot_key(self, key: str) -> bool:
        """检查是否为热点键"""
        # 实时检测一次
        if time.time() - self._last_detection >= self._detection_period:
            self._detect_patterns()
        return key in self._hot_keys
    
    def is_cold_key(self, key: str) -> bool:
        """检查是否为冷键"""
        if time.time() - self._last_detection >= self._detection_period:
            self._detect_patterns()
        return key in self._cold_keys
    
    def get_hot_keys(self) -> List[str]:
        """获取热点键列表"""
        if time.time() - self._last_detection >= self._detection_period:
            self._detect_patterns()
        return self._hot_keys
    
    def get_cold_keys(self) -> List[str]:
        """获取冷键列表"""
        if time.time() - self._last_detection >= self._detection_period:
            self._detect_patterns()
        return self._cold_keys
    
    def get_access_frequency(self, key: str) -> float:
        """获取访问频率（每分钟）"""
        now = time.time()
        times = self._access_times.get(key, [])
        recent_times = [t for t in times if t >= now - 300]
        return len(recent_times) / 5.0  # 最近5分钟的平均频率


class CacheOptimizer:
    """缓存优化器 - 增强版"""

    def __init__(self):
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "hot_key_hits": 0,
            "cold_key_hits": 0,
            "ttl_adjustments": 0
        }
        # 访问模式检测器
        self._pattern_detector = AccessPatternDetector()
        # 动态TTL映射
        self._dynamic_ttl: Dict[str, int] = {}
        # 默认TTL配置
        self._default_ttl = 3600
        self._hot_ttl = 7200  # 热点数据延长TTL
        self._cold_ttl = 600   # 冷数据缩短TTL

    def get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [prefix]
        key_parts.extend([str(arg) for arg in args])
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_str = ":".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()

    def calculate_hit_rate(self) -> float:
        """计算缓存命中率"""
        total = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total == 0:
            return 0.0
        return self.cache_stats["hits"] / total

    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            **self.cache_stats,
            "hit_rate": f"{self.calculate_hit_rate() * 100:.2f}%",
            "hot_key_count": len(self._pattern_detector.get_hot_keys()),
            "cold_key_count": len(self._pattern_detector.get_cold_keys())
        }

    def reset_stats(self):
        """重置统计"""
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "hot_key_hits": 0,
            "cold_key_hits": 0,
            "ttl_adjustments": 0
        }
    
    def record_access(self, key: str, is_hit: bool):
        """记录缓存访问"""
        self._pattern_detector.record_access(key)
        
        if is_hit:
            self.cache_stats["hits"] += 1
            if self._pattern_detector.is_hot_key(key):
                self.cache_stats["hot_key_hits"] += 1
            elif self._pattern_detector.is_cold_key(key):
                self.cache_stats["cold_key_hits"] += 1
        else:
            self.cache_stats["misses"] += 1
    
    def get_dynamic_ttl(self, key: str, base_ttl: int = None) -> int:
        """
        根据访问模式动态计算TTL
        
        Args:
            key: 缓存键
            base_ttl: 基础TTL
        
        Returns:
            动态调整后的TTL（秒）
        """
        ttl = base_ttl if base_ttl else self._default_ttl
        
        # 根据访问模式调整TTL
        if self._pattern_detector.is_hot_key(key):
            # 热点数据：延长TTL
            new_ttl = max(ttl, self._hot_ttl)
        elif self._pattern_detector.is_cold_key(key):
            # 冷数据：缩短TTL
            new_ttl = min(ttl, self._cold_ttl)
        else:
            new_ttl = ttl
        
        # 记录TTL调整次数
        if new_ttl != ttl:
            self.cache_stats["ttl_adjustments"] += 1
        
        return new_ttl
    
    def suggest_preload_keys(self) -> List[str]:
        """建议预加载的热点键"""
        return self._pattern_detector.get_hot_keys()
    
    def suggest_cleanup_keys(self) -> List[str]:
        """建议清理的冷键"""
        return self._pattern_detector.get_cold_keys()

# 全局缓存优化器
_cache_optimizer = CacheOptimizer()

def get_cache_optimizer() -> CacheOptimizer:
    """获取缓存优化器"""
    return _cache_optimizer

def cached(ttl: int = 3600, prefix: str = "default", dynamic_ttl: bool = True):
    """缓存装饰器 - 支持动态TTL"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from app.core.cache import api_cache

            # 生成缓存键
            cache_key = f"{prefix}:{func.__name__}:{_cache_optimizer.get_cache_key('', *args, **kwargs)}"

            # 尝试获取缓存
            cached_value = api_cache.get(cache_key)
            if cached_value is not None:
                _cache_optimizer.record_access(cache_key, is_hit=True)
                try:
                    return json.loads(cached_value)
                except:
                    return cached_value

            # 执行函数
            _cache_optimizer.record_access(cache_key, is_hit=False)
            result = func(*args, **kwargs)

            # 计算动态TTL
            final_ttl = _cache_optimizer.get_dynamic_ttl(cache_key, ttl) if dynamic_ttl else ttl

            # 存储结果
            _cache_optimizer.cache_stats["sets"] += 1
            try:
                api_cache.set(cache_key, json.dumps(result), ttl=final_ttl)
            except:
                api_cache.set(cache_key, str(result), ttl=final_ttl)

            return result
        return wrapper
    return decorator

def smart_cache(key_prefix: str, ttl: int = 3600, condition: Callable[[Any], bool] = None, 
                dynamic_ttl: bool = True):
    """智能缓存装饰器 - 增强版"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from app.core.cache import api_cache

            cache_key = f"{key_prefix}:{func.__name__}:{_cache_optimizer.get_cache_key('', *args, **kwargs)}"

            # 检查缓存
            cached_value = api_cache.get(cache_key)
            if cached_value is not None:
                _cache_optimizer.record_access(cache_key, is_hit=True)
                try:
                    result = json.loads(cached_value)
                    # 检查条件
                    if condition is None or condition(result):
                        return result
                except:
                    pass

            # 执行函数
            _cache_optimizer.record_access(cache_key, is_hit=False)
            result = func(*args, **kwargs)

            # 计算动态TTL
            final_ttl = _cache_optimizer.get_dynamic_ttl(cache_key, ttl) if dynamic_ttl else ttl

            # 存储结果
            _cache_optimizer.cache_stats["sets"] += 1
            try:
                api_cache.set(cache_key, json.dumps(result), ttl=final_ttl)
            except:
                pass

            return result
        return wrapper
    return decorator


class CachePreloader:
    """缓存预加载器"""
    
    def __init__(self):
        self._preload_tasks: List[Dict[str, Any]] = []
    
    def register_preload_task(self, name: str, loader_func: Callable, ttl: int = 3600):
        """
        注册预加载任务
        
        Args:
            name: 任务名称
            loader_func: 加载函数，返回缓存数据
            ttl: 缓存有效期
        """
        self._preload_tasks.append({
            "name": name,
            "loader": loader_func,
            "ttl": ttl,
            "last_run": 0
        })
    
    def preload_all(self, force: bool = False):
        """
        执行所有预加载任务
        
        Args:
            force: 是否强制刷新（即使最近已执行过）
        """
        from app.core.cache import api_cache
        
        for task in self._preload_tasks:
            now = time.time()
            
            # 检查是否需要执行
            if not force and now - task["last_run"] < task["ttl"]:
                continue
            
            try:
                # 执行加载函数
                data = task["loader"]()
                
                # 存储到缓存
                cache_key = f"preload:{task['name']}"
                api_cache.set(cache_key, json.dumps(data), ttl=task["ttl"])
                
                # 更新最后执行时间
                task["last_run"] = now
                
                print(f"✅ 缓存预加载完成: {task['name']}")
            except Exception as e:
                print(f"❌ 缓存预加载失败 {task['name']}: {e}")
    
    def preload_hot_keys(self):
        """预加载热点键"""
        hot_keys = _cache_optimizer.suggest_preload_keys()
        print(f"预加载热点键 ({len(hot_keys)}个): {hot_keys}")


# 全局缓存预加载器
_cache_preloader = CachePreloader()

def get_cache_preloader() -> CachePreloader:
    """获取缓存预加载器"""
    return _cache_preloader
