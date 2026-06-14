#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一监控仪表盘API
整合所有智能模块的监控数据，提供可视化接口
"""

import time
import json
import logging
import math
from typing import Dict, Any, Optional, List
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clean_inf_values(data):
    """递归清理字典中的inf和nan值，使其可JSON序列化"""
    if isinstance(data, dict):
        return {k: clean_inf_values(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_inf_values(item) for item in data]
    elif isinstance(data, float):
        if math.isinf(data) or math.isnan(data):
            return None
        return data
    return data


class MonitoringDashboard:
    """统一监控仪表盘"""
    
    def __init__(self):
        self.smart_cache = None
        self.context_manager = None
        self.scheduler = None
        self.gateway = None
        self.integration_center = None
        
        self._init_services()
    
    def _init_services(self):
        """初始化服务引用"""
        try:
            from smart_cache import SmartCache
            self.smart_cache = SmartCache()
        except Exception as e:
            logger.warning(f"智能缓存初始化失败: {e}")
        
        try:
            from enhanced_context_manager import get_context_manager
            self.context_manager = get_context_manager()
        except Exception as e:
            logger.warning(f"上下文管理器初始化失败: {e}")
        
        try:
            from enhanced_task_scheduler import get_scheduler
            self.scheduler = get_scheduler()
        except Exception as e:
            logger.warning(f"任务调度器初始化失败: {e}")
        
        try:
            from smart_gateway import get_gateway
            self.gateway = get_gateway()
        except Exception as e:
            logger.warning(f"智能网关初始化失败: {e}")
        
        try:
            from smart_integration_center import get_integration_center
            self.integration_center = get_integration_center()
        except Exception as e:
            logger.warning(f"集成中心初始化失败: {e}")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取完整的仪表盘数据"""
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "metrics": {},
            "alerts": []
        }
        
        # 获取系统级指标
        try:
            dashboard["metrics"]["system"] = self._get_system_metrics()
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            dashboard["metrics"]["system"] = {"status": "error", "message": str(e)}
        
        # 获取缓存指标
        try:
            dashboard["services"]["cache"] = self._get_cache_status()
        except Exception as e:
            logger.error(f"获取缓存状态失败: {e}")
            dashboard["services"]["cache"] = {"status": "error", "message": str(e)}
        
        # 获取上下文管理状态
        try:
            dashboard["services"]["context"] = self._get_context_status()
        except Exception as e:
            logger.error(f"获取上下文状态失败: {e}")
            dashboard["services"]["context"] = {"status": "error", "message": str(e)}
        
        # 获取任务调度状态
        try:
            dashboard["services"]["scheduler"] = self._get_scheduler_status()
        except Exception as e:
            logger.error(f"获取调度器状态失败: {e}")
            dashboard["services"]["scheduler"] = {"status": "error", "message": str(e)}
        
        # 获取网关状态
        try:
            dashboard["services"]["gateway"] = self._get_gateway_status()
        except Exception as e:
            logger.error(f"获取网关状态失败: {e}")
            dashboard["services"]["gateway"] = {"status": "error", "message": str(e)}
        
        # 获取集成中心状态
        try:
            dashboard["services"]["integration"] = self._get_integration_status()
        except Exception as e:
            logger.error(f"获取集成中心状态失败: {e}")
            dashboard["services"]["integration"] = {"status": "error", "message": str(e)}
        
        # 生成告警
        try:
            dashboard["alerts"] = self._generate_alerts(dashboard)
        except Exception as e:
            logger.error(f"生成告警失败: {e}")
            dashboard["alerts"] = []
        
        return clean_inf_values(dashboard)
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """获取系统资源指标"""
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "cores": psutil.cpu_count(logical=True),
                    "status": "healthy" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
                },
                "memory": {
                    "percent": memory.percent,
                    "used_gb": round(memory.used / (1024 ** 3), 2),
                    "total_gb": round(memory.total / (1024 ** 3), 2),
                    "status": "healthy" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
                },
                "disk": {
                    "percent": disk.percent,
                    "used_gb": round(disk.used / (1024 ** 3), 2),
                    "total_gb": round(disk.total / (1024 ** 3), 2),
                    "status": "healthy" if disk.percent < 80 else "warning" if disk.percent < 95 else "critical"
                },
                "uptime": round(time.time() - psutil.boot_time(), 0),
                "process_count": len(psutil.pids())
            }
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return {}
    
    def _get_cache_status(self) -> Dict[str, Any]:
        """获取缓存状态"""
        if not self.smart_cache:
            return {"status": "unavailable"}
        
        try:
            return {
                "status": "healthy",
                "size": len(self.smart_cache.cache),
                "max_size": self.smart_cache.max_size,
                "hot_keys_count": len(self.smart_cache.hot_keys),
                "hit_rate": round(self.smart_cache._hits / max(self.smart_cache._hits + self.smart_cache._misses, 1) * 100, 2),
                "hits": self.smart_cache._hits,
                "misses": self.smart_cache._misses
            }
        except Exception as e:
            logger.error(f"获取缓存状态失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def _get_context_status(self) -> Dict[str, Any]:
        """获取上下文管理状态"""
        if not self.context_manager:
            return {"status": "unavailable"}
        
        try:
            status = self.context_manager.get_status()
            status["status"] = "healthy"
            return status
        except Exception as e:
            logger.error(f"获取上下文状态失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def _get_scheduler_status(self) -> Dict[str, Any]:
        """获取任务调度状态"""
        if not self.scheduler:
            return {"status": "unavailable"}
        
        try:
            status = self.scheduler.get_status()
            status["status"] = "healthy" if status["running"] else "stopped"
            return status
        except Exception as e:
            logger.error(f"获取调度器状态失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def _get_gateway_status(self) -> Dict[str, Any]:
        """获取网关状态"""
        if not self.gateway:
            return {"status": "unavailable"}
        
        try:
            status = self.gateway.get_status()
            status["status"] = "healthy" if status["error_rate"] < 5 else "warning"
            return clean_inf_values(status)
        except Exception as e:
            logger.error(f"获取网关状态失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def _get_integration_status(self) -> Dict[str, Any]:
        """获取集成中心状态"""
        if not self.integration_center:
            return {"status": "unavailable"}
        
        try:
            status = self.integration_center.get_status()
            status["status"] = "healthy" if status["initialized"] else "initializing"
            return clean_inf_values(status)
        except Exception as e:
            logger.error(f"获取集成中心状态失败: {e}")
            return {"status": "error", "error": str(e)}
    
    def _generate_alerts(self, dashboard: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根据状态生成告警"""
        alerts = []
        
        # 系统资源告警
        system = dashboard["metrics"].get("system", {})
        if system.get("cpu", {}).get("status") == "critical":
            alerts.append({
                "level": "critical",
                "category": "system",
                "message": f"CPU使用率过高: {system['cpu']['percent']}%",
                "timestamp": datetime.now().isoformat()
            })
        
        if system.get("memory", {}).get("status") == "critical":
            alerts.append({
                "level": "critical",
                "category": "system",
                "message": f"内存使用率过高: {system['memory']['percent']}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # 缓存告警
        cache = dashboard["services"].get("cache", {})
        if cache.get("hit_rate", 100) < 80:
            alerts.append({
                "level": "warning",
                "category": "cache",
                "message": f"缓存命中率低于80%: {cache.get('hit_rate', 0)}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # 网关告警
        gateway = dashboard["services"].get("gateway", {})
        if gateway.get("error_rate", 0) > 5:
            alerts.append({
                "level": "warning",
                "category": "gateway",
                "message": f"网关错误率超过5%: {gateway.get('error_rate', 0)}%",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def get_summary(self) -> Dict[str, Any]:
        """获取监控摘要"""
        dashboard = self.get_dashboard_data()
        
        services = dashboard["services"]
        metrics = dashboard["metrics"]
        
        healthy_count = sum(1 for s in services.values() if s.get("status") == "healthy")
        total_count = len(services)
        
        return {
            "timestamp": dashboard["timestamp"],
            "health_score": round(healthy_count / total_count * 100, 0),
            "service_status": {
                "healthy": healthy_count,
                "total": total_count
            },
            "alerts_count": len(dashboard["alerts"]),
            "response_time": metrics.get("system", {}).get("response_time", {}).get("avg", "N/A"),
            "cpu": metrics.get("system", {}).get("cpu", {}).get("percent", "N/A"),
            "memory": metrics.get("system", {}).get("memory", {}).get("percent", "N/A")
        }


# 全局仪表盘实例
_dashboard = None

def get_dashboard() -> MonitoringDashboard:
    """获取全局监控仪表盘实例"""
    global _dashboard
    if _dashboard is None:
        _dashboard = MonitoringDashboard()
    return _dashboard


# FastAPI路由
from fastapi import APIRouter

router = APIRouter(prefix="/api/monitor", tags=["监控仪表盘"])

@router.get("/dashboard")
async def get_full_dashboard():
    """获取完整仪表盘数据"""
    dashboard = get_dashboard()
    return {"success": True, "data": dashboard.get_dashboard_data()}

@router.get("/summary")
async def get_monitor_summary():
    """获取监控摘要"""
    dashboard = get_dashboard()
    return {"success": True, "data": dashboard.get_summary()}

@router.get("/alerts")
async def get_alerts():
    """获取当前告警列表"""
    dashboard = get_dashboard()
    data = dashboard.get_dashboard_data()
    return {"success": True, "data": data.get("alerts", [])}

@router.get("/system")
async def get_system_metrics():
    """获取系统资源指标"""
    dashboard = get_dashboard()
    data = dashboard.get_dashboard_data()
    return {"success": True, "data": data.get("metrics", {}).get("system", {})}

@router.get("/services")
async def get_service_status():
    """获取所有服务状态"""
    dashboard = get_dashboard()
    data = dashboard.get_dashboard_data()
    return {"success": True, "data": data.get("services", {})}


if __name__ == "__main__":
    # 测试仪表盘
    dashboard = get_dashboard()
    
    print("=== 统一监控仪表盘测试 ===")
    print(f"\n摘要: {json.dumps(dashboard.get_summary(), indent=2, ensure_ascii=False)}")
    
    full_data = dashboard.get_dashboard_data()
    print(f"\n服务状态:")
    for service, status in full_data["services"].items():
        print(f"  {service}: {status.get('status', 'unknown')}")
    
    print(f"\n告警数量: {len(full_data['alerts'])}")
    if full_data["alerts"]:
        for alert in full_data["alerts"]:
            print(f"  [{alert['level']}] {alert['message']}")
    
    print("\n=== 测试完成 ===")