"""
智能体服务
提供智能体的管理、调度和执行功能
"""

import logging
from typing import Dict, Any, Optional, List
from agents.registry import get_registry, AgentRegistry, AgentNotFoundError
from agents.base_agent import BaseAgent, AgentInfo, IntentMatch
from hermes_enhanced_integration import HermesManager, get_hermes_manager

logger = logging.getLogger(__name__)


class AgentService:
    """智能体服务"""
    
    def __init__(self):
        self._registry: AgentRegistry = get_registry()
        self._hermes: HermesManager = get_hermes_manager()
        logger.info("智能体服务初始化完成")
    
    def register_agent(self, agent_id: str, agent_class, default: bool = False, **kwargs) -> None:
        """
        注册智能体
        
        Args:
            agent_id: 智能体唯一标识
            agent_class: 智能体类
            default: 是否设为默认智能体
            **kwargs: 智能体初始化参数
        """
        self._registry.register(agent_id, agent_class, default=default, **kwargs)
    
    def get_agent(self, agent_id: str) -> BaseAgent:
        """
        获取智能体实例
        
        Args:
            agent_id: 智能体标识
        
        Returns:
            智能体实例
        """
        return self._registry.get_agent(agent_id)
    
    def get_default_agent(self) -> BaseAgent:
        """
        获取默认智能体
        
        Returns:
            默认智能体实例
        """
        return self._registry.get_default_agent()
    
    def list_agents(self) -> List[str]:
        """
        获取所有注册的智能体ID
        
        Returns:
            智能体ID列表
        """
        return self._registry.list_agents()
    
    def get_agent_info(self, agent_id: str) -> AgentInfo:
        """
        获取智能体信息
        
        Args:
            agent_id: 智能体标识
        
        Returns:
            智能体信息
        """
        return self._registry.get_agent_info(agent_id)
    
    def get_all_agents_info(self) -> List[AgentInfo]:
        """
        获取所有智能体信息
        
        Returns:
            智能体信息列表
        """
        return self._registry.get_all_agents_info()
    
    def unregister_agent(self, agent_id: str) -> None:
        """
        注销智能体
        
        Args:
            agent_id: 智能体标识
        """
        self._registry.unregister(agent_id)
    
    def set_default_agent(self, agent_id: str) -> None:
        """
        设置默认智能体
        
        Args:
            agent_id: 智能体标识
        """
        self._registry.set_default_agent(agent_id)
    
    def select_agent(self, user_input: str) -> Optional[str]:
        """
        根据用户输入选择最佳智能体
        
        Args:
            user_input: 用户输入文本
        
        Returns:
            最佳智能体ID，如果没有合适的则返回None
        """
        return self._registry.select_best_agent(user_input)
    
    def select_agent_with_intent(self, user_input: str) -> IntentMatch:
        """
        根据用户输入选择最佳智能体并返回意图匹配结果
        
        Args:
            user_input: 用户输入文本
        
        Returns:
            IntentMatch 对象
        """
        return self._registry.select_best_agent_with_intent(user_input)
    
    def find_agents_for_intent(self, intent: str) -> List[str]:
        """
        查找支持指定意图的智能体
        
        Args:
            intent: 意图标识
        
        Returns:
            支持该意图的智能体ID列表
        """
        return self._registry.find_agents_for_intent(intent)
    
    def execute_agent(self, agent_id: str, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        执行智能体
        
        Args:
            agent_id: 智能体标识
            user_input: 用户输入文本
            context: 上下文信息
        
        Returns:
            智能体响应
        """
        try:
            agent = self.get_agent(agent_id)
            return agent.handle(user_input, context or {})
        except AgentNotFoundError as e:
            logger.error(f"智能体未找到: {e}")
            return f"抱歉，未找到智能体 {agent_id}"
        except Exception as e:
            logger.error(f"智能体执行失败: {e}", exc_info=True)
            return f"抱歉，智能体执行出错: {str(e)}"
    
    async def async_execute_agent(self, agent_id: str, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        异步执行智能体
        
        Args:
            agent_id: 智能体标识
            user_input: 用户输入文本
            context: 上下文信息
        
        Returns:
            智能体响应
        """
        return self.execute_agent(agent_id, user_input, context)
    
    def execute_best_agent(self, user_input: str, context: Dict[str, Any] = None) -> dict:
        """
        执行最佳智能体
        
        Args:
            user_input: 用户输入文本
            context: 上下文信息
        
        Returns:
            执行结果字典，包含agent_id和response
        """
        # 使用Hermes进行意图识别
        intent_info = {}
        if self._hermes.is_available():
            try:
                intent_info = self._hermes.classify_intent(user_input)
            except Exception as e:
                logger.warning(f"Hermes意图识别失败: {e}")
        
        # 选择最佳智能体
        agent_id = self.select_agent(user_input)
        
        if agent_id:
            response = self.execute_agent(agent_id, user_input, context)
            return {
                'success': True,
                'agent_id': agent_id,
                'response': response,
                'intent': intent_info
            }
        else:
            # 使用默认智能体
            try:
                agent = self.get_default_agent()
                response = agent.handle(user_input, context or {})
                return {
                    'success': True,
                    'agent_id': agent.agent_id,
                    'response': response,
                    'intent': intent_info
                }
            except Exception as e:
                logger.error(f"默认智能体执行失败: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取智能体服务统计信息
        
        Returns:
            统计信息字典
        """
        return self._registry.get_stats()
    
    def clear_all_agents(self) -> None:
        """
        清空所有智能体
        """
        self._registry.clear()


class AgentServiceBuilder:
    """
    智能体服务构建器
    """
    
    def __init__(self):
        self._registry = None
        self._hermes = None
    
    def with_registry(self, registry: AgentRegistry):
        """设置注册中心"""
        self._registry = registry
        return self
    
    def with_hermes(self, hermes: HermesManager):
        """设置Hermes管理器"""
        self._hermes = hermes
        return self
    
    def build(self) -> AgentService:
        """构建智能体服务"""
        service = AgentService()
        if self._registry:
            service._registry = self._registry
        if self._hermes:
            service._hermes = self._hermes
        return service


# 全局实例
agent_service = AgentService()


def get_agent_service() -> AgentService:
    """
    获取智能体服务实例
    
    Returns:
        智能体服务实例
    """
    return agent_service


# 便捷函数
def execute_agent(agent_id: str, user_input: str, context: Dict[str, Any] = None) -> str:
    """
    便捷函数：执行智能体
    
    Args:
        agent_id: 智能体标识
        user_input: 用户输入
        context: 上下文
    
    Returns:
        智能体响应
    """
    return agent_service.execute_agent(agent_id, user_input, context)


def execute_best_agent(user_input: str, context: Dict[str, Any] = None) -> dict:
    """
    便捷函数：执行最佳智能体
    
    Args:
        user_input: 用户输入
        context: 上下文
    
    Returns:
        执行结果
    """
    return agent_service.execute_best_agent(user_input, context)


def list_all_agents() -> List[str]:
    """
    便捷函数：获取所有智能体ID
    
    Returns:
        智能体ID列表
    """
    return agent_service.list_agents()
