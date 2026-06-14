"""
各角色智能体定义 - 11个专业智能体
"""

import logging
import time
import re
import threading
import functools
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openclaw.llm_service import LLMService
from openclaw.multi_llm_service import generate_with_fallback

# 尝试导入统一数据访问层
try:
    from unified_data_access import get_unified_data_access
    UNIFIED_DAL_AVAILABLE = True
except ImportError:
    UNIFIED_DAL_AVAILABLE = False

logger = logging.getLogger(__name__)


def error_handler(default_response="抱歉，系统暂时无法处理您的请求。请稍后再试，或换个方式提问。"):
    """错误处理装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                return default_response
        return wrapper
    return decorator


class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, name: str, role: str, description: str):
        self.name = name
        self.role = role
        self.description = description
    
    @abstractmethod
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """处理用户输入"""
        pass
    
    def get_info(self) -> Dict[str, str]:
        """获取智能体信息"""
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description
        }


class WebDeveloperAgent(BaseAgent):
    """网络开发工程师 - zk-dev"""
    
    def __init__(self):
        super().__init__(
            name="网络开发工程师",
            role="技术支持",
            description="负责网站技术问题、代码错误、系统异常等问题的处理"
        )
    
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        return (
            "🔧 您好，我是网络开发工程师。\n\n"
            "关于您遇到的技术问题，我需要了解更多细节：\n\n"
            "1️⃣ 您使用的是什么浏览器？（Chrome/Edge/手机浏览器）\n"
            "2️⃣ 具体出现了什么错误提示？\n"
            "3️⃣ 是在什么操作下出现的问题？\n\n"
            "请提供以上信息，我会尽快为您排查和解决。\n\n"
            "【常见问题快速解决】\n"
            "• 页面打不开 → 刷新页面或清除浏览器缓存\n"
            "• 表单提交失败 → 检查必填项是否填写完整\n"
            "• 加载慢 → 尝试切换网络或稍后重试"
        )


class UIDesignerAgent(BaseAgent):
    """UI美工 - zk-ui"""
    
    def __init__(self):
        super().__init__(
            name="UI美工",
            role="设计支持",
            description="负责海报设计、界面美化、图片处理等设计相关工作"
        )
    
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        return (
            "🎨 您好，我是UI美工。\n\n"
            "关于您的设计需求，我可以为您提供：\n\n"
            "✅ 活动海报设计（开放日、招生季等）\n"
            "✅ 界面优化建议\n"
            "✅ 图片处理和美化\n"
            "✅ 宣传物料设计\n"
            "✅ 品牌视觉统一\n\n"
            "请告诉我您的具体需求，包括：\n"
            "• 用途是什么？\n"
            "• 尺寸要求？\n"
            "• 风格偏好？\n\n"
            "我会为您提供专业的设计方案。"
        )


class InfoQueryAgent(BaseAgent):
    """信息获取与审核 - zk-info"""
    
    def __init__(self):
        super().__init__(
            name="信息获取与审核",
            role="信息服务",
            description="负责政策解读、学校信息查询、分数线查询等信息服务"
        )
        self.llm_service = LLMService()  # 初始化语言模型服务
    
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        user_lower = user_input.lower() if user_input else ""
        
        # 先获取基础回复
        if "未央" in user_lower or "丘北" in user_lower:
            base_response = self._get_weiyang_info()
        elif "政策" in user_lower:
            base_response = self._get_policy_info()
        elif "分数" in user_lower or "录取" in user_lower:
            base_response = self._get_score_info()
        elif "学校" in user_lower or "高中" in user_lower or "初中" in user_lower:
            base_response = self._get_school_info(original_input)
        else:
            base_response = self._get_general_info()
        
        # 先使用LLMService增强回复
        try:
            # 构建提示词
            prompt = f"作为信息获取与审核专员，针对用户问题：'{user_input}'，基于以下信息生成专业、准确的回复：\n\n{base_response}"
            # 调用LLM服务
            llm_result = self.llm_service.generate_answer(prompt)
            if llm_result and "answer" in llm_result:
                return llm_result["answer"]
        except Exception as e:
            logger.error(f"LLM服务调用失败: {e}")
            # LLMService失败时，使用multi_llm_service作为备用
            try:
                logger.info("尝试使用multi_llm_service作为备用")
                fallback_result = generate_with_fallback(prompt)
                if fallback_result and "answer" in fallback_result:
                    return fallback_result["answer"]
            except Exception as fallback_e:
                logger.error(f"备用LLM服务调用失败: {fallback_e}")
        
        # 如果所有LLM服务都失败，返回原始回复
        return base_response
    
    def _get_weiyang_info(self) -> str:
        return (
            "📚 丘北未央中学（文山州一中丘北校区）\n\n"
            "【学校定位】\n"
            "非营利性民办完全中学（初中+高中），文山州一中直管校区，2019年创办\n\n"
            "【办学优势】\n"
            "• 州一中直管：教学、管理、考试全部与州一中同步\n"
            "• 全封闭管理：24小时生活管理，适合需要严格管束的学生\n"
            "• 师资优质：州一中骨干教师领衔，本科100%、研究生超20%\n"
            "• 小班教学：个性化关注，每个孩子都能被照顾到\n\n"
            "【校园环境】\n"
            "园林式校园，设施齐全，智慧家校系统\n"
            "地址：丘北县文秀路129号\n"
            "电话：0876-4122666\n\n"
            "需要了解招生条件或学费吗？"
        )
    
    def _get_policy_info(self) -> str:
        return (
            "📋 云南省中考政策要点\n\n"
            "【考试科目】\n"
            "语文、数学、英语、物理、化学、道德与法治、历史、体育等\n\n"
            "【录取方式】\n"
            "• 公办高中：划片录取+志愿填报\n"
            "• 民办高中：自主招生\n\n"
            "【志愿填报】\n"
            "中考成绩公布后填报，一般可填报多个志愿\n\n"
            "需要了解具体地州的政策吗？告诉我您在哪个城市。"
        )
    
    def _get_score_info(self) -> str:
        return (
            "📊 录取分数线查询\n\n"
            "【2025年参考分数线】\n"
            "• 文山州一中：约620分\n"
            "• 丘北一中：约550分\n"
            "• 未央中学：参考平时成绩综合评估\n\n"
            "【说明】\n"
            "每年分数线会根据试卷难度和招生计划调整\n"
            "以上仅供参考，以官方发布为准\n\n"
            "需要了解具体学校的录取情况吗？"
        )
    
    @error_handler(default_response="抱歉，暂时无法获取该学校信息。请稍后再试，或询问其他学校。")
    def _get_school_info(self, user_input: str) -> str:
        """获取学校信息"""
        user_lower = user_input.lower()
        
        if "昆明" in user_lower and ("一级一等" in user_lower or "一级" in user_lower):
            return (
                "🏫 昆明市一级一等高中\n\n"
                "【主要学校】\n"
                "• 云南师范大学附属中学\n"
                "• 昆明市第一中学\n"
                "• 昆明市第三中学\n"
                "• 昆明市第八中学\n"
                "• 昆明市第十四中学\n"
                "• 云南大学附属中学\n\n"
                "【特点】\n"
                "• 教学质量高，师资力量强\n"
                "• 一本率高，升学质量好\n"
                "• 设施完善，校园环境优美\n\n"
                "需要了解具体学校的详细信息吗？"
            )
        elif "文山" in user_lower or "丘北" in user_lower:
            return (
                "🏫 文山州主要高中\n\n"
                "【公办高中】\n"
                "• 文山州第一中学（州属重点）\n"
                "• 丘北县第一中学\n"
                "• 砚山县第一中学\n\n"
                "【民办高中】\n"
                "• 丘北未央中学（文山州一中丘北校区）\n"  
                "• 砚山润泽学校\n\n"
                "需要了解具体学校的详细信息吗？"
            )
        else:
            return (
                "🏫 学校信息查询\n\n"
                "【热门学校推荐】\n"
                "• 昆明市：云师大附中、昆明一中、昆三中\n"
                "• 曲靖市：曲靖一中、曲靖二中\n"
                "• 玉溪市：玉溪一中、玉溪师院附中\n"
                "• 文山州：文山州一中、丘北未央中学\n\n"
                "【学校类型】\n"
                "• 公办高中：收费低，师资稳定\n"
                "• 民办高中：管理严格，特色鲜明\n\n"
                "需要了解哪个地州或具体学校的信息？"
            )
    
    def _get_general_info(self) -> str:
        return (
            "您好，我是信息获取与审核专员。\n\n"
            "我可以为您提供：\n"
            "✅ 中考政策解读\n"
            "✅ 学校信息查询\n"
            "✅ 录取分数线查询\n"
            "✅ 招生计划查询\n"
            "✅ 未央中学详细介绍\n\n"
            "请告诉我您想了解的具体信息。"
        )


class MarketingAgent(BaseAgent):
    """市场品宣与推广 - zk-marketing"""
    
    def __init__(self):
        super().__init__(
            name="市场品宣与推广",
            role="市场推广",
            description="负责市场推广、文案策划、引流宣传等市场相关工作"
        )
    
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        return (
            "📢 您好，我是市场品宣与推广专员。\n\n"
            "关于您的推广需求，我可以为您提供：\n\n"
            "✅ 公众号/小红书/抖音文案\n"
            "✅ #云南中考 #文山中考 #丘北小升初 话题内容\n"
            "✅ 引流策略和推广方案\n"
            "✅ 家长关心问题合集\n\n"
            "请告诉我您的具体需求：\n"
            "• 目标平台是什么？\n"
            "• 目标人群是谁？\n"
            "• 推广目的是什么？\n\n"
            "我会为您制定专业的推广方案。"
        )


class OutProvinceAgent(BaseAgent):
    """外省市场拓展专员 - zk-outside"""
    
    def __init__(self):
        super().__init__(
            name="外省市场拓展专员",
            role="外省服务",
            description="负责贵州、四川、广西等外省市场拓展和服务"
        )
    
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        return (
            "🌐 您好，我是外省市场拓展专员。\n\n"
            "关于外省服务，我需要了解：\n\n"
            "1️⃣ 您来自哪个省份？\n"
            "2️⃣ 您的具体需求是什么？\n\n"
            "【目前覆盖省份】\n"
            "• 云南省（主要服务区域）\n"
            "• 贵州省（拓展中）\n"
            "• 四川省（拓展中）\n"
            "• 广西壮族自治区（拓展中）\n\n"
            "如果您是外省家长想了解云南学校，或想在我们平台拓展外省业务，请详细说明您的需求。"
        )


class FinanceAgent(BaseAgent):
    """财务 - zk-finance"""
    
    def __init__(self):
        super().__init__(
            name="财务",
            role="财务服务",
            description="负责费用咨询、价格查询、收费标准等财务相关问题"
        )
    
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        user_lower = user_input.lower() if user_input else ""
        
        if "未央" in user_lower and ("学费" in user_lower or "收费" in user_lower or "多少钱" in user_lower):
            return self._get_weiyang_fee()
        
        return (
            "💰 您好，我是财务专员。\n\n"
            "【收费标准说明】\n"
            "• 基础咨询服务：免费\n"
            "• 深度择校方案：根据需求定制\n"
            "• 所有收费透明公开，开具正规发票\n\n"
            "【未央中学收费】\n"
            "民办寄宿制学校，费用包含学费、住宿费、伙食费等\n"
            "具体收费标准每年可能调整\n\n"
            "为避免信息过时，建议您留个微信\n"
            "我把最新的收费明细发给您\n\n"
            "【重要声明】\n"
            "所有费用以学校官方公布为准"
        )
    
    def _get_weiyang_fee(self) -> str:
        return (
            "💰 丘北未央中学2026年收费标准\n\n"
            "【初中部收费】\n"
            "• 公费生（英才班）：语数平均分≥180分，学费0元/学期\n"
            "• 自费生A类（实验班）：语数平均分160-179分，学费3900元/学期\n"
            "• 自费生B类（平行班）：语数平均分＜160分，学费4900元/学期\n"
            "• 住宿费：600元/学期（所有学生）\n\n"
            "【高中部收费】（按中考裸分）\n"
            "• 620分以上：学费0元 + 住宿费0元\n"
            "• 600-619分：学费800元 + 住宿费600元\n"
            "• 570-599分：学费2000元 + 住宿费600元\n"
            "• 540-569分：学费2500元 + 住宿费600元\n"
            "• 510-539分：学费3000元 + 住宿费600元\n"
            "• 480-509分：学费3500元 + 住宿费600元\n"
            "• 450-479分：学费4000元 + 住宿费600元\n"
            "• 420-449分：学费5000元 + 住宿费600元\n\n"
            "【奖学金政策】\n"
            "• 初一奖学金：语数总分200分奖励5万元，199分奖励4万元\n"
            "• 高一奖学金：中考全州第1名奖励30万元，第2名25万元\n"
            "• 高考奖学金：考入清华北大额外奖励10万元\n\n"
            "【联系方式】\n"
            "招生热线：0876-4122666\n"
            "地址：丘北县锦屏镇文秀路129号（弘毅楼一楼招生办）"
        )


class LegalAgent(BaseAgent):
    """法务合规 - zk-legal"""
    
    def __init__(self):
        super().__init__(
            name="法务合规",
            role="法务支持",
            description="负责合同审核、法律咨询、纠纷处理等法务相关工作"
        )
    
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        return (
            "⚖️ 您好，我是法务合规专员。\n\n"
            "【合规声明】\n"
            "我们严格遵守相关法律法规，以下是我们服务的边界：\n\n"
            "❌ 我们不做：\n"
            "• 不承诺录取、不包上高中、不提供内部指标\n"
            "• 不提分保证、不与教育局合作、不提供独家渠道\n"
            "• 不保证百分百上岸\n\n"
            "✅ 我们只做：\n"
            "• 政策解读、学校介绍、择校建议、信息参考\n"
            "• 所有数据以官方发布为准\n"
            "• 所有服务以咨询、指导、信息服务为主\n\n"
            "如果您有合同、协议、纠纷等相关问题，请详细说明，我会为您提供专业建议。"
        )


class ConversionAgent(BaseAgent):
    """促单转化专员 - zk-sales"""
    
    def __init__(self):
        super().__init__(
            name="促单转化专员",
            role="转化服务",
            description="负责报名咨询、预约服务、开放日安排等转化相关工作"
        )
    
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        return (
            "🎯 您好，我是促单转化专员。\n\n"
            "关于报名和预约，我可以为您提供：\n\n"
            "✅ 未央中学报名咨询\n"
            "✅ 校园开放日预约\n"
            "✅ 一对一咨询服务\n"
            "✅ 招生简章发送\n\n"
            "【报名流程】\n"
            "1. 咨询了解 → 2. 预约看校 → 3. 提交资料 → 4. 综合评估 → 5. 办理入学\n\n"
            "【留资福利】\n"
            "留下您的微信，我免费发送：\n"
            "📋 未央中学招生简章\n"
            "📋 最新收费标准\n"
            "📋 校园开放日预约链接\n\n"
            "请问您的孩子现在是几年级？"
        )


class PaymentAgent(BaseAgent):
    """缴费办理专员 - zk-pay"""
    
    def __init__(self):
        super().__init__(
            name="缴费办理专员",
            role="缴费服务",
            description="负责缴费办理、支付处理、订单查询等缴费相关工作"
        )
    
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        return (
            "💳 您好，我是缴费办理专员。\n\n"
            "【缴费方式】\n"
            "• 微信支付\n"
            "• 支付宝支付\n"
            "• 银行转账\n"
            "• 现场缴费\n\n"
            "【缴费流程】\n"
            "1. 确认缴费项目\n"
            "2. 核对金额\n"
            "3. 选择支付方式\n"
            "4. 完成支付\n"
            "5. 获取缴费凭证\n\n"
            "【注意事项】\n"
            "• 请保存好缴费凭证\n"
            "• 如需发票请提前说明\n"
            "• 有问题随时联系\n\n"
            "请问您需要办理什么缴费业务？"
        )


class LogisticsAgent(BaseAgent):
    """后勤保障服务 - zk-logistics"""
    
    def __init__(self):
        super().__init__(
            name="后勤保障服务",
            role="后勤支持",
            description="负责参观接待、交通指引、食宿安排等后勤相关工作"
        )
    
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        user_lower = user_input.lower() if user_input else ""
        
        if "参观" in user_lower or "看校" in user_lower or "开放日" in user_lower:
            return self._get_visit_info()
        elif "宿舍" in user_lower or "住宿" in user_lower:
            return self._get_dorm_info()
        elif "食堂" in user_lower or "吃饭" in user_lower:
            return self._get_canteen_info()
        elif "路线" in user_lower or "怎么走" in user_lower or "地址" in user_lower:
            return self._get_location_info()
        else:
            return self._get_general_info()
    
    def _get_visit_info(self) -> str:
        return (
            "🏛️ 丘北未央中学校园参观预约\n\n"
            "【开放时间】\n"
            "• 工作日：8:30-17:00\n"
            "• 周末：9:00-16:00\n"
            "无需提前预约，可直接到校参观\n\n"
            "【参观内容】\n"
            "• 教学楼、教室（智慧教室展示）\n"
            "• 学生宿舍（4-6人间，独立卫生间）\n"
            "• 食堂餐厅（自营食堂，菜品丰富）\n"
            "• 运动场馆（足球场、篮球场、体育馆）\n"
            "• 图书馆、实验室\n"
            "• 校园环境（园林式校园）\n\n"
            "【预约看校福利】\n"
            "到校参观即可领取：\n"
            "• 未央中学招生简章\n"
            "• 2026年收费标准\n"
            "• 校园精美画册\n\n"
            "【学校地址】\n"
            "丘北县锦屏镇文秀路129号（弘毅楼一楼招生办）\n\n"
            "【招生热线】\n"
            "0876-4122666\n\n"
            "【交通指引】\n"
            "• 丘北县城内可步行或打车\n"
            "• 周边停车场充足，免费停车"
        )
    
    def _get_dorm_info(self) -> str:
        return (
            "🏠 丘北未央中学宿舍情况\n\n"
            "【宿舍配置】\n"
            "• 标准4-6人间，上床下桌设计\n"
            "• 独立卫生间、洗漱间\n"
            "• 24小时热水供应\n"
            "• 空调、储物柜、书桌齐全\n"
            "• 每层楼配备公共洗衣房\n\n"
            "【管理特点】\n"
            "• 全封闭管理，出入刷卡登记\n"
            "• 生活老师24小时值班\n"
            "• 统一作息：早6:30起床，晚22:30熄灯\n"
            "• 每日内务检查，培养良好习惯\n"
            "• 定期组织宿舍文化活动\n\n"
            "【住宿费用】\n"
            "• 600元/学期（所有学生统一标准）\n\n"
            "建议您带孩子实地参观，亲眼看看宿舍环境"
        )
    
    def _get_canteen_info(self) -> str:
        return (
            "🍽️ 丘北未央中学食堂情况\n\n"
            "【食堂特点】\n"
            "• 学校自营食堂，不外包\n"
            "• 食材新鲜，每日配送\n"
            "• 食品安全等级A级，卫生管理严格\n"
            "• 专业营养师配餐，营养均衡\n\n"
            "【用餐安排】\n"
            "• 早餐：6:30-7:30\n"
            "• 午餐：11:30-12:30\n"
            "• 晚餐：17:30-18:30\n"
            "• 宵夜：21:00-21:30（住校生）\n\n"
            "【菜品特色】\n"
            "• 每餐8-10个菜品选择\n"
            "• 提供清真窗口\n"
            "• 每日特色菜轮换\n"
            "• 汤品免费供应\n\n"
            "【用餐费用】\n"
            "• 充卡消费，按需点餐\n"
            "• 日均消费约30-40元\n\n"
            "欢迎您来校实地考察食堂环境"
        )
    
    def _get_location_info(self) -> str:
        return (
            "📍 学校位置与交通\n\n"
            "【学校地址】\n"
            "丘北县文秀路129号\n"
            "近普者黑景区，交通便利\n\n"
            "【交通指引】\n"
            "• 自驾：导航搜索'丘北未央中学'\n"
            "• 公交：可乘坐当地公交到达\n\n"
            "【停车】\n"
            "校内设有停车场，参观可停车\n\n"
            "需要我帮您预约参观吗？"
        )
    
    def _get_general_info(self) -> str:
        return (
            "🛎️ 您好，我是后勤保障服务专员。\n\n"
            "我可以为您提供：\n"
            "✅ 学校参观预约\n"
            "✅ 交通路线指引\n"
            "✅ 食堂、宿舍介绍\n"
            "✅ 开放日安排\n"
            "✅ 周边食宿推荐\n\n"
            "请告诉我您的具体需求。"
        )


class ControlCenterSpecialistAgent(BaseAgent):
    """总控智能体 - 处理中考择校相关咨询"""
    
    def __init__(self):
        super().__init__(
            name="总控智能体",
            role="总调度",
            description="负责接待用户、识别意图、智能分派、统一回复"
        )
        self.llm_service = LLMService()  # 初始化语言模型服务
        
    def _extract_school_from_history(self, history: List[Dict[str, Any]]) -> str:
        """从历史消息中提取提到的学校名称"""
        school_keywords = ['中学', '高中', '一中', '二中', '三中', '附中', '实验中学', '外国语']
        
        # 从最新的消息开始查找
        for msg in reversed(history):
            content = msg.get('content', '')
            for keyword in school_keywords:
                if keyword in content:
                    # 提取学校名称（简单的启发式方法）
                    words = content.replace('，', ' ').replace('。', ' ').replace('？', ' ').split()
                    for word in words:
                        if keyword in word:
                            return word
        return ""
    
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        import json
        
        # 优先使用原始输入进行意图识别（避免Hermes重写后的文本干扰）
        original_input = context.get('original_input', user_input) if context else user_input
        
        # 从context中获取历史消息
        history = context.get('history', []) if context else []
        context_school = self._extract_school_from_history(history) if history else ""
        
        # ==================== 基本输入验证 ====================
        # 检查空输入或无效输入
        if not original_input or not original_input.strip():
            return (
                "您好！有什么我可以帮您的吗？\n\n"
                "您可以告诉我：\n"
                "• 想了解的学校名称\n"
                "• 孩子的年级和分数\n"
                "• 想咨询的问题（如志愿填报、政策等）\n\n"
                "请输入您的问题，我来为您解答！"
            )
        
        user_input_lower = original_input.lower() if original_input else ""
        logger.info(f"ControlCenterSpecialistAgent.handle called - input: '{user_input}', original: '{original_input}', context_has_original: {context.get('original_input') is not None if context else False}")
        
        # 获取会话状态
        session_id = context.get('session_id') if context else None
        previous_context = None
        response = None
        add_follow_up = True  # 初始化跟进问题标志
        
        # 提取Hermes智能分析结果
        hermes_emotion = context.get('hermes_emotion', {}) if context else {}
        hermes_insight = context.get('hermes_insight', {}) if context else {}
        hermes_data = context.get('hermes_data', {}) if context else {}
        
        # 从缓存获取会话状态
        if session_id:
            try:
                from app.core.cache import session_cache_manager
                cached_data = session_cache_manager.get_session(session_id)
                if cached_data:
                    previous_context = cached_data
                    logger.info(f"Found session {session_id} with previous context")
                    logger.info(f"Session data - last_answer: {cached_data.get('last_answer', '')[:50]}...")
                    logger.info(f"Session data - topic: {cached_data.get('topic', '')}")
                    logger.info(f"Session data - conversation_history length: {len(cached_data.get('conversation_history', []))}")
                else:
                    logger.info(f"Session {session_id} not found in cache")
            except Exception as e:
                logger.error(f"Failed to get session from cache: {e}")
        
        # ==================== 智能输入验证（基于上下文） ====================
        import re
        # 检查是否为无意义输入（在有上下文时更宽松）
        if len(original_input.strip()) < 2:
            # 如果有会话上下文，允许简短回答
            if previous_context and previous_context.get('conversation_history'):
                # 简短回答由上下文处理逻辑处理，不拦截
                pass
            else:
                return (
                    "您的输入太短了，请重新描述您的问题。\n\n"
                    "比如：\n"
                    "• '昆明有哪些好高中'\n"
                    "• '孩子中考能考650分'\n"
                    "• '师大附中怎么样'"
                )
        
        # 检查是否为纯特殊字符
        if not re.search(r'[\u4e00-\u9fa5a-zA-Z0-9]', original_input):
            return (
                "抱歉，我没有理解您的问题。\n\n"
                "请您用中文或英文描述您想咨询的内容，比如：\n"
                "• '昆明高中录取分数'\n"
                "• '中考志愿怎么填'\n"
                "• '师大附中好不好'"
            )
        
        # 检查是否为上下文相关回复
        is_context_response = False
        
        # 初始化变量
        last_answer = ""
        last_question = ""
        conversation_history = []
        topic = ""
        topic_history = []
        history_text = ""
        history_text_lower = ""
        
        # 优先从缓存获取会话状态
        if previous_context:
            last_answer = previous_context.get('last_answer', '')
            last_question = previous_context.get('last_question', '')
            conversation_history = previous_context.get('conversation_history', [])
            topic = previous_context.get('topic', '')
            topic_history = previous_context.get('topic_history', [])  # 获取话题历史
        
        # 如果有从数据库获取的历史消息，也可以用于上下文分析
        if history:
            # 从数据库历史消息中提取最后一条助手回复
            for msg in reversed(history):
                if msg.get('role') == 'assistant':
                    last_answer = msg.get('content', '')
                    break
            for msg in reversed(history):
                if msg.get('role') == 'user':
                    last_question = msg.get('content', '')
                    break
            # 从数据库历史消息构建history_text
            history_text = " ".join([msg.get('content', '') for msg in history if msg.get('role') == 'user'])
            history_text_lower = history_text.lower()
        
        # 如果有conversation_history，也合并到history_text中
        if conversation_history:
            for item in conversation_history:
                if 'question' in item:
                    history_text += item['question'] + " "
            history_text_lower = history_text.lower()
        
        # ==================== 上下文处理逻辑（只要有历史消息或缓存上下文就执行） ====================
        # 检测"回到之前的话题"等指令
        back_to_topic = False
        back_to_topic_phrases = [
            "回到", "之前", "刚才", "刚才说的", "之前说的",
            "继续说", "接着说", "再说说", "回到那个",
            "再说一下", "继续聊", "回到之前"
        ]
        if any(phrase in user_input_lower for phrase in back_to_topic_phrases):
            # 尝试回到之前的话题
            if len(topic_history) >= 2:
                # 使用倒数第二个话题
                previous_topic = topic_history[-2]
                logger.info(f"用户请求回到之前的话题: {previous_topic}")
                topic = previous_topic
                back_to_topic = True
                # 根据话题生成响应
                if previous_topic == "未央中学":
                    response = self._get_weiyang_info()
                    is_context_response = True
                elif previous_topic == "昆明学校":
                    response = "好的，我们继续聊聊昆明的学校。您想了解哪所学校的详细信息？"
                    is_context_response = True
                elif previous_topic == "分数推荐":
                    response = "好的，我们继续聊聊分数和学校推荐。您孩子的分数是多少？"
                    is_context_response = True
                elif previous_topic == "中考政策":
                    response = "好的，我们继续聊聊中考政策。您想了解哪方面的政策？"
                    is_context_response = True

        # ==================== 话题切换检测 ====================
        current_topic = self._detect_topic(original_input) if not back_to_topic else topic
        topic_switched = False
        if topic and topic != "其他" and current_topic != topic:
            # 检测话题是否切换
            topic_keywords = {
                "未央中学": ["未央", "丘北"],
                "昆明学校": ["昆明", "昆一中", "昆三中", "师大附中"],
                "中考政策": ["政策", "中考", "志愿", "填报"],
                "分数推荐": ["分", "分数", "录取线", "能上"],
                "学习计划": ["学习", "备考", "复习", "计划"],
                "费用咨询": ["学费", "费用", "收费", "价格"]
            }
            old_keywords = topic_keywords.get(topic, [])
            if old_keywords and not any(kw in user_input_lower for kw in old_keywords):
                # 话题已切换到新话题
                topic_switched = True
                logger.info(f"检测到话题切换: {topic} -> {current_topic}")

        # ==================== 否定回复（优先检查） ====================
        # 检查是否为否定回复 - 放在最前面优先处理
        negative_responses = ["不需要", "不用", "算了", "不", "不要", "不用了", "暂时不需要", "下次再说", "不需要了"]
        if user_input_lower.strip() in negative_responses:
            is_context_response = True
            logger.info(f"Detected negative context response: {user_input_lower}")
            response = "好的，如果您以后有需要，随时可以再来咨询我！再见！👋"
            add_follow_up = False  # 直接设置为False，避免后续添加跟进问题
        
        # ==================== 指代词理解（上下文追问） ====================
        # 检查是否包含指代词（扩展版）
        pronouns = ["这个", "那个", "它", "这所", "那所", "这些", "那些", "此", "其"]
        has_pronoun = any(word in user_input_lower for word in ["这个", "那个", "它", "这所", "那所", "这些", "那些", "此", "其"])
        
        logger.info(f"[DEBUG] has_pronoun: {has_pronoun}, user_input_lower: '{user_input_lower}'")
        logger.info(f"[DEBUG] context_school: '{context_school}'")
        
        if has_pronoun:
            logger.info(f"[DEBUG] 进入指代词处理代码块")
            is_context_response = True
            
            # 首先检查从历史消息中提取的学校名称
            if context_school:
                logger.info(f"[DEBUG] context_school 不为空")
                if "分数线" in user_input_lower or "录取线" in user_input_lower:
                    logger.info(f"[DEBUG] 检测到分数线关键词")
                    response = (
                        f"根据您提到的\"{context_school}\"，我来为您查询相关信息。\n\n"
                        f"{context_school}的录取分数线会因年份和地区而有所不同。一般来说：\n\n"
                        "• 一级一等高完中：580-650分\n"
                        "• 一级二等高完中：540-580分\n"
                        "• 普通高完中：480-540分\n\n"
                        "建议您使用我们的学校查询功能获取最新、最准确的录取分数线信息。"
                    )
                    add_follow_up = False
                    logger.info(f"[DEBUG] 已设置响应: {response[:50]}...")
                elif "怎么样" in user_input_lower or "好吗" in user_input_lower:
                    response = self._get_school_info(context_school)
                    add_follow_up = False
                elif "学费" in user_input_lower or "费用" in user_input_lower:
                    response = (
                        f"关于{context_school}的费用情况：\n\n"
                        "【公办高中（重点高中）】\n"
                        "• 学费：约200-400元/学期（公办学校学费较低）\n"
                        "• 住宿费：约300-600元/学期\n"
                        "• 教辅费：约500-1000元/学期\n\n"
                        "【民办高中】\n"
                        "• 学费：约5000-20000元/学期不等\n"
                        "• 住宿费：约800-1500元/学期\n\n"
                        f"具体费用以{context_school}官方公布为准。"
                    )
                    add_follow_up = False
            
            # 如果当前话题是未央中学，直接处理
            if response is None and (topic == "未央中学" or "未央" in last_answer or "丘北" in last_answer):
                if "学费" in user_input_lower or "费用" in user_input_lower:
                    response = self._get_weiyang_enrollment_info()
                elif "怎么样" in user_input_lower or "好吗" in user_input_lower:
                    response = self._get_weiyang_info()
                elif "录取" in user_input_lower or "分数" in user_input_lower:
                    response = self._get_weiyang_enrollment_info()
                else:
                    response = self._get_weiyang_info()
            elif response is None and (topic == "昆明学校" or "昆明" in last_answer):
                logger.info(f"[DEBUG] 进入昆明学校逻辑，response 是 None: {response is None}")
                # 昆明相关话题
                if "学费" in user_input_lower or "费用" in user_input_lower:
                    response = (
                        "关于昆明重点高中的费用情况：\n\n"
                        "【公办高中（重点高中）】\n"
                        "• 学费：约200-400元/学期（公办学校学费较低）\n"
                        "• 住宿费：约300-600元/学期\n"
                        "• 教辅费：约500-1000元/学期\n\n"
                        "【民办高中】\n"
                        "• 学费：约5000-20000元/学期不等\n"
                        "• 住宿费：约800-1500元/学期\n\n"
                        "【部分学校参考】\n"
                        "• 师大附中（公办）：学费约300元/学期\n"
                        "• 昆一中（公办）：学费约300元/学期\n"
                        "• 云大附中（民办）：学费约15000元/学期\n\n"
                        "具体费用以学校官方公布为准。"
                    )
                elif "怎么样" in user_input_lower or "好吗" in user_input_lower:
                    response = self._get_school_info("昆明重点高中")
                else:
                    logger.info(f"[DEBUG] 进入 else 分支，调用 _get_policy_info")
                    response = self._get_policy_info(user_input)
            elif response is None and (topic == "分数推荐" or "推荐学校" in last_answer):
                # 分数推荐相关话题 - 用户追问推荐学校的详细信息
                # 优先检查是否包含学校名称
                school_keywords = ["师大附中", "昆一中", "昆三中", "云大附中", "昆明", "中学", "高中"]
                has_school = any(word in original_input.lower() for word in school_keywords)
                if has_school:
                    response = self._get_school_info(original_input)
                elif "学费" in user_input_lower or "费用" in user_input_lower:
                    response = (
                        "关于云南高中的费用情况：\n\n"
                        "【公办高中（重点高中）】\n"
                        "• 学费：约200-400元/学期（公办学校学费较低）\n"
                        "• 住宿费：约300-600元/学期\n"
                        "• 教辅费：约500-1000元/学期\n\n"
                        "【民办高中】\n"
                        "• 学费：约5000-20000元/学期不等\n"
                        "• 住宿费：约800-1500元/学期\n\n"
                        "【部分学校参考】\n"
                        "• 师大附中（公办）：学费约300元/学期\n"
                        "• 昆一中（公办）：学费约300元/学期\n"
                        "• 云大附中（民办）：学费约15000元/学期\n"
                        "• 文山州一中（公办）：学费约300元/学期\n\n"
                        "具体费用以各学校官方公布为准。您之前关注的学校需要我详细说明费用吗？"
                    )
                elif "怎么样" in user_input_lower or "好吗" in user_input_lower:
                    response = self._get_school_info(user_input)
                elif "录取" in user_input_lower or "分数" in user_input_lower:
                    response = self._get_school_recommendation_by_score(original_input)
                else:
                    response = self._get_school_info(original_input)
            else:
                # 其他话题，使用指代词解析
                referenced_entity = self._resolve_pronoun(user_input_lower, conversation_history, last_answer, topic)
                logger.info(f"Detected pronoun reference: {user_input_lower}, resolved to: {referenced_entity}")
                if referenced_entity:
                    if "学费" in user_input_lower or "费用" in user_input_lower:
                        if "未央" in referenced_entity or "丘北" in referenced_entity:
                            response = self._get_weiyang_enrollment_info()
                        else:
                            response = self._get_policy_info(user_input)
                    elif "怎么样" in user_input_lower or "好吗" in user_input_lower:
                        response = self._get_school_info(referenced_entity)
                    else:
                        response = self._get_school_info(referenced_entity)
        
        # ==================== 指代词+学费/费用（上下文追问，旧逻辑保持兼容） ====================
        elif any(word in user_input_lower for word in ["这些", "那些", "这所", "那所"]) and any(word in user_input_lower for word in ["学费", "费用", "价钱"]):
            logger.info(f"Detected context reference with fee query: {user_input_lower}")
            # 检查历史中是否有昆明学校推荐
            if ("昆明" in history_text_lower or "昆明" in last_question.lower()) and ("推荐" in history_text_lower or "学校" in history_text_lower):
                is_context_response = True
                response = (
                    "关于昆明重点高中的费用情况：\n\n"
                    "【公办高中（重点高中）】\n"
                    "• 学费：约200-400元/学期（公办学校学费较低）\n"
                    "• 住宿费：约300-600元/学期\n"
                    "• 教辅费：约500-1000元/学期\n\n"
                    "【民办高中】\n"
                    "• 学费：约5000-20000元/学期不等\n"
                    "• 住宿费：约800-1500元/学期\n\n"
                    "【部分学校参考】\n"
                    "• 师大附中（公办）：学费约300元/学期\n"
                    "• 昆一中（公办）：学费约300元/学期\n"
                    "• 云大附中（民办）：学费约15000元/学期\n\n"
                    "具体费用以学校官方公布为准。需要了解其他学校的信息吗？"
                )
            elif "未央" in history_text_lower or "丘北" in history_text_lower:
                is_context_response = True
                response = self._get_weiyang_enrollment_info()
        
        # ==================== 推荐请求处理 ====================
        # 检查是否为"还有其他推荐吗？"这类问题
        elif any(phrase in user_input_lower for phrase in ["还有其他", "其他推荐", "还有什么", "还有哪些"]):
            logger.info(f"Detected recommendation request: {user_input_lower}")
            is_context_response = True
            # 根据当前话题生成推荐
            if topic == "未央中学" or "未央" in last_answer or "丘北" in last_answer:
                # 推荐其他文山州的学校
                response = (
                    "除了未央中学，文山州还有这些优质学校可以考虑：\n\n"
                    "【文山州一中本部】\n"
                    "• 类型：公办省一级一等高中\n"
                    "• 特色：文山州最好的公办高中，升学率高\n"
                    "• 地址：文山市开化街道\n\n"
                    "【文山州二中】\n"
                    "• 类型：公办省一级二等高中\n"
                    "• 特色：文科优势明显\n"
                    "• 地址：文山市卧龙街道\n\n"
                    "【砚山一中】\n"
                    "• 类型：公办省一级三等高中\n"
                    "• 特色：理科实力强\n"
                    "• 地址：砚山县江那镇\n\n"
                    "需要了解哪所学校的详细信息？"
                )
            elif topic == "昆明学校" or "昆明" in last_answer:
                # 推荐其他昆明的学校
                response = (
                    "除了之前提到的学校，昆明还有这些优质高中：\n\n"
                    "【昆三中】\n"
                    "• 类型：公办省一级一等高中\n"
                    "• 特色：科技教育突出，升学率高\n"
                    "• 地址：昆明市呈贡区\n\n"
                    "【昆八中】\n"
                    "• 类型：公办省一级一等高中\n"
                    "• 特色：管理严格，学风优良\n"
                    "• 地址：昆明市五华区\n\n"
                    "【云大附中】\n"
                    "• 类型：民办省一级一等高中\n"
                    "• 特色：名校资源，师资雄厚\n"
                    "• 地址：昆明市呈贡区\n\n"
                    "需要了解哪所学校的详细信息？"
                )
            else:
                # 通用推荐
                response = (
                    "当然！根据您的需求，我可以推荐这些方向：\n\n"
                    "【重点高中推荐】\n"
                    "• 昆明：师大附中、昆一中、昆三中\n"
                    "• 文山：文山州一中、未央中学\n\n"
                    "【特色学校推荐】\n"
                    "• 艺术特色：云南艺术学院附属中学\n"
                    "• 体育特色：昆明市体育学校\n\n"
                    "您想了解哪个地区或类型的学校？"
                )
        
        # ==================== 简短肯定回复 ====================
        # 检查是否为简短肯定回复
        elif user_input_lower.strip() in ["需要", "是的", "好的", "想", "要", "可以", "嗯", "对", "是", "了解", "咨询", 
                                          "好", "行", "没问题", "可以的", "愿意", "感兴趣", "想了解", "想知道"]:
            is_context_response = True
            logger.info(f"Detected context response: {user_input_lower}")
            # 根据历史对话和话题决定回复内容
            if topic == "未央中学" or "未央" in last_answer or "丘北" in last_answer:
                logger.info("Returning weiyang enrollment info based on context")
                # 检查最后回答是否包含特定信息
                if "学费" in last_answer or "费用" in last_answer:
                    response = (
                        "好的！关于未央中学的学费：\n\n"
                        "【学费标准】\n"
                        "• 英才班（公费）：0元/学期\n"
                        "• 英才班（自费）：根据分数段确定\n"
                        "• 实验班：3900元/学期\n"
                        "• 平行班：4900元/学期\n\n"
                        "【其他费用】\n"
                        "• 住宿费：600元/学期\n"
                        "• 教辅费：约500-1000元/学期\n\n"
                        "需要了解招生条件或报名流程吗？"
                    )
                elif "参观" in last_answer or "预约" in last_answer:
                    response = (
                        "好的！关于参观预约：\n\n"
                        "【参观时间】\n"
                        "• 工作日：8:30-17:00\n"
                        "• 周末及节假日：9:00-16:00\n\n"
                        "【学校地址】\n"
                        "丘北县锦屏镇文秀路129号\n\n"
                        "【招生热线】\n"
                        "0876-4122666\n\n"
                        "需要我帮您联系负责老师吗？"
                    )
                else:
                    response = self._get_weiyang_enrollment_info()
            elif topic == "预约看校" or "预约看校" in last_answer:
                logger.info("Returning visit info based on context")
                response = self._get_visit_info()
            elif topic == "中考政策" or "政策" in last_answer:
                logger.info("Returning policy info based on context")
                response = self._get_policy_info(user_input)
            elif topic == "未央中学" and ("招生条件" in last_answer or "学费" in last_answer):
                # 只有在话题是未央中学时，才根据招生条件或学费上下文返回未央中学信息
                logger.info("Returning detailed enrollment info based on context")
                response = self._get_weiyang_enrollment_info()
            else:
                # 如果历史中有学校相关内容，返回学校信息
                if "未央" in history_text_lower or "丘北" in history_text_lower:
                    response = self._get_weiyang_enrollment_info()
                elif "昆明" in history_text_lower or "师大附中" in history_text_lower or "昆一中" in history_text_lower:
                    response = (
                        "好的！关于昆明的学校，您还想了解哪方面的信息？\n\n"
                        "• 学校对比\n"
                        "• 录取分数\n"
                        "• 学费情况\n"
                        "• 招生政策\n\n"
                        "请告诉我您的需求，我来为您详细介绍！"
                    )
                else:
                    # 通用引导
                    response = (
                        "好的！请问您想了解：\n\n"
                        "• 🏫 学校信息（如：昆明有哪些好高中）\n"
                        "• 📊 分数推荐（如：孩子中考能考650分）\n"
                        "• 📝 政策咨询（如：中考志愿怎么填）\n"
                        "• 💰 学费咨询（如：未央中学学费多少）\n\n"
                        "请告诉我您的需求，我来为您解答！"
                    )
        
        # ==================== 疑问回复 ====================
        # 检查是否为疑问回复
        elif any(word in user_input_lower for word in ["什么", "怎么", "为什么", "怎么样", "好不好", "可以吗", "能吗", "方便吗", "多少钱", "多少分"]):
            # ==================== 专门政策问题优先检测 ====================
            # 检查是否包含专门的指标到校或提前批政策问题
            is_policy_query = any(kw in user_input_lower for kw in ["指标到校", "指标生", "定向招生", "定向生", "提前批", "提前批次"])
            
            if is_policy_query:
                # 专门的政策问题，调用政策查询
                is_context_response = True
                response = self._get_policy_info(user_input)
            else:
                # 优先检查是否包含学校名称（使用original_input避免Hermes重写干扰）
                school_keywords = ["师大附中", "昆一中", "昆三中", "昆八中", "云大附中", "昆十中", "未央中学"]
                has_school = any(word in original_input.lower() for word in school_keywords)
                
                # 检查是否包含指代词（如"这些学校"、"那"、"呢"）
                has_reference = any(word in user_input_lower for word in ["这些", "那些", "这所", "那所", "呢"])
                
                if has_school:
                    # 如果包含学校名称，直接处理学校查询
                    is_context_response = True
                    response = self._get_school_info(original_input)
                elif has_reference and ("学费" in user_input_lower or "费用" in user_input_lower):
                    # 如果是指代词+学费，理解为对之前推荐学校学费的追问
                    # 先检查历史中是否有昆明学校推荐
                    if "昆明" in history_text_lower and ("推荐" in history_text_lower or "学校" in history_text_lower):
                        is_context_response = True
                        response = (
                            "关于昆明重点高中的费用情况：\n\n"
                            "【公办高中（重点高中）】\n"
                            "• 学费：约200-400元/学期（公办学校学费较低）\n"
                            "• 住宿费：约300-600元/学期\n"
                            "• 教辅费：约500-1000元/学期\n\n"
                            "【民办高中】\n"
                            "• 学费：约5000-20000元/学期不等\n"
                            "• 住宿费：约800-1500元/学期\n\n"
                            "【部分学校参考】\n"
                            "• 师大附中（公办）：学费约300元/学期\n"
                            "• 昆一中（公办）：学费约300元/学期\n"
                            "• 云大附中（民办）：学费约15000元/学期\n\n"
                            "具体费用以学校官方公布为准。需要了解其他学校的信息吗？"
                        )
                    else:
                        is_context_response = True
                        if topic == "未央中学" or "未央" in last_answer or "丘北" in last_answer:
                            response = self._get_weiyang_enrollment_info()
                        else:
                            response = self._get_policy_info(user_input)
                else:
                    is_context_response = True
                    # 优先检查是否包含分数
                    score_match = re.search(r'(\d{2,3})', original_input.lower())
                    if score_match:
                        score = int(score_match.group(1))
                        # 检查是否在合理的分数范围内（100-200分表示语数总分，400-750表示中考分数）
                        if (100 <= score <= 200) or (400 <= score <= 750):
                            logger.info(f"Detected score in question: {score}")
                            # 根据历史话题决定回复
                            if topic == "未央中学" or "未央" in last_answer or "丘北" in last_answer or "小升初" in last_answer:
                                response = self._analyze_score_for_weiyang(score)
                            else:
                                # 中考分数，进入志愿分析模式
                                response = self._get_volunteer_analysis(f"{score}分")
                    # 根据历史对话和话题回答
                    if topic == "未央中学" or "未央" in last_answer or "丘北" in last_answer:
                        if "学费" in user_input_lower or "多少钱" in user_input_lower:
                            response = self._get_weiyang_enrollment_info()
                        elif "分数" in user_input_lower or "录取" in user_input_lower:
                            response = self._get_weiyang_enrollment_info()
                        elif "怎么" in user_input_lower or "如何" in user_input_lower:
                            response = self._get_weiyang_enrollment_info()
                        elif "预约" in last_answer or "参观" in last_answer or "看校" in last_answer:
                            # 用户在确认参观时间
                            response = (
                                "😊 本周日当然可以！\n\n"
                                "【参观时间】\n"
                                "• 周日：9:00-16:00\n"
                                "• 建议上午9:00或下午14:00到达，有专门的接待老师\n\n"
                                "【温馨提示】\n"
                                "• 学校地址：丘北县锦屏镇文秀路129号\n"
                                "• 可直接到校参观，无需提前预约\n"
                                "• 如需专人讲解，可以提前联系招生热线：0876-4122666\n\n"
                                "需要我帮您联系负责老师吗？"
                        )

        # 如果不是上下文相关回复，按原有逻辑处理
        if response is None:
            # 处理学费相关查询（根据上下文决定返回内容）
            if any(word in user_input_lower for word in ["学费", "费用", "收费", "价格", "多少钱", "花多少"]):
                logger.info("Matched: 学费相关查询")
                # 根据上下文决定返回哪个学校的信息
                if topic == "未央中学" or "未央" in (last_answer or "") or "丘北" in (last_answer or ""):
                    response = self._get_weiyang_enrollment_info()
                elif topic == "昆明学校" or "昆明" in (last_answer or "") or "师大附中" in (last_answer or ""):
                    response = (
                        "关于昆明重点高中的费用情况：\n\n"
                        "【公办高中（重点高中）】\n"
                        "• 学费：约200-400元/学期（公办学校学费较低）\n"
                        "• 住宿费：约300-600元/学期\n"
                        "• 教辅费：约500-1000元/学期\n\n"
                        "【民办高中】\n"
                        "• 学费：约5000-20000元/学期不等\n"
                        "• 住宿费：约800-1500元/学期\n\n"
                        "【部分学校参考】\n"
                        "• 师大附中（公办）：学费约300元/学期\n"
                        "• 昆一中（公办）：学费约300元/学期\n"
                        "• 云大附中（民办）：学费约15000元/学期\n\n"
                        "具体费用以学校官方公布为准。"
                    )
                else:
                    # 默认返回通用学费信息
                    response = (
                        "关于云南高中的费用情况：\n\n"
                        "【公办高中】\n"
                        "• 学费：约200-400元/学期\n"
                        "• 住宿费：约300-600元/学期\n\n"
                        "【民办高中】\n"
                        "• 学费：约5000-20000元/学期不等\n"
                        "• 住宿费：约800-1500元/学期\n\n"
                        "具体费用请咨询目标学校。需要我帮您查询特定学校的费用吗？"
                    )
            
            # 处理报名咨询（优先于学校名称匹配）
            elif any(word in user_input_lower for word in ["报名", "怎么报", "如何报"]):
                logger.info("Matched: 报名咨询")
                # 根据上下文决定返回哪个学校的报名信息
                if topic == "未央中学" or "未央" in (last_answer or "") or "丘北" in (last_answer or ""):
                    response = self._get_weiyang_enrollment_info()
                else:
                    response = self._get_policy_info(user_input)
            
            # 处理预约看校（优先于学校名称匹配）
            elif any(word in user_input_lower for word in ["预约", "看校", "参观", "开放日"]):
                response = self._get_visit_info()
            
            elif any(word in user_input_lower for word in ["谢谢", "感谢", "再见", "拜拜"]):
                response = self._get_closing_message()
            
            # 处理总结请求
            elif any(word in user_input_lower for word in ["总结", "总结一下", "回顾", "回顾一下", "概括一下"]):
                response = self._get_conversation_summary(session_id)
            
            elif any(word in user_input_lower for word in ["资料", "简章", "发给我", "留微信", "联系方式"]):
                response = self._get_lead_generation_message()
            
            # 处理小升初相关查询（六年级优先）
            elif any(word in user_input_lower for word in ["六年级", "小升初", "升初中", "初一", "七年级", "小学毕业"]):
                response = self._get_primary_to_middle_info()
            
            # 处理分数推荐学校查询
            elif any(word in user_input_lower for word in ["分", "分数", "多少分"]) and ("推荐" in user_input_lower or "上" in user_input_lower or "能上" in user_input_lower):
                response = self._get_school_recommendation_by_score(original_input)
            
            # 处理备考建议查询（优先于政策）
            elif any(word in user_input_lower for word in ["备考", "复习", "怎么学", "怎么复习", "学习计划", "提分", "冲刺"]):
                response = self._get_study_plan(user_input)
            
            # 处理政策相关查询
            elif any(word in user_input_lower for word in ["政策", "中考", "录取", "志愿", "填报"]):
                response = self._get_policy_info(user_input)
            
            # 处理学习计划相关查询（优先于学校名称匹配）
            else:
                learning_keywords = ["学习", "计划", "辅导", "补习", "复习", "备考", 
                                    "物理", "化学", "语文", "数学", "英语", "生物",
                                    "历史", "地理", "政治", "道法", "科目", "刷题",
                                    "做题", "知识点", "考点", "难点", "错题", "练习"]
                if any(word in user_input_lower for word in learning_keywords):
                    response = self._get_learning_plan_info()
                
                # 处理学校相关查询
                else:
                    school_keywords = ["学校", "高中", "中学", "一中", "二中", "三中", "四中", "五中", "六中", "七中", "八中", "九中", "十中",
                                      "实验", "师范", "附中", "附小", "小学", "职中", "职高", "中专", "学院", "大学", "未央"]
                    if any(word in user_input_lower for word in school_keywords):
                        response = self._get_school_info(original_input)
                    
                    # 处理地区信息（回答"在哪个城市"时）
                    elif any(word in user_input_lower for word in ["丘北", "文山", "砚山", "广南", "富宁", "麻栗坡", "西畴", "马关"]):
                        response = self._get_qububei_info()
                    
                    # 默认返回服务介绍
                    else:
                        response = self._get_service_introduction()
        
        # 保存会话状态到缓存（包含多轮对话历史）
        # 如果有session_id，保存会话状态
        if session_id:
            try:
                from app.core.cache import session_cache_manager

                existing_data = session_cache_manager.get_session(session_id)
                conversation_history = []
                topic = ""

                if existing_data:
                    conversation_history = existing_data.get('conversation_history', [])
                    topic = existing_data.get('topic', '')

                conversation_history.append({
                    'question': user_input,
                    'answer': response,
                    'timestamp': time.time()
                })
                
                # 限制最大历史记录为5轮（优化上下文窗口大小）
                max_history_length = 5
                if len(conversation_history) > max_history_length:
                    conversation_history = conversation_history[-max_history_length:]
                
                # 检测当前话题并更新话题历史
                current_topic = self._detect_topic(conversation_history)
                
                # 更新话题历史记录（智能管理）
                topic_history = existing_data.get('topic_history', []) if existing_data else []
                if current_topic and current_topic != "其他":
                    # 智能话题管理：
                    # 1. 如果话题历史为空，直接添加
                    # 2. 如果当前话题与最后一个话题不同，添加新话题
                    # 3. 如果话题历史过长（超过5个），移除最旧的话题
                    # 4. 如果用户明确切换话题，保留最近5个话题以便返回
                    if not topic_history:
                        topic_history = [current_topic]
                    elif topic_history[-1] != current_topic:
                        topic_history.append(current_topic)
                        # 限制话题历史为5个（允许更多话题切换）
                        if len(topic_history) > 5:
                            topic_history = topic_history[-5:]
                        logger.info(f"话题切换: {topic_history[-2]} -> {current_topic}")
                
                # 构建完整的会话数据
                session_data = {
                    'last_question': user_input,
                    'last_answer': response,
                    'conversation_history': conversation_history,
                    'topic': current_topic,
                    'topic_history': topic_history,  # 添加话题历史
                    'timestamp': time.time()
                }
                
                session_cache_manager.save_session(session_id, session_data, ttl=7200)
                logger.info(f"Saved session {session_id} to cache with {len(conversation_history)} history items")
            except Exception as e:
                logger.error(f"Failed to save session to cache: {e}")
        
        # 在回答后添加智能跟进问题（除了否定回复和结束语）
        # add_follow_up 已经在方法开头初始化，并且可能在否定回复处理中设置为False
        # 这里只需要检查响应内容是否包含否定短语
        negative_phrases = ["随时再来咨询", "再见", "谢谢", "不需要", "不用了", "以后有需要"]
        response_stripped = response.strip()
        for phrase in negative_phrases:
            if phrase in response_stripped:
                add_follow_up = False
                break
        
        # 添加智能跟进问题
        if add_follow_up and session_id:
            try:
                from app.core.cache import session_cache_manager
                hermes_followup = None
                if hermes_insight:
                    should_ask = hermes_insight.get('should_ask_followup', True)
                    if should_ask:
                        hermes_followup = hermes_insight.get('followup_topic', '')
                        if hermes_followup:
                            logger.info(f"使用Hermes洞察生成跟进: {hermes_followup}")
                
                if hermes_followup and hermes_followup not in response:
                    response += f"\n\n{hermes_followup}"
                    logger.info(f"添加Hermes跟进问题: {hermes_followup}")
                else:
                    # 获取或初始化会话数据
                    existing_data = session_cache_manager.get_session(session_id)
                    if not topic or topic == "其他":
                        topic = self._detect_topic(user_input)
                    
                    # 创建临时历史用于检测阶段（包含当前对话）
                    temp_history = conversation_history.copy()
                    temp_history.append({
                        'question': user_input,
                        'answer': response
                    })
                    
                    stage = self._detect_conversation_stage(temp_history)
                    
                    # 如果有Hermes缺失信息提示，生成针对性追问
                    if hermes_insight and hermes_insight.get('missing_info'):
                        missing = hermes_insight.get('missing_info', [])
                        if missing:
                            follow_up = "请问您方便告诉我" + "、".join(missing) + "吗？这样我可以给您更精准的建议~"
                            logger.info(f"根据Hermes缺失信息生成追问: {follow_up}")
                        else:
                            follow_up = self._generate_follow_up_question(topic, stage)
                    else:
                        follow_up = self._generate_follow_up_question(topic, stage)
                    
                    # 如果没有找到特定话题的跟进问题，使用通用跟进问题
                    if not follow_up:
                        follow_up = self._generate_general_follow_up(stage)
                    
                    # 过滤无效的跟进问题
                    invalid_followups = ["了解更多信息", "请继续", "还有其他问题吗", ""]
                    if follow_up in invalid_followups:
                        follow_up = ""
                    
                    # 避免重复的跟进问题
                    if follow_up and follow_up not in response:
                        response += f"\n\n{follow_up}"
                        logger.info(f"添加跟进问题: {follow_up}")
            except Exception as e:
                logger.error(f"Failed to generate follow-up question: {e}")
        
        # 决定是否需要LLM增强
        llm_enhanced = False
        should_enhance = False

        # ==================== 专门政策问题不需要LLM增强 ====================
        # 检查是否是专门的指标到校或提前批问题，这些问题已有专业回复
        is_specialized_policy = any(kw in user_input_lower for kw in ["指标到校", "指标生", "定向招生", "定向生", "提前批", "提前批次"])

        # 触发条件1：响应是默认服务介绍
        if response == self._get_service_introduction() or "请告诉我具体想了解哪所学校" in response:
            should_enhance = True
            logger.info("触发LLM增强：默认服务介绍")

        # 触发条件2：用户问题包含复杂查询关键词
        complex_keywords = ["怎么办", "如何选择", "怎么选", "哪个好", "有什么区别", "有什么建议",
                         "能不能", "可不可以", "会不会", "好不好", "要不要", "有必要吗",
                         "分析一下", "帮我看看", "帮我分析", "推荐一下", "介绍一下"]
        if any(kw in user_input_lower for kw in complex_keywords) and not is_specialized_policy:
            should_enhance = True
            logger.info("触发LLM增强：复杂查询关键词")

        # 触发条件3：响应较短但用户问题较长或复杂
        if len(response) < 50 and len(user_input) > 15 and not is_specialized_policy:
            should_enhance = True
            logger.info("触发LLM增强：响应较短但问题复杂")

        # 触发条件4：上下文相关但规则未匹配到
        if previous_context and response == self._get_service_introduction():
            # 有上下文但返回了默认介绍，说明规则未正确匹配
            should_enhance = True
            logger.info("触发LLM增强：上下文未正确匹配")

        if should_enhance:
            logger.info("尝试使用LLM增强回复...")
            try:
                # 构建对话历史上下文
                history_context = ""
                if previous_context:
                    for item in previous_context.get('conversation_history', [])[-5:]:
                        history_context += f"用户：{item.get('question', '')}\n"
                        history_context += f"AI：{item.get('answer', '')}\n"

                # 获取当前话题
                current_topic = ""
                if previous_context:
                    current_topic = previous_context.get('topic', '')

                # 构建增强提示词
                prompt = f"""你是一个专业、亲切的云南中考择校咨询顾问。

当前话题：{current_topic}
对话历史：
{history_context}
用户最新问题：{user_input}

请给出专业的回复，要求：
1. 简洁有针对性，突出专业价值
2. 如果用户问题模糊，主动追问关键信息（分数、地区、年级等）
3. 结合对话历史，保持连贯性
4. 适当使用emoji增加可读性
5. 主动提供有用的建议和信息

回复："""

                llm_result = self.llm_service.generate_answer(prompt)
                if llm_result and "answer" in llm_result and llm_result["answer"]:
                    enhanced_response = llm_result["answer"].strip()
                    # 确保增强回复不为空
                    if enhanced_response and len(enhanced_response) > 10:
                        response = enhanced_response
                        llm_enhanced = True
                        logger.info("LLM增强回复成功")
            except Exception as e:
                logger.error(f"LLM服务调用失败: {e}")
        
        # 如果使用了LLM增强回复，需要重新保存会话状态
        if llm_enhanced and session_id:
            try:
                from app.core.cache import session_cache_manager
                existing_data = session_cache_manager.get_session(session_id)
                if existing_data:
                    conversation_history = existing_data.get('conversation_history', [])
                    if conversation_history:
                        conversation_history[-1]['answer'] = response
                    session_cache_manager.save_session(session_id, existing_data, ttl=7200)
                    logger.info("更新会话状态（LLM增强后）")
            except Exception as e:
                logger.error(f"Failed to update session after LLM enhancement: {e}")
        
        # ==================== 情感分析驱动的回复调整 ====================
        response = self._apply_emotion_tone(response, hermes_emotion, user_input_lower)
        
        # ==================== 通知Hermes记录系统回复 ====================
        if session_id:
            try:
                import requests
                threading.Thread(
                    target=lambda: requests.post(
                        "http://localhost:8888/v1/record-answer",
                        json={"data": {"answer": response, "session_id": session_id}},
                        timeout=2
                    )
                ).start()
            except:
                pass
        
        # ==================== Hermes上下文感知个性化回复增强 ====================
        if not llm_enhanced and should_enhance:
            hermes_enhanced = self._get_hermes_enhanced_response(
                session_id, user_input, response, context
            )
            if hermes_enhanced and hermes_enhanced != response:
                response = hermes_enhanced
                logger.info("Hermes个性化增强回复成功")
        
        # ==================== 响应清理：去除噪声文本 ====================
        noise_patterns = ["了解更多信息", "请继续", "还有其他问题吗", "还有什么可以帮您"]
        for noise in noise_patterns:
            response = response.replace(f"\n\n{noise}", "")
            response = response.replace(f"\n{noise}", "")
            response = response.strip()
        
        # 返回响应时，同时返回session_id（用于前端保存）
        return response
    
    def _apply_emotion_tone(self, response: str, hermes_emotion: dict, user_input: str = "") -> str:
        """根据用户情感调整回复语气"""
        if not hermes_emotion or not response:
            return response
        
        closing_phrases = ["再见", "随时再来", "随时可以再来", "以后有需要", "拜拜", "下次见"]
        is_closing = any(phrase in response for phrase in closing_phrases)
        if is_closing:
            return response
        
        emotion = hermes_emotion.get('emotion', '中性')
        sentiment = hermes_emotion.get('sentiment', '其他')
        needs_support = hermes_emotion.get('needs_support', False)
        confidence = hermes_emotion.get('confidence', 0.5)
        urgency = hermes_emotion.get('urgency', '中')
        
        if confidence < 0.3:
            return response
        
        logger.info(f"情感调整: emotion={emotion}, sentiment={sentiment}, urgency={urgency}, needs_support={needs_support}")
        
        prefix = ""
        suffix = ""
        
        if emotion == "焦虑":
            prefix = "我能理解您的担心，让我帮您分析一下。\n\n"
            if urgency == "高":
                suffix = "\n\n😊 放轻松，每个孩子都有自己的节奏，我们一起找到最适合的方案。如有紧急问题，也可以拨打我们的咨询热线。"
            else:
                suffix = "\n\n😊 放轻松，每个孩子都有自己的节奏，我们一起找到最适合的方案。"
        elif emotion == "困惑":
            prefix = "我明白您的困惑，让我为您详细解释一下。\n\n"
            suffix = "\n\n💡 如果还有不清楚的地方，可以继续问我，我会耐心为您解答。"
        elif emotion == "消极":
            prefix = "您别着急，我来帮您想想办法。\n\n"
            suffix = "\n\n💪 只要找到合适的方向，一切都会好起来的！"
        elif emotion == "积极":
            suffix = "\n\n✨ 您的态度非常积极，这对孩子的升学很有帮助！"
        elif emotion == "兴奋":
            suffix = "\n\n🎉 很高兴听到这个好消息！继续保持这份热情，孩子一定会有好的收获！"
        elif emotion == "期待":
            if urgency == "高":
                suffix = "\n\n🌟 我理解您的急切心情，我会尽快为您提供详细信息！"
            else:
                suffix = "\n\n🌟 祝孩子取得理想的成绩，有什么问题随时问我！"
        elif emotion == "中性":
            if needs_support:
                suffix = "\n\n🤝 有任何问题都可以随时找我，我会一直在的。"
        elif sentiment == "疑惑":
            suffix = "\n\n💡 如果还有不清楚的地方，可以继续问我，我会详细为您解答。"
        elif sentiment == "不满":
            prefix = "感谢您的反馈，我会认真对待。\n\n"
            suffix = "\n\n🙏 非常抱歉给您带来不便，我会尽力帮您解决问题。"
        elif needs_support and not suffix:
            suffix = "\n\n🤝 有任何问题都可以随时找我，我会一直在的。"
        
        return prefix + response + suffix
    
    def _get_hermes_enhanced_response(self, session_id: str, user_input: str, 
                                       base_response: str, context: dict) -> str:
        """通过Hermes生成上下文感知的个性化回复"""
        if not session_id:
            return base_response
        
        try:
            import requests
            payload = {
                "data": {
                    "input": user_input,
                    "base_response": base_response,
                    "session_id": session_id,
                    "context": context
                }
            }
            response = requests.post(
                "http://localhost:8888/v1/contextual-response",
                json=payload,
                timeout=8
            )
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data', {}).get('response'):
                    enhanced = result['data']['response']
                    if enhanced and len(enhanced) > 10:
                        return enhanced
        except Exception as e:
            logger.error(f"Hermes个性化增强失败: {e}")
        
        return base_response
    
    def _get_9th_grade_info(self) -> str:
        """获取九年级学生的高中部招生信息"""
        return (
            "🎓 针对9年级学生 - 丘北未央中学高中部招生信息\n\n"
            "【招生对象】\n"
            "2026年初中毕业生\n\n"
            "【招生计划】\n"
            "• 鹏程班：50人（顶尖班型，冲刺双一流）\n"
            "• 英才班：150人（重点班型）\n"
            "• 实验班：400人\n\n"
            "【录取方式】\n"
            "• 主要依据：中考裸分\n"
            "• 参考：综合素质评价\n\n"
            "【学费标准】（按中考裸分）\n"
            "• 620分以上：公费（学费0元+住宿费0元）\n"
            "• 600-619分：学费800元+住宿费600元\n"
            "• 570-599分：学费2000元+住宿费600元\n"
            "• 540-569分：学费2500元+住宿费600元\n"
            "• 510-539分：学费3000元+住宿费600元\n"
            "• 480-509分：学费3500元+住宿费600元\n"
            "• 450-479分：学费4000元+住宿费600元\n"
            "• 420-449分：学费5000元+住宿费600元\n\n"
            "【奖学金政策】\n"
            "• 中考全州第1名：奖励30万元\n"
            "• 中考全州第2名：奖励25万元\n"
            "• 中考全州第3名：奖励20万元\n"
            "• 中考全州4-100名：奖励5-15万元\n\n"
            "【报名咨询】\n"
            "招生热线：0876-4122666\n"
            "地址：丘北县锦屏镇文秀路129号"
        )
    
    def _get_7th_grade_info(self) -> str:
        """获取七年级学生的初中部招生信息"""
        return (
            "🎓 针对7年级学生 - 丘北未央中学初中部信息\n\n"
            "【在读学生服务】\n"
            "如果你目前在未央中学读7年级，以下是相关信息：\n\n"
            "【教学安排】\n"
            "• 课程设置：语文、数学、英语、物理、生物、道德与法治、历史、地理\n"
            "• 特色课程：科技创新、艺术素养、体育竞技\n\n"
            "【升学规划】\n"
            "• 本校直升：未央中学初中部学生可优先升入本校高中部\n"
            "• 升学指导：学校提供专业的中考备考指导\n\n"
            "【联系我们】\n"
            "招生热线：0876-4122666\n"
            "地址：丘北县锦屏镇文秀路129号"
        )
    
    def _detect_topic(self, text_or_history) -> str:
        """根据文本或对话历史检测当前话题（只分析用户问题）"""
        if isinstance(text_or_history, str):
            text_lower = text_or_history.lower()
        else:
            # 只分析用户的问题，不分析系统的回答
            all_text = ""
            for item in text_or_history:
                if 'question' in item:
                    all_text += item['question'] + " "
            text_lower = all_text.lower()

        topic_keywords = [
            ("未央中学", ["未央", "丘北"]),
            ("昆明学校", ["昆明", "昆一中", "昆三中", "昆八中", "师大附中", "云大附中", "附中", "一中", "二中", "三中"]),
            ("分数推荐", ["分推荐", "分数推荐", "多少分能上", "推荐学校"]),
            ("报名咨询", ["报名", "招生"]),
            ("学费查询", ["学费", "费用", "收费", "多少钱"]),
            ("预约看校", ["预约", "看校", "参观"]),
            ("中考政策", ["中考", "政策", "录取", "志愿"]),
            ("小升初", ["小升初", "六年级", "初一"]),
            ("学习计划", ["学习", "计划", "辅导", "补习"]),
            ("学校对比", ["对比", "哪个好", "推荐"]),
        ]

        for topic_name, keywords in topic_keywords:
            if any(keyword in text_lower for keyword in keywords):
                return topic_name

        return "其他"
    
    def _detect_conversation_stage(self, conversation_history: list) -> str:
        """检测对话阶段"""
        if not conversation_history:
            return "greeting"
        
        # 检查是否有结束语
        last_item = conversation_history[-1]
        last_question = last_item.get('question', '').lower()
        last_answer = last_item.get('answer', '').lower()
        
        if any(word in last_question for word in ["谢谢", "再见", "拜拜", "结束", "完成"]):
            return "closing"
        
        if any(word in last_answer for word in ["以后有需要", "随时咨询"]):
            return "closed"
        
        # 根据对话轮数判断
        num_rounds = len(conversation_history)
        
        if num_rounds == 1:
            return "intro"  # 介绍阶段
        elif num_rounds <= 3:
            return "exploration"  # 探索阶段
        elif num_rounds <= 5:
            return "decision"  # 决策阶段
        else:
            return "deepening"  # 深入交流阶段
    
    def _generate_follow_up_question(self, topic: str, stage: str) -> str:
        """根据话题和对话阶段生成跟进问题"""
        follow_up_map = {
            "未央中学": {
                "intro": "您是想了解招生条件、学费标准，还是想预约看校呢？",
                "exploration": "需要我帮您预约看校时间吗？我们可以安排专人接待您和孩子参观校园 😊",
                "decision": "请问孩子现在几年级？不同年级有不同的招生政策和准备建议哦~",
                "deepening": "还有其他想了解的吗？比如奖学金政策、校园环境或升学成果？"
            },
            "报名咨询": {
                "intro": "您是想了解报名流程、所需材料，还是想咨询录取概率呢？",
                "exploration": "我可以帮您梳理报名流程，让准备更充分～",
                "decision": "请问方便留下联系方式吗？我们的招生老师可以给您提供一对一指导 📞",
                "deepening": "报名方面还有其他疑问吗？我来帮您解答～"
            },
            "学费查询": {
                "intro": "您想了解初中部还是高中部的费用呢？不同年级收费标准有差异哦~",
                "exploration": "需要我帮您计算一下孩子升学的年度费用预算吗？",
                "decision": "其实学校有丰富的奖学金政策，成绩优秀的孩子可以省不少学费呢～",
                "deepening": "费用方面还有其他想了解的吗？比如住宿费、教辅费等～"
            },
            "中考政策": {
                "intro": "您想了解昆明市还是文山州的中考政策呢？不同地区略有差异~",
                "exploration": "我可以帮您分析今年的中考志愿填报策略，提高录取概率～",
                "decision": "请问孩子目前的成绩在什么水平呢？我来帮您匹配合适的学校 📊",
                "deepening": "政策方面还有其他疑问吗？比如定向生、指标到校等～"
            },
            "昆明学校": {
                "intro": "您想了解昆明哪所学校呢？每个学校都有自己的特色～",
                "exploration": "需要我帮您对比几所学校吗？这样更容易找到最适合孩子的～",
                "decision": "请问孩子中考预估能考多少分呢？我来帮您分析录取可能性 🎯",
                "deepening": "还有其他学校想了解吗？比如云大附中、昆八中等～"
            },
            "分数推荐": {
                "intro": "根据分数推荐学校需要了解孩子的年级和所在地区～",
                "exploration": "我可以帮您分析志愿填报策略，冲刺更好的学校～",
                "decision": "请问孩子有偏科吗？可以根据单科成绩给出更精准的推荐～",
                "deepening": "还有其他因素需要考虑吗？比如住宿要求、是否有特长生身份～"
            },
            "学习计划": {
                "intro": "想了解哪科的学习方法呢？不同科目复习策略不一样～",
                "exploration": "我可以帮您制定一个中考冲刺计划，提高复习效率～",
                "decision": "请问孩子目前哪科最薄弱呢？我来重点帮您分析～",
                "deepening": "还有其他学习方面的问题吗？比如时间管理、压力缓解等～"
            }
        }

        return follow_up_map.get(topic, {}).get(stage, "")
    
    def _generate_general_follow_up(self, stage: str) -> str:
        """生成通用跟进问题（当没有特定话题的跟进问题时使用）"""
        general_follow_up = {
            "greeting": "请问有什么我可以帮助您的吗？比如了解学校信息、中考政策或者志愿填报建议～",
            "intro": "请问您主要想了解哪方面的信息呢？学校介绍、录取分数线还是志愿填报建议？",
            "exploration": "需要我帮您深入分析一下吗？比如对比几所学校或者制定备考计划～",
            "decision": "请问孩子目前的成绩情况怎么样？我可以帮您做更精准的分析和推荐 📊",
            "deepening": "还有其他想了解的吗？随时可以问我～",
            "closing": "",
            "closed": ""
        }
        return general_follow_up.get(stage, "")
    
    def _resolve_pronoun(self, user_input: str, conversation_history: list, last_answer: str, current_topic: str) -> str:
        """解析指代词指代的对象"""
        # 学校名称列表
        school_keywords = ["未央中学", "文山州一中", "昆一中", "昆三中", "昆八中", "师大附中", "云大附中", "昆十中"]
        
        # 检查是否为"那个"，需要特殊处理（通常指上一个推荐的选项）
        is_that = "那个" in user_input
        
        # 首先从最近的回答中查找可能的实体
        recent_text = last_answer
        
        # 然后从对话历史中查找（按时间倒序）
        for item in reversed(conversation_history):
            if 'answer' in item:
                recent_text += " " + item['answer']
            if 'question' in item:
                recent_text += " " + item['question']
        
        # 查找最近提到的学校
        mentioned_schools = []
        for school in school_keywords:
            if school in recent_text:
                mentioned_schools.append(school)
        
        # 如果是"那个"，返回第二个提到的学校（第一个是当前话题的学校）
        if is_that and len(mentioned_schools) >= 2:
            return mentioned_schools[-1]  # 返回最后提到的学校
        elif mentioned_schools:
            return mentioned_schools[-1]  # 返回最后提到的学校
        
        # 检查是否有推荐相关的历史
        has_recommendation = any(
            '推荐' in item.get('question', '') or '推荐' in item.get('answer', '')
            for item in conversation_history[-3:]  # 检查最近3轮
        )
        
        if has_recommendation and is_that:
            # 如果有推荐历史且用户问"那个"，返回当前话题或默认推荐
            if current_topic and current_topic != "其他":
                topic_entities = {
                    "未央中学": "未央中学",
                    "昆明学校": "昆一中",
                    "中考政策": "中考政策",
                    "分数推荐": "分数推荐",
                    "学习计划": "学习计划",
                    "费用咨询": "学费"
                }
                return topic_entities.get(current_topic, "")
        
        # 如果没有找到具体学校，返回话题相关的实体
        topic_entities = {
            "未央中学": "未央中学",
            "昆明学校": "昆明重点高中",
            "中考政策": "中考政策",
            "分数推荐": "分数推荐",
            "学习计划": "学习计划",
            "费用咨询": "学费"
        }
        
        if current_topic in topic_entities:
            return topic_entities[current_topic]
        
        # 如果还是找不到，返回空字符串
        return ""
    
    def _get_school_info(self, user_input: str) -> str:
        """获取学校信息"""
        user_lower = user_input.lower()

        # 检测是否为学校对比请求
        comparison_keywords = ["对比", "比较", "哪个好", "差异", "区别"]
        if any(keyword in user_lower for keyword in comparison_keywords):
            # 尝试提取两所学校名称
            schools = []
            school_patterns = ["师大附中", "昆一中", "昆三中", "昆八中", "云大附中", "未央中学", "昆十中",
                              "昆十四中", "大理一中", "曲靖一中",
                              "云南师范大学附属中学", "昆明第一中学", "昆明第三中学", "昆明第八中学",
                              "云南大学附属中学", "昆明第十中学", "昆明第十四中学",
                              "大理白族自治州第一中学", "曲靖市第一中学", "丘北未央"]
            for pattern in school_patterns:
                if pattern in user_input:
                    schools.append(pattern)

            if len(schools) >= 2:
                return self._compare_schools(schools[0], schools[1])
            elif len(schools) == 1:
                # 只有一个学校，尝试从历史上下文中获取另一所
                return (
                    f"您想了解 {schools[0]} 与哪所学校对比呢？\n\n"
                    "请告诉我另一所学校名称，比如：\n"
                    "• 昆一中\n"
                    "• 昆三中\n"
                    "• 昆十中\n"
                    "• 云大附中\n"
                    "• 大理一中\n"
                    "• 曲靖一中\n\n"
                    "我可以为您进行详细的对比分析！"
                )

        # 丘北未央中学
        if "未央" in user_lower or "丘北未央" in user_lower:
            return self._get_weiyang_info()
        
        # 云南师范大学附属中学（师大附中）
        if "师大附中" in user_lower or "云南师范大学附属中学" in user_lower:
            return (
                "🏫 云南师范大学附属中学（师大附中）\n\n"
                "【学校简介】\n"
                "云南师范大学附属中学是云南省一级一等高级中学，云南省教育厅直属重点中学，"
                "创建于1940年，是云南省乃至全国知名的优质高中。\n\n"
                "【办学优势】\n"
                "• 全省顶尖：云南省高中教育的标杆，清北录取人数常年全省第一\n"
                "• 师资雄厚：特级教师、高级教师占比高，教学水平精湛\n"
                "• 成绩优异：高考一本率常年95%以上，600分以上人数占比高\n"
                "• 竞赛突出：数学、物理、化学等学科竞赛成绩全省领先\n"
                "• 校风优良：治学严谨，注重学生全面发展\n\n"
                "【校区分布】\n"
                "• 校本部：昆明市高新区洪源路36号\n"
                "• 呈贡校区：昆明市呈贡区（新校区）\n\n"
                "【招生信息】\n"
                "• 录取线：约680-690分（昆明主城区）\n"
                "• 招生范围：面向全省招生\n"
                "• 联系方式：0871-68215819\n\n"
                "【评价】\n"
                "如果您的孩子成绩优秀（680分以上），师大附中是非常理想的选择！\n"
                "需要了解更多关于师大附中的信息吗？"
            )
        
        # 昆明第一中学（昆一中）
        if ("昆明" in user_lower or "昆" in user_lower) and ("一中" in user_lower or "第一中学" in user_lower):
            # 检查是否询问分校
            if "分校" in user_lower or "校区" in user_lower:
                return (
                    "🏫 昆明市第一中学 - 校区分布\n\n"
                    "【本部校区】\n"
                    "• 地址：昆明市五华区西昌路233号\n"
                    "• 特色：百年名校本部，师资力量最强\n\n"
                    "【分校/合作校区】\n"
                    "• 昆一中度假区分校（滇池度假区）\n"
                    "• 昆一中经开校区（经济技术开发区）\n"
                    "• 昆一中晋宁学校（晋宁区）\n"
                    "• 昆一中西山学校（西山区）\n\n"
                    "【说明】\n"
                    "分校与本部共享教学资源和管理模式，但办学独立。\n"
                    "需要了解具体分校的招生信息吗？"
                )
            # 询问特色/怎么样
            elif "特色" in user_lower or "怎么样" in user_lower or "如何" in user_lower:
                return (
                    "🏫 昆明市第一中学 - 办学特色\n\n"
                    "【百年底蕴】\n"
                    "• 创办于1905年，云南历史最悠久的中学之一\n"
                    "• 云南省教育厅直属重点中学\n\n"
                    "【办学特色】\n"
                    "• 治学严谨：以\"求实、创新、勤奋、守纪\"为校训\n"
                    "• 师资雄厚：特级教师20余人，高级教师占比超60%\n"
                    "• 成绩优异：高考一本率常年90%以上\n"
                    "• 学科竞赛：数学、物理、化学竞赛成绩突出\n"
                    "• 校园文化：百年校庆、艺术节、体育节等活动丰富\n\n"
                    "【地址】昆明市五华区西昌路233号\n"
                    "【电话】0871-65324879"
                )
            # 通用昆一中信息
            return (
                "🏫 昆明市第一中学\n\n"
                "【学校简介】\n"
                "昆明市第一中学是云南省一级一等高级中学，云南省教育厅直属重点中学，"
                "创办于1905年，是云南历史最悠久的中学之一。\n\n"
                "【办学优势】\n"
                "• 百年名校：历史悠久，底蕴深厚\n"
                "• 师资雄厚：特级教师、高级教师占比高\n"
                "• 成绩优异：高考一本率常年保持在90%以上\n"
                "• 素质教育：注重学生全面发展\n\n"
                "【学校地址】昆明市五华区西昌路233号\n"
                "【联系电话】0871-65324879\n\n"
                "需要了解更多关于昆明一中的招生信息或校园生活吗？"
            )
        
        # 昆明第八中学（昆八中）
        if ("昆明" in user_lower or "昆" in user_lower) and ("八中" in user_lower or "第八中学" in user_lower):
            return (
                "🏫 昆明市第八中学\n\n"
                "【学校简介】\n"
                "昆明市第八中学是云南省一级一等高级中学，创建于1952年，"
                "是昆明市教育局直属的优质中学。\n\n"
                "【办学特色】\n"
                "• 教学质量高：高考一本率稳居昆明市前列\n"
                "• 德育工作突出：\"养正教育\"办学理念\n"
                "• 艺术教育特色：舞蹈、合唱、器乐等艺术团体成绩优异\n"
                "• 科技创新：机器人、航模等科技活动成果丰硕\n\n"
                "【校区分布】\n"
                "• 龙泉校区（本部）：昆明市五华区龙泉路628号\n"
                "• 西坝校区：昆明市西山区西坝路\n\n"
                "【联系电话】0871-65155666\n\n"
                "需要了解更多关于昆八中的招生信息吗？"
            )
        
        # 云南大学附属中学（云大附中）
        if "云大附中" in user_lower or "云南大学附属中学" in user_lower:
            return (
                "🏫 云南大学附属中学（云大附中）\n\n"
                "【学校简介】\n"
                "云南大学附属中学是云南省一级一等完全中学，创建于1927年，"
                "是云南省首批示范学校，依托云南大学优质资源办学。\n\n"
                "【办学优势】\n"
                "• 名校背景：依托云南大学，学术氛围浓厚\n"
                "• 师资优秀：高学历教师比例高，教学经验丰富\n"
                "• 成绩突出：中考、高考成绩稳居省市前列\n"
                "• 特色鲜明：注重科技创新和综合素质培养\n\n"
                "【校区分布】\n"
                "• 一二一校区：昆明市五华区一二一大街\n"
                "• 星耀校区：昆明市官渡区星耀路\n"
                "• 呈贡校区：昆明市呈贡区\n\n"
                "【联系电话】0871-65033859\n\n"
                "需要了解更多关于云大附中的招生信息或校园生活吗？"
            )
        
        # 昆明第三中学（昆三中）
        if ("昆明" in user_lower or "昆" in user_lower) and ("三中" in user_lower or "第三中学" in user_lower):
            return (
                "🏫 昆明市第三中学（昆三中）\n\n"
                "【学校简介】\n"
                "昆明市第三中学是云南省一级一等高级中学，创建于1907年，"
                "是昆明市教育局直属重点中学，以科技教育见长。\n\n"
                "【办学特色】\n"
                "• 科技教育：机器人、科技创新成果突出，多次获得国家级奖项\n"
                "• 教学质量：高考一本率常年保持在85%以上\n"
                "• 师资力量：特级教师、高级教师占比高\n"
                "• 校园文化：注重学生创新能力和实践能力培养\n\n"
                "【校区分布】\n"
                "• 呈贡校区（本部）：昆明市呈贡区惠通路\n"
                "• 滇池星城校区：昆明市西山区\n"
                "• 经开校区：昆明市经济技术开发区\n\n"
                "【联系电话】0871-67477999\n\n"
                "需要了解更多关于昆三中的招生信息吗？"
            )
        
        # 昆明第十中学（昆十中）
        if ("昆明" in user_lower or "昆" in user_lower) and ("十中" in user_lower or "第十中学" in user_lower):
            return (
                "🏫 昆明市第十中学（昆十中）\n\n"
                "【学校简介】\n"
                "昆明市第十中学是云南省一级一等高级中学，创建于1920年，"
                "是昆明市教育局直属优质中学。\n\n"
                "【办学特色】\n"
                "• 教学质量：高考一本率稳定在80%以上\n"
                "• 体育特色：足球、篮球等体育项目成绩优异\n"
                "• 艺术教育：美术、音乐等艺术特色鲜明\n"
                "• 国际交流：与多国学校建立交流合作关系\n\n"
                "【校区分布】\n"
                "• 白塔校区（本部）：昆明市盘龙区白塔路\n"
                "• 求实校区：昆明市盘龙区求实路\n\n"
                "【联系电话】0871-63125606\n\n"
                "需要了解更多关于昆十中的招生信息吗？"
            )
        
        # 大理第一中学（大理一中）
        if "大理" in user_lower and ("一中" in user_lower or "第一中学" in user_lower):
            return (
                "🏫 大理白族自治州第一中学（大理一中）\n\n"
                "【学校简介】\n"
                "大理白族自治州第一中学是云南省一级一等高级中学，创建于1877年，"
                "是云南省历史最悠久的中学之一，滇西地区顶尖高中。\n\n"
                "【办学优势】\n"
                "• 百年名校：历史悠久，文化底蕴深厚\n"
                "• 教学质量：高考一本率常年保持在85%以上，大理州第一\n"
                "• 师资力量：特级教师、高级教师占比高\n"
                "• 白族文化：传承白族优秀传统文化\n\n"
                "【学校地址】大理市大理镇\n"
                "【联系电话】0872-2125016\n\n"
                "需要了解更多关于大理一中的招生信息吗？"
            )
        
        # 曲靖第一中学（曲靖一中）
        if "曲靖" in user_lower and ("一中" in user_lower or "第一中学" in user_lower):
            return (
                "🏫 曲靖市第一中学（曲靖一中）\n\n"
                "【学校简介】\n"
                "曲靖市第一中学是云南省一级一等高级中学，创建于1913年，"
                "是曲靖市教育局直属重点中学，滇东北地区顶尖高中。\n\n"
                "【办学优势】\n"
                "• 教学质量：高考一本率常年保持在90%以上，曲靖市第一\n"
                "• 师资力量：特级教师、高级教师占比高，教学经验丰富\n"
                "• 学科竞赛：数学、物理、化学竞赛成绩突出\n"
                "• 校园文化：注重学生综合素质培养\n\n"
                "【学校地址】曲靖市麒麟区\n"
                "【联系电话】0874-3122888\n\n"
                "需要了解更多关于曲靖一中的招生信息吗？"
            )
        
        # 玉溪第一中学（玉溪一中）
        if "玉溪" in user_lower and ("一中" in user_lower or "第一中学" in user_lower):
            return (
                "🏫 玉溪市第一中学（玉溪一中）\n\n"
                "【学校简介】\n"
                "玉溪市第一中学是云南省一级一等高级中学，创建于1925年，"
                "是玉溪市教育局直属重点中学。\n\n"
                "【办学优势】\n"
                "• 教学质量：高考一本率常年保持在80%以上，玉溪市第一\n"
                "• 师资力量：特级教师、高级教师占比高\n"
                "• 校园文化：注重学生全面发展\n"
                "• 环境优美：校园环境优美，设施完善\n\n"
                "【学校地址】玉溪市红塔区\n"
                "【联系电话】0877-2023608\n\n"
                "需要了解更多关于玉溪一中的招生信息吗？"
            )
        
        # 使用统一数据访问层获取学校信息
        if UNIFIED_DAL_AVAILABLE:
            try:
                dal = get_unified_data_access()
                
                # 搜索学校
                results = dal.search_schools(user_input)
                if results:
                    response = "🏫 为您找到以下学校：\n\n"
                    for i, school in enumerate(results[:3], 1):
                        school_name = school.get('name', '')
                        school_type = school.get('type_name', '')
                        school_level = school.get('level', '')
                        school_address = school.get('address', '')
                        min_score = school.get('min_score', '')
                        description = school.get('description', '')
                        
                        response += f"{i}. {school_name}\n"
                        response += f"   • 类型：{school_type} {school_level}\n"
                        response += f"   • 地址：{school_address}\n"
                        response += f"   • 分数线：{min_score}分\n"
                        response += f"   • 简介：{description}\n\n"
                    response += "需要了解哪所学校的详细信息？"
                    return response
            except Exception as e:
                logger.error(f"Failed to use unified data access layer: {e}")
        
        # 其他学校通用回复
        return (
            f"📚 关于您询问的学校信息\n\n"
            "我可以为您提供云南省内各所中学的详细信息，包括：\n"
            "• 学校概况和办学特色\n"
            "• 师资力量和教学质量\n"
            "• 历年录取分数线\n"
            "• 校园环境和设施\n"
            "• 招生政策和报名方式\n\n"
            "请告诉我具体想了解哪所学校，或者您所在的城市，我可以为您推荐合适的学校！"
        )
    
    def _get_school_recommendation_by_score(self, user_input: str, user_profile: dict = None) -> str:
        """根据分数推荐学校（支持个性化推荐）"""
        user_lower = user_input.lower()
        
        # 提取分数（匹配数字+分的模式）
        import re
        score_match = re.search(r'(\d{2,3})分', user_input)
        if score_match:
            score = int(score_match.group(1))
        else:
            score_match = re.search(r'(\d{2,3})', user_input)
            score = int(score_match.group(1)) if score_match else None
        
        # 验证分数是否在合理范围内
        if score is not None and not ((100 <= score <= 200) or (400 <= score <= 750)):
            score = None
        
        # 从用户画像或输入中获取地区信息
        city = "昆明"
        if user_profile and user_profile.get("location"):
            city = user_profile["location"]
        elif "昆明" in user_lower:
            city = "昆明"
        elif any(loc in user_lower for loc in ["文山", "丘北", "红河", "曲靖", "玉溪", "大理"]):
            city = user_lower
        
        if score is None:
            return "请告诉我具体的分数，我可以为您推荐合适的学校！"
        
        # 获取用户关注点
        concerns = user_profile.get("concerns", []) if user_profile else []
        
        # 个性化推荐理由生成
        def get_personalized_reason(school_name, school_info):
            """根据用户关注点生成个性化推荐理由"""
            reason = ""
            if "升学率" in concerns:
                reason += f"，该校一本率较高，升学表现优秀"
            if "费用" in concerns:
                reason += f"，该校收费合理"
            if "管理" in concerns:
                reason += f"，该校管理严格，校风良好"
            if "住宿" in concerns:
                reason += f"，该校住宿条件良好"
            if "师资" in concerns:
                reason += f"，该校师资力量雄厚"
            return reason
        
        # 昆明地区分数推荐
        if city == "昆明" or "昆明" in str(city):
            if score >= 680:
                reasons = []
                if concerns:
                    reasons.append("根据您关注的重点，为您推荐以下学校：")
                return (
                    f"🏆 {score}分 - 昆明顶尖高中推荐\n\n"
                    f"{''.join(reasons)}\n"
                    "【第一梯队（冲刺）】\n"
                    f"• 云南师范大学附属中学（师大附中）\n"
                    f"  - 录取线：约680-690分\n"
                    f"  - 特色：云南省顶尖高中，清北摇篮{get_personalized_reason('师大附中', '')}\n\n"
                    f"• 昆明市第一中学（昆一中）\n"
                    f"  - 录取线：约675-685分\n"
                    f"  - 特色：百年名校，一本率90%+{get_personalized_reason('昆一中', '')}\n\n"
                    f"• 昆明市第三中学（昆三中）\n"
                    f"  - 录取线：约670-680分\n"
                    f"  - 特色：呈贡校区环境优美，成绩优异{get_personalized_reason('昆三中', '')}\n\n"
                    "【建议】\n"
                    "您的分数非常优秀，可以冲刺云南省最好的高中！\n"
                    "建议第一志愿填报师大附中或昆一中。"
                )
            elif score >= 650:
                return (
                    f"🌟 {score}分 - 昆明优质高中推荐\n\n"
                    "【推荐学校】\n"
                    f"• 昆明市第八中学（昆八中）\n"
                    f"  - 录取线：约650-660分\n"
                    f"  - 特色：教学质量高，一本率85%+{get_personalized_reason('昆八中', '')}\n\n"
                    f"• 云南大学附属中学（云大附中）\n"
                    f"  - 录取线：约645-655分\n"
                    f"  - 特色：依托云大，学术氛围浓厚{get_personalized_reason('云大附中', '')}\n\n"
                    f"• 昆明市第十中学（昆十中）\n"
                    f"  - 录取线：约640-650分\n"
                    f"  - 特色：求实校区成绩突出{get_personalized_reason('昆十中', '')}\n\n"
                    "【建议】\n"
                    "这个分数段选择较多，可以兼顾冲刺和稳妥志愿。"
                )
            elif score >= 600:
                return (
                    f"📚 {score}分 - 昆明高中推荐\n\n"
                    "【推荐学校】\n"
                    "• 昆明市第十四中学\n"
                    "  - 录取线：约590-600分\n\n"
                    "• 昆明市实验中学\n"
                    "  - 录取线：约580-595分\n\n"
                    "• 官渡区第一中学\n"
                    "  - 录取线：约570-590分\n\n"
                    "【建议】\n"
                    "建议结合志愿填报策略，合理安排梯度。"
                )
            else:
                return (
                    f"🎯 {score}分 - 昆明高中推荐\n\n"
                    "【推荐学校】\n"
                    "• 各类民办高中\n"
                    "• 普通高中\n\n"
                    "【建议】\n"
                    "建议关注民办高中和特色学校的招生政策。"
                )
        
        # 云南其他地区
        return (
            f"🎓 {score}分 - 云南高中推荐\n\n"
            "根据您的分数，建议关注以下类型学校：\n"
            "• 地州重点高中（如文山州一中、红河州一中等）\n"
            "• 当地优质民办学校\n\n"
            "建议告诉我您所在的城市，我可以提供更精准的推荐！"
        )

    def _compare_schools(self, school1: str, school2: str) -> str:
        """对比两所学校的关键信息"""
        # 学校基础信息映射（扩展版）
        school_info = {
            "师大附中": {
                "name": "云南师范大学附属中学",
                "type": "公办",
                "level": "一级一等",
                "score_line": "680-690分",
                "first_rate": "95%+",
                "founded": "1940年",
                "location": "昆明市高新区洪源路36号",
                "phone": "0871-68215819",
                "highlight": "云南省顶尖高中，清北录取人数全省第一",
                "campus_size": "约200亩",
                "student_count": "约2500人",
                "teacher_count": "特级教师12人，高级教师80+人",
                "specialty": ["奥赛", "科技创新", "文科"],
                "tuition": "约300元/学期（公办）",
                "dormitory": "有住宿，4-6人/间",
                "entrance_exam": "自主招生+中考统招",
                "famous_alumni": "多位两院院士、科技精英"
            },
            "昆一中": {
                "name": "昆明市第一中学",
                "type": "公办",
                "level": "一级一等",
                "score_line": "675-685分",
                "first_rate": "90%+",
                "founded": "1905年",
                "location": "昆明市五华区西昌路233号",
                "phone": "0871-65324879",
                "highlight": "百年名校，历史悠久",
                "campus_size": "约150亩",
                "student_count": "约3000人",
                "teacher_count": "特级教师8人，高级教师60+人",
                "specialty": ["文科", "外语", "艺术"],
                "tuition": "约300元/学期（公办）",
                "dormitory": "有住宿，6人/间",
                "entrance_exam": "统招+定向",
                "famous_alumni": "多位云南名人、学者"
            },
            "昆三中": {
                "name": "昆明市第三中学",
                "type": "公办",
                "level": "一级一等",
                "score_line": "670-680分",
                "first_rate": "85%+",
                "founded": "1907年",
                "location": "昆明市呈贡区",
                "phone": "0871-67426100",
                "highlight": "呈贡校区环境优美，科技教育突出",
                "campus_size": "约300亩",
                "student_count": "约3200人",
                "teacher_count": "特级教师6人，高级教师50+人",
                "specialty": ["理科", "科技", "体育"],
                "tuition": "约300元/学期（公办）",
                "dormitory": "有住宿，4-6人/间",
                "entrance_exam": "统招+定向",
                "famous_alumni": "多位科技界、商界精英"
            },
            "昆八中": {
                "name": "昆明市第八中学",
                "type": "公办",
                "level": "一级一等",
                "score_line": "650-660分",
                "first_rate": "85%+",
                "founded": "1952年",
                "location": "昆明市五华区龙泉路628号",
                "phone": "0871-65155666",
                "highlight": "德育工作突出，艺术教育特色",
                "campus_size": "约200亩",
                "student_count": "约3500人",
                "teacher_count": "特级教师5人，高级教师45+人",
                "specialty": ["艺术", "德育", "综合"],
                "tuition": "约300元/学期（公办）",
                "dormitory": "有住宿，6人/间",
                "entrance_exam": "统招+定向",
                "famous_alumni": "多位文化艺术界人士"
            },
            "云大附中": {
                "name": "云南大学附属中学",
                "type": "民办",
                "level": "一级一等",
                "score_line": "645-655分",
                "first_rate": "90%+",
                "founded": "1927年",
                "location": "昆明市呈贡区",
                "phone": "0871-67453388",
                "highlight": "依托云大资源，学术氛围浓厚",
                "campus_size": "约250亩",
                "student_count": "约4000人",
                "teacher_count": "云大兼职教授+骨干教师",
                "specialty": ["综合", "国际化", "竞赛"],
                "tuition": "约20000元/学年",
                "dormitory": "有住宿，4人/间",
                "entrance_exam": "自主招生+中考",
                "famous_alumni": "多位云大教授、企业家"
            },
            "昆十中": {
                "name": "昆明市第十中学",
                "type": "公办",
                "level": "一级一等",
                "score_line": "640-650分",
                "first_rate": "80%+",
                "founded": "1920年",
                "location": "昆明市盘龙区白塔路247号",
                "phone": "0871-63162331",
                "highlight": "理科见长，体育传统强校",
                "campus_size": "约120亩",
                "student_count": "约2800人",
                "teacher_count": "特级教师4人，高级教师40+人",
                "specialty": ["理科", "体育", "传统教育"],
                "tuition": "约300元/学期（公办）",
                "dormitory": "部分住宿",
                "entrance_exam": "统招+定向",
                "famous_alumni": "多位体育健将、科学家"
            },
            "昆十四中": {
                "name": "昆明市第十四中学",
                "type": "公办",
                "level": "一级一等",
                "score_line": "630-640分",
                "first_rate": "75%+",
                "founded": "1954年",
                "location": "昆明市五华区黑林铺前街79号",
                "phone": "0871-68180101",
                "highlight": "低进高出，加工能力强",
                "campus_size": "约150亩",
                "student_count": "约3000人",
                "teacher_count": "高级教师35+人",
                "specialty": ["加工能力", "理科", "均衡教育"],
                "tuition": "约300元/学期（公办）",
                "dormitory": "有住宿",
                "entrance_exam": "统招+定向",
                "famous_alumni": "多位行业骨干"
            },
            "未央中学": {
                "name": "丘北未央中学",
                "type": "民办",
                "level": "省一级二等",
                "score_line": "参考中考综合成绩",
                "first_rate": "高考成绩逐年提升",
                "founded": "2019年",
                "location": "丘北县文秀路129号",
                "phone": "0876-4122666",
                "highlight": "州一中直管，全封闭管理",
                "campus_size": "约200亩",
                "student_count": "约2000人",
                "teacher_count": "州一中骨干教师领衔",
                "specialty": ["全封闭管理", "州一中资源", "严格管理"],
                "tuition": "4000-5000元/学期（按分数段）",
                "dormitory": "全住宿，4-6人/间",
                "entrance_exam": "自主招生+中考",
                "famous_alumni": "近年崭露头角"
            },
            "大理一中": {
                "name": "大理白族自治州第一中学",
                "type": "公办",
                "level": "一级一等",
                "score_line": "660-670分",
                "first_rate": "88%+",
                "founded": "1877年",
                "location": "大理市下关镇",
                "phone": "0872-2125339",
                "highlight": "滇西名校，百年历史",
                "campus_size": "约180亩",
                "student_count": "约2500人",
                "teacher_count": "特级教师7人，高级教师55+人",
                "specialty": ["综合", "文科", "民族教育"],
                "tuition": "约300元/学期（公办）",
                "dormitory": "有住宿",
                "entrance_exam": "统招+定向",
                "famous_alumni": "多位云南名人"
            },
            "曲靖一中": {
                "name": "曲靖市第一中学",
                "type": "公办",
                "level": "一级一等",
                "score_line": "675-685分",
                "first_rate": "92%+",
                "founded": "1913年",
                "location": "曲靖市麒麟区",
                "phone": "0874-3122416",
                "highlight": "滇东名校，高考成绩优异",
                "campus_size": "约200亩",
                "student_count": "约3000人",
                "teacher_count": "特级教师9人，高级教师65+人",
                "specialty": ["理科", "奥赛", "高考"],
                "tuition": "约300元/学期（公办）",
                "dormitory": "有住宿",
                "entrance_exam": "统招+定向",
                "famous_alumni": "多位科技精英"
            }
        }

        # 标准化学校名称
        def normalize_school(name):
            name = name.lower()
            if "师大附中" in name or "云南师范大学附属中学" in name:
                return "师大附中"
            elif "昆一中" in name or "昆明第一中学" in name:
                return "昆一中"
            elif "昆三中" in name or "昆明第三中学" in name:
                return "昆三中"
            elif "昆八中" in name or "昆明第八中学" in name:
                return "昆八中"
            elif "云大附中" in name or "云南大学附属中学" in name:
                return "云大附中"
            elif "昆十中" in name or "昆明第十中学" in name:
                return "昆十中"
            elif "昆十四中" in name or "昆明第十四中学" in name:
                return "昆十四中"
            elif "大理一中" in name or "大理白族自治州第一中学" in name:
                return "大理一中"
            elif "曲靖一中" in name or "曲靖市第一中学" in name:
                return "曲靖一中"
            elif "未央" in name or "丘北未央" in name:
                return "未央中学"
            return None

        s1_key = normalize_school(school1)
        s2_key = normalize_school(school2)

        if not s1_key or not s2_key:
            return "抱歉，我暂时无法对比这两所学校。请确认学校名称是否正确。"

        if s1_key not in school_info or s2_key not in school_info:
            return "抱歉，我暂时没有其中一所学校的详细信息，无法进行对比。"

        info1 = school_info[s1_key]
        info2 = school_info[s2_key]

        # 生成特色标签字符串
        def format_specialties(specialties):
            return "、".join(specialties)

        return f"""🏫 {info1['name']} vs {info2['name']}

📊 【基本信息对比】
                          {info1['name']}          {info2['name']}
学校性质                    {info1['type']}                    {info2['type']}
办学等级                    {info1['level']}               {info2['level']}
创建时间                    {info1['founded']}                 {info2['founded']}
校园规模                    {info1['campus_size']}         {info2['campus_size']}
学生人数                    {info1['student_count']}         {info2['student_count']}

📚 【师资力量对比】
师资概况                    {info1['teacher_count']}
                           {info2['teacher_count']}

🎯 【招生录取对比】
录取分数线                  {info1['score_line']}           {info2['score_line']}
一本率                      {info1['first_rate']}                  {info2['first_rate']}
招生方式                    {info1['entrance_exam']}
                           {info2['entrance_exam']}

💰 【费用对比】
学费标准                    {info1['tuition']}
                           {info2['tuition']}
住宿条件                    {info1['dormitory']}
                           {info2['dormitory']}

🎨 【办学特色对比】
特色方向                    {format_specialties(info1['specialty'])}
                           {format_specialties(info2['specialty'])}
学校亮点                    {info1['highlight']}
                           {info2['highlight']}

📍 【联系方式】
{info1['name']}
地址: {info1['location']}
电话: {info1['phone']}

{info2['name']}
地址: {info2['location']}
电话: {info2['phone']}

💡 【选择建议】
1. 如果孩子成绩优秀(680+分)，优先考虑录取分数线更高的学校
2. 如果孩子在650-680分区间，可根据特长和偏好选择特色匹配的学校
3. 考虑家庭经济情况，民办学校学费通常较高
4. 关注学校特色与孩子兴趣特长的匹配度
5. 两所学校都是云南省优质高中，可结合家庭地理位置选择

需要我帮您分析更具体的志愿填报策略吗？"""

    def _get_policy_info(self, user_input: str) -> str:
        """获取政策信息"""
        user_lower = user_input.lower()
        
        # ==================== 指标到校政策（优先检测） ====================
        if any(kw in user_lower for kw in ["指标到校", "指标生", "定向招生", "定向生"]):
            return self._get_zhibiao_daoxiao_info(user_input)
        
        # ==================== 提前批政策 ====================
        if any(kw in user_lower for kw in ["提前批", "提前批次"]):
            return self._get_zaoti_pi_info(user_input)
        
        # ==================== 特长生政策 ====================
        if any(kw in user_lower for kw in ["特长生", "体育特长", "艺术特长", "科技特长", "特长招生"]):
            return self._get_special_student_info(user_input)
        
        # ==================== 民族班政策 ====================
        if any(kw in user_lower for kw in ["民族班", "少数民族", "民族加分", "少数民族加分"]):
            return self._get_minzu_class_info(user_input)
        
        # ==================== 海军航空班 ====================
        if any(kw in user_lower for kw in ["海军航空班", "航空班", "招飞"]):
            return self._get_haijun_hangkong_info(user_input)
        
        # ==================== 志愿填报分析请求 ====================
        if any(kw in user_lower for kw in ["志愿", "填报", "志愿填报", "怎么填", "怎么报"]):
            return self._get_volunteer_analysis(user_input)
        
        # 文山州中考政策
        if "文山" in user_lower:
            return (
                "📋 文山州中考招录政策\n\n"
                "【考试科目】\n"
                "• 必考科目：语文、数学、英语（各120分）\n"
                "• 选考科目：物理、化学、道德与法治、历史、生物、地理（各100分）\n"
                "• 体育：50分（必考）\n\n"
                "【总分】790分\n\n"
                "【录取方式】\n"
                "• 公办高中：按分数从高到低录取，结合志愿填报\n"
                "• 州属重点高中（文山州一中）：全州统招+定向名额\n"
                "• 县属高中：主要面向本县招生\n"
                "• 民办高中：自主招生，需达到最低控制线\n\n"
                "【志愿设置】\n"
                "• 提前批：州一中、州民中\n"
                "• 第一批：县级重点高中\n"
                "• 第二批：一般公办高中\n"
                "• 第三批：民办高中\n\n"
                "【特殊政策】\n"
                "• 定向招生：优质高中50%名额定向分配到各乡镇初中\n"
                "• 少数民族加分：最多加20分\n"
                "• 体育艺术特长生：单独录取通道\n\n"
                "【时间安排】\n"
                "• 考试时间：6月下旬\n"
                "• 成绩公布：7月中旬\n"
                "• 志愿填报：7月中下旬\n"
                "• 录取结果：8月上旬\n\n"
                "需要了解具体学校的录取分数线或报名流程吗？"
            )
        
        # 通用云南省中考政策
        return (
            "📋 云南省中考政策要点\n\n"
            "【考试科目】\n"
            "语文、数学、英语、物理、化学、道德与法治、历史、体育等\n\n"
            "【录取方式】\n"
            "• 公办高中：划片录取+志愿填报\n"
            "• 民办高中：自主招生\n\n"
            "【志愿填报】\n"
            "中考成绩公布后填报，一般可填报多个志愿\n\n"
            "需要了解具体地州的政策吗？告诉我您在哪个城市。"
        )
    
    def _get_zhibiao_daoxiao_info(self, user_input: str) -> str:
        """获取指标到校详细政策"""
        user_lower = user_input.lower()
        
        # 昆明市指标到校政策
        if "昆明" in user_lower:
            return (
                "📋 昆明市指标到校生政策\n\n"
                "【什么是指标到校】\n"
                "指标到校（定向招生）是指优质高中将招生计划的一定比例\n"
                "定向分配到区域内各初中学校招生，让更多初中生有机会进入重点高中。\n\n"
                "【昆明市政策要点】\n"
                "• 指标到校比例：优质高中招生计划中，指标到校占50%\n"
                "• 录取分数线：指标到校生录取分数比统招线低10-20分\n"
                "• 报名条件：必须连续三年在学籍所在学校就读\n"
                "• 校内竞争：校内学生按分数排名竞争指标名额\n\n"
                "【如何填报指标到校志愿】\n\n"
                "1️⃣ **确认资格**\n"
                "   • 在学籍所在初中连续就读满3年\n"
                "   • 符合昆明市中考报名条件\n"
                "   • 估分达到志愿高中指标到校最低控制线\n\n"
                "2️⃣ **了解本校配额**\n"
                "   • 向班主任或学校教务处咨询\n"
                "   • 了解本校获得哪些高中的指标名额\n"
                "   • 知道每个指标的竞争人数\n\n"
                "3️⃣ **志愿填报技巧**\n"
                "   • 不能跨校填报，只能填报本校获得的指标高中\n"
                "   • 建议选择比自身实力略高的学校作为冲刺\n"
                "   • 校内排名靠前的学生适合填报优质高中\n"
                "   • 校内排名中等的学生建议选择稳妥的学校\n\n"
                "【昆明市主要优质高中】\n"
                "• 师大附中、昆一中、昆三中（指标到校名额多）\n"
                "• 昆八中、昆十中、昆十四中（指标到校名额较多）\n\n"
                "【注意事项】\n"
                "• 指标到校未被录取，不影响后续批次录取\n"
                "• 填报后一般不能更改，请谨慎选择\n\n"
                "请问您孩子的预估分数和校内排名是多少？我可以帮您分析具体填报策略。"
            )
        
        # 文山州指标到校政策
        if "文山" in user_lower:
            return (
                "📋 文山州指标到校（定向生）政策\n\n"
                "【政策要点】\n"
                "• 优质高中（州一中、文山学院附中等）50%招生计划定向招生\n"
                "• 定向名额分配到全州各乡镇初中学校\n"
                "• 录取分数比统招线适当降低\n\n"
                "【报名条件】\n"
                "• 在学学籍地初中学校连续就读满3年\n"
                "• 符合文山州中考报名条件\n"
                "• 学业水平考试等级达到要求\n\n"
                "【填报建议】\n"
                "• 了解本校获得的定向高中名额\n"
                "• 根据校内排名和估分选择合适的高中\n"
                "• 校内排名靠前可冲刺州一中\n\n"
                "需要了解更具体的填报策略吗？"
            )
        
        # 通用指标到校政策
        return (
            "📋 指标到校（定向招生）政策解读\n\n"
            "【什么是指标到校】\n"
            "指标到校是指优质高中将部分招生名额定向分配到\n"
            "区域内各初中学校，让更多学生有机会进入重点高中。\n\n"
            "【基本政策】\n"
            "• 指标到校比例：一般为招生计划的50%\n"
            "• 录取优惠：可比统招线低10-20分录取\n"
            "• 报名条件：需在学籍校连续就读满3年\n"
            "• 竞争方式：校内学生按分数排名竞争指标\n\n"
            "【填报技巧】\n"
            "• 了解本校获得的指标名额有哪些高中\n"
            "• 根据校内排名选择合适的学校\n"
            "• 排名靠前可以冲刺更好的学校\n"
            "• 指标到校未被录取不影响后续批次\n\n"
            "请问您是哪个地区的学生？我可以提供更具体的政策解读。"
        )
    
    def _get_zaoti_pi_info(self, user_input: str) -> str:
        """获取提前批政策信息"""
        user_lower = user_input.lower()
        
        # 昆明市提前批
        if "昆明" in user_lower:
            return (
                "📋 昆明市中考提前批政策\n\n"
                "【提前批概述】\n"
                "提前批是在正式填报志愿前进行的提前录取批次，\n"
                "适合对特定学校或专业有明确目标的学生。\n\n"
                "【昆明市提前批设置】\n"
                "• 提前批学校：部分优质高中和特色学校\n"
                "• 招生类型：民族班、海军航空班、特定专业等\n"
                "• 录取方式：提前面试/测试+中考成绩综合评价\n\n"
                "【提前批填报注意事项】\n\n"
                "1️⃣ **适合人群**\n"
                "   • 有明确的高中目标学校\n"
                "   • 符合提前批招生的特殊条件（如民族身份）\n"
                "   • 愿意参加学校组织的面试或测试\n\n"
                "2️⃣ **填报技巧**\n"
                "   • 提前批不影响后续批次录取，可以大胆冲刺\n"
                "   • 但一旦被提前批录取，不能放弃再去竞争后续批次\n"
                "   • 建议估分达到或接近目标学校往年录取线再填报\n\n"
                "3️⃣ **常见误区**\n"
                "   • 误区1：提前批录取分数一定低（不一定）\n"
                "   • 误区2：可以不填报提前批（可以，但可能错过机会）\n"
                "   • 误区3：提前批被录取就不能去其他学校（是的）\n\n"
                "【云南师大附中海军航空班】\n"
                "• 招生对象：立志从事海军航空事业的男生\n"
                "• 身体条件：身高、体重、视力等要求\n"
                "• 录取优惠：成绩优秀可享受学费减免\n\n"
                "需要了解您所在地区的具体提前批学校吗？"
            )
        
        # 文山州提前批
        if "文山" in user_lower:
            return (
                "📋 文山州中考提前批政策\n\n"
                "【提前批学校】\n"
                "• 文山州第一中学（州属重点高中）\n"
                "• 文山州民族中学\n\n"
                "【填报条件】\n"
                "• 需达到提前批学校的录取分数线\n"
                "• 部分学校可能有面试或特长测试\n\n"
                "【注意事项】\n"
                "• 提前批录取优先于第一批次\n"
                "• 一旦被提前批录取，不再参与后续批次录取\n"
                "• 未被提前批录取不影响后续批次填报\n\n"
                "需要了解具体的填报策略吗？"
            )
        
        # 通用提前批政策
        return (
            "📋 中考提前批政策解读\n\n"
            "【什么是提前批】\n"
            "提前批是在正常批次录取前进行的招生批次，\n"
            "通常包括重点高中的特殊类型招生。\n\n"
            "【提前批招生类型】\n"
            "• 民族班：面向少数民族学生\n"
            "• 特色班：艺术、体育、国际课程等\n"
            "• 直升班：初中部直升高中部\n"
            "• 航空班/军警校：定向培养\n\n"
            "【填报注意事项】\n\n"
            "1️⃣ **录取规则**\n"
            "   • 提前批录取后不能参加后续批次录取\n"
            "   • 未被提前批录取不影响后续正常批次\n\n"
            "2️⃣ **填报建议**\n"
            "   • 提前批可以当作冲刺机会，但要有心理准备\n"
            "   • 确保了解目标学校的特殊要求（面试、体检等）\n"
            "   • 如果没有明确的提前批目标学校，建议跳过\n\n"
            "3️⃣ **风险提示**\n"
            "   • 一旦被提前批录取，必须接受录取结果\n"
            "   • 不能反悔再去竞争普通批次学校\n\n"
            "请问您是哪个地区的学生？我可以提供更具体的提前批政策。"
        )
    
    def _get_special_student_info(self, user_input: str) -> str:
        """获取特长生政策信息"""
        user_lower = user_input.lower()
        
        # 体育特长生
        if any(kw in user_lower for kw in ["体育特长", "体育生", "田径", "篮球", "足球", "游泳", "武术"]):
            return (
                "🏃 体育特长生招生政策\n\n"
                "【招生范围】\n"
                "• 田径、篮球、足球、排球、游泳、武术、羽毛球、乒乓球等\n\n"
                "【报名条件】\n"
                "• 具有一定的体育专项技能\n"
                "• 身体健康，符合体育训练要求\n"
                "• 初中阶段获得过县级以上比赛奖项优先\n\n"
                "【测试内容】\n"
                "• 专项技能测试\n"
                "• 身体素质测试\n"
                "• 文化课成绩要求（需达到最低控制线）\n\n"
                "【录取优惠】\n"
                "• 可享受降低10-30分录取优惠\n"
                "• 具体降分幅度根据学校和项目而定\n\n"
                "【报名时间】\n"
                "• 每年3-4月，具体时间关注学校通知\n\n"
                "【注意事项】\n"
                "• 需提前到目标学校报名\n"
                "• 参加学校组织的专项测试\n"
                "• 特长生录取后需参加学校运动队训练\n\n"
                "需要了解具体学校的体育特长生招生信息吗？"
            )
        
        # 艺术特长生
        if any(kw in user_lower for kw in ["艺术特长", "音乐", "舞蹈", "美术", "书法", "播音", "表演"]):
            return (
                "🎨 艺术特长生招生政策\n\n"
                "【招生范围】\n"
                "• 音乐（声乐、器乐）、舞蹈、美术、书法、播音主持、表演等\n\n"
                "【报名条件】\n"
                "• 具有一定的艺术专业基础\n"
                "• 初中阶段获得过县级以上比赛奖项优先\n"
                "• 部分学校要求提供作品集\n\n"
                "【测试内容】\n"
                "• 专业技能展示\n"
                "• 乐理知识测试（音乐类）\n"
                "• 文化课成绩要求（需达到最低控制线）\n\n"
                "【录取优惠】\n"
                "• 可享受降低10-30分录取优惠\n"
                "• 具体降分幅度根据学校和专业而定\n\n"
                "【报名时间】\n"
                "• 每年3-4月，具体时间关注学校通知\n\n"
                "【注意事项】\n"
                "• 需提前准备作品集或视频资料\n"
                "• 参加学校组织的专业面试\n"
                "• 艺术特长生录取后需参加学校艺术社团\n\n"
                "需要了解具体学校的艺术特长生招生信息吗？"
            )
        
        # 科技特长生
        if any(kw in user_lower for kw in ["科技特长", "信息学", "编程", "机器人", "航模", "科技创新"]):
            return (
                "🤖 科技特长生招生政策\n\n"
                "【招生范围】\n"
                "• 科技创新、信息学竞赛（NOIP）、机器人、航模等\n\n"
                "【报名条件】\n"
                "• 初中阶段参加过科技类竞赛\n"
                "• 获得过相关竞赛奖项优先\n"
                "• 具有一定的编程或科技实践能力\n\n"
                "【测试内容】\n"
                "• 专业知识测试\n"
                "• 实践操作能力\n"
                "• 项目展示与答辩\n\n"
                "【录取优惠】\n"
                "• 可享受降低10-20分录取优惠\n"
                "• 信息学竞赛获奖选手可获得更大优惠\n\n"
                "【报名时间】\n"
                "• 每年3-4月，具体时间关注学校通知\n\n"
                "【注意事项】\n"
                "• 需准备竞赛获奖证书\n"
                "• 部分学校要求现场编程测试\n"
                "• 科技特长生可加入学校竞赛团队\n\n"
                "需要了解具体学校的科技特长生招生信息吗？"
            )
        
        # 通用特长生政策
        return (
            "⭐ 特长生招生政策解读\n\n"
            "【特长生类型】\n"
            "• 体育特长生：田径、篮球、足球、游泳、武术等\n"
            "• 艺术特长生：音乐、舞蹈、美术、书法、播音主持等\n"
            "• 科技特长生：信息学、机器人、科技创新等\n\n"
            "【报名条件】\n"
            "• 具有相关特长和技能\n"
            "• 初中阶段获得过相关奖项优先\n"
            "• 文化课成绩需达到学校最低控制线\n\n"
            "【录取优惠】\n"
            "• 一般可降10-30分录取\n"
            "• 具体降分幅度因学校和项目而异\n\n"
            "【报名流程】\n"
            "1. 关注目标学校招生简章\n"
            "2. 按要求提交报名材料\n"
            "3. 参加学校组织的专项测试\n"
            "4. 根据测试成绩和中考成绩综合录取\n\n"
            "【注意事项】\n"
            "• 特长生录取后需参加学校相关训练和活动\n"
            "• 未被录取不影响普通批次录取\n\n"
            "您想了解哪种类型的特长生政策？"
        )
    
    def _get_minzu_class_info(self, user_input: str) -> str:
        """获取民族班政策信息"""
        user_lower = user_input.lower()
        
        # 民族班政策
        if "民族班" in user_lower:
            return (
                "🏫 民族班招生政策\n\n"
                "【招生对象】\n"
                "• 云南省户籍的少数民族学生\n"
                "• 包括：彝族、哈尼族、傣族、白族、回族、苗族等25个少数民族\n\n"
                "【报名条件】\n"
                "• 具有云南省户籍的少数民族学生\n"
                "• 符合中考报名条件\n"
                "• 部分学校要求在少数民族地区就读\n\n"
                "【录取优惠】\n"
                "• 可享受降低20-40分录取优惠\n"
                "• 具体降分幅度根据学校和地区而定\n"
                "• 民族班学生享受国家助学金政策\n\n"
                "【志愿填报】\n"
                "• 与普通志愿填报同步\n"
                "• 在提前批或第一批次填报\n"
                "• 需在志愿表中注明少数民族身份\n\n"
                "【培养特点】\n"
                "• 单独编班，配备优秀师资\n"
                "• 注重民族文化教育\n"
                "• 提供学业辅导和生活关怀\n\n"
                "【注意事项】\n"
                "• 需提供少数民族身份证明\n"
                "• 民族班名额有限，按分数从高到低录取\n"
                "• 被录取后需签订相关协议\n\n"
                "需要了解具体学校的民族班招生信息吗？"
            )
        
        # 少数民族加分政策
        if any(kw in user_lower for kw in ["民族加分", "少数民族加分", "加分"]):
            return (
                "🎁 云南省少数民族加分政策\n\n"
                "【加分标准】\n"
                "• 聚居区少数民族：加20分\n"
                "• 散居区少数民族：加10分\n"
                "• 边疆少数民族地区考生：可额外加分\n\n"
                "【适用范围】\n"
                "• 适用于云南省内所有高中录取\n"
                "• 加分计入中考总分参与录取\n"
                "• 可与其他政策性加分叠加（但有上限）\n\n"
                "【申请流程】\n"
                "• 在中考报名时申报少数民族身份\n"
                "• 提供户口本等相关证明材料\n"
                "• 由教育部门审核确认\n\n"
                "【注意事项】\n"
                "• 加分政策以当年官方公告为准\n"
                "• 不同地区可能有细微差别\n"
                "• 加分仅适用于投档，具体录取由学校决定\n\n"
                "需要了解您所在地区的具体加分政策吗？"
            )
        
        # 通用民族政策
        return (
            "🌟 少数民族招生政策\n\n"
            "【民族班】\n"
            "• 面向少数民族学生的专项招生计划\n"
            "• 可享受20-40分降分录取优惠\n"
            "• 配备优秀师资，单独编班教学\n\n"
            "【少数民族加分】\n"
            "• 聚居区少数民族：加20分\n"
            "• 散居区少数民族：加10分\n"
            "• 加分计入中考总分\n\n"
            "【报考建议】\n"
            "• 少数民族学生可同时享受民族班和加分政策\n"
            "• 提前了解目标学校的民族班招生计划\n"
            "• 准备好相关身份证明材料\n\n"
            "您想了解民族班还是少数民族加分政策？"
        )
    
    def _get_haijun_hangkong_info(self, user_input: str) -> str:
        """获取海军航空班政策信息"""
        return (
            "✈️ 海军航空班招生政策\n\n"
            "【招生对象】\n"
            "• 立志从事海军航空事业的优秀男生\n"
            "• 年龄14-16周岁（当年9月1日前满14岁，不满17岁）\n\n"
            "【身体条件】\n"
            "• 身高：162-180cm\n"
            "• 体重：符合标准（BMI指数正常）\n"
            "• 视力：双眼裸眼视力不低于4.6，无色盲、色弱\n"
            "• 身体健康，符合海军招飞体检标准\n\n"
            "【报名条件】\n"
            "• 热爱祖国，立志献身国防事业\n"
            "• 品学兼优，综合素质优秀\n"
            "• 具有云南省户籍\n\n"
            "【选拔流程】\n"
            "1. 网上报名（每年2-3月）\n"
            "2. 初检筛查\n"
            "3. 全面体检\n"
            "4. 心理测试\n"
            "5. 政治考核\n"
            "6. 中考成绩达标\n\n"
            "【培养模式】\n"
            "• 军事化管理\n"
            "• 航空特色课程（航空理论、飞行模拟等）\n"
            "• 定期体能训练\n"
            "• 寒暑假军事体验\n\n"
            "【录取优惠】\n"
            "• 学费减免\n"
            "• 享受海军专项培养经费\n"
            "• 毕业后优先推荐报考海军飞行院校\n\n"
            "【招生学校】\n"
            "• 云南师范大学附属中学（云南省唯一承办学校）\n\n"
            "【招生规模】\n"
            "• 每年全省招生约50人\n\n"
            "【注意事项】\n"
            "• 录取后需签订培养协议\n"
            "• 严格遵守军事化管理规定\n"
            "• 全程淘汰制，不符合要求将退回普通班\n\n"
            "需要了解更多海军航空班的详细信息吗？"
        )

    def _get_volunteer_analysis(self, user_input: str) -> str:
        """志愿填报分析"""
        import re
        
        # 尝试提取分数
        score_match = re.search(r'(\d{2,3})分?', user_input)
        score = int(score_match.group(1)) if score_match else None
        
        if score:
            return self._generate_volunteer_plan(score)
        else:
            return (
                "📋 志愿填报分析指导\n\n"
                "为了给您提供精准的志愿填报建议，请告诉我：\n"
                "1. 您的**预估中考分数**是多少？\n"
                "2. 您所在的**地区**（昆明/文山/大理/曲靖等）？\n"
                "3. 您的**目标学校类型**（重点高中/普通高中/民办高中）？\n"
                "4. 是否有**特长或加分项**（体育/艺术/少数民族等）？\n\n"
                "有了这些信息，我就能为您制定专属的志愿填报策略！"
            )

    def _generate_volunteer_plan(self, score: int) -> str:
        """根据分数生成志愿填报方案"""
        # 昆明地区学校分数线参考
        schools_by_score = [
            ("师大附中", 680),
            ("昆一中", 675),
            ("曲靖一中", 675),
            ("昆三中", 670),
            ("大理一中", 660),
            ("昆八中", 650),
            ("云大附中", 645),
            ("昆十中", 640),
            ("昆十四中", 630),
            ("其他一级完中", 600),
        ]
        
        # 找出匹配的学校
        reach_schools = []   # 冲刺学校
        match_schools = []   # 匹配学校
        safe_schools = []    # 稳妥学校
        
        for name, line in schools_by_score:
            if score >= line - 10 and score < line + 5:
                reach_schools.append(name)
            elif score >= line + 5 and score < line + 20:
                match_schools.append(name)
            elif score >= line + 20:
                safe_schools.append(name)
        
        # 生成志愿方案
        plan = f"""📊 【{score}分】志愿填报方案分析

🎯 【分数定位】
根据您的分数，您处于云南省中考的{
    "顶尖水平" if score >= 670 else
    "优秀水平" if score >= 640 else
    "良好水平" if score >= 600 else
    "中等水平"
}

🎓 【志愿填报策略】
志愿填报要遵循\"冲一冲、稳一稳、保一保\"的原则！

1️⃣ **冲刺志愿**（比分数高5-10分）：
   {chr(10).join(f'   • {s}' for s in reach_schools[:2]) if reach_schools else '   可以尝试比自己分数略高的学校'}

2️⃣ **匹配志愿**（分数范围内）：
   {chr(10).join(f'   • {s}' for s in match_schools[:3]) if match_schools else '   根据您的分数选择合适的学校'}

3️⃣ **稳妥志愿**（比分数低15-20分）：
   {chr(10).join(f'   • {s}' for s in safe_schools[:3]) if safe_schools else '   选择有把握的学校保底'}

💡 【填报技巧】
• 志愿顺序很重要，把最想去的学校放在前面
• 注意查看学校的招生计划和历年分数线变化
• 考虑\"大小年\"现象，某些学校可能分数波动
• 不要只看名校，适合自己的才是最好的
• 充分利用定向生、特长生等政策

📝 【注意事项】
• 了解各校的住宿条件、交通情况
• 关注学校的特色班、实验班招生
• 考虑家庭经济情况选择民办还是公办
• 务必在规定时间内完成填报并确认

需要我帮您对比具体学校的详细情况吗？"""
        return plan

    def _get_study_plan(self, user_input: str) -> str:
        """备考建议生成"""
        user_lower = user_input.lower()
        
        # 检测是否为备考建议请求
        study_keywords = ["备考", "复习", "怎么学", "怎么复习", "学习计划", "提分", "冲刺"]
        if any(kw in user_lower for kw in study_keywords):
            return (
                "📚 中考备考冲刺指南\n\n"
                "🎯 【考前冲刺策略】\n\n"
                "📖 【各科复习重点】\n"
                "• **语文**：强化作文训练，背诵古诗文，复习现代文阅读技巧\n"
                "• **数学**：回归基础，整理错题本，重点攻克薄弱知识点\n"
                "• **英语**：每天坚持背单词，练习听力，复习语法和作文模板\n"
                "• **物理/化学**：理解概念公式，多做真题，重视实验题\n"
                "• **政史地生**：记忆核心知识点，关注时事热点，多做选择题\n\n"
                "⏰ 【时间管理建议】\n"
                "• 每天保证6-8小时睡眠，不要熬夜过度\n"
                "• 制定每日学习计划，文理交叉复习\n"
                "• 每天至少做一套真题，培养考试手感\n"
                "• 每周安排1-2次模拟考试，适应考试节奏\n\n"
                "💪 【心理调节】\n"
                "• 保持积极心态，相信自己的能力\n"
                "• 适当运动，缓解紧张情绪\n"
                "• 和家长老师多沟通，寻求支持\n"
                "• 考前1周开始调整作息，适应考试时间\n\n"
                "🎁 【考试技巧】\n"
                "• 先易后难，合理分配时间\n"
                "• 认真审题，避免低级错误\n"
                "• 书写工整，保持卷面整洁\n"
                "• 仔细检查，不要提前交卷\n\n"
                "您想了解哪个科目的具体复习方法吗？我可以为您详细解答！"
            )
        
        return ""

    def _get_learning_plan_info(self) -> str:
        """获取学习计划信息"""
        return (
            "📝 个性化学习计划\n\n"
            "我可以根据您孩子的情况，为您制定专属的学习计划：\n"
            "• 学科薄弱环节分析\n"
            "• 复习进度安排\n"
            "• 备考策略建议\n"
            "• 学习资源推荐\n\n"
            "请告诉我孩子的年级、学习情况和目标，我会为您制定最适合的学习计划！"
        )
    
    def _get_service_introduction(self) -> str:
        return (
            "您好！我是您的中考择校顾问 🌟\n\n"
            "我可以为您提供：\n"
            "📊 云南各高中录取分数线分析\n"
            "🏫 学校推荐与对比（昆明、文山等地区）\n"
            "📝 中考政策与志愿填报指导\n"
            "💰 学费及奖学金政策咨询\n"
            "📅 预约校园参观\n\n"
            "请告诉我：您想了解哪所学校，或者孩子的年级和分数，我来为您详细分析！"
        )
    
    def _get_conversation_summary(self, session_id: str) -> str:
        """获取对话总结"""
        if not session_id:
            return "需要先进行对话才能总结，请先向我提问吧！"
        
        try:
            import requests
            payload = {
                "data": {
                    "session_id": session_id
                },
                "type": "summary"
            }
            response = requests.post("http://localhost:8888/v1/agent", json=payload, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get('data'):
                    return result['data'].get('summary', "对话总结生成中...")
        
        except Exception as e:
            logger.error(f"Hermes总结请求失败: {e}")
        
        # 备用：本地生成简单总结
        return self._generate_simple_summary(session_id)
    
    def _generate_simple_summary(self, session_id: str) -> str:
        """本地生成简单的对话总结"""
        try:
            from app.core.cache import session_cache_manager
            existing_data = session_cache_manager.get_session(session_id)
            if existing_data:
                questions = existing_data.get('questions', [])
                answers = existing_data.get('answers', [])
                
                if questions and answers:
                    summary = "📋 对话总结\n\n"
                    summary += f"【对话轮次】共{len(questions)}轮\n\n"
                    summary += "【对话内容】\n"
                    for i, (q, a) in enumerate(zip(questions, answers), 1):
                        short_answer = a[:40] + "..." if len(a) > 40 else a
                        summary += f"{i}. 您问：{q}\n   我答：{short_answer}\n"
                    summary += "\n如果您还有其他问题，随时可以问我！"
                    return summary
        
        except Exception as e:
            logger.error(f"本地总结生成失败: {e}")
        
        return "我们刚刚开始对话，还没有太多内容可以总结。有什么我可以帮助您的吗？"
    
    def _get_weiyang_info(self) -> str:
        return (
            "📚 丘北未央中学（文山州一中丘北校区）\n\n"
            "【学校定位】\n"
            "非营利性民办完全中学（初中+高中），文山州一中直管校区\n\n"
            "【办学优势】\n"
            "• 州一中直管：教学、管理、考试全部与州一中同步\n"
            "• 全封闭管理：24小时生活管理，适合需要严格管束的学生\n"
            "• 师资优质：州一中骨干教师领衔\n\n"
            "【地址】丘北县文秀路129号\n"
            "【电话】0876-4122666"
        )
    
    def _get_weiyang_enrollment_info(self) -> str:
        return (
            "📋 丘北未央中学（文山州一中丘北校区）- 2026年招生详情\n\n"
            "【招生条件】\n"
            "• 初中部：面向文山州全州招收小学六年级应届毕业生\n"
            "• 高中部：面向文山州全州招收初中应届毕业生，需参加云南省统一中考\n"
            "• 随迁子女：需提供《随迁子女义务教育就学证明》、居住证、父母务工证明\n\n"
            "【初一收费标准】\n"
            "• 公费生（英才班）：语数平均分≥180分，学费0元/学期\n"
            "• 自费生A类（实验班）：语数平均分160-179分，学费3900元/学期\n"
            "• 自费生B类（平行班）：语数平均分＜160分，学费4900元/学期\n"
            "• 住宿费：600元/学期\n\n"
            "【高一收费标准】（按中考裸分段）\n"
            "• 620分以上：公费，学费0元/学期\n"
            "• 600-619分：学费800元/学期\n"
            "• 570-599分：学费2000元/学期\n"
            "• 540-569分：学费2500元/学期\n"
            "• 510-539分：学费3000元/学期\n"
            "• 480-509分：学费3500元/学期\n"
            "• 450-479分：学费4000元/学期\n"
            "• 420-449分：学费5000元/学期\n"
            "• 住宿费：600元/学期\n\n"
            "【其他费用】\n"
            "• 课本费/教辅费：300-500元/学期\n"
            "• 保险费：150元/学年\n"
            "• 活动费：300元/学年\n"
            "• 考试费：500元/学期\n\n"
            "【奖学金政策】\n"
            "• 初一：语数总分200分奖5万，199分奖4万，198分奖3万...\n"
            "• 高一：中考全州第1名奖30万，第2名25万，第3名20万...\n"
            "• 高考：考入清华北大额外奖励10万\n\n"
            "【预约看校】\n"
            "• 招生热线：0876-4122666\n"
            "• 工作时间：工作日8:30-17:00，周末9:00-16:00\n"
            "• 地址：丘北县锦屏镇文秀路129号（弘毅楼一楼招生办）"
        )
    
    def _get_primary_to_middle_info(self) -> str:
        return (
            "🎓 小升初 - 丘北未央中学初中部招生信息\n\n"
            "【招生对象】\n"
            "面向文山州全州招收小学六年级应届毕业生\n\n"
            "【初一班级类型及学费】\n"
            "• 英才班（50人）：语数平均分≥180分，公费生学费0元/学期\n"
            "• 实验班（150人）：语数平均分160-179分，学费3900元/学期\n"
            "• 平行班（200人）：语数平均分＜160分，学费4900元/学期\n"
            "• 住宿费：600元/学期\n\n"
            "【报名条件】\n"
            "• 需提供五年级下学期、六年级上学期语文数学成绩单\n"
            "• 成绩单需加盖小学教务处公章\n\n"
            "【奖学金】\n"
            "• 语数总分200分：奖励5万元\n"
            "• 语数总分199分：奖励4万元\n"
            "• 语数总分198分：奖励3万元\n"
            "• 语数总分197分：奖励2万元\n"
            "• 语数总分196分：奖励1万元\n\n"
            "【联系方式】\n"
            "• 招生热线：0876-4122666\n"
            "• 地址：丘北县锦屏镇文秀路129号\n\n"
            "孩子成绩怎么样？我可以帮您分析适合报读哪个班型。"
        )
    
    def _get_qububei_info(self) -> str:
        return (
            "📍 丘北地区升学咨询\n\n"
            "丘北的家长您好！您想了解哪方面？\n\n"
            "【推荐学校】\n"
            "• 重点推荐：文山州一中丘北校区（未央中学）\n"
            "  - 州一中直管，教学管理同步\n"
            "  - 全封闭管理，师资优质\n\n"
            "【小升初家长常问】\n"
            "• 今年丘北有哪些初中招生？\n"
            "• 未央中学学费多少？\n"
            "• 小升初需要准备什么材料？\n"
            "• 如何预约参观学校？\n\n"
            "请问您想了解哪方面？我可以为您详细介绍。"
        )
    
    def _get_visit_info(self) -> str:
        return (
            "🏫 预约参观丘北未央中学\n\n"
            "【参观时间】\n"
            "• 工作日：8:30-17:00\n"
            "• 周末及节假日：9:00-16:00\n"
            "• 无需提前预约，可直接到校参观\n\n"
            "【参观内容】\n"
            "• 校园环境、教学楼、实验室\n"
            "• 学生宿舍（6-8人间，独立卫浴）\n"
            "• 食堂、图书馆、运动场\n"
            "• 可现场咨询招生政策、提交报名材料\n\n"
            "【学校地址】\n"
            "丘北县锦屏镇文秀路129号\n"
            "（县武装部、应急管理局旁）\n\n"
            "【招生热线】\n"
            "0876-4122666\n\n"
            "【区域负责老师】\n"
            "• 丘北县城：朱老师 15288462036\n"
            "• 丘北乡镇：赖老师 13888444021\n"
            "• 砚山、文山：陈老师 15368422446\n\n"
            "请问您想什么时候来参观？我可以帮您联系负责老师。"
        )
    
    def _get_lead_generation_message(self) -> str:
        return (
            "📋 免费获取择校方案\n\n"
            "我可以帮您定制专属择校方案，包含：\n"
            "✅ 未央中学招生简章\n"
            "✅ 最新收费标准\n"
            "✅ 择校对比分析\n"
            "✅ 升学规划建议\n"
            "✅ 个性化学习计划\n\n"
            "【获取方式】\n"
            "留下您的微信，我直接发给您\n"
            "不收取任何费用，不骚扰\n\n"
            "【重要声明】\n"
            "• 我们仅提供政策解读、学校介绍、择校建议\n"
            "• 所有数据以官方发布为准\n"
            "• 不承诺录取、不保证分数、不包上高中"
        )
    
    @error_handler(default_response="抱歉，分数分析暂时出现问题。请稍后再试，或直接告诉我您的分数，我帮您分析。")
    def _analyze_score_for_weiyang(self, score: int) -> str:
        """根据分数分析适合未央中学的班型"""
        # 判断是小升初分数（100-200）还是中考分数（400-750）
        if 100 <= score <= 200:
            # 小升初语数总分
            if score >= 200:
                return (
                    f"🎉 恭喜！{score}分非常优秀！\n\n"
                    "【推荐班型】英才班（公费）\n"
                    "• 学费：0元/学期\n"
                    "• 奖学金：5万元\n"
                    "• 师资：州一中骨干教师授课\n\n"
                    "建议尽快联系学校确认录取事宜！招生热线：0876-4122666"
                )
            elif score >= 198:
                return (
                    f"👏 {score}分很不错！\n\n"
                    "【推荐班型】英才班\n"
                    "• 学费：0元/学期\n"
                    f"• 奖学金：{210 - score}万元\n"
                    "• 班型优势：小班教学，重点培养\n\n"
                    "准备材料：五年级下学期、六年级上学期成绩单（加盖公章）"
                )
            elif score >= 180:
                return (
                    f"👍 {score}分达到英才班分数线！\n\n"
                    "【推荐班型】英才班（公费）\n"
                    "• 学费：0元/学期\n"
                    "• 无需额外费用\n\n"
                    "建议关注：学校开放日活动，可预约参观校园"
                )
            elif score >= 160:
                return (
                    f"😊 {score}分适合实验班！\n\n"
                    "【推荐班型】实验班\n"
                    "• 学费：3900元/学期\n"
                    "• 住宿费：600元/学期\n"
                    "• 特点：师资优良，管理严格\n\n"
                    "如需奖学金，建议冲刺更高分数！"
                )
            else:
                return (
                    f"💪 {score}分可以报考平行班！\n\n"
                    "【推荐班型】平行班\n"
                    "• 学费：4900元/学期\n"
                    "• 住宿费：600元/学期\n"
                    "• 特点：全封闭管理，适合需要严格管束的学生\n\n"
                    "暑期建议：加强语文数学复习，开学后有分班考机会！"
                )
        elif 400 <= score <= 750:
            # 中考分数
            if score >= 620:
                return (
                    f"🎉 恭喜！{score}分达到公费线！\n\n"
                    "【录取类型】公费生\n"
                    "• 学费：0元/学期\n"
                    "• 住宿费：600元/学期\n\n"
                    "非常优秀！建议关注学校的鹏程班选拔！"
                )
            elif score >= 600:
                return (
                    f"👍 {score}分很不错！\n\n"
                    "【录取类型】自费生\n"
                    "• 学费：800元/学期\n"
                    "• 住宿费：600元/学期\n\n"
                    "接近公费线，继续加油！"
                )
            elif score >= 570:
                return (
                    f"😊 {score}分可以录取！\n\n"
                    "【录取类型】自费生\n"
                    "• 学费：2000元/学期\n"
                    "• 住宿费：600元/学期\n\n"
                    "建议关注学校奖学金政策！"
                )
            elif score >= 540:
                return (
                    f"💪 {score}分可以报考！\n\n"
                    "【录取类型】自费生\n"
                    "• 学费：2500元/学期\n"
                    "• 住宿费：600元/学期\n\n"
                    "暑期建议：查漏补缺，提升薄弱科目！"
                )
            else:
                return (
                    f"📚 {score}分可以报考！\n\n"
                    "【录取类型】自费生\n"
                    "• 学费根据分数段确定\n"
                    "• 住宿费：600元/学期\n\n"
                    "具体学费请咨询招生办：0876-4122666"
                )
        else:
            return f"分数 {score} 不在有效范围内，请确认分数是否正确。"
    
    def _get_closing_message(self) -> str:
        return (
            "感谢你的咨询！祝你孩子升学顺利，前程似锦！🎓\n\n"
            "随时再来咨询，再见！👋\n"
            "🦞 云南中考择校智能服务中心"
        )


class LearningPlanAgent(BaseAgent):
    """个性化学习计划生成 - zk-learning"""
    
    def __init__(self):
        super().__init__(
            name="个性化学习计划生成",
            role="学习规划",
            description="负责根据学生情况生成个性化学习计划和学习建议"
        )
        self.llm_service = LLMService()  # 初始化语言模型服务
    
    def handle(self, user_input: str, context: Dict[str, Any] = None) -> str:
        user_lower = user_input.lower() if user_input else ""
        
        # 分析用户输入，提取关键信息
        grade = self._extract_grade(user_input)
        subject = self._extract_subject(user_input)
        score = self._extract_score(user_input)
        goal = self._extract_goal(user_input)
        
        # 先获取基础回复
        if grade or subject or score or goal:
            base_response = self._generate_personalized_plan(grade, subject, score, goal)
        elif "学习计划" in user_lower or "学习规划" in user_lower or "学习建议" in user_lower:
            base_response = self._generate_learning_plan()
        elif "薄弱科目" in user_lower or "偏科" in user_lower:
            base_response = self._get_subject_improvement()
        elif "时间管理" in user_lower or "学习方法" in user_lower:
            base_response = self._get_study_methods()
        else:
            base_response = self._get_general_info()
        
        # 先使用LLMService增强回复
        try:
            # 构建提示词
            prompt = f"作为个性化学习计划生成专员，针对用户问题：'{user_input}'，基于以下信息生成专业、详细的学习计划和建议：\n\n{base_response}"
            # 调用LLM服务
            llm_result = self.llm_service.generate_answer(prompt)
            if llm_result and "answer" in llm_result:
                return llm_result["answer"]
        except Exception as e:
            logger.error(f"LLM服务调用失败: {e}")
            # LLMService失败时，使用multi_llm_service作为备用
            try:
                logger.info("尝试使用multi_llm_service作为备用")
                fallback_result = generate_with_fallback(prompt)
                if fallback_result and "answer" in fallback_result:
                    return fallback_result["answer"]
            except Exception as fallback_e:
                logger.error(f"备用LLM服务调用失败: {fallback_e}")
        
        # 如果所有LLM服务都失败，返回原始回复
        return base_response
    
    def _extract_grade(self, user_input: str) -> str:
        """提取年级信息"""
        user_lower = user_input.lower()
        grades = ['初一', '初二', '初三', '高一', '高二', '高三', '初中', '高中']
        for grade in grades:
            if grade in user_lower:
                return grade
        return ""
    
    def _extract_subject(self, user_input: str) -> str:
        """提取科目信息"""
        user_lower = user_input.lower()
        subjects = ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理', '政治']
        for subject in subjects:
            if subject in user_lower:
                return subject
        return ""
    
    def _extract_score(self, user_input: str) -> str:
        """提取分数信息"""
        import re
        score_match = re.search(r'(\d+)分', user_input)
        if score_match:
            return score_match.group(1)
        return ""
    
    def _extract_goal(self, user_input: str) -> str:
        """提取目标信息"""
        user_lower = user_input.lower()
        if "提高" in user_lower or "提升" in user_lower:
            import re
            goal_match = re.search(r'提高到(\d+)分', user_lower)
            if goal_match:
                return goal_match.group(1)
        return ""
    
    def _generate_personalized_plan(self, grade: str, subject: str, score: str, goal: str) -> str:
        """生成个性化学习计划"""
        plan = "📅 个性化学习计划\n\n"
        
        # 基本信息
        if grade:
            plan += f"【年级】{grade}\n"
        if subject:
            plan += f"【科目】{subject}\n"
        if score:
            plan += f"【当前成绩】{score}分\n"
        if goal:
            plan += f"【目标成绩】{goal}分\n"
        
        plan += "\n【学习计划】\n"
        
        # 针对数学的学习计划
        if subject == '数学':
            plan += "• 基础巩固：每天完成10道基础题，整理错题本\n"
            plan += "• 题型训练：每周针对一种题型进行专项练习\n"
            plan += "• 模拟考试：每周做一套模拟试卷，分析错题\n"
            plan += "• 查漏补缺：针对薄弱环节进行专项提升\n"
        
        # 时间安排
        plan += "\n【时间安排】\n"
        plan += "• 周一至周五：每天晚上1小时数学学习\n"
        plan += "• 周六：上午2小时综合练习\n"
        plan += "• 周日：上午1小时复习错题\n"
        
        # 学习方法建议
        plan += "\n【学习方法建议】\n"
        plan += "• 建立错题本，定期复习\n"
        plan += "• 多做典型例题，掌握解题思路\n"
        plan += "• 遇到问题及时请教老师或同学\n"
        plan += "• 保持良好的学习心态，循序渐进\n"
        
        return plan
    
    def _generate_learning_plan(self) -> str:
        return (
            "📅 个性化学习计划生成\n\n"
            "为了给您制定最适合的学习计划，我需要了解：\n\n"
            "1️⃣ 孩子现在几年级？\n"
            "2️⃣ 目前的学习成绩如何？（可提供各科分数或等级）\n"
            "3️⃣ 有哪些薄弱科目？\n"
            "4️⃣ 学习时间安排如何？\n"
            "5️⃣ 目标学校是什么？\n\n"
            "提供以上信息后，我会为您生成：\n"
            "• 每日学习时间表\n"
            "• 各科学习方法建议\n"
            "• 薄弱科目提升计划\n"
            "• 模拟考试安排\n"
            "• 心理调节建议"
        )
    
    def _get_subject_improvement(self) -> str:
        return (
            "📚 薄弱科目提升方案\n\n"
            "请告诉我孩子的薄弱科目，我会为您提供针对性的提升建议：\n\n"
            "【语文】\n" 
            "• 阅读理解：每天阅读30分钟，做1-2篇阅读理解练习\n"
            "• 作文：每周写1-2篇作文，积累素材和好词好句\n\n"
            "【数学】\n"
            "• 基础巩固：整理错题本，定期复习\n"
            "• 题型训练：分模块练习，掌握解题技巧\n\n"
            "【英语】\n"
            "• 词汇积累：每天背30-50个单词\n"
            "• 听力口语：每天听英语30分钟，跟读练习\n\n"
            "【物理/化学】\n"
            "• 实验理解：重视实验原理和操作\n"
            "• 公式记忆：理解公式推导过程\n\n"
            "需要针对具体科目制定详细计划吗？"
        )
    
    def _get_study_methods(self) -> str:
        return (
            "🎯 高效学习方法\n\n"
            "【时间管理】\n"
            "• 番茄工作法：25分钟学习+5分钟休息\n"
            "• 四象限法则：优先处理重要紧急的任务\n"
            "• 每日计划：晚上制定第二天的学习计划\n\n"
            "【学习方法】\n"
            "• 费曼学习法：教是最好的学\n"
            "• 艾宾浩斯遗忘曲线：定期复习巩固\n"
            "• 思维导图：整理知识体系\n\n"
            "【习惯养成】\n"
            "• 早起学习：利用早晨黄金时间\n"
            "• 睡前复习：睡前回顾当天学习内容\n"
            "• 运动锻炼：保持身体健康，提高学习效率\n\n"
            "需要针对孩子的具体情况制定个性化方案吗？"
        )
    
    def _get_general_info(self) -> str:
        return (
            "🎓 您好，我是个性化学习计划生成专员。\n\n"
            "我可以为您提供：\n"
            "✅ 个性化学习计划定制\n"
            "✅ 薄弱科目提升方案\n"
            "✅ 高效学习方法指导\n"
            "✅ 时间管理技巧\n"
            "✅ 学习动力激发\n\n"
            "请告诉我孩子的年级、学习情况和目标，我会为您制定最适合的学习计划。"
        )


# 智能体注册表 - 12个智能体
AGENTS = {
    "control_center": ControlCenterSpecialistAgent(),
    "website_issue": WebDeveloperAgent(),
    "design": UIDesignerAgent(),
    "info_query": InfoQueryAgent(),
    "marketing": MarketingAgent(),
    "out_province": OutProvinceAgent(),
    "finance": FinanceAgent(),
    "legal": LegalAgent(),
    "conversion": ConversionAgent(),
    "payment": PaymentAgent(),
    "logistics": LogisticsAgent(),
    "learning_plan": LearningPlanAgent()
}

# 智能体ID映射（对应zk-master/zk-dev等）
AGENT_ID_MAP = {
    "control_center": "zk-master",
    "website_issue": "zk-dev",
    "design": "zk-ui",
    "info_query": "zk-info",
    "marketing": "zk-marketing",
    "out_province": "zk-outside",
    "finance": "zk-finance",
    "legal": "zk-legal",
    "conversion": "zk-sales",
    "payment": "zk-pay",
    "logistics": "zk-logistics",
    "learning_plan": "zk-learning"
}


def get_agent(intent: str) -> Optional[BaseAgent]:
    """根据意图获取对应的智能体"""
    return AGENTS.get(intent)


def get_agent_by_id(agent_id: str) -> Optional[BaseAgent]:
    """根据智能体ID获取智能体"""
    for intent, aid in AGENT_ID_MAP.items():
        if aid == agent_id:
            return AGENTS.get(intent)
    return None


def list_all_agents() -> list:
    """列出所有智能体"""
    return [
        {
            "id": AGENT_ID_MAP[intent],
            "intent": intent,
            "name": agent.name,
            "role": agent.role,
            "description": agent.description
        }
        for intent, agent in AGENTS.items()
    ]
