"""
智能体注册中心模块
提供智能体的注册、管理和调度功能
"""

from typing import Dict, Any, Optional, List, Type, Callable
from .base_agent import BaseAgent, AgentInfo, AgentNotFoundError, IntentMatch
import logging
from threading import RLock

logger = logging.getLogger(__name__)


class AgentRegistry:
    """智能体注册中心"""
    
    _instance = None
    _lock = RLock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化注册中心"""
        if not hasattr(self, '_initialized'):
            self._agents: Dict[str, dict] = {}
            self._intents: Dict[str, List[str]] = {}  # intent -> [agent_id, ...]
            self._default_agent_id: Optional[str] = None
            self._initialized = True
            logger.info("智能体注册中心初始化完成")
    
    def register(
        self,
        agent_id: str,
        agent_class: Type[BaseAgent],
        default: bool = False,
        **kwargs
    ) -> None:
        """
        注册智能体
        
        Args:
            agent_id: 智能体唯一标识
            agent_class: 智能体类（继承自BaseAgent）
            default: 是否设为默认智能体
            **kwargs: 智能体初始化参数
        
        Raises:
            ValueError: 如果agent_id已存在
            TypeError: 如果agent_class不是BaseAgent的子类
        """
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"agent_class必须是BaseAgent的子类，当前为{type(agent_class)}")
        
        if agent_id in self._agents:
            raise ValueError(f"智能体 {agent_id} 已注册")
        
        self._agents[agent_id] = {
            'class': agent_class,
            'instance': None,
            'kwargs': kwargs,
            'metadata': {}
        }
        
        # 记录支持的意图
        # 先创建一个临时实例来获取意图信息
        temp_instance = agent_class(**kwargs)
        supported_intents = temp_instance.get_supported_intents()
        for intent in supported_intents:
            if intent not in self._intents:
                self._intents[intent] = []
            if agent_id not in self._intents[intent]:
                self._intents[intent].append(agent_id)
        
        if default:
            self._default_agent_id = agent_id
        
        logger.info(f"智能体注册成功: {agent_id}")
    
    def register_with_decorator(self, agent_id: str, default: bool = False, **kwargs):
        """
        装饰器形式注册智能体
        
        Args:
            agent_id: 智能体唯一标识
            default: 是否设为默认智能体
            **kwargs: 智能体初始化参数
        
        Returns:
            装饰器函数
        """
        def decorator(cls: Type[BaseAgent]) -> Type[BaseAgent]:
            self.register(agent_id, cls, default=default, **kwargs)
            return cls
        return decorator
    
    def get_agent(self, agent_id: str) -> BaseAgent:
        """
        获取智能体实例（懒加载）
        
        Args:
            agent_id: 智能体唯一标识
        
        Returns:
            智能体实例
        
        Raises:
            AgentNotFoundError: 如果智能体未注册
        """
        if agent_id not in self._agents:
            raise AgentNotFoundError(f"智能体 {agent_id} 未注册")
        
        entry = self._agents[agent_id]
        if entry['instance'] is None:
            with self._lock:
                # 双重检查
                if entry['instance'] is None:
                    entry['instance'] = entry['class'](**entry['kwargs'])
                    logger.debug(f"智能体实例化: {agent_id}")
        
        return entry['instance']
    
    def get_default_agent(self) -> BaseAgent:
        """
        获取默认智能体
        
        Returns:
            默认智能体实例
        
        Raises:
            AgentNotFoundError: 如果没有默认智能体
        """
        if self._default_agent_id is None:
            raise AgentNotFoundError("未设置默认智能体")
        return self.get_agent(self._default_agent_id)
    
    def list_agents(self) -> List[str]:
        """
        列出所有注册的智能体
        
        Returns:
            智能体ID列表
        """
        return list(self._agents.keys())
    
    def has_agent(self, agent_id: str) -> bool:
        """
        检查智能体是否已注册
        
        Args:
            agent_id: 智能体唯一标识
            
        Returns:
            True 如果智能体已注册，否则 False
        """
        return agent_id in self._agents
    
    def get_agent_info(self, agent_id: str) -> AgentInfo:
        """
        获取智能体信息
        
        Args:
            agent_id: 智能体唯一标识
        
        Returns:
            智能体信息
        
        Raises:
            AgentNotFoundError: 如果智能体未注册
        """
        agent = self.get_agent(agent_id)
        return agent.get_agent_info()
    
    def get_all_agents_info(self) -> List[AgentInfo]:
        """
        获取所有智能体的信息
        
        Returns:
            所有智能体信息列表
        """
        return [self.get_agent_info(agent_id) for agent_id in self.list_agents()]
    
    def unregister(self, agent_id: str) -> None:
        """
        注销智能体
        
        Args:
            agent_id: 智能体唯一标识
        
        Raises:
            AgentNotFoundError: 如果智能体未注册
        """
        if agent_id not in self._agents:
            raise AgentNotFoundError(f"智能体 {agent_id} 未注册")
        
        # 从意图映射中移除
        entry = self._agents[agent_id]
        if entry['instance']:
            intents = entry['instance'].get_supported_intents()
            for intent in intents:
                if intent in self._intents and agent_id in self._intents[intent]:
                    self._intents[intent].remove(agent_id)
        
        # 如果是默认智能体，清空默认设置
        if self._default_agent_id == agent_id:
            self._default_agent_id = None
        
        del self._agents[agent_id]
        logger.info(f"智能体注销成功: {agent_id}")
    
    def find_agents_for_intent(self, intent: str) -> List[str]:
        """
        查找支持指定意图的智能体
        
        Args:
            intent: 意图标识
        
        Returns:
            支持该意图的智能体ID列表
        """
        return self._intents.get(intent, [])
    
    def select_best_agent(self, user_input: str) -> Optional[str]:
        """
        根据用户输入选择最佳智能体
        
        Args:
            user_input: 用户输入文本
        
        Returns:
            最佳智能体ID，如果没有合适的则返回None
        """
        best_agent_id = None
        best_confidence = 0.0
        
        for agent_id in self._agents.keys():
            try:
                agent = self.get_agent(agent_id)
                confidence = agent.can_handle(user_input)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_agent_id = agent_id
            except Exception as e:
                logger.warning(f"获取智能体 {agent_id} 失败: {e}")
        
        return best_agent_id
    
    def select_best_agent_with_intent(self, user_input: str) -> IntentMatch:
        """
        根据用户输入选择最佳智能体并返回意图匹配结果
        
        Args:
            user_input: 用户输入文本
        
        Returns:
            IntentMatch 对象
        """
        agent_id = self.select_best_agent(user_input)
        if agent_id:
            agent = self.get_agent(agent_id)
            confidence = agent.can_handle(user_input)
            return IntentMatch(
                intent=agent.get_supported_intents()[0] if agent.get_supported_intents() else "unknown",
                confidence=confidence,
                agent_id=agent_id
            )
        return IntentMatch(intent="unknown", confidence=0.0)
    
    def set_default_agent(self, agent_id: str) -> None:
        """
        设置默认智能体
        
        Args:
            agent_id: 智能体唯一标识
        
        Raises:
            AgentNotFoundError: 如果智能体未注册
        """
        if agent_id not in self._agents:
            raise AgentNotFoundError(f"智能体 {agent_id} 未注册")
        self._default_agent_id = agent_id
        logger.info(f"默认智能体设置为: {agent_id}")
    
    def clear(self) -> None:
        """
        清空所有注册的智能体
        """
        self._agents.clear()
        self._intents.clear()
        self._default_agent_id = None
        logger.info("智能体注册中心已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取注册中心统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'total_agents': len(self._agents),
            'total_intents': len(self._intents),
            'has_default_agent': self._default_agent_id is not None,
            'default_agent_id': self._default_agent_id
        }


class AgentFactory:
    """
    智能体工厂
    提供智能体的创建和管理功能
    """
    
    def __init__(self, registry: Optional[AgentRegistry] = None):
        """
        初始化工厂
        
        Args:
            registry: 智能体注册中心，如果为None则使用全局实例
        """
        self._registry = registry if registry else AgentRegistry()
    
    def create_agent(self, agent_id: str, **kwargs) -> BaseAgent:
        """
        创建智能体实例
        
        Args:
            agent_id: 智能体标识
            **kwargs: 额外参数
        
        Returns:
            智能体实例
        """
        return self._registry.get_agent(agent_id)
    
    def create_default_agent(self) -> BaseAgent:
        """
        创建默认智能体
        
        Returns:
            默认智能体实例
        """
        return self._registry.get_default_agent()
    
    def get_or_create_agent(self, agent_id: str) -> BaseAgent:
        """
        获取或创建智能体
        
        Args:
            agent_id: 智能体标识
        
        Returns:
            智能体实例
        """
        return self._registry.get_agent(agent_id)


# 全局实例
agent_registry = AgentRegistry()


def get_registry() -> AgentRegistry:
    """
    获取智能体注册中心实例
    
    Returns:
        智能体注册中心实例
    """
    return agent_registry


def register_agent(agent_id: str, default: bool = False, **kwargs) -> Callable:
    """
    便捷装饰器：注册智能体
    
    Args:
        agent_id: 智能体标识
        default: 是否设为默认智能体
        **kwargs: 初始化参数
    
    Returns:
        装饰器函数
    """
    return agent_registry.register_with_decorator(agent_id, default=default, **kwargs)


def get_agent(agent_id: str) -> BaseAgent:
    """
    便捷函数：获取智能体
    
    Args:
        agent_id: 智能体标识
    
    Returns:
        智能体实例
    """
    return agent_registry.get_agent(agent_id)


def get_default_agent() -> BaseAgent:
    """
    便捷函数：获取默认智能体
    
    Returns:
        默认智能体实例
    """
    return agent_registry.get_default_agent()


# 延迟导入：在 registry 初始化完成后触发智能体注册
# 注意：这里不能在模块级直接 import agents.agent_registration，否则会形成循环导入
# 所以使用"懒加载"——当第一个智能体被调用时会触发（由 agent_orchestrator 负责导入）
# 这里提供一个显式的初始化函数作为备用入口
def ensure_agents_registered():
    """确保所有智能体都被注册（可被外部显式调用）"""
    try:
        if not agent_registry.list_agents():
            # 导入后会自动执行该模块的 register_all_agents()
            import agents.agent_registration  # noqa: F401
    except Exception:
        pass


# 在模块导入完成后再显式调用一次，确保智能体被注册
try:
    ensure_agents_registered()
except Exception:
    pass
