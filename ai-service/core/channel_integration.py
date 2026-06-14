#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多渠道智能体调用
支持Web、电话、微信等多渠道的智能体调用
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import uuid

from agents.agent_orchestrator import get_agent_orchestrator
from data.unified_data_access import get_unified_data_access
from skills.skill_integration import get_skill_integration

logger = logging.getLogger(__name__)


class ChannelBase:
    """渠道基类"""
    
    def __init__(self, channel_type: str):
        self.channel_type = channel_type
        self.orchestrator = get_agent_orchestrator()
        self.data_access = get_unified_data_access()
        self.skill_integration = get_skill_integration()
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        raise NotImplementedError("Subclasses must implement process_request")
    
    def create_session(self, user_id: str) -> str:
        """创建会话"""
        session_id = str(uuid.uuid4())
        
        # 保存会话信息
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'channel': self.channel_type,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.data_access.save_user_activity({
            'user_id': user_id,
            'activity_type': 'session_start',
            'content': session_data,
            'channel': self.channel_type
        })
        
        return session_id
    
    def log_interaction(self, session_id: str, user_input: str, 
                      response: Dict, user_id: str):
        """记录交互"""
        interaction_data = {
            'session_id': session_id,
            'user_input': user_input,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
        self.data_access.save_user_activity({
            'user_id': user_id,
            'activity_type': 'agent_interaction',
            'content': interaction_data,
            'channel': self.channel_type
        })


class WebChannel(ChannelBase):
    """Web渠道"""
    
    def __init__(self):
        super().__init__('web')
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理Web请求"""
        user_id = request.get('user_id', 'anonymous')
        user_input = request.get('message', '')
        session_id = request.get('session_id')
        context = request.get('context', {})
        
        # 创建会话（如果不存在）
        if not session_id:
            session_id = self.create_session(user_id)
        
        # 调用智能体
        result = self.orchestrator.dispatch(user_input, context)
        
        # 记录交互
        self.log_interaction(session_id, user_input, result, user_id)
        
        # 返回结果
        return {
            'success': True,
            'session_id': session_id,
            'channel': 'web',
            'response': result.get('response'),
            'agent': result.get('agent'),
            'skills_used': result.get('skills_used', []),
            'timestamp': result.get('timestamp')
        }


class PhoneChannel(ChannelBase):
    """电话渠道"""
    
    def __init__(self):
        super().__init__('phone')
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理电话请求"""
        call_id = request.get('call_id')
        phone_number = request.get('phone_number')
        user_input = request.get('dtmf_input', '')  # DTMF按键输入
        voice_input = request.get('voice_input', '')  # 语音识别结果
        context = request.get('context', {})
        
        # 确定用户输入
        if voice_input:
            user_input = voice_input
        elif user_input:
            user_input = user_input
        else:
            return {
                'success': False,
                'error': 'No input provided'
            }
        
        # 创建会话
        session_id = self.create_session(phone_number)
        
        # 调用智能体
        result = self.orchestrator.dispatch(user_input, context)
        
        # 记录交互
        self.log_interaction(session_id, user_input, result, phone_number)
        
        # 保存通话记录
        self._save_call_record(call_id, phone_number, result)
        
        # 返回结果（电话系统需要语音输出）
        return {
            'success': True,
            'session_id': session_id,
            'channel': 'phone',
            'call_id': call_id,
            'response': result.get('response'),
            'agent': result.get('agent'),
            'voice_output': self._text_to_speech(result.get('response', '')),
            'timestamp': result.get('timestamp')
        }
    
    def _save_call_record(self, call_id: str, phone_number: str, 
                         result: Dict):
        """保存通话记录"""
        call_record = {
            'call_id': call_id,
            'phone_number': phone_number,
            'call_time': datetime.now(),
            'duration': 0,
            'call_type': 'inbound',
            'status': 'completed',
            'intent': result.get('intent'),
            'agent': result.get('agent')
        }
        
        # 这里应该调用电话系统的数据库保存
        # 目前使用统一数据访问层
        self.data_access.save_user_activity({
            'user_id': phone_number,
            'activity_type': 'phone_call',
            'content': call_record,
            'channel': 'phone'
        })
    
    def _text_to_speech(self, text: str) -> str:
        """文本转语音（模拟）"""
        # 这里应该调用实际的TTS服务
        # 目前返回原始文本
        return text


class WechatChannel(ChannelBase):
    """微信渠道"""
    
    def __init__(self):
        super().__init__('wechat')
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理微信请求"""
        openid = request.get('openid')
        message = request.get('message', '')
        msg_type = request.get('msg_type', 'text')
        context = request.get('context', {})
        
        # 创建会话
        session_id = self.create_session(openid)
        
        # 处理不同类型的消息
        if msg_type == 'text':
            result = self.orchestrator.dispatch(message, context)
        elif msg_type == 'voice':
            # 语音消息需要ASR
            voice_text = self._speech_to_text(request.get('media_id'))
            result = self.orchestrator.dispatch(voice_text, context)
        else:
            result = {
                'success': False,
                'error': f'Unsupported message type: {msg_type}'
            }
        
        # 记录交互
        self.log_interaction(session_id, message, result, openid)
        
        # 返回结果（微信需要文本回复）
        return {
            'success': True,
            'session_id': session_id,
            'channel': 'wechat',
            'openid': openid,
            'response': result.get('response'),
            'agent': result.get('agent'),
            'msg_type': 'text',
            'timestamp': result.get('timestamp')
        }
    
    def _speech_to_text(self, media_id: str) -> str:
        """语音转文本（模拟）"""
        # 这里应该调用实际的ASR服务
        # 目前返回模拟文本
        return "语音识别结果"


class ChannelIntegration:
    """渠道集成管理器"""
    
    def __init__(self):
        self.channels = {
            'web': WebChannel(),
            'phone': PhoneChannel(),
            'wechat': WechatChannel()
        }
        
        # 统一用户画像
        self.unified_profiles = {}
        
        logger.info(f"ChannelIntegration initialized with {len(self.channels)} channels")
    
    def get_channel(self, channel_type: str) -> Optional[ChannelBase]:
        """获取渠道实例"""
        return self.channels.get(channel_type)
    
    def process_request(self, channel_type: str, 
                       request: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求（统一入口）"""
        channel = self.get_channel(channel_type)
        if not channel:
            return {
                'success': False,
                'error': f'Channel {channel_type} not found'
            }
        
        try:
            return channel.process_request(request)
        except Exception as e:
            logger.error(f"Channel processing error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_unified_profile(self, user_id: str) -> Dict[str, Any]:
        """获取统一用户画像"""
        if user_id not in self.unified_profiles:
            # 从各渠道收集用户信息
            profile = {
                'user_id': user_id,
                'channels': {},
                'activities': [],
                'preferences': {}
            }
            
            # 从数据访问层获取用户活动
            activities = self.data_access.get_user_activities(user_id)
            
            # 按渠道分组
            for activity in activities:
                channel = activity.get('channel', 'unknown')
                if channel not in profile['channels']:
                    profile['channels'][channel] = []
                
                profile['channels'][channel].append(activity)
                profile['activities'].append(activity)
            
            self.unified_profiles[user_id] = profile
        
        return self.unified_profiles[user_id]
    
    def sync_across_channels(self, user_id: str, 
                            message: str, source_channel: str):
        """跨渠道同步消息"""
        # 获取用户的所有活跃会话
        profile = self.get_unified_profile(user_id)
        
        # 向其他渠道推送消息
        for channel_type in self.channels:
            if channel_type != source_channel:
                # 这里应该实现实际的消息推送逻辑
                logger.info(f"Syncing message to {channel_type} for user {user_id}")
    
    def get_channel_stats(self) -> Dict[str, Any]:
        """获取渠道统计"""
        stats = {}
        
        for channel_type, channel in self.channels.items():
            stats[channel_type] = {
                'type': channel_type,
                'status': 'active',
                'sessions': len([s for s in self.unified_profiles.values() 
                               if channel_type in s.get('channels', {})])
            }
        
        return {
            'channels': stats,
            'total_channels': len(self.channels),
            'total_profiles': len(self.unified_profiles),
            'timestamp': datetime.now().isoformat()
        }


# 全局实例
_channel_integration = None


def get_channel_integration() -> ChannelIntegration:
    """获取渠道集成实例（单例）"""
    global _channel_integration
    if _channel_integration is None:
        _channel_integration = ChannelIntegration()
    return _channel_integration


if __name__ == '__main__':
    # 测试渠道集成
    integration = ChannelIntegration()
    
    print("=" * 60)
    print("多渠道智能体调用测试")
    print("=" * 60)
    
    # 测试Web渠道
    print("\n🌐 测试Web渠道:")
    web_request = {
        'user_id': 'user123',
        'message': '我想了解未央中学',
        'context': {}
    }
    result = integration.process_request('web', web_request)
    print(f"响应: {result.get('response', '')[:100]}...")
    print(f"智能体: {result.get('agent')}")
    
    # 测试电话渠道
    print("\n📞 测试电话渠道:")
    phone_request = {
        'call_id': 'CALL001',
        'phone_number': '13800138000',
        'voice_input': '我想了解招生范围',
        'context': {}
    }
    result = integration.process_request('phone', phone_request)
    print(f"响应: {result.get('response', '')[:100]}...")
    print(f"智能体: {result.get('agent')}")
    
    # 测试微信渠道
    print("\n💬 测试微信渠道:")
    wechat_request = {
        'openid': 'openid123',
        'message': '我想了解学费',
        'msg_type': 'text',
        'context': {}
    }
    result = integration.process_request('wechat', wechat_request)
    print(f"响应: {result.get('response', '')[:100]}...")
    print(f"智能体: {result.get('agent')}")
    
    # 获取渠道统计
    print("\n📊 渠道统计:")
    stats = integration.get_channel_stats()
    print(f"总渠道数: {stats['total_channels']}")
    print(f"总用户数: {stats['total_profiles']}")
    for channel_type, channel_stats in stats['channels'].items():
        print(f"  {channel_type}: {channel_stats['sessions']} 个活跃会话")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
