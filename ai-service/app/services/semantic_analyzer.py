#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度语义理解分析器
提供同义词识别、指代消解、多意图组合识别等能力
"""

import logging
from typing import Dict, Any, Optional, List, Tuple, Set
import re

logger = logging.getLogger(__name__)


class SynonymExpander:
    """同义词扩展器"""
    
    # 中考领域同义词词典
    SYNONYM_GROUPS = {
        'school': ['中学', '高中', '初中', '学校', '院校', '学府', '中学部', '高中部'],
        'exam': ['中考', '考试', '升学考试', '初中毕业考试', '中招考试'],
        'score': ['分数', '成绩', '总分', '考分', '得分', '分数段', '估分'],
        'admission': ['录取', '招生', '报考', '投档', '入学', '升学'],
        'policy': ['政策', '规定', '规则', '办法', '方案', '通知'],
        'recommendation': ['推荐', '建议', '指导', '参考', '选择', '择校'],
        'study': ['学习', '复习', '备考', '复习备考', '学习计划'],
        'tuition': ['学费', '费用', '收费', '学杂费', '开支'],
        'location': ['地址', '位置', '校区', '地点', '校址'],
        'major': ['专业', '学科', '科目', '课程'],
        'teacher': ['老师', '教师', '师资', '教员'],
        'campus': ['校园', '校区', '校舍', '学校环境'],
        'rate': ['升学率', '一本率', '本科率', '上线率'],
        'line': ['分数线', '录取线', '投档线', '省控线', '最低分'],
        'probability': ['概率', '可能性', '机会', '希望'],
        'compare': ['对比', '比较', '差异', '区别'],
        'question': ['问题', '疑问', '困惑', '难题'],
        'help': ['帮助', '帮忙', '协助', '支持'],
        'thank': ['谢谢', '感谢', '多谢', '辛苦了'],
        'hello': ['你好', '您好', '嗨', '哈喽'],
        'goodbye': ['再见', '拜拜', '告辞', '先走了']
    }
    
    # 反向映射：词 -> 主词
    _word_to_main: Dict[str, str] = {}
    
    def __init__(self):
        # 构建反向映射
        for main_word, synonyms in self.SYNONYM_GROUPS.items():
            for word in synonyms:
                self._word_to_main[word] = main_word
    
    def expand(self, text: str) -> str:
        result = text
        for word, main_word in self._word_to_main.items():
            if word in result:
                result = result.replace(word, f"{word}({main_word})")
        return result
    
    def get_main_word(self, word: str) -> Optional[str]:
        return self._word_to_main.get(word)
    
    def get_synonyms(self, word: str) -> List[str]:
        main_word = self._word_to_main.get(word)
        if main_word:
            return self.SYNONYM_GROUPS.get(main_word, [])
        return []
    
    def match_synonym_group(self, text: str) -> List[str]:
        matched_groups = []
        for main_word, synonyms in self.SYNONYM_GROUPS.items():
            for synonym in synonyms:
                if synonym in text:
                    matched_groups.append(main_word)
                    break
        return matched_groups


class CoreferenceResolver:
    """指代消解器"""
    
    PRONOUNS = ['它', '他', '她', '这', '那', '这个', '那个', '这些', '那些',
                '该', '此', '其', '上述', '以上', '下面', '前面', '后面']
    
    def resolve(self, text: str, context: List[Dict]) -> Tuple[str, Dict]:
        resolved_text = text
        resolutions = {}
        
        entities = self._extract_entities(context)
        
        for pronoun in self.PRONOUNS:
            if pronoun in resolved_text:
                best_entity = self._find_best_entity(pronoun, entities)
                if best_entity:
                    resolved_text = resolved_text.replace(pronoun, f"{pronoun}({best_entity})")
                    resolutions[pronoun] = best_entity
        
        return resolved_text, resolutions
    
    def _extract_entities(self, context: List[Dict]) -> List[str]:
        entities = []
        
        school_patterns = [
            r'(师大附中|昆一中|昆三中|昆八中|云大附中|滇池中学|民族中学|实验中学|外国语学校)',
            r'([\u4e00-\u9fa5]+中学)',
            r'([\u4e00-\u9fa5]+高中)'
        ]
        
        score_pattern = r'(\d{2,3})\s*分'
        district_pattern = r'([\u4e00-\u9fa5]+区|[\u4e00-\u9fa5]+市|[\u4e00-\u9fa5]+县)'
        
        for msg in context:
            content = msg.get('content', '')
            
            for pattern in school_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, tuple):
                        entities.extend(match)
                    else:
                        entities.append(match)
            
            score_matches = re.findall(score_pattern, content)
            entities.extend([f"{s}分" for s in score_matches])
            
            district_matches = re.findall(district_pattern, content)
            entities.extend(district_matches)
        
        unique_entities = []
        seen = set()
        for entity in reversed(entities):
            clean_entity = entity.strip()
            if clean_entity and clean_entity not in seen:
                seen.add(clean_entity)
                unique_entities.append(clean_entity)
        
        return list(reversed(unique_entities))
    
    def _find_best_entity(self, pronoun: str, entities: List[str]) -> Optional[str]:
        if not entities:
            return None
        
        singular_pronouns = ['它', '他', '她', '这', '那', '这个', '那个', '该', '此', '其']
        plural_pronouns = ['这些', '那些']
        
        if pronoun in singular_pronouns:
            for entity in entities:
                if '中学' in entity or '高中' in entity or '学校' in entity:
                    return entity
            return entities[0]
        elif pronoun in plural_pronouns:
            return entities[0] if entities else None
        
        return entities[0] if entities else None


class MultiIntentRecognizer:
    """多意图识别器"""
    
    _SIMPLE_INTENTS = {
        'school_selection': {
            'keywords': ['选学校', '择校', '高中', '中学', '报考', '志愿', '填报志愿'],
            'patterns': [r'.*选.*学校.*', r'.*择校.*', r'.*报考.*高中.*']
        },
        'policy': {
            'keywords': ['政策', '招生', '录取', '分数线', '加分', '投档'],
            'patterns': [r'.*政策.*', r'.*招生.*', r'.*录取.*', r'.*分数线.*']
        },
        'recommendation': {
            'keywords': ['推荐', '建议', '哪个好', '比较', '更好'],
            'patterns': [r'.*推荐.*', r'.*建议.*', r'.*哪个.*好.*']
        },
        'score': {
            'keywords': ['分数', '成绩', '多少分', '总分', '估分'],
            'patterns': [r'.*分数.*', r'.*成绩.*', r'.*多少分.*']
        },
        'school_info': {
            'keywords': ['学校', '中学', '高中', '附中', '校区', '地址', '学费'],
            'patterns': [r'.*学校.*', r'.*中学.*', r'.*高中.*']
        },
        'tuition': {
            'keywords': ['学费', '费用', '收费', '多少钱'],
            'patterns': [r'.*学费.*', r'.*费用.*', r'.*收费.*']
        },
        'school_compare': {
            'keywords': ['对比', '比较', '区别', '差异'],
            'patterns': [r'.*对比.*', r'.*比较.*', r'.*区别.*']
        },
        'admission_probability': {
            'keywords': ['录取概率', '能不能上', '录取可能性', '考上'],
            'patterns': [r'.*录取.*概率.*', r'.*能不能.*上.*']
        },
        'study_plan': {
            'keywords': ['学习计划', '复习', '备考', '时间安排'],
            'patterns': [r'.*学习计划.*', r'.*复习.*', r'.*备考.*']
        },
        'emotional': {
            'keywords': ['压力', '焦虑', '紧张', '担心', '烦', '累'],
            'patterns': [r'.*压力.*', r'.*焦虑.*', r'.*担心.*']
        },
        'greeting': {
            'keywords': ['你好', '您好', '嗨', 'Hello', 'Hi'],
            'patterns': [r'^你好.*', r'^您好.*', r'^嗨.*']
        },
        'farewell': {
            'keywords': ['再见', '拜拜', 'goodbye', 'bye'],
            'patterns': [r'.*再见.*', r'.*拜拜.*']
        },
        'thanks': {
            'keywords': ['谢谢', '谢谢你', '感谢', '辛苦了'],
            'patterns': [r'.*谢谢.*', r'.*感谢.*']
        },
        'chat': {
            'keywords': ['聊聊天', '随便聊聊', '谈谈', '说说'],
            'patterns': [r'.*聊聊.*', r'.*谈谈.*']
        },
        'question': {
            'keywords': ['什么', '怎么', '为什么', '如何', '哪个'],
            'patterns': [r'^什么.*', r'^怎么.*', r'^为什么.*']
        }
    }
    
    def __init__(self):
        self._intent_classifier = None
        try:
            from .intelligent_chat_manager import IntentClassifier
            self._intent_classifier = IntentClassifier()
        except ImportError:
            self._intent_classifier = None
            logger.warning("无法导入IntentClassifier，将使用简化的意图配置")
    
    def recognize(self, text: str, threshold: float = 0.3) -> List[Tuple[str, float]]:
        text_lower = text.lower()
        scores = {}
        
        if self._intent_classifier and hasattr(self._intent_classifier, 'INTENTS'):
            intents_config = self._intent_classifier.INTENTS
        else:
            intents_config = self._SIMPLE_INTENTS
        
        for intent, config in intents_config.items():
            score = 0
            matched_keywords = 0
            
            for keyword in config['keywords']:
                if keyword.lower() in text_lower:
                    matched_keywords += 1
                    keyword_weight = min(len(keyword) / 4, 1.0)
                    score += 0.2 * keyword_weight
            
            for pattern in config.get('patterns', []):
                if re.match(pattern, text_lower) or re.search(pattern, text_lower):
                    score += 0.3
            
            if score >= threshold:
                scores[intent] = min(score, 1.0)
        
        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_intents
    
    def get_intent_combinations(self, intents: List[Tuple[str, float]]) -> List[str]:
        intent_names = [intent[0] for intent in intents]
        combinations = []
        
        combination_rules = [
            (['school_selection', 'score'], '根据分数推荐学校'),
            (['school_selection', 'tuition'], '考虑学费的学校选择'),
            (['school_selection', 'school_compare'], '学校对比选择'),
            (['policy', 'score'], '分数相关政策'),
            (['recommendation', 'school_info'], '学校信息推荐'),
            (['study_plan', 'score'], '基于分数的学习计划'),
            (['emotional', 'study_plan'], '缓解压力的学习计划'),
            (['school_info', 'tuition'], '学校费用信息'),
            (['school_info', 'rate'], '学校升学率信息'),
            (['admission_probability', 'score'], '分数录取概率')
        ]
        
        for intent_set, description in combination_rules:
            if all(intent in intent_names for intent in intent_set):
                combinations.append(description)
        
        return combinations


class SemanticAnalyzer:
    """深度语义分析器"""
    
    def __init__(self):
        self._synonym_expander = SynonymExpander()
        self._coreference_resolver = CoreferenceResolver()
        self._multi_intent_recognizer = MultiIntentRecognizer()
        
        logger.info("深度语义分析器初始化完成")
    
    def analyze(self, text: str, context: List[Dict]) -> Dict[str, Any]:
        result = {
            'original_text': text,
            'synonyms': [],
            'resolved_text': text,
            'resolutions': {},
            'intents': [],
            'intent_combinations': [],
            'entities': []
        }
        
        expanded_text = self._synonym_expander.expand(text)
        matched_groups = self._synonym_expander.match_synonym_group(text)
        result['synonyms'] = matched_groups
        
        resolved_text, resolutions = self._coreference_resolver.resolve(text, context)
        result['resolved_text'] = resolved_text
        result['resolutions'] = resolutions
        
        intents = self._multi_intent_recognizer.recognize(text)
        result['intents'] = intents
        
        combinations = self._multi_intent_recognizer.get_intent_combinations(intents)
        result['intent_combinations'] = combinations
        
        entities = self._coreference_resolver._extract_entities(context + [{'content': text}])
        result['entities'] = entities
        
        return result
    
    def expand_synonyms(self, text: str) -> str:
        return self._synonym_expander.expand(text)
    
    def resolve_coreference(self, text: str, context: List[Dict]) -> Tuple[str, Dict]:
        return self._coreference_resolver.resolve(text, context)
    
    def recognize_intents(self, text: str) -> List[Tuple[str, float]]:
        return self._multi_intent_recognizer.recognize(text)


semantic_analyzer = SemanticAnalyzer()


def get_semantic_analyzer() -> SemanticAnalyzer:
    return semantic_analyzer


def analyze_semantics(text: str, context: List[Dict] = None) -> Dict[str, Any]:
    if context is None:
        context = []
    return semantic_analyzer.analyze(text, context)


if __name__ == '__main__':
    print("=" * 70)
    print("深度语义分析器测试")
    print("=" * 70)
    
    analyzer = SemanticAnalyzer()
    
    print("\n1. 同义词扩展测试")
    test_text = "哪所中学升学率高"
    print(f"原文: {test_text}")
    print(f"扩展: {analyzer.expand_synonyms(test_text)}")
    
    print("\n2. 指代消解测试")
    context = [
        {'role': 'user', 'content': '师大附中怎么样？'},
        {'role': 'assistant', 'content': '师大附中是云南省重点中学...'}
    ]
    text = "它的录取分数线是多少？"
    resolved, resolutions = analyzer.resolve_coreference(text, context)
    print(f"原文: {text}")
    print(f"解析: {resolved}")
    print(f"指代映射: {resolutions}")
    
    print("\n3. 多意图识别测试")
    text = "推荐一些适合580分的学校，顺便说一下学费"
    intents = analyzer.recognize_intents(text)
    print(f"原文: {text}")
    print(f"识别意图: {intents}")
    
    print("\n4. 完整语义分析")
    context = [
        {'role': 'user', 'content': '我是五华区的考生'},
        {'role': 'user', 'content': '师大附中怎么样？'}
    ]
    text = "它的录取分数线是多少？学费贵吗？"
    result = analyzer.analyze(text, context)
    print(f"原文: {text}")
    print(f"同义词组: {result['synonyms']}")
    print(f"解析文本: {result['resolved_text']}")
    print(f"指代映射: {result['resolutions']}")
    print(f"识别意图: {result['intents']}")
    print(f"意图组合: {result['intent_combinations']}")
    print(f"提取实体: {result['entities']}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)