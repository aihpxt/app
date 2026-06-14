#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能提醒服务
支持中考相关日期提醒、学习计划提醒等
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from enum import Enum

logger = logging.getLogger(__name__)


class ReminderType(Enum):
    """提醒类型"""
    EXAM_DATE = 'exam_date'
    REGISTRATION = 'registration'
    VOLUNTEER_FILLING = 'volunteer_filling'
    STUDY_PLAN = 'study_plan'
    DAILY_REVIEW = 'daily_review'
    WEEKLY_CHECK = 'weekly_check'


class IntelligentReminder:
    """智能提醒服务"""
    
    def __init__(self):
        self._reminders = {}
        self._default_dates = self._load_default_dates()
        logger.info("智能提醒服务初始化完成")
    
    def _load_default_dates(self) -> Dict[str, str]:
        """加载默认日期配置"""
        return {
            'exam_date': '2026-06-20',  # 中考日期
            'registration_start': '2026-11-15',  # 报名开始
            'registration_end': '2026-11-30',  # 报名结束
            'volunteer_start': '2026-06-25',  # 志愿填报开始
            'volunteer_end': '2026-06-30',  # 志愿填报结束
            'results_release': '2026-07-15'  # 成绩公布
        }
    
    def set_reminder(self, user_id: str, reminder_type: str, date: str, message: str = None) -> bool:
        """
        设置提醒
        
        Args:
            user_id: 用户ID
            reminder_type: 提醒类型
            date: 提醒日期 (YYYY-MM-DD)
            message: 自定义消息
        
        Returns:
            是否设置成功
        """
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            logger.error(f"无效日期格式: {date}")
            return False
        
        if user_id not in self._reminders:
            self._reminders[user_id] = []
        
        reminder = {
            'type': reminder_type,
            'date': date,
            'message': message or self._get_default_message(reminder_type, date),
            'created_at': datetime.now().isoformat(),
            'enabled': True
        }
        
        self._reminders[user_id].append(reminder)
        logger.info(f"设置提醒成功: {user_id} - {reminder_type} - {date}")
        return True
    
    def _get_default_message(self, reminder_type: str, date: str) -> str:
        """获取默认提醒消息"""
        messages = {
            'exam_date': f"距离中考还有 {self._get_days_until(date)} 天！请继续努力备考！",
            'registration': f"中考报名将于{date}开始，请提前准备相关材料！",
            'volunteer_filling': f"志愿填报将于{date}开始，请提前做好准备！",
            'study_plan': "今天的学习计划已更新，请查看！",
            'daily_review': "该进行每日复习了，记得完成今天的学习任务！",
            'weekly_check': "本周学习总结已生成，请查看！"
        }
        return messages.get(reminder_type, f"提醒：{date}")
    
    def _get_days_until(self, date_str: str) -> int:
        """计算距离指定日期还有多少天"""
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
            today = datetime.now().date()
            delta = target_date.date() - today
            return max(0, delta.days)
        except:
            return 0
    
    def get_active_reminders(self, user_id: str) -> List[Dict]:
        """获取用户的所有活动提醒"""
        if user_id not in self._reminders:
            return []
        
        return [r for r in self._reminders[user_id] if r.get('enabled', True)]
    
    def get_today_reminders(self, user_id: str) -> List[Dict]:
        """获取用户今天的提醒"""
        today = datetime.now().strftime('%Y-%m-%d')
        return [r for r in self.get_active_reminders(user_id) if r['date'] == today]
    
    def get_upcoming_reminders(self, user_id: str, days: int = 7) -> List[Dict]:
        """获取未来几天的提醒"""
        result = []
        today = datetime.now().date()
        
        for reminder in self.get_active_reminders(user_id):
            try:
                reminder_date = datetime.strptime(reminder['date'], '%Y-%m-%d').date()
                delta = reminder_date - today
                if 0 <= delta.days <= days:
                    reminder['days_until'] = delta.days
                    result.append(reminder)
            except:
                pass
        
        # 按日期排序
        result.sort(key=lambda x: x['date'])
        return result
    
    def disable_reminder(self, user_id: str, reminder_index: int) -> bool:
        """禁用提醒"""
        if user_id not in self._reminders:
            return False
        
        if 0 <= reminder_index < len(self._reminders[user_id]):
            self._reminders[user_id][reminder_index]['enabled'] = False
            return True
        
        return False
    
    def clear_reminders(self, user_id: str):
        """清除用户所有提醒"""
        if user_id in self._reminders:
            del self._reminders[user_id]
    
    def get_exam_countdown(self) -> str:
        """获取中考倒计时"""
        exam_date = self._default_dates.get('exam_date')
        days = self._get_days_until(exam_date)
        
        if days == 0:
            return "🎉 今天就是中考！祝你考试顺利！"
        elif days < 0:
            return f"中考已于{exam_date}结束，祝你取得好成绩！"
        elif days == 1:
            return "⏰ 明天就是中考了！好好休息，放松心态！"
        elif days <= 7:
            return f"🔥 距离中考还有{days}天！最后冲刺阶段，加油！"
        elif days <= 30:
            return f"📚 距离中考还有{days}天！保持节奏，稳步前进！"
        elif days <= 60:
            return f"⏳ 距离中考还有{days}天！制定计划，高效复习！"
        else:
            return f"📅 距离中考还有{days}天！打好基础，循序渐进！"
    
    def generate_study_reminder(self, user_profile: Dict) -> Optional[str]:
        """生成个性化学习提醒"""
        if not user_profile:
            return None
        
        score = user_profile.get('score')
        grade = user_profile.get('grade')
        district = user_profile.get('district')
        
        reminders = []
        
        # 根据分数给出提醒
        if score:
            if score < 500:
                reminders.append("基础薄弱，建议从课本基础知识开始复习！")
            elif score < 550:
                reminders.append("成绩中等，重点突破薄弱科目！")
            elif score < 580:
                reminders.append("成绩良好，继续保持，冲刺重点高中！")
            else:
                reminders.append("成绩优秀，保持状态，挑战更高目标！")
        
        # 根据年级给出提醒
        if grade == '九年级':
            reminders.append("九年级是关键时期，制定合理的学习计划很重要！")
        elif grade == '八年级':
            reminders.append("八年级是打基础的好时机，不要松懈！")
        
        if reminders:
            return "💡 学习提醒：" + " ".join(reminders)
        
        return None


# 全局实例
reminder_service = IntelligentReminder()


def get_reminder_service() -> IntelligentReminder:
    """获取智能提醒服务实例"""
    return reminder_service


if __name__ == '__main__':
    # 测试智能提醒服务
    print("=" * 70)
    print("智能提醒服务测试")
    print("=" * 70)
    
    reminder = IntelligentReminder()
    
    # 测试倒计时
    print("\n📅 中考倒计时:")
    print(reminder.get_exam_countdown())
    
    # 测试设置提醒
    print("\n🔔 设置提醒:")
    user_id = "test_user_001"
    
    reminder.set_reminder(user_id, 'exam_date', '2026-06-20')
    reminder.set_reminder(user_id, 'registration', '2026-11-15')
    reminder.set_reminder(user_id, 'volunteer_filling', '2026-06-25')
    
    print("提醒设置成功！")
    
    # 测试获取即将到来的提醒
    print("\n📋 未来7天的提醒:")
    upcoming = reminder.get_upcoming_reminders(user_id, days=30)
    for r in upcoming:
        days = r.get('days_until', 0)
        print(f"• {r['date']} ({days}天后) - {r['message'][:50]}...")
    
    # 测试个性化学习提醒
    print("\n💡 个性化学习提醒:")
    user_profile = {
        'score': 580,
        'grade': '九年级',
        'district': '五华区'
    }
    study_reminder = reminder.generate_study_reminder(user_profile)
    print(study_reminder)
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)