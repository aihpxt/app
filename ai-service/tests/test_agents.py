"""
智能体模块单元测试
测试智能体注册中心、编排器和协调器的核心功能
"""

import pytest
import uuid

# 确保智能体注册
from agents.agent_registration import register_all_agents
register_all_agents()

# 导入测试目标
from agents.registry import AgentRegistry, get_registry, AgentNotFoundError
from agents.base_agent import BaseAgent, AgentInfo
from agents.agent_orchestrator import AgentOrchestrator, get_orchestrator, DispatchStrategy
from hermes_agent_coordinator import HermesAgentCoordinator, get_coordinator, CollaborationMode


class TestAgentRegistry:
    """智能体注册中心测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.registry = get_registry()
    
    def test_list_agents(self):
        """测试列出所有智能体"""
        agents = self.registry.list_agents()
        
        assert isinstance(agents, list)
        assert len(agents) >= 1  # 至少有一个默认智能体
    
    def test_get_agent(self):
        """测试获取智能体"""
        agents = self.registry.list_agents()
        if agents:
            agent_id = agents[0]
            agent = self.registry.get_agent(agent_id)
            
            assert agent is not None
            assert isinstance(agent, BaseAgent)
            assert agent.agent_id == agent_id
    
    def test_get_agent_info(self):
        """测试获取智能体信息"""
        agents = self.registry.list_agents()
        if agents:
            agent_id = agents[0]
            info = self.registry.get_agent_info(agent_id)
            
            assert info is not None
            assert isinstance(info, AgentInfo)
            assert info.agent_id == agent_id
            assert isinstance(info.agent_name, str)
    
    def test_get_all_agents_info(self):
        """测试获取所有智能体信息"""
        info_list = self.registry.get_all_agents_info()
        
        assert isinstance(info_list, list)
        for info in info_list:
            assert isinstance(info, AgentInfo)
    
    def test_get_default_agent(self):
        """测试获取默认智能体"""
        agent = self.registry.get_default_agent()
        
        assert agent is not None
        assert isinstance(agent, BaseAgent)
    
    def test_find_agents_for_intent(self):
        """测试查找支持指定意图的智能体"""
        intent = "school_inquiry"
        agents = self.registry.find_agents_for_intent(intent)
        
        assert isinstance(agents, list)
    
    def test_get_stats(self):
        """测试获取注册中心统计信息"""
        stats = self.registry.get_stats()
        
        assert isinstance(stats, dict)
        assert 'total_agents' in stats
        assert isinstance(stats['total_agents'], int)
        assert 'has_default_agent' in stats
        assert isinstance(stats['has_default_agent'], bool)


class TestAgentOrchestrator:
    """智能体编排器测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.orchestrator = get_orchestrator()
    
    def test_select_agent_basic(self):
        """测试选择智能体"""
        agent_id, confidence = self.orchestrator.select_agent("你好")
        
        assert agent_id is not None
        assert isinstance(agent_id, str)
        assert isinstance(confidence, float)
        assert confidence >= 0.0
        assert confidence <= 1.0
    
    def test_select_agent_with_context(self):
        """测试带上下文选择智能体"""
        context = {
            'history': [],
            'user_profile': {}
        }
        agent_id, confidence = self.orchestrator.select_agent("师大附中怎么样", context)
        
        assert agent_id is not None
        assert isinstance(confidence, float)
    
    def test_process_request(self):
        """测试处理请求"""
        result = self.orchestrator.process_request("测试消息")
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'content' in result
    
    def test_set_strategy(self):
        """测试设置调度策略"""
        strategies = [
            DispatchStrategy.INTENT_BASED,
            DispatchStrategy.CONFIDENCE_BASED,
            DispatchStrategy.ROUND_ROBIN,
            DispatchStrategy.LOAD_BALANCED,
            DispatchStrategy.HYBRID
        ]
        
        for strategy in strategies:
            self.orchestrator.set_strategy(strategy)
            # 验证策略设置后仍能正常工作
            agent_id, confidence = self.orchestrator.select_agent("测试")
            assert agent_id is not None
    
    def test_get_agent_stats(self):
        """测试获取智能体统计信息"""
        stats = self.orchestrator.get_agent_stats()
        
        assert isinstance(stats, dict)


class TestHermesAgentCoordinator:
    """Hermes-智能体协调器测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.coordinator = get_coordinator()
        self.test_session_id = str(uuid.uuid4())
    
    def test_analyze_and_guide(self):
        """测试分析和指导功能"""
        guidance = self.coordinator.analyze_and_guide(self.test_session_id, "你好")
        
        assert isinstance(guidance, dict)
        assert 'intent' in guidance
        assert 'emotion' in guidance
        assert 'recommended_agents' in guidance
        assert isinstance(guidance['recommended_agents'], list)
    
    def test_process_request(self):
        """测试处理请求"""
        result = self.coordinator.process_request(self.test_session_id, "测试消息")
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'content' in result
    
    def test_set_collaboration_mode(self):
        """测试设置协作模式"""
        modes = [
            CollaborationMode.PASSIVE,
            CollaborationMode.ACTIVE,
            CollaborationMode.GUIDED,
            CollaborationMode.FULL_INTEGRATION
        ]
        
        for mode in modes:
            self.coordinator.set_collaboration_mode(mode)
            # 验证模式设置后仍能正常工作
            result = self.coordinator.process_request(self.test_session_id, "测试")
            assert result.get('success') == True
    
    def test_get_coordination_stats(self):
        """测试获取协调器统计信息"""
        stats = self.coordinator.get_coordination_stats()
        
        assert isinstance(stats, dict)
        assert 'hermes_available' in stats
        assert isinstance(stats['hermes_available'], bool)
        assert 'collaboration_mode' in stats
        assert 'registered_agents' in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
