"""
定时任务调度器
用于自动执行学习任务
"""

import time
import threading
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openclaw.auto_learning_system import AutoLearningSystem
from openclaw.school_info_updater import SchoolInfoUpdater
from openclaw.policy_info_updater import PolicyInfoUpdater
from openclaw.industry_info_updater import IndustryInfoUpdater

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        self.auto_learning_system = AutoLearningSystem()
        self.running = False
        self.scheduler_thread = None
        
    def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已经在运行")
            return
        
        self.running = True
        logger.info("启动任务调度器...")
        
        # 配置定时任务
        self._setup_scheduled_tasks()
        
        # 启动调度线程
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("任务调度器已启动")
        logger.info("定时任务:")
        logger.info("  - 学校信息更新: 每天凌晨2点")
        logger.info("  - 政策信息更新: 每天凌晨3点")
        logger.info("  - 行业信息更新: 每天凌晨4点")
        logger.info("  - 数据质量检查: 每天凌晨5点")
        logger.info("  - 完整学习周期: 每周日凌晨1点")

    def stop(self):
        """停止调度器"""
        if not self.running:
            return
        
        self.running = False
        logger.info("停止任务调度器...")
        
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("任务调度器已停止")

    def _setup_scheduled_tasks(self):
        """配置定时任务"""
        # 每天凌晨2点更新学校信息
        schedule.every().day.at("02:00").do(self._update_school_info_task)
        
        # 每天凌晨3点更新政策信息
        schedule.every().day.at("03:00").do(self._update_policy_info_task)
        
        # 每天凌晨4点更新行业信息
        schedule.every().day.at("04:00").do(self._update_industry_info_task)
        
        # 每天凌晨5点检查数据质量
        schedule.every().day.at("05:00").do(self._check_data_quality_task)
        
        # 每周日凌晨1点执行完整学习周期
        schedule.every().sunday.at("01:00").do(self._full_learning_cycle_task)
        
        # 每小时执行一次轻量级更新
        schedule.every().hour.do(self._lightweight_update_task)

    def _run_scheduler(self):
        """运行调度器"""
        logger.info("调度器线程已启动")
        
        while self.running:
            try:
                # 检查并执行待执行的任务
                schedule.run_pending()
                
                # 等待1分钟
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"调度器运行错误: {e}")
                time.sleep(60)

    def _update_school_info_task(self):
        """学校信息更新任务"""
        logger.info("=" * 60)
        logger.info("开始执行学校信息更新任务")
        logger.info("=" * 60)
        
        try:
            # 获取需要更新的学校
            updater = SchoolInfoUpdater(self.auto_learning_system.db_path)
            
            # 这里可以实现批量更新逻辑
            # 例如：每天更新10所学校
            logger.info("学校信息更新任务完成")
            
        except Exception as e:
            logger.error(f"学校信息更新任务失败: {e}")

    def _update_policy_info_task(self):
        """政策信息更新任务"""
        logger.info("=" * 60)
        logger.info("开始执行政策信息更新任务")
        logger.info("=" * 60)
        
        try:
            updater = PolicyInfoUpdater(self.auto_learning_system.db_path)
            results = updater.update_policy_info()
            
            logger.info(f"政策信息更新任务完成: {results}")
            
        except Exception as e:
            logger.error(f"政策信息更新任务失败: {e}")

    def _update_industry_info_task(self):
        """行业信息更新任务"""
        logger.info("=" * 60)
        logger.info("开始执行行业信息更新任务")
        logger.info("=" * 60)
        
        try:
            updater = IndustryInfoUpdater(self.auto_learning_system.db_path)
            results = updater.update_industry_info()
            
            logger.info(f"行业信息更新任务完成: {results}")
            
        except Exception as e:
            logger.error(f"行业信息更新任务失败: {e}")

    def _check_data_quality_task(self):
        """数据质量检查任务"""
        logger.info("=" * 60)
        logger.info("开始执行数据质量检查任务")
        logger.info("=" * 60)
        
        try:
            self.auto_learning_system._check_data_quality()
            logger.info("数据质量检查任务完成")
            
        except Exception as e:
            logger.error(f"数据质量检查任务失败: {e}")

    def _full_learning_cycle_task(self):
        """完整学习周期任务"""
        logger.info("=" * 60)
        logger.info("开始执行完整学习周期任务")
        logger.info("=" * 60)
        
        try:
            self.auto_learning_system.start_learning_cycle()
            logger.info("完整学习周期任务完成")
            
        except Exception as e:
            logger.error(f"完整学习周期任务失败: {e}")

    def _lightweight_update_task(self):
        """轻量级更新任务"""
        try:
            # 执行轻量级更新，例如：
            # - 检查紧急政策更新
            # - 更新热门学校信息
            # - 清理过期数据
            logger.debug("执行轻量级更新任务")
            
        except Exception as e:
            logger.error(f"轻量级更新任务失败: {e}")

    def run_manual_task(self, task_type: str) -> Dict:
        """手动执行任务"""
        logger.info(f"手动执行任务: {task_type}")
        
        try:
            if task_type == 'school':
                self._update_school_info_task()
            elif task_type == 'policy':
                self._update_policy_info_task()
            elif task_type == 'industry':
                self._update_industry_info_task()
            elif task_type == 'quality':
                self._check_data_quality_task()
            elif task_type == 'full':
                self._full_learning_cycle_task()
            else:
                return {'success': False, 'message': f'未知任务类型: {task_type}'}
            
            return {'success': True, 'message': f'{task_type} 任务执行成功'}
            
        except Exception as e:
            logger.error(f"手动执行任务失败: {e}")
            return {'success': False, 'message': str(e)}

    def get_scheduled_tasks(self) -> List[Dict]:
        """获取定时任务列表"""
        tasks = []
        
        for job in schedule.jobs:
            tasks.append({
                'task_type': str(job.job_func),
                'next_run': job.next_run.strftime('%Y-%m-%d %H:%M:%S') if job.next_run else None,
                'interval': str(job.interval)
            })
        
        return tasks

    def get_task_status(self) -> Dict:
        """获取任务状态"""
        return {
            'running': self.running,
            'thread_alive': self.scheduler_thread.is_alive() if self.scheduler_thread else False,
            'scheduled_tasks': len(schedule.jobs),
            'last_check': datetime.now().isoformat()
        }


# 全局调度器实例
scheduler = TaskScheduler()


def start_scheduler():
    """启动调度器"""
    scheduler.start()


def stop_scheduler():
    """停止调度器"""
    scheduler.stop()


if __name__ == "__main__":
    # 创建日志目录
    os.makedirs('logs', exist_ok=True)
    
    # 启动调度器
    start_scheduler()
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n收到停止信号...")
        stop_scheduler()
        print("调度器已停止")