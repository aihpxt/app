import time
import threading
import json
from datetime import datetime

class AutoTaskScheduler:
    """自动化任务调度器"""
    
    def __init__(self):
        self.tasks = {}
        self.running = False
        self.thread = None
    
    def register_task(self, task_name, task_func, interval, priority=5, importance=5.0):
        """注册任务
        
        Args:
            task_name (str): 任务名称
            task_func (callable): 任务函数
            interval (int): 执行间隔（秒）
            priority (int): 优先级（1-10）
            importance (float): 重要性（1.0-10.0）
        """
        self.tasks[task_name] = {
            "func": task_func,
            "interval": interval,
            "priority": priority,
            "importance": importance,
            "last_run": None,
            "next_run": None
        }
    
    def start(self):
        """启动任务调度器"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
    
    def stop(self):
        """停止任务调度器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _run(self):
        """调度器主循环"""
        while self.running:
            current_time = time.time()
            
            # 创建任务字典的副本，避免在迭代过程中字典大小改变
            tasks_copy = list(self.tasks.items())
            for task_name, task_info in tasks_copy:
                next_run = task_info["next_run"]
                if next_run is None or current_time >= next_run:
                    # 执行任务
                    try:
                        result = task_info["func"]()
                        print(f"[{datetime.now()}] 任务 {task_name} 执行完成: {result}")
                    except Exception as e:
                        print(f"[{datetime.now()}] 任务 {task_name} 执行失败: {str(e)}")
                    
                    # 更新任务状态
                    task_info["last_run"] = current_time
                    # 确保 interval 是一个数字
                    interval = task_info["interval"]
                    if isinstance(interval, dict) and "interval" in interval:
                        interval = interval["interval"]
                    task_info["next_run"] = current_time + interval
            
            # 休眠1秒
            time.sleep(1)
    
    def get_all_tasks_status(self):
        """获取所有任务状态"""
        status = {}
        current_time = time.time()
        
        for task_name, task_info in self.tasks.items():
            status[task_name] = {
                "last_run": task_info["last_run"],
                "next_run": task_info["next_run"],
                "interval": task_info["interval"],
                "time_until_next_run": task_info["next_run"] - current_time if task_info["next_run"] else None
            }
        
        return status
    
    def get_all_tasks(self):
        """获取所有任务列表（兼容API调用）"""
        return self.get_all_tasks_status()
    
    def is_running(self):
        """检查调度器是否运行中"""
        return self.running

# 创建全局调度器实例
auto_task_scheduler = AutoTaskScheduler()

def get_task_scheduler():
    """获取任务调度器实例"""
    return auto_task_scheduler
