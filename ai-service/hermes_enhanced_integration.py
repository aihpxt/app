"""
Hermes 增强集成模块
深度集成Hermes高级AI能力到智能体系统
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import requests
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class EnhancementLevel(Enum):
    """Hermes增强级别"""
    NONE = 0           # 无增强
    BASIC = 1          # 基础增强（情感分析）
    STANDARD = 2       # 标准增强（情感+意图+洞察）
    FULL = 3           # 完全增强（所有功能）


@dataclass
class HermesEnhancement:
    """Hermes增强结果"""
    emotion_analysis: Optional[Dict] = None      # 情感分析结果
    intent_classification: Optional[Dict] = None # 意图分类结果
    user_profile: Optional[Dict] = None          # 用户画像
    conversation_state: Optional[Dict] = None    # 会话状态
    insights: Optional[Dict] = None             # 洞察结果
    rewritten_input: Optional[str] = None        # 重写后的输入
    recommended_skills: Optional[List[str]] = None # 推荐的技能
    followup_suggestions: Optional[List[str]] = None # 跟进建议


class HermesIntegration:
    """Hermes增强集成器"""

    def __init__(self, base_url: str = "http://localhost:8888", timeout: float = 2.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.available = False
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._health_check()

    def _health_check(self) -> bool:
        """健康检查"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            if response.status_code == 200:
                self.available = True
                logger.info("Hermes服务可用")
                return True
        except Exception as e:
            logger.warning(f"Hermes服务不可用: {e}")
            self.available = False
            return False

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.available

    def analyze_emotion(self, user_input: str, session_id: str = None) -> Optional[Dict]:
        """分析用户情感"""
        if not self.available:
            return None

        try:
            response = requests.post(
                f"{self.base_url}/v1/analyze",
                json={
                    "data": {
                        "input": user_input,
                        "session_id": session_id,
                        "analysis_type": "emotion"
                    }
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"情感分析失败: {e}")
        return None

    def classify_intent(self, user_input: str) -> Optional[Dict]:
        """分类用户意图"""
        if not self.available:
            return None

        try:
            response = requests.post(
                f"{self.base_url}/v1/classify",
                json={
                    "data": {
                        "input": user_input,
                        "classification_type": "intent"
                    }
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"意图分类失败: {e}")
        return None

    def track_conversation(
        self,
        session_id: str,
        user_input: str,
        context: Dict = None
    ) -> Optional[Dict]:
        """跟踪会话状态"""
        if not self.available or not session_id:
            return None

        try:
            response = requests.post(
                f"{self.base_url}/v1/track",
                json={
                    "data": {
                        "session_id": session_id,
                        "input": user_input,
                        "context": context or {}
                    }
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"会话跟踪失败: {e}")
        return None

    def update_profile(
        self,
        session_id: str,
        user_input: str,
        context: Dict = None
    ) -> Optional[Dict]:
        """更新用户画像"""
        if not self.available or not session_id:
            return None

        try:
            response = requests.post(
                f"{self.base_url}/v1/profile",
                json={
                    "data": {
                        "session_id": session_id,
                        "input": user_input,
                        "context": context or {}
                    }
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"用户画像更新失败: {e}")
        return None

    def generate_insights(
        self,
        session_id: str,
        user_input: str,
        context: Dict = None
    ) -> Optional[Dict]:
        """生成洞察"""
        if not self.available:
            return None

        try:
            response = requests.post(
                f"{self.base_url}/v1/insights",
                json={
                    "data": {
                        "session_id": session_id,
                        "input": user_input,
                        "context": context or {}
                    }
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"洞察生成失败: {e}")
        return None

    def enhance_response(
        self,
        base_response: str,
        enhancement: HermesEnhancement
    ) -> str:
        """基于Hermes增强结果优化响应"""
        if not enhancement or not enhancement.followup_suggestions:
            return base_response

        # 添加跟进建议
        suggestions = enhancement.followup_suggestions[:2]  # 最多添加2个建议
        if suggestions:
            response = base_response.rstrip()
            if not response.endswith(("。", "！", "？")):
                response += "。"
            response += "\n\n💡 您可能还想了解：\n"
            for i, suggestion in enumerate(suggestions, 1):
                response += f"{i}. {suggestion}\n"
            return response

        return base_response

    def enhance_with_tone(
        self,
        base_response: str,
        emotion: Dict
    ) -> str:
        """根据情感调整响应语气"""
        if not emotion:
            return base_response

        emotion_type = emotion.get('emotion', '中性')
        urgency = emotion.get('urgency', '中')

        # 焦虑情绪：添加安慰和鼓励
        if emotion_type == '焦虑':
            if "别担心" not in base_response and "可以" not in base_response:
                base_response = "别担心，" + base_response

        # 期待情绪：确认用户需求
        elif emotion_type == '期待':
            if not base_response.endswith("吗？"):
                base_response += "\n请问您还有什么想了解的吗？"

        # 困惑情绪：简化表达
        elif emotion_type == '困惑':
            # 确保表达清晰易懂
            base_response = base_response.replace("。", "。\n")

        return base_response

    def get_session_report(self, session_id: str) -> Optional[Dict]:
        """获取会话报告"""
        if not self.available or not session_id:
            return None

        try:
            response = requests.post(
                f"{self.base_url}/v1/session-report",
                json={"data": {"session_id": session_id}},
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"会话报告获取失败: {e}")
        return None

    def send_feedback(
        self,
        session_id: str,
        feedback_type: str,
        score: float = 0.5,
        details: Dict = None
    ) -> bool:
        """发送反馈"""
        if not self.available:
            return False

        try:
            response = requests.post(
                f"{self.base_url}/v1/feedback",
                json={
                    "data": {
                        "session_id": session_id,
                        "type": feedback_type,
                        "score": score,
                        "details": details or {}
                    }
                },
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"反馈发送失败: {e}")
            return False

    def get_recommended_skills(self, user_input: str) -> List[str]:
        """获取推荐技能"""
        if not self.available:
            return []

        try:
            response = requests.post(
                f"{self.base_url}/v1/agent",
                json={
                    "data": {
                        "input": user_input,
                        "type": "dispatch"
                    }
                },
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('recommended_skills', [])
        except Exception as e:
            logger.warning(f"技能推荐失败: {e}")
        return []

    def complete_enhancement(
        self,
        session_id: str,
        user_input: str,
        base_response: str,
        context: Dict = None,
        level: EnhancementLevel = EnhancementLevel.STANDARD
    ) -> tuple:
        """
        完整的Hermes增强流程

        Args:
            session_id: 会话ID
            user_input: 用户输入
            base_response: 基础响应
            context: 上下文
            level: 增强级别

        Returns:
            (增强后的响应, 增强结果对象)
        """
        enhancement = HermesEnhancement()

        # 1. 情感分析（所有级别）
        if level.value >= EnhancementLevel.BASIC.value:
            emotion_result = self.analyze_emotion(user_input, session_id)
            if emotion_result:
                enhancement.emotion_analysis = emotion_result.get('data', {})

        # 2. 标准增强：意图分类 + 会话跟踪 + 用户画像
        if level.value >= EnhancementLevel.STANDARD.value:
            # 并行执行多个请求
            intent_result = self.classify_intent(user_input)
            if intent_result:
                enhancement.intent_classification = intent_result.get('data', {})

            track_result = self.track_conversation(session_id, user_input, context)
            if track_result:
                enhancement.conversation_state = track_result.get('data', {})

            profile_result = self.update_profile(session_id, user_input, context)
            if profile_result:
                enhancement.user_profile = profile_result.get('data', {})

        # 3. 完全增强：洞察生成 + 技能推荐
        if level.value >= EnhancementLevel.FULL.value:
            insights_result = self.generate_insights(session_id, user_input, context)
            if insights_result:
                enhancement.insights = insights_result.get('data', {})
                enhancement.followup_suggestions = enhancement.insights.get('followup_topics', [])

            enhancement.recommended_skills = self.get_recommended_skills(user_input)

        # 4. 根据情感调整响应
        if enhancement.emotion_analysis:
            base_response = self.enhance_with_tone(
                base_response,
                enhancement.emotion_analysis
            )

        # 5. 添加跟进建议
        if enhancement.followup_suggestions:
            base_response = self.enhance_response(base_response, enhancement)

        return base_response, enhancement


class HermesLocalFallback:
    """Hermes本地降级实现"""

    @staticmethod
    def analyze_emotion_local(user_input: str) -> Dict:
        """本地情感分析"""
        user_lower = user_input.lower()

        # 关键词检测
        anxiety_keywords = ["怎么办", "担心", "焦虑", "考不上", "压力"]
        positive_keywords = ["谢谢", "很好", "不错", "太好了"]
        expect_keywords = ["多少", "推荐", "可以", "能上"]

        if any(kw in user_lower for kw in anxiety_keywords):
            return {
                "emotion": "焦虑",
                "urgency": "高",
                "sentiment": "焦虑",
                "needs_support": True,
                "confidence": 0.8
            }
        elif any(kw in user_lower for kw in positive_keywords):
            return {
                "emotion": "积极",
                "urgency": "低",
                "sentiment": "满意",
                "needs_support": False,
                "confidence": 0.8
            }
        elif any(kw in user_lower for kw in expect_keywords):
            return {
                "emotion": "期待",
                "urgency": "中",
                "sentiment": "其他",
                "needs_support": True,
                "confidence": 0.7
            }

        return {
            "emotion": "中性",
            "urgency": "中",
            "sentiment": "其他",
            "needs_support": False,
            "confidence": 0.5
        }

    @staticmethod
    def classify_intent_local(user_input: str) -> Dict:
        """本地意图分类"""
        user_lower = user_input.lower()

        # 关键词模式匹配
        patterns = {
            "school_inquiry": ["学校", "高中", "中学", "录取", "分数线"],
            "policy_inquiry": ["政策", "中考", "志愿", "填报", "录取规则"],
            "fee_inquiry": ["学费", "费用", "收费", "多少钱"],
            "score_recommendation": ["分", "分数", "推荐", "能上"],
            "general_question": []
        }

        for intent, keywords in patterns.items():
            if not keywords:
                continue
            if any(kw in user_lower for kw in keywords):
                return {
                    "intent": intent,
                    "name": intent.replace("_", " "),
                    "confidence": 0.8
                }

        return {
            "intent": "general_inquiry",
            "name": "一般咨询",
            "confidence": 0.5
        }

    @staticmethod
    def generate_insights_local(
        user_input: str,
        user_profile: Dict = None,
        conversation_history: List = None
    ) -> Dict:
        """本地洞察生成"""
        insights = {
            "missing_info": [],
            "followup_topics": [],
            "emotion_signal": "neutral",
            "urgency": "medium"
        }

        profile = user_profile or {}
        user_lower = user_input.lower()

        # 检查缺失信息
        if not profile.get('score'):
            insights["missing_info"].append("考生成绩")
        if not profile.get('location'):
            insights["missing_info"].append("所在地区")
        if not profile.get('grade'):
            insights["missing_info"].append("年级")

        # 生成跟进话题
        if "学校" in user_lower or "高中" in user_lower:
            if not profile.get('score'):
                insights["followup_topics"].append("请问您孩子的中考成绩大概是多少？")
        elif "志愿" in user_lower or "填报" in user_lower:
            if not profile.get('score'):
                insights["followup_topics"].append("需要知道孩子的分数才能给出更好的建议")

        # 情感信号
        emotion_result = HermesLocalFallback.analyze_emotion_local(user_input)
        insights["emotion_signal"] = emotion_result.get("emotion", "neutral")
        insights["urgency"] = emotion_result.get("urgency", "medium")

        return insights


class HermesManager:
    """Hermes管理器 - 统一管理Hermes服务"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, base_url: str = "http://localhost:8888"):
        if not hasattr(self, '_initialized'):
            self._integration = HermesIntegration(base_url)
            self._fallback = HermesLocalFallback()
            self._initialized = True
            logger.info("Hermes管理器初始化完成")

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self._integration.is_available()

    def enhance(
        self,
        session_id: str,
        user_input: str,
        base_response: str,
        context: Dict = None,
        level: EnhancementLevel = EnhancementLevel.STANDARD
    ) -> tuple:
        """
        增强响应

        Returns:
            (增强后的响应, 增强结果)
        """
        if self._integration.is_available():
            return self._integration.complete_enhancement(
                session_id, user_input, base_response, context, level
            )

        # 降级到本地实现
        enhancement = HermesEnhancement()
        emotion = self._fallback.analyze_emotion_local(user_input)
        enhancement.emotion_analysis = emotion

        # 根据情感调整响应
        enhanced_response = base_response
        if emotion.get('emotion') == '焦虑':
            enhanced_response = "别担心，" + enhanced_response

        return enhanced_response, enhancement

    def analyze_emotion(self, user_input: str, session_id: str = None) -> Dict:
        """情感分析"""
        if self._integration.is_available():
            result = self._integration.analyze_emotion(user_input, session_id)
            if result:
                return result.get('data', {})
        return self._fallback.analyze_emotion_local(user_input)

    def classify_intent(self, user_input: str) -> Dict:
        """意图分类"""
        if self._integration.is_available():
            result = self._integration.classify_intent(user_input)
            if result:
                return result.get('data', {})
        return self._fallback.classify_intent_local(user_input)

    def generate_insights(
        self,
        user_input: str,
        user_profile: Dict = None,
        conversation_history: List = None
    ) -> Dict:
        """生成洞察"""
        if self._integration.is_available():
            result = self._integration.generate_insights(
                session_id="temp",
                user_input=user_input,
                context={"profile": user_profile, "history": conversation_history}
            )
            if result:
                return result.get('data', {})
        return self._fallback.generate_insights_local(
            user_input, user_profile, conversation_history
        )

    def get_session_report(self, session_id: str) -> Optional[Dict]:
        """获取会话报告"""
        return self._integration.get_session_report(session_id)

    def send_feedback(
        self,
        session_id: str,
        feedback_type: str,
        score: float = 0.5,
        details: Dict = None
    ) -> bool:
        """发送反馈"""
        return self._integration.send_feedback(session_id, feedback_type, score, details)


# 全局实例
hermes_manager = HermesManager()


def get_hermes_manager() -> HermesManager:
    """获取Hermes管理器实例"""
    return hermes_manager
