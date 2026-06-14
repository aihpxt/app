#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能追问与澄清引擎
负责检测信息缺失、处理模糊查询、确认多意图
"""

import logging
from typing import Dict, Any, Optional, List, Tuple, Set
import re

logger = logging.getLogger(__name__)


class ClarificationEngine:
    """智能追问与澄清引擎"""
    
    def __init__(self):
        # 需要的信息类型
        self.REQUIRED_INFO_TYPES = {
            'score': ['分数', '多少分', '考了', '成绩', '总分'],
            'school': ['学校', '中学', '高中', '附中', '一中', '二中', '三中'],
            'location': ['哪里', '哪个区', '哪个市', '位置', '地址', '地区'],
            'policy': ['政策', '分数线', '录取', '志愿', '加分'],
            'subject': ['科目', '语文', '数学', '英语', '物理', '化学']
        }
        
        # 模糊关键词模式
        self.AMBIGUITY_PATTERNS = {
            'school_ambiguity': re.compile(r'(哪个|哪些|什么)\s*(学校|中学|高中)'),
            'score_range': re.compile(r'(\d+)\s*(到|-)\s*(\d+)'),
            'vague_request': re.compile(r'(帮我|我想|推荐|介绍|分析)(.*?)(一下)?'),
            'missing_context': re.compile(r'(它|这个|那个|这样|那样)')
        }
        
        # 追问模板
        self.CLARIFICATION_TEMPLATES = {
            'missing_score': [
                '请问你的中考分数是多少呢？',
                '为了给你更精准的建议，能告诉我你的分数吗？',
                '想了解一下你的中考成绩大概是多少分？'
            ],
            'missing_school': [
                '你想了解哪所学校的信息呢？',
                '请问你关注的是哪所中学？',
                '能告诉我具体是哪所学校吗？'
            ],
            'missing_location': [
                '请问你想了解哪个地区的学校？',
                '你关注的是哪个城市或区域的学校呢？',
                '能告诉我你所在的地区吗？'
            ],
            'ambiguous_school': [
                '你说的是哪一所学校呢？可以说具体一点吗？',
                '我不太确定你指的是哪所学校，能补充说明一下吗？',
                '有几所学校比较相似，能告诉我具体是哪一所吗？'
            ],
            'confirm_intent': [
                '你是想了解{intent}吗？',
                '{intent}，对吗？',
                '你的意思是{intent}，我理解得对吗？'
            ],
            'multiple_intents': [
                '你有多个需求，包括{intents}，请问你想先了解哪个？',
                '我注意到你有几个问题，{intents}，先从哪一个开始呢？'
            ]
        }
        
        logger.info("智能追问与澄清引擎初始化完成")
    
    def detect_missing_info(self, message: str, context: Dict[str, Any]) -> List[str]:
        """
        检测缺失的必要信息
        
        Args:
            message: 用户消息
            context: 当前上下文
        
        Returns:
            缺失的信息类型列表
        """
        missing_info = []
        
        # 检查分数信息
        has_score = False
        score_patterns = [r'\d{3,4}', r'\d+分']
        for pattern in score_patterns:
            if re.search(pattern, message):
                has_score = True
                break
        if not has_score and context.get('score') is None:
            missing_info.append('score')
        
        # 检查学校信息
        has_school = False
        for keyword in self.REQUIRED_INFO_TYPES['school']:
            if keyword in message:
                has_school = True
                break
        if not has_school and context.get('school') is None:
            missing_info.append('school')
        
        # 检查位置信息
        has_location = False
        location_keywords = ['昆明', '五华', '盘龙', '西山', '官渡', '呈贡', '安宁']
        for keyword in location_keywords:
            if keyword in message:
                has_location = True
                break
        if not has_location and context.get('location') is None:
            missing_info.append('location')
        
        return missing_info
    
    def detect_ambiguity(self, message: str) -> List[str]:
        """
        检测模糊或歧义表达
        
        Args:
            message: 用户消息
        
        Returns:
            检测到的歧义类型列表
        """
        ambiguities = []
        
        # 检测学校歧义
        if self.AMBIGUITY_PATTERNS['school_ambiguity'].search(message):
            ambiguities.append('ambiguous_school')
        
        # 检测缺失上下文引用
        if self.AMBIGUITY_PATTERNS['missing_context'].search(message):
            ambiguities.append('missing_context')
        
        # 检测模糊请求
        if self.AMBIGUITY_PATTERNS['vague_request'].search(message):
            vague_groups = self.AMBIGUITY_PATTERNS['vague_request'].search(message).groups()
            if vague_groups and len(vague_groups[1].strip()) < 5:
                ambiguities.append('vague_request')
        
        return ambiguities
    
    def generate_clarification(self, missing_info: List[str], ambiguities: List[str], 
                               intents: Optional[List[str]] = None) -> Optional[str]:
        """
        生成澄清问题
        
        Args:
            missing_info: 缺失的信息类型列表
            ambiguities: 歧义类型列表
            intents: 检测到的意图列表
        
        Returns:
            澄清问题字符串，如果不需要澄清则返回None
        """
        # 优先处理歧义
        if 'missing_context' in ambiguities:
            return "你说的'它'或'这个'是指什么呢？可以说得更具体一些吗？"
        
        if 'ambiguous_school' in ambiguities:
            return self._get_template('ambiguous_school')
        
        if 'vague_request' in ambiguities:
            return "你想了解哪方面的信息呢？比如学校介绍、录取分数线、志愿填报建议等。"
        
        # 处理缺失信息 - 优先级：分数 > 学校 > 位置
        if 'score' in missing_info:
            return self._get_template('missing_score')
        
        if 'school' in missing_info:
            return self._get_template('missing_school')
        
        if 'location' in missing_info:
            return self._get_template('missing_location')
        
        # 处理多意图确认
        if intents and len(intents) > 1:
            intents_str = '、'.join(intents[:3])
            if len(intents) > 3:
                intents_str += '等'
            return self.CLARIFICATION_TEMPLATES['multiple_intents'][0].format(intents=intents_str)
        
        return None
    
    def _get_template(self, template_type: str) -> str:
        """获取追问模板"""
        templates = self.CLARIFICATION_TEMPLATES.get(template_type, [])
        if templates:
            return templates[0]
        return ""
    
    def confirm_intent(self, intent: str, confidence: float) -> Optional[str]:
        """
        当意图识别置信度较低时，确认用户意图
        
        Args:
            intent: 识别到的意图
            confidence: 置信度
        
        Returns:
            确认问题，如果置信度足够高则返回None
        """
        if confidence < 0.7:
            return self.CLARIFICATION_TEMPLATES['confirm_intent'][0].format(intent=intent)
        return None
    
    def analyze_and_clarify(self, message: str, context: Dict[str, Any], 
                            intents: Optional[List[Dict[str, float]]] = None) -> Tuple[bool, str]:
        """
        综合分析并生成澄清问题
        
        Args:
            message: 用户消息
            context: 当前上下文
            intents: 识别到的意图列表（包含置信度）
        
        Returns:
            (需要澄清标志, 澄清消息)
        """
        # 检测缺失信息
        missing_info = self.detect_missing_info(message, context)
        logger.debug(f"检测到缺失信息: {missing_info}")
        
        # 检测歧义
        ambiguities = self.detect_ambiguity(message)
        logger.debug(f"检测到歧义: {ambiguities}")
        
        # 提取意图列表
        intent_list = []
        if intents:
            intent_list = [intent['intent'] for intent in intents]
        
        # 生成澄清消息
        clarification = self.generate_clarification(missing_info, ambiguities, intent_list)
        
        if clarification:
            logger.info(f"生成澄清消息: {clarification}")
            return (True, clarification)
        
        return (False, "")
    
    def validate_response(self, message: str, expected_type: str) -> bool:
        """
        验证用户对追问的响应是否有效
        
        Args:
            message: 用户响应
            expected_type: 期望的信息类型
        
        Returns:
            是否有效
        """
        if expected_type == 'score':
            # 检查是否为有效的分数
            match = re.search(r'(\d{3,4})', message)
            if match and 300 <= int(match.group(1)) <= 700:
                return True
            return False
        
        elif expected_type == 'school':
            # 检查是否包含学校相关关键词
            for keyword in self.REQUIRED_INFO_TYPES['school']:
                if keyword in message:
                    return True
            # 检查是否为具体学校名称
            school_names = ['师大附中', '昆一中', '昆三中', '昆八中', '云大附中', '滇池中学']
            for name in school_names:
                if name in message or name[:2] in message:
                    return True
            return False
        
        elif expected_type == 'location':
            # 检查是否包含地区关键词
            locations = ['昆明', '五华', '盘龙', '西山', '官渡', '呈贡', '安宁']
            for location in locations:
                if location in message:
                    return True
            return False
        
        return True


# 全局实例
clarification_engine = ClarificationEngine()


def get_clarification_engine() -> ClarificationEngine:
    """获取澄清引擎实例"""
    return clarification_engine


if __name__ == '__main__':
    print("=" * 70)
    print("智能追问与澄清引擎测试")
    print("=" * 70)
    
    engine = ClarificationEngine()
    
    # 测试1: 检测缺失信息 - 缺少分数
    print("\n1. 测试缺失信息检测（缺少分数）")
    print("-" * 50)
    message = "我想了解昆一中的情况"
    context = {}
    missing = engine.detect_missing_info(message, context)
    print(f"用户消息: {message}")
    print(f"检测到缺失信息: {missing}")
    
    # 测试2: 检测缺失信息 - 已有分数
    print("\n2. 测试缺失信息检测（已有分数）")
    print("-" * 50)
    message = "我考了650分，想了解昆一中"
    context = {'score': 650}
    missing = engine.detect_missing_info(message, context)
    print(f"用户消息: {message}")
    print(f"检测到缺失信息: {missing}")
    
    # 测试3: 检测歧义 - 模糊学校
    print("\n3. 测试歧义检测（模糊学校）")
    print("-" * 50)
    message = "哪个学校比较好？"
    ambiguities = engine.detect_ambiguity(message)
    print(f"用户消息: {message}")
    print(f"检测到歧义: {ambiguities}")
    
    # 测试4: 检测歧义 - 缺失上下文
    print("\n4. 测试歧义检测（缺失上下文）")
    print("-" * 50)
    message = "它的录取分数线是多少？"
    ambiguities = engine.detect_ambiguity(message)
    print(f"用户消息: {message}")
    print(f"检测到歧义: {ambiguities}")
    
    # 测试5: 综合分析
    print("\n5. 测试综合分析")
    print("-" * 50)
    message = "帮我推荐学校"
    context = {}
    needs_clarify, response = engine.analyze_and_clarify(message, context)
    print(f"用户消息: {message}")
    print(f"需要澄清: {needs_clarify}")
    print(f"澄清消息: {response}")
    
    # 测试6: 意图确认
    print("\n6. 测试意图确认")
    print("-" * 50)
    confirm_msg = engine.confirm_intent('查询录取分数线', 0.65)
    print(f"置信度0.65时的确认消息: {confirm_msg}")
    confirm_msg = engine.confirm_intent('查询录取分数线', 0.85)
    print(f"置信度0.85时的确认消息: {confirm_msg}")
    
    # 测试7: 响应验证
    print("\n7. 测试响应验证")
    print("-" * 50)
    print(f"验证分数'650分': {engine.validate_response('650分', 'score')}")
    print(f"验证分数'abc': {engine.validate_response('abc', 'score')}")
    print(f"验证学校'昆一中': {engine.validate_response('昆一中', 'school')}")
    print(f"验证学校'好学校': {engine.validate_response('好学校', 'school')}")
    print(f"验证位置'五华区': {engine.validate_response('五华区', 'location')}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)