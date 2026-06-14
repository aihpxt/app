"""
校园生活智能体
提供校园环境、宿舍条件、食堂、社团活动等信息查询服务
"""

import logging
from typing import Dict, Any, Optional, List
from agents.base_agent import BaseAgent, AgentInfo
from app.utils.unified_data_access import UnifiedDatabaseManager

logger = logging.getLogger(__name__)


class CampusLifeAgent(BaseAgent):
    """校园生活智能体"""
    
    agent_id = "campus_life_agent"
    agent_name = "校园生活助手"
    description = "提供校园环境、宿舍条件、食堂、社团活动等信息查询服务"
    
    def __init__(self):
        super().__init__()
        self.db_manager = UnifiedDatabaseManager()
        self.supported_intents = [
            'campus_environment',
            'dormitory',
            'canteen',
            'club_activity',
            'facilities',
            'school_life'
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
            
            # 获取学校信息
            school_name = self._extract_school_name(user_input, context)
            
            # 根据查询类型生成响应
            response = self._generate_response(query_type, school_name)
            
            return {
                'success': True,
                'response': response,
                'query_type': query_type,
                'school_name': school_name
            }
            
        except Exception as e:
            logger.error(f"校园生活智能体处理失败: {e}", exc_info=True)
            return {
                'success': False,
                'response': f"抱歉，处理您的请求时发生错误：{str(e)}"
            }
    
    def _classify_query(self, user_input: str) -> str:
        """分类用户查询类型"""
        user_input_lower = user_input.lower()
        
        # 环境查询
        if any(kw in user_input_lower for kw in ['环境', '校园环境', '校园面貌', '学校环境']):
            return 'campus_environment'
        
        # 宿舍查询
        if any(kw in user_input_lower for kw in ['宿舍', '住宿', '寝室', '住宿条件']):
            return 'dormitory'
        
        # 食堂查询
        if any(kw in user_input_lower for kw in ['食堂', '饭堂', '伙食', '吃饭', '餐饮']):
            return 'canteen'
        
        # 社团查询
        if any(kw in user_input_lower for kw in ['社团', '活动', '学生会', '社团活动']):
            return 'club_activity'
        
        # 设施查询
        if any(kw in user_input_lower for kw in ['设施', '设备', '体育馆', '图书馆', '实验室']):
            return 'facilities'
        
        # 默认返回校园生活综合信息
        return 'school_life'
    
    def _extract_school_name(self, user_input: str, context: Optional[Dict]) -> Optional[str]:
        """提取学校名称"""
        # 首先从上下文中获取
        if context:
            # 检查指代词解析结果
            resolved_entity = context.get('resolved_entity')
            if resolved_entity:
                return resolved_entity.get('entity_name')
            
            # 检查上下文中的学校名称
            school_name = context.get('school_name')
            if school_name:
                return school_name
        
        # 从用户输入中提取
        school_keywords = ['中学', '高中', '附中', '一中', '二中', '三中']
        for keyword in school_keywords:
            if keyword in user_input:
                # 简单提取包含关键词的部分
                words = user_input.replace('，', ' ').replace('。', ' ').split()
                for word in words:
                    if keyword in word:
                        return word
        
        return None
    
    def _generate_response(self, query_type: str, school_name: Optional[str]) -> str:
        """根据查询类型生成响应"""
        school_display = school_name if school_name else '该学校'
        
        responses = {
            'campus_environment': self._get_environment_info(school_display),
            'dormitory': self._get_dormitory_info(school_display),
            'canteen': self._get_canteen_info(school_display),
            'club_activity': self._get_club_info(school_display),
            'facilities': self._get_facilities_info(school_display),
            'school_life': self._get_general_info(school_display)
        }
        
        return responses.get(query_type, self._get_general_info(school_display))
    
    def _get_environment_info(self, school_name: str) -> str:
        """获取校园环境信息"""
        return f"""【{school_name} - 校园环境】

🌳 **校园环境优美**
• 绿化覆盖率高，校园整洁美观
• 拥有花园式景观设计
• 配备现代化教学楼和运动场地

🏫 **校园设施**
• 教学楼：配备多媒体教室、实验室
• 图书馆：藏书丰富，环境安静
• 体育馆：室内篮球场、羽毛球场等

🌿 **校园文化**
• 注重学生综合素质培养
• 定期举办文化节、艺术节等活动
• 校园氛围积极向上，学风浓厚

如需了解更多详细信息，建议访问{school_name}官方网站或联系招生办。"""
    
    def _get_dormitory_info(self, school_name: str) -> str:
        """获取宿舍信息"""
        return f"""【{school_name} - 宿舍条件】

🛏️ **宿舍配置**
• 一般为4-6人间
• 上床下桌布局
• 配备独立衣柜和书桌

🚿 **生活设施**
• 每间宿舍配有独立卫生间
• 供应热水（定时供应）
• 配备空调或风扇

🏢 **宿舍管理**
• 有专门的宿管老师负责
• 实行封闭式管理
• 卫生检查定期进行

💰 **住宿费用**
• 公办学校：约300-600元/学期
• 民办学校：约800-1500元/学期

具体住宿安排以学校实际情况为准。"""
    
    def _get_canteen_info(self, school_name: str) -> str:
        """获取食堂信息"""
        return f"""【{school_name} - 食堂情况】

🍽️ **食堂设施**
• 设有多个食堂窗口
• 提供多种菜式选择
• 环境整洁卫生

🍲 **菜品特色**
• 提供滇味、川味等多种口味
• 设有清真窗口（部分学校）
• 提供早餐、午餐、晚餐及夜宵

💰 **消费标准**
• 早餐：5-10元
• 午餐/晚餐：10-15元
• 整体消费适中，支持校园卡支付

🥗 **食品安全**
• 严格执行卫生标准
• 食材新鲜，每日采购
• 定期接受卫生部门检查"""
    
    def _get_club_info(self, school_name: str) -> str:
        """获取社团活动信息"""
        return f"""【{school_name} - 社团活动】

🎭 **社团类型**
• 学术类：数学社、物理社、文学社等
• 艺术类：音乐社、舞蹈社、美术社等
• 体育类：篮球社、足球社、羽毛球社等
• 综合类：志愿者协会、动漫社等

📅 **活动安排**
• 新生招新：开学季集中招新
• 社团活动：每周定期活动
• 校园活动：文化节、运动会、艺术节

🌟 **特色活动**
• 校园歌手大赛
• 辩论赛
• 科技创新比赛
• 社会实践活动

加入社团是丰富校园生活、培养兴趣爱好的好途径！"""
    
    def _get_facilities_info(self, school_name: str) -> str:
        """获取设施信息"""
        return f"""【{school_name} - 校园设施】

📚 **图书馆**
• 藏书量丰富
• 提供自习室和电子阅览室
• 开放时间：早8:00-晚10:00

🏀 **体育设施**
• 室外运动场：足球场、篮球场、田径场
• 室内体育馆：羽毛球馆、乒乓球馆
• 部分学校配备游泳池

🔬 **实验室**
• 物理、化学、生物实验室
• 配备先进实验设备
• 供学生进行实验教学和科研活动

🖥️ **信息技术**
• 计算机教室配备最新设备
• 校园WiFi全覆盖
• 电子白板教学设备"""
    
    def _get_general_info(self, school_name: str) -> str:
        """获取综合信息"""
        return f"""【{school_name} - 校园生活指南】

欢迎了解{school_name}的校园生活！以下是您可能关心的方面：

🏫 **校园环境**
• 优美的校园景观和现代化设施

🛏️ **宿舍生活**
• 舒适的住宿环境和完善的生活设施

🍽️ **食堂餐饮**
• 多样化的菜品选择和合理的消费标准

🎭 **社团活动**
• 丰富多彩的社团组织和校园活动

📚 **学习设施**
• 图书馆、实验室等完善的学习资源

您想了解哪个方面的详细信息呢？可以告诉我具体想了解的内容！"""


# 注册智能体
campus_life_agent = CampusLifeAgent()


def get_campus_life_agent() -> CampusLifeAgent:
    """获取校园生活智能体实例"""
    return campus_life_agent


# 智能体信息（用于注册）
agent_info = AgentInfo(
    agent_id="campus_life_agent",
    agent_name="校园生活助手",
    description="提供校园环境、宿舍条件、食堂、社团活动等信息查询服务",
    supported_intents=[
        'campus_environment',
        'dormitory',
        'canteen',
        'club_activity',
        'facilities',
        'school_life'
    ]
)
