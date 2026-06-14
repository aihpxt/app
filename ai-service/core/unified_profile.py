#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户画像统一
整合各渠道的用户信息，构建统一用户画像
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from collections import defaultdict

from data.unified_data_access import get_unified_data_access

logger = logging.getLogger(__name__)


class UnifiedUserProfile:
    """统一用户画像"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.data_access = get_unified_data_access()
        self.profile = self._build_profile()
    
    def _build_profile(self) -> Dict[str, Any]:
        """构建用户画像"""
        profile = {
            'user_id': self.user_id,
            'basic_info': self._get_basic_info(),
            'channels': self._get_channel_info(),
            'activities': self._get_activities(),
            'preferences': self._get_preferences(),
            'interactions': self._get_interactions(),
            'tags': self._generate_tags(),
            'score': self._calculate_score(),
            'updated_at': datetime.now().isoformat()
        }
        
        return profile
    
    def _get_basic_info(self) -> Dict[str, Any]:
        """获取基本信息"""
        # 从用户数据库获取基本信息
        user_info = self.data_access.get_user_info(self.user_id)
        
        if user_info:
            return {
                'name': user_info.get('name', ''),
                'phone': user_info.get('phone', self.user_id),
                'email': user_info.get('email', ''),
                'grade': user_info.get('grade', ''),
                'city': user_info.get('city', ''),
                'school': user_info.get('school', ''),
                'created_at': user_info.get('created_at', '')
            }
        
        return {
            'phone': self.user_id,
            'created_at': datetime.now().isoformat()
        }
    
    def _get_channel_info(self) -> Dict[str, Any]:
        """获取渠道信息"""
        channels = defaultdict(lambda: {
            'first_seen': None,
            'last_seen': None,
            'interaction_count': 0,
            'total_duration': 0
        })
        
        # 获取用户活动
        activities = self.data_access.execute_query(
            "SELECT * FROM user_activities WHERE user_id = ?",
            (self.user_id,)
        )
        
        for activity in activities:
            channel = activity.get('channel', 'unknown')
            timestamp = activity.get('timestamp')
            
            if channels[channel]['first_seen'] is None:
                channels[channel]['first_seen'] = timestamp
            
            channels[channel]['last_seen'] = timestamp
            channels[channel]['interaction_count'] += 1
            
            # 如果是通话记录，累加时长
            if activity.get('activity_type') == 'phone_call':
                content = json.loads(activity.get('content', '{}'))
                duration = content.get('duration', 0)
                channels[channel]['total_duration'] += duration
        
        return dict(channels)
    
    def _get_activities(self) -> List[Dict[str, Any]]:
        """获取活动记录"""
        activities = self.data_access.execute_query(
            "SELECT * FROM user_activities WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50",
            (self.user_id,)
        )
        
        return activities
    
    def _get_preferences(self) -> Dict[str, Any]:
        """获取偏好信息"""
        preferences = {
            'favorite_schools': [],
            'interested_topics': [],
            'communication_preference': 'web',
            'active_hours': []
        }
        
        # 获取收藏的学校
        favorites = self.data_access.get_favorites(self.user_id)
        preferences['favorite_schools'] = [
            {
                'school_id': fav.get('school_id'),
                'school_name': fav.get('school_name'),
                'added_at': fav.get('created_at')
            }
            for fav in favorites
        ]
        
        # 分析活动记录，提取偏好
        activities = self._get_activities()
        
        # 统计感兴趣的话题
        topic_counts = defaultdict(int)
        for activity in activities:
            content = activity.get('content', '')
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except:
                    pass
            
            # 根据活动类型判断话题
            activity_type = activity.get('activity_type')
            if activity_type == 'school_query':
                topic_counts['school_info'] += 1
            elif activity_type == 'agent_interaction':
                topic_counts['consultation'] += 1
            elif activity_type == 'phone_call':
                topic_counts['phone_consultation'] += 1
        
        # 取前3个话题
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        preferences['interested_topics'] = [topic for topic, count in sorted_topics[:3]]
        
        # 分析活跃时段
        hour_counts = defaultdict(int)
        for activity in activities:
            timestamp = activity.get('timestamp')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    hour_counts[dt.hour] += 1
                except:
                    pass
        
        # 取活跃时段
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        preferences['active_hours'] = [hour for hour, count in sorted_hours[:3]]
        
        # 确定沟通偏好
        channel_info = self._get_channel_info()
        if 'phone' in channel_info and channel_info['phone']['interaction_count'] > 0:
            preferences['communication_preference'] = 'phone'
        elif 'wechat' in channel_info and channel_info['wechat']['interaction_count'] > 0:
            preferences['communication_preference'] = 'wechat'
        
        return preferences
    
    def _get_interactions(self) -> Dict[str, Any]:
        """获取交互统计"""
        interactions = {
            'total_interactions': 0,
            'by_channel': defaultdict(int),
            'by_type': defaultdict(int),
            'by_agent': defaultdict(int),
            'avg_response_time': 0
        }
        
        activities = self._get_activities()
        
        for activity in activities:
            channel = activity.get('channel', 'unknown')
            activity_type = activity.get('activity_type', 'unknown')
            
            interactions['total_interactions'] += 1
            interactions['by_channel'][channel] += 1
            interactions['by_type'][activity_type] += 1
            
            # 如果是智能体交互，记录智能体
            if activity_type == 'agent_interaction':
                content = activity.get('content', '')
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                        agent = content.get('agent')
                        if agent:
                            interactions['by_agent'][agent] += 1
                    except:
                        pass
        
        # 转换为普通字典
        interactions['by_channel'] = dict(interactions['by_channel'])
        interactions['by_type'] = dict(interactions['by_type'])
        interactions['by_agent'] = dict(interactions['by_agent'])
        
        return interactions
    
    def _generate_tags(self) -> List[str]:
        """生成用户标签"""
        tags = []
        
        # 基于基本信息生成标签
        basic_info = self._get_basic_info()
        if basic_info.get('grade'):
            tags.append(f"{basic_info['grade']}年级")
        
        if basic_info.get('city'):
            tags.append(f"{basic_info['city']}用户")
        
        # 基于渠道生成标签
        channels = self._get_channel_info()
        if 'phone' in channels and channels['phone']['interaction_count'] > 5:
            tags.append('电话咨询用户')
        if 'wechat' in channels and channels['wechat']['interaction_count'] > 5:
            tags.append('微信活跃用户')
        if 'web' in channels and channels['web']['interaction_count'] > 10:
            tags.append('网站活跃用户')
        
        # 基于偏好生成标签
        preferences = self._get_preferences()
        if len(preferences.get('favorite_schools', [])) > 3:
            tags.append('择校积极用户')
        
        if 'consultation' in preferences.get('interested_topics', []):
            tags.append('咨询需求用户')
        
        # 基于交互生成标签
        interactions = self._get_interactions()
        if interactions['total_interactions'] > 20:
            tags.append('高频互动用户')
        
        return tags
    
    def _calculate_score(self) -> float:
        """计算用户评分"""
        score = 0.0
        
        # 基础分（注册即得）
        score += 10.0
        
        # 互动分
        interactions = self._get_interactions()
        score += min(interactions['total_interactions'] * 0.5, 30.0)
        
        # 渠道分
        channels = self._get_channel_info()
        channel_count = len([c for c in channels.values() if c['interaction_count'] > 0])
        score += channel_count * 5.0
        
        # 偏好分
        preferences = self._get_preferences()
        if len(preferences.get('favorite_schools', [])) > 0:
            score += 5.0
        
        # 活跃度分
        if interactions['total_interactions'] > 10:
            score += 10.0
        
        # 限制最高分
        return min(score, 100.0)
    
    def update_profile(self, update_data: Dict[str, Any]):
        """更新用户画像"""
        # 更新基本信息
        if 'basic_info' in update_data:
            basic_info = update_data['basic_info']
            self.data_access.execute_update(
                "UPDATE users SET name=?, email=?, grade=?, city=?, school=? WHERE phone=?",
                (
                    basic_info.get('name'),
                    basic_info.get('email'),
                    basic_info.get('grade'),
                    basic_info.get('city'),
                    basic_info.get('school'),
                    self.user_id
                )
            )
        
        # 重新构建画像
        self.profile = self._build_profile()
    
    def get_profile(self) -> Dict[str, Any]:
        """获取用户画像"""
        return self.profile
    
    def get_summary(self) -> Dict[str, Any]:
        """获取画像摘要"""
        return {
            'user_id': self.user_id,
            'name': self.profile['basic_info'].get('name', ''),
            'grade': self.profile['basic_info'].get('grade', ''),
            'city': self.profile['basic_info'].get('city', ''),
            'tags': self.profile['tags'],
            'score': self.profile['score'],
            'total_interactions': self.profile['interactions']['total_interactions'],
            'favorite_schools_count': len(self.profile['preferences']['favorite_schools']),
            'updated_at': self.profile['updated_at']
        }


class UserProfileManager:
    """用户画像管理器"""
    
    def __init__(self):
        self.data_access = get_unified_data_access()
        self.profiles = {}
    
    def get_profile(self, user_id: str) -> UnifiedUserProfile:
        """获取用户画像"""
        if user_id not in self.profiles:
            self.profiles[user_id] = UnifiedUserProfile(user_id)
        
        return self.profiles[user_id]
    
    def update_profile(self, user_id: str, update_data: Dict[str, Any]):
        """更新用户画像"""
        profile = self.get_profile(user_id)
        profile.update_profile(update_data)
        
        logger.info(f"Profile updated for user {user_id}")
    
    def get_profile_summary(self, user_id: str) -> Dict[str, Any]:
        """获取画像摘要"""
        profile = self.get_profile(user_id)
        return profile.get_summary()
    
    def search_profiles(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """搜索用户画像"""
        # 这里应该实现更复杂的搜索逻辑
        # 目前返回所有用户
        users = self.data_access.execute_query("SELECT DISTINCT user_id FROM user_activities")
        
        results = []
        for user in users[:10]:  # 限制返回数量
            user_id = user.get('user_id')
            summary = self.get_profile_summary(user_id)
            results.append(summary)
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        # 获取所有用户
        users = self.data_access.execute_query("SELECT DISTINCT user_id FROM user_activities")
        total_users = len(users)
        
        # 计算平均评分
        total_score = 0
        score_count = 0
        
        for user in users:
            user_id = user.get('user_id')
            profile = self.get_profile(user_id)
            total_score += profile.get_score()
            score_count += 1
        
        avg_score = total_score / score_count if score_count > 0 else 0
        
        # 统计标签
        tag_counts = defaultdict(int)
        for user in users:
            user_id = user.get('user_id')
            profile = self.get_profile(user_id)
            for tag in profile.get_tags():
                tag_counts[tag] += 1
        
        return {
            'total_users': total_users,
            'avg_score': round(avg_score, 2),
            'top_tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'timestamp': datetime.now().isoformat()
        }


# 全局实例
_user_profile_manager = None


def get_user_profile_manager() -> UserProfileManager:
    """获取用户画像管理器实例（单例）"""
    global _user_profile_manager
    if _user_profile_manager is None:
        _user_profile_manager = UserProfileManager()
    return _user_profile_manager


if __name__ == '__main__':
    # 测试用户画像统一
    manager = UserProfileManager()
    
    print("=" * 60)
    print("用户画像统一测试")
    print("=" * 60)
    
    # 测试用户ID
    test_user_id = '13800138000'
    
    # 获取用户画像
    print(f"\n👤 用户画像: {test_user_id}")
    profile = manager.get_profile(test_user_id)
    summary = profile.get_summary()
    
    print(f"姓名: {summary.get('name', '未知')}")
    print(f"年级: {summary.get('grade', '未知')}")
    print(f"城市: {summary.get('city', '未知')}")
    print(f"评分: {summary.get('score', 0)}")
    print(f"总互动: {summary.get('total_interactions', 0)}")
    print(f"收藏学校: {summary.get('favorite_schools_count', 0)}")
    print(f"标签: {', '.join(summary.get('tags', []))}")
    
    # 获取详细画像
    print(f"\n📊 详细画像:")
    full_profile = profile.get_profile()
    
    print("\n基本信息:")
    basic_info = full_profile['basic_info']
    for key, value in basic_info.items():
        print(f"  {key}: {value}")
    
    print("\n渠道信息:")
    channels = full_profile['channels']
    for channel, info in channels.items():
        print(f"  {channel}:")
        print(f"    互动次数: {info['interaction_count']}")
        print(f"    首次访问: {info['first_seen']}")
        print(f"    最近访问: {info['last_seen']}")
    
    print("\n偏好信息:")
    preferences = full_profile['preferences']
    print(f"  收藏学校: {len(preferences.get('favorite_schools', []))}")
    print(f"  感兴趣话题: {', '.join(preferences.get('interested_topics', []))}")
    print(f"  沟通偏好: {preferences.get('communication_preference', 'web')}")
    
    # 获取统计信息
    print("\n📈 统计信息:")
    stats = manager.get_statistics()
    print(f"总用户数: {stats['total_users']}")
    print(f"平均评分: {stats['avg_score']}")
    print(f"热门标签:")
    for tag, count in stats['top_tags'][:5]:
        print(f"  {tag}: {count}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
