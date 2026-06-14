#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超级上下文管理器
提供指代消解、对话状态管理、智能主题追踪等高级功能
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class EntityTracker:
    """
    实体追踪器 - 用于跟踪对话中提到的实体（学校、地区、分数等）
    """
    
    # 常见学校名称模式
    SCHOOL_PATTERNS = [
        r'(云南师范大学附属中学|师大附中)',
        r'(昆明市第一中学|昆一中)',
        r'(昆明市第三中学|昆三中)',
        r'(昆明市第八中学|昆八中)',
        r'(云南大学附属中学|云大附中)',
        r'(昆明市第十中学|昆十中)',
        r'(昆明市第十四中学|昆十四中)',
        r'(官渡区第一中学|官一中)',
        r'([\u4e00-\u9fa5]+中学)',
        r'([\u4e00-\u9fa5]+高中)',
    ]
    
    # 指代消解模式
    REFERENCE_PATTERNS = [
        r'^它$', r'^它的$', r'^那个$', r'^那所$', r'^这所$', r'^这$', r'^那$',
        r'^这个学校$', r'^那个学校$', r'^那所学校$', r'^这所学校$',
        r'^这所中学$', r'^那所中学$', r'^这个中学$', r'^那个中学$',
        r'^这所高中$', r'^那所高中$', r'^这个高中$', r'^那个高中$',
    ]
    
    def __init__(self):
        self.entities: Dict[str, List[Dict[str, Any]]] = {}
        self.current_school: Optional[str] = None
        self.entity_timestamps: Dict[str, datetime] = {}
    
    def extract_school(self, text: str) -> Optional[str]:
        """从文本中提取学校名称"""
        for pattern in self.SCHOOL_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None
    
    def is_reference(self, text: str) -> bool:
        """判断是否是指代性表达"""
        text_stripped = text.strip()
        for pattern in self.REFERENCE_PATTERNS:
            if re.fullmatch(pattern, text_stripped, re.IGNORECASE):
                return True
        
        # 检查是否是短文本且没有明显的关键词
        if len(text_stripped) < 10 and not any(kw in text_stripped for kw in ['学校', '高中', '中学', '志愿', '分数']):
            return True
        
        return False
    
    def add_entity(self, entity_type: str, entity_value: str, source_text: str):
        """添加实体"""
        if entity_type not in self.entities:
            self.entities[entity_type] = []
        
        # 检查是否已存在，避免重复
        exists = any(e['value'] == entity_value for e in self.entities[entity_type])
        if not exists:
            self.entities[entity_type].append({
                'value': entity_value,
                'source': source_text,
                'timestamp': datetime.now()
            })
        
        self.entity_timestamps[entity_value] = datetime.now()
        
        # 更新当前学校
        if entity_type == 'school':
            self.current_school = entity_value
    
    def get_latest_entity(self, entity_type: str) -> Optional[str]:
        """获取最近提到的实体"""
        if entity_type not in self.entities:
            return None
        
        entities = self.entities[entity_type]
        if not entities:
            return None
        
        # 按时间排序，返回最新的
        entities_sorted = sorted(entities, key=lambda x: x['timestamp'], reverse=True)
        return entities_sorted[0]['value']
    
    def resolve_reference(self, text: str, context: List[Dict]) -> Optional[Dict[str, str]]:
        """
        消解指代
        
        Args:
            text: 当前文本
            context: 对话历史
            
        Returns:
            消解结果 {'type': 'school|district|score', 'value': '...'}
        """
        if not self.is_reference(text):
            return None
        
        # 优先检查当前学校
        if self.current_school:
            return {'type': 'school', 'value': self.current_school}
        
        # 检查对话历史中最近提到的学校
        for msg in reversed(context):
            if msg.get('role') in ['user', 'assistant']:
                school = self.extract_school(msg.get('content', ''))
                if school:
                    self.current_school = school
                    return {'type': 'school', 'value': school}
        
        return None
    
    def clear(self):
        """清除所有实体"""
        self.entities = {}
        self.current_school = None
        self.entity_timestamps = {}


class DialogueState:
    """
    对话状态管理
    """
    
    STATE_START = 'start'
    STATE_INFO_GATHERING = 'info_gathering'
    STATE_PROVIDING_INFO = 'providing_info'
    STATE_WAITING_FOR_CLARIFICATION = 'waiting_for_clarification'
    STATE_COMPLETED = 'completed'
    
    def __init__(self):
        self.current_state: str = self.STATE_START
        self.required_info: Dict[str, bool] = {
            'district': False,  # 是否需要地区
            'score': False,     # 是否需要分数
            'grade': False,     # 是否需要年级
        }
        self.last_question: Optional[str] = None
        self.conversation_topic: Optional[str] = None
    
    def update_required_info(self, key: str, has_value: bool):
        """更新所需信息状态"""
        if key in self.required_info:
            self.required_info[key] = has_value
    
    def is_info_complete(self) -> bool:
        """检查是否已获取所有所需信息"""
        # 对于择校，至少需要地区或分数之一
        return self.required_info['district'] or self.required_info['score']
    
    def reset(self):
        """重置状态"""
        self.current_state = self.STATE_START
        self.required_info = {
            'district': False,
            'score': False,
            'grade': False,
        }
        self.last_question = None
        self.conversation_topic = None


class SmartQuestioner:
    """
    智能提问器 - 根据上下文生成智能追问
    """
    
    QUESTION_TEMPLATES = {
        'need_district': [
            '你是哪个地区的考生呢？这样我可以为你推荐更合适的学校~',
            '请问你在哪个地区呢？我会结合当地的学校情况来帮你~',
            '方便告诉我你所在的地区吗？这样推荐会更精准~'
        ],
        'need_score': [
            '你的预估分数大概是多少呢？我可以帮你分析一下~',
            '可以告诉我你的估分吗？我会根据分数给你建议~',
            '你目前的成绩大概在什么水平呢？这样我能更好地帮你~'
        ],
        'need_both': [
            '为了给你更准确的建议，请告诉我你的地区和预估分数~',
            '请提供一下你的地区和分数，我会给你更精准的择校建议~'
        ],
        'clarify_school': [
            '你是指哪所学校呢？可以告诉我具体的校名~',
            '请问你想了解哪所学校的信息呢？',
            '你想了解的是哪所学校？请告诉我一下~'
        ],
        'clarify_intent': [
            '我有点没太明白，你可以具体说一下想了解什么吗？',
            '你想咨询哪方面的问题呢？比如学校、志愿、政策等~'
        ]
    }
    
    def __init__(self):
        import random
        self.random = random
    
    def get_next_question(self, user_profile: Dict, state: DialogueState) -> Optional[str]:
        """
        获取下一个问题
        
        Args:
            user_profile: 用户画像
            state: 对话状态
            
        Returns:
            问题文本
        """
        has_district = bool(user_profile.get('district'))
        has_score = bool(user_profile.get('score'))
        
        if not has_district and not has_score:
            return self._pick_template('need_both')
        elif not has_district:
            return self._pick_template('need_district')
        elif not has_score:
            return self._pick_template('need_score')
        
        return None
    
    def clarify_school(self) -> str:
        """追问学校名称"""
        return self._pick_template('clarify_school')
    
    def clarify_intent(self) -> str:
        """追问意图"""
        return self._pick_template('clarify_intent')
    
    def _pick_template(self, template_type: str) -> str:
        """随机选择模板"""
        templates = self.QUESTION_TEMPLATES.get(template_type, [])
        if templates:
            return self.random.choice(templates)
        return '请提供更多信息~'


class EnhancedTopicTracker:
    """
    增强版主题追踪器
    """
    
    # 主题关键词映射
    TOPIC_KEYWORDS = {
        'school_selection': ['择校', '选学校', '高中', '中学', '报考', '志愿', '填报', '志愿方案'],
        'school_info': ['学校', '附中', '一中', '二中', '三中', '地址', '电话', '学费', '升学率', '一本率'],
        'policy': ['政策', '招生', '录取', '分数线', '加分', '投档', '指标到校', '提前批'],
        'study_plan': ['学习计划', '复习', '备考', '刷题', '学习方法'],
        'score': ['分数', '成绩', '估分', '得分', '总分'],
        'exam': ['考试', '中考', '模拟考', '月考'],
        'admission': ['录取概率', '能不能上', '考上', '机会'],
        'compare': ['对比', '比较', '哪个好', '区别'],
        'emotional': ['压力', '焦虑', '紧张', '担心', '烦', '累'],
        'general_chat': ['聊天', '随便聊聊', '谈谈', '说说'],
    }
    
    def __init__(self):
        self.topic_history: List[Tuple[str, float, datetime]] = []
        self.topic_streak: Dict[str, int] = {}  # 主题连续出现次数
        self.last_topic: Optional[str] = None
    
    def track_topic(self, text: str) -> Tuple[str, float]:
        """
        追踪对话主题
        
        Returns:
            (主题名称, 置信度)
        """
        text_lower = text.lower()
        scores = {}
        
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            score = 0
            matched = 0
            
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matched += 1
                    score += 0.2
            
            # 根据匹配数量调整
            if matched >= 2:
                score += 0.1 * (matched - 1)
            
            if score > 0:
                scores[topic] = min(score, 1.0)
        
        if scores:
            sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            best_topic, best_score = sorted_topics[0]
            
            # 更新主题连续计数
            if best_topic == self.last_topic:
                self.topic_streak[best_topic] = self.topic_streak.get(best_topic, 0) + 1
            else:
                self.topic_streak = {best_topic: 1}
            
            self.last_topic = best_topic
            
            # 记录主题历史
            self.topic_history.append((best_topic, best_score, datetime.now()))
            if len(self.topic_history) > 20:
                self.topic_history = self.topic_history[-20:]
            
            return best_topic, best_score
        
        # 如果没有匹配到主题，保持上一个主题
        if self.last_topic:
            return self.last_topic, 0.3
        
        return 'general', 0.3
    
    def has_topic_streak(self, topic: str, min_streak: int = 2) -> bool:
        """检查是否有连续的主题"""
        return self.topic_streak.get(topic, 0) >= min_streak
    
    def get_dominant_topic(self, window: int = 5) -> Optional[str]:
        """获取主导主题（基于最近N轮）"""
        if not self.topic_history:
            return None
        
        recent_history = self.topic_history[-window:]
        topic_counts: Dict[str, float] = {}
        
        for topic, confidence, _ in recent_history:
            topic_counts[topic] = topic_counts.get(topic, 0) + confidence
        
        if topic_counts:
            return max(topic_counts.items(), key=lambda x: x[1])[0]
        
        return None
    
    def reset(self):
        """重置主题追踪"""
        self.topic_history = []
        self.topic_streak = {}
        self.last_topic = None


class SuperContextManager:
    """
    超级上下文管理器
    集成实体追踪、对话状态管理、智能主题追踪等功能
    """
    
    def __init__(self):
        self.conversations: Dict[str, Dict[str, Any]] = {}
        logger.info("超级上下文管理器初始化完成")
    
    def _get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        """获取或创建会话"""
        if session_id not in self.conversations:
            self.conversations[session_id] = {
                'messages': [],
                'entity_tracker': EntityTracker(),
                'dialogue_state': DialogueState(),
                'topic_tracker': EnhancedTopicTracker(),
                'user_profile': {},
                'created_at': datetime.now()
            }
        return self.conversations[session_id]
    
    def add_message(self, session_id: str, role: str, content: str):
        """添加消息到上下文"""
        session = self._get_or_create_session(session_id)
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now()
        }
        
        session['messages'].append(message)
        
        # 保持消息窗口大小
        if len(session['messages']) > 50:
            session['messages'] = session['messages'][-50:]
        
        # 提取并添加实体
        self._extract_entities(session, content, role)
        
        # 更新主题
        if role == 'user':
            topic, confidence = session['topic_tracker'].track_topic(content)
            message['topic'] = topic
            message['topic_confidence'] = confidence
        
        # 更新用户画像
        self._update_user_profile(session)
    
    def _extract_entities(self, session: Dict, content: str, role: str):
        """从消息中提取实体"""
        entity_tracker = session['entity_tracker']
        
        # 提取学校
        school = entity_tracker.extract_school(content)
        if school:
            entity_tracker.add_entity('school', school, content)
        
        # 提取分数
        score_match = re.search(r'(\d{2,3})\s*分', content)
        if score_match:
            score = int(score_match.group(1))
            entity_tracker.add_entity('score', str(score), content)
        
        # 提取地区
        district_match = self._extract_district(content)
        if district_match:
            entity_tracker.add_entity('district', district_match, content)
    
    def _extract_district(self, text: str) -> Optional[str]:
        """从文本中提取地区"""
        # 区县
        districts = ['五华区', '盘龙区', '官渡区', '西山区', '呈贡区',
                    '麒麟区', '宣威市', '大理市', '蒙自市', '文山市',
                    '景洪市', '瑞丽市', '芒市', '香格里拉市']
        for district in districts:
            if district in text:
                return district
        
        # 市级
        cities = ['昆明', '曲靖', '玉溪', '保山', '昭通', '丽江', 
                 '普洱', '临沧', '楚雄', '红河', '文山', '西双版纳',
                 '大理', '德宏', '怒江', '迪庆']
        for city in cities:
            if city in text:
                return city + '市'
        
        return None
    
    def _update_user_profile(self, session: Dict):
        """更新用户画像"""
        entity_tracker = session['entity_tracker']
        profile = {}
        
        # 获取最新实体
        school = entity_tracker.get_latest_entity('school')
        district = entity_tracker.get_latest_entity('district')
        score_str = entity_tracker.get_latest_entity('score')
        
        if school:
            profile['school'] = school
        if district:
            profile['district'] = district
        if score_str:
            profile['score'] = int(score_str)
        
        session['user_profile'] = profile
    
    def get_context(self, session_id: str) -> List[Dict]:
        """获取对话历史"""
        session = self._get_or_create_session(session_id)
        return session['messages']
    
    def get_user_profile(self, session_id: str) -> Dict:
        """获取用户画像"""
        session = self._get_or_create_session(session_id)
        return session['user_profile']
    
    def resolve_reference(self, session_id: str, text: str) -> Optional[Dict[str, str]]:
        """消解指代"""
        session = self._get_or_create_session(session_id)
        return session['entity_tracker'].resolve_reference(text, session['messages'])
    
    def get_current_topic(self, session_id: str) -> Optional[Tuple[str, float]]:
        """获取当前主题"""
        session = self._get_or_create_session(session_id)
        if session['messages']:
            last_msg = session['messages'][-1]
            if 'topic' in last_msg:
                return last_msg['topic'], last_msg['topic_confidence']
        return None
    
    def get_dominant_topic(self, session_id: str, window: int = 5) -> Optional[str]:
        """获取主导主题"""
        session = self._get_or_create_session(session_id)
        return session['topic_tracker'].get_dominant_topic(window)
    
    def get_smart_question(self, session_id: str) -> Optional[str]:
        """获取智能追问"""
        session = self._get_or_create_session(session_id)
        questioner = SmartQuestioner()
        return questioner.get_next_question(session['user_profile'], session['dialogue_state'])
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """获取会话完整信息"""
        session = self._get_or_create_session(session_id)
        return {
            'session_id': session_id,
            'message_count': len(session['messages']),
            'user_profile': session['user_profile'],
            'current_topic': self.get_current_topic(session_id),
            'dominant_topic': self.get_dominant_topic(session_id),
            'created_at': session['created_at'],
            'is_active': (datetime.now() - session['created_at']).total_seconds() < 3600  # 1小时内活跃
        }
    
    def clear_session(self, session_id: str):
        """清除会话"""
        if session_id in self.conversations:
            del self.conversations[session_id]


# 全局实例
_super_context_manager: Optional[SuperContextManager] = None


def get_super_context_manager() -> SuperContextManager:
    """获取超级上下文管理器实例"""
    global _super_context_manager
    if _super_context_manager is None:
        _super_context_manager = SuperContextManager()
    return _super_context_manager
