"""时间和日期工具"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import time

class TimeUtils:
    """时间工具"""

    @staticmethod
    def get_current_time() -> datetime:
        """获取当前时间"""
        return datetime.now()

    @staticmethod
    def get_timestamp() -> float:
        """获取时间戳"""
        return time.time()

    @staticmethod
    def format_datetime(dt: Optional[datetime] = None, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """格式化时间"""
        if dt is None:
            dt = datetime.now()
        return dt.strftime(format)

    @staticmethod
    def parse_datetime(date_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
        """解析时间字符串"""
        try:
            return datetime.strptime(date_str, format)
        except ValueError:
            return None

    @staticmethod
    def get_relative_time(dt: datetime) -> str:
        """获取相对时间描述"""
        now = datetime.now()
        diff = now - dt

        seconds = diff.total_seconds()

        if seconds < 60:
            return f"{int(seconds)}秒前"
        elif seconds < 3600:
            return f"{int(seconds / 60)}分钟前"
        elif seconds < 86400:
            return f"{int(seconds / 3600)}小时前"
        elif seconds < 604800:
            return f"{int(seconds / 86400)}天前"
        else:
            return dt.strftime("%Y-%m-%d")

    @staticmethod
    def get_date_range(days: int) -> Tuple[datetime, datetime]:
        """获取日期范围"""
        end = datetime.now()
        start = end - timedelta(days=days)
        return start, end

    @staticmethod
    def is_today(dt: datetime) -> bool:
        """是否是今天"""
        today = datetime.now().date()
        return dt.date() == today

    @staticmethod
    def is_this_week(dt: datetime) -> bool:
        """是否是本周"""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=6)
        return week_start.date() <= dt.date() <= week_end.date()

    @staticmethod
    def is_this_month(dt: datetime) -> bool:
        """是否是本月"""
        now = datetime.now()
        return dt.year == now.year and dt.month == now.month

    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """添加天数"""
        return dt + timedelta(days=days)

    @staticmethod
    def add_hours(dt: datetime, hours: int) -> datetime:
        """添加小时"""
        return dt + timedelta(hours=hours)

    @staticmethod
    def add_minutes(dt: datetime, minutes: int) -> datetime:
        """添加分钟"""
        return dt + timedelta(minutes=minutes)

    @staticmethod
    def get_days_between(start: datetime, end: datetime) -> int:
        """计算两天之间的天数"""
        return (end.date() - start.date()).days

# 全局时间工具实例
_time_utils = TimeUtils()

def get_time_utils() -> TimeUtils:
    """获取时间工具实例"""
    return _time_utils
