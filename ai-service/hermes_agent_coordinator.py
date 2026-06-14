"""
Hermes与智能体协调器
实现Hermes高级AI服务与智能体系统的深度协作
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from threading import RLock

from hermes_enhanced_integration import HermesManager, EnhancementLevel, get_hermes_manager
from agents.base_agent import BaseAgent, AgentInfo
from agents.registry import AgentRegistry, get_registry

logger = logging.getLogger(__name__)


class CollaborationMode(Enum):
    """协作模式"""
    PASSIVE = "passive"              # 被动模式：仅在智能体完成后进行增强
    ACTIVE = "active"                # 主动模式：在智能体处理前后都参与
    GUIDED = "guided"                # 引导模式：Hermes指导智能体选择和执行
    FULL_INTEGRATION = "full"        # 完全集成：深度融合


@dataclass
class AgentExecutionContext:
    """智能体执行上下文"""
    session_id: str
    user_input: str
    intent: Dict[str, Any] = None
    emotion: Dict[str, Any] = None
    context_school: str = None
    history: List[Dict] = None
    user_profile: Dict[str, Any] = None


@dataclass
class CollaborationResult:
    """协作结果"""
    success: bool
    response: str
    agent_id: str = None
    confidence: float = 0.0
    enhancement: Any = None
    intent_info: Dict = None
    emotion_info: Dict = None


class HermesAgentCoordinator:
    """
    Hermes与智能体协调器
    负责协调Hermes高级AI服务与智能体系统之间的协作
    """
    
    _instance = None
    _lock = RLock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._hermes: HermesManager = get_hermes_manager()
            self._agent_registry: AgentRegistry = get_registry()
            self._collaboration_mode = CollaborationMode.FULL_INTEGRATION
            self._initialized = True
            logger.info("Hermes-智能体协调器初始化完成")
    
    def set_collaboration_mode(self, mode: CollaborationMode):
        """设置协作模式"""
        self._collaboration_mode = mode
        logger.info(f"协作模式已设置为: {mode.value}")
    
    def analyze_and_guide(self, session_id: str, user_input: str, 
                         history: List[Dict] = None) -> Dict[str, Any]:
        """
        分析用户输入并提供智能体选择指导
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            history: 对话历史
        
        Returns:
            指导信息，包含意图、情感、推荐智能体等
        """
        guidance = {
            'intent': None,
            'emotion': None,
            'recommended_agents': [],
            'context_info': {},
            'suggested_actions': []
        }
        
        # 1. 意图分析
        if self._hermes.is_available():
            guidance['intent'] = self._hermes.classify_intent(user_input)
            logger.debug(f"Hermes意图分析结果: {guidance['intent']}")
        
        # 2. 情感分析
        if self._hermes.is_available():
            guidance['emotion'] = self._hermes.analyze_emotion(user_input, session_id)
            logger.debug(f"Hermes情感分析结果: {guidance['emotion']}")
        
        # 3. 生成洞察和推荐
        if self._hermes.is_available():
            insights = self._hermes.generate_insights(
                user_input,
                user_profile=self._get_user_profile(session_id),
                conversation_history=history
            )
            guidance['context_info'] = insights
            guidance['suggested_actions'] = insights.get('followup_topics', [])
        
        # 4. 推荐智能体
        guidance['recommended_agents'] = self._recommend_agents(user_input, guidance['intent'])
        
        return guidance
    
    def _get_user_profile(self, session_id: str) -> Dict[str, Any]:
        """获取用户画像"""
        if self._hermes.is_available():
            try:
                profile_result = self._hermes._integration.update_profile(session_id, "", {})
                if profile_result:
                    return profile_result.get('data', {}).get('profile', {})
            except Exception as e:
                logger.warning(f"Hermes获取用户画像失败: {e}")
        return {}
    
    def _recommend_agents(self, user_input: str, intent: Dict = None) -> List[str]:
        """
        根据用户输入和意图推荐智能体
        
        Args:
            user_input: 用户输入
            intent: 意图信息
        
        Returns:
            推荐的智能体ID列表
        """
        if intent and intent.get('intent'):
            agents = self._agent_registry.find_agents_for_intent(intent['intent'])
            if agents:
                return agents
        
        # 降级到基于关键词的推荐
        return self._agent_registry.list_agents()
    
    def orchestrate_with_hermes(self, session_id: str, user_input: str, 
                               history: List[Dict] = None) -> CollaborationResult:
        """
        使用Hermes协调智能体执行（完整流程）
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            history: 对话历史
        
        Returns:
            协作结果
        """
        try:
            # 1. 分析阶段：Hermes分析用户输入
            guidance = self.analyze_and_guide(session_id, user_input, history)
            
            # 2. 构建执行上下文
            context = AgentExecutionContext(
                session_id=session_id,
                user_input=user_input,
                intent=guidance['intent'],
                emotion=guidance['emotion'],
                context_school=self._extract_school(history),
                history=history,
                user_profile=self._get_user_profile(session_id)
            )
            
            # 3. 智能体选择与执行
            result = self._execute_with_guidance(context, guidance)
            
            # 4. 增强阶段：Hermes增强响应
            enhanced_response, enhancement = self._enhance_response(
                session_id, user_input, result.response, guidance
            )
            
            # 5. 更新会话状态
            self._update_session_state(session_id, user_input, guidance, result)
            
            return CollaborationResult(
                success=True,
                response=enhanced_response,
                agent_id=result.agent_id,
                confidence=result.confidence,
                enhancement=enhancement,
                intent_info=guidance['intent'],
                emotion_info=guidance['emotion']
            )
        
        except Exception as e:
            logger.error(f"Hermes-智能体协作失败: {e}", exc_info=True)
            return CollaborationResult(
                success=False,
                response=f"处理请求时发生错误: {str(e)}"
            )
    
    def _extract_school(self, history: List[Dict]) -> Optional[str]:
        """从历史中提取学校名称"""
        if not history:
            return None
        
        school_keywords = ['中学', '高中', '一中', '二中', '三中', '附中']
        
        for msg in reversed(history):
            content = msg.get('content', '')
            for keyword in school_keywords:
                if keyword in content:
                    import re
                    pattern = rf'[\u4e00-\u9fa5]*{keyword}[\u4e00-\u9fa5]*'
                    match = re.search(pattern, content)
                    if match:
                        return match.group().strip()
        return None
    
    def _execute_with_guidance(self, context: AgentExecutionContext, 
                              guidance: Dict) -> CollaborationResult:
        """
        在Hermes指导下执行智能体
        
        Args:
            context: 执行上下文
            guidance: Hermes指导信息
        
        Returns:
            执行结果
        """
        # 根据协作模式选择执行策略
        if self._collaboration_mode == CollaborationMode.GUIDED:
            return self._guided_execution(context, guidance)
        else:
            return self._standard_execution(context, guidance)
    
    def _guided_execution(self, context: AgentExecutionContext, 
                         guidance: Dict) -> CollaborationResult:
        """
        引导式执行：Hermes指导智能体选择
        
        Args:
            context: 执行上下文
            guidance: Hermes指导信息
        
        Returns:
            执行结果
        """
        recommended_agents = guidance.get('recommended_agents', [])
        
        if recommended_agents:
            # 优先使用推荐的智能体
            for agent_id in recommended_agents:
                try:
                    agent = self._agent_registry.get_agent(agent_id)
                    response = agent.handle(context.user_input, {
                        'session_id': context.session_id,
                        'history': context.history,
                        'intent': context.intent,
                        'emotion': context.emotion,
                        'user_profile': context.user_profile,
                        'context_school': context.context_school
                    })
                    return CollaborationResult(
                        success=True,
                        response=response,
                        agent_id=agent_id,
                        confidence=0.9  # 引导模式置信度较高
                    )
                except Exception as e:
                    logger.warning(f"推荐智能体 {agent_id} 执行失败: {e}")
        
        # 降级到默认智能体
        return self._fallback_execution(context)
    
    def _standard_execution(self, context: AgentExecutionContext, 
                           guidance: Dict) -> CollaborationResult:
        """
        标准执行：智能体自主处理
        
        Args:
            context: 执行上下文
            guidance: Hermes指导信息
        
        Returns:
            执行结果
        """
        # 尝试根据意图选择智能体
        if context.intent and context.intent.get('intent'):
            agents = self._agent_registry.find_agents_for_intent(context.intent['intent'])
            if agents:
                agent_id = agents[0]
                try:
                    agent = self._agent_registry.get_agent(agent_id)
                    response = agent.handle(context.user_input, {
                        'session_id': context.session_id,
                        'history': context.history,
                        'intent': context.intent,
                        'emotion': context.emotion,
                        'user_profile': context.user_profile,
                        'context_school': context.context_school
                    })
                    return CollaborationResult(
                        success=True,
                        response=response,
                        agent_id=agent_id,
                        confidence=context.intent.get('confidence', 0.7)
                    )
                except Exception as e:
                    logger.warning(f"智能体 {agent_id} 执行失败: {e}")
        
        # 降级到默认智能体
        return self._fallback_execution(context)
    
    def _fallback_execution(self, context: AgentExecutionContext) -> CollaborationResult:
        """
        降级执行：使用默认智能体
        
        Args:
            context: 执行上下文
        
        Returns:
            执行结果
        """
        try:
            agent = self._agent_registry.get_default_agent()
            response = agent.handle(context.user_input, {
                'session_id': context.session_id,
                'history': context.history,
                'intent': context.intent,
                'emotion': context.emotion,
                'user_profile': context.user_profile,
                'context_school': context.context_school
            })
            return CollaborationResult(
                success=True,
                response=response,
                agent_id=agent.agent_id,
                confidence=0.5  # 降级模式置信度较低
            )
        except Exception as e:
            logger.error(f"默认智能体执行失败: {e}")
            return CollaborationResult(
                success=False,
                response=f"处理请求时发生错误: {str(e)}"
            )
    
    def _enhance_response(self, session_id: str, user_input: str, 
                         response: str, guidance: Dict) -> tuple:
        """
        使用Hermes增强响应
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            response: 基础响应
            guidance: Hermes指导信息
        
        Returns:
            (增强后的响应, 增强结果)
        """
        if self._hermes.is_available():
            try:
                context = {
                    'intent': guidance.get('intent'),
                    'emotion': guidance.get('emotion'),
                    'user_profile': guidance.get('user_profile', {}),
                    'suggested_actions': guidance.get('suggested_actions', [])
                }
                return self._hermes.enhance(
                    session_id=session_id,
                    user_input=user_input,
                    base_response=response,
                    context=context,
                    level=EnhancementLevel.STANDARD
                )
            except Exception as e:
                logger.warning(f"Hermes增强失败: {e}")
        
        return response, None
    
    def _update_session_state(self, session_id: str, user_input: str,
                             guidance: Dict, result: CollaborationResult):
        """
        更新会话状态
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            guidance: Hermes指导信息
            result: 执行结果
        """
        if self._hermes.is_available():
            try:
                # 异步更新会话状态
                self._hermes._integration.executor.submit(
                    self._hermes._integration.track_conversation,
                    session_id, user_input, {
                        'intent': guidance.get('intent'),
                        'emotion': guidance.get('emotion'),
                        'agent_id': result.agent_id,
                        'confidence': result.confidence
                    }
                )
            except Exception as e:
                logger.warning(f"更新会话状态失败: {e}")
    
    def process_request(self, session_id: str, user_input: str, 
                       history: List[Dict] = None) -> Dict[str, Any]:
        """
        处理请求（便捷接口）
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            history: 对话历史
        
        Returns:
            处理结果
        """
        result = self.orchestrate_with_hermes(session_id, user_input, history)
        
        return {
            'success': result.success,
            'content': result.response,
            'session_id': session_id,
            'agent_id': result.agent_id,
            'confidence': result.confidence,
            'intent': result.intent_info,
            'emotion': result.emotion_info
        }
    
    def get_coordination_stats(self) -> Dict[str, Any]:
        """获取协调器统计信息"""
        return {
            'hermes_available': self._hermes.is_available(),
            'collaboration_mode': self._collaboration_mode.value,
            'registered_agents': len(self._agent_registry.list_agents()),
            'has_default_agent': self._agent_registry._default_agent_id is not None
        }


# 全局实例
hermes_agent_coordinator = HermesAgentCoordinator()


def get_coordinator() -> HermesAgentCoordinator:
    """获取Hermes-智能体协调器实例"""
    return hermes_agent_coordinator


def coordinate_request(session_id: str, user_input: str, 
                      history: List[Dict] = None) -> Dict[str, Any]:
    """
    便捷函数：协调处理请求
    
    Args:
        session_id: 会话ID
        user_input: 用户输入
        history: 对话历史
    
    Returns:
        处理结果
    """
    return hermes_agent_coordinator.process_request(session_id, user_input, history)
