#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动数据同步系统
支持增量同步、全量同步、数据更新检测
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum
from threading import Lock
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SyncMode(Enum):
    """同步模式"""
    FULL = "full"
    INCREMENTAL = "incremental"


class SyncStatus(Enum):
    """同步状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SyncTask:
    """同步任务"""
    
    def __init__(self, task_id: str, data_source: str, sync_mode: SyncMode = SyncMode.INCREMENTAL,
                 interval: int = 3600, last_sync: float = None):
        self.task_id = task_id
        self.data_source = data_source
        self.sync_mode = sync_mode
        self.interval = interval
        self.last_sync = last_sync
        self.status = SyncStatus.PENDING
        self.error_count = 0
        self.last_error = None
        self.retry_count = 0
        self.max_retries = 3
        self.retry_delay = 60  # 秒


class AutoDataSync:
    """自动数据同步系统 - 增强版（支持自动重试）"""
    
    def __init__(self):
        self.sync_tasks: Dict[str, SyncTask] = {}
        self.data_providers: Dict[str, Callable] = {}
        self.data_sinks: Dict[str, Callable] = {}
        self.listeners: List[Callable] = []
        self.lock = Lock()
        self._sync_history: List[Dict] = []
        # 重试统计
        self._retry_stats = {
            "total_retries": 0,
            "retry_success": 0,
            "retry_failed": 0
        }
    
    def register_data_provider(self, source_id: str, provider_func: Callable):
        """注册数据提供者"""
        self.data_providers[source_id] = provider_func
        logger.info(f"数据提供者已注册: {source_id}")
    
    def register_data_sink(self, sink_id: str, sink_func: Callable):
        """注册数据接收器"""
        self.data_sinks[sink_id] = sink_func
        logger.info(f"数据接收器已注册: {sink_id}")
    
    def add_sync_task(self, task_id: str, source_id: str, sink_id: str,
                      sync_mode: SyncMode = SyncMode.INCREMENTAL, interval: int = 3600):
        """添加同步任务"""
        if source_id not in self.data_providers:
            raise ValueError(f"数据提供者不存在: {source_id}")
        if sink_id not in self.data_sinks:
            raise ValueError(f"数据接收器不存在: {sink_id}")
        
        with self.lock:
            self.sync_tasks[task_id] = SyncTask(
                task_id=task_id,
                data_source=source_id,
                sync_mode=sync_mode,
                interval=interval
            )
        
        logger.info(f"同步任务已添加: {task_id}")
    
    def remove_sync_task(self, task_id: str):
        """移除同步任务"""
        with self.lock:
            if task_id in self.sync_tasks:
                del self.sync_tasks[task_id]
                logger.info(f"同步任务已移除: {task_id}")
    
    def _calculate_retry_delay(self, attempt: int, base_delay: int = 60) -> float:
        """
        计算重试延迟时间（指数退避）
        
        Args:
            attempt: 当前重试次数（从0开始）
            base_delay: 基础延迟时间（秒）
        
        Returns:
            float: 延迟时间（秒）
        """
        delay = base_delay * (2 ** attempt)
        # 添加随机抖动（0-10%）
        import random
        jitter = delay * random.uniform(0, 0.1)
        # 最大延迟不超过5分钟
        return min(delay + jitter, 300)
    
    def sync_data(self, task_id: str, retry_on_failure: bool = True) -> Dict:
        """
        执行同步任务（支持自动重试）
        
        Args:
            task_id: 任务ID
            retry_on_failure: 是否在失败时自动重试
        
        Returns:
            同步结果
        """
        task = self.sync_tasks.get(task_id)
        if not task:
            return {"success": False, "error": "任务不存在"}
        
        with self.lock:
            task.status = SyncStatus.RUNNING
            task.retry_count = 0
        
        last_exception = None
        
        # 执行同步（包含重试逻辑）
        for attempt in range(task.max_retries + 1):
            try:
                if attempt > 0:
                    # 重试前等待
                    delay = self._calculate_retry_delay(attempt - 1, task.retry_delay)
                    logger.warning(f"同步任务 {task_id} 第 {attempt} 次重试，等待 {delay:.2f} 秒")
                    time.sleep(delay)
                
                # 获取数据
                provider = self.data_providers.get(task.data_source)
                if not provider:
                    return {"success": False, "error": "数据提供者不存在"}
                
                # 根据同步模式获取数据
                if task.sync_mode == SyncMode.INCREMENTAL:
                    data = provider(last_sync=task.last_sync)
                else:
                    data = provider()
                
                if not data:
                    logger.info(f"同步任务 {task_id}: 无更新数据")
                    with self.lock:
                        task.status = SyncStatus.COMPLETED
                    return {"success": True, "updated": 0}
                
                # 写入数据
                sink = self.data_sinks.get("default")
                if sink:
                    result = sink(data, task.sync_mode)
                    
                    if result.get("success"):
                        with self.lock:
                            task.last_sync = time.time()
                            task.status = SyncStatus.COMPLETED
                            task.error_count = 0
                            task.retry_count = attempt  # 记录重试次数
                        
                        updated_count = result.get("updated", 0)
                        inserted_count = result.get("inserted", 0)
                        
                        # 如果是重试成功，更新统计
                        if attempt > 0:
                            with self.lock:
                                self._retry_stats["retry_success"] += 1
                        
                        # 记录历史
                        self._record_history(task_id, True, updated_count + inserted_count)
                        
                        # 通知监听器
                        self._notify_listeners({
                            "event": "sync_completed",
                            "task_id": task_id,
                            "updated": updated_count,
                            "inserted": inserted_count,
                            "retries": attempt
                        })
                        
                        logger.info(f"同步任务完成: {task_id}, 更新: {updated_count}, 新增: {inserted_count}, 重试次数: {attempt}")
                        
                        return {
                            "success": True,
                            "updated": updated_count,
                            "inserted": inserted_count,
                            "retries": attempt,
                            "message": "同步完成"
                        }
                
                return {"success": False, "error": "数据写入失败"}
            
            except Exception as e:
                last_exception = e
                
                if attempt == task.max_retries:
                    # 已达到最大重试次数
                    with self.lock:
                        task.status = SyncStatus.FAILED
                        task.error_count += 1
                        task.last_error = str(e)
                        task.retry_count = attempt
                        self._retry_stats["retry_failed"] += 1
                    
                    self._record_history(task_id, False, 0, str(e))
                    
                    # 发送失败通知
                    self._notify_listeners({
                        "event": "sync_failed",
                        "task_id": task_id,
                        "error": str(e),
                        "retries": attempt,
                        "max_retries": task.max_retries
                    })
                    
                    logger.error(f"同步任务失败 {task_id}（已重试 {attempt} 次）: {e}")
                    
                    return {"success": False, "error": str(e), "retries": attempt}
                
                # 记录重试
                with self.lock:
                    task.retry_count = attempt + 1
                    self._retry_stats["total_retries"] += 1
                
                logger.warning(f"同步任务 {task_id} 第 {attempt + 1} 次尝试失败，将进行重试: {e}")
        
        # 如果到达这里，说明所有重试都失败了
        with self.lock:
            task.status = SyncStatus.FAILED
        
        return {"success": False, "error": str(last_exception), "retries": task.max_retries}
    
    def sync_all(self) -> List[Dict]:
        """同步所有任务"""
        results = []
        for task_id in self.sync_tasks:
            result = self.sync_data(task_id)
            results.append({"task_id": task_id, **result})
        return results
    
    def schedule_sync(self, task_id: str, interval: int):
        """调度定时同步"""
        task = self.sync_tasks.get(task_id)
        if task:
            task.interval = interval
            logger.info(f"同步任务调度已更新: {task_id}, 间隔: {interval}秒")
    
    def check_updates(self, source_id: str) -> bool:
        """检查数据源是否有更新"""
        provider = self.data_providers.get(source_id)
        if not provider:
            return False
        
        try:
            # 获取最新数据的哈希值
            data = provider()
            if data:
                data_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
                
                # 检查是否与上次同步的数据相同
                task = next((t for t in self.sync_tasks.values() if t.data_source == source_id), None)
                if task:
                    # 简单检查：如果有数据且上次同步时间较久，认为有更新
                    if task.last_sync is None:
                        return True
                    # 实际应用中应该存储上次的数据哈希进行对比
                    return True
            
            return False
        except Exception as e:
            logger.error(f"检查更新失败 {source_id}: {e}")
            return False
    
    def _record_history(self, task_id: str, success: bool, count: int, error: str = None):
        """记录同步历史"""
        history = {
            "task_id": task_id,
            "timestamp": time.time(),
            "success": success,
            "count": count,
            "error": error
        }
        
        with self.lock:
            self._sync_history.append(history)
            # 保留最近100条记录
            if len(self._sync_history) > 100:
                self._sync_history.pop(0)
    
    def get_sync_history(self, task_id: str = None) -> List[Dict]:
        """获取同步历史"""
        if task_id:
            return [h for h in self._sync_history if h["task_id"] == task_id]
        return self._sync_history
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        task = self.sync_tasks.get(task_id)
        if task:
            return {
                "task_id": task.task_id,
                "data_source": task.data_source,
                "sync_mode": task.sync_mode.value,
                "interval": task.interval,
                "status": task.status.value,
                "last_sync": datetime.fromtimestamp(task.last_sync).isoformat() if task.last_sync else None,
                "error_count": task.error_count,
                "last_error": task.last_error
            }
        return None
    
    def get_all_tasks(self) -> List[Dict]:
        """获取所有任务状态"""
        return [self.get_task_status(task_id) for task_id in self.sync_tasks]
    
    def register_listener(self, listener: Callable):
        """注册监听器"""
        self.listeners.append(listener)
        logger.info("监听器已注册")
    
    def _notify_listeners(self, event: Dict):
        """通知所有监听器"""
        for listener in self.listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"监听器通知失败: {e}")
    
    def get_retry_stats(self) -> Dict:
        """获取重试统计信息"""
        total = self._retry_stats["total_retries"] + self._retry_stats["retry_success"]
        return {
            **self._retry_stats,
            "retry_success_rate": self._retry_stats["retry_success"] / max(total, 1)
        }


# 全局实例
data_sync = AutoDataSync()


# 示例数据提供者
def school_data_provider(last_sync=None):
    """学校数据提供者示例"""
    logger.info("获取学校数据...")
    # 模拟数据
    return [
        {"id": "1", "name": "师大附中", "score": 680, "updated_at": time.time()},
        {"id": "2", "name": "昆一中", "score": 675, "updated_at": time.time()},
    ]


def policy_data_provider(last_sync=None):
    """政策数据提供者示例"""
    logger.info("获取政策数据...")
    return [
        {"id": "p1", "title": "2024中考政策", "content": "新政策内容", "updated_at": time.time()}
    ]


# 模拟失败的数据提供者（用于测试重试机制）
failure_counter = 0

def failing_provider(last_sync=None):
    """模拟失败的数据提供者"""
    global failure_counter
    failure_counter += 1
    logger.info(f"获取数据（第 {failure_counter} 次尝试）...")
    
    # 前2次失败，第3次成功
    if failure_counter <= 2:
        raise Exception("模拟网络错误")
    
    return [
        {"id": "test1", "name": "测试学校", "score": 600, "updated_at": time.time()}
    ]


# 示例数据接收器
def default_data_sink(data, sync_mode):
    """默认数据接收器"""
    logger.info(f"写入数据，模式: {sync_mode.value}")
    
    if sync_mode == SyncMode.INCREMENTAL:
        # 增量更新
        updated = len(data)
        return {"success": True, "updated": updated, "inserted": 0}
    else:
        # 全量更新
        inserted = len(data)
        return {"success": True, "updated": 0, "inserted": inserted}


# 示例监听器
def sync_notifier(event):
    """同步通知器"""
    if event["event"] == "sync_completed":
        retries = event.get("retries", 0)
        print(f"📊 同步完成: {event['task_id']}, 更新: {event['updated']}, 新增: {event['inserted']}, 重试次数: {retries}")
    elif event["event"] == "sync_failed":
        print(f"❌ 同步失败: {event['task_id']}, 错误: {event['error']}, 重试次数: {event['retries']}/{event['max_retries']}")


if __name__ == "__main__":
    print("=" * 70)
    print("自动数据同步系统测试")
    print("=" * 70)
    
    # 注册数据提供者
    data_sync.register_data_provider("school", school_data_provider)
    data_sync.register_data_provider("policy", policy_data_provider)
    data_sync.register_data_provider("failing", failing_provider)
    
    # 注册数据接收器
    data_sync.register_data_sink("default", default_data_sink)
    
    # 注册监听器
    data_sync.register_listener(sync_notifier)
    
    # 添加同步任务
    data_sync.add_sync_task("school_sync", "school", "default", SyncMode.INCREMENTAL, 300)
    data_sync.add_sync_task("policy_sync", "policy", "default", SyncMode.FULL, 3600)
    data_sync.add_sync_task("failing_sync", "failing", "default", SyncMode.INCREMENTAL, 300)
    
    # 执行正常同步测试
    print("\n--- 测试1: 正常同步 ---")
    result = data_sync.sync_data("school_sync")
    print(f"同步结果: {json.dumps(result, ensure_ascii=False)}")
    
    # 执行重试机制测试
    print("\n--- 测试2: 重试机制测试 ---")
    print("注意：此测试会模拟前2次失败，第3次成功")
    result = data_sync.sync_data("failing_sync")
    print(f"同步结果: {json.dumps(result, ensure_ascii=False)}")
    
    # 获取重试统计
    print("\n--- 测试3: 重试统计 ---")
    stats = data_sync.get_retry_stats()
    print(f"重试统计: {json.dumps(stats, ensure_ascii=False)}")
    
    # 获取状态
    print("\n--- 测试4: 任务状态 ---")
    status = data_sync.get_task_status("failing_sync")
    print(f"任务状态: {json.dumps(status, ensure_ascii=False)}")
    
    print("\n✅ 测试完成！")
    print("=" * 70)