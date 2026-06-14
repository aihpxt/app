#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能错题分析系统
帮助学生分析错题，找出薄弱环节，提供针对性学习建议
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ErrorAnalyzer:
    """错题分析器"""
    
    def __init__(self):
        self._error_patterns = self._load_error_patterns()
        self._subject_topics = self._load_subject_topics()
        logger.info("智能错题分析系统初始化完成")
    
    def _load_error_patterns(self) -> Dict[str, List[str]]:
        """加载错误模式"""
        return {
            '数学': {
                '函数': ['函数概念理解错误', '定义域值域判断错误', '函数图像识别错误'],
                '几何': ['辅助线添加错误', '角度计算错误', '相似三角形判定错误'],
                '代数': ['方程求解错误', '不等式解法错误', '因式分解错误'],
                '概率': ['概率计算错误', '排列组合错误', '期望方差计算错误']
            },
            '语文': {
                '阅读理解': ['主旨概括错误', '细节理解错误', '推理判断错误'],
                '作文': ['立意不明确', '结构混乱', '语言表达欠佳'],
                '古诗文': ['诗词理解错误', '文言实词虚词错误', '名句默写错误'],
                '语言运用': ['病句辨析错误', '成语使用错误', '标点符号错误']
            },
            '英语': {
                '听力': ['语音辨识错误', '数字记录错误', '信息抓取错误'],
                '语法': ['时态错误', '语态错误', '从句用法错误'],
                '阅读理解': ['主旨大意错误', '词义猜测错误', '推理判断错误'],
                '写作': ['句型单一', '语法错误', '逻辑不连贯']
            },
            '物理': {
                '力学': ['受力分析错误', '牛顿定律应用错误', '功和能计算错误'],
                '电学': ['电路分析错误', '欧姆定律应用错误', '电功率计算错误'],
                '光学': ['光的反射折射错误', '透镜成像错误', '色散现象错误'],
                '热学': ['温度热量内能混淆', '热传递方式错误', '物态变化判断错误']
            },
            '化学': {
                '化学方程式': ['配平错误', '化学式书写错误', '反应条件错误'],
                '实验': ['实验操作错误', '现象描述错误', '仪器使用错误'],
                '计算': ['物质的量计算错误', '溶液浓度计算错误', '化学平衡计算错误'],
                '元素周期': ['元素性质判断错误', '周期律应用错误', '化学键类型判断错误']
            }
        }
    
    def _load_subject_topics(self) -> Dict[str, List[str]]:
        """加载科目知识点"""
        return {
            '数学': ['函数', '几何', '代数', '概率', '三角函数', '数列', '导数'],
            '语文': ['阅读理解', '作文', '古诗文', '语言运用', '现代文阅读'],
            '英语': ['听力', '语法', '阅读理解', '写作', '完形填空', '词汇'],
            '物理': ['力学', '电学', '光学', '热学', '电磁学', '原子物理'],
            '化学': ['化学方程式', '实验', '计算', '元素周期', '有机化学', '化学反应']
        }
    
    def analyze_errors(self, errors: List[Dict]) -> Dict[str, Any]:
        """
        分析错题
        
        Args:
            errors: 错题列表，每个错题包含 subject, topic, error_type, error_count
        
        Returns:
            分析结果
        """
        # 统计各科错题数量
        subject_stats = {}
        topic_stats = {}
        
        for error in errors:
            subject = error.get('subject')
            topic = error.get('topic')
            
            # 更新科目统计
            if subject not in subject_stats:
                subject_stats[subject] = {'count': 0, 'topics': {}}
            subject_stats[subject]['count'] += 1
            
            # 更新知识点统计
            if topic not in subject_stats[subject]['topics']:
                subject_stats[subject]['topics'][topic] = 0
            subject_stats[subject]['topics'][topic] += 1
            
            # 更新全局知识点统计
            if topic not in topic_stats:
                topic_stats[topic] = {'count': 0, 'subjects': []}
            topic_stats[topic]['count'] += 1
            if subject not in topic_stats[topic]['subjects']:
                topic_stats[topic]['subjects'].append(subject)
        
        # 找出薄弱科目和知识点
        weak_subjects = self._identify_weak_subjects(subject_stats)
        weak_topics = self._identify_weak_topics(topic_stats)
        
        # 生成学习建议
        suggestions = self._generate_suggestions(weak_subjects, weak_topics, errors)
        
        return {
            'subject_stats': subject_stats,
            'topic_stats': topic_stats,
            'weak_subjects': weak_subjects,
            'weak_topics': weak_topics,
            'suggestions': suggestions,
            'total_errors': len(errors),
            'analysis_time': datetime.now().isoformat()
        }
    
    def _identify_weak_subjects(self, subject_stats: Dict) -> List[str]:
        """识别薄弱科目"""
        if not subject_stats:
            return []
        
        # 找出错题数量超过平均水平的科目
        avg_count = sum(s['count'] for s in subject_stats.values()) / len(subject_stats)
        weak_subjects = [sub for sub, stats in subject_stats.items() if stats['count'] > avg_count]
        
        # 按错题数量排序
        weak_subjects.sort(key=lambda x: subject_stats[x]['count'], reverse=True)
        
        return weak_subjects[:3]  # 返回前3个最薄弱的科目
    
    def _identify_weak_topics(self, topic_stats: Dict) -> List[str]:
        """识别薄弱知识点"""
        if not topic_stats:
            return []
        
        # 找出错题数量最多的知识点
        topics = sorted(topic_stats.items(), key=lambda x: x[1]['count'], reverse=True)
        weak_topics = [topic for topic, stats in topics[:5]]
        
        return weak_topics
    
    def _generate_suggestions(self, weak_subjects: List[str], weak_topics: List[str], errors: List[Dict]) -> List[str]:
        """生成学习建议"""
        suggestions = []
        
        # 根据薄弱科目生成建议
        for subject in weak_subjects:
            subject_suggestion = self._generate_subject_suggestion(subject)
            if subject_suggestion:
                suggestions.append(subject_suggestion)
        
        # 根据薄弱知识点生成建议
        for topic in weak_topics:
            topic_suggestion = self._generate_topic_suggestion(topic)
            if topic_suggestion:
                suggestions.append(topic_suggestion)
        
        # 通用建议
        suggestions.append(self._generate_general_suggestions(len(errors)))
        
        return suggestions
    
    def _generate_subject_suggestion(self, subject: str) -> Optional[str]:
        """生成科目学习建议"""
        suggestions = {
            '数学': f"📐 **{subject}** 错题较多，建议：\n• 每天做10-15道基础题巩固概念\n• 重点复习函数、几何等薄弱章节\n• 建立错题本，定期回顾",
            '语文': f"📖 **{subject}** 错题较多，建议：\n• 每天阅读一篇课外文章\n• 积累古诗文和成语\n• 每周写一篇作文并修改",
            '英语': f"🔤 **{subject}** 错题较多，建议：\n• 每天听30分钟听力材料\n• 背诵5-10个单词\n• 积累语法知识点",
            '物理': f"⚛️ **{subject}** 错题较多，建议：\n• 理解基本概念和公式\n• 多做实验题和计算题\n• 分析错题的物理过程",
            '化学': f"🧪 **{subject}** 错题较多，建议：\n• 熟记化学方程式\n• 理解实验原理\n• 多做计算题练习"
        }
        return suggestions.get(subject)
    
    def _generate_topic_suggestion(self, topic: str) -> Optional[str]:
        """生成知识点学习建议"""
        suggestions = {
            '函数': f"📈 **{topic}** 薄弱，建议：\n• 理解函数定义和性质\n• 多做函数图像题\n• 掌握函数的单调性、奇偶性判断",
            '几何': f"📐 **{topic}** 薄弱，建议：\n• 掌握常见辅助线添加方法\n• 多做证明题练习\n• 理解相似三角形和全等三角形判定",
            '阅读理解': f"📖 **{topic}** 薄弱，建议：\n• 学会快速定位关键信息\n• 练习概括文章主旨\n• 分析作者的写作意图",
            '语法': f"🔤 **{topic}** 薄弱，建议：\n• 系统学习语法知识点\n• 多做语法练习题\n• 注意时态和语态的正确使用",
            '力学': f"⚛️ **{topic}** 薄弱，建议：\n• 掌握受力分析方法\n• 理解牛顿三大定律\n• 多做应用题练习",
            '电学': f"⚡ **{topic}** 薄弱，建议：\n• 掌握电路分析方法\n• 理解欧姆定律和电功率公式\n• 多做电路计算题",
            '化学方程式': f"🧪 **{topic}** 薄弱，建议：\n• 熟记常见化学反应\n• 掌握配平方法\n• 注意反应条件和气体符号",
            '作文': f"✍️ **{topic}** 薄弱，建议：\n• 积累写作素材\n• 学习文章结构\n• 多写多练多修改"
        }
        return suggestions.get(topic)
    
    def _generate_general_suggestions(self, error_count: int) -> str:
        """生成通用学习建议"""
        if error_count > 20:
            return "📊 **学习建议**：\n• 错题量较多，建议每天花30分钟整理错题\n• 分析错误原因，避免重复犯错\n• 定期回顾错题本，巩固知识点"
        elif error_count > 10:
            return "📊 **学习建议**：\n• 错题量适中，继续保持错题整理习惯\n• 针对薄弱环节进行专项练习\n• 每周复习一次错题"
        else:
            return "📊 **学习建议**：\n• 错题量较少，继续保持\n• 可以适当增加练习难度\n• 定期回顾已掌握的知识点"
    
    def generate_report(self, errors: List[Dict], user_profile: Optional[Dict] = None) -> str:
        """
        生成错题分析报告
        
        Args:
            errors: 错题列表
            user_profile: 用户画像
        
        Returns:
            报告文本
        """
        analysis = self.analyze_errors(errors)
        
        report = f"""📊 错题分析报告

📋 基本信息
• 错题总数：{analysis['total_errors']}道
• 分析时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        
        # 用户信息
        if user_profile:
            report += f"""• 用户：{user_profile.get('grade', '')}年级
"""
        
        # 科目分布
        report += """

📚 科目错题分布：
"""
        for subject, stats in analysis['subject_stats'].items():
            report += f"• {subject}：{stats['count']}道\n"
            for topic, count in stats['topics'].items():
                report += f"  └─ {topic}：{count}道\n"
        
        # 薄弱环节
        if analysis['weak_subjects']:
            report += f"""

⚠️ 薄弱科目：{', '.join(analysis['weak_subjects'])}
"""
        
        if analysis['weak_topics']:
            report += f"""⚠️ 薄弱知识点：{', '.join(analysis['weak_topics'])}
"""
        
        # 学习建议
        report += """

💡 学习建议：
"""
        for suggestion in analysis['suggestions']:
            report += f"{suggestion}\n\n"
        
        return report


# 全局实例
error_analyzer = ErrorAnalyzer()


def get_error_analyzer() -> ErrorAnalyzer:
    """获取错题分析器实例"""
    return error_analyzer


if __name__ == '__main__':
    # 测试错题分析系统
    print("=" * 70)
    print("智能错题分析系统测试")
    print("=" * 70)
    
    analyzer = ErrorAnalyzer()
    
    # 测试数据
    test_errors = [
        {'subject': '数学', 'topic': '函数', 'error_type': '概念理解错误', 'error_count': 5},
        {'subject': '数学', 'topic': '几何', 'error_type': '辅助线添加错误', 'error_count': 4},
        {'subject': '数学', 'topic': '代数', 'error_type': '方程求解错误', 'error_count': 3},
        {'subject': '英语', 'topic': '语法', 'error_type': '时态错误', 'error_count': 4},
        {'subject': '英语', 'topic': '阅读理解', 'error_type': '主旨大意错误', 'error_count': 3},
        {'subject': '物理', 'topic': '力学', 'error_type': '受力分析错误', 'error_count': 6},
        {'subject': '物理', 'topic': '电学', 'error_type': '电路分析错误', 'error_count': 3},
        {'subject': '化学', 'topic': '化学方程式', 'error_type': '配平错误', 'error_count': 2},
        {'subject': '语文', 'topic': '阅读理解', 'error_type': '主旨概括错误', 'error_count': 3},
        {'subject': '语文', 'topic': '作文', 'error_type': '立意不明确', 'error_count': 2}
    ]
    
    print("\n📊 测试错题数据：")
    print(f"共 {len(test_errors)} 条错题记录")
    
    # 生成报告
    print("\n" + "=" * 70)
    print("错题分析报告")
    print("=" * 70)
    
    report = analyzer.generate_report(test_errors, {'grade': '九年级'})
    print(report)
    
    print("=" * 70)
    print("测试完成！")
    print("=" * 70)