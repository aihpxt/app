"""审计日志API路由"""

from fastapi import APIRouter, Query, HTTPException, Request
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.core.audit_logger import AuditLogger, AuditAction, AuditLevel

router = APIRouter(prefix="/api/audit", tags=["审计日志"])

class AuditLogResponse(BaseModel):
    """审计日志响应模型"""
    timestamp: str
    action: str
    level: str
    user_id: Optional[str]
    resource: Optional[str]
    details: Optional[dict]
    ip_address: Optional[str]
    status: str
    event_id: str

class AuditStatsResponse(BaseModel):
    """审计统计响应模型"""
    total_events: int
    by_action: dict
    by_level: dict
    by_status: dict
    unique_users: int
    recent_events: List[dict]

audit_logger = AuditLogger()

@router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    start_date: Optional[str] = Query(None, description="开始日期 YYYYMMDD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYYMMDD"),
    action: Optional[str] = Query(None, description="操作类型"),
    level: Optional[str] = Query(None, description="日志级别"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量")
):
    """查询审计日志"""
    try:
        action_enum = AuditAction[action.upper()] if action else None
        level_enum = AuditLevel[level.upper()] if level else None

        logs = audit_logger.query_logs(
            start_date=start_date,
            end_date=end_date,
            action=action_enum,
            level=level_enum,
            limit=limit
        )

        return logs

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@router.get("/statistics", response_model=AuditStatsResponse)
async def get_audit_statistics(days: int = Query(7, ge=1, le=90)):
    """获取审计统计信息"""
    try:
        stats = audit_logger.get_statistics(days=days)
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"统计失败: {str(e)}")

@router.post("/log")
async def create_audit_log(request: Request):
    """记录自定义审计日志"""
    try:
        body = await request.json()

        action = body.get("action", "SYSTEM_EVENT")
        level = body.get("level", "INFO")
        user_id = body.get("user_id")
        resource = body.get("resource")
        details = body.get("details")
        status = body.get("status", "SUCCESS")

        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        audit_logger.log(
            action=AuditAction[action.upper()],
            level=AuditLevel[level.upper()],
            user_id=user_id,
            resource=resource,
            details=details,
            ip_address=client_ip,
            user_agent=user_agent,
            status=status
        )

        return {"status": "success", "message": "审计日志已记录"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"记录失败: {str(e)}")

@router.get("/security-events")
async def get_security_events(limit: int = Query(50, ge=1, le=500)):
    """获取安全相关事件"""
    try:
        events = audit_logger.query_logs(
            action=AuditAction.SECURITY_EVENT,
            limit=limit
        )
        return events

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@router.get("/login-history")
async def get_login_history(user_id: Optional[str] = None, limit: int = Query(50)):
    """获取登录历史"""
    try:
        logs = audit_logger.query_logs(
            action=AuditAction.LOGIN,
            user_id=user_id,
            limit=limit
        )
        return logs

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
