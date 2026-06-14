"""
智能体编排器模块
提供智能体调度、路由和协作功能
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from threading import RLock
import time

from agents.base_agent import BaseAgent, IntentMatch
from agents.registry import AgentRegistry, AgentNotFoundError

logger = logging.getLogger(__name__)


class DispatchStrategy(Enum):
    """调度策略"""
    INTENT_BASED = "intent_based"          # 基于意图
    CONFIDENCE_BASED = "confidence_based"  # 基于置信度
    ROUND_ROBIN = "round_robin"            # 轮询
    LOAD_BALANCED = "load_balanced"        # 负载均衡
    HYBRID = "hybrid"                      # 混合策略


class AgentLoadInfo:
    """智能体负载信息"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.active_tasks = 0
        self.total_requests = 0
        self.total_response_time = 0.0
        self.last_request_time = 0.0
    
    def record_request(self, response_time: float):
        """记录请求"""
        self.active_tasks -= 1
        self.total_requests += 1
        self.total_response_time += response_time
        self.last_request_time = time.time()
    
    def start_request(self):
        """开始请求"""
        self.active_tasks += 1


class AgentOrchestrator:
    """
    智能体编排器
    负责智能体的调度、路由和协作
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
            self._registry = AgentRegistry()
            self._load_info: Dict[str, AgentLoadInfo] = {}
            self._strategy = DispatchStrategy.HYBRID
            self._intent_cache: Dict[str, str] = {}  # 意图到智能体的缓存
            self._context_window_size = 10
            self._initialized = True
            logger.info("智能体编排器初始化完成")
    
    def set_strategy(self, strategy: DispatchStrategy):
        """设置调度策略"""
        self._strategy = strategy
        logger.info(f"调度策略已设置为: {strategy.value}")
    
    def get_load_info(self, agent_id: str) -> AgentLoadInfo:
        """获取智能体负载信息"""
        if agent_id not in self._load_info:
            self._load_info[agent_id] = AgentLoadInfo(agent_id)
        return self._load_info[agent_id]
    
    def select_agent(self, user_input: str, context: Dict = None) -> Tuple[str, float]:
        """
        选择最佳智能体
        
        Args:
            user_input: 用户输入
            context: 上下文信息
        
        Returns:
            (agent_id, confidence)
        """
        if self._strategy == DispatchStrategy.INTENT_BASED:
            return self._select_by_intent(user_input, context)
        elif self._strategy == DispatchStrategy.CONFIDENCE_BASED:
            return self._select_by_confidence(user_input)
        elif self._strategy == DispatchStrategy.ROUND_ROBIN:
            return self._select_by_round_robin()
        elif self._strategy == DispatchStrategy.LOAD_BALANCED:
            return self._select_by_load(user_input)
        else:
            return self._select_hybrid(user_input, context)
    
    def _select_by_intent(self, user_input: str, context: Dict = None) -> Tuple[str, float]:
        """基于意图选择智能体"""
        # 先尝试从缓存获取
        cache_key = user_input[:100]
        if cache_key in self._intent_cache:
            agent_id = self._intent_cache[cache_key]
            return agent_id, 0.8
        
        # 使用Hermes进行意图分类
        intent = self._classify_intent(user_input)
        intent_name = intent.get('intent')
        
        if intent_name:
            agents = self._registry.find_agents_for_intent(intent_name)
            if agents:
                # 考虑负载选择
                agent_id = self._select_least_loaded(agents)
                self._intent_cache[cache_key] = agent_id
                return agent_id, intent.get('confidence', 0.8)
        
        # 降级到置信度选择
        return self._select_by_confidence(user_input)
    
    def _select_by_confidence(self, user_input: str) -> Tuple[str, float]:
        """基于置信度选择智能体"""
        best_agent_id = None
        best_confidence = 0.0
        
        for agent_id in self._registry.list_agents():
            try:
                agent = self._registry.get_agent(agent_id)
                confidence = agent.can_handle(user_input)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_agent_id = agent_id
            except Exception as e:
                logger.warning(f"获取智能体 {agent_id} 失败: {e}")
        
        if best_agent_id:
            return best_agent_id, best_confidence
        
        return self._get_default_agent()
    
    def _select_by_round_robin(self) -> Tuple[str, float]:
        """轮询选择智能体"""
        agents = self._registry.list_agents()
        if not agents:
            return self._get_default_agent()
        
        # 简单轮询：基于请求计数
        if not hasattr(self, '_round_robin_index'):
            self._round_robin_index = 0
        
        agent_id = agents[self._round_robin_index % len(agents)]
        self._round_robin_index += 1
        
        return agent_id, 0.5
    
    def _select_by_load(self, user_input: str) -> Tuple[str, float]:
        """基于负载选择智能体"""
        # 首先获取所有能处理该请求的智能体
        candidates = []
        for agent_id in self._registry.list_agents():
            try:
                agent = self._registry.get_agent(agent_id)
                confidence = agent.can_handle(user_input)
                if confidence >= 0.3:  # 最低置信度要求
                    load_info = self.get_load_info(agent_id)
                    candidates.append((agent_id, confidence, load_info))
            except Exception as e:
                logger.warning(f"获取智能体 {agent_id} 失败: {e}")
        
        if not candidates:
            return self._get_default_agent()
        
        # 选择负载最低的智能体
        # 负载 = 活跃任务数 + 平均响应时间 * 系数
        best_agent_id = None
        best_score = float('inf')
        
        for agent_id, confidence, load_info in candidates:
            avg_response_time = load_info.total_response_time / max(load_info.total_requests, 1)
            load_score = load_info.active_tasks + avg_response_time * 0.1
            # 综合考虑置信度和负载
            score = load_score / confidence
            
            if score < best_score:
                best_score = score
                best_agent_id = agent_id
        
        return best_agent_id, 0.5
    
    def _select_hybrid(self, user_input: str, context: Dict = None) -> Tuple[str, float]:
        """混合策略选择智能体"""
        # 第一步：基于意图选择
        intent_result = self._select_by_intent(user_input, context)
        if intent_result[1] >= 0.7:  # 高置信度意图匹配
            return intent_result
        
        # 第二步：考虑负载
        load_result = self._select_by_load(user_input)
        return load_result
    
    def _select_least_loaded(self, agent_ids: List[str]) -> str:
        """从候选智能体中选择负载最低的"""
        best_agent_id = agent_ids[0]
        min_load = float('inf')
        
        for agent_id in agent_ids:
            load_info = self.get_load_info(agent_id)
            load = load_info.active_tasks
            if load < min_load:
                min_load = load
                best_agent_id = agent_id
        
        return best_agent_id
    
    def _classify_intent(self, user_input: str) -> Dict[str, Any]:
        """分类用户意图"""
        try:
            from hermes_enhanced_integration import get_hermes_manager
            hermes = get_hermes_manager()
            return hermes.classify_intent(user_input)
        except Exception as e:
            logger.warning(f"Hermes意图分类失败: {e}")
            return {"intent": "general_inquiry", "confidence": 0.5}
    
    def _get_default_agent(self) -> Tuple[str, float]:
        """获取默认智能体"""
        try:
            agent = self._registry.get_default_agent()
            return agent.agent_id, 0.1
        except AgentNotFoundError:
            agents = self._registry.list_agents()
            if agents:
                return agents[0], 0.1
            return None, 0.0
    
    def execute_agent(self, agent_id: str, user_input: str, context: Dict) -> str:
        """
        执行智能体
        
        Args:
            agent_id: 智能体ID
            user_input: 用户输入
            context: 上下文
        
        Returns:
            响应内容
        """
        load_info = self.get_load_info(agent_id)
        load_info.start_request()
        start_time = time.time()
        
        try:
            agent = self._registry.get_agent(agent_id)
            response = agent.handle(user_input, context)
            
            response_time = time.time() - start_time
            load_info.record_request(response_time)
            
            logger.debug(f"智能体 {agent_id} 执行完成，耗时: {response_time:.2f}s")
            return response
        
        except Exception as e:
            response_time = time.time() - start_time
            load_info.record_request(response_time)
            logger.error(f"智能体 {agent_id} 执行失败: {e}")
            raise
    
    def process_request(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """
        处理请求（完整流程）
        
        Args:
            user_input: 用户输入
            context: 上下文
        
        Returns:
            处理结果
        """
        try:
            # 选择智能体
            agent_id, confidence = self.select_agent(user_input, context)
            
            if not agent_id:
                return {
                    'success': False,
                    'content': "抱歉，暂时没有可用的智能体来处理您的请求。",
                    'agent_id': None
                }
            
            # 执行智能体
            response = self.execute_agent(agent_id, user_input, context or {})
            
            return {
                'success': True,
                'content': response,
                'agent_id': agent_id,
                'confidence': confidence
            }
        
        except Exception as e:
            logger.error(f"请求处理失败: {e}", exc_info=True)
            return {
                'success': False,
                'content': f"处理请求时发生错误: {str(e)}",
                'agent_id': None
            }
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """获取智能体统计信息"""
        stats = {}
        for agent_id in self._registry.list_agents():
            load_info = self.get_load_info(agent_id)
            avg_response_time = load_info.total_response_time / max(load_info.total_requests, 1)
            
            try:
                agent_info = self._registry.get_agent_info(agent_id)
                stats[agent_id] = {
                    'name': agent_info.agent_name,
                    'active_tasks': load_info.active_tasks,
                    'total_requests': load_info.total_requests,
                    'avg_response_time': round(avg_response_time, 2),
                    'last_request_time': load_info.last_request_time
                }
            except Exception as e:
                stats[agent_id] = {
                    'name': agent_id,
                    'active_tasks': load_info.active_tasks,
                    'total_requests': load_info.total_requests,
                    'avg_response_time': round(avg_response_time, 2),
                    'last_request_time': load_info.last_request_time
                }
        
        return stats
    
    def clear_intent_cache(self):
        """清除意图缓存"""
        self._intent_cache.clear()
        logger.info("意图缓存已清除")
    
    def set_context_window_size(self, size: int):
        """设置上下文窗口大小"""
        self._context_window_size = size
        logger.info(f"上下文窗口大小已设置为: {size}")
    
    def dispatch_task(self, agent_id: str, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """
        分派任务到指定智能体（兼容旧接口）
        
        Args:
            agent_id: 智能体ID
            user_input: 用户输入
            context: 上下文信息
        
        Returns:
            执行结果
        """
        try:
            response = self.execute_agent(agent_id, user_input, context or {})
            return {
                'success': True,
                'response': response,
                'data': response,
                'agent_id': agent_id
            }
        except Exception as e:
            logger.error(f"任务分派失败: {e}", exc_info=True)
            return {
                'success': False,
                'response': str(e),
                'data': str(e),
                'agent_id': agent_id
            }
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """
        获取所有智能体列表（兼容旧接口）
        
        Returns:
            智能体列表
        """
        agents = []
        for agent_id in self._registry.list_agents():
            try:
                agent_info = self._registry.get_agent_info(agent_id)
                agents.append({
                    'agent_id': agent_id,
                    'name': agent_info.agent_name,
                    'description': agent_info.description,
                    'supported_intents': agent_info.supported_intents
                })
            except Exception as e:
                logger.warning(f"获取智能体信息失败 {agent_id}: {e}")
                agents.append({
                    'agent_id': agent_id,
                    'name': agent_id,
                    'description': '',
                    'supported_intents': []
                })
        return agents
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定智能体信息（兼容旧接口）
        
        Args:
            agent_id: 智能体ID
        
        Returns:
            智能体信息，如果不存在返回None
        """
        try:
            agent_info = self._registry.get_agent_info(agent_id)
            return {
                'agent_id': agent_id,
                'name': agent_info.agent_name,
                'description': agent_info.description,
                'supported_intents': agent_info.supported_intents
            }
        except Exception as e:
            logger.warning(f"获取智能体信息失败 {agent_id}: {e}")
            return None


# 全局实例
agent_orchestrator = AgentOrchestrator()


def get_orchestrator() -> AgentOrchestrator:
    """获取智能体编排器实例"""
    return agent_orchestrator


def get_agent_orchestrator() -> AgentOrchestrator:
    """获取智能体编排器实例（兼容旧接口）"""
    return agent_orchestrator


def orchestrate_request(user_input: str, context: Dict = None) -> Dict[str, Any]:
    """
    便捷函数：编排处理请求
    
    Args:
        user_input: 用户输入
        context: 上下文
    
    Returns:
        处理结果
    """
    return agent_orchestrator.process_request(user_input, context)
