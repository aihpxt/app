from auto_task_scheduler import auto_task_scheduler
from system_report import generate_system_report


# 注册任务
def register_tasks():
    """注册所有任务"""
    # 注册系统报告生成任务
    auto_task_scheduler.register_task(
        task_name="generate_system_report",
        task_func=generate_system_report,
        interval=43200,  # 12小时
        priority=4,
        importance=6.0
    )
    
    # 启动任务调度器
    auto_task_scheduler.start()


# 调用注册函数
register_tasks()