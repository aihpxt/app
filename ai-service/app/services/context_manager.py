#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版上下文管理器
支持多轮对话、主题追踪、历史摘要生成等功能
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class TopicTracker:
    """对话主题追踪器"""
    
    # 预定义主题关键词
    TOPIC_KEYWORDS = {
        'school_selection': ['择校', '选学校', '高中', '中学', '报考', '志愿', '填报志愿'],
        'policy': ['政策', '招生', '录取', '分数线', '加分', '投档', '省控线'],
        'study_plan': ['学习计划', '复习', '备考', '时间安排', '复习策略', '刷题'],
        'score': ['分数', '成绩', '总分', '估分', '得分', '分数段'],
        'school_info': ['学校', '附中', '一中', '二中', '校区', '地址', '电话', '学费'],
        'emotional': ['压力', '焦虑', '紧张', '担心', '烦', '累', '郁闷'],
        'exam': ['考试', '中考', '模拟考', '月考', '期中', '期末'],
        'admission_probability': ['录取概率', '能不能上', '可能性', '机会'],
        'school_compare': ['对比', '比较', '区别', '差异'],
        'tuition': ['学费', '费用', '收费', '多少钱'],
        'general_chat': ['聊天', '聊聊', '谈谈', '说说话']
    }
    
    def __init__(self):
        self._topic_history: Dict[str, List[Tuple[str, float, datetime]]] = {}
    
    def track_topic(self, session_id: str, text: str) -> Tuple[str, float]:
        """
        追踪当前对话主题
        
        Args:
            session_id: 会话ID
            text: 当前消息文本
        
        Returns:
            (主题名称, 置信度)
        """
        text_lower = text.lower()
        scores = {}
        
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += 0.2
            
            if score > 0:
                scores[topic] = min(score, 1.0)
        
        if scores:
            sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            best_topic, confidence = sorted_topics[0]
            
            # 记录主题历史
            if session_id not in self._topic_history:
                self._topic_history[session_id] = []
            self._topic_history[session_id].append((best_topic, confidence, datetime.now()))
            
            # 保留最近10条主题记录
            if len(self._topic_history[session_id]) > 10:
                self._topic_history[session_id] = self._topic_history[session_id][-10:]
            
            return best_topic, confidence
        
        return 'general', 0.5
    
    def get_topic_history(self, session_id: str) -> List[Tuple[str, float, datetime]]:
        """获取会话的主题历史"""
        return self._topic_history.get(session_id, [])
    
    def get_current_topic(self, session_id: str) -> Optional[Tuple[str, float]]:
        """获取当前主题"""
        history = self.get_topic_history(session_id)
        if history:
            return history[-1][:2]
        return None
    
    def detect_topic_change(self, session_id: str) -> bool:
        """检测是否发生主题切换"""
        history = self.get_topic_history(session_id)
        if len(history) < 2:
            return False
        
        recent_topics = history[-3:]
        topics = [h[0] for h in recent_topics]
        
        # 如果最近3条消息主题不一致，可能发生了切换
        return len(set(topics)) > 1
    
    def get_dominant_topic(self, session_id: str) -> Optional[str]:
        """获取会话的主导主题"""
        history = self.get_topic_history(session_id)
        if not history:
            return None
        
        topic_counts = {}
        for topic, confidence, _ in history:
            topic_counts[topic] = topic_counts.get(topic, 0) + confidence
        
        if topic_counts:
            return max(topic_counts, key=topic_counts.get)
        
        return None


class ConversationSummarizer:
    """对话历史摘要生成器"""
    
    def __init__(self):
        pass
    
    def generate_summary(self, messages: List[Dict], max_length: int = 100) -> str:
        """
        生成对话历史摘要
        
        Args:
            messages: 消息列表
            max_length: 摘要最大长度
        
        Returns:
            摘要文本
        """
        if not messages:
            return ""
        
        # 提取关键信息
        key_info = []
        
        for msg in messages:
            content = msg.get('content', '')
            
            # 提取学校名称
            school_patterns = [
                r'(师大附中|昆一中|昆三中|昆八中|云大附中|滇池中学|民族中学|实验中学|外国语学校)',
                r'([\u4e00-\u9fa5]+中学)',
                r'([\u4e00-\u9fa5]+高中)'
            ]
            for pattern in school_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, tuple):
                        key_info.extend(match)
                    else:
                        key_info.append(match)
            
            # 提取分数
            score_match = re.search(r'(\d{2,3})\s*分', content)
            if score_match:
                key_info.append(f"{score_match.group(1)}分")
            
            # 提取地区
            district_match = re.search(r'([\u4e00-\u9fa5]+区|[\u4e00-\u9fa5]+市|[\u4e00-\u9fa5]+县)', content)
            if district_match:
                key_info.append(district_match.group(1))
        
        # 去重
        key_info = list(dict.fromkeys(key_info))
        
        # 生成摘要
        if key_info:
            summary = "对话涉及：" + "、".join(key_info)
        else:
            # 如果没有提取到关键信息，使用最后一条消息
            summary = messages[-1].get('content', '')[:max_length]
        
        # 截断到最大长度
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary
    
    def generate_context_prompt(self, messages: List[Dict], max_messages: int = 5) -> str:
        """
        生成上下文提示（用于对话理解）
        
        Args:
            messages: 消息列表
            max_messages: 最大消息数
        
        Returns:
            上下文提示文本
        """
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
        
        prompt = ""
        for msg in recent_messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            if role and content:
                role_text = "用户" if role == 'user' else "助手"
                prompt += f"{role_text}: {content}\n"
        
        return prompt.strip()


class EnhancedContextManager:
    """增强版上下文管理器"""
    
    def __init__(self, window_size: int = 50):
        self._contexts: Dict[str, List[Dict]] = {}
        self._window_size = window_size
        self._topic_tracker = TopicTracker()
        self._summarizer = ConversationSummarizer()
        # 会话状态：active, completed, pending_clarification
        self._session_states: Dict[str, str] = {}
        # 会话创建时间
        self._session_created: Dict[str, datetime] = {}
        
        logger.info("增强版上下文管理器初始化完成")
    
    def add_message(self, session_id: str, role: str, content: str):
        """添加消息到上下文"""
        if session_id not in self._contexts:
            self._contexts[session_id] = []
            self._session_created[session_id] = datetime.now()
            self._session_states[session_id] = 'active'
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'topic': None,
            'topic_confidence': 0.0
        }
        
        # 追踪主题
        topic, confidence = self._topic_tracker.track_topic(session_id, content)
        message['topic'] = topic
        message['topic_confidence'] = confidence
        
        self._contexts[session_id].append(message)
        
        # 保持窗口大小
        if len(self._contexts[session_id]) > self._window_size:
            self._contexts[session_id] = self._contexts[session_id][-self._window_size:]
    
    def get_context(self, session_id: str) -> List[Dict]:
        """获取会话上下文"""
        return self._contexts.get(session_id, [])
    
    def get_last_message(self, session_id: str) -> Optional[Dict]:
        """获取最后一条消息"""
        context = self.get_context(session_id)
        return context[-1] if context else None
    
    def get_messages_by_role(self, session_id: str, role: str) -> List[Dict]:
        """获取特定角色的消息"""
        context = self.get_context(session_id)
        return [msg for msg in context if msg.get('role') == role]
    
    def get_user_profile(self, session_id: str) -> Optional[Dict]:
        """从上下文中提取用户画像"""
        context = self.get_context(session_id)
        profile = {}
        
        for msg in context:
            if msg.get('role') != 'user':
                continue
            
            content = msg.get('content', '')
            
            # 提取地区信息
            if not profile.get('district'):
                common_districts = ['五华区', '盘龙区', '官渡区', '西山区', '呈贡区',
                                   '麒麟区', '宣威市', '大理市', '蒙自市', '文山市',
                                   '景洪市', '瑞丽市', '芒市', '香格里拉市']
                for district in common_districts:
                    if district in content:
                        profile['district'] = district
                        break
                
                # 如果没有找到具体区县，检查是否有市级信息
                if not profile.get('district'):
                    cities = ['昆明', '曲靖', '玉溪', '保山', '昭通', '丽江', 
                             '普洱', '临沧', '楚雄', '红河', '文山', '西双版纳',
                             '大理', '德宏', '怒江', '迪庆']
                    for city in cities:
                        if city in content:
                            profile['district'] = city + '市'
                            break
            
            # 提取年级信息
            if not profile.get('grade'):
                if '初三' in content or '九年级' in content:
                    profile['grade'] = '九年级'
                elif '初二' in content or '八年级' in content:
                    profile['grade'] = '八年级'
            
            # 提取分数信息
            if not profile.get('score'):
                score_match = re.search(r'(\d{2,3})\s*分', content)
                if score_match:
                    profile['score'] = int(score_match.group(1))
        
        return profile if profile else None
    
    def has_recent_topic(self, session_id: str, topic: str) -> bool:
        """检查最近是否讨论过某个话题"""
        context = self.get_context(session_id)
        recent_messages = context[-3:] if len(context) > 3 else context
        
        return any(topic.lower() in msg.get('content', '').lower() for msg in recent_messages)
    
    def get_topic_history(self, session_id: str) -> List[Tuple[str, float, datetime]]:
        """获取主题历史"""
        return self._topic_tracker.get_topic_history(session_id)
    
    def get_current_topic(self, session_id: str) -> Optional[Tuple[str, float]]:
        """获取当前主题"""
        return self._topic_tracker.get_current_topic(session_id)
    
    def detect_topic_change(self, session_id: str) -> bool:
        """检测主题切换"""
        return self._topic_tracker.detect_topic_change(session_id)
    
    def get_dominant_topic(self, session_id: str) -> Optional[str]:
        """获取主导主题"""
        return self._topic_tracker.get_dominant_topic(session_id)
    
    def generate_summary(self, session_id: str, max_length: int = 100) -> str:
        """生成会话摘要"""
        messages = self.get_context(session_id)
        return self._summarizer.generate_summary(messages, max_length)
    
    def generate_context_prompt(self, session_id: str, max_messages: int = 5) -> str:
        """生成上下文提示"""
        messages = self.get_context(session_id)
        return self._summarizer.generate_context_prompt(messages, max_messages)
    
    def get_session_state(self, session_id: str) -> str:
        """获取会话状态"""
        return self._session_states.get(session_id, 'unknown')
    
    def set_session_state(self, session_id: str, state: str):
        """设置会话状态"""
        valid_states = ['active', 'completed', 'pending_clarification']
        if state in valid_states:
            self._session_states[session_id] = state
    
    def get_session_age(self, session_id: str) -> Optional[int]:
        """获取会话时长（分钟）"""
        created = self._session_created.get(session_id)
        if created:
            return int((datetime.now() - created).total_seconds() / 60)
        return None
    
    def is_session_active(self, session_id: str, timeout_minutes: int = 30) -> bool:
        """检查会话是否活跃"""
        age = self.get_session_age(session_id)
        if age is None:
            return False
        return age < timeout_minutes
    
    def can_continue(self, session_id: str) -> bool:
        """检查是否可以继续对话（上下文相关）"""
        context = self.get_context(session_id)
        if len(context) == 0:
            return True
        
        # 检查最后一条消息是否是追问
        last_msg = context[-1]
        if last_msg.get('role') == 'assistant':
            content = last_msg.get('content', '')
            # 如果助手最后一条消息是在提问，说明需要用户回复
            question_keywords = ['？', '？', '吗', '什么', '怎么', '为什么', '如何', '哪个']
            if any(keyword in content for keyword in question_keywords):
                return True
        
        return True
    
    def clear_context(self, session_id: str):
        """清除会话上下文"""
        if session_id in self._contexts:
            del self._contexts[session_id]
        if session_id in self._session_states:
            del self._session_states[session_id]
        if session_id in self._session_created:
            del self._session_created[session_id]
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """获取会话完整信息"""
        context = self.get_context(session_id)
        user_profile = self.get_user_profile(session_id)
        current_topic = self.get_current_topic(session_id)
        dominant_topic = self.get_dominant_topic(session_id)
        summary = self.generate_summary(session_id)
        age = self.get_session_age(session_id)
        state = self.get_session_state(session_id)
        
        return {
            'session_id': session_id,
            'message_count': len(context),
            'user_profile': user_profile,
            'current_topic': current_topic,
            'dominant_topic': dominant_topic,
            'summary': summary,
            'age_minutes': age,
            'state': state,
            'is_active': self.is_session_active(session_id)
        }


# 全局实例
enhanced_context_manager = EnhancedContextManager()


def get_enhanced_context_manager() -> EnhancedContextManager:
    """获取增强版上下文管理器实例"""
    return enhanced_context_manager


if __name__ == '__main__':
    print("=" * 70)
    print("增强版上下文管理器测试")
    print("=" * 70)
    
    manager = EnhancedContextManager()
    
    session_id = "test_session_001"
    
    test_messages = [
        ("user", "你好，我想了解中考择校"),
        ("assistant", "您好！我来帮你分析中考择校问题。"),
        ("user", "我是五华区的考生"),
        ("assistant", "好的，已知你来自五华区。"),
        ("user", "师大附中怎么样？"),
        ("assistant", "师大附中是云南省重点中学..."),
        ("user", "它的录取分数线是多少？"),
        ("assistant", "去年的录取分数线大概是680分左右。"),
        ("user", "学费贵吗？"),
    ]
    
    print("\n📝 添加测试消息：")
    print("-" * 50)
    for role, content in test_messages:
        manager.add_message(session_id, role, content)
        print(f"[{role}] {content}")
    
    print("\n📊 会话信息：")
    print("-" * 50)
    info = manager.get_session_info(session_id)
    print(f"消息数量: {info['message_count']}")
    print(f"用户画像: {info['user_profile']}")
    print(f"当前主题: {info['current_topic']}")
    print(f"主导主题: {info['dominant_topic']}")
    print(f"会话摘要: {info['summary']}")
    print(f"会话时长: {info['age_minutes']}分钟")
    print(f"会话状态: {info['state']}")
    print(f"是否活跃: {info['is_active']}")
    
    print("\n🔍 主题历史：")
    print("-" * 50)
    topic_history = manager.get_topic_history(session_id)
    for topic, confidence, timestamp in topic_history:
        print(f"{timestamp.strftime('%H:%M:%S')} - {topic} ({confidence:.2f})")
    
    print("\n💬 上下文提示：")
    print("-" * 50)
    prompt = manager.generate_context_prompt(session_id, max_messages=3)
    print(prompt)
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)