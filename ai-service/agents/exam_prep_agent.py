"""
备考指导智能体
提供中考备考学习计划、复习策略、时间管理等指导服务
"""

import logging
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent, AgentInfo

logger = logging.getLogger(__name__)


class ExamPreparationAgent(BaseAgent):
    """备考指导智能体"""
    
    agent_id = "exam_prep_agent"
    agent_name = "备考指导助手"
    description = "提供中考备考学习计划、复习策略、时间管理等指导服务"
    
    def __init__(self):
        super().__init__()
        self.supported_intents = [
            'study_plan',
            'review_strategy',
            'time_management',
            'exam_preparation',
            'subject_strategy',
            'stress_management'
        ]
    
    def handle(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        处理用户查询
        
        Args:
            user_input: 用户输入
            context: 上下文信息
        
        Returns:
            响应结果
        """
        try:
            # 识别查询类型
            query_type = self._classify_query(user_input)
            
            # 获取相关信息
            subject = self._extract_subject(user_input)
            time_frame = self._extract_time_frame(user_input)
            
            # 根据查询类型生成响应
            response = self._generate_response(query_type, subject, time_frame)
            
            return {
                'success': True,
                'response': response,
                'query_type': query_type,
                'subject': subject,
                'time_frame': time_frame
            }
            
        except Exception as e:
            logger.error(f"备考指导智能体处理失败: {e}", exc_info=True)
            return {
                'success': False,
                'response': f"抱歉，处理您的请求时发生错误：{str(e)}"
            }
    
    def _classify_query(self, user_input: str) -> str:
        """分类用户查询类型"""
        user_input_lower = user_input.lower()
        
        # 学习计划
        if any(kw in user_input_lower for kw in ['学习计划', '计划', '安排', '规划']):
            return 'study_plan'
        
        # 复习策略
        if any(kw in user_input_lower for kw in ['复习', '策略', '方法', '技巧']):
            return 'review_strategy'
        
        # 时间管理
        if any(kw in user_input_lower for kw in ['时间', '管理', '安排', '作息']):
            return 'time_management'
        
        # 科目策略
        subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治']
        if any(subject in user_input_lower for subject in subjects):
            return 'subject_strategy'
        
        # 压力管理
        if any(kw in user_input_lower for kw in ['压力', '焦虑', '紧张', '心态']):
            return 'stress_management'
        
        # 默认返回备考综合指导
        return 'exam_preparation'
    
    def _extract_subject(self, user_input: str) -> Optional[str]:
        """提取科目名称"""
        subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治']
        for subject in subjects:
            if subject in user_input:
                return subject
        return None
    
    def _extract_time_frame(self, user_input: str) -> Optional[str]:
        """提取时间范围"""
        time_frames = {
            '一周': ['一周', '7天', '七天'],
            '一个月': ['一个月', '30天', '三十天'],
            '三个月': ['三个月', '90天'],
            '半年': ['半年', '六个月'],
            '一年': ['一年', '12个月']
        }
        
        for time_frame, keywords in time_frames.items():
            if any(kw in user_input for kw in keywords):
                return time_frame
        
        return None
    
    def _generate_response(self, query_type: str, subject: Optional[str], time_frame: Optional[str]) -> str:
        """根据查询类型生成响应"""
        responses = {
            'study_plan': self._get_study_plan(time_frame),
            'review_strategy': self._get_review_strategy(subject),
            'time_management': self._get_time_management(),
            'subject_strategy': self._get_subject_strategy(subject),
            'stress_management': self._get_stress_management(),
            'exam_preparation': self._get_general_guide()
        }
        
        return responses.get(query_type, self._get_general_guide())
    
    def _get_study_plan(self, time_frame: Optional[str]) -> str:
        """获取学习计划指导"""
        plan_time = time_frame if time_frame else '中考前三个月'
        
        return f"""📚 【{plan_time}学习计划指南】

⏰ **阶段划分**
• **基础巩固阶段**（第1-4周）：系统梳理知识点，建立知识框架
• **专项突破阶段**（第5-8周）：针对薄弱科目和题型进行专项训练
• **模拟冲刺阶段**（第9-12周）：模拟考试，调整答题节奏

📖 **每日学习安排建议**
• 上午：数学、物理等理科（头脑清醒时）
• 下午：语文、英语等文科（阅读量大）
• 晚上：错题整理、查漏补缺

🎯 **每周目标设定**
• 完成1-2套模拟试卷
• 整理错题本，分析错误原因
• 针对薄弱环节进行专项练习

💡 **小贴士**
• 制定计划时要留有余地，避免过度疲劳
• 定期回顾和调整计划
• 保持规律作息，保证充足睡眠"""
    
    def _get_review_strategy(self, subject: Optional[str]) -> str:
        """获取复习策略"""
        if subject:
            return self._get_subject_review(subject)
        
        return """🔍 【中考复习策略】

📋 **通用复习方法**
• **思维导图法**：用思维导图梳理知识框架
• **错题分析法**：建立错题本，定期回顾
• **真题演练法**：通过真题熟悉考试题型

📈 **复习进度安排**
1. 第一遍：全面复习，标记重点
2. 第二遍：重点突破，强化记忆
3. 第三遍：模拟演练，查漏补缺

🎯 **重点突破策略**
• 先掌握基础题（70%）
• 再攻克中等题（20%）
• 最后挑战难题（10%）

⏳ **时间分配原则**
• 薄弱科目多花时间
• 优势科目保持状态
• 每天保证每科都有复习时间"""
    
    def _get_subject_review(self, subject: str) -> str:
        """获取特定科目复习策略"""
        strategies = {
            '语文': """📖 【语文复习策略】

📝 **基础知识**
• 古诗文背诵默写（必拿分）
• 文言文字词解释
• 病句辨析与修改

📚 **阅读理解**
• 记叙文：把握主旨、分析人物形象
• 说明文：提取信息、理解说明方法
• 议论文：理清论点、论据、论证

✍️ **作文写作**
• 积累素材，准备模板
• 练习开头结尾技巧
• 注意书写工整""",
            
            '数学': """🔢 【数学复习策略】

📐 **代数部分**
• 方程与不等式求解
• 函数图像与性质
• 数列求和公式

📊 **几何部分**
• 三角形全等与相似
• 圆的性质与计算
• 立体几何基础

🎯 **解题技巧**
• 掌握常见辅助线添加方法
• 熟悉各类题型的解题思路
• 注意步骤规范，避免粗心丢分""",
            
            '英语': """🔤 【英语复习策略】

📚 **词汇积累**
• 高频单词背诵
• 短语搭配记忆
• 同义词辨析

📖 **语法掌握**
• 时态语态
• 从句结构
• 非谓语动词

🎧 **听说训练**
• 每天听听力材料
• 跟读模仿发音
• 背诵范文提高语感""",
            
            '物理': """⚡ 【物理复习策略】

🔧 **力学部分**
• 牛顿运动定律
• 功和能的关系
• 压强与浮力

⚙️ **电学部分**
• 电路分析
• 欧姆定律
• 电功率计算

🔬 **实验部分**
• 掌握基本实验原理
• 学会数据处理
• 注意实验安全规范""",
            
            '化学': """🧪 【化学复习策略】

⚗️ **基础知识**
• 元素符号与化合价
• 化学式与化学方程式
• 物质分类与性质

🔬 **实验操作**
• 常见实验仪器使用
• 气体制备与收集
• 物质检验方法

📊 **计算技巧**
• 根据化学方程式计算
• 溶液浓度计算
• 守恒法解题技巧""",
            
            '历史': """📜 【历史复习策略】

⏰ **时间线梳理**
• 中国古代史时间轴
• 中国近代史重大事件
• 世界史重要时期

📚 **专题复习**
• 政治制度演变
• 经济发展历程
• 文化思想变迁

🗺️ **中外对比**
• 同一时期中外历史事件对比
• 分析历史事件的因果关系"""
        }
        
        return strategies.get(subject, f"""📚 【{subject}复习策略】

• 梳理该科目知识框架
• 重点突破薄弱章节
• 多做练习题巩固知识点
• 定期进行模拟测试""")
    
    def _get_time_management(self) -> str:
        """获取时间管理建议"""
        return """⏰ 【时间管理指南】

📅 **制定时间表**
• 合理分配各科学习时间
• 设定固定的学习时段
• 留出休息和娱乐时间

⏳ **高效利用时间**
• 利用碎片时间背单词、古诗文
• 大块时间用于难题攻克
• 避免拖延，立即行动

💤 **作息建议**
• 保证每天7-8小时睡眠
• 中午适当午休（20-30分钟）
• 保持规律的作息习惯

🎯 **番茄工作法**
• 专注学习25分钟
• 休息5分钟
• 每4个番茄钟后休息20分钟"""
    
    def _get_subject_strategy(self, subject: Optional[str]) -> str:
        """获取科目策略"""
        if subject:
            return self._get_subject_review(subject)
        
        return """🎯 【科目学习策略】

📚 **语文**
• 每天背诵古诗文
• 阅读一篇课外文章
• 积累作文素材

🔢 **数学**
• 每天练习10-15道题
• 整理错题，分析原因
• 总结解题方法

🔤 **英语**
• 每天背诵20个单词
• 听一篇听力材料
• 朗读课文培养语感

⚡ **物理/化学**
• 理解公式推导过程
• 多做实验题
• 注意单位和公式应用

📜 **文科科目**
• 建立知识框架
• 制作记忆卡片
• 定期回顾复习"""
    
    def _get_stress_management(self) -> str:
        """获取压力管理建议"""
        return """🧘 【考前心态调整】

💆 **缓解压力方法**
• 适当运动（跑步、打球、散步）
• 听音乐放松心情
• 和家人朋友沟通交流

🎯 **正确看待考试**
• 考试是检验学习成果的方式
• 保持平常心，尽力而为
• 相信自己的努力会有收获

😴 **保证充足睡眠**
• 避免熬夜复习
• 保持规律作息
• 睡眠不足影响记忆力

💡 **积极心理暗示**
• 告诉自己"我可以的"
• 关注进步，而非完美
• 把考试当作一次练习"""
    
    def _get_general_guide(self) -> str:
        """获取综合备考指导"""
        return """🎓 【中考备考综合指导】

欢迎来到中考备考指导！以下是您可能需要的帮助：

📚 **学习计划**
• 制定科学的复习计划
• 合理分配学习时间

🎯 **复习策略**
• 各科目复习方法
• 错题整理技巧

⏰ **时间管理**
• 高效利用时间
• 保持规律作息

🧘 **心态调整**
• 缓解考前压力
• 保持积极心态

您想了解哪个方面的详细信息呢？可以告诉我具体需求！"""


# 注册智能体
exam_prep_agent = ExamPreparationAgent()


def get_exam_prep_agent() -> ExamPreparationAgent:
    """获取备考指导智能体实例"""
    return exam_prep_agent


# 智能体信息（用于注册）
agent_info = AgentInfo(
    agent_id="exam_prep_agent",
    agent_name="备考指导助手",
    description="提供中考备考学习计划、复习策略、时间管理等指导服务",
    supported_intents=[
        'study_plan',
        'review_strategy',
        'time_management',
        'exam_preparation',
        'subject_strategy',
        'stress_management'
    ]
)
