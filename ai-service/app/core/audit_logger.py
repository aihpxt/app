"""审计日志模块"""

import json
import os
import gzip
import shutil
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from functools import wraps
import hashlib
import asyncio
from pathlib import Path

class AuditLevel(Enum):
    """审计级别"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AuditAction(Enum):
    """审计操作类型"""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    API_ACCESS = "API_ACCESS"
    DATA_CREATE = "DATA_CREATE"
    DATA_UPDATE = "DATA_UPDATE"
    DATA_DELETE = "DATA_DELETE"
    CONFIG_CHANGE = "CONFIG_CHANGE"
    SECURITY_EVENT = "SECURITY_EVENT"
    SYSTEM_EVENT = "SYSTEM_EVENT"

class AuditLogger:
    """审计日志记录器"""

    def __init__(self, log_dir: str = "logs/audit", retention_days: int = 90):
        self.log_dir = log_dir
        self.retention_days = retention_days
        os.makedirs(log_dir, exist_ok=True)
        self.current_date = datetime.now().strftime("%Y%m%d")
        self.log_file = os.path.join(log_dir, f"audit_{self.current_date}.log")
        self.alert_handlers = []

    def _rotate_log(self):
        """日志轮转"""
        new_date = datetime.now().strftime("%Y%m%d")
        if new_date != self.current_date:
            self.current_date = new_date
            self.log_file = os.path.join(self.log_dir, f"audit_{self.current_date}.log")

    def _hash_sensitive_data(self, data: str) -> str:
        """对敏感数据脱敏"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def log(
        self,
        action: AuditAction,
        level: AuditLevel,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "SUCCESS"
    ):
        """记录审计日志"""
        self._rotate_log()

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action.value,
            "level": level.value,
            "user_id": self._hash_sensitive_data(user_id) if user_id else None,
            "resource": resource,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "status": status,
            "event_id": self._generate_event_id()
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def _generate_event_id(self) -> str:
        """生成事件ID"""
        timestamp = datetime.now().timestamp()
        return hashlib.md5(f"{timestamp}".encode()).hexdigest()[:12]

    def query_logs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        action: Optional[AuditAction] = None,
        user_id: Optional[str] = None,
        level: Optional[AuditLevel] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """查询审计日志"""
        logs = []

        if start_date and end_date:
            date_range = self._date_range(start_date, end_date)
        else:
            date_range = [self.current_date]

        for date in date_range:
            log_file = os.path.join(self.log_dir, f"audit_{date}.log")
            if not os.path.exists(log_file):
                continue

            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())

                        if action and entry["action"] != action.value:
                            continue
                        if level and entry["level"] != level.value:
                            continue
                        if user_id and entry.get("user_id") != self._hash_sensitive_data(user_id):
                            continue

                        logs.append(entry)

                        if len(logs) >= limit:
                            break

                    except json.JSONDecodeError:
                        continue

        return logs

    def _date_range(self, start: str, end: str) -> List[str]:
        """生成日期范围"""
        from datetime import datetime, timedelta
        start_dt = datetime.strptime(start, "%Y%m%d")
        end_dt = datetime.strptime(end, "%Y%m%d")

        dates = []
        current = start_dt
        while current <= end_dt:
            dates.append(current.strftime("%Y%m%d"))
            current += timedelta(days=1)

        return dates

    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取审计统计信息"""
        stats = {
            "total_events": 0,
            "by_action": {},
            "by_level": {},
            "by_status": {},
            "unique_users": set(),
            "recent_events": []
        }

        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y%m%d")
            log_file = os.path.join(self.log_dir, f"audit_{date_str}.log")

            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            stats["total_events"] += 1

                            action = entry.get("action", "UNKNOWN")
                            stats["by_action"][action] = stats["by_action"].get(action, 0) + 1

                            level = entry.get("level", "UNKNOWN")
                            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1

                            status = entry.get("status", "UNKNOWN")
                            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

                            if entry.get("user_id"):
                                stats["unique_users"].add(entry["user_id"])

                        except json.JSONDecodeError:
                            continue

            current += timedelta(days=1)

        stats["unique_users"] = len(stats["unique_users"])
        return stats

    def compress_old_logs(self, days_old: int = 7):
        """压缩旧日志文件"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cutoff_str = cutoff_date.strftime("%Y%m%d")

        for filename in os.listdir(self.log_dir):
            if filename.endswith(".log") and not filename.endswith(".gz"):
                date_str = filename.replace("audit_", "").replace(".log", "")
                if date_str < cutoff_str:
                    log_path = os.path.join(self.log_dir, filename)
                    gz_path = f"{log_path}.gz"

                    if not os.path.exists(gz_path):
                        with open(log_path, "rb") as f_in:
                            with gzip.open(gz_path, "wb") as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        os.remove(log_path)
                        print(f"已压缩日志: {filename}")

    def cleanup_old_logs(self):
        """清理过期日志文件"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        cutoff_str = cutoff_date.strftime("%Y%m%d")

        for filename in os.listdir(self.log_dir):
            if filename.startswith("audit_"):
                if filename.endswith(".log"):
                    date_str = filename.replace("audit_", "").replace(".log", "")
                elif filename.endswith(".log.gz"):
                    date_str = filename.replace("audit_", "").replace(".log.gz", "")
                else:
                    continue

                if date_str < cutoff_str:
                    file_path = os.path.join(self.log_dir, filename)
                    os.remove(file_path)
                    print(f"已清理过期日志: {filename}")

    def register_alert_handler(self, handler):
        """注册告警处理器"""
        self.alert_handlers.append(handler)

    def _trigger_alerts(self, log_entry):
        """触发告警"""
        for handler in self.alert_handlers:
            try:
                handler(log_entry)
            except Exception as e:
                print(f"告警处理失败: {e}")

    def log(
        self,
        action: AuditAction,
        level: AuditLevel,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "SUCCESS"
    ):
        """记录审计日志（重写以支持告警）"""
        self._rotate_log()

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action.value,
            "level": level.value,
            "user_id": self._hash_sensitive_data(user_id) if user_id else None,
            "resource": resource,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "status": status,
            "event_id": self._generate_event_id()
        }

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        if level in (AuditLevel.ERROR, AuditLevel.CRITICAL):
            self._trigger_alerts(log_entry)

    async def async_log(
        self,
        action: AuditAction,
        level: AuditLevel,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "SUCCESS"
    ):
        """异步记录审计日志"""
        await asyncio.to_thread(
            self.log,
            action=action,
            level=level,
            user_id=user_id,
            resource=resource,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )

    def export_logs(self, output_path: str, start_date: str, end_date: str):
        """导出日志到文件"""
        logs = self.query_logs(start_date=start_date, end_date=end_date)
        
        output_filename = f"audit_export_{start_date}_{end_date}.json"
        full_path = os.path.join(output_path, output_filename)
        
        os.makedirs(output_path, exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        
        return full_path


def audit_log(
    action: AuditAction,
    resource: str,
    level: AuditLevel = AuditLevel.INFO
):
    """审计日志装饰器"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id") or (args[0] if args else None)
            result = await func(*args, **kwargs)

            await audit_logger.async_log(
                action=action,
                level=level,
                user_id=str(user_id) if user_id else None,
                resource=resource,
                details={"function": func.__name__},
                status="SUCCESS"
            )

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id") or (args[0] if args else None)
            result = func(*args, **kwargs)

            audit_logger.log(
                action=action,
                level=level,
                user_id=str(user_id) if user_id else None,
                resource=resource,
                details={"function": func.__name__},
                status="SUCCESS"
            )

            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def create_console_alert_handler():
    """创建控制台告警处理器"""
    def handler(log_entry):
        timestamp = log_entry.get("timestamp", "")
        level = log_entry.get("level", "")
        action = log_entry.get("action", "")
        event_id = log_entry.get("event_id", "")
        
        print(f"[ALERT] {level} - {action} - {event_id} - {timestamp}")
    
    return handler


audit_logger = AuditLogger()
audit_logger.register_alert_handler(create_console_alert_handler())
