"""
智能体注册模块
负责注册所有智能体到注册中心
"""

import logging
from agents.registry import agent_registry, register_agent
from agents.base_agent import ContextAwareAgent
from agents.campus_life_agent import CampusLifeAgent
from agents.exam_prep_agent import ExamPreparationAgent
from agents.mental_health_agent import MentalHealthAgent

logger = logging.getLogger(__name__)


# ==================== 延迟初始化单例 ====================

# 延迟初始化的单例引用
_control_center_ref = None


def _get_control_center():
    """懒加载获取ControlCenterSpecialistAgent单例"""
    global _control_center_ref
    if _control_center_ref is None:
        from agents.specialists import ControlCenterSpecialistAgent
        _control_center_ref = ControlCenterSpecialistAgent()
    return _control_center_ref


# ==================== 智能体注册 ====================

# 学校查询智能体
class SchoolInquiryAgent(ContextAwareAgent):
    """学校查询智能体"""
    
    agent_id = "school_inquiry_agent"
    agent_name = "学校查询专家"
    description = "负责学校信息查询、学校对比、学校推荐等服务"
    
    def __init__(self):
        super().__init__()
        self.supported_intents = ["school_inquiry", "school_compare", "school_recommend"]
    
    def can_handle(self, user_input: str) -> float:
        """判断是否能处理该请求"""
        keywords = ["学校", "中学", "高中", "附中", "一中", "二中", "三中", "对比", "推荐"]
        user_lower = user_input.lower()
        matches = sum(1 for kw in keywords if kw in user_lower)
        return min(matches * 0.2, 1.0)
    
    def get_supported_intents(self) -> list:
        return self.supported_intents
    
    def handle(self, user_input: str, context: dict) -> str:
        """处理用户输入"""
        return _get_control_center()._get_school_info(user_input)


# 分数推荐智能体
class ScoreRecommendationAgent(ContextAwareAgent):
    """分数推荐智能体"""
    
    agent_id = "score_recommendation_agent"
    agent_name = "分数推荐专家"
    description = "根据分数推荐合适的学校"
    
    def __init__(self):
        super().__init__()
        self.supported_intents = ["score_recommendation", "school_by_score"]
    
    def can_handle(self, user_input: str) -> float:
        """判断是否能处理该请求"""
        keywords = ["分", "分数", "录取线", "能上", "推荐"]
        user_lower = user_input.lower()
        matches = sum(1 for kw in keywords if kw in user_lower)
        return min(matches * 0.25, 1.0)
    
    def get_supported_intents(self) -> list:
        return self.supported_intents
    
    def handle(self, user_input: str, context: dict) -> str:
        """处理用户输入"""
        return _get_control_center()._get_school_recommendation_by_score(user_input)


# 中考政策智能体
class PolicyInquiryAgent(ContextAwareAgent):
    """中考政策智能体"""
    
    agent_id = "policy_inquiry_agent"
    agent_name = "政策咨询专家"
    description = "负责中考政策解读、志愿填报指导等服务"
    
    def __init__(self):
        super().__init__()
        self.supported_intents = ["policy_inquiry", "volunteer_guidance", "exam_policy"]
    
    def can_handle(self, user_input: str) -> float:
        """判断是否能处理该请求"""
        keywords = ["政策", "中考", "志愿", "填报", "录取规则"]
        user_lower = user_input.lower()
        matches = sum(1 for kw in keywords if kw in user_lower)
        return min(matches * 0.25, 1.0)
    
    def get_supported_intents(self) -> list:
        return self.supported_intents
    
    def handle(self, user_input: str, context: dict) -> str:
        """处理用户输入"""
        return _get_control_center()._get_policy_info(user_input)


# 费用咨询智能体
class FeeInquiryAgent(ContextAwareAgent):
    """费用咨询智能体"""
    
    agent_id = "fee_inquiry_agent"
    agent_name = "费用咨询专家"
    description = "负责学费查询、费用咨询等服务"
    
    def __init__(self):
        super().__init__()
        self.supported_intents = ["fee_inquiry", "tuition", "cost"]
    
    def can_handle(self, user_input: str) -> float:
        """判断是否能处理该请求"""
        keywords = ["学费", "费用", "收费", "多少钱", "价格"]
        user_lower = user_input.lower()
        matches = sum(1 for kw in keywords if kw in user_lower)
        return min(matches * 0.3, 1.0)
    
    def get_supported_intents(self) -> list:
        return self.supported_intents
    
    def handle(self, user_input: str, context: dict) -> str:
        """处理用户输入"""
        return _get_control_center()._get_weiyang_enrollment_info()


# 未央中学智能体
class WeiyangSchoolAgent(ContextAwareAgent):
    """未央中学智能体"""
    
    agent_id = "weiyang_school_agent"
    agent_name = "未央中学专家"
    description = "负责未央中学相关咨询服务"
    
    def __init__(self):
        super().__init__()
        self.supported_intents = ["weiyang", "qiubei_school"]
    
    def can_handle(self, user_input: str) -> float:
        """判断是否能处理该请求"""
        keywords = ["未央", "丘北"]
        user_lower = user_input.lower()
        matches = sum(1 for kw in keywords if kw in user_lower)
        return min(matches * 0.5, 1.0)
    
    def get_supported_intents(self) -> list:
        return self.supported_intents
    
    def handle(self, user_input: str, context: dict) -> str:
        """处理用户输入"""
        return _get_control_center()._get_weiyang_info()


# 学习计划智能体
class StudyPlanAgent(ContextAwareAgent):
    """学习计划智能体"""
    
    agent_id = "study_plan_agent"
    agent_name = "学习规划专家"
    description = "负责学习计划制定、备考指导等服务"
    
    def __init__(self):
        super().__init__()
        self.supported_intents = ["study_plan", "exam_prep", "learning"]
    
    def can_handle(self, user_input: str) -> float:
        """判断是否能处理该请求"""
        keywords = ["学习", "备考", "复习", "计划", "提分"]
        user_lower = user_input.lower()
        matches = sum(1 for kw in keywords if kw in user_lower)
        return min(matches * 0.25, 1.0)
    
    def get_supported_intents(self) -> list:
        return self.supported_intents
    
    def handle(self, user_input: str, context: dict) -> str:
        """处理用户输入"""
        return (
            "📚 学习计划与备考指导\n\n"
            "【备考建议】\n"
            "• 制定合理的学习计划，分阶段复习\n"
            "• 重点突破薄弱科目\n"
            "• 定期模拟考试，熟悉考试流程\n\n"
            "【学习资源】\n"
            "• 历年真题练习\n"
            "• 知识点梳理\n"
            "• 错题本整理\n\n"
            "【时间安排】\n"
            "• 每天保证8小时学习时间\n"
            "• 合理安排休息，保持良好状态\n\n"
            "需要我帮您制定具体的学习计划吗？"
        )


# 总控智能体（默认）
class ControlCenterAgent(ContextAwareAgent):
    """总控智能体"""
    
    agent_id = "control_center_agent"
    agent_name = "智能助手"
    description = "总控智能体，负责接待用户、识别意图、智能分派"
    
    def __init__(self):
        super().__init__()
        self.supported_intents = ["general", "default", "fallback"]
    
    def can_handle(self, user_input: str) -> float:
        """判断是否能处理该请求（默认兜底智能体）"""
        return 0.1  # 低置信度，作为兜底
    
    def get_supported_intents(self) -> list:
        return self.supported_intents
    
    def handle(self, user_input: str, context: dict) -> str:
        """处理用户输入"""
        return _get_control_center().handle(user_input, context)


def register_all_agents():
    """
    注册所有智能体到注册中心
    """
    try:
        # 注册学校查询智能体
        agent_registry.register("school_inquiry_agent", SchoolInquiryAgent)
        
        # 注册分数推荐智能体
        agent_registry.register("score_recommendation_agent", ScoreRecommendationAgent)
        
        # 注册中考政策智能体
        agent_registry.register("policy_inquiry_agent", PolicyInquiryAgent)
        
        # 注册费用咨询智能体
        agent_registry.register("fee_inquiry_agent", FeeInquiryAgent)
        
        # 注册未央中学智能体
        agent_registry.register("weiyang_school_agent", WeiyangSchoolAgent)
        
        # 注册学习计划智能体
        agent_registry.register("study_plan_agent", StudyPlanAgent)
        
        # 注册校园生活智能体
        agent_registry.register("campus_life_agent", CampusLifeAgent)
        
        # 注册备考指导智能体
        agent_registry.register("exam_prep_agent", ExamPreparationAgent)
        
        # 注册心理辅导智能体
        agent_registry.register("mental_health_agent", MentalHealthAgent)
        
        # 注册总控智能体（作为默认智能体）
        agent_registry.register("control_center_agent", ControlCenterAgent, default=True)
        
        logger.info(f"成功注册 {len(agent_registry.list_agents())} 个智能体")
        
    except Exception as e:
        logger.error(f"智能体注册失败: {e}", exc_info=True)


def initialize_agents():
    """
    初始化智能体（在应用启动时调用）
    """
    try:
        register_all_agents()
        logger.info("智能体初始化完成")
    except Exception as e:
        logger.warning(f"智能体初始化失败: {e}")


# 移除模块加载时自动注册，改为显式调用
# register_all_agents()
