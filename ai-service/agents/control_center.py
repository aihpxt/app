"""
云南省中考择校总控中心智能体
负责接待用户、识别意图、智能分派、统一回复

身份：云南中考择校智能体公司总经理、总调度中心
职责：统一接待用户、识别意图、智能分派任务、汇总结果、统一回复、监控全流程
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 动态导入，避免循环导入
def get_dispatcher():
    from agents.intent_dispatcher import get_dispatcher as _get_dispatcher
    return _get_dispatcher()

def get_agent_orchestrator():
    from agents.agent_orchestrator import get_agent_orchestrator as _get_agent_orchestrator
    return _get_agent_orchestrator()
from openclaw.llm_service import LLMService
from openclaw.multi_llm_service import generate_with_fallback

logger = logging.getLogger(__name__)


class ControlCenterAgent:
    """
    云南省中考择校总控中心智能体
    
    身份：云南中考择校智能体公司总经理、总调度中心
    职责：统一接待用户、识别意图、智能分派任务、汇总结果、统一回复、监控全流程
    
    调度规则：
    1. 技术问题、网站异常、智能体故障 → 转给【网络开发工程师】
    2. 海报、设计、排版、视觉、头像界面 → 转给【UI美工】
    3. 学校信息、中考政策、分数线、数据更新、内容审核 → 转给【信息获取与审核】
    4. 推广文案、公众号、短视频、本地引流、品牌宣传 → 转给【市场品宣与推广】
    5. 外省咨询、外省政策、拓展外地市场 → 转给【外省市场拓展专员】
    6. 费用、报价、套餐、对账、营收 → 转给【财务】
    7. 合同、合规、风险、承诺限制、隐私、纠纷 → 转给【法务合规】
    8. 高意向家长、逼单、锁客、跟进、活动邀约 → 转给【促单转化专员】
    9. 缴费、报名、收款、订单确认、入学通知 → 转给【缴费办理专员】
    10. 参观、开放日、食宿、交通、停车、接待、物料 → 转给【后勤保障服务】
    11. 常规择校咨询、政策问答 → 自行解答
    
    回复原则：专业、稳重、不夸大、不承诺录取、不保证分数，以云南省本地政策为准
    """
    
    def __init__(self):
        self.name = "云南省中考择校总控中心"
        self.role = "总调度、总经理"
        self.identity = "云南中考择校智能体公司总经理、总调度中心"
        self.welcome_message = (
            "🦞 你好！我是云南中考择校智能服务中心\n\n"
            "我能为你提供：\n"
            "✅ 云南中考政策查询\n"
            "✅ 文山/丘北学校对比\n"
            "✅ 未央中学报名咨询\n"
            "✅ 志愿填报指导\n"
            "✅ 免费看校预约\n\n"
            "请问孩子现在几年级？在哪个城市？"
        )
        self.dispatcher = get_dispatcher()  # 使用全局分派器
        self.agent_orchestrator = get_agent_orchestrator()  # 使用智能体编排器
        self.executor = ThreadPoolExecutor(max_workers=5)  # 线程池
        self.llm_service = LLMService()  # 初始化语言模型服务
        
        # 调度规则说明
        self.dispatch_rules = {
            "website_issue": "技术问题、网站异常、智能体故障 → 网络开发工程师",
            "design": "海报、设计、排版、视觉、头像界面 → UI美工",
            "info_query": "学校信息、中考政策、分数线、数据更新、内容审核 → 信息获取与审核",
            "marketing": "推广文案、公众号、短视频、本地引流、品牌宣传 → 市场品宣与推广",
            "out_province": "外省咨询、外省政策、拓展外地市场 → 外省市场拓展专员",
            "finance": "费用、报价、套餐、对账、营收 → 财务",
            "legal": "合同、合规、风险、承诺限制、隐私、纠纷 → 法务合规",
            "conversion": "高意向家长、逼单、锁客、跟进、活动邀约 → 促单转化专员",
            "payment": "缴费、报名、收款、订单确认、入学通知 → 缴费办理专员",
            "logistics": "参观、开放日、食宿、交通、停车、接待、物料 → 后勤保障服务",
            "control_center": "常规择校咨询、政策问答 → 总控中心自行解答"
        }
        
        # 会话管理
        self.session_store = {}  # 会话存储
        self.session_expiry = 3600  # 会话过期时间（秒）
        self.last_cleanup = time.time()  # 最后清理时间
        self.cleanup_interval = 600  # 清理间隔（秒）
        
        # 性能统计
        self.performance_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time": 0,
            "avg_response_time": 0,
            "max_response_time": 0,
            "min_response_time": float('inf')
        }
        
    def initialize(self):
        """初始化智能体"""
        logger.info(f"{self.name} 智能体已初始化")
        logger.info(f"身份: {self.identity}")
        logger.info(f"调度规则数量: {len(self.dispatch_rules)}")
        logger.info("智能体编排器集成成功")
    
    def greet(self) -> str:
        """欢迎语"""
        return self.welcome_message
    
    def process(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理用户输入 - 总调度中心核心流程
        
        流程：
        1. 清理过期会话
        2. 检查会话历史，判断是否为上下文相关回复
        3. 识别用户意图
        4. 根据调度规则分派给对应智能体
        5. 汇总处理结果
        6. 统一格式化回复
        7. 记录用户行为和会话状态
        8. 更新性能统计
        
        Args:
            user_input: 用户输入
            context: 上下文信息
            
        Returns:
            处理结果
        """
        start_time = time.time()
        
        try:
            # 1. 清理过期会话（异步执行，不阻塞主流程）
            self.executor.submit(self._cleanup_expired_sessions)
            
            # 2. 获取会话历史，检查是否为上下文相关回复
            session_id = context.get("session_id") if context else None
            previous_context = None
            if session_id and session_id in self.session_store:
                previous_context = self.session_store[session_id]
                logger.info(f"找到历史会话: {session_id}")
            
            # 3. 检查是否为简短肯定回复（需要上下文理解）
            user_input_lower = user_input.lower().strip()
            is_context_response = False
            if previous_context:
                # 检查是否为简短肯定回复
                if user_input_lower in ["需要", "是的", "好的", "想", "要", "可以", "嗯", "对", "是", "了解", "咨询"]:
                    is_context_response = True
                    logger.info(f"检测到上下文相关回复: {user_input}")
                # 检查是否为对上一轮问题的直接回答
                elif previous_context.get("last_intent") in ["info_query", "control_center"]:
                    # 如果上一轮是信息查询，检查当前输入是否包含年级、城市等信息
                    if any(word in user_input_lower for word in ["年级", "9年级", "九年级", "初三", "六年级", "小六", "小升初"]):
                        is_context_response = True
                    elif any(word in user_input_lower for word in ["文山", "丘北", "昆明", "曲靖", "玉溪", "城市"]):
                        is_context_response = True
            
            # 4. 识别意图（使用分派器的意图识别）
            intent_result = self.dispatcher.recognize_intent(user_input)
            intent = intent_result.get("intent", "control_center")
            
            # 5. 如果是上下文相关回复，调整意图
            if is_context_response and previous_context:
                # 根据上一轮的意图和内容决定当前回复
                last_answer = previous_context.get("last_answer", "")
                if "未央" in last_answer or "丘北" in last_answer:
                    # 如果上一轮提到了未央中学，用户的简短回复应该得到详细信息
                    intent = "info_query"  # 强制使用信息查询智能体
            
            # 6. 记录调度决策
            logger.info(f"意图识别: {intent} -> {self.dispatch_rules.get(intent, '总控中心')}")
            
            # 7. 并行执行智能分派和技能检查
            future_dispatch = self.executor.submit(self.dispatcher.dispatch, intent_result, user_input, context)
            
            # 8. 等待分派结果
            dispatch_result = future_dispatch.result()
            
            # 9. 如果是上下文相关回复，生成更智能的回复
            if is_context_response and previous_context:
                response = self._generate_context_response(previous_context, user_input)
            else:
                # 生成统一回复（不等待技能检查结果，提高响应速度）
                response = self._generate_response(dispatch_result, {})
            
            # 7. 记录日志和监控
            processing_time = time.time() - start_time
            logger.info(
                f"处理完成 - 意图: {intent}, "
                f"分派: {dispatch_result['agent']}, "
                f"耗时: {processing_time:.2f}秒"
            )
            
            # 8. 记录用户行为（异步执行，不阻塞主流程）
            if context and context.get("user_id"):
                self.executor.submit(self._record_user_activity, context["user_id"], intent, dispatch_result, processing_time)
            
            # 9. 更新会话状态
            session_id = context.get("session_id") if context else None
            if not session_id:
                session_id = hashlib.md5((user_input + str(time.time())).encode('utf-8')).hexdigest()
            
            session_data = {
                "last_question": user_input,
                "last_answer": response,
                "last_intent": intent,
                "entities": intent_result.get("entities", {}),
                "skills_used": [],
                "timestamp": time.time()
            }
            
            # 存储会话状态
            self.session_store[session_id] = session_data
            
            if context:
                context["session_id"] = session_id
                context["session_data"] = session_data
            
            # 10. 更新性能统计
            self._update_performance_stats(processing_time, True)
            
            return {
                "success": True,
                "response": response,
                "intent": intent_result,
                "dispatch": dispatch_result,
                "processing_time": processing_time,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"处理失败: {e}")
            processing_time = time.time() - start_time
            self._update_performance_stats(processing_time, False)
            return {
                "success": False,
                "response": "抱歉，系统处理出现异常，请稍后重试。",
                "error": str(e),
                "processing_time": processing_time
            }
    
    def _record_user_activity(self, user_id: str, intent: str, dispatch_result: Dict, processing_time: float):
        """
        记录用户行为（异步执行）
        
        Args:
            user_id: 用户ID
            intent: 意图
            dispatch_result: 分派结果
            processing_time: 处理时间
        """
        try:
            from core.user_activity import record_user_activity
            record_user_activity(
                user_id,
                "chat_interaction",
                {
                    "intent": intent,
                    "agent": dispatch_result.get("agent", "总控中心"),
                    "processing_time": processing_time,
                    "skills_used": []
                }
            )
        except Exception as e:
            logger.warning(f"记录用户行为失败: {e}")
    
    def _generate_response(self, dispatch_result: Dict, orchestrator_result: Dict) -> str:
        """
        生成最终回复 - 统一格式化输出

        Args:
            dispatch_result: 分派结果
            orchestrator_result: 编排器结果

        Returns:
            最终回复
        """
        agent = dispatch_result.get("agent", "总控中心")
        response = dispatch_result.get("response", "")
        
        # 先使用LLMService增强回复
        try:
            # 构建提示词
            prompt = f"作为云南中考择校智能服务中心，针对以下问题生成专业、友好的回复：\n\n{response}"
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
        return response
    
    def _generate_context_response(self, previous_context: Dict, user_input: str) -> str:
        """
        根据上下文生成智能回复
        
        Args:
            previous_context: 上一轮会话上下文
            user_input: 当前用户输入
            
        Returns:
            智能回复内容
        """
        user_input_lower = user_input.lower().strip()
        last_answer = previous_context.get("last_answer", "")
        last_intent = previous_context.get("last_intent", "")
        
        # 检查是否提到未央中学
        if "未央" in last_answer or "丘北" in last_answer:
            # 用户的简短回复应该得到未央中学的详细信息
            if user_input_lower in ["需要", "是的", "好的", "想", "要", "可以", "嗯", "对", "是"]:
                # 返回详细的未央中学招生信息
                return (
                    "📋 丘北未央中学2026年招生详情\n\n"
                    "【高中部招生】\n"
                    "• 招生计划：600人（鹏程班50人、英才班150人、实验班400人）\n"
                    "• 录取方式：中考成绩+综合评估\n"
                    "• 分数线参考：420分以上可报名，620分以上公费\n\n"
                    "【学费标准】（按中考裸分）\n"
                    "• 620分以上：学费0元 + 住宿费0元\n"
                    "• 600-619分：学费800元 + 住宿费600元\n"
                    "• 570-599分：学费2000元 + 住宿费600元\n"
                    "• 540-569分：学费2500元 + 住宿费600元\n"
                    "• 510-539分：学费3000元 + 住宿费600元\n"
                    "• 480-509分：学费3500元 + 住宿费600元\n"
                    "• 450-479分：学费4000元 + 住宿费600元\n"
                    "• 420-449分：学费5000元 + 住宿费600元\n\n"
                    "【报名方式】\n"
                    "携带户口本、中考成绩单到学校招生办现场办理\n\n"
                    "【联系方式】\n"
                    "招生热线：0876-4122666\n"
                    "地址：丘北县锦屏镇文秀路129号（弘毅楼一楼招生办）"
                )
            
            # 检查是否包含年级信息
            if any(word in user_input_lower for word in ["9年级", "九年级", "初三"]):
                # 用户提到了9年级，应该返回高中部招生信息
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
            
            # 检查是否包含城市信息
            if any(word in user_input_lower for word in ["文山", "文山市"]):
                # 用户提到了文山市，结合之前的对话，应该返回更详细的信息
                return (
                    "📍 文山市学生报考丘北未央中学指南\n\n"
                    "【学校位置】\n"
                    "丘北县锦屏镇文秀路129号，距文山市约1小时车程\n\n"
                    "【招生范围】\n"
                    "面向文山州全州招生，文山市学生可正常报考\n\n"
                    "【交通安排】\n"
                    "• 自驾：约1小时车程，学校提供免费停车位\n"
                    "• 班车：周末提供文山-丘北接送服务（需提前预约）\n\n"
                    "【报考优势】\n"
                    "• 州一中直管，教学管理同步\n"
                    "• 全封闭管理，适合需要严格管束的学生\n"
                    "• 与州一中本部共享师资和教学资源\n\n"
                    "【报名方式】\n"
                    "携带户口本、中考成绩单到学校招生办现场办理"
                )
        
        # 默认返回通用回复
        return (
            "感谢您的回复！根据您的情况，\n\n"
            "如果您想了解未央中学的详细信息，请告诉我：\n"
            "1. 孩子现在几年级？\n"
            "2. 您最关心哪些方面？（招生条件/学费/奖学金/校园环境）\n\n"
            "我会为您提供更精准的信息。"
        )
    
    def _cleanup_expired_sessions(self):
        """清理过期会话"""
        current_time = time.time()
        if current_time - self.last_cleanup >= self.cleanup_interval:
            expired_sessions = [
                session_id for session_id, session_data in self.session_store.items()
                if current_time - session_data["timestamp"] >= self.session_expiry
            ]
            for session_id in expired_sessions:
                del self.session_store[session_id]
            self.last_cleanup = current_time
            if expired_sessions:
                logger.info(f"清理了 {len(expired_sessions)} 个过期会话")
    
    def _update_performance_stats(self, processing_time: float, success: bool):
        """更新性能统计"""
        self.performance_stats["total_requests"] += 1
        self.performance_stats["total_response_time"] += processing_time
        self.performance_stats["avg_response_time"] = (
            self.performance_stats["total_response_time"] / self.performance_stats["total_requests"]
        )
        self.performance_stats["max_response_time"] = max(
            self.performance_stats["max_response_time"], processing_time
        )
        self.performance_stats["min_response_time"] = min(
            self.performance_stats["min_response_time"], processing_time
        )
        if success:
            self.performance_stats["successful_requests"] += 1
        else:
            self.performance_stats["failed_requests"] += 1
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体完整信息"""
        return {
            "name": self.name,
            "role": self.role,
            "identity": self.identity,
            "welcome_message": self.welcome_message,
            "dispatch_rules": self.dispatch_rules,
            "capabilities": [
                "统一接待用户",
                "智能意图识别",
                "任务智能分派",
                "结果汇总回复",
                "全流程监控",
                "智能体协调",
                "技能调用"
            ],
            "reply_principles": [
                "专业、稳重",
                "不夸大、不承诺录取、不保证分数",
                "以云南省本地政策为准"
            ],
            "stats": {
                "dispatch": self.dispatcher.get_stats(),
                "performance": self.performance_stats,
                "sessions": {
                    "active": len(self.session_store),
                    "expiry": self.session_expiry
                }
            }
        }
    
    def get_dispatch_stats(self) -> Dict[str, Any]:
        """获取分派统计"""
        return self.dispatcher.get_stats()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return self.performance_stats
    
    def get_session_stats(self) -> Dict[str, Any]:
        """获取会话统计"""
        return {
            "active_sessions": len(self.session_store),
            "session_expiry": self.session_expiry,
            "last_cleanup": self.last_cleanup
        }
    
    def reset_stats(self):
        """重置统计"""
        self.dispatcher.reset_stats()
        self.performance_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time": 0,
            "avg_response_time": 0,
            "max_response_time": 0,
            "min_response_time": float('inf')
        }
        logger.info("统计信息已重置")
    
    def shutdown(self):
        """关闭线程池"""
        self.executor.shutdown(wait=False)
        logger.info("ControlCenterAgent shutdown")


# 全局总控中心实例
control_center = ControlCenterAgent()


def get_control_center() -> ControlCenterAgent:
    """获取全局总控中心实例"""
    return control_center

def shutdown_control_center():
    """关闭总控中心"""
    global control_center
    if control_center:
        control_center.shutdown()
        control_center = None