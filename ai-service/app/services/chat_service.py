"""
统一对话服务
管理完整的对话流程，包括消息处理、智能体分派、上下文管理等
集成智能对话管理器，支持意图识别、情感分析和智能响应
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# 智能体相关
from agents.registry import get_registry, AgentRegistry
from agents.base_agent import BaseAgent
from agents.agent_orchestrator import get_orchestrator, AgentOrchestrator

# Hermes相关
from hermes_enhanced_integration import HermesManager, EnhancementLevel, get_hermes_manager
from hermes_agent_coordinator import get_coordinator, HermesAgentCoordinator

# 数据库相关
from app.utils.unified_data_access import UnifiedDatabaseManager, db_manager

# 智能对话管理
from app.services.intelligent_chat_manager import get_intelligent_chat_manager, IntelligentChatManager
from app.services.super_chat_manager import get_super_chat_manager, SuperIntelligentChatManager

logger = logging.getLogger(__name__)


class ChatService:
    """统一对话服务（支持超级聊天管理器）"""
    
    def __init__(self, use_super_manager: bool = True):
        self._agent_registry: AgentRegistry = get_registry()
        self._agent_orchestrator: AgentOrchestrator = get_orchestrator()
        self._hermes: HermesManager = get_hermes_manager()
        self._coordinator: HermesAgentCoordinator = get_coordinator()
        self._db_manager: UnifiedDatabaseManager = db_manager
        
        # 选择聊天管理器
        self._use_super_manager = use_super_manager
        if use_super_manager:
            self._chat_manager = get_super_chat_manager()
            logger.info("统一对话服务初始化完成（使用超级聊天管理器）")
        else:
            self._chat_manager = get_intelligent_chat_manager()
            logger.info("统一对话服务初始化完成（使用普通聊天管理器）")
    
    def process_message(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """
        处理用户消息（完整流程）
        集成智能对话管理器，支持意图识别、情感分析和智能响应
        
        Args:
            session_id: 会话ID
            user_input: 用户输入文本
        
        Returns:
            处理结果字典，包含success、content、session_id等
        """
        try:
            # 1. 使用聊天管理器进行初步处理
            chat_result = self._chat_manager.process_message(session_id, user_input)
            intent = chat_result.get('intent')
            sentiment = chat_result.get('sentiment')
            user_profile = chat_result.get('user_profile')
            
            # 2. 根据意图决定处理方式
            # 对于简单的对话意图（问候、告别、感谢、闲聊），直接使用聊天管理器响应
            simple_intents = ['greeting', 'farewell', 'thanks', 'chat', 'emotional']
            
            if intent in simple_intents or chat_result.get('response_type') != 'default':
                response = chat_result.get('content', "")
                response_info = {
                    'agent_id': 'chat_manager',
                    'confidence': chat_result.get('intent_confidence', 0.0),
                    'intent': intent,
                    'sentiment': sentiment,
                    'user_profile': user_profile,
                    'response_type': chat_result.get('response_type'),
                    'resolved_reference': chat_result.get('resolved_reference'),
                    'is_super_manager': self._use_super_manager
                }
            else:
                # 对于复杂的业务意图，使用专业智能体处理
                history = self._load_conversation_history(session_id)
                
                # 将用户画像传递给协调器
                context = {'user_profile': user_profile, 'history': history}
                
                coordinator_result = self._coordinator.process_request(session_id, user_input, history, context)
                
                if not coordinator_result.get('success'):
                    response = coordinator_result.get('content', chat_result.get('content', "处理请求时发生错误"))
                else:
                    response = coordinator_result.get('content', "")
                
                response_info = {
                    'agent_id': coordinator_result.get('agent_id', 'chat_manager'),
                    'confidence': coordinator_result.get('confidence', chat_result.get('intent_confidence', 0.0)),
                    'intent': coordinator_result.get('intent', intent),
                    'sentiment': sentiment,
                    'user_profile': user_profile,
                    'resolved_reference': chat_result.get('resolved_reference'),
                    'is_super_manager': self._use_super_manager
                }
            
            # 3. 保存消息
            self._save_messages(session_id, user_input, response)
            
            return {
                'success': True,
                'content': response,
                'session_id': session_id,
                **response_info
            }
        
        except Exception as e:
            logger.error(f"消息处理失败: {e}", exc_info=True)
            return {
                'success': False,
                'content': f"抱歉，处理您的请求时发生错误：{str(e)}",
                'session_id': session_id
            }
    
    async def async_process_message(self, session_id: str, user_input: str) -> Dict[str, Any]:
        """
        异步处理用户消息
        
        Args:
            session_id: 会话ID
            user_input: 用户输入文本
        
        Returns:
            处理结果字典
        """
        return self.process_message(session_id, user_input)
    
    def _load_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        加载会话历史
        
        Args:
            session_id: 会话ID
        
        Returns:
            历史消息列表
        """
        try:
            return self._db_manager.get_conversation_history(session_id)
        except Exception as e:
            logger.warning(f"加载会话历史失败: {e}")
            return []
    
    def _save_messages(self, session_id: str, user_input: str, response: str):
        """
        保存消息到数据库
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            response: 响应内容
        """
        try:
            self._db_manager.save_message(session_id, 'user', user_input)
            self._db_manager.save_message(session_id, 'assistant', response)
        except Exception as e:
            logger.error(f"保存消息失败: {e}")
    
    def create_new_session(self) -> str:
        """
        创建新会话
        
        Returns:
            新会话ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        logger.info(f"创建新会话: {session_id}")
        return session_id
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话信息
        
        Args:
            session_id: 会话ID
        
        Returns:
            会话信息字典
        """
        try:
            stats = self._db_manager.get_conversation_stats()
            history = self._db_manager.get_conversation_history(session_id)
            
            return {
                'session_id': session_id,
                'message_count': len(history),
                'total_messages': stats.get('total_messages', 0),
                'total_sessions': stats.get('total_sessions', 0),
                'is_active': len(history) > 0
            }
        except Exception as e:
            logger.error(f"获取会话信息失败: {e}")
            return {'session_id': session_id, 'error': str(e)}
    
    def end_session(self, session_id: str) -> bool:
        """
        结束会话
        
        Args:
            session_id: 会话ID
        
        Returns:
            是否成功结束
        """
        try:
            deleted_count = self._db_manager.delete_conversation(session_id)
            logger.info(f"结束会话 {session_id}，删除消息数: {deleted_count}")
            return True
        except Exception as e:
            logger.error(f"结束会话失败: {e}")
            return False
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取会话历史（对外接口）
        
        Args:
            session_id: 会话ID
        
        Returns:
            历史消息列表
        """
        return self._load_conversation_history(session_id)
    
    def send_feedback(self, session_id: str, feedback_type: str, 
                     score: float = 0.5, details: Dict = None) -> bool:
        """
        发送用户反馈
        
        Args:
            session_id: 会话ID
            feedback_type: 反馈类型
            score: 分数 (0-1)
            details: 详细信息
        
        Returns:
            是否成功发送
        """
        if self._hermes.is_available():
            return self._hermes.send_feedback(session_id, feedback_type, score, details)
        return False
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """
        获取智能体统计信息
        
        Returns:
            智能体统计信息
        """
        return self._agent_orchestrator.get_agent_stats()
    
    def get_coordination_stats(self) -> Dict[str, Any]:
        """
        获取协调器统计信息
        
        Returns:
            协调器统计信息
        """
        return self._coordinator.get_coordination_stats()
    
    def set_dispatch_strategy(self, strategy: str):
        """
        设置智能体调度策略
        
        Args:
            strategy: 策略名称（intent_based, confidence_based, round_robin, load_balanced, hybrid）
        """
        from agents.agent_orchestrator import DispatchStrategy
        
        strategy_map = {
            'intent_based': DispatchStrategy.INTENT_BASED,
            'confidence_based': DispatchStrategy.CONFIDENCE_BASED,
            'round_robin': DispatchStrategy.ROUND_ROBIN,
            'load_balanced': DispatchStrategy.LOAD_BALANCED,
            'hybrid': DispatchStrategy.HYBRID
        }
        
        if strategy in strategy_map:
            self._agent_orchestrator.set_strategy(strategy_map[strategy])
            logger.info(f"调度策略已设置为: {strategy}")
        else:
            logger.warning(f"未知的调度策略: {strategy}")
    
    def set_collaboration_mode(self, mode: str):
        """
        设置Hermes与智能体的协作模式
        
        Args:
            mode: 协作模式（passive, active, guided, full）
        """
        from hermes_agent_coordinator import CollaborationMode
        
        mode_map = {
            'passive': CollaborationMode.PASSIVE,
            'active': CollaborationMode.ACTIVE,
            'guided': CollaborationMode.GUIDED,
            'full': CollaborationMode.FULL_INTEGRATION
        }
        
        if mode in mode_map:
            self._coordinator.set_collaboration_mode(mode_map[mode])
            logger.info(f"协作模式已设置为: {mode}")
        else:
            logger.warning(f"未知的协作模式: {mode}")


class ChatServiceBuilder:
    """
    对话服务构建器
    提供灵活的服务配置
    """
    
    def __init__(self):
        self._agent_registry = None
        self._agent_orchestrator = None
        self._hermes_manager = None
        self._coordinator = None
        self._db_manager = None
        self._enhancement_level = EnhancementLevel.STANDARD
    
    def with_agent_registry(self, registry: AgentRegistry):
        """设置智能体注册中心"""
        self._agent_registry = registry
        return self
    
    def with_agent_orchestrator(self, orchestrator: AgentOrchestrator):
        """设置智能体编排器"""
        self._agent_orchestrator = orchestrator
        return self
    
    def with_hermes_manager(self, hermes: HermesManager):
        """设置Hermes管理器"""
        self._hermes_manager = hermes
        return self
    
    def with_coordinator(self, coordinator: HermesAgentCoordinator):
        """设置Hermes-智能体协调器"""
        self._coordinator = coordinator
        return self
    
    def with_db_manager(self, db_manager: UnifiedDatabaseManager):
        """设置数据库管理器"""
        self._db_manager = db_manager
        return self
    
    def with_enhancement_level(self, level: EnhancementLevel):
        """设置增强级别"""
        self._enhancement_level = level
        return self
    
    def build(self) -> ChatService:
        """构建对话服务"""
        service = ChatService()
        
        if self._agent_registry:
            service._agent_registry = self._agent_registry
        if self._agent_orchestrator:
            service._agent_orchestrator = self._agent_orchestrator
        if self._hermes_manager:
            service._hermes = self._hermes_manager
        if self._coordinator:
            service._coordinator = self._coordinator
        if self._db_manager:
            service._db_manager = self._db_manager
        
        return service


# 全局实例
chat_service = ChatService()


def get_chat_service() -> ChatService:
    """
    获取对话服务实例
    
    Returns:
        对话服务实例
    """
    return chat_service


# 便捷函数
def process_chat(session_id: str, user_input: str) -> Dict[str, Any]:
    """
    便捷函数：处理聊天消息
    
    Args:
        session_id: 会话ID
        user_input: 用户输入
    
    Returns:
        处理结果
    """
    return chat_service.process_message(session_id, user_input)


def create_session() -> str:
    """
    便捷函数：创建新会话
    
    Returns:
        会话ID
    """
    return chat_service.create_new_session()
