#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化学习建议生成器
根据用户成绩和学习数据自动生成个性化学习建议
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SubjectAnalyzer:
    """科目分析器"""
    
    SUBJECTS = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治']
    
    def __init__(self):
        self._subject_info = {
            '语文': {
                'total_score': 120,
                'weak_points': ['阅读理解', '作文', '古诗文', '文言文'],
                'improvement_methods': {
                    '阅读理解': '每天阅读一篇课外文章，练习概括主旨和分析人物',
                    '作文': '积累素材，每周写一篇作文并修改',
                    '古诗文': '每天背诵1-2首古诗，理解含义',
                    '文言文': '掌握常见实词虚词，翻译课文'
                }
            },
            '数学': {
                'total_score': 120,
                'weak_points': ['函数', '几何', '应用题', '代数运算'],
                'improvement_methods': {
                    '函数': '理解函数概念，多做图像题',
                    '几何': '掌握辅助线添加技巧，多练习证明题',
                    '应用题': '学会分析题意，建立数学模型',
                    '代数运算': '加强计算练习，避免粗心'
                }
            },
            '英语': {
                'total_score': 120,
                'weak_points': ['听力', '阅读理解', '语法', '写作'],
                'improvement_methods': {
                    '听力': '每天听30分钟听力材料',
                    '阅读理解': '精读文章，积累词汇',
                    '语法': '系统学习语法知识点，多做练习',
                    '写作': '背诵范文，每周写一篇作文'
                }
            },
            '物理': {
                'total_score': 100,
                'weak_points': ['力学', '电学', '光学', '热学'],
                'improvement_methods': {
                    '力学': '理解牛顿定律，多做受力分析',
                    '电学': '掌握电路分析方法',
                    '光学': '理解光的反射折射定律',
                    '热学': '掌握热力学基本概念'
                }
            },
            '化学': {
                'total_score': 80,
                'weak_points': ['化学方程式', '实验', '计算', '元素周期'],
                'improvement_methods': {
                    '化学方程式': '掌握配平方法，多练习',
                    '实验': '理解实验原理，记住操作步骤',
                    '计算': '掌握物质的量计算',
                    '元素周期': '理解周期律，记住常见元素性质'
                }
            }
        }
    
    def analyze_subject(self, subject: str, score: int) -> Dict[str, Any]:
        """
        分析科目成绩
        
        Args:
            subject: 科目名称
            score: 分数
        
        Returns:
            分析结果
        """
        info = self._subject_info.get(subject)
        if not info:
            return {'subject': subject, 'score': score, 'level': 'unknown'}
        
        total = info['total_score']
        percentage = (score / total) * 100
        
        if percentage >= 90:
            level = '优秀'
            suggestion = f'{subject}成绩优秀，保持状态，适当挑战难题'
        elif percentage >= 80:
            level = '良好'
            suggestion = f'{subject}成绩良好，巩固基础，提升弱项'
        elif percentage >= 60:
            level = '及格'
            suggestion = f'{subject}需要加强，重点攻克薄弱环节'
        else:
            level = '需努力'
            suggestion = f'{subject}基础薄弱，建议从基础知识点开始补习'
        
        return {
            'subject': subject,
            'score': score,
            'total_score': total,
            'percentage': round(percentage, 1),
            'level': level,
            'suggestion': suggestion,
            'weak_points': info['weak_points'],
            'improvement_methods': info['improvement_methods']
        }


class StudyPlanGenerator:
    """学习计划生成器"""
    
    def __init__(self):
        self._subject_analyzer = SubjectAnalyzer()
    
    def generate_daily_plan(self, scores: Dict[str, int], study_hours: float = 4.0) -> str:
        """
        生成每日学习计划
        
        Args:
            scores: 各科成绩
            study_hours: 每日学习时长（小时）
        
        Returns:
            学习计划文本
        """
        # 分析各科成绩
        analysis = {}
        for subject, score in scores.items():
            analysis[subject] = self._subject_analyzer.analyze_subject(subject, score)
        
        # 按成绩排序（从低到高）
        sorted_subjects = sorted(analysis.items(), key=lambda x: x[1]['percentage'])
        
        # 分配学习时间（弱科多分配时间）
        plan = f"""📅 每日学习计划（{study_hours}小时）
        
"""
        
        total_time = study_hours * 60
        num_subjects = len(sorted_subjects)
        base_time = total_time / num_subjects
        
        for i, (subject, info) in enumerate(sorted_subjects):
            # 弱科增加20%时间，强科减少10%时间
            if info['level'] in ['及格', '需努力']:
                time_minutes = base_time * 1.2
            elif info['level'] == '优秀':
                time_minutes = base_time * 0.9
            else:
                time_minutes = base_time
            
            plan += f"""📚 {subject}（{info['level']}）
   目标：{info['suggestion']}
   时间：{int(time_minutes)}分钟
   建议：{list(info['improvement_methods'].values())[0]}
   
"""
        
        plan += """⏰ 时间安排建议：
• 上午：数学、物理等理科（头脑清醒时）
• 下午：语文、英语等文科
• 晚上：整理错题，查漏补缺

💡 小贴士：
• 每学习45分钟休息10分钟
• 保持专注，远离手机干扰
• 每天坚持，循序渐进"""
        
        return plan
    
    def generate_weekly_plan(self, scores: Dict[str, int]) -> str:
        """
        生成周学习计划
        
        Args:
            scores: 各科成绩
        
        Returns:
            周学习计划文本
        """
        analysis = {}
        for subject, score in scores.items():
            analysis[subject] = self._subject_analyzer.analyze_subject(subject, score)
        
        plan = """📅 周学习计划
        
🎯 本周目标：
• 完成1-2套模拟试卷
• 整理错题本，分析错误原因
• 针对薄弱环节进行专项练习

📚 每日安排：
| 时间 | 内容 |
|------|------|
| 周一 | 数学专题复习 |
| 周二 | 语文阅读理解专项 |
| 周三 | 英语听力练习 |
| 周四 | 物理/化学实验复习 |
| 周五 | 模拟考试 |
| 周六 | 错题整理 + 薄弱科目加强 |
| 周日 | 休息 + 下周计划 |

📊 各科重点：
"""
        
        for subject, info in analysis.items():
            plan += f"""• {subject}：{info['suggestion']}
"""
        
        plan += """

💡 每周检查：
1. 各科作业完成情况
2. 模拟考试成绩分析
3. 错题本更新情况
4. 下周计划调整"""
        
        return plan
    
    def generate_exam_plan(self, days_remaining: int, scores: Dict[str, int]) -> str:
        """
        生成考前冲刺计划
        
        Args:
            days_remaining: 剩余天数
            scores: 各科成绩
        
        Returns:
            冲刺计划文本
        """
        analysis = {}
        for subject, score in scores.items():
            analysis[subject] = self._subject_analyzer.analyze_subject(subject, score)
        
        # 计算阶段
        if days_remaining > 60:
            phase = '基础巩固阶段'
            focus = '系统梳理知识点，建立知识框架'
        elif days_remaining > 30:
            phase = '专项突破阶段'
            focus = '针对薄弱科目和题型进行专项训练'
        else:
            phase = '模拟冲刺阶段'
            focus = '模拟考试，调整答题节奏'
        
        plan = f"""🎯 考前冲刺计划（剩余{days_remaining}天）

📋 当前阶段：{phase}
🎯 重点：{focus}

📊 各科分析：
"""
        
        for subject, info in analysis.items():
            plan += f"""• {subject}：{info['score']}/{info['total_score']}（{info['percentage']}%）- {info['level']}
"""
        
        plan += f"""

⏱️ 每日时间分配（建议每天学习{min(6, days_remaining//10 + 4)}小时）：
"""
        
        # 按薄弱程度分配时间
        sorted_subjects = sorted(analysis.items(), key=lambda x: x[1]['percentage'])
        for subject, info in sorted_subjects:
            plan += f"""• {subject}：{2 if info['level'] in ['及格', '需努力'] else 1}小时
"""
        
        plan += """

📌 每日必做：
1. 完成一套模拟试卷（或分科练习）
2. 整理当天错题，分析错误原因
3. 复习前一天的错题
4. 背诵10个英语单词 + 1首古诗文

💡 冲刺小贴士：
• 保持规律作息，保证7-8小时睡眠
• 模拟考试时严格计时
• 重点突破基础题（占70%）
• 保持积极心态，相信自己"""
        
        return plan


class LearningFeedback:
    """学习反馈记录"""
    
    def __init__(self, user_id: str, subject: str, feedback_type: str, 
                 score_change: Optional[int] = None, comment: Optional[str] = None):
        self.user_id = user_id
        self.subject = subject
        self.feedback_type = feedback_type  # 'positive', 'negative', 'neutral'
        self.score_change = score_change
        self.comment = comment
        self.timestamp = datetime.now()


class AdaptiveLearningModel:
    """自适应学习模型"""
    
    def __init__(self):
        # 学习效果权重（根据用户反馈动态调整）
        self._method_weights = {
            '语文': {
                '阅读理解': 1.0,
                '作文': 1.0,
                '古诗文': 1.0,
                '文言文': 1.0
            },
            '数学': {
                '函数': 1.0,
                '几何': 1.0,
                '应用题': 1.0,
                '代数运算': 1.0
            },
            '英语': {
                '听力': 1.0,
                '阅读理解': 1.0,
                '语法': 1.0,
                '写作': 1.0
            },
            '物理': {
                '力学': 1.0,
                '电学': 1.0,
                '光学': 1.0,
                '热学': 1.0
            },
            '化学': {
                '化学方程式': 1.0,
                '实验': 1.0,
                '计算': 1.0,
                '元素周期': 1.0
            }
        }
        
        # 用户反馈历史
        self._feedback_history: List[LearningFeedback] = []
        
        # 学习进度跟踪
        self._user_progress: Dict[str, Dict[str, float]] = {}
        
        logger.info("自适应学习模型初始化完成")
    
    def record_feedback(self, feedback: LearningFeedback):
        """记录用户反馈"""
        self._feedback_history.append(feedback)
        
        # 更新学习效果权重
        self._update_weights(feedback)
        
        # 更新用户进度
        if feedback.user_id not in self._user_progress:
            self._user_progress[feedback.user_id] = {}
        self._user_progress[feedback.user_id][feedback.subject] = (
            self._user_progress[feedback.user_id].get(feedback.subject, 0) + 
            (1 if feedback.feedback_type == 'positive' else -1 if feedback.feedback_type == 'negative' else 0)
        )
        
        logger.info(f"用户反馈已记录: {feedback.user_id} - {feedback.subject} - {feedback.feedback_type}")
    
    def _update_weights(self, feedback: LearningFeedback):
        """根据反馈更新学习方法权重"""
        subject_methods = self._method_weights.get(feedback.subject)
        if not subject_methods:
            return
        
        # 根据反馈类型调整权重
        adjustment = 0.1 if feedback.feedback_type == 'positive' else -0.05
        
        # 如果有具体的薄弱点反馈，只调整对应方法的权重
        if feedback.comment:
            for method in subject_methods.keys():
                if method in feedback.comment:
                    subject_methods[method] = max(0.5, min(1.5, subject_methods[method] + adjustment))
        else:
            # 否则整体调整该科目的所有方法权重
            for method in subject_methods.keys():
                subject_methods[method] = max(0.5, min(1.5, subject_methods[method] + adjustment))
    
    def get_effective_methods(self, subject: str) -> List[str]:
        """获取最有效的学习方法（根据权重排序）"""
        subject_methods = self._method_weights.get(subject, {})
        # 按权重降序排列
        sorted_methods = sorted(subject_methods.items(), key=lambda x: x[1], reverse=True)
        return [method for method, weight in sorted_methods if weight >= 0.8]
    
    def get_user_progress(self, user_id: str) -> Optional[Dict[str, float]]:
        """获取用户学习进度"""
        return self._user_progress.get(user_id)
    
    def suggest_focus_areas(self, user_id: str, scores: Dict[str, int]) -> List[str]:
        """根据用户历史数据建议重点关注领域"""
        progress = self.get_user_progress(user_id)
        if not progress:
            # 如果没有历史数据，返回分数最低的科目
            return sorted(scores.keys(), key=lambda x: scores[x])[:2]
        
        # 综合考虑分数和学习进度
        focus_areas = []
        for subject, score in scores.items():
            progress_score = progress.get(subject, 0)
            # 分数低且进度慢的科目优先关注
            priority = (100 - score) * 0.7 + max(0, -progress_score) * 0.3
            focus_areas.append((subject, priority))
        
        # 返回优先级最高的2-3个科目
        return [subject for subject, priority in sorted(focus_areas, key=lambda x: -x[1])[:3]]


class AutoLearningAdvisor:
    """自动化学习建议器 - 增强版"""
    
    def __init__(self):
        self._plan_generator = StudyPlanGenerator()
        self._subject_analyzer = SubjectAnalyzer()
        self._adaptive_model = AdaptiveLearningModel()
        logger.info("自动化学习建议器（增强版）初始化完成")
    
    def record_user_feedback(self, user_id: str, subject: str, feedback_type: str, 
                             score_change: Optional[int] = None, comment: Optional[str] = None):
        """
        记录用户反馈
        
        Args:
            user_id: 用户ID
            subject: 科目名称
            feedback_type: 反馈类型（positive/negative/neutral）
            score_change: 分数变化
            comment: 反馈评论
        """
        feedback = LearningFeedback(user_id, subject, feedback_type, score_change, comment)
        self._adaptive_model.record_feedback(feedback)
    
    def analyze_scores(self, scores: Dict[str, int], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        分析成绩并生成建议（支持自适应）
        
        Args:
            scores: 各科成绩
            user_id: 用户ID（用于获取历史数据）
        
        Returns:
            分析结果和建议
        """
        # 分析各科
        analysis = {}
        total_score = 0
        total_max = 0
        
        for subject, score in scores.items():
            subject_info = self._subject_analyzer.analyze_subject(subject, score)
            # 添加自适应学习方法建议
            effective_methods = self._adaptive_model.get_effective_methods(subject)
            subject_info['effective_methods'] = effective_methods
            analysis[subject] = subject_info
            total_score += score
            total_max += subject_info.get('total_score', 0)
        
        # 计算总分和排名建议
        avg_percentage = (total_score / total_max) * 100 if total_max > 0 else 0
        
        if avg_percentage >= 90:
            overall_level = '优秀'
            overall_suggestion = '整体成绩优秀！保持状态，适当挑战更高难度题目'
        elif avg_percentage >= 80:
            overall_level = '良好'
            overall_suggestion = '整体成绩良好，继续保持，重点提升薄弱科目'
        elif avg_percentage >= 60:
            overall_level = '中等'
            overall_suggestion = '整体成绩中等，需要加强复习，提升薄弱环节'
        else:
            overall_level = '需努力'
            overall_suggestion = '整体成绩偏低，建议从基础开始，系统复习'
        
        # 获取建议关注的领域
        focus_areas = []
        if user_id:
            focus_areas = self._adaptive_model.suggest_focus_areas(user_id, scores)
        
        return {
            'total_score': total_score,
            'total_max': total_max,
            'average_percentage': round(avg_percentage, 1),
            'overall_level': overall_level,
            'overall_suggestion': overall_suggestion,
            'subject_analysis': analysis,
            'focus_areas': focus_areas,
            'user_progress': self._adaptive_model.get_user_progress(user_id) if user_id else None
        }
    
    def generate_adaptive_plan(self, user_id: str, scores: Dict[str, int], 
                               study_hours: float = 4.0) -> str:
        """
        生成自适应学习计划
        
        Args:
            user_id: 用户ID
            scores: 各科成绩
            study_hours: 每日学习时长（小时）
        
        Returns:
            自适应学习计划文本
        """
        analysis = self.analyze_scores(scores, user_id)
        focus_areas = analysis.get('focus_areas', [])
        
        plan = f"""🎯 自适应学习计划（用户ID: {user_id}）

📊 当前分析：
• 总分：{analysis['total_score']}/{analysis['total_max']}
• 平均分：{analysis['average_percentage']}%
• 综合评级：{analysis['overall_level']}

🎯 重点关注科目：
"""
        
        for i, area in enumerate(focus_areas, 1):
            plan += f"{i}. {area}\n"
        
        plan += f"""

📚 各科学习建议（每日{study_hours}小时）：
"""
        
        total_time = study_hours * 60
        num_subjects = len(scores)
        base_time = total_time / num_subjects
        
        for subject, info in analysis['subject_analysis'].items():
            # 根据薄弱程度和学习进度调整时间
            if subject in focus_areas:
                time_minutes = base_time * 1.3
            elif info['level'] == '优秀':
                time_minutes = base_time * 0.8
            else:
                time_minutes = base_time
            
            # 获取最有效的学习方法
            effective_methods = info.get('effective_methods', [])
            method_suggestion = f"推荐方法：{', '.join(effective_methods)}" if effective_methods else ""
            
            plan += f"""
🔹 {subject}（{info['level']}）
   • 分数：{info['score']}/{info['total_score']}
   • 时间：{int(time_minutes)}分钟
   • 建议：{info['suggestion']}
   • {method_suggestion}
"""
        
        plan += """
💡 自适应小贴士：
• 根据你的学习历史，系统已调整了学习方法的优先级
• 建议重点关注标记为"重点关注"的科目
• 完成学习后请提供反馈，系统会持续优化建议

📅 学习节奏：
• 每45分钟休息10分钟
• 每天保持固定的学习时间
• 定期复习已学内容"""
        
        return plan
    
    def generate_report(self, scores: Dict[str, int], days_remaining: int = 60, 
                        user_id: Optional[str] = None) -> str:
        """
        生成完整的学习分析报告（支持自适应）
        
        Args:
            scores: 各科成绩
            days_remaining: 剩余天数
            user_id: 用户ID（用于获取历史数据）
        
        Returns:
            报告文本
        """
        analysis = self.analyze_scores(scores, user_id)
        
        report = f"""📊 学习分析报告

📋 总体情况
• 总分：{analysis['total_score']}/{analysis['total_max']}
• 平均分：{analysis['average_percentage']}%
• 综合评级：{analysis['overall_level']}
• {analysis['overall_suggestion']}
"""
        
        if analysis.get('focus_areas'):
            report += """
🎯 重点关注科目：
"""
            for area in analysis['focus_areas']:
                report += f"• {area}\n"
        
        report += """
📚 各科详情：
"""
        
        for subject, info in analysis['subject_analysis'].items():
            effective_methods = info.get('effective_methods', [])
            method_text = f"\n   • 推荐方法：{', '.join(effective_methods)}" if effective_methods else ""
            
            report += f"""
🔹 {subject}：{info['score']}/{info['total_score']}（{info['percentage']}%）- {info['level']}
   • {info['suggestion']}{method_text}
"""
        
        report += f"""

📅 考前冲刺计划（剩余{days_remaining}天）
"""
        
        report += self._plan_generator.generate_exam_plan(days_remaining, scores)
        
        return report


# 全局实例
learning_advisor = AutoLearningAdvisor()


def get_learning_advisor() -> AutoLearningAdvisor:
    """获取自动化学习建议器实例"""
    return learning_advisor


if __name__ == '__main__':
    # 测试学习建议器
    print("=" * 70)
    print("自动化学习建议器测试")
    print("=" * 70)
    
    advisor = AutoLearningAdvisor()
    
    # 测试成绩
    test_scores = {
        '语文': 95,
        '数学': 80,
        '英语': 88,
        '物理': 70,
        '化学': 60
    }
    
    print("\n📊 测试成绩：")
    for subject, score in test_scores.items():
        print(f"   {subject}: {score}分")
    
    print("\n" + "=" * 70)
    print("学习分析报告")
    print("=" * 70)
    
    report = advisor.generate_report(test_scores, days_remaining=45)
    print(report)
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)