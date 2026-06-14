#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能学习助手
帮助学生制定个性化学习计划，提供学习建议和资源推荐
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class IntelligentStudyHelper:
    """智能学习助手"""
    
    def __init__(self):
        self._subjects = ['语文', '数学', '英语', '物理', '化学']
        self._study_methods = {
            '语文': ['阅读理解技巧', '作文写作方法', '古诗文背诵', '词汇积累'],
            '数学': ['公式记忆', '解题技巧', '错题整理', '专题训练'],
            '英语': ['词汇背诵', '语法学习', '听力训练', '写作练习'],
            '物理': ['公式推导', '实验理解', '计算题练习', '概念理解'],
            '化学': ['方程式记忆', '实验操作', '计算题练习', '元素周期表']
        }
        logger.info("智能学习助手初始化完成")
    
    def generate_daily_plan(self, user_profile: Dict) -> str:
        """
        生成每日学习计划
        
        Args:
            user_profile: 用户画像（包含分数、年级、薄弱科目等）
        
        Returns:
            每日学习计划
        """
        score = user_profile.get('score', 0)
        grade = user_profile.get('grade', '九年级')
        weak_subjects = user_profile.get('weak_subjects', [])
        strong_subjects = user_profile.get('strong_subjects', [])
        
        # 根据分数确定学习强度
        if score >= 580:
            intensity = '高效冲刺'
            total_time = 3.5
        elif score >= 520:
            intensity = '稳步提升'
            total_time = 4.0
        else:
            intensity = '基础巩固'
            total_time = 4.5
        
        # 分配学习时间
        time_allocation = self._allocate_time(weak_subjects, strong_subjects, total_time)
        
        # 生成计划
        plan = f"""📅 **{datetime.now().strftime('%Y年%m月%d日')} 学习计划**
        
🎯 今日目标：{intensity}
⏰ 总学习时长：{total_time}小时

"""
        
        for subject, time in time_allocation.items():
            if time > 0:
                methods = self._get_study_methods(subject, weak_subjects)
                plan += f"""📚 **{subject}** ({time}小时)
{methods}

"""
        
        plan += """💡 学习建议：
• 每45分钟休息10分钟
• 保持专注，远离手机
• 及时整理错题
• 睡前复习当天内容

加油！你一定可以的！💪"""
        
        return plan
    
    def _allocate_time(self, weak_subjects: List[str], strong_subjects: List[str], total_time: float) -> Dict[str, float]:
        """分配学习时间"""
        allocation = {}
        
        # 基础分配
        base_time = total_time / len(self._subjects)
        
        for subject in self._subjects:
            if subject in weak_subjects:
                # 薄弱科目多分配20%
                allocation[subject] = round(base_time * 1.2, 1)
            elif subject in strong_subjects:
                # 强项科目少分配10%
                allocation[subject] = round(base_time * 0.9, 1)
            else:
                allocation[subject] = round(base_time, 1)
        
        return allocation
    
    def _get_study_methods(self, subject: str, weak_subjects: List[str]) -> str:
        """获取学习方法建议"""
        methods = self._study_methods.get(subject, [])
        
        if subject in weak_subjects:
            # 薄弱科目更详细的建议
            detailed_methods = {
                '语文': """• 阅读一篇课外文章并做笔记
• 背诵5首古诗或文言片段
• 练习2篇阅读理解
• 积累10个成语或好词好句""",
                '数学': """• 复习当天课堂内容
• 完成10道基础题
• 攻克2道中档题
• 整理错题并分析原因""",
                '英语': """• 背诵20个单词
• 做1篇完形填空
• 练习听力30分钟
• 写一段100字左右的短文""",
                '物理': """• 复习公式并默写
• 做5道计算题
• 分析1道错题
• 理解一个物理概念""",
                '化学': """• 背诵5个化学方程式
• 做5道计算题
• 复习元素周期表
• 整理实验知识点"""
            }
            return detailed_methods.get(subject, "\n".join([f"• {m}" for m in methods]))
        else:
            return "\n".join([f"• {m}" for m in methods])
    
    def generate_weekly_plan(self, user_profile: Dict) -> str:
        """
        生成周学习计划
        
        Args:
            user_profile: 用户画像
        
        Returns:
            周学习计划
        """
        score = user_profile.get('score', 0)
        grade = user_profile.get('grade', '九年级')
        weak_subjects = user_profile.get('weak_subjects', [])
        
        plan = f"""📅 **{datetime.now().strftime('%Y年')}第{datetime.now().isocalendar()[1]}周学习计划**
        
🎯 本周目标：
{'• 重点突破薄弱科目' if weak_subjects else '• 全面提升'}
{'• 保持优势科目' if score >= 550 else '• 巩固基础知识'}

📚 每日学习安排：
"""
        
        days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        focus_subjects = weak_subjects if weak_subjects else self._subjects[:3]
        
        for i, day in enumerate(days):
            if i < 5:  # 工作日
                plan += f"""**{day}**（上学日）
• 放学后学习：2-3小时
• 重点科目：{focus_subjects[i % len(focus_subjects)]}
• 任务：完成作业 + 专项练习

"""
            else:  # 周末
                plan += f"""**{day}**（休息日）
• 全天学习：4-5小时
• 上午：模拟考试 / 专题复习
• 下午：错题整理 + 薄弱科目强化
• 晚上：自由复习 + 放松

"""
        
        plan += """📊 周末复盘：
1. 检查本周学习任务完成情况
2. 整理错题本
3. 调整下周学习计划
4. 适当休息，保持状态

加油！坚持就是胜利！💪"""
        
        return plan
    
    def get_exam_strategy(self, days_left: int, user_profile: Dict) -> str:
        """
        获取考前冲刺策略
        
        Args:
            days_left: 剩余天数
            user_profile: 用户画像
        
        Returns:
            冲刺策略
        """
        score = user_profile.get('score', 0)
        weak_subjects = user_profile.get('weak_subjects', [])
        
        if days_left <= 7:
            strategy = self._get_final_week_strategy(score, weak_subjects)
        elif days_left <= 30:
            strategy = self._get_one_month_strategy(score, weak_subjects)
        else:
            strategy = self._get_long_term_strategy(score, weak_subjects)
        
        return strategy
    
    def _get_final_week_strategy(self, score: int, weak_subjects: List[str]) -> str:
        """最后一周冲刺策略"""
        return f"""🔥 **考前最后一周冲刺策略**

⏰ 剩余时间：7天

🎯 核心策略：回归基础，保持状态

📚 每日安排：
• 上午：模拟考试（按中考时间）
• 下午：错题回顾 + 薄弱科目快速复习
• 晚上：公式/单词背诵 + 放松

⚠️ 重点注意：
• 不要再做难题偏题
• 保持规律作息（和中考时间同步）
• 调整心态，相信自己
• 准备考试用品

{'💪 薄弱科目快速突破：' + '、'.join(weak_subjects) if weak_subjects else ''}

相信自己，你已经准备好了！🎊"""
    
    def _get_one_month_strategy(self, score: int, weak_subjects: List[str]) -> str:
        """一个月冲刺策略"""
        return f"""📚 **考前一个月冲刺策略**

⏰ 剩余时间：约30天

🎯 核心策略：专题突破，模拟训练

📅 四周计划：
第1周：薄弱科目专题突破
第2周：综合模拟训练
第3周：错题复盘 + 强化训练
第4周：调整状态 + 回归基础

📊 每日任务：
• 2小时专题训练
• 1小时错题整理
• 30分钟背诵（单词/公式/古诗文）

{'🎯 重点突破：' + '、'.join(weak_subjects) if weak_subjects else '🎯 全面提升'}

坚持下去，胜利就在眼前！💪"""
    
    def _get_long_term_strategy(self, score: int, weak_subjects: List[str]) -> str:
        """长期复习策略"""
        return f"""📅 **长期复习策略**

⏰ 剩余时间：充足

🎯 核心策略：循序渐进，稳扎稳打

📚 复习阶段：
1. 基础巩固（4周）
   • 梳理课本知识点
   • 完成课后习题
   • 建立知识框架

2. 专题强化（4周）
   • 分专题突破
   • 大量练习
   • 总结解题方法

3. 模拟训练（4周）
   • 定期模拟考试
   • 错题复盘
   • 调整答题节奏

4. 冲刺阶段（2周）
   • 回归基础
   • 保持状态
   • 调整心态

{'🎯 需要重点关注：' + '、'.join(weak_subjects) if weak_subjects else ''}

循序渐进，一步一个脚印！💪"""
    
    def get_subject_tips(self, subject: str) -> str:
        """
        获取科目学习技巧
        
        Args:
            subject: 科目名称
        
        Returns:
            学习技巧
        """
        tips = {
            '语文': """📖 **语文学习技巧**

🎯 阅读理解：
• 先通读全文，了解大意
• 带着问题找答案
• 注意关键词和中心句
• 分析作者意图和写作手法

✍️ 作文写作：
• 审题要准，立意要深
• 结构清晰，层次分明
• 语言生动，用词准确
• 开头结尾要精彩

📝 古诗文：
• 理解意思再背诵
• 注意文言实词虚词
• 积累名句名篇
• 了解作者背景

📚 每日积累：
• 阅读一篇好文章
• 背诵一首古诗
• 积累5个好词好句""",
            '数学': """🔢 **数学学习技巧**

📐 基础知识：
• 吃透课本例题
• 熟记公式定理
• 理解概念本质

💡 解题方法：
• 审题要仔细，理解题意
• 画图辅助思考
• 从简单到复杂逐步推进
• 检查答案是否合理

📝 错题整理：
• 分类整理错题
• 分析错误原因
• 定期回顾复习
• 总结解题规律

🎯 专题突破：
• 函数与方程
• 几何证明
• 应用题
• 概率统计""",
            '英语': """🔤 **英语学习技巧**

📚 词汇积累：
• 每天背诵20-30个单词
• 结合例句记忆
• 定期复习巩固

📖 语法学习：
• 理解基本概念
• 多做练习题
• 注意时态语态

🎧 听力训练：
• 每天听30分钟
• 精听和泛听结合
• 跟读模仿

✍️ 写作练习：
• 掌握基本句型
• 多用连接词
• 注意语法正确""",
            '物理': """⚛️ **物理学习技巧**

📐 概念理解：
• 理解物理过程
• 掌握基本公式
• 注意单位和符号

🔧 解题步骤：
• 分析物理情景
• 画出示意图
• 选择合适公式
• 代入数据计算

🔬 实验理解：
• 理解实验原理
• 掌握实验步骤
• 注意实验误差

🎯 重点专题：
• 力学综合
• 电学计算
• 光学现象
• 热学知识""",
            '化学': """🧪 **化学学习技巧**

⚗️ 方程式记忆：
• 理解反应原理
• 掌握配平方法
• 注意反应条件

🧪 实验操作：
• 了解实验目的
• 掌握操作步骤
• 注意安全事项

📊 计算题：
• 掌握物质的量计算
• 注意溶液浓度计算
• 理解化学平衡

🔬 元素周期：
• 掌握周期律
• 理解原子结构
• 记忆常见元素性质"""
        }
        
        return tips.get(subject, f"**{subject}**学习技巧正在整理中...")


# 全局实例
study_helper = IntelligentStudyHelper()


def get_study_helper() -> IntelligentStudyHelper:
    """获取智能学习助手实例"""
    return study_helper


if __name__ == '__main__':
    # 测试智能学习助手
    print("=" * 70)
    print("智能学习助手测试")
    print("=" * 70)
    
    helper = IntelligentStudyHelper()
    
    # 测试用户画像
    user_profile = {
        'score': 550,
        'grade': '九年级',
        'weak_subjects': ['数学', '物理'],
        'strong_subjects': ['语文', '英语']
    }
    
    print("\n📅 测试每日学习计划：")
    daily_plan = helper.generate_daily_plan(user_profile)
    print(daily_plan)
    
    print("\n" + "=" * 70)
    print("📅 测试周学习计划：")
    weekly_plan = helper.generate_weekly_plan(user_profile)
    print(weekly_plan[:500] + "..." if len(weekly_plan) > 500 else weekly_plan)
    
    print("\n" + "=" * 70)
    print("🔥 测试考前冲刺策略（30天）：")
    strategy = helper.get_exam_strategy(30, user_profile)
    print(strategy)
    
    print("\n" + "=" * 70)
    print("📚 测试数学学习技巧：")
    tips = helper.get_subject_tips('数学')
    print(tips)
    
    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)