"""告警管理器 - 增强版"""

import time
import logging
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import psutil

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertRule:
    """告警规则 - 增强版"""

    def __init__(
        self,
        name: str,
        condition: Callable[[], bool],
        level: AlertLevel,
        message: str,
        cooldown: int = 300,
        aggregation_window: int = 60,
        aggregation_count: int = 3
    ):
        """
        初始化告警规则
        
        Args:
            name: 规则名称
            condition: 告警条件函数
            level: 告警级别
            message: 告警消息
            cooldown: 冷却时间（秒）
            aggregation_window: 聚合窗口时间（秒）- 在该时间段内需要满足多次条件才触发
            aggregation_count: 聚合计数 - 需要满足条件的次数
        """
        self.name = name
        self.condition = condition
        self.level = level
        self.message = message
        self.cooldown = cooldown
        self.last_triggered = 0
        self.aggregation_window = aggregation_window
        self.aggregation_count = aggregation_count
        self.trigger_history = deque()  # 记录触发历史时间戳

    def _check_aggregation(self) -> bool:
        """检查聚合条件"""
        if self.aggregation_count <= 1:
            return True
        
        # 清理过期的历史记录
        cutoff = time.time() - self.aggregation_window
        while self.trigger_history and self.trigger_history[0] < cutoff:
            self.trigger_history.popleft()
        
        # 检查是否达到聚合计数
        return len(self.trigger_history) >= self.aggregation_count

    def should_alert(self) -> tuple:
        """检查是否应该告警 - 返回(是否在冷却中, 是否应该触发告警)"""
        in_cooldown = time.time() - self.last_triggered < self.cooldown
        if in_cooldown:
            return (False, False)
        
        # 调用条件函数
        triggered = self.condition()
        
        if triggered:
            # 记录触发时间
            self.trigger_history.append(time.time())
            # 检查聚合条件
            if self._check_aggregation():
                return (True, True)
        
        return (True, False)

    def trigger(self):
        """触发告警"""
        self.last_triggered = time.time()
        # 重置聚合历史
        self.trigger_history.clear()

@dataclass
class Alert:
    """告警信息"""
    rule_name: str
    level: AlertLevel
    message: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)

class AlertManager:
    """告警管理器 - 增强版"""

    def __init__(self):
        self.rules: List[AlertRule] = []
        self.alerts: List[Alert] = []
        self.handlers: List[Callable[[Alert], None]] = []
        # 告警统计
        self.stats = {
            "total_triggers": 0,
            "triggers_by_level": {
                "info": 0,
                "warning": 0,
                "error": 0,
                "critical": 0
            },
            "active_alerts": 0,
            "rules_checked": 0
        }
        # 告警抑制规则（用于避免告警风暴）
        self.suppression_rules: Dict[str, float] = {}

    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.rules.append(rule)
        logger.info(f"告警规则已添加: {rule.name}")

    def add_handler(self, handler: Callable[[Alert], None]):
        """添加告警处理器"""
        self.handlers.append(handler)
        logger.info("告警处理器已添加")

    def suppress_alerts(self, rule_name: str, duration: int):
        """
        抑制指定规则的告警
        
        Args:
            rule_name: 规则名称
            duration: 抑制时长（秒）
        """
        self.suppression_rules[rule_name] = time.time() + duration
        logger.info(f"告警规则 {rule_name} 已被抑制 {duration} 秒")

    def _is_suppressed(self, rule_name: str) -> bool:
        """检查规则是否被抑制"""
        end_time = self.suppression_rules.get(rule_name)
        if end_time and time.time() < end_time:
            return True
        # 清理过期的抑制规则
        if end_time and time.time() >= end_time:
            del self.suppression_rules[rule_name]
        return False

    def check_all(self) -> List[Alert]:
        """检查所有规则"""
        new_alerts = []
        self.stats["rules_checked"] += len(self.rules)
        
        for rule in self.rules:
            try:
                # 检查是否被抑制
                if self._is_suppressed(rule.name):
                    continue
                
                should_alert, triggered = rule.should_alert()
                if should_alert and triggered:
                    alert = Alert(
                        rule_name=rule.name,
                        level=rule.level,
                        message=rule.message
                    )
                    new_alerts.append(alert)
                    self.alerts.append(alert)
                    rule.trigger()
                    
                    # 更新统计
                    self.stats["total_triggers"] += 1
                    self.stats["triggers_by_level"][rule.level.value] += 1
                    self.stats["active_alerts"] = len(self.get_recent_alerts(60))
                    
                    # 通知所有处理器
                    for handler in self.handlers:
                        try:
                            handler(alert)
                        except Exception as e:
                            logger.error(f"告警处理器执行失败: {e}")
            except Exception as e:
                logger.error(f"告警规则检查失败 {rule.name}: {e}")
        
        return new_alerts

    def get_recent_alerts(self, minutes: int = 60) -> List[Alert]:
        """获取最近的告警"""
        cutoff = time.time() - (minutes * 60)
        return [a for a in self.alerts if a.timestamp > cutoff]

    def clear_old_alerts(self, hours: int = 24):
        """清除旧告警"""
        cutoff = time.time() - (hours * 3600)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff]

    def get_stats(self) -> Dict:
        """获取告警统计信息"""
        return {
            **self.stats,
            "rule_count": len(self.rules),
            "handler_count": len(self.handlers),
            "suppressed_rules": len(self.suppression_rules),
            "total_alerts": len(self.alerts)
        }

    def get_status(self) -> Dict:
        """获取告警管理器状态"""
        recent_alerts = self.get_recent_alerts(5)
        critical_alerts = [a for a in recent_alerts if a.level == AlertLevel.CRITICAL]
        
        return {
            "status": "healthy" if not critical_alerts else "critical",
            "recent_alerts_count": len(recent_alerts),
            "critical_alerts_count": len(critical_alerts),
            "stats": self.get_stats()
        }

# 全局告警管理器
alert_manager = AlertManager()

def get_alert_manager() -> AlertManager:
    """获取告警管理器"""
    return alert_manager

def init_alert_rules():
    """初始化告警规则 - 增强版"""
    manager = get_alert_manager()

    # CPU使用率告警（带聚合检测，避免误报）
    manager.add_rule(AlertRule(
        name="high_cpu",
        condition=lambda: psutil.cpu_percent(interval=0.5) > 85,
        level=AlertLevel.WARNING,
        message="CPU使用率超过85%",
        cooldown=300,
        aggregation_window=60,
        aggregation_count=3
    ))

    # CPU使用率严重告警
    manager.add_rule(AlertRule(
        name="critical_cpu",
        condition=lambda: psutil.cpu_percent(interval=0.5) > 95,
        level=AlertLevel.CRITICAL,
        message="CPU使用率超过95%，系统负载过高",
        cooldown=120
    ))

    # 内存使用率告警
    manager.add_rule(AlertRule(
        name="high_memory",
        condition=lambda: psutil.virtual_memory().percent > 85,
        level=AlertLevel.WARNING,
        message="内存使用率超过85%",
        cooldown=300,
        aggregation_window=120,
        aggregation_count=5
    ))

    # 内存使用率严重告警
    manager.add_rule(AlertRule(
        name="critical_memory",
        condition=lambda: psutil.virtual_memory().percent > 95,
        level=AlertLevel.CRITICAL,
        message="内存使用率超过95%，系统可能面临内存不足",
        cooldown=60
    ))

    # 磁盘使用率告警
    manager.add_rule(AlertRule(
        name="high_disk",
        condition=lambda: psutil.disk_usage('/').percent > 85,
        level=AlertLevel.WARNING,
        message="磁盘使用率超过85%",
        cooldown=600
    ))

    # 磁盘使用率严重告警
    manager.add_rule(AlertRule(
        name="critical_disk",
        condition=lambda: psutil.disk_usage('/').percent > 95,
        level=AlertLevel.CRITICAL,
        message="磁盘使用率超过95%，请及时清理空间",
        cooldown=300
    ))

    # Redis连接失败告警
    def check_redis():
        try:
            import redis
            from app.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, socket_timeout=2)
            r.ping()
            return False
        except Exception as e:
            logger.warning(f"Redis检查失败: {e}")
            return True

    manager.add_rule(AlertRule(
        name="redis_down",
        condition=check_redis,
        level=AlertLevel.ERROR,
        message="Redis服务不可用",
        cooldown=300,
        aggregation_window=60,
        aggregation_count=2
    ))

    # 服务响应慢告警
    def check_slow_response():
        try:
            import requests
            start = time.time()
            r = requests.get('http://localhost:8001/health', timeout=10)
            duration = time.time() - start
            return duration > 3.0
        except Exception as e:
            logger.warning(f"服务响应检查失败: {e}")
            return False

    manager.add_rule(AlertRule(
        name="slow_response",
        condition=check_slow_response,
        level=AlertLevel.WARNING,
        message="服务响应时间超过3秒",
        cooldown=300,
        aggregation_window=60,
        aggregation_count=3
    ))

    # 网络连接检查
    def check_network():
        try:
            import requests
            requests.get('https://www.baidu.com', timeout=5)
            return False
        except Exception as e:
            logger.warning(f"网络连接检查失败: {e}")
            return True

    manager.add_rule(AlertRule(
        name="network_unavailable",
        condition=check_network,
        level=AlertLevel.WARNING,
        message="网络连接异常",
        cooldown=300,
        aggregation_window=60,
        aggregation_count=2
    ))

    logger.info("告警规则初始化完成")

def setup_alert_handlers():
    """设置告警处理器 - 增强版"""
    manager = get_alert_manager()

    # 控制台输出处理器
    def console_handler(alert: Alert):
        level_icons = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }
        icon = level_icons.get(alert.level, "📢")
        print(f"{icon} [{alert.level.value.upper()}] {alert.message}")

    manager.add_handler(console_handler)

    # 日志记录处理器
    def log_handler(alert: Alert):
        level_loggers = {
            AlertLevel.INFO: logger.info,
            AlertLevel.WARNING: logger.warning,
            AlertLevel.ERROR: logger.error,
            AlertLevel.CRITICAL: logger.critical
        }
        log_func = level_loggers.get(alert.level, logger.info)
        log_func(f"[ALERT] {alert.rule_name}: {alert.message}")

    manager.add_handler(log_handler)

    # 文件记录处理器
    def file_handler(alert: Alert):
        try:
            log_dir = "/tmp/alerts"
            import os
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"alerts_{time.strftime('%Y-%m-%d')}.log")
            with open(log_file, "a", encoding="utf-8") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] [{alert.level.value}] {alert.rule_name}: {alert.message}\n")
        except Exception as e:
            logger.error(f"告警文件写入失败: {e}")

    manager.add_handler(file_handler)

    logger.info("告警处理器设置完成")
