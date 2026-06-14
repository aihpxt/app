"""
ChatService 单元测试
测试统一对话服务的核心功能
"""

import pytest
import uuid
from datetime import datetime

# 确保智能体注册
from agents.agent_registration import register_all_agents
register_all_agents()

# 导入测试目标
from app.services.chat_service import ChatService, get_chat_service, process_chat, create_session


class TestChatService:
    """ChatService 测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.chat_service = get_chat_service()
        self.test_session_id = str(uuid.uuid4())
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        # 清理测试会话
        try:
            self.chat_service.end_session(self.test_session_id)
        except:
            pass
    
    def test_create_new_session(self):
        """测试创建新会话"""
        session_id = self.chat_service.create_new_session()
        
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        
        # 验证会话信息
        session_info = self.chat_service.get_session_info(session_id)
        assert session_info['session_id'] == session_id
        assert session_info['message_count'] == 0
    
    def test_process_message_basic(self):
        """测试基本消息处理"""
        result = self.chat_service.process_message(self.test_session_id, "你好")
        
        assert result is not None
        assert isinstance(result, dict)
        assert result.get('success') == True
        assert 'content' in result
        assert isinstance(result.get('content'), str)
        assert len(result.get('content')) > 0
    
    def test_process_message_with_context(self):
        """测试上下文保持（连续对话）"""
        # 第一轮对话：询问学校信息
        result1 = self.chat_service.process_message(self.test_session_id, "师大附中怎么样")
        assert result1.get('success') == True
        
        # 第二轮对话：使用指代词
        result2 = self.chat_service.process_message(self.test_session_id, "它的分数线是多少")
        assert result2.get('success') == True
        
        # 验证响应内容
        assert 'content' in result2
        content = result2['content']
        assert isinstance(content, str)
        assert len(content) > 0
    
    def test_session_info(self):
        """测试获取会话信息"""
        # 先发送几条消息
        self.chat_service.process_message(self.test_session_id, "第一条消息")
        self.chat_service.process_message(self.test_session_id, "第二条消息")
        
        session_info = self.chat_service.get_session_info(self.test_session_id)
        
        assert session_info['session_id'] == self.test_session_id
        assert session_info['message_count'] >= 4  # 2条用户消息 + 2条助手响应
        assert session_info['is_active'] == True
    
    def test_end_session(self):
        """测试结束会话"""
        # 先创建会话并发送消息
        self.chat_service.process_message(self.test_session_id, "测试消息")
        
        # 获取会话信息确认存在
        session_info = self.chat_service.get_session_info(self.test_session_id)
        assert session_info['message_count'] > 0
        
        # 结束会话
        result = self.chat_service.end_session(self.test_session_id)
        assert result == True
        
        # 验证会话已删除
        session_info = self.chat_service.get_session_info(self.test_session_id)
        assert session_info['message_count'] == 0
    
    def test_get_conversation_history(self):
        """测试获取对话历史"""
        # 发送消息
        self.chat_service.process_message(self.test_session_id, "你好")
        self.chat_service.process_message(self.test_session_id, "再见")
        
        # 获取历史
        history = self.chat_service.get_conversation_history(self.test_session_id)
        
        assert isinstance(history, list)
        assert len(history) >= 4  # 2条用户消息 + 2条助手响应
        
        # 验证消息结构
        for msg in history:
            assert 'role' in msg
            assert 'content' in msg
            assert 'created_at' in msg
            assert msg['role'] in ['user', 'assistant']
    
    def test_process_chat_convenience_function(self):
        """测试便捷函数 process_chat"""
        session_id = str(uuid.uuid4())
        result = process_chat(session_id, "测试便捷函数")
        
        assert result is not None
        assert result.get('success') == True
        assert 'content' in result
        
        # 清理
        self.chat_service.end_session(session_id)
    
    def test_create_session_convenience_function(self):
        """测试便捷函数 create_session"""
        session_id = create_session()
        
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        
        # 验证会话存在
        session_info = self.chat_service.get_session_info(session_id)
        assert session_info['session_id'] == session_id
    
    def test_empty_message(self):
        """测试空消息处理"""
        result = self.chat_service.process_message(self.test_session_id, "")
        
        # 注意：根据当前实现，空消息可能会返回成功但内容为空，或返回失败
        # 这里验证不会抛出异常
        assert result is not None
        assert isinstance(result, dict)
    
    def test_get_agent_stats(self):
        """测试获取智能体统计信息"""
        stats = self.chat_service.get_agent_stats()
        
        assert isinstance(stats, dict)
        # 应该至少有一个智能体
        assert len(stats) >= 1
    
    def test_get_coordination_stats(self):
        """测试获取协调器统计信息"""
        stats = self.chat_service.get_coordination_stats()
        
        assert isinstance(stats, dict)
        assert 'hermes_available' in stats
        assert isinstance(stats['hermes_available'], bool)
        assert 'collaboration_mode' in stats
        assert 'registered_agents' in stats
        assert isinstance(stats['registered_agents'], int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
