"""
心理辅导智能体
提供考前心理调节、压力管理、情绪疏导等服务
"""

import logging
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent, AgentInfo

logger = logging.getLogger(__name__)


class MentalHealthAgent(BaseAgent):
    """心理辅导智能体"""
    
    agent_id = "mental_health_agent"
    agent_name = "心理辅导助手"
    description = "提供考前心理调节、压力管理、情绪疏导等服务"
    
    def __init__(self):
        super().__init__()
        self.supported_intents = [
            'stress_management',
            'anxiety_relief',
            'emotion_regulation',
            'confidence_building',
            'sleep_improvement',
            'mental_health'
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
            
            # 根据查询类型生成响应
            response = self._generate_response(query_type)
            
            return {
                'success': True,
                'response': response,
                'query_type': query_type
            }
            
        except Exception as e:
            logger.error(f"心理辅导智能体处理失败: {e}", exc_info=True)
            return {
                'success': False,
                'response': f"抱歉，处理您的请求时发生错误：{str(e)}"
            }
    
    def _classify_query(self, user_input: str) -> str:
        """分类用户查询类型"""
        user_input_lower = user_input.lower()
        
        # 压力管理
        if any(kw in user_input_lower for kw in ['压力', '紧张', '焦虑', '压力大', '烦躁']):
            return 'stress_management'
        
        # 焦虑缓解
        if any(kw in user_input_lower for kw in ['焦虑', '担心', '害怕', '恐惧', '不安']):
            return 'anxiety_relief'
        
        # 情绪调节
        if any(kw in user_input_lower for kw in ['情绪', '心情', '低落', '烦躁', '郁闷']):
            return 'emotion_regulation'
        
        # 自信心建立
        if any(kw in user_input_lower for kw in ['自信', '信心', '底气', '自我肯定']):
            return 'confidence_building'
        
        # 睡眠改善
        if any(kw in user_input_lower for kw in ['睡眠', '失眠', '睡不着', '睡不好']):
            return 'sleep_improvement'
        
        # 默认返回心理辅导综合信息
        return 'mental_health'
    
    def _generate_response(self, query_type: str) -> str:
        """根据查询类型生成响应"""
        responses = {
            'stress_management': self._get_stress_management(),
            'anxiety_relief': self._get_anxiety_relief(),
            'emotion_regulation': self._get_emotion_regulation(),
            'confidence_building': self._get_confidence_building(),
            'sleep_improvement': self._get_sleep_improvement(),
            'mental_health': self._get_general_guide()
        }
        
        return responses.get(query_type, self._get_general_guide())
    
    def _get_stress_management(self) -> str:
        """获取压力管理建议"""
        return """🧘 【考前压力管理指南】

💆 **压力来源分析**
• 来自父母的期望
• 对未来的不确定感
• 同学之间的竞争
• 对自己的高要求

🎯 **减压方法**

1️⃣ **深呼吸练习**
• 吸气4秒 → 屏住4秒 → 呼气6秒
• 每天练习3-5次，每次5分钟

2️⃣ **身体放松法**
• 渐进式肌肉放松：从脚趾到头部逐组肌肉放松
• 想象放松：想象自己在宁静的环境中

3️⃣ **时间管理**
• 制定合理的学习计划
• 适当休息，避免过度疲劳
• 留出娱乐和运动时间

4️⃣ **认知调整**
• 接受压力是正常的
• 关注过程而非结果
• 设定合理的目标

⚡ **紧急减压技巧**
• 快速呼吸法：4-7-8呼吸法
• 身体活动：伸展、散步、简单运动
• 转移注意力：听音乐、看风景、与人交谈"""
    
    def _get_anxiety_relief(self) -> str:
        """获取焦虑缓解建议"""
        return """😊 【焦虑情绪缓解】

🔍 **焦虑的表现**
• 心慌、心跳加速
• 紧张不安、坐立不定
• 注意力不集中
• 失眠、多梦

🧘 **缓解方法**

1️⃣ **正念练习**
• 专注于当下
• 观察自己的情绪但不评判
• 通过呼吸练习回到当下

2️⃣ **积极自我对话**
• 用积极的想法替代消极想法
• 例如："我已经准备得很好了"
• 避免"我肯定考不好"这样的想法

3️⃣ **分解任务**
• 将大目标分解成小任务
• 逐个完成，增加掌控感
• 每完成一个任务就给自己鼓励

4️⃣ **寻求支持**
• 和家人朋友倾诉
• 寻求老师的帮助
• 必要时寻求专业心理咨询

💡 **焦虑时可以做的事**
• 写下来：把担心的事情写下来
• 做运动：跑步、打球、瑜伽
• 听音乐：舒缓的音乐有助于放松"""
    
    def _get_emotion_regulation(self) -> str:
        """获取情绪调节建议"""
        return """🌈 【情绪调节指南】

🎭 **常见情绪困扰**
• 烦躁、易怒
• 低落、沮丧
• 焦虑、紧张
• 自责、愧疚

⚖️ **调节方法**

1️⃣ **情绪识别**
• 认识自己的情绪状态
• 给情绪命名（如：我现在感到焦虑）
• 理解情绪产生的原因

2️⃣ **情绪表达**
• 找信任的人倾诉
• 通过写日记表达
• 艺术表达：绘画、音乐、写作

3️⃣ **积极转移**
• 做喜欢的事情转移注意力
• 看一部喜欢的电影
• 进行户外活动

4️⃣ **自我关怀**
• 善待自己，接纳自己的情绪
• 做一些让自己感到愉悦的事
• 给自己奖励和肯定

💝 **重要提醒**
• 所有情绪都是正常的
• 允许自己有负面情绪
• 寻求帮助不是软弱的表现"""
    
    def _get_confidence_building(self) -> str:
        """获取自信心建立建议"""
        return """🌟 【建立自信心】

💪 **自信心的重要性**
• 自信心影响考试表现
• 自信的人更容易发挥正常水平
• 积极的自我预期有助于成功

🏗️ **建立自信的方法**

1️⃣ **回顾成就**
• 列出自己过去的成功经历
• 回顾克服困难的经历
• 肯定自己的努力和进步

2️⃣ **设定合理目标**
• 设定可实现的小目标
• 逐步实现，积累信心
• 庆祝每一个小成就

3️⃣ **积极自我暗示**
• 每天对自己说积极的话
• 例如："我可以的！"、"我已经准备好了！"
• 用正面语言替代负面想法

4️⃣ **充分准备**
• 充分的准备是自信的基础
• 制定学习计划并执行
• 相信付出会有回报

5️⃣ **保持良好状态**
• 保证充足睡眠
• 保持健康饮食
• 适当运动

✨ **每日自信练习**
• 照镜子对自己微笑
• 大声说出自己的优点
• 记录每天的进步"""
    
    def _get_sleep_improvement(self) -> str:
        """获取睡眠改善建议"""
        return """😴 【改善睡眠质量】

🌙 **睡眠的重要性**
• 睡眠影响记忆力和注意力
• 充足睡眠有助于恢复精力
• 考前良好睡眠尤为重要

🛏️ **改善方法**

1️⃣ **建立规律作息**
• 每天同一时间睡觉和起床
• 即使周末也要保持规律
• 避免长时间午睡

2️⃣ **创造良好睡眠环境**
• 保持卧室安静、黑暗、凉爽
• 温度适宜（约18-22℃）
• 使用遮光窗帘和耳塞

3️⃣ **睡前放松程序**
• 睡前1小时远离电子设备
• 阅读一本纸质书
• 听舒缓的音乐
• 进行放松练习

4️⃣ **避免刺激性活动**
• 睡前3小时避免剧烈运动
• 避免摄入咖啡因和尼古丁
• 晚餐不宜过饱

5️⃣ **如果无法入睡**
• 不要强迫自己入睡
• 做一些安静的事情
• 避免看时间增加焦虑

⏰ **推荐作息**
• 初中生：每晚9-10小时
• 高中生：每晚8-9小时
• 考前保持规律作息"""
    
    def _get_general_guide(self) -> str:
        """获取综合心理辅导指导"""
        return """💝 【心理辅导服务】

欢迎来到心理辅导中心！中考前的心理状态非常重要，我可以为您提供以下帮助：

🧘 **压力管理**
• 如何应对考前压力
• 放松技巧和方法

😊 **情绪调节**
• 缓解焦虑和紧张
• 调节情绪状态

🌟 **自信心建立**
• 提升自我信心
• 积极心理暗示

😴 **睡眠改善**
• 改善睡眠质量
• 建立良好作息

您想了解哪个方面的详细信息呢？随时可以告诉我您的感受，我会尽力帮助您！

💡 温馨提示：如果您感到情绪持续低落或焦虑严重，建议及时寻求专业心理咨询师的帮助。"""


# 注册智能体
mental_health_agent = MentalHealthAgent()


def get_mental_health_agent() -> MentalHealthAgent:
    """获取心理辅导智能体实例"""
    return mental_health_agent


# 智能体信息（用于注册）
agent_info = AgentInfo(
    agent_id="mental_health_agent",
    agent_name="心理辅导助手",
    description="提供考前心理调节、压力管理、情绪疏导等服务",
    supported_intents=[
        'stress_management',
        'anxiety_relief',
        'emotion_regulation',
        'confidence_building',
        'sleep_improvement',
        'mental_health'
    ]
)
