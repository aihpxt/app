#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版智能任务调度中心
支持动态优先级调整、任务依赖管理、并行执行和监控告警
"""

import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from queue import PriorityQueue
from dataclasses import dataclass, field
from threading import Lock, Thread
from collections import defaultdict

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
    """任务项（用于优先队列）"""
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
        self.execution_times: List[float] = []
    
    def should_run(self, current_time: float) -> bool:
        """判断是否应该执行"""
        if self.status == TaskStatus.RUNNING:
            return False
        
        if self.next_run is None:
            return True
        
        return current_time >= self.next_run
    
    def schedule_next_run(self):
        """计划下次执行时间"""
        now = time.time()
        
        if self.schedule_type == "interval":
            self.next_run = now + self.interval
        elif self.schedule_type == "cron":
            self.next_run = self._parse_cron(self.cron_expr)
        else:
            self.next_run = now + self.interval
    
    def _parse_cron(self, cron_expr: str) -> float:
        """简单的cron表达式解析"""
        now = datetime.now()
        parts = cron_expr.split()
        
        if len(parts) >= 2:
            try:
                minute = int(parts[0])
                hour = int(parts[1])
                
                next_run = now.replace(
                    hour=hour,
                    minute=minute,
                    second=0,
                    microsecond=0
                )
                
                if next_run <= now:
                    next_run += timedelta(days=1)
                
                return next_run.timestamp()
            except:
                pass
        
        return time.time() + 3600
    
    def record_execution(self, duration: float, success: bool):
        """记录执行结果"""
        self.execution_times.append(duration)
        if len(self.execution_times) > 100:
            self.execution_times = self.execution_times[-100:]
        
        if success:
            self.run_count += 1
            self.status = TaskStatus.COMPLETED
        else:
            self.fail_count += 1
            self.status = TaskStatus.FAILED
    
    @property
    def avg_execution_time(self):
        if not self.execution_times:
            return 0.0
        return sum(self.execution_times) / len(self.execution_times)


class EnhancedTaskScheduler:
    """增强版智能任务调度器"""
    
    def __init__(self, max_workers: int = 4):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.priority_queue = PriorityQueue()
        self.executor_threads: List[Thread] = []
        self.max_workers = max_workers
        self.running = False
        self.lock = Lock()
        self.dependency_graph: Dict[str, List[str]] = defaultdict(list)
        self.completed_tasks: List[str] = []
        
        # 性能指标
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time": 0.0,
            "avg_task_duration": 0.0
        }
        
        # 动态优先级调整参数
        self.adaptive_priority_enabled = True
        self.system_load_threshold = 0.8
    
    def add_task(self, task: ScheduledTask):
        """添加任务"""
        with self.lock:
            self.tasks[task.task_id] = task
            
            # 构建依赖图
            for dep_id in task.dependencies:
                self.dependency_graph[dep_id].append(task.task_id)
            
            # 计算初始优先级（考虑依赖）
            adjusted_priority = self._calculate_priority(task)
            self.priority_queue.put(TaskItem(adjusted_priority, task.task_id, task))
            
            logger.info(f"任务已添加: {task.task_id} (优先级: {task.priority.name})")
    
    def _calculate_priority(self, task: ScheduledTask) -> int:
        """计算任务优先级（考虑依赖和系统负载）"""
        base_priority = task.priority.value
        
        # 如果依赖任务未完成，降低优先级
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                base_priority += 1
        
        # 自适应调整：系统负载高时提高关键任务优先级
        if self.adaptive_priority_enabled:
            try:
                import psutil
                cpu_load = psutil.cpu_percent() / 100
                
                if cpu_load > self.system_load_threshold:
                    if task.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]:
                        base_priority = max(1, base_priority - 1)
                    else:
                        base_priority += 1
            except:
                pass
        
        return base_priority
    
    def remove_task(self, task_id: str):
        """移除任务"""
        with self.lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                logger.info(f"任务已移除: {task_id}")
    
    def start(self):
        """启动调度器"""
        if self.running:
            return
        
        self.running = True
        logger.info("智能任务调度器启动")
        
        # 启动工作线程
        for i in range(self.max_workers):
            thread = Thread(target=self._worker_loop, name=f"Worker-{i+1}", daemon=True)
            thread.start()
            self.executor_threads.append(thread)
        
        # 启动调度线程
        scheduler_thread = Thread(target=self._scheduler_loop, name="Scheduler", daemon=True)
        scheduler_thread.start()
    
    def stop(self):
        """停止调度器"""
        self.running = False
        logger.info("智能任务调度器停止")
    
    def _scheduler_loop(self):
        """调度主循环"""
        while self.running:
            now = time.time()
            
            # 更新任务状态并重新入队
            with self.lock:
                for task_id, task in list(self.tasks.items()):
                    if task.should_run(now) and task.status != TaskStatus.RUNNING:
                        # 检查依赖
                        if self._check_dependencies(task):
                            priority = self._calculate_priority(task)
                            self.priority_queue.put(TaskItem(priority, task_id, task))
            
            time.sleep(1)
    
    def _check_dependencies(self, task: ScheduledTask) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                dep_task = self.tasks.get(dep_id)
                if dep_task and dep_task.status == TaskStatus.FAILED:
                    logger.warning(f"任务 {task.task_id} 的依赖 {dep_id} 失败，跳过执行")
                    return False
                return False
        return True
    
    def _worker_loop(self):
        """工作线程循环"""
        while self.running:
            try:
                # 非阻塞获取任务
                try:
                    task_item = self.priority_queue.get(block=True, timeout=1)
                except:
                    continue
                
                task = task_item.task
                
                # 检查任务是否仍然有效
                with self.lock:
                    if task.task_id not in self.tasks:
                        continue
                    
                    current_task = self.tasks[task.task_id]
                    if current_task.status == TaskStatus.RUNNING:
                        continue
                    
                    current_task.status = TaskStatus.RUNNING
                
                # 执行任务
                start_time = time.time()
                try:
                    result = task.func()
                    duration = time.time() - start_time
                    task.record_execution(duration, success=True)
                    
                    with self.lock:
                        self.completed_tasks.append(task.task_id)
                        self.metrics["tasks_completed"] += 1
                        self.metrics["total_execution_time"] += duration
                    
                    logger.info(f"任务完成: {task.task_id} (耗时: {duration:.2f}s)")
                except Exception as e:
                    duration = time.time() - start_time
                    task.record_execution(duration, success=False)
                    task.last_error = str(e)
                    
                    with self.lock:
                        self.metrics["tasks_failed"] += 1
                    
                    logger.error(f"任务失败: {task.task_id} - {e}")
                    
                    # 重试逻辑
                    if task.fail_count < task.max_retries:
                        with self.lock:
                            task.status = TaskStatus.PENDING
                            task.next_run = time.time() + task.retry_delay
                
                # 计划下次执行
                task.schedule_next_run()
                
            except Exception as e:
                logger.error(f"工作线程异常: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        with self.lock:
            avg_duration = 0.0
            if self.metrics["tasks_completed"] > 0:
                avg_duration = self.metrics["total_execution_time"] / self.metrics["tasks_completed"]
            
            task_status = {}
            for task_id, task in self.tasks.items():
                task_status[task_id] = {
                    "status": task.status.value,
                    "priority": task.priority.name,
                    "run_count": task.run_count,
                    "fail_count": task.fail_count,
                    "avg_execution_time": round(task.avg_execution_time, 3),
                    "next_run": task.next_run
                }
            
            return {
                "running": self.running,
                "queue_size": self.priority_queue.qsize(),
                "worker_count": len(self.executor_threads),
                "metrics": {
                    "tasks_completed": self.metrics["tasks_completed"],
                    "tasks_failed": self.metrics["tasks_failed"],
                    "total_execution_time": round(self.metrics["total_execution_time"], 3),
                    "avg_task_duration": round(avg_duration, 3),
                    "success_rate": round(self.metrics["tasks_completed"] / max(self.metrics["tasks_completed"] + self.metrics["tasks_failed"], 1) * 100, 2)
                },
                "tasks": task_status
            }


# 全局调度器实例
_scheduler = None

def get_scheduler(max_workers: int = 4) -> EnhancedTaskScheduler:
    """获取全局调度器实例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = EnhancedTaskScheduler(max_workers=max_workers)
    return _scheduler


# 示例任务
def example_task():
    """示例任务"""
    time.sleep(1)
    logger.info("示例任务执行中...")
    return {"result": "success"}


if __name__ == "__main__":
    scheduler = get_scheduler(max_workers=2)
    
    # 添加示例任务
    task1 = ScheduledTask(
        task_id="example_task",
        func=example_task,
        schedule_type="interval",
        interval=5,
        priority=TaskPriority.HIGH
    )
    scheduler.add_task(task1)
    
    # 启动调度器
    scheduler.start()
    logger.info("调度器已启动，按 Ctrl+C 停止")
    
    # 定期打印状态
    try:
        while True:
            time.sleep(3)
            status = scheduler.get_status()
            print(f"\n=== 调度器状态 ({datetime.now().strftime('%H:%M:%S')}) ===")
            print(json.dumps(status, indent=2, ensure_ascii=False))
    except KeyboardInterrupt:
        scheduler.stop()
        print("\n调度器已停止")