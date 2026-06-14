#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能缓存优化系统
支持热点数据识别、智能预热、动态失效策略
"""

import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict
from threading import Lock
import hashlib
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CacheEntry:
    """缓存条目"""
    
    def __init__(self, key: str, value: Any, ttl: int = 3600):
        self.key = key
        self.value = value
        self.ttl = ttl
        self.created_at = time.time()
        self.access_count = 0
        self.last_access = time.time()
        self.is_hot = False
        self.hot_score = 0.0


class CachePolicy(Enum):
    """缓存策略"""
    LRU = "lru"  # 最近最少使用
    LFU = "lfu"  # 最不经常使用
    TTL = "ttl"  # 时间过期
    SMART = "smart"  # 智能策略


class SmartCache:
    """智能缓存系统"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.policy = CachePolicy.SMART
        self.access_patterns: Dict[str, List[float]] = defaultdict(list)
        self.hot_keys: List[str] = []
        self.lock = Lock()
        self._hits = 0
        self._misses = 0
        
        # 定期清理过期缓存
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """启动定期清理线程"""
        import threading
        
        def cleanup_loop():
            while True:
                time.sleep(60)  # 每分钟检查一次
                self._cleanup_expired()
                self._update_hot_keys()
        
        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()
    
    def _cleanup_expired(self):
        """清理过期缓存"""
        now = time.time()
        expired_keys = []
        
        with self.lock:
            for key, entry in self.cache.items():
                if now - entry.created_at > entry.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                logger.debug(f"缓存过期: {key}")
        
        if expired_keys:
            logger.info(f"清理过期缓存: {len(expired_keys)} 条")
    
    def _update_hot_keys(self):
        """更新热点键列表"""
        with self.lock:
            # 计算热度分数
            now = time.time()
            hot_candidates = []
            
            for key, entry in self.cache.items():
                # 热度 = 访问次数 / 存在时间（秒）
                age = now - entry.created_at
                if age < 60:
                    age = 60  # 至少1分钟
                
                # 时间衰减的热度分数
                decay_factor = 0.9 ** (age / 3600)  # 每小时衰减10%
                hot_score = entry.access_count * decay_factor
                entry.hot_score = hot_score
                
                if hot_score > 0.1:  # 热度阈值
                    hot_candidates.append((hot_score, key))
            
            # 按热度排序，取前20%作为热点
            hot_candidates.sort(reverse=True, key=lambda x: x[0])
            hot_count = max(1, int(len(self.cache) * 0.2))
            self.hot_keys = [k for _, k in hot_candidates[:hot_count]]
            
            # 标记热点
            for key in self.cache:
                self.cache[key].is_hot = key in self.hot_keys
        
        if self.hot_keys:
            logger.debug(f"热点键更新: {len(self.hot_keys)} 个")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        with self.lock:
            entry = self.cache.get(key)
            
            if entry:
                # 检查是否过期
                if time.time() - entry.created_at > entry.ttl:
                    del self.cache[key]
                    self._misses += 1
                    return None
                
                # 更新访问信息
                entry.access_count += 1
                entry.last_access = time.time()
                self._hits += 1
                
                # 记录访问模式
                self._record_access_pattern(key)
                
                return entry.value
            
            self._misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """设置缓存"""
        effective_ttl = ttl if ttl is not None else self.default_ttl
        
        with self.lock:
            # 检查是否需要淘汰
            if len(self.cache) >= self.max_size:
                self._evict()
            
            self.cache[key] = CacheEntry(key, value, effective_ttl)
            logger.debug(f"缓存设置: {key}")
    
    def _evict(self):
        """淘汰缓存"""
        if not self.cache:
            return
        
        candidates = []
        now = time.time()
        
        for key, entry in self.cache.items():
            if self.policy == CachePolicy.LRU:
                # 淘汰最久未访问的
                score = entry.last_access
            elif self.policy == CachePolicy.LFU:
                # 淘汰访问次数最少的
                score = entry.access_count
            elif self.policy == CachePolicy.SMART:
                # 智能策略：综合考虑热度和过期时间
                age = now - entry.created_at
                remaining_ttl = entry.ttl - age
                # 优先淘汰热度低且快过期的
                score = entry.hot_score * (remaining_ttl / entry.ttl)
            else:
                score = entry.last_access
            
            candidates.append((score, key))
        
        # 淘汰分数最低的
        candidates.sort(key=lambda x: x[0])
        evict_key = candidates[0][1]
        
        del self.cache[evict_key]
        logger.debug(f"缓存淘汰: {evict_key}")
    
    def _record_access_pattern(self, key: str):
        """记录访问模式"""
        now = time.time()
        self.access_patterns[key].append(now)
        
        # 保留最近100次访问记录
        if len(self.access_patterns[key]) > 100:
            self.access_patterns[key].pop(0)
    
    def delete(self, key: str):
        """删除缓存"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug(f"缓存删除: {key}")
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            logger.info("缓存已清空")
    
    def warm_up(self, keys: List[str], data_provider: Callable):
        """预热缓存"""
        logger.info(f"开始预热缓存: {len(keys)} 个键")
        
        for key in keys:
            if key not in self.cache:
                try:
                    data = data_provider(key)
                    if data:
                        self.set(key, data)
                        logger.debug(f"预热缓存: {key}")
                except Exception as e:
                    logger.error(f"预热缓存失败 {key}: {e}")
        
        logger.info(f"缓存预热完成")
    
    def predict_hot_keys(self) -> List[str]:
        """预测热点键"""
        # 分析访问模式，预测即将成为热点的键
        now = time.time()
        predictions = []
        
        for key, access_times in self.access_patterns.items():
            if len(access_times) < 5:
                continue
            
            # 计算访问频率趋势
            recent_accesses = [t for t in access_times if now - t < 300]  # 最近5分钟
            if len(recent_accesses) > len(access_times) * 0.5:
                # 近期访问频繁，可能成为热点
                predictions.append(key)
        
        return predictions
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        total = len(self.cache)
        hits = self._hits
        misses = self._misses
        total_requests = hits + misses
        hit_rate = hits / total_requests if total_requests > 0 else 0
        
        # 计算热点比例
        hot_count = sum(1 for entry in self.cache.values() if entry.is_hot)
        
        return {
            "total_entries": total,
            "hot_entries": hot_count,
            "hits": hits,
            "misses": misses,
            "hit_rate": round(hit_rate * 100, 2),
            "max_size": self.max_size,
            "policy": self.policy.value
        }
    
    def set_policy(self, policy: CachePolicy):
        """设置缓存策略"""
        self.policy = policy
        logger.info(f"缓存策略已更新: {policy.value}")
    
    def get_hot_keys(self) -> List[str]:
        """获取热点键"""
        return self.hot_keys.copy()


# 全局缓存实例
smart_cache = SmartCache(max_size=5000, default_ttl=3600)


# 示例数据提供者
def example_data_provider(key: str):
    """示例数据提供者"""
    # 模拟数据获取
    data = {
        "school_info": {"name": "师大附中", "score": 680},
        "policy_info": {"title": "中考政策", "content": "政策内容"},
        "user_info": {"name": "测试用户", "city": "昆明"}
    }
    return data.get(key)


if __name__ == "__main__":
    # 测试缓存功能
    print("测试智能缓存系统...")
    
    # 设置缓存
    smart_cache.set("school_info", {"name": "师大附中", "score": 680})
    smart_cache.set("policy_info", {"title": "中考政策", "content": "政策内容"})
    
    # 获取缓存
    result = smart_cache.get("school_info")
    print(f"获取缓存: {result}")
    
    # 模拟多次访问
    for _ in range(10):
        smart_cache.get("school_info")
    
    # 获取统计
    stats = smart_cache.get_stats()
    print(f"缓存统计: {json.dumps(stats, ensure_ascii=False, indent=2)}")
    
    # 获取热点键
    hot_keys = smart_cache.get_hot_keys()
    print(f"热点键: {hot_keys}")