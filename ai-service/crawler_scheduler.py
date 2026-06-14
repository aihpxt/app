#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫定时任务调度器
自动执行政策爬虫和学校爬虫，实现数据自动更新
"""

import os
import sys
import time
import logging
from datetime import datetime
from smart_task_scheduler import scheduler, TaskPriority

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/crawler_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CrawlerScheduler")

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_policy_crawler():
    """执行政策爬虫"""
    logger.info("========== 开始执行政策爬虫 ==========")
    try:
        from openclaw.policy_crawler import main as policy_main
        policy_main()
        logger.info("政策爬虫执行成功")
        return True
    except Exception as e:
        logger.error(f"政策爬虫执行失败: {str(e)}", exc_info=True)
        return False


def run_school_crawler():
    """执行学校爬虫"""
    logger.info("========== 开始执行学校爬虫 ==========")
    try:
        from openclaw.enhanced_school_crawler import main as school_main
        school_main()
        logger.info("学校爬虫执行成功")
        return True
    except Exception as e:
        logger.error(f"学校爬虫执行失败: {str(e)}", exc_info=True)
        return False


def run_school_info_updater():
    """执行学校信息更新"""
    logger.info("========== 开始执行学校信息更新 ==========")
    try:
        from tools.batch_update_schools import main as update_main
        update_main()
        logger.info("学校信息更新成功")
        return True
    except Exception as e:
        logger.error(f"学校信息更新失败: {str(e)}", exc_info=True)
        return False


def run_prefecture_schools():
    """执行地州学校数据更新"""
    logger.info("========== 开始执行地州学校数据更新 ==========")
    try:
        from openclaw.prefecture_schools import main as prefecture_main
        prefecture_main()
        logger.info("地州学校数据更新成功")
        return True
    except Exception as e:
        logger.error(f"地州学校数据更新失败: {str(e)}", exc_info=True)
        return False


def run_data_quality_check():
    """执行数据质量检查"""
    logger.info("========== 开始执行数据质量检查 ==========")
    try:
        from tools.school_data_quality import SchoolDataQualityChecker
        checker = SchoolDataQualityChecker()
        checker.generate_report()
        checker.close()
        logger.info("数据质量检查完成")
        return True
    except Exception as e:
        logger.error(f"数据质量检查失败: {str(e)}", exc_info=True)
        return False


def daily_crawler_task():
    """每日爬虫任务（凌晨2:00执行）"""
    logger.info(f"========== 每日爬虫任务开始 [{datetime.now()}] ==========")
    
    # 按顺序执行爬虫任务
    success_count = 0
    total_tasks = 4
    
    # 1. 政策爬虫
    if run_policy_crawler():
        success_count += 1
    
    # 等待5秒
    time.sleep(5)
    
    # 2. 学校爬虫
    if run_school_crawler():
        success_count += 1
    
    # 等待5秒
    time.sleep(5)
    
    # 3. 学校信息更新
    if run_school_info_updater():
        success_count += 1
    
    # 等待5秒
    time.sleep(5)
    
    # 4. 地州学校数据更新
    if run_prefecture_schools():
        success_count += 1
    
    logger.info(f"========== 每日爬虫任务完成 [{datetime.now()}] ==========")
    logger.info(f"执行结果: {success_count}/{total_tasks} 任务成功")
    
    # 触发数据更新事件
    scheduler.trigger_event("crawler_completed", {
        "success_count": success_count,
        "total_tasks": total_tasks,
        "timestamp": datetime.now().isoformat()
    })


def hourly_health_check():
    """每小时健康检查"""
    logger.debug(f"爬虫调度器健康检查 [{datetime.now()}]")
    # 检查任务状态
    tasks = scheduler.get_all_tasks()
    for task in tasks:
        if task and task['status'] == 'failed':
            logger.warning(f"检测到失败任务: {task['task_id']}")


def init_scheduler():
    """初始化调度器"""
    logger.info("========== 初始化爬虫调度器 ==========")
    
    # 每日爬虫任务 - 每天凌晨2:00执行
    # 使用间隔任务，设置为86400秒（24小时），延迟到凌晨2点
    scheduler.schedule_interval_task(
        "daily_crawler",
        daily_crawler_task,
        interval=86400,  # 24小时
        priority=TaskPriority.HIGH
    )
    
    # 每小时健康检查
    scheduler.schedule_interval_task(
        "hourly_health_check",
        hourly_health_check,
        interval=3600,  # 1小时
        priority=TaskPriority.LOW
    )
    
    # 数据质量检查 - 每周一凌晨3:00执行（604800秒 = 7天）
    scheduler.schedule_interval_task(
        "weekly_quality_check",
        run_data_quality_check,
        interval=604800,  # 7天
        priority=TaskPriority.MEDIUM
    )
    
    logger.info("爬虫调度器初始化完成")


def on_crawler_completed(data):
    """爬虫完成事件处理器"""
    logger.info(f"爬虫任务完成通知: {data}")
    # 可以在这里添加通知逻辑，如发送邮件、推送消息等


def main():
    """主函数"""
    logger.info("========== 启动爬虫定时任务调度器 ==========")
    
    # 注册事件处理器
    scheduler.register_event_handler("crawler_completed", on_crawler_completed)
    
    # 初始化调度器
    init_scheduler()
    
    # 启动调度器
    scheduler.start()
    
    logger.info("爬虫定时任务调度器已启动")
    logger.info("每日爬虫任务将在每天凌晨2:00自动执行")
    logger.info("按 Ctrl+C 停止调度器")
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在停止调度器...")
        scheduler.stop()
        logger.info("爬虫定时任务调度器已停止")


if __name__ == "__main__":
    main()