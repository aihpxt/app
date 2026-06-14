"""
智能体注册模块 - 简化版
负责注册所有智能体到注册中心
设计原则：
1. 不依赖外部 LLM 服务（避免 500 错误）
2. 所有智能体直接实现本地响应逻辑
3. 注册中心在模块加载时自动初始化
"""

import logging
from agents.registry import agent_registry, register_agent
from agents.base_agent import BaseAgent, ContextAwareAgent

logger = logging.getLogger(__name__)


# ============================================================
# 通用工具函数
# ============================================================

def _match_intent(user_input: str) -> str:
    """简单意图识别 - 基于关键词匹配"""
    text = (user_input or "").lower()

    greetings = ["你好", "您好", "hi", "hello", "在吗", "在么", "嗨", "哈喽", "早上好", "下午好", "晚上好"]
    farewells = ["再见", "拜拜", "bye", "goodbye"]
    thanks = ["谢谢", "感谢", "多谢", "thx", "thanks"]

    school_keywords = [
        "学校", "中学", "一中", "二中", "附中", "高中", "初中",
        "文山", "昆明", "曲靖", "玉溪", "保山", "昭通", "丽江", "普洱",
        "录取分数", "分数线", "一本率", "升学率",
        "排名", "怎么样", "介绍", "简介", "情况如何", "好不好", "如何",
        "可以报考", "能报", "报考"
    ]

    policy_keywords = [
        "政策", "政策解读", "招生政策", "报考政策", "中考政策",
        "指标到校", "定向", "统招", "择校", "志愿填报", "志愿",
        "自主招生", "民族班", "加分", "优惠", "规则"
    ]

    score_keywords = [
        "分数", "分", "预估分", "考了", "考多少", "能上", "推荐",
        "500", "600", "550", "580", "620", "650", "680", "700"
    ]

    study_keywords = [
        "学习", "复习", "备考", "计划", "方法", "技巧", "怎么学",
        "科目", "数学", "语文", "英语", "物理", "化学"
    ]

    fee_keywords = ["学费", "费用", "收费", "多少钱", "价格"]

    if any(g in text for g in greetings):
        return "greeting"
    if any(f in text for f in farewells):
        return "farewell"
    if any(t in text for t in thanks):
        return "thanks"
    if any(p in text for p in policy_keywords):
        return "policy"
    if any(s in text for s in school_keywords):
        return "school_query"
    if any(s in text for s in score_keywords):
        return "score"
    if any(s in text for s in study_keywords):
        return "study"
    if any(f in text for f in fee_keywords):
        return "fee"

    return "general"


# ============================================================
# 学校查询智能体
# ============================================================

class SchoolInquiryAgent(ContextAwareAgent):
    agent_id = "school_inquiry_agent"
    agent_name = "学校查询专家"
    description = "负责学校信息查询、学校对比、学校推荐等服务"

    def __init__(self):
        super().__init__()
        self.supported_intents = ["school_inquiry", "school_compare", "school_recommend"]

    def can_handle(self, user_input: str) -> float:
        text = (user_input or "").lower()
        keywords = ["学校", "中学", "一中", "二中", "附中", "高中", "对比", "推荐", "文山", "昆明", "未央", "丘北"]
        matches = sum(1 for kw in keywords if kw in text)
        return min(matches * 0.25, 1.0)

    def get_supported_intents(self) -> list:
        return self.supported_intents

    def handle(self, user_input: str, context: dict) -> str:
        return f"关于「{user_input}」，云南的优秀高中包括：\n\n" \
               f"🏫 **昆明市**：昆明市第一中学、云南师范大学附属中学、昆明市第三中学\n" \
               f"🏫 **文山州**：文山州第一中学、砚山县第一中学、丘北县第一中学\n" \
               f"🏫 **曲靖市**：曲靖市第一中学、曲靖市第二中学\n" \
               f"🏫 **玉溪市**：玉溪市第一中学\n\n" \
               f"如果您想了解具体学校的录取分数、一本率等详细信息，请告诉我学校名称，" \
               f"或者告诉我孩子的分数和所在城市，我可以为您推荐合适的学校。"


# ============================================================
# 分数推荐智能体
# ============================================================

class ScoreRecommendationAgent(ContextAwareAgent):
    agent_id = "score_recommendation_agent"
    agent_name = "分数推荐专家"
    description = "根据分数推荐合适的学校"

    def __init__(self):
        super().__init__()
        self.supported_intents = ["score_recommendation", "school_by_score"]

    def can_handle(self, user_input: str) -> float:
        text = (user_input or "").lower()
        keywords = ["分", "分数", "录取线", "能上", "推荐", "估分", "考了"]
        matches = sum(1 for kw in keywords if kw in text)
        return min(matches * 0.3, 1.0)

    def get_supported_intents(self) -> list:
        return self.supported_intents

    def handle(self, user_input: str, context: dict) -> str:
        return "分数是中考择校的关键参考。一般来说：\n\n" \
               "🌟 **680分以上**：可以冲刺顶级高中（如师大附中、昆一中）\n" \
               "🌟 **650-680分**：各地州重点中学尖子班\n" \
               "🌟 **600-650分**：各地州重点中学\n" \
               "🌟 **550-600分**：普通高中或较好的县中\n" \
               "🌟 **500-550分**：普通高中、民办高中\n\n" \
               "📊 云南省中考总分一般在 700-750 分左右（含体育）。\n\n" \
               "告诉我孩子的具体分数和所在城市，我可以为您做更精准的推荐！"


# ============================================================
# 中考政策智能体
# ============================================================

class PolicyInquiryAgent(ContextAwareAgent):
    agent_id = "policy_inquiry_agent"
    agent_name = "政策咨询专家"
    description = "负责中考政策解读、志愿填报指导等服务"

    def __init__(self):
        super().__init__()
        self.supported_intents = ["policy_inquiry", "volunteer_guidance", "exam_policy"]

    def can_handle(self, user_input: str) -> float:
        text = (user_input or "").lower()
        keywords = ["政策", "中考", "志愿", "填报", "录取规则", "招生", "加分"]
        matches = sum(1 for kw in keywords if kw in text)
        return min(matches * 0.3, 1.0)

    def get_supported_intents(self) -> list:
        return self.supported_intents

    def handle(self, user_input: str, context: dict) -> str:
        return "云南省中考政策主要包括以下内容：\n\n" \
               "📋 **招生方式**：统一招生、指标到校、自主招生相结合\n" \
               "📋 **志愿填报**：中考后估分或知分填报志愿，一般分多个批次\n" \
               "📋 **加分政策**：少数民族、烈士子女等可享受加分\n" \
               "📋 **民族班**：部分学校设有民族班，面向少数民族考生\n\n" \
               "具体政策以云南省教育厅当年发布的官方文件为准。"


# ============================================================
# 费用咨询智能体
# ============================================================

class FeeInquiryAgent(ContextAwareAgent):
    agent_id = "fee_inquiry_agent"
    agent_name = "费用咨询专家"
    description = "负责学费查询、费用咨询等服务"

    def __init__(self):
        super().__init__()
        self.supported_intents = ["fee_inquiry", "tuition", "cost"]

    def can_handle(self, user_input: str) -> float:
        text = (user_input or "").lower()
        keywords = ["学费", "费用", "收费", "多少钱", "价格"]
        matches = sum(1 for kw in keywords if kw in text)
        return min(matches * 0.3, 1.0)

    def get_supported_intents(self) -> list:
        return self.supported_intents

    def handle(self, user_input: str, context: dict) -> str:
        return "关于学校费用：\n\n" \
               "💰 **公立高中**：学费较低，一般每学期数百元\n" \
               "💰 **民办高中**：学费较高，一般每年1-3万元\n" \
               "💰 **住宿费**：根据学校条件，一般每年几百到几千元\n" \
               "💰 **其他费用**：书本费、校服费、伙食费等\n\n" \
               "具体费用请以学校官方公布的收费标准为准。"


# ============================================================
# 学习计划智能体
# ============================================================

class StudyPlanAgent(ContextAwareAgent):
    agent_id = "study_plan_agent"
    agent_name = "学习规划专家"
    description = "负责学习计划制定、备考指导等服务"

    def __init__(self):
        super().__init__()
        self.supported_intents = ["study_plan", "exam_prep", "learning"]

    def can_handle(self, user_input: str) -> float:
        text = (user_input or "").lower()
        keywords = ["学习", "备考", "复习", "计划", "方法", "提分", "科目"]
        matches = sum(1 for kw in keywords if kw in text)
        return min(matches * 0.25, 1.0)

    def get_supported_intents(self) -> list:
        return self.supported_intents

    def handle(self, user_input: str, context: dict) -> str:
        return "高效的中考备考建议：\n\n" \
               "📚 **制定计划**：按科目分配时间，薄弱科目多花时间\n" \
               "📚 **夯实基础**：先掌握教材知识点，再做难题\n" \
               "📚 **真题训练**：多做历年真题，熟悉出题规律\n" \
               "📚 **错题总结**：建立错题本，定期回顾\n" \
               "📚 **劳逸结合**：保证睡眠，适当运动\n" \
               "📚 **心态调整**：保持积极，避免焦虑\n\n" \
               "有具体的科目或学习问题，随时告诉我！"


# ============================================================
# 总控智能体（默认兜底）
# ============================================================

class ControlCenterAgent(ContextAwareAgent):
    agent_id = "control_center_agent"
    agent_name = "智能助手"
    description = "总控智能体，负责接待用户、识别意图、智能分派"

    def __init__(self):
        super().__init__()
        self.supported_intents = ["general", "default", "fallback"]

    def can_handle(self, user_input: str) -> float:
        return 0.05  # 很低的置信度，作为最后兜底

    def get_supported_intents(self) -> list:
        return self.supported_intents

    def handle(self, user_input: str, context: dict) -> str:
        intent = _match_intent(user_input)

        if intent == "greeting":
            return "你好！我是云南省中考择校智能助手小龙虾。我可以帮您查询学校信息、解读中考政策、推荐合适的学校。请问有什么可以帮您的？"
        if intent == "farewell":
            return "再见！祝您和孩子在中考中取得理想的成绩，考上心仪的学校！"
        if intent == "thanks":
            return "不客气！如果还有其他问题，随时问我~"
        if intent == "school_query":
            school_agent = SchoolInquiryAgent()
            return school_agent.handle(user_input, context)
        if intent == "policy":
            policy_agent = PolicyInquiryAgent()
            return policy_agent.handle(user_input, context)
        if intent == "score":
            score_agent = ScoreRecommendationAgent()
            return score_agent.handle(user_input, context)
        if intent == "study":
            study_agent = StudyPlanAgent()
            return study_agent.handle(user_input, context)
        if intent == "fee":
            fee_agent = FeeInquiryAgent()
            return fee_agent.handle(user_input, context)

        # 通用响应
        return f"我收到了您的问题：「{user_input}」。\n\n" \
               f"作为云南省中考择校助手，我可以为您提供以下帮助：\n" \
               f"🏫 学校信息查询\n" \
               f"📋 中考政策解读\n" \
               f"📊 根据分数推荐学校\n" \
               f"📚 学习备考建议\n\n" \
               f"请告诉我您具体想了解什么？"


# ============================================================
# 智能体注册
# ============================================================

_AGENT_CLASSES = [
    SchoolInquiryAgent,
    ScoreRecommendationAgent,
    PolicyInquiryAgent,
    FeeInquiryAgent,
    StudyPlanAgent,
    ControlCenterAgent,  # 最后注册，作为默认
]


def register_all_agents():
    """
    注册所有智能体到注册中心（幂等操作）
    """
    try:
        registered = 0
        # 使用公共 API list_agents() 而不是访问私有属性 _agents
        registered_ids = set(agent_registry.list_agents())
        for agent_class in _AGENT_CLASSES:
            try:
                if agent_class.agent_id not in registered_ids:
                    is_default = (agent_class.agent_id == "control_center_agent")
                    agent_registry.register(agent_class.agent_id, agent_class, default=is_default)
                    registered += 1
            except Exception as e:
                logger.warning(f"注册智能体 {agent_class.agent_id} 失败: {e}")

        logger.info(f"智能体注册完成，本次新增 {registered} 个，总计 {len(agent_registry.list_agents())} 个")
        return True
    except Exception as e:
        logger.error(f"智能体注册失败: {e}", exc_info=True)
        return False


def initialize_agents():
    """
    初始化智能体（在应用启动时调用）
    """
    try:
        register_all_agents()
        logger.info("智能体初始化完成")
        return True
    except Exception as e:
        logger.warning(f"智能体初始化失败: {e}")
        return False


# 模块加载时自动注册（确保无论在哪里导入，智能体都已就绪）
register_all_agents()
