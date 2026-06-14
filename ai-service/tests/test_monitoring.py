#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控与告警单元测试
覆盖告警管理器、系统监控等核心功能
"""

import pytest
import time
from app.core.alert_manager import AlertLevel, AlertRule, Alert, AlertManager


class TestAlertLevel:
    """告警级别测试"""
    
    def test_alert_level_values(self):
        """测试告警级别值"""
        assert AlertLevel.INFO.value == "info"
        assert AlertLevel.WARNING.value == "warning"
        assert AlertLevel.ERROR.value == "error"
        assert AlertLevel.CRITICAL.value == "critical"
    
    def test_alert_level_order(self):
        """测试告警级别顺序"""
        levels = list(AlertLevel)
        assert levels[0] == AlertLevel.INFO
        assert levels[1] == AlertLevel.WARNING
        assert levels[2] == AlertLevel.ERROR
        assert levels[3] == AlertLevel.CRITICAL


class TestAlertRule:
    """告警规则测试"""
    
    def test_rule_initialization(self):
        """测试规则初始化"""
        rule = AlertRule(
            name="test_rule",
            condition=lambda: False,
            level=AlertLevel.WARNING,
            message="Test message",
            cooldown=60,
            aggregation_count=3
        )
        
        assert rule.name == "test_rule"
        assert rule.level == AlertLevel.WARNING
        assert rule.message == "Test message"
        assert rule.cooldown == 60
        assert rule.aggregation_count == 3
    
    def test_should_alert_immediate(self):
        """测试立即触发告警（无聚合）"""
        trigger_condition = [False, False, True]
        index = [0]
        
        def condition():
            result = trigger_condition[index[0]] if index[0] < len(trigger_condition) else False
            index[0] += 1
            return result
        
        rule = AlertRule(
            name="test_immediate",
            condition=condition,
            level=AlertLevel.ERROR,
            message="Error occurred",
            cooldown=0,
            aggregation_count=1
        )
        
        # 第一次检查：条件为False
        in_cooldown, should_alert = rule.should_alert()
        assert in_cooldown is True  # 不在冷却中
        assert should_alert is False
        
        # 第二次检查：条件为False
        in_cooldown, should_alert = rule.should_alert()
        assert should_alert is False
        
        # 第三次检查：条件为True，应该触发告警
        in_cooldown, should_alert = rule.should_alert()
        assert should_alert is True
    
    def test_alert_cooldown(self):
        """测试告警冷却机制"""
        rule = AlertRule(
            name="test_cooldown",
            condition=lambda: True,
            level=AlertLevel.WARNING,
            message="Warning",
            cooldown=2,
            aggregation_count=1
        )
        
        # 第一次触发
        in_cooldown, should_alert = rule.should_alert()
        assert should_alert is True
        rule.trigger()
        
        # 立即再次检查，应该在冷却中
        in_cooldown, should_alert = rule.should_alert()
        assert in_cooldown is False  # 在冷却中
        assert should_alert is False
        
        # 等待冷却结束
        time.sleep(2.1)
        
        # 冷却结束后可以再次触发
        in_cooldown, should_alert = rule.should_alert()
        assert in_cooldown is True
        assert should_alert is True
    
    def test_alert_aggregation(self):
        """测试告警聚合功能"""
        trigger_count = [0]
        
        def condition():
            trigger_count[0] += 1
            return True
        
        rule = AlertRule(
            name="test_aggregation",
            condition=condition,
            level=AlertLevel.ERROR,
            message="Aggregation test",
            cooldown=0,
            aggregation_window=60,
            aggregation_count=3
        )
        
        # 需要3次触发才告警
        in_cooldown, should_alert = rule.should_alert()
        assert should_alert is False  # 第1次
        
        in_cooldown, should_alert = rule.should_alert()
        assert should_alert is False  # 第2次
        
        in_cooldown, should_alert = rule.should_alert()
        assert should_alert is True   # 第3次，达到聚合阈值
    
    def test_rule_trigger(self):
        """测试触发告警后重置状态"""
        rule = AlertRule(
            name="test_trigger",
            condition=lambda: True,
            level=AlertLevel.INFO,
            message="Test",
            aggregation_count=2
        )
        
        # 触发两次以满足聚合条件
        rule.should_alert()
        rule.should_alert()
        
        # 触发告警
        rule.trigger()
        
        # 聚合历史应该被清空
        assert len(rule.trigger_history) == 0


class TestAlert:
    """告警信息测试"""
    
    def test_alert_initialization(self):
        """测试告警初始化"""
        alert = Alert(
            rule_name="test_rule",
            level=AlertLevel.WARNING,
            message="Test warning",
            metadata={"key": "value"}
        )
        
        assert alert.rule_name == "test_rule"
        assert alert.level == AlertLevel.WARNING
        assert alert.message == "Test warning"
        assert alert.metadata == {"key": "value"}
        assert alert.timestamp > 0


class TestAlertManager:
    """告警管理器测试"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.manager = AlertManager()
    
    def test_add_rule(self):
        """测试添加规则"""
        rule = AlertRule(
            name="test_rule",
            condition=lambda: False,
            level=AlertLevel.INFO,
            message="Test"
        )
        
        self.manager.add_rule(rule)
        assert rule in self.manager.rules
    
    def test_check_all(self):
        """测试检查所有规则"""
        trigger_flag = [True]
        
        def condition():
            return trigger_flag[0]
        
        rule = AlertRule(
            name="test_check",
            condition=condition,
            level=AlertLevel.WARNING,
            message="Test alert",
            aggregation_count=1
        )
        
        self.manager.add_rule(rule)
        alerts = self.manager.check_all()
        
        assert len(alerts) == 1
        assert alerts[0].rule_name == "test_check"
        assert alerts[0].level == AlertLevel.WARNING
    
    def test_get_recent_alerts(self):
        """测试获取最近的告警"""
        # 添加一些告警到历史
        alert1 = Alert(
            rule_name="rule1",
            level=AlertLevel.INFO,
            message="Info alert"
        )
        alert2 = Alert(
            rule_name="rule2",
            level=AlertLevel.ERROR,
            message="Error alert"
        )
        
        self.manager.alerts.append(alert1)
        self.manager.alerts.append(alert2)
        
        # 获取最近的告警
        alerts = self.manager.get_recent_alerts(minutes=60)
        assert len(alerts) == 2
    
    def test_clear_old_alerts(self):
        """测试清除旧告警"""
        # 添加一个旧告警（模拟100小时前）
        old_alert = Alert(
            rule_name="old_rule",
            level=AlertLevel.WARNING,
            message="Old alert",
            timestamp=time.time() - (100 * 3600)
        )
        self.manager.alerts.append(old_alert)
        
        # 添加一个新告警
        new_alert = Alert(
            rule_name="new_rule",
            level=AlertLevel.WARNING,
            message="New alert"
        )
        self.manager.alerts.append(new_alert)
        
        assert len(self.manager.alerts) == 2
        
        # 清除24小时前的告警
        self.manager.clear_old_alerts(hours=24)
        assert len(self.manager.alerts) == 1
        assert self.manager.alerts[0].rule_name == "new_rule"
    
    def test_get_stats(self):
        """测试获取统计信息"""
        stats = self.manager.get_stats()
        assert "total_triggers" in stats
        assert "rule_count" in stats
        assert "handler_count" in stats
    
    def test_alert_suppression(self):
        """测试告警抑制"""
        rule = AlertRule(
            name="suppress_rule",
            condition=lambda: True,
            level=AlertLevel.WARNING,
            message="Suppressed alert",
            aggregation_count=1
        )
        
        self.manager.add_rule(rule)
        
        # 第一次检查应该触发告警
        alerts1 = self.manager.check_all()
        assert len(alerts1) == 1
        
        # 抑制该规则10秒
        self.manager.suppress_alerts("suppress_rule", 10)
        
        # 在抑制期间不应该触发告警
        alerts2 = self.manager.check_all()
        assert len(alerts2) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])