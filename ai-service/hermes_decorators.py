"""
Hermes增强装饰器
用于简化智能体函数的Hermes增强集成
"""

import functools
import logging
from typing import Callable, Optional, Dict, List, Any
from hermes_enhanced_integration import (
    HermesManager,
    HermesEnhancement,
    EnhancementLevel,
    get_hermes_manager
)

logger = logging.getLogger(__name__)


def hermes_enhanced(
    level: EnhancementLevel = EnhancementLevel.STANDARD,
    session_id_param: str = "session_id",
    user_input_param: str = "user_input",
    response_param: str = "response"
):
    """
    Hermes增强装饰器

    用法:
    @hermes_enhanced(level=EnhancementLevel.STANDARD)
    def handle_message(session_id, user_input, response):
        # 处理消息
        return response

    @hermes_enhanced(level=EnhancementLevel.FULL, session_id_param="sid")
    def my_agent(sid, user_input, context):
        # ...
        return response
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取Hermes管理器
            hermes = get_hermes_manager()

            # 提取参数
            session_id = kwargs.get(session_id_param)
            if session_id is None:
                # 尝试从位置参数获取
                import inspect
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if session_id_param in params:
                    idx = params.index(session_id_param)
                    if idx < len(args):
                        session_id = args[idx]

            user_input = kwargs.get(user_input_param)
            if user_input is None:
                import inspect
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if user_input_param in params:
                    idx = params.index(user_input_param)
                    if idx < len(args):
                        user_input = args[idx]

            # 调用原函数获取响应
            response = func(*args, **kwargs)

            # 如果响应不是字符串，直接返回
            if not isinstance(response, str):
                return response

            # 提取上下文参数
            context = kwargs.get('context', {})
            if context is None:
                context = {}

            # 应用Hermes增强
            if hermes.is_available():
                try:
                    enhanced_response, enhancement = hermes.enhance(
                        session_id=session_id,
                        user_input=user_input or "",
                        base_response=response,
                        context=context,
                        level=level
                    )
                    # 将增强结果添加到context中
                    kwargs['context'] = context
                    kwargs['_hermes_enhancement'] = enhancement
                    return enhanced_response
                except Exception as e:
                    logger.warning(f"Hermes增强失败: {e}")

            return response

        return wrapper
    return decorator


def track_conversation(func: Callable) -> Callable:
    """
    会话跟踪装饰器
    自动跟踪对话状态并更新用户画像
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        hermes = get_hermes_manager()

        # 提取session_id和user_input
        session_id = kwargs.get('session_id') or kwargs.get('sid')
        user_input = kwargs.get('user_input') or kwargs.get('message')
        context = kwargs.get('context', {})

        # 调用原函数
        result = func(*args, **kwargs)

        # 异步更新会话状态
        if session_id and hermes.is_available():
            try:
                hermes._integration.executor.submit(
                    hermes._integration.track_conversation,
                    session_id, user_input, context
                )
            except Exception as e:
                logger.warning(f"会话跟踪失败: {e}")

        return result

    return wrapper


def analyze_and_enhance(func: Callable) -> Callable:
    """
    分析并增强装饰器
    在函数执行前后进行分析和增强
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        hermes = get_hermes_manager()

        # 提取参数
        session_id = kwargs.get('session_id')
        user_input = kwargs.get('user_input')
        response = kwargs.get('response')

        # 前置分析
        emotion = None
        intent = None
        if hermes.is_available():
            emotion = hermes.analyze_emotion(user_input or "", session_id)
            intent = hermes.classify_intent(user_input or "")

        # 将分析结果添加到kwargs
        kwargs['_emotion'] = emotion
        kwargs['_intent'] = intent

        # 调用原函数
        result = func(*args, **kwargs)

        # 后置增强
        if isinstance(result, str) and hermes.is_available():
            enhanced, _ = hermes.enhance(
                session_id=session_id,
                user_input=user_input or "",
                base_response=result,
                context=kwargs.get('context', {}),
                level=EnhancementLevel.BASIC
            )
            return enhanced

        return result

    return wrapper


class HermesAware:
    """
    Hermes感知的基类
    用于创建具有Hermes增强功能的类
    """

    def __init__(self):
        self._hermes = get_hermes_manager()

    @property
    def hermes_available(self) -> bool:
        """检查Hermes是否可用"""
        return self._hermes.is_available()

    def enhance_response(
        self,
        session_id: str,
        user_input: str,
        response: str,
        context: Dict = None,
        level: EnhancementLevel = EnhancementLevel.STANDARD
    ) -> str:
        """增强响应"""
        if not self._hermes.is_available():
            return response

        enhanced, _ = self._hermes.enhance(
            session_id=session_id,
            user_input=user_input,
            base_response=response,
            context=context or {},
            level=level
        )
        return enhanced

    def analyze_emotion(self, user_input: str, session_id: str = None) -> Dict:
        """分析情感"""
        return self._hermes.analyze_emotion(user_input, session_id)

    def classify_intent(self, user_input: str) -> Dict:
        """分类意图"""
        return self._hermes.classify_intent(user_input)

    def generate_insights(
        self,
        user_input: str,
        user_profile: Dict = None,
        conversation_history: List = None
    ) -> Dict:
        """生成洞察"""
        return self._hermes.generate_insights(user_input, user_profile, conversation_history)

    def send_feedback(
        self,
        session_id: str,
        feedback_type: str,
        score: float = 0.5,
        details: Dict = None
    ) -> bool:
        """发送反馈"""
        return self._hermes.send_feedback(session_id, feedback_type, score, details)


def with_hermes_tracking(func: Callable) -> Callable:
    """
    带Hermes跟踪的函数包装器

    用法:
    @with_hermes_tracking
    async def handle_message(session_id, message):
        # 自动跟踪会话
        pass
    """
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        hermes = get_hermes_manager()

        session_id = kwargs.get('session_id')
        user_input = kwargs.get('message') or kwargs.get('user_input')

        # 调用原函数
        result = func(*args, **kwargs)

        # 记录答案
        if session_id and hermes.is_available():
            try:
                hermes._integration.executor.submit(
                    hermes._integration._send_record_answer,
                    session_id, str(result)[:500] if result else ""
                )
            except Exception:
                pass

        return result

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        hermes = get_hermes_manager()

        session_id = kwargs.get('session_id')
        user_input = kwargs.get('message') or kwargs.get('user_input')

        # 调用原函数
        result = await func(*args, **kwargs)

        # 记录答案
        if session_id and hermes.is_available():
            try:
                hermes._integration.executor.submit(
                    hermes._integration._send_record_answer,
                    session_id, str(result)[:500] if result else ""
                )
            except Exception:
                pass

        return result

    # 根据原函数类型返回对应的包装器
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def emotion_adaptive(func: Callable) -> Callable:
    """
    情感自适应装饰器
    根据用户情感状态调整响应

    用法:
    @emotion_adaptive
    def generate_response(user_input, context):
        # 生成响应时会自动考虑用户情感
        pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        hermes = get_hermes_manager()

        # 获取用户输入
        user_input = kwargs.get('user_input') or kwargs.get('message')
        session_id = kwargs.get('session_id')

        # 分析情感
        emotion = None
        if hermes.is_available() and user_input:
            emotion = hermes.analyze_emotion(user_input, session_id)

        # 添加到kwargs
        kwargs['_emotion'] = emotion

        # 调用原函数
        result = func(*args, **kwargs)

        # 根据情感调整响应
        if isinstance(result, str) and emotion:
            emotion_type = emotion.get('emotion', '中性')

            # 焦虑：添加安慰
            if emotion_type == '焦虑':
                if "别担心" not in result and "您可以" not in result:
                    result = "别担心，" + result

            # 困惑：简化表达
            elif emotion_type == '困惑':
                # 确保表达清晰
                result = result.replace("。", "。\n").replace("，", "，\n")

            # 期待：确认需求
            elif emotion_type == '期待':
                if not result.endswith("吗？") and not result.endswith("呢？"):
                    result += "\n请问还有其他问题吗？"

        return result

    return wrapper
