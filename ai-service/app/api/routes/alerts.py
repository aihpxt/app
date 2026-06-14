"""告警路由"""

from fastapi import APIRouter
from app.core.alert_manager import get_alert_manager, init_alert_rules, AlertLevel

router = APIRouter(prefix="/api/alerts", tags=["告警"])

def init_alerts():
    """初始化告警系统"""
    manager = get_alert_manager()
    if not manager.rules:
        init_alert_rules()
        from app.core.alert_manager import setup_alert_handlers
        setup_alert_handlers()

@router.get("/")
async def get_alerts(minutes: int = 60):
    """获取告警列表"""
    init_alerts()
    manager = get_alert_manager()
    manager.check_all()
    alerts = manager.get_recent_alerts(minutes)

    return {
        "success": True,
        "data": {
            "count": len(alerts),
            "alerts": [
                {
                    "rule_name": a.rule_name,
                    "level": a.level.value,
                    "message": a.message,
                    "timestamp": a.timestamp
                }
                for a in alerts
            ]
        }
    }

@router.get("/check")
async def check_alerts():
    """手动检查告警"""
    init_alerts()
    manager = get_alert_manager()
    new_alerts = manager.check_all()

    return {
        "success": True,
        "data": {
            "new_alerts_count": len(new_alerts),
            "new_alerts": [
                {
                    "rule_name": a.rule_name,
                    "level": a.level.value,
                    "message": a.message,
                    "timestamp": a.timestamp
                }
                for a in new_alerts
            ]
        }
    }

@router.get("/rules")
async def get_alert_rules():
    """获取告警规则列表"""
    init_alerts()
    manager = get_alert_manager()

    return {
        "success": True,
        "data": {
            "count": len(manager.rules),
            "rules": [
                {
                    "name": r.name,
                    "level": r.level.value,
                    "message": r.message,
                    "cooldown": r.cooldown,
                    "last_triggered": r.last_triggered
                }
                for r in manager.rules
            ]
        }
    }

@router.post("/clear")
async def clear_alerts():
    """清除旧告警"""
    init_alerts()
    manager = get_alert_manager()
    manager.clear_old_alerts(hours=24)

    return {
        "success": True,
        "message": "已清除24小时前的告警"
    }
