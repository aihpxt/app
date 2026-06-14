#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能总结服务
支持对话总结、要点提取和自动追问
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class IntelligentSummarizer:
    """智能总结器"""
    
    def __init__(self):
        self._summary_templates = {
            'school_selection': {
                'title': '择校咨询总结',
                'fields': ['district', 'score', 'preferred_type', 'preferred_features'],
                'format': """## 择校咨询总结
                
### 用户信息
- 地区：{district}
- 预估分数：{score}分
- 偏好类型：{preferred_type}
- 偏好特色：{preferred_features}

### 已提供的建议
• 分析了{district}的招生政策
• 推荐了匹配的学校
• 提供了志愿填报建议

需要我继续为你推荐更多学校，还是详细介绍某所学校？"""
            },
            'study_plan': {
                'title': '学习计划总结',
                'fields': ['grade', 'scores', 'weak_subjects'],
                'format': """## 学习计划总结
                
### 当前情况
- 年级：{grade}
- 各科成绩：{scores}
- 薄弱科目：{weak_subjects}

### 已制定的计划
• 每日学习时间分配
• 薄弱科目提升方案
• 考前冲刺计划

需要我调整学习计划，还是提供更多学习资源？"""
            },
            'policy': {
                'title': '政策咨询总结',
                'fields': ['district', 'topic'],
                'format': """## 政策咨询总结
                
### 查询内容
- 地区：{district}
- 主题：{topic}

### 已解答的问题
• 招生政策要点
• 录取规则说明
• 注意事项提醒

还有其他政策问题需要了解吗？"""
            }
        }
        logger.info("智能总结器初始化完成")
    
    def summarize_conversation(self, context: List[Dict], intent: str = None) -> str:
        """
        总结对话内容
        
        Args:
            context: 对话上下文
            intent: 当前意图
        
        Returns:
            总结文本
        """
        # 提取关键信息
        info = self._extract_info(context)
        
        # 根据意图选择模板
        template = self._summary_templates.get(intent, None)
        
        if template:
            # 填充模板
            try:
                return template['format'].format(**info)
            except KeyError:
                # 如果模板字段不完整，生成通用总结
                return self._generate_generic_summary(context, info)
        else:
            return self._generate_generic_summary(context, info)
    
    def _extract_info(self, context: List[Dict]) -> Dict[str, Any]:
        """从上下文中提取关键信息"""
        info = {
            'district': '未提供',
            'score': '未提供',
            'grade': '未提供',
            'preferred_type': '未指定',
            'preferred_features': '未指定',
            'weak_subjects': [],
            'scores': {},
            'topic': '未指定'
        }
        
        for msg in context:
            content = msg.get('content', '')
            
            # 提取地区
            if info['district'] == '未提供':
                common_districts = ['五华区', '盘龙区', '官渡区', '西山区', '呈贡区',
                                   '麒麟区', '大理市', '蒙自市', '文山市', '景洪市']
                for district in common_districts:
                    if district in content:
                        info['district'] = district
                        break
            
            # 提取分数
            if info['score'] == '未提供':
                import re
                match = re.search(r'(\d{2,3})\s*分', content)
                if match:
                    info['score'] = match.group(1)
            
            # 提取年级
            if info['grade'] == '未提供':
                if '初三' in content or '九年级' in content:
                    info['grade'] = '九年级'
                elif '初二' in content or '八年级' in content:
                    info['grade'] = '八年级'
            
            # 提取偏好类型
            if info['preferred_type'] == '未指定':
                if '公办' in content:
                    info['preferred_type'] = '公办学校'
                elif '民办' in content:
                    info['preferred_type'] = '民办学校'
                elif '重点' in content:
                    info['preferred_type'] = '重点中学'
            
            # 提取偏好特色
            if info['preferred_features'] == '未指定':
                features = []
                if '理科' in content:
                    features.append('理科强')
                if '文科' in content:
                    features.append('文科强')
                if '艺术' in content:
                    features.append('艺术特色')
                if features:
                    info['preferred_features'] = '、'.join(features)
            
            # 提取科目成绩
            subjects = ['语文', '数学', '英语', '物理', '化学']
            for subject in subjects:
                pattern = rf'{subject}[：:]?\s*(\d{{2,3}})\s*分'
                match = re.search(pattern, content)
                if match and subject not in info['scores']:
                    info['scores'][subject] = match.group(1)
        
        return info
    
    def _generate_generic_summary(self, context: List[Dict], info: Dict) -> str:
        """生成通用总结"""
        user_messages = [msg for msg in context if msg.get('role') == 'user']
        message_count = len(user_messages)
        
        summary = f"""## 对话总结

### 对话概况
- 消息数：{message_count}条
- 时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

### 已了解的信息
"""
        
        if info['district'] != '未提供':
            summary += f"- 地区：{info['district']}\n"
        if info['score'] != '未提供':
            summary += f"- 预估分数：{info['score']}分\n"
        if info['grade'] != '未提供':
            summary += f"- 年级：{info['grade']}\n"
        if info['preferred_type'] != '未指定':
            summary += f"- 学校类型偏好：{info['preferred_type']}\n"
        if info['scores']:
            summary += f"- 各科成绩：{', '.join([f'{k}: {v}分' for k, v in info['scores'].items()])}\n"
        
        summary += """

### 接下来可以做什么？
• 继续了解中考招生政策
• 获取学校推荐
• 制定学习计划
• 了解志愿填报流程

请问你想继续了解哪方面的内容？"""
        
        return summary
    
    def suggest_follow_up(self, context: List[Dict]) -> Optional[str]:
        """
        根据对话历史建议后续问题
        
        Args:
            context: 对话上下文
        
        Returns:
            建议的追问问题
        """
        info = self._extract_info(context)
        gaps = []
        
        # 检查缺失的关键信息
        if info['district'] == '未提供':
            gaps.append('户籍所在地')
        if info['score'] == '未提供':
            gaps.append('预估分数')
        if info['grade'] == '未提供':
            gaps.append('年级')
        
        if gaps:
            return f"为了给你更准确的建议，我还需要了解一下：{'、'.join(gaps)}，可以告诉我吗？"
        
        # 如果信息完整，建议下一步
        if info['district'] != '未提供' and info['score'] != '未提供':
            return "需要我为你生成详细的学校推荐报告吗？"
        
        return None


class IntelligentFollowUp:
    """智能追问器"""
    
    def __init__(self):
        self._follow_up_rules = [
            {
                'trigger': ['推荐', '学校'],
                'conditions': {'district': '未提供'},
                'question': '为了推荐学校，我需要知道你的户籍所在地是哪个区县，可以告诉我吗？'
            },
            {
                'trigger': ['推荐', '学校'],
                'conditions': {'score': '未提供'},
                'question': '为了推荐合适的学校，我需要知道你的预估分数，可以告诉我吗？'
            },
            {
                'trigger': ['学习', '计划'],
                'conditions': {'grade': '未提供'},
                'question': '为了制定学习计划，我需要知道你目前在读几年级，可以告诉我吗？'
            },
            {
                'trigger': ['学习', '计划'],
                'conditions': {'scores': {}},
                'question': '为了制定针对性的学习计划，可以告诉我你的各科成绩吗？'
            },
            {
                'trigger': ['政策', '招生'],
                'conditions': {'district': '未提供'},
                'question': '不同地区的政策有所不同，请问你来自哪个区县？'
            }
        ]
    
    def generate_follow_up(self, context: List[Dict], last_intent: str) -> Optional[str]:
        """
        生成追问问题
        
        Args:
            context: 对话上下文
            last_intent: 最后识别的意图
        
        Returns:
            追问问题或None
        """
        summarizer = IntelligentSummarizer()
        info = summarizer._extract_info(context)
        
        # 获取最后一条用户消息
        user_messages = [msg for msg in context if msg.get('role') == 'user']
        if not user_messages:
            return None
        
        last_message = user_messages[-1]['content']
        
        # 检查规则
        for rule in self._follow_up_rules:
            # 检查触发词
            has_trigger = any(trigger in last_message for trigger in rule['trigger'])
            
            if has_trigger:
                # 检查条件
                conditions_met = True
                for key, value in rule['conditions'].items():
                    if key == 'scores':
                        if info.get(key) != value:
                            conditions_met = False
                    elif info.get(key) != value:
                        conditions_met = False
                
                if conditions_met:
                    return rule['question']
        
        return None


# 全局实例
summarizer = IntelligentSummarizer()
follow_up = IntelligentFollowUp()


def get_summarizer() -> IntelligentSummarizer:
    """获取智能总结器实例"""
    return summarizer


def get_follow_up() -> IntelligentFollowUp:
    """获取智能追问器实例"""
    return follow_up


if __name__ == '__main__':
    # 测试智能总结器
    print("=" * 70)
    print("智能总结器测试")
    print("=" * 70)
    
    # 模拟对话上下文
    context = [
        {'role': 'user', 'content': '你好，我是五华区的初三学生'},
        {'role': 'assistant', 'content': '你好！很高兴为你服务！'},
        {'role': 'user', 'content': '我的预估分数大概是580分'},
        {'role': 'assistant', 'content': '好的，我知道了你的情况'},
        {'role': 'user', 'content': '我想报考理科强的公办学校'},
        {'role': 'assistant', 'content': '好的，我来帮你分析'}
    ]
    
    summarizer = IntelligentSummarizer()
    
    # 测试总结功能
    print("\n📝 测试总结功能：")
    summary = summarizer.summarize_conversation(context, 'school_selection')
    print(summary)
    
    # 测试追问建议
    print("\n" + "=" * 70)
    print("智能追问测试")
    print("=" * 70)
    
    follow_up = IntelligentFollowUp()
    
    # 测试追问
    print("\n🔍 测试追问建议：")
    question = follow_up.generate_follow_up(context, 'school_selection')
    print(f"追问问题: {question if question else '无需追问'}")
    
    # 测试不完整信息的追问
    context_incomplete = [
        {'role': 'user', 'content': '我想让你推荐学校'}
    ]
    question = follow_up.generate_follow_up(context_incomplete, 'recommendation')
    print(f"\n不完整信息的追问: {question}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)