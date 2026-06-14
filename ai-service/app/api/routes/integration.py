"""集成路由模块"""

from fastapi import APIRouter, Depends, Body
from typing import Dict, Any, List
from app.core.exceptions import BadRequestException, InternalServerErrorException

router = APIRouter()

@router.get("/status")
def get_integration_status():
    """获取集成状态"""
    try:
        from hermes_openclaw_integration import get_hermes_openclaw_integration
        integration = get_hermes_openclaw_integration()
        status = integration.get_integration_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))

@router.get("/metrics")
def get_integration_metrics():
    """获取集成指标"""
    try:
        from hermes_openclaw_integration import get_hermes_openclaw_integration
        integration = get_hermes_openclaw_integration()
        metrics = integration.get_integration_metrics()
        return {
            "success": True,
            "data": metrics
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))

@router.post("/dispatch")
def dispatch_request(data: Dict[str, Any] = Body(...)):
    """智能分派请求"""
    try:
        from hermes_openclaw_integration import get_hermes_openclaw_integration
        integration = get_hermes_openclaw_integration()
        user_input = data.get('input', '')
        if not user_input:
            raise BadRequestException(detail="输入内容不能为空")
        context = data.get('context', {})
        result = integration.intelligent_dispatch(user_input, context)
        return {
            "success": True,
            "data": result
        }
    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))

@router.post("/orchestrate")
def orchestrate_workflow(data: Dict[str, Any] = Body(...)):
    """工作流编排"""
    try:
        from hermes_openclaw_integration import get_hermes_openclaw_integration
        integration = get_hermes_openclaw_integration()
        user_input = data.get('input', '')
        if not user_input:
            raise BadRequestException(detail="输入内容不能为空")
        context = data.get('context', {})
        result = integration.orchestrate(user_input, context)
        return {
            "success": True,
            "data": result
        }
    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))

@router.get("/config")
def get_integration_config():
    """获取集成配置"""
    try:
        from hermes_openclaw_integration import get_hermes_openclaw_integration
        integration = get_hermes_openclaw_integration()
        config = {
            "hermes_url": integration.hermes_url,
            "timeout": integration.timeout,
            "initialized": integration.initialized
        }
        return {
            "success": True,
            "data": config
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))

@router.post("/config")
def update_integration_config(config: Dict[str, Any] = Body(...)):
    """更新集成配置"""
    try:
        from hermes_openclaw_integration import get_hermes_openclaw_integration
        integration = get_hermes_openclaw_integration()
        if 'hermes_url' in config:
            integration.hermes_url = config['hermes_url']
        if 'timeout' in config:
            integration.timeout = config['timeout']
        result = {
            "hermes_url": integration.hermes_url,
            "timeout": integration.timeout
        }
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))

@router.get("/endpoints")
def get_integration_endpoints():
    """获取集成端点信息"""
    try:
        endpoints = [
            {
                "path": "/api/v1/integration/status",
                "method": "GET",
                "description": "获取集成状态"
            },
            {
                "path": "/api/v1/integration/metrics",
                "method": "GET",
                "description": "获取集成指标"
            },
            {
                "path": "/api/v1/integration/dispatch",
                "method": "POST",
                "description": "智能分派请求"
            },
            {
                "path": "/api/v1/integration/orchestrate",
                "method": "POST",
                "description": "工作流编排"
            },
            {
                "path": "/api/v1/integration/config",
                "method": "GET",
                "description": "获取集成配置"
            },
            {
                "path": "/api/v1/integration/config",
                "method": "POST",
                "description": "更新集成配置"
            },
            {
                "path": "/api/v1/integration/endpoints",
                "method": "GET",
                "description": "获取集成端点信息"
            }
        ]
        return {
            "success": True,
            "data": endpoints
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))
