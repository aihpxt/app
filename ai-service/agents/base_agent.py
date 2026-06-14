"""
智能体基类模块
定义智能体的通用接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentInfo:
    """智能体信息"""
    agent_id: str
    agent_name: str
    description: str = ""
    supported_intents: List[str] = None
    version: str = "1.0.0"
    
    def __post_init__(self):
        if self.supported_intents is None:
            self.supported_intents = []


@dataclass
class IntentMatch:
    """意图匹配结果"""
    intent: str
    confidence: float
    agent_id: str = None


class AgentNotFoundError(Exception):
    """智能体未找到异常"""
    pass


class BaseAgent(ABC):
    """智能体基类"""
    
    agent_id: str = None
    agent_name: str = None
    description: str = None
    version: str = "1.0.0"
    
    def __init__(self):
        self._logger = logging.getLogger(f"agent.{self.agent_id}")
    
    @abstractmethod
    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入文本
            context: 上下文信息，包含会话历史、用户画像等
        
        Returns:
            响应文本
        """
        pass
    
    def can_handle(self, user_input: str) -> float:
        """
        判断是否能处理该请求
        
        Args:
            user_input: 用户输入文本
        
        Returns:
            置信度 (0.0-1.0)
        """
        return 0.0
    
    def get_supported_intents(self) -> List[str]:
        """
        获取支持的意图列表
        
        Returns:
            意图列表
        """
        return []
    
    def get_agent_info(self) -> AgentInfo:
        """
        获取智能体信息
        
        Returns:
            AgentInfo 对象
        """
        return AgentInfo(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            description=self.description,
            supported_intents=self.get_supported_intents(),
            version=self.version
        )
    
    def extract_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        从上下文中提取关键信息
        
        Args:
            context: 上下文字典
        
        Returns:
            提取的关键信息
        """
        return {
            'session_id': context.get('session_id'),
            'history': context.get('history', []),
            'user_profile': context.get('user_profile', {}),
            'intent': context.get('intent')
        }
    
    def format_response(self, content: str) -> str:
        """
        格式化响应
        
        Args:
            content: 响应内容
        
        Returns:
            格式化后的响应
        """
        return content.strip()
    
    def log_request(self, user_input: str, response: str):
        """
        记录请求日志
        
        Args:
            user_input: 用户输入
            response: 响应内容
        """
        self._logger.info(f"Request: {user_input[:50]} -> Response: {response[:50]}")
    
    async def async_handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """
        异步处理用户输入（默认同步实现）
        
        Args:
            user_input: 用户输入文本
            context: 上下文信息
        
        Returns:
            响应文本
        """
        return self.handle(user_input, context)


class SimpleAgent(BaseAgent):
    """
    简单智能体实现
    适用于基础的规则驱动智能体
    """
    
    def __init__(self, agent_id: str, agent_name: str, description: str = ""):
        super().__init__()
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.description = description
    
    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """处理用户输入（需要子类实现）"""
        return "未实现的响应"


class CompositeAgent(BaseAgent):
    """
    复合智能体
    可以组合多个子智能体
    """
    
    def __init__(self):
        super().__init__()
        self._sub_agents = []
    
    def add_sub_agent(self, agent: BaseAgent):
        """添加子智能体"""
        self._sub_agents.append(agent)
    
    def remove_sub_agent(self, agent_id: str):
        """移除子智能体"""
        self._sub_agents = [a for a in self._sub_agents if a.agent_id != agent_id]
    
    def select_agent(self, user_input: str) -> Optional[BaseAgent]:
        """
        根据用户输入选择最合适的子智能体
        
        Args:
            user_input: 用户输入文本
        
        Returns:
            最佳匹配的子智能体，如果没有合适的则返回None
        """
        best_agent = None
        best_confidence = 0.0
        
        for agent in self._sub_agents:
            confidence = agent.can_handle(user_input)
            if confidence > best_confidence:
                best_confidence = confidence
                best_agent = agent
        
        return best_agent
    
    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入文本
            context: 上下文信息
        
        Returns:
            响应文本
        """
        agent = self.select_agent(user_input)
        if agent:
            return agent.handle(user_input, context)
        return self._fallback_response(user_input, context)
    
    def _fallback_response(self, user_input: str, context: Dict[str, Any]) -> str:
        """
        降级响应
        
        Args:
            user_input: 用户输入文本
            context: 上下文信息
        
        Returns:
            降级响应文本
        """
        return "抱歉，我暂时无法回答这个问题。"
    
    def get_supported_intents(self) -> List[str]:
        """获取所有子智能体支持的意图"""
        intents = []
        for agent in self._sub_agents:
            intents.extend(agent.get_supported_intents())
        return list(set(intents))


class ContextAwareAgent(BaseAgent):
    """
    上下文感知智能体
    具备上下文管理能力的智能体基类
    """
    
    def __init__(self):
        super().__init__()
        self._context_window_size = 10
    
    def get_context_window_size(self) -> int:
        """获取上下文窗口大小"""
        return self._context_window_size
    
    def set_context_window_size(self, size: int):
        """设置上下文窗口大小"""
        self._context_window_size = size
    
    def truncate_history(self, history: List[Dict]) -> List[Dict]:
        """
        截断历史记录到窗口大小
        
        Args:
            history: 完整的历史记录
        
        Returns:
            截断后的历史记录
        """
        if len(history) > self._context_window_size:
            return history[-self._context_window_size:]
        return history
    
    def extract_context_school(self, history: List[Dict]) -> Optional[str]:
        """
        从历史中提取学校名称
        
        Args:
            history: 对话历史
        
        Returns:
            提取到的学校名称，如果没有则返回None
        """
        school_keywords = ['中学', '高中', '一中', '二中', '三中', '附中']
        
        # 从最近的消息开始查找
        for msg in reversed(history):
            content = msg.get('content', '')
            for keyword in school_keywords:
                if keyword in content:
                    # 尝试提取学校名称
                    import re
                    # 匹配包含关键词的词
                    pattern = rf'[\u4e00-\u9fa5]*{keyword}[\u4e00-\u9fa5]*'
                    match = re.search(pattern, content)
                    if match:
                        return match.group().strip()
        return None
    
    def has_pronoun(self, text: str) -> bool:
        """
        检测文本中是否包含指代词
        
        Args:
            text: 输入文本
        
        Returns:
            是否包含指代词
        """
        pronouns = ["这个", "那个", "它", "这所", "那所", "这些", "那些", "此", "其"]
        return any(word in text for word in pronouns)
