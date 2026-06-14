#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版上下文管理系统
支持跨模块上下文共享、序列化传递、会话状态管理
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List
from threading import Lock
import hashlib
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContextScope(Enum):
    """上下文作用域"""
    SESSION = "session"       # 会话级别
    CONVERSATION = "conversation"  # 对话级别
    GLOBAL = "global"         # 全局级别
    USER = "user"             # 用户级别


class ContextEntry:
    """上下文条目"""
    
    def __init__(self, key: str, value: Any, scope: ContextScope = ContextScope.SESSION, 
                 ttl: int = 3600):
        self.key = key
        self.value = value
        self.scope = scope
        self.ttl = ttl
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.access_count = 0
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        return time.time() - self.created_at > self.ttl
    
    def access(self):
        """标记访问"""
        self.last_accessed = time.time()
        self.access_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "key": self.key,
            "value": self.value,
            "scope": self.scope.value,
            "ttl": self.ttl,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextEntry':
        """从字典反序列化"""
        entry = cls(
            key=data["key"],
            value=data["value"],
            scope=ContextScope(data["scope"]),
            ttl=data["ttl"]
        )
        entry.created_at = data["created_at"]
        entry.last_accessed = data["last_accessed"]
        entry.access_count = data["access_count"]
        return entry


class EnhancedContextManager:
    """增强版上下文管理器"""
    
    def __init__(self):
        self.context_store: Dict[str, Dict[str, ContextEntry]] = {}  # scope -> {key -> entry}
        self.session_contexts: Dict[str, Dict[str, Any]] = {}  # session_id -> context_data
        self.user_contexts: Dict[str, Dict[str, Any]] = {}  # user_id -> context_data
        self.lock = Lock()
        self.max_context_size = 1000
        self.cleanup_interval = 600  # 10分钟清理一次
        
        # 启动定时清理线程
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """启动定时清理线程"""
        import threading
        
        def cleanup_loop():
            while True:
                time.sleep(self.cleanup_interval)
                self._cleanup_expired()
        
        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()
    
    def _cleanup_expired(self):
        """清理过期上下文"""
        with self.lock:
            expired_count = 0
            for scope, entries in list(self.context_store.items()):
                expired_keys = [key for key, entry in entries.items() if entry.is_expired()]
                for key in expired_keys:
                    del entries[key]
                    expired_count += 1
            
            # 清理过期会话
            expired_sessions = [sid for sid, ctx in self.session_contexts.items() 
                               if time.time() - ctx.get("last_updated", 0) > 7200]
            for sid in expired_sessions:
                del self.session_contexts[sid]
                expired_count += 1
            
            if expired_count > 0:
                logger.info(f"清理了 {expired_count} 个过期上下文")
    
    def set(self, key: str, value: Any, scope: ContextScope = ContextScope.SESSION, 
            session_id: str = None, user_id: str = None, ttl: int = 3600):
        """设置上下文值"""
        with self.lock:
            # 确保作用域存在
            if scope.value not in self.context_store:
                self.context_store[scope.value] = {}
            
            # 创建上下文条目
            entry = ContextEntry(key, value, scope, ttl)
            self.context_store[scope.value][key] = entry
            
            # 如果是会话级别，同时保存到会话上下文
            if scope == ContextScope.SESSION and session_id:
                if session_id not in self.session_contexts:
                    self.session_contexts[session_id] = {
                        "session_id": session_id,
                        "created_at": time.time(),
                        "last_updated": time.time(),
                        "data": {}
                    }
                self.session_contexts[session_id]["data"][key] = value
                self.session_contexts[session_id]["last_updated"] = time.time()
            
            # 如果是用户级别，同时保存到用户上下文
            if scope == ContextScope.USER and user_id:
                if user_id not in self.user_contexts:
                    self.user_contexts[user_id] = {}
                self.user_contexts[user_id][key] = value
            
            logger.debug(f"上下文已设置: {scope.value}/{key}")
    
    def get(self, key: str, scope: ContextScope = ContextScope.SESSION, 
            session_id: str = None, default: Any = None) -> Any:
        """获取上下文值"""
        with self.lock:
            # 优先从会话上下文获取（如果提供了session_id）
            if session_id and session_id in self.session_contexts:
                if key in self.session_contexts[session_id]["data"]:
                    # 更新访问时间
                    self.session_contexts[session_id]["last_updated"] = time.time()
                    
                    # 同时更新作用域存储中的访问记录
                    if scope.value in self.context_store and key in self.context_store[scope.value]:
                        self.context_store[scope.value][key].access()
                    
                    return self.session_contexts[session_id]["data"][key]
            
            # 从作用域存储获取
            if scope.value in self.context_store and key in self.context_store[scope.value]:
                entry = self.context_store[scope.value][key]
                if not entry.is_expired():
                    entry.access()
                    return entry.value
            
            return default
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取完整的会话上下文"""
        with self.lock:
            if session_id in self.session_contexts:
                return self.session_contexts[session_id]["data"].copy()
            return None
    
    def set_session_context(self, session_id: str, context_data: Dict[str, Any]):
        """设置完整的会话上下文"""
        with self.lock:
            if session_id not in self.session_contexts:
                self.session_contexts[session_id] = {
                    "session_id": session_id,
                    "created_at": time.time(),
                    "last_updated": time.time(),
                    "data": {}
                }
            
            self.session_contexts[session_id]["data"].update(context_data)
            self.session_contexts[session_id]["last_updated"] = time.time()
            
            # 同时更新作用域存储
            for key, value in context_data.items():
                if ContextScope.SESSION.value not in self.context_store:
                    self.context_store[ContextScope.SESSION.value] = {}
                self.context_store[ContextScope.SESSION.value][key] = ContextEntry(
                    key, value, ContextScope.SESSION
                )
    
    def merge_session_context(self, session_id: str, context_data: Dict[str, Any]):
        """合并会话上下文"""
        with self.lock:
            if session_id not in self.session_contexts:
                self.set_session_context(session_id, context_data)
            else:
                self.session_contexts[session_id]["data"].update(context_data)
                self.session_contexts[session_id]["last_updated"] = time.time()
    
    def delete(self, key: str, scope: ContextScope = ContextScope.SESSION, session_id: str = None):
        """删除上下文值"""
        with self.lock:
            if scope.value in self.context_store and key in self.context_store[scope.value]:
                del self.context_store[scope.value][key]
            
            if session_id and session_id in self.session_contexts:
                if key in self.session_contexts[session_id]["data"]:
                    del self.session_contexts[session_id]["data"][key]
    
    def clear_session(self, session_id: str):
        """清除会话上下文"""
        with self.lock:
            if session_id in self.session_contexts:
                # 获取会话中的所有键并从作用域存储中删除
                for key in self.session_contexts[session_id]["data"]:
                    if ContextScope.SESSION.value in self.context_store:
                        self.context_store[ContextScope.SESSION.value].pop(key, None)
                
                del self.session_contexts[session_id]
                logger.info(f"会话上下文已清除: {session_id}")
    
    def serialize_context(self, session_id: str) -> str:
        """序列化会话上下文用于跨模块传递"""
        context = self.get_session_context(session_id)
        if not context:
            return ""
        
        # 压缩上下文数据
        data = {
            "session_id": session_id,
            "timestamp": time.time(),
            "context": context
        }
        
        return json.dumps(data, ensure_ascii=False)
    
    def deserialize_context(self, serialized: str) -> Optional[Dict[str, Any]]:
        """反序列化上下文数据"""
        try:
            data = json.loads(serialized)
            session_id = data.get("session_id")
            context_data = data.get("context", {})
            
            if session_id:
                self.set_session_context(session_id, context_data)
            
            return context_data
        except Exception as e:
            logger.error(f"上下文反序列化失败: {e}")
            return None
    
    def get_context_diff(self, session_id: str, reference_context: Dict[str, Any]) -> Dict[str, Any]:
        """获取上下文差异（用于增量传递）"""
        current = self.get_session_context(session_id) or {}
        diff = {}
        
        for key, value in current.items():
            if key not in reference_context or reference_context[key] != value:
                diff[key] = value
        
        return diff
    
    def get_status(self) -> Dict[str, Any]:
        """获取上下文管理器状态"""
        with self.lock:
            scope_stats = {}
            for scope, entries in self.context_store.items():
                scope_stats[scope] = {
                    "count": len(entries),
                    "keys": list(entries.keys())[:10]  # 最多显示10个键
                }
            
            return {
                "total_sessions": len(self.session_contexts),
                "total_users": len(self.user_contexts),
                "scope_stats": scope_stats,
                "max_size": self.max_context_size,
                "cleanup_interval": self.cleanup_interval
            }


# 全局上下文管理器实例
_context_manager = None

def get_context_manager() -> EnhancedContextManager:
    """获取全局上下文管理器实例"""
    global _context_manager
    if _context_manager is None:
        _context_manager = EnhancedContextManager()
    return _context_manager


if __name__ == "__main__":
    manager = get_context_manager()
    
    # 测试上下文管理
    session_id = "test-session-123"
    
    # 设置会话上下文
    manager.set("user_name", "张三", ContextScope.SESSION, session_id=session_id)
    manager.set("score", 680, ContextScope.SESSION, session_id=session_id)
    manager.set("city", "昆明", ContextScope.SESSION, session_id=session_id)
    
    # 获取上下文
    print(f"user_name: {manager.get('user_name', ContextScope.SESSION, session_id=session_id)}")
    print(f"score: {manager.get('score', ContextScope.SESSION, session_id=session_id)}")
    
    # 获取完整会话上下文
    full_context = manager.get_session_context(session_id)
    print(f"完整会话上下文: {full_context}")
    
    # 序列化测试
    serialized = manager.serialize_context(session_id)
    print(f"序列化后: {serialized[:100]}...")
    
    # 反序列化测试
    new_manager = EnhancedContextManager()
    new_manager.deserialize_context(serialized)
    print(f"反序列化后获取: {new_manager.get('user_name', ContextScope.SESSION, session_id=session_id)}")
    
    # 状态检查
    print(f"\n状态: {json.dumps(manager.get_status(), indent=2, ensure_ascii=False)}")
    
    print("\n=== 测试完成 ===")