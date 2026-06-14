#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个性化响应引擎
基于用户画像、对话历史和偏好学习提供个性化响应
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class UserPreferenceTracker:
    """用户偏好追踪器"""
    
    def __init__(self):
        self._preferences: Dict[str, Dict[str, float]] = {}
    
    def track_preference(self, session_id: str, preference_type: str, value: str, weight: float = 1.0):
        """
        追踪用户偏好
        
        Args:
            session_id: 会话ID
            preference_type: 偏好类型（如 school_type, location, budget等）
            value: 偏好值
            weight: 权重
        """
        if session_id not in self._preferences:
            self._preferences[session_id] = {}
        
        key = f"{preference_type}_{value}"
        if key in self._preferences[session_id]:
            self._preferences[session_id][key] += weight
        else:
            self._preferences[session_id][key] = weight
    
    def get_preferences(self, session_id: str) -> Dict[str, float]:
        """获取用户偏好"""
        return self._preferences.get(session_id, {})
    
    def get_top_preferences(self, session_id: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """获取用户最偏好的前N项"""
        preferences = self.get_preferences(session_id)
        sorted_prefs = sorted(preferences.items(), key=lambda x: x[1], reverse=True)
        return sorted_prefs[:top_n]
    
    def infer_preferences_from_history(self, messages: List[Dict]):
        """从对话历史推断偏好"""
        preferences = {}
        
        for msg in messages:
            content = msg.get('content', '')
            
            # 推断学校类型偏好
            school_types = {
                '重点中学': ['重点', '一级', '名校', '优质', '顶尖'],
                '公办': ['公办', '公立'],
                '民办': ['民办', '私立'],
                '寄宿': ['寄宿', '住校', '住宿'],
                '走读': ['走读', '不住校']
            }
            for pref_type, keywords in school_types.items():
                for keyword in keywords:
                    if keyword in content:
                        preferences[f'school_type_{pref_type}'] = preferences.get(f'school_type_{pref_type}', 0) + 1.0
            
            # 推断关注点偏好
            concerns = {
                '升学率': ['升学率', '一本率', '本科率'],
                '费用': ['学费', '费用', '收费', '多少钱'],
                '地理位置': ['地址', '位置', '校区', '近', '远'],
                '师资': ['老师', '师资', '教师'],
                '校园环境': ['校园', '环境', '设施']
            }
            for pref_type, keywords in concerns.items():
                for keyword in keywords:
                    if keyword in content:
                        preferences[f'concern_{pref_type}'] = preferences.get(f'concern_{pref_type}', 0) + 1.0
        
        return preferences


class ResponseStyleManager:
    """响应风格管理器"""
    
    STYLES = {
        'friendly': {
            'greetings': ['你好！', '您好！', '嗨！', '哈喽！', '你好呀！'],
            'endings': ['祝你成功！', '加油！', '相信你可以的！', '有问题随时找我！'],
            'tone': 'warm',
            'formality': 'casual'
        },
        'professional': {
            'greetings': ['您好，', '您好！', '尊敬的用户，'],
            'endings': ['感谢您的咨询。', '如有其他问题，请随时联系。', '祝您学业进步。'],
            'tone': 'neutral',
            'formality': 'formal'
        },
        'concise': {
            'greetings': ['您好。', '你好。'],
            'endings': ['谢谢。', '再见。'],
            'tone': 'neutral',
            'formality': 'neutral'
        },
        'enthusiastic': {
            'greetings': ['你好！🎉', '您好！✨', '嗨！🌟'],
            'endings': ['加油哦！💪', '你一定可以的！🚀', '期待你的好消息！🎊'],
            'tone': 'excited',
            'formality': 'casual'
        }
    }
    
    def __init__(self):
        self._user_styles: Dict[str, str] = {}
    
    def get_style(self, session_id: str) -> str:
        """获取用户偏好的响应风格"""
        return self._user_styles.get(session_id, 'friendly')
    
    def set_style(self, session_id: str, style: str):
        """设置用户响应风格"""
        if style in self.STYLES:
            self._user_styles[session_id] = style
    
    def infer_style_from_sentiment(self, sentiment: str, sentiment_confidence: float) -> str:
        """根据情感推断响应风格"""
        if sentiment == 'negative' and sentiment_confidence > 0.7:
            return 'friendly'
        elif sentiment == 'positive' and sentiment_confidence > 0.7:
            return 'enthusiastic'
        return 'friendly'
    
    def apply_style(self, response: str, style: str) -> str:
        """应用响应风格"""
        if style not in self.STYLES:
            return response
        
        style_config = self.STYLES[style]
        
        # 根据风格调整响应
        if style == 'friendly':
            response = response.replace('。', '～').replace('！', '～')
        elif style == 'professional':
            response = response.replace('！', '。').replace('～', '。')
        elif style == 'concise':
            # 简化响应
            sentences = response.split('。')
            if len(sentences) > 3:
                response = '。'.join(sentences[:3]) + '。'
        elif style == 'enthusiastic':
            response += ' 💪'
        
        return response


class PersonalizationEngine:
    """个性化引擎"""
    
    def __init__(self):
        self._preference_tracker = UserPreferenceTracker()
        self._style_manager = ResponseStyleManager()
        logger.info("个性化引擎初始化完成")
    
    def personalize_response(self, response: str, session_id: str, 
                            user_profile: Optional[Dict] = None,
                            messages: Optional[List[Dict]] = None) -> Tuple[str, Dict]:
        """
        个性化响应
        
        Args:
            response: 原始响应文本
            session_id: 会话ID
            user_profile: 用户画像
            messages: 对话历史消息
        
        Returns:
            (个性化后的响应, 个性化信息)
        """
        personalization_info = {
            'applied_style': None,
            'applied_preferences': [],
            'profile_used': False
        }
        
        # 1. 根据用户画像个性化
        if user_profile:
            personalization_info['profile_used'] = True
            
            # 如果用户有地区信息，添加地区相关内容
            if user_profile.get('district'):
                response = f"📍 根据{user_profile['district']}的情况，{response}"
            
            # 如果用户有分数信息，添加分数相关建议
            if user_profile.get('score'):
                score = user_profile['score']
                if score >= 600:
                    response += "\n🎉 你的分数很不错，可以冲刺省级重点中学！"
                elif score >= 550:
                    response += "\n👍 你的分数不错，可以考虑州市级重点中学！"
                elif score >= 500:
                    response += "\n💪 继续努力，还有提升空间！"
        
        # 2. 根据对话历史推断偏好
        if messages:
            preferences = self._preference_tracker.infer_preferences_from_history(messages)
            if preferences:
                top_prefs = sorted(preferences.items(), key=lambda x: x[1], reverse=True)[:3]
                personalization_info['applied_preferences'] = [p[0] for p in top_prefs]
                
                # 根据偏好调整响应
                for pref_key, _ in top_prefs:
                    if 'concern_升学率' in pref_key:
                        response += "\n📊 特别关注升学率的话，我可以为你推荐升学率较高的学校。"
                    elif 'concern_费用' in pref_key:
                        response += "\n💰 如果你比较关注费用，可以考虑公办学校或性价比高的民办学校。"
                    elif 'concern_地理位置' in pref_key:
                        response += "\n📍 如果你在意地理位置，可以告诉我你希望的区域。"
        
        # 3. 根据情感调整风格
        # (情感信息需要从上下文获取，这里简化处理)
        style = self._style_manager.get_style(session_id)
        response = self._style_manager.apply_style(response, style)
        personalization_info['applied_style'] = style
        
        return response, personalization_info
    
    def track_interaction(self, session_id: str, user_input: str, response: str):
        """
        追踪用户交互，学习偏好
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            response: 系统响应
        """
        # 从用户输入中提取偏好
        preferences = self._preference_tracker.infer_preferences_from_history([{'content': user_input}])
        for pref_key, weight in preferences.items():
            pref_type, value = pref_key.split('_', 1)
            self._preference_tracker.track_preference(session_id, pref_type, value, weight)
    
    def get_user_profile_enhanced(self, session_id: str, basic_profile: Optional[Dict]) -> Dict[str, Any]:
        """
        获取增强的用户画像（包含学习到的偏好）
        
        Args:
            session_id: 会话ID
            basic_profile: 基础用户画像
        
        Returns:
            增强的用户画像
        """
        profile = basic_profile.copy() if basic_profile else {}
        
        # 添加学习到的偏好
        preferences = self._preference_tracker.get_top_preferences(session_id)
        if preferences:
            profile['learned_preferences'] = preferences
        
        # 添加偏好风格
        profile['preferred_style'] = self._style_manager.get_style(session_id)
        
        return profile
    
    def suggest_schools(self, session_id: str, user_profile: Dict) -> List[Dict]:
        """
        根据用户画像推荐学校
        
        Args:
            session_id: 会话ID
            user_profile: 用户画像
        
        Returns:
            推荐学校列表
        """
        score = user_profile.get('score', 0)
        district = user_profile.get('district', '')
        
        # 基于分数的推荐
        recommendations = []
        
        if score >= 680:
            recommendations.extend([
                {'name': '云南师范大学附属中学', 'type': '省级重点', 'match_score': 95},
                {'name': '昆明市第一中学', 'type': '省级重点', 'match_score': 93},
                {'name': '云南大学附属中学', 'type': '省级重点', 'match_score': 90}
            ])
        elif score >= 650:
            recommendations.extend([
                {'name': '昆明市第三中学', 'type': '省级重点', 'match_score': 88},
                {'name': '昆明市第八中学', 'type': '省级重点', 'match_score': 85},
                {'name': '昆明市第十中学', 'type': '市级重点', 'match_score': 82}
            ])
        elif score >= 600:
            recommendations.extend([
                {'name': '昆明市第十四中学', 'type': '市级重点', 'match_score': 78},
                {'name': '官渡区第一中学', 'type': '市级重点', 'match_score': 75},
                {'name': '西山区第一中学', 'type': '区级重点', 'match_score': 72}
            ])
        else:
            recommendations.extend([
                {'name': '昆明市实验中学', 'type': '普通中学', 'match_score': 65},
                {'name': '昆明市民办中学', 'type': '民办', 'match_score': 60},
                {'name': '当地普通高中', 'type': '普通', 'match_score': 55}
            ])
        
        # 根据地区过滤
        if district:
            recommendations = [r for r in recommendations if district in r.get('name', '') or True]
        
        return recommendations


# 全局实例
personalization_engine = PersonalizationEngine()


def get_personalization_engine() -> PersonalizationEngine:
    """获取个性化引擎实例"""
    return personalization_engine


if __name__ == '__main__':
    print("=" * 70)
    print("个性化响应引擎测试")
    print("=" * 70)
    
    engine = PersonalizationEngine()
    
    # 测试1: 个性化响应
    print("\n1. 个性化响应测试")
    print("-" * 50)
    response = "好的，我来帮你分析择校情况。"
    user_profile = {'district': '五华区', 'score': 580}
    messages = [
        {'content': '我比较关注升学率'},
        {'content': '学费大概多少钱'}
    ]
    
    personalized, info = engine.personalize_response(response, 'test', user_profile, messages)
    print(f"原始响应: {response}")
    print(f"个性化响应: {personalized}")
    print(f"个性化信息: {info}")
    
    # 测试2: 用户画像增强
    print("\n2. 用户画像增强测试")
    print("-" * 50)
    basic_profile = {'district': '五华区', 'score': 580}
    enhanced_profile = engine.get_user_profile_enhanced('test', basic_profile)
    print(f"基础画像: {basic_profile}")
    print(f"增强画像: {enhanced_profile}")
    
    # 测试3: 学校推荐
    print("\n3. 学校推荐测试")
    print("-" * 50)
    user_profile = {'score': 660, 'district': '五华区'}
    schools = engine.suggest_schools('test', user_profile)
    print(f"用户画像: {user_profile}")
    print("推荐学校:")
    for school in schools:
        print(f"  - {school['name']} ({school['type']}) [匹配度: {school['match_score']}%]")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)