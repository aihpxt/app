"""
意图识别和分派系统
根据用户输入识别意图并分派给对应的智能体
"""

import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

# 动态导入，避免循环导入
def get_agent(intent: str):
    from .specialists import get_agent as _get_agent
    return _get_agent(intent)

def get_AGENTS():
    from .specialists import AGENTS
    return AGENTS

logger = logging.getLogger(__name__)


class IntentDispatcher:
    """意图识别和分派器"""
    
    def __init__(self):
        # 意图-关键词映射表
        self.intent_keywords = {
            "control_center": {
                "keywords": [
                    "中考", "择校", "云南中考", "文山中考", "丘北",
                    "怎么选学校", "志愿", "分数", "高中", "初中",
                    "升学", "考高中", "上高中", "选学校", "学校推荐",
                    "未央", "未央中学", "文山州一中", "丘北中学", "小升初",
                    "九年级", "9年级", "初三", "六年级", "小六"
                ],
                "priority": 0,
                "agent_name": "总控智能体",
                "description": "处理中考择校相关咨询"
            },
            "website_issue": {
                "keywords": [
                    "网站打不开", "按钮没用", "表单失效", "加载慢",
                    "代码", "异常", "错误", "链接", "404", "500",
                    "无法访问", "崩溃", "白屏", "卡顿", "bug",
                    "页面", "显示", "跳转", "登录不上"
                ],
                "priority": 1,
                "agent_name": "网络开发工程师",
                "description": "处理网站技术问题、代码错误、系统异常"
            },
            "design": {
                "keywords": [
                    "海报", "设计", "封面", "排版", "图片",
                    "配色", "头像", "界面", "宣传图", "物料",
                    "UI", "美化", "字体", "logo", "图标",
                    "banner", "视觉", "风格", "布局", "样式"
                ],
                "priority": 2,
                "agent_name": "UI美工",
                "description": "处理海报设计、界面美化、图片处理"
            },
            "info_query": {
                "keywords": [
                    "政策", "分数线", "学校信息", "真假", "是否正规",
                    "数据", "更新", "录取", "招生", "排名",
                    "录取率", "一本率", "本科率", "升学率", "师资",
                    "学费", "地址", "电话", "特色", "优势"
                ],
                "priority": 3,
                "agent_name": "信息获取与审核",
                "description": "提供政策解读、学校信息查询、分数线查询"
            },
            "marketing": {
                "keywords": [
                    "推广", "引流", "文案", "公众号", "抖音",
                    "小红书", "宣传", "怎么招人", "营销", "广告",
                    "投放", "获客", "曝光", "品牌", "知名度",
                    "影响力", "传播", "活动", "策划", "运营"
                ],
                "priority": 4,
                "agent_name": "市场品宣与推广",
                "description": "处理市场推广、文案策划、引流宣传"
            },
            "out_province": {
                "keywords": [
                    "贵州", "四川", "广西", "重庆", "外省",
                    "外地", "其他省", "省外", "异地", "跨省",
                    "西藏"
                ],
                "priority": 5,
                "agent_name": "外省市场拓展专员",
                "description": "处理贵州、四川、广西等外省市场拓展"
            },
            "finance": {
                "keywords": [
                    "多少钱", "费用", "收费", "报价", "套餐",
                    "价格", "优惠", "发票", "学费", "成本",
                    "预算", "折扣", "便宜", "贵", "免费",
                    "付费", "退款", "退费", "报销"
                ],
                "priority": 6,
                "agent_name": "财务",
                "description": "处理费用咨询、价格查询、收费标准"
            },
            "legal": {
                "keywords": [
                    "合同", "协议", "保证", "录取", "承诺",
                    "纠纷", "退费", "合法", "隐私", "维权",
                    "退款", "赔偿", "违约", "条款", "法律",
                    "律师", "起诉", "投诉", "举报", "违规", "违法"
                ],
                "priority": 7,
                "agent_name": "法务合规",
                "description": "处理合同审核、法律咨询、纠纷处理"
            },
            "conversion": {
                "keywords": [
                    "怎么报名", "如何预约", "开放日", "什么时候报名",
                    "名额", "报名", "预约", "登记", "咨询",
                    "意向", "留资", "留电话", "加微信", "联系",
                    "想上", "想去", "考虑", "感兴趣", "了解一下"
                ],
                "priority": 8,
                "agent_name": "促单转化专员",
                "description": "处理报名咨询、预约服务、开放日安排"
            },
            "payment": {
                "keywords": [
                    "缴费", "支付", "交钱", "报名成功", "订单",
                    "怎么付款", "付款", "转账", "定金", "押金",
                    "全款", "分期", "刷卡", "扫码", "微信",
                    "支付宝", "银行", "对公", "个人账户"
                ],
                "priority": 9,
                "agent_name": "缴费办理专员",
                "description": "处理缴费办理、支付处理、订单查询"
            },
            "logistics": {
                "keywords": [
                    "参观", "看校", "怎么走", "停车", "食堂",
                    "宿舍", "路线", "接待", "开放日集合", "交通",
                    "地铁", "公交", "开车", "导航", "地址",
                    "位置", "在哪", "多远", "多久", "时间",
                    "住宿", "吃饭", "餐饮", "周边", "附近"
                ],
                "priority": 10,
                "agent_name": "后勤保障服务",
                "description": "处理参观接待、交通指引、食宿安排"
            },
            "learning_plan": {
                "keywords": [
                    "学习计划", "学习规划", "学习建议", "薄弱科目",
                    "偏科", "时间管理", "学习方法", "学习效率",
                    "学习习惯", "成绩提升", "复习计划", "备考计划",
                    "学习目标", "学习动力", "学习策略", "学习技巧",
                    "物理", "化学", "语文", "数学", "英语", "生物",
                    "历史", "地理", "政治", "道法", "科目", "复习",
                    "备考", "刷题", "做题", "知识点", "考点", "难点",
                    "错题", "练习", "作业", "考试", "测验", "模拟考"
                ],
                "priority": 11,
                "agent_name": "个性化学习计划生成",
                "description": "根据学生情况生成个性化学习计划和学习建议"
            }
        }
        
        # 初始化统计
        self.dispatch_stats = {
            "total_requests": 0,
            "intent_distribution": {},
            "agent_distribution": {}
        }
        
        logger.info("意图分派器初始化完成")
    
    def recognize_intent(self, user_input: str) -> Dict[str, Any]:
        """
        识别用户意图
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            意图识别结果
        """
        user_input_lower = user_input.lower()
        
        # 记录所有匹配到的意图
        matched_intents = []
        
        for intent_key, intent_config in self.intent_keywords.items():
            matched_keywords = []
            
            for keyword in intent_config["keywords"]:
                if keyword in user_input_lower:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                # 计算置信度
                confidence = len(matched_keywords) / len(intent_config["keywords"])
                
                matched_intents.append({
                    "intent": intent_key,
                    "confidence": confidence,
                    "matched_keywords": matched_keywords,
                    "priority": intent_config["priority"],
                    "agent_name": intent_config["agent_name"]
                })
        
        # 如果没有匹配到任何意图，返回默认意图（总控中心）
        if not matched_intents:
            return {
                "intent": "control_center",
                "confidence": 1.0,
                "matched_keywords": [],
                "priority": 0,
                "agent_name": "总控智能体",
                "all_matches": []
            }
        
        # 按优先级和置信度排序
        # 优先级数字越小越优先，置信度越高越优先
        matched_intents.sort(key=lambda x: (x["priority"], -x["confidence"]))
        
        # 返回最佳匹配
        best_match = matched_intents[0]
        best_match["all_matches"] = matched_intents[1:] if len(matched_intents) > 1 else []
        
        return best_match
    
    def dispatch(self, intent_result: Dict[str, Any], user_input: str, 
                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        分派任务到对应的智能体
        
        Args:
            intent_result: 意图识别结果
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            分派结果
        """
        intent = intent_result.get("intent", "control_center")
        
        # 更新统计
        self.dispatch_stats["total_requests"] += 1
        self.dispatch_stats["intent_distribution"][intent] = \
            self.dispatch_stats["intent_distribution"].get(intent, 0) + 1
        
        # 获取对应的智能体
        agent = get_agent(intent)
        
        if agent:
            # 调用智能体处理
            response = agent.handle(user_input, context)
            
            # 更新统计
            self.dispatch_stats["agent_distribution"][agent.name] = \
                self.dispatch_stats["agent_distribution"].get(agent.name, 0) + 1
            
            logger.info(f"任务已分派给 {agent.name}")
            
            return {
                "agent": agent.name,
                "agent_role": agent.role,
                "intent": intent,
                "confidence": intent_result.get("confidence", 0),
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # 如果没有对应的智能体，由总控中心处理
            self.dispatch_stats["agent_distribution"]["总控智能体"] = \
                self.dispatch_stats["agent_distribution"].get("总控智能体", 0) + 1
            
            return {
                "agent": "总控智能体",
                "agent_role": "总调度",
                "intent": intent,
                "confidence": intent_result.get("confidence", 0),
                "response": self._handle_general_qa(user_input, context),
                "timestamp": datetime.now().isoformat()
            }
    
    def _handle_general_qa(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        处理一般性问题
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            回复内容
        """
        return (
            "感谢您的咨询！我是云南中考择校智能服务中心。\n\n"
            "我可以为您提供以下服务：\n"
            "1. 中考政策解读\n"
            "2. 学校信息查询\n"
            "3. 志愿填报建议\n"
            "4. 未央中学报名咨询\n\n"
            "请告诉我您的具体需求，我会为您提供专业、准确的服务。"
        )
    
    def get_dispatch_rules(self) -> List[Dict[str, Any]]:
        """获取分派规则列表"""
        rules = []
        for intent_key, intent_config in self.intent_keywords.items():
            rules.append({
                "intent": intent_key,
                "agent_name": intent_config["agent_name"],
                "description": intent_config["description"],
                "keywords": intent_config["keywords"][:5],  # 只显示前5个关键词
                "priority": intent_config["priority"]
            })
        
        # 按优先级排序
        rules.sort(key=lambda x: x["priority"])
        return rules
    
    def get_stats(self) -> Dict[str, Any]:
        """获取分派统计信息"""
        return {
            "total_requests": self.dispatch_stats["total_requests"],
            "intent_distribution": self.dispatch_stats["intent_distribution"],
            "agent_distribution": self.dispatch_stats["agent_distribution"],
            "available_agents": len(get_AGENTS()) + 1  # +1 for control_center
        }
    
    def reset_stats(self):
        """重置统计信息"""
        self.dispatch_stats = {
            "total_requests": 0,
            "intent_distribution": {},
            "agent_distribution": {}
        }
        logger.info("统计信息已重置")


# 全局分派器实例
dispatcher = IntentDispatcher()


def get_dispatcher() -> IntentDispatcher:
    """获取全局分派器实例"""
    return dispatcher