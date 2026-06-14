"""任务调度路由模块"""

from fastapi import APIRouter, Depends, Body
from typing import Dict, Any, List
from app.core.exceptions import BadRequestException, InternalServerErrorException

router = APIRouter()

@router.post("/tasks/run")
async def run_task(data: Dict[str, Any] = Body(...)):
    """运行任务"""
    try:
        from auto_task_scheduler import get_task_scheduler
        scheduler = get_task_scheduler()
        task_name = data.get('task_name')
        if not task_name:
            raise BadRequestException(detail="任务名称不能为空")
        task_args = data.get('task_args', {})
        result = scheduler.run_task(task_name, **task_args)
        return {
            "success": True,
            "data": result
        }
    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))

@router.get("/tasks")
async def get_all_tasks():
    """获取所有任务"""
    try:
        from auto_task_scheduler import get_task_scheduler
        scheduler = get_task_scheduler()
        tasks = scheduler.get_tasks()
        return {
            "success": True,
            "data": tasks
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))

@router.post("/tasks/add")
async def add_task(data: Dict[str, Any] = Body(...)):
    """添加任务"""
    try:
        from auto_task_scheduler import get_task_scheduler
        scheduler = get_task_scheduler()
        task_name = data.get('task_name')
        if not task_name:
            raise BadRequestException(detail="任务名称不能为空")
        interval = data.get('interval')
        if not interval:
            raise BadRequestException(detail="任务间隔不能为空")
        task_func = data.get('task_func')
        if not task_func:
            raise BadRequestException(detail="任务函数不能为空")
        task_args = data.get('task_args', {})
        scheduler.add_task(task_name, interval, task_func, **task_args)
        return {
            "success": True,
            "data": {"message": "任务添加成功"}
        }
    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))

@router.post("/tasks/remove")
async def remove_task(data: Dict[str, Any] = Body(...)):
    """移除任务"""
    try:
        from auto_task_scheduler import get_task_scheduler
        scheduler = get_task_scheduler()
        task_name = data.get('task_name')
        if not task_name:
            raise BadRequestException(detail="任务名称不能为空")
        scheduler.remove_task(task_name)
        return {
            "success": True,
            "data": {"message": "任务移除成功"}
        }
    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))
