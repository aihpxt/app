#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超级智能对话管理器
集成超级上下文管理器，支持指代消解、智能主题追踪、智能追问等高级功能
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class SuperIntelligentChatManager:
    """
    超级智能对话管理器
    集成了增强版上下文管理、指代消解、智能主题追踪等高级功能
    """
    
    def __init__(self):
        # 导入核心组件
        from .intelligent_chat_manager import IntentClassifier, SentimentAnalyzer
        from .smart_response_generator import get_response_generator
        from .super_context_manager import get_super_context_manager
        
        self._intent_classifier = IntentClassifier()
        self._sentiment_analyzer = SentimentAnalyzer()
        self._response_generator = get_response_generator()
        self._super_context = get_super_context_manager()
        
        # 导入旧的语义分析器作为备用
        try:
            from .semantic_analyzer import get_semantic_analyzer
            self._semantic_analyzer = get_semantic_analyzer()
            self._has_semantic_analyzer = True
        except:
            self._has_semantic_analyzer = False
        
        self._personality = {
            'name': '小龙虾',
            'role': '云南省中考智能助手',
            'tone': 'friendly',
            'style': 'helpful'
        }
        
        logger.info("超级智能对话管理器初始化完成！")
    
    def process_message(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            session_id: 会话ID
            user_input: 用户输入文本
            
        Returns:
            处理结果字典
        """
        # 1. 添加用户消息到超级上下文
        self._super_context.add_message(session_id, 'user', user_input)
        
        # 2. 获取上下文信息
        context = self._super_context.get_context(session_id)
        user_profile = self._super_context.get_user_profile(session_id)
        
        # 3. 尝试指代消解
        resolved = self._super_context.resolve_reference(session_id, user_input)
        enriched_input = self._enrich_input(user_input, resolved)
        
        # 4. 获取主题信息
        current_topic = self._super_context.get_current_topic(session_id)
        dominant_topic = self._super_context.get_dominant_topic(session_id)
        
        # 5. 语义分析（如果有）
        semantic_result = {}
        if self._has_semantic_analyzer:
            try:
                semantic_result = self._semantic_analyzer.analyze(enriched_input, context[:-1])
            except:
                semantic_result = {}
        
        # 6. 意图识别
        intents = semantic_result.get('intents', [])
        if intents:
            intent, intent_confidence = intents[0]
        else:
            intent, intent_confidence = self._intent_classifier.classify(enriched_input)
        
        # 7. 根据上下文增强意图
        intent, intent_confidence = self._enhance_intent_with_context(
            intent, intent_confidence, current_topic, dominant_topic, enriched_input
        )
        
        # 8. 情感分析
        sentiment, sentiment_confidence = self._sentiment_analyzer.analyze(user_input)
        
        # 9. 生成响应
        response, response_info = self._generate_response(
            enriched_input,
            intent,
            sentiment,
            context,
            user_profile,
            semantic_result,
            resolved
        )
        
        # 10. 添加助手响应到上下文
        self._super_context.add_message(session_id, 'assistant', response)
        
        # 11. 获取会话信息
        session_info = self._super_context.get_session_info(session_id)
        
        return {
            'success': True,
            'content': response,
            'session_id': session_id,
            'intent': intent,
            'intent_confidence': intent_confidence,
            'sentiment': sentiment,
            'sentiment_confidence': sentiment_confidence,
            'user_profile': user_profile,
            'context_length': len(context),
            'resolved_reference': resolved,
            'current_topic': current_topic,
            'dominant_topic': dominant_topic,
            'session_info': session_info,
            'enriched_input': enriched_input
        }
    
    def _enrich_input(self, text: str, resolved: Optional[Dict[str, str]]) -> str:
        """根据消解结果丰富输入文本"""
        if resolved and resolved.get('type') == 'school':
            school_name = resolved['value']
            # 如果原文本很短，补充完整信息
            if len(text) < 15:
                text = f"{text}（指{school_name}）"
        return text
    
    def _enhance_intent_with_context(self, intent: str, confidence: float, 
                                    current_topic: Optional[Tuple[str, float]],
                                    dominant_topic: Optional[str],
                                    text: str) -> Tuple[str, float]:
        """
        根据上下文增强意图识别
        """
        # 如果没有识别到明确的意图，但有主导主题，使用主题作为意图
        if intent == 'unknown' or confidence < 0.3:
            if dominant_topic:
                # 映射主题到意图
                topic_to_intent = {
                    'school_selection': 'school_selection',
                    'school_info': 'school_info',
                    'policy': 'policy',
                    'score': 'score',
                    'admission': 'admission_probability',
                    'compare': 'school_compare',
                    'study_plan': 'study_plan',
                    'emotional': 'emotional'
                }
                if dominant_topic in topic_to_intent:
                    return topic_to_intent[dominant_topic], max(confidence, 0.4)
        
        return intent, confidence
    
    def _generate_response(self, user_input: str, intent: str, sentiment: str,
                          context: List[Dict], user_profile: Dict,
                          semantic_result: Dict, resolved: Optional[Dict]) -> Tuple[str, Dict]:
        """
        生成响应
        """
        # 特殊情况：指代消解成功，明确了学校
        if resolved and resolved.get('type') == 'school':
            # 检查是否只是简单的指代
            if len(user_input.replace('（指' + resolved['value'] + '）', '').strip()) < 10:
                # 生成关于该学校的信息
                return self._response_for_school(resolved['value'], user_profile), {}
        
        # 检查是否需要智能追问
        smart_question = self._check_smart_question(user_profile, intent, context)
        if smart_question:
            return smart_question, {'needs_clarification': True}
        
        # 使用响应生成器
        try:
            response = self._response_generator.generate_response(
                intent, sentiment, user_profile, context, semantic_result
            )
            return response, {}
        except Exception as e:
            logger.error(f"响应生成失败: {e}")
            return "抱歉，我理解了你的问题，让我想想怎么回答~", {}
    
    def _response_for_school(self, school_name: str, user_profile: Dict) -> str:
        """生成关于特定学校的响应"""
        # 这里可以调用知识图谱获取学校详细信息
        # 先使用简单的模板响应
        base_response = f"关于{school_name}，我可以帮你了解：\n"
        base_response += "📊 录取分数线\n"
        base_response += "🏫 学校基本信息\n"
        base_response += "📈 升学率情况\n"
        base_response += "📍 地址和联系方式\n"
        base_response += "\n你想了解哪方面呢？"
        
        # 如果有用户分数，可以加入录取概率分析
        if user_profile.get('score'):
            score = user_profile['score']
            base_response = f"结合你的分数{score}分，关于{school_name}：\n" + base_response
        
        return base_response
    
    def _check_smart_question(self, user_profile: Dict, intent: str, context: List[Dict]) -> Optional[str]:
        """
        检查是否需要智能追问
        """
        # 如果是择校相关且信息不全
        if intent in ['school_selection', 'recommendation']:
            has_district = bool(user_profile.get('district'))
            has_score = bool(user_profile.get('score'))
            
            if not has_district and not has_score:
                return "为了给你更准确的建议，请告诉我你的地区和预估分数~"
            elif not has_district:
                return "你是哪个地区的考生呢？这样我可以为你推荐更合适的学校~"
            elif not has_score:
                return "你的预估分数大概是多少呢？我可以帮你分析一下~"
        
        # 如果是school_info但没有明确学校
        if intent == 'school_info' and not user_profile.get('school'):
            return "你想了解哪所学校呢？"
        
        return None
    
    def clear_session(self, session_id: str):
        """清除会话"""
        self._super_context.clear_session(session_id)


# 全局实例
_super_chat_manager: Optional[SuperIntelligentChatManager] = None


def get_super_chat_manager() -> SuperIntelligentChatManager:
    """获取超级智能对话管理器实例"""
    global _super_chat_manager
    if _super_chat_manager is None:
        _super_chat_manager = SuperIntelligentChatManager()
    return _super_chat_manager
