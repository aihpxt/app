#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能对话管理器
增强对话的智能化程度，具备上下文理解、情感分析、意图识别等能力
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)


class IntentClassifier:
    """意图分类器 - 增强版"""
    
    INTENTS = {
        'greeting': {
            'keywords': ['你好', '您好', '嗨', 'Hello', 'Hi', '早上好', '下午好', '晚上好', '你好呀', '嗨喽', '哈喽', '您好呀', '嗨嗨', '您好！', '你好！', '嘿', '嘿呀', '早安', '午安', '晚安'],
            'patterns': [r'^你好.*', r'^您好.*', r'^嗨.*', r'^hello.*', r'^hi.*', r'^早上好.*', r'^下午好.*', r'^晚上好.*', r'^早安.*', r'^午安.*', r'^晚安.*']
        },
        'farewell': {
            'keywords': ['再见', '拜拜', '再见了', '下次见', 'goodbye', 'bye', '拜拜了', '先走了', '下次聊', '回头见', '先撤了', '告辞', '先走一步', '回见', '拜拜啦'],
            'patterns': [r'.*再见.*', r'.*拜拜.*', r'.*先走了.*', r'.*下次见.*', r'.*先撤.*', r'.*告辞.*']
        },
        'thanks': {
            'keywords': ['谢谢', '谢谢你', '感谢', '辛苦了', '太谢谢了', '非常感谢', '多谢', '谢了', '感激', '谢谢啦', '谢谢你了', '非常谢谢', '万分感谢'],
            'patterns': [r'.*谢谢.*', r'.*感谢.*', r'.*辛苦了.*', r'.*感激.*']
        },
        'school_selection': {
            'keywords': ['选学校', '择校', '高中', '中学', '报考', '志愿', '填报志愿', '报志愿', '选高中', '初中毕业', '升学', '报考高中', '选哪所', '挑学校', '选校', '择校指导', '志愿选择', '志愿方案', '填报方案', '志愿计划', '报考方案', '志愿建议', '填报建议', '志愿填报', '志愿填'],
            'patterns': [r'.*选.*学校.*', r'.*择校.*', r'.*报考.*高中.*', r'.*志愿.*', r'.*填报.*志愿.*', r'.*升学.*', r'.*初中毕业.*', r'.*志愿.*方案.*', r'.*填报.*方案.*']
        },
        'policy': {
            'keywords': ['政策', '招生', '录取', '分数线', '加分', '投档', '录取线', '招生政策', '加分政策', '定向生', '指标到校', '提前批', '录取规则', '招生计划', '录取流程', '投档线', '省控线'],
            'patterns': [r'.*政策.*', r'.*招生.*', r'.*录取.*', r'.*分数线.*', r'.*加分.*', r'.*投档.*', r'.*指标到校.*', r'.*提前批.*']
        },
        'study_plan': {
            'keywords': ['学习计划', '计划', '复习', '备考', '时间安排', '复习计划', '学习安排', '备考计划', '刷题', '做题', '学习方法', '复习策略', '备考攻略', '时间管理', '学习技巧', '提分技巧'],
            'patterns': [r'.*学习计划.*', r'.*复习.*', r'.*备考.*', r'.*时间安排.*', r'.*复习计划.*', r'.*学习方法.*', r'.*复习策略.*']
        },
        'question': {
            'keywords': ['什么', '怎么', '为什么', '如何', '是否', '哪个', '哪种', '哪所', '哪儿', '哪里', '能否', '能不能', '是否可以', '啥', '咋', '为啥', '怎么样', '好不好', '可以吗'],
            'patterns': [r'^什么.*', r'^怎么.*', r'^为什么.*', r'^如何.*', r'^哪个.*', r'^哪种.*', r'^能否.*', r'^啥.*', r'^咋.*', r'^为啥.*']
        },
        'recommendation': {
            'keywords': ['推荐', '建议', '哪个好', '比较', '更好', '最好', '推荐一下', '给个建议', '帮忙推荐', '推荐学校', '选哪个', '对比', '哪个更好', '哪个合适', '推荐一下', '给点建议'],
            'patterns': [r'.*推荐.*', r'.*建议.*', r'.*比较.*', r'.*哪个好.*', r'.*更好.*', r'.*对比.*']
        },
        'emotional': {
            'keywords': ['压力', '焦虑', '紧张', '担心', '害怕', '烦', '累', '郁闷', '烦躁', '不安', '睡不着', '担心考不好', '焦虑不安', '压力大', '心烦', '心累', '紧张不安', '担忧', '发愁', '沮丧'],
            'patterns': [r'.*压力.*', r'.*焦虑.*', r'.*担心.*', r'.*害怕.*', r'.*烦.*', r'.*累.*', r'.*郁闷.*', r'.*烦躁.*', r'.*不安.*']
        },
        'chat': {
            'keywords': ['聊聊天', '随便聊聊', '谈谈', '说说', '聊聊', '说说话', '闲谈', '聊一下', '聊聊呗', '唠嗑', '聊两句', '随便说', '聊点别的', '闲聊'],
            'patterns': [r'.*聊聊.*', r'.*谈谈.*', r'.*说说.*', r'.*闲谈.*', r'.*唠嗑.*', r'.*聊两句.*']
        },
        'score': {
            'keywords': ['分数', '成绩', '多少分', '考多少', '总分', '各科', '分数段', '估分', '得分', '分数范围', '分数线', '分数预测', '模拟成绩', '模考分数', '预估分'],
            'patterns': [r'.*分数.*', r'.*成绩.*', r'.*多少分.*', r'.*总分.*', r'.*估分.*', r'.*得分.*', r'.*分数范围.*']
        },
        'school_info': {
            'keywords': ['学校', '中学', '高中', '附中', '一中', '二中', '三中', '校区', '地址', '电话', '学费', '住宿', '学校介绍', '学校信息', '校园环境', '师资力量', '升学率', '一本率'],
            'patterns': [r'.*学校.*', r'.*中学.*', r'.*高中.*', r'.*附中.*', r'.*一中.*', r'.*二中.*', r'.*三中.*']
        },
        'exam': {
            'keywords': ['考试', '中考', '模拟考', '月考', '期中', '期末', '考试时间', '考试科目', '考场', '考试安排', '考试范围', '考试大纲', '考试内容', '备考时间'],
            'patterns': [r'.*考试.*', r'.*中考.*', r'.*模拟.*', r'.*月考.*', r'.*期中.*', r'.*期末.*']
        },
        'admission_probability': {
            'keywords': ['录取概率', '能不能上', '录取可能性', '考上', '机会', '概率', '可能性', '希望', '能上吗', '能考上吗', '录取机会'],
            'patterns': [r'.*录取.*概率.*', r'.*能不能.*上.*', r'.*录取.*可能.*', r'.*能上.*吗.*', r'.*考上.*吗.*']
        },
        'school_compare': {
            'keywords': ['对比', '比较', '哪个好', '区别', '差异', '不同', '对比分析', '学校对比', '比较学校', '哪个更好'],
            'patterns': [r'.*对比.*', r'.*比较.*', r'.*哪个.*好.*', r'.*区别.*', r'.*差异.*']
        },
        'tuition': {
            'keywords': ['学费', '费用', '收费', '多少钱', '价格', '交费', '缴费', '学费多少', '收费标准', '费用多少', '价格多少'],
            'patterns': [r'.*学费.*', r'.*费用.*', r'.*收费.*', r'.*多少钱.*', r'.*价格.*']
        }
    }
    
    def classify(self, text: str) -> Tuple[str, float]:
        """
        分类意图（增强版）
        
        Args:
            text: 用户输入文本
        
        Returns:
            (意图名称, 置信度)
        """
        text_lower = text.lower()
        scores = {}
        
        # 计算文本长度，用于调整分数
        text_length = len(text_lower)
        
        for intent, config in self.INTENTS.items():
            score = 0
            matched_keywords = 0
            matched_patterns = 0
            
            # 关键词匹配
            for keyword in config['keywords']:
                if keyword.lower() in text_lower:
                    matched_keywords += 1
                    # 根据关键词长度调整分数（越长的关键词匹配越重要）
                    keyword_weight = min(len(keyword) / 4, 1.0)
                    score += 0.2 * keyword_weight
            
            # 模式匹配
            for pattern in config['patterns']:
                if re.match(pattern, text_lower) or re.search(pattern, text_lower):
                    matched_patterns += 1
                    score += 0.3
            
            # 如果同时匹配了关键词和模式，给予额外奖励
            if matched_keywords > 0 and matched_patterns > 0:
                score += 0.2
            
            # 根据匹配数量调整分数
            total_matches = matched_keywords + matched_patterns
            if total_matches >= 2:
                score += 0.1 * (total_matches - 1)
            
            # 归一化分数
            if score > 0:
                scores[intent] = min(score, 1.0)
        
        if scores:
            # 获取最高分和次高分，用于判断是否有明显的意图
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            best_intent, best_score = sorted_scores[0]
            
            # 如果最高分和次高分差距较小，增加置信度判断
            if len(sorted_scores) >= 2:
                second_score = sorted_scores[1][1]
                if best_score - second_score < 0.2:
                    # 差距较小，降低置信度
                    best_score = min(best_score, 0.7)
            
            return best_intent, round(best_score, 2)
        
        return 'unknown', 0.0


class SentimentAnalyzer:
    """情感分析器 - 增强版"""
    
    POSITIVE_WORDS = [
        '好', '棒', '开心', '高兴', '喜欢', '满意', '感谢', '谢谢', '不错', '精彩',
        '棒', '太棒了', '太好了', '优秀', '完美', '顺利', '成功', '进步', '开心',
        '高兴', '快乐', '愉快', '幸福', '满足', '欣慰', '自豪', '自信', '轻松',
        '兴奋', '期待', '希望', '信心', '加油', '鼓励', '支持', '赞赏', '表扬'
    ]
    
    NEGATIVE_WORDS = [
        '不好', '差', '难过', '伤心', '担心', '害怕', '焦虑', '压力', '烦', '累', '失望',
        '紧张', '不安', '烦躁', '郁闷', '发愁', '沮丧', '担忧', '恐惧', '害怕',
        '焦虑', '紧张', '压力大', '心烦', '心累', '疲惫', '困扰', '无助', '迷茫',
        '失望', '失落', '挫败', '伤心', '难过', '痛苦', '烦恼', '担忧', '害怕'
    ]
    
    NEUTRAL_WORDS = ['一般', '普通', '还行', '可以', '差不多', '还好', '将就', '一般般']
    
    # 情感强度修饰词
    INTENSIFIERS = ['非常', '特别', '十分', '极其', '真的', '太', '很', '特别']
    REDUCERS = ['有点', '稍微', '略微', '一点点']
    
    def analyze(self, text: str) -> Tuple[str, float]:
        """
        分析情感（增强版）
        
        Args:
            text: 用户输入文本
        
        Returns:
            (情感类型, 置信度)
        """
        text_lower = text.lower()
        
        # 计算情感词数量
        pos_count = 0
        neg_count = 0
        neu_count = 0
        
        # 检查每个词是否在文本中，并考虑强度修饰词
        for word in self.POSITIVE_WORDS:
            if word in text_lower:
                count = text_lower.count(word)
                # 检查是否有强度修饰词
                for intensifier in self.INTENSIFIERS:
                    if intensifier in text_lower:
                        count *= 1.5
                for reducer in self.REDUCERS:
                    if reducer in text_lower:
                        count *= 0.5
                pos_count += count
        
        for word in self.NEGATIVE_WORDS:
            if word in text_lower:
                count = text_lower.count(word)
                for intensifier in self.INTENSIFIERS:
                    if intensifier in text_lower:
                        count *= 1.5
                for reducer in self.REDUCERS:
                    if reducer in text_lower:
                        count *= 0.5
                neg_count += count
        
        for word in self.NEUTRAL_WORDS:
            if word in text_lower:
                neu_count += text_lower.count(word)
        
        total = pos_count + neg_count + neu_count
        
        if total == 0:
            return 'neutral', 0.5
        
        pos_score = pos_count / total
        neg_score = neg_count / total
        
        # 计算置信度
        confidence = min(total / 5, 1.0)  # 匹配越多，置信度越高
        
        if pos_score > neg_score:
            if pos_score - neg_score > 0.2:
                return 'positive', min(confidence, pos_score)
            else:
                return 'neutral', 0.5 + (pos_score - neg_score) * confidence
        elif neg_score > pos_score:
            if neg_score - pos_score > 0.2:
                return 'negative', min(confidence, neg_score)
            else:
                return 'neutral', 0.5 + (pos_score - neg_score) * confidence
        else:
            return 'neutral', confidence


class ContextManager:
    """上下文管理器"""
    
    def __init__(self, window_size: int = 50):
        self._contexts: Dict[str, List[Dict]] = {}
        self._window_size = window_size
    
    def add_message(self, session_id: str, role: str, content: str):
        """添加消息到上下文"""
        if session_id not in self._contexts:
            self._contexts[session_id] = []
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
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
    
    def get_user_profile(self, session_id: str) -> Optional[Dict]:
        """从上下文中提取用户画像（只从用户消息中提取）"""
        context = self.get_context(session_id)
        profile = {}
        
        for msg in context:
            # 只从用户消息中提取信息
            if msg.get('role') != 'user':
                continue
            
            content = msg.get('content', '')
            
            # 提取地区信息（优先匹配常见区县名）
            if not profile.get('district'):
                common_districts = ['五华区', '盘龙区', '官渡区', '西山区', '呈贡区', 
                                   '麒麟区', '宣威市', '大理市', '蒙自市', '文山市',
                                   '景洪市', '瑞丽市', '芒市', '香格里拉市',
                                   '江川区', '澄江市', '通海县', '华宁县', '易门县',
                                   '新平县', '元江县', '峨山县', '红塔区',
                                   '昭阳区', '鲁甸县', '巧家县', '盐津县', '大关县',
                                   '永善县', '绥江县', '镇雄县', '彝良县', '威信县',
                                   '水富市', '麒麟区', '马龙区', '陆良县', '师宗县',
                                   '罗平县', '富源县', '会泽县', '宣威市',
                                   '沾益区', '玉州区', '江川区', '澄江市', '通海县',
                                   '华宁县', '易门县', '新平县', '元江县', '峨山县',
                                   '红塔区', '隆阳区', '施甸县', '腾冲市', '龙陵县',
                                   '昌宁县', '昭阳区', '鲁甸县', '巧家县', '盐津县',
                                   '大关县', '永善县', '绥江县', '镇雄县', '彝良县',
                                   '威信县', '水富市', '楚雄市', '双柏县', '牟定县',
                                   '南华县', '姚安县', '大姚县', '永仁县', '元谋县',
                                   '武定县', '禄丰县', '个旧市', '开远市', '蒙自市',
                                   '屏边县', '建水县', '石屏县', '弥勒市', '泸西县',
                                   '元阳县', '红河县', '金平县', '绿春县', '河口县',
                                   '文山市', '砚山县', '西畴县', '麻栗坡县', '马关县',
                                   '丘北县', '广南县', '富宁县', '景洪市', '勐海县',
                                   '勐腊县', '大理市', '漾濞县', '祥云县', '宾川县',
                                   '弥渡县', '南涧县', '巍山县', '永平县', '云龙县',
                                   '洱源县', '剑川县', '鹤庆县', '瑞丽市', '芒市',
                                   '陇川县', '盈江县', '梁河县', '泸水市', '福贡县',
                                   '贡山县', '兰坪县', '香格里拉市', '德钦县', '维西县',
                                   '临沧市', '凤庆县', '云县', '永德县', '镇康县',
                                   '双江县', '耿马县', '沧源县']
                
                for district in common_districts:
                    if district in content:
                        profile['district'] = district
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
    
    def clear_context(self, session_id: str):
        """清除会话上下文"""
        if session_id in self._contexts:
            del self._contexts[session_id]


class IntelligentChatManager:
    """智能对话管理器（集成深度语义分析和增强上下文管理）"""
    
    def __init__(self):
        self._intent_classifier = IntentClassifier()
        self._sentiment_analyzer = SentimentAnalyzer()
        # 使用增强版上下文管理器
        from .context_manager import get_enhanced_context_manager
        self._context_manager = get_enhanced_context_manager()
        # 导入智能响应生成器
        from .smart_response_generator import get_response_generator
        self._response_generator = get_response_generator()
        # 导入深度语义分析器
        from .semantic_analyzer import get_semantic_analyzer
        self._semantic_analyzer = get_semantic_analyzer()
        
        self._personality = {
            'name': '小智',
            'role': '云南省中考智能助手',
            'tone': 'friendly',
            'style': 'concise'
        }
        
        logger.info("智能对话管理器初始化完成（集成深度语义分析器和增强上下文管理器）")
    
    def process_message(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """
        处理用户消息（集成深度语义分析和增强上下文管理）
        
        Args:
            session_id: 会话ID
            user_input: 用户输入文本
        
        Returns:
            处理结果字典
        """
        # 添加用户消息到上下文
        self._context_manager.add_message(session_id, 'user', user_input)
        
        # 获取上下文信息
        context = self._context_manager.get_context(session_id)
        user_profile = self._context_manager.get_user_profile(session_id)
        
        # 获取主题信息
        current_topic = self._context_manager.get_current_topic(session_id)
        dominant_topic = self._context_manager.get_dominant_topic(session_id)
        topic_changed = self._context_manager.detect_topic_change(session_id)
        
        # 深度语义分析（包含同义词识别、指代消解、多意图识别）
        semantic_result = self._semantic_analyzer.analyze(user_input, context[:-1])
        
        # 意图识别（优先使用多意图识别结果）
        intents = semantic_result.get('intents', [])
        if intents:
            intent, intent_confidence = intents[0]
        else:
            intent, intent_confidence = self._intent_classifier.classify(user_input)
        
        # 情感分析
        sentiment, sentiment_confidence = self._sentiment_analyzer.analyze(user_input)
        
        # 生成响应（传入语义分析结果）
        response, response_info = self._generate_response(
            user_input, 
            intent, 
            sentiment, 
            context, 
            user_profile,
            semantic_result
        )
        
        # 添加助手响应到上下文
        self._context_manager.add_message(session_id, 'assistant', response)
        
        # 生成会话摘要
        summary = self._context_manager.generate_summary(session_id)
        
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
            'intents': intents,
            'synonyms': semantic_result.get('synonyms', []),
            'resolutions': semantic_result.get('resolutions', {}),
            'entities': semantic_result.get('entities', []),
            'intent_combinations': semantic_result.get('intent_combinations', []),
            # 主题追踪信息
            'current_topic': current_topic,
            'dominant_topic': dominant_topic,
            'topic_changed': topic_changed,
            # 会话摘要
            'summary': summary,
            **response_info
        }
    
    def _generate_response(self, user_input: str, intent: str, sentiment: str, 
                          context: List[Dict], user_profile: Optional[Dict],
                          semantic_result: Optional[Dict] = None) -> Tuple[str, Dict]:
        """
        生成响应（支持语义分析结果）
        
        Args:
            user_input: 用户输入
            intent: 意图
            sentiment: 情感
            context: 上下文
            user_profile: 用户画像
            semantic_result: 语义分析结果
        
        Returns:
            (响应文本, 附加信息)
        """
        # 使用智能响应生成器生成响应（传入语义分析结果）
        response = self._response_generator.generate_response(
            intent, sentiment, user_profile, context, semantic_result
        )
        
        return response, {'response_type': intent}
    
    def _handle_school_selection(self, user_input: str, user_profile: Optional[Dict]) -> Tuple[str, Dict]:
        """处理择校相关问题"""
        district = user_profile.get('district') if user_profile else None
        
        if district:
            response = f"""🏫 好的！我来帮你分析{district}的择校情况。
            
根据云南省招生政策，{district}的考生通常可以报考：
• 本地优质高中
• 省级重点中学（部分有全省招生资格）
• 民办优质高中

为了给你更准确的建议，我需要了解一下：
1. 你目前的成绩大概在什么水平？
2. 你更倾向于报考公办还是民办学校？
3. 有没有特别想报考的学校？"""
        else:
            response = """🏫 好的！我来帮你分析中考择校问题。
            
为了给你提供准确的建议，请告诉我：
1. 你的户籍所在地是哪个区县？
2. 你目前的成绩大概在什么水平？
3. 你更倾向于报考公办还是民办学校？

云南省实行各州市独立招生政策，了解你的户籍所在地很重要哦！"""
        
        return response, {'response_type': 'school_selection', 'district': district}
    
    def _handle_policy(self, user_input: str, user_profile: Optional[Dict]) -> Tuple[str, Dict]:
        """处理政策相关问题"""
        district = user_profile.get('district') if user_profile else None
        
        response = f"""📋 好的！我来帮你了解中考招生政策。
        
{'📍 已知你来自' + district if district else ''}

常见的招生政策问题包括：
• 录取分数线
• 志愿填报规则
• 加分政策
• 跨州市报考限制
• 特长生招生

请问你具体想了解哪方面的政策呢？"""
        
        return response, {'response_type': 'policy', 'district': district}
    
    def _handle_study_plan(self, user_input: str, user_profile: Optional[Dict]) -> Tuple[str, Dict]:
        """处理学习计划问题"""
        grade = user_profile.get('grade') if user_profile else '九年级'
        
        response = f"""📚 好的！我来帮你制定学习计划。

{'📌 已知你在读' + grade if grade else ''}

学习计划包括：
• 每日时间安排
• 各科复习策略
• 模拟考试计划
• 错题整理方法

请问你目前最想提升哪个科目？或者你有特定的时间安排需求吗？"""
        
        return response, {'response_type': 'study_plan', 'grade': grade}
    
    def _handle_question(self, user_input: str, context: List[Dict]) -> Tuple[str, Dict]:
        """处理一般性问题"""
        # 检查是否有上下文可以参考
        if len(context) > 1:
            response = """🤔 好的，我来帮你解答这个问题。
            
为了更准确地回答你，我需要确认一下：
你问的是关于刚才讨论的内容吗？还是有新的问题呢？

如果是新问题，麻烦你再详细说明一下，我会尽力帮你解答！"""
        else:
            response = """🤔 好的，请问你有什么问题呢？

我可以帮你解答关于：
• 中考招生政策
• 学校选择建议
• 备考学习计划
• 心理状态调整

请告诉我你的具体问题！"""
        
        return response, {'response_type': 'question'}
    
    def _handle_recommendation(self, user_input: str, user_profile: Optional[Dict]) -> Tuple[str, Dict]:
        """处理推荐请求"""
        district = user_profile.get('district') if user_profile else None
        
        response = f"""🎯 好的！我来给你推荐合适的学校。
        
{'📍 已知你来自' + district if district else ''}

为了给你准确的推荐，我需要了解：
1. 你目前的预估分数是多少？
2. 你更看重学校的哪些方面？（教学质量、升学率、校风、地理位置等）
3. 有没有预算方面的考虑？

告诉我这些信息，我会为你推荐最适合的学校！"""
        
        return response, {'response_type': 'recommendation', 'district': district}
    
    def _handle_emotional(self, user_input: str, sentiment: str) -> Tuple[str, Dict]:
        """处理情感表达"""
        if sentiment == 'negative':
            response = """💝 我理解你的感受，备考确实会有压力。

别担心，很多同学都会有这样的感觉。这里有一些建议：
• 适当运动可以缓解压力（散步、跑步、打球）
• 和家人朋友聊聊天，释放情绪
• 合理安排时间，不要过度疲劳
• 相信自己的努力，你已经很棒了！

如果需要的话，我可以帮你制定更合理的学习计划，减轻负担！"""
        else:
            response = """😊 很高兴听到你状态不错！保持积极的心态很重要。

继续加油，相信你的努力一定会有收获的！如果有任何问题，随时来找我！"""
        
        return response, {'response_type': 'emotional', 'sentiment': sentiment}
    
    def _handle_chat(self, user_input: str) -> Tuple[str, Dict]:
        """处理闲聊"""
        responses = [
            '好呀！我们可以聊聊中考备考的心得，或者你最近学习上遇到的问题！',
            '当然可以！你想聊点什么呢？学习、生活都可以哦！',
            '很高兴和你聊天！有什么想聊的尽管说！'
        ]
        
        import random
        return random.choice(responses), {'response_type': 'chat'}
    
    def _handle_default(self, user_input: str, context: List[Dict]) -> Tuple[str, Dict]:
        """处理未知意图"""
        # 如果上下文比较长，尝试追问
        if len(context) > 1:
            response = """📝 抱歉，我可能没完全理解你的意思。

为了更好地帮助你，可以请你再详细说明一下吗？

或者，你可以选择以下服务：
• 🏫 中考择校建议
• 📋 招生政策咨询
• 📚 备考学习计划
• 💝 心理状态调整"""
        else:
            response = """你好！我是云南省中考智能助手。

我可以帮你解答以下问题：
• 🏫 中考择校建议
• 📋 招生政策咨询（录取分数线、志愿填报等）
• 📚 备考学习计划（各科复习策略、时间管理）
• 💝 心理状态调整（压力缓解、心态调整）

请问你需要哪方面的帮助呢？"""
        
        return response, {'response_type': 'default'}
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """获取会话信息"""
        context = self._context_manager.get_context(session_id)
        user_profile = self._context_manager.get_user_profile(session_id)
        
        return {
            'session_id': session_id,
            'message_count': len(context),
            'user_profile': user_profile,
            'active': len(context) > 0
        }
    
    def clear_session(self, session_id: str):
        """清除会话"""
        self._context_manager.clear_context(session_id)
    
    def set_personality(self, name: str = None, tone: str = None, style: str = None):
        """设置助手个性"""
        if name:
            self._personality['name'] = name
        if tone:
            self._personality['tone'] = tone
        if style:
            self._personality['style'] = style


# 全局实例
intelligent_chat_manager = IntelligentChatManager()


def get_intelligent_chat_manager() -> IntelligentChatManager:
    """获取智能对话管理器实例"""
    return intelligent_chat_manager


# 便捷函数
def intelligent_chat(session_id: str, user_input: str) -> Dict[str, Any]:
    """便捷函数：智能对话"""
    return intelligent_chat_manager.process_message(session_id, user_input)


if __name__ == '__main__':
    # 测试智能对话管理器
    print("=" * 70)
    print("智能对话管理器测试")
    print("=" * 70)
    
    manager = IntelligentChatManager()
    
    # 模拟对话
    session_id = "test_session_001"
    
    test_messages = [
        "你好",
        "我是五华区的，想了解中考择校",
        "我的成绩大概580分左右",
        "推荐一些适合我的学校吧",
        "谢谢",
        "再见"
    ]
    
    for msg in test_messages:
        print(f"\n{'='*70}")
        print(f"用户: {msg}")
        print(f"{'='*70}")
        
        result = manager.process_message(session_id, msg)
        print(f"助手: {result['content']}")
        print(f"\n📊 意图: {result['intent']} ({result['intent_confidence']:.2f})")
        print(f"💭 情感: {result['sentiment']} ({result['sentiment_confidence']:.2f})")
        if result.get('user_profile'):
            print(f"👤 用户画像: {result['user_profile']}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)