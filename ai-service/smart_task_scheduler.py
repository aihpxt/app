#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能任务调度系统
支持定时任务、事件触发任务、任务优先级、依赖管理
"""

import time
import threading
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from queue import PriorityQueue
from dataclasses import dataclass, field
from threading import Lock

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass(order=True)
class TaskItem:
    """任务项"""
    priority: int
    task_id: str = field(compare=False)
    task: 'ScheduledTask' = field(compare=False)


class ScheduledTask:
    """调度任务"""
    
    def __init__(self, task_id: str, func: Callable, 
                 schedule_type: str = "interval",
                 interval: int = 3600,
                 cron_expr: str = None,
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 dependencies: List[str] = None,
                 max_retries: int = 3,
                 retry_delay: int = 60):
        self.task_id = task_id
        self.func = func
        self.schedule_type = schedule_type  # interval, cron, event
        self.interval = interval  # 秒
        self.cron_expr = cron_expr
        self.priority = priority
        self.dependencies = dependencies or []
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.last_run = None
        self.next_run = None
        self.status = TaskStatus.PENDING
        self.run_count = 0
        self.fail_count = 0
        self.last_error = None
    
    def should_run(self, current_time: float) -> bool:
        """判断是否应该执行"""
        if self.schedule_type == "interval":
            if self.last_run is None:
                return True
            return current_time >= self.last_run + self.interval
        return False


class SmartTaskScheduler:
    """智能任务调度器"""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.task_queue = PriorityQueue()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.running = False
        self.thread = None
        self.lock = Lock()
        self._event_triggers = {}
    
    def add_task(self, task: ScheduledTask):
        """添加任务"""
        with self.lock:
            self.tasks[task.task_id] = task
            # 立即加入队列
            self._enqueue_task(task)
            logger.info(f"任务已添加: {task.task_id} (优先级: {task.priority.name})")
    
    def remove_task(self, task_id: str):
        """移除任务"""
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                logger.info(f"任务已移除: {task_id}")
    
    def schedule_interval_task(self, task_id: str, func: Callable, 
                               interval: int, priority: TaskPriority = TaskPriority.MEDIUM):
        """调度间隔任务"""
        task = ScheduledTask(
            task_id=task_id,
            func=func,
            schedule_type="interval",
            interval=interval,
            priority=priority
        )
        self.add_task(task)
    
    def schedule_cron_task(self, task_id: str, func: Callable, 
                           cron_expr: str, priority: TaskPriority = TaskPriority.MEDIUM):
        """调度Cron任务"""
        task = ScheduledTask(
            task_id=task_id,
            func=func,
            schedule_type="cron",
            cron_expr=cron_expr,
            priority=priority
        )
        self.add_task(task)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"事件处理器已注册: {event_type}")
    
    def trigger_event(self, event_type: str, data: Any = None):
        """触发事件"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                    logger.info(f"事件已处理: {event_type}")
                except Exception as e:
                    logger.error(f"事件处理失败 {event_type}: {e}")
    
    def _enqueue_task(self, task: ScheduledTask):
        """将任务加入队列"""
        item = TaskItem(
            priority=task.priority.value,
            task_id=task.task_id,
            task=task
        )
        self.task_queue.put(item)
    
    def _run_task(self, task: ScheduledTask):
        """执行任务"""
        task.status = TaskStatus.RUNNING
        task.last_run = time.time()
        task.run_count += 1
        
        logger.info(f"开始执行任务: {task.task_id}")
        
        retries = 0
        while retries <= task.max_retries:
            try:
                result = task.func()
                task.status = TaskStatus.COMPLETED
                logger.info(f"任务执行成功: {task.task_id}")
                return result
            except Exception as e:
                retries += 1
                task.last_error = str(e)
                logger.error(f"任务执行失败 {task.task_id} (重试 {retries}/{task.max_retries}): {e}")
                
                if retries <= task.max_retries:
                    time.sleep(task.retry_delay * retries)
                else:
                    task.status = TaskStatus.FAILED
                    task.fail_count += 1
                    logger.error(f"任务执行最终失败: {task.task_id}")
                    return None
    
    def _process_queue(self):
        """处理任务队列"""
        while self.running:
            try:
                # 设置超时，允许检查running状态
                item = self.task_queue.get(timeout=1)
                task = item.task
                
                # 检查依赖
                if not self._check_dependencies(task):
                    # 依赖未完成，重新入队
                    self._enqueue_task(task)
                    continue
                
                # 检查是否应该执行（间隔任务）
                if task.schedule_type == "interval":
                    current_time = time.time()
                    if task.last_run is not None and current_time < task.last_run + task.interval:
                        # 还没到执行时间，重新入队
                        self._enqueue_task(task)
                        continue
                
                # 执行任务（异步）
                threading.Thread(
                    target=self._run_task,
                    args=(task,),
                    daemon=True
                ).start()
                
            except Exception as e:
                if not self.running:
                    break
    
    def _check_dependencies(self, task: ScheduledTask) -> bool:
        """检查任务依赖"""
        if not task.dependencies:
            return True
        
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                logger.warning(f"任务依赖不存在: {dep_id}")
                return False
            dep_task = self.tasks[dep_id]
            if dep_task.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已经在运行")
            return
        
        self.running = True
        logger.info("启动智能任务调度器...")
        
        # 启动队列处理线程
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()
        
        # 启动定时检查线程
        self._start_scheduler_loop()
        
        logger.info("智能任务调度器已启动")
    
    def _start_scheduler_loop(self):
        """启动调度循环"""
        def scheduler_loop():
            while self.running:
                current_time = time.time()
                
                # 检查所有任务是否需要执行
                with self.lock:
                    for task_id, task in self.tasks.items():
                        if task.status == TaskStatus.RUNNING:
                            continue
                            
                        if task.should_run(current_time):
                            # 如果任务不在队列中，加入队列
                            # 简单检查：如果上次运行时间已过间隔，且不在运行中，加入队列
                            self._enqueue_task(task)
                
                time.sleep(1)
        
        threading.Thread(target=scheduler_loop, daemon=True).start()
    
    def stop(self):
        """停止调度器"""
        self.running = False
        logger.info("停止智能任务调度器...")
        
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("智能任务调度器已停止")
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        with self.lock:
            task = self.tasks.get(task_id)
            if task:
                return {
                    "task_id": task.task_id,
                    "status": task.status.value,
                    "priority": task.priority.name,
                    "run_count": task.run_count,
                    "fail_count": task.fail_count,
                    "last_run": datetime.fromtimestamp(task.last_run).isoformat() if task.last_run else None,
                    "last_error": task.last_error
                }
        return None
    
    def get_all_tasks(self) -> List[Dict]:
        """获取所有任务状态"""
        with self.lock:
            return [self.get_task_status(task_id) for task_id in self.tasks]
    
    def update_task_priority(self, task_id: str, new_priority: TaskPriority):
        """更新任务优先级"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].priority = new_priority
                logger.info(f"任务优先级已更新: {task_id} -> {new_priority.name}")


# 全局调度器实例
scheduler = SmartTaskScheduler()


# 示例任务
def example_task():
    """示例任务"""
    logger.info("执行示例任务...")
    time.sleep(1)
    logger.info("示例任务完成")


def data_sync_task():
    """数据同步任务"""
    logger.info("执行数据同步任务...")
    # 模拟数据同步
    time.sleep(2)
    logger.info("数据同步任务完成")


def health_check_task():
    """健康检查任务"""
    logger.info("执行健康检查任务...")
    # 模拟健康检查
    time.sleep(0.5)
    logger.info("健康检查任务完成")


if __name__ == "__main__":
    # 注册示例任务
    scheduler.schedule_interval_task("example", example_task, interval=30, priority=TaskPriority.LOW)
    scheduler.schedule_interval_task("data_sync", data_sync_task, interval=60, priority=TaskPriority.HIGH)
    scheduler.schedule_interval_task("health_check", health_check_task, interval=10, priority=TaskPriority.CRITICAL)
    
    # 启动调度器
    scheduler.start()
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()