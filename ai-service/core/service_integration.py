#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础服务整合
整合AI服务、电话系统等基础服务
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import asyncio

from data.unified_data_access import get_unified_data_access
from agents.specialists import AGENTS, get_agent_by_id
from openclaw.agent_management import AgentManagementService

logger = logging.getLogger(__name__)


class ServiceIntegration:
    """服务整合类"""
    
    def __init__(self):
        self.data_access = get_unified_data_access()
        self.agent_manager = AgentManagementService()
        self.services = {
            'ai_service': AIServiceIntegration(),
            'call_center': CallCenterIntegration(),
            'data_service': DataServiceIntegration(),
            'user_service': UserServiceIntegration()
        }
        
        logger.info("ServiceIntegration initialized with all services")
    
    def get_service(self, service_name: str):
        """获取服务实例"""
        return self.services.get(service_name)
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        service_name = request.get('service')
        action = request.get('action')
        params = request.get('params', {})
        
        service = self.get_service(service_name)
        if not service:
            return {
                'success': False,
                'error': f'Service {service_name} not found'
            }
        
        try:
            result = service.execute(action, params)
            return {
                'success': True,
                'data': result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Service execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        status = {}
        for name, service in self.services.items():
            try:
                status[name] = {
                    'status': 'running',
                    'health': service.health_check()
                }
            except Exception as e:
                status[name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return {
            'services': status,
            'timestamp': datetime.now().isoformat()
        }


class AIServiceIntegration:
    """AI服务整合"""
    
    def __init__(self):
        self.agent_manager = AgentManagementService()
    
    def execute(self, action: str, params: Dict) -> Any:
        """执行AI服务操作"""
        if action == 'chat':
            return self.chat(params.get('message'), params.get('context'))
        elif action == 'get_agents':
            return self.get_agents()
        elif action == 'dispatch':
            return self.dispatch(params.get('message'), params.get('context'))
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def chat(self, message: str, context: Dict = None) -> str:
        """AI对话"""
        if context is None:
            context = {}
        
        result = self.agent_manager.dispatch_agent(message, context)
        return result.get('response', '')
    
    def get_agents(self) -> List[Dict]:
        """获取智能体列表"""
        return self.agent_manager.list_agents()
    
    def dispatch(self, message: str, context: Dict = None) -> Dict:
        """智能分派"""
        return self.agent_manager.dispatch_agent(message, context)
    
    def health_check(self) -> Dict:
        """健康检查"""
        try:
            agents = self.get_agents()
            return {
                'agents_count': len(agents),
                'status': 'healthy'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


class CallCenterIntegration:
    """电话系统整合"""
    
    def __init__(self):
        self.data_access = get_unified_data_access()
    
    def execute(self, action: str, params: Dict) -> Any:
        """执行电话系统操作"""
        if action == 'get_call_records':
            return self.get_call_records(params.get('phone_number'))
        elif action == 'save_call_record':
            return self.save_call_record(params)
        elif action == 'get_statistics':
            return self.get_statistics()
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def get_call_records(self, phone_number: str = None) -> List[Dict]:
        """获取通话记录"""
        return self.data_access.get_call_records(phone_number)
    
    def save_call_record(self, record: Dict) -> bool:
        """保存通话记录"""
        # 同步到用户活动
        activity = {
            'user_id': record.get('phone_number'),
            'activity_type': 'phone_call',
            'content': record,
            'channel': 'phone'
        }
        self.data_access.save_user_activity(activity)
        
        return True
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        records = self.get_call_records()
        
        stats = {
            'total_calls': len(records),
            'by_status': {},
            'by_intent': {}
        }
        
        for record in records:
            status = record.get('status', 'unknown')
            intent = record.get('intent', 'unknown')
            
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            stats['by_intent'][intent] = stats['by_intent'].get(intent, 0) + 1
        
        return stats
    
    def health_check(self) -> Dict:
        """健康检查"""
        try:
            stats = self.get_statistics()
            return {
                'total_calls': stats['total_calls'],
                'status': 'healthy'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


class DataServiceIntegration:
    """数据服务整合"""
    
    def __init__(self):
        self.data_access = get_unified_data_access()
    
    def execute(self, action: str, params: Dict) -> Any:
        """执行数据服务操作"""
        if action == 'get_school':
            return self.get_school(params.get('school_id'))
        elif action == 'get_schools':
            return self.get_schools(params.get('filters'))
        elif action == 'search':
            return self.search(params.get('keyword'), params.get('search_type'))
        elif action == 'get_policies':
            return self.get_policies(params.get('filters'))
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def get_school(self, school_id: str) -> Optional[Dict]:
        """获取学校信息"""
        return self.data_access.get_school_info(school_id)
    
    def get_schools(self, filters: Dict = None) -> List[Dict]:
        """获取学校列表"""
        return self.data_access.get_all_schools(filters)
    
    def search(self, keyword: str, search_type: str = 'all') -> List[Dict]:
        """搜索"""
        return self.data_access.search_unified(keyword, search_type)
    
    def get_policies(self, filters: Dict = None) -> List[Dict]:
        """获取政策信息"""
        return self.data_access.get_policies(filters)
    
    def health_check(self) -> Dict:
        """健康检查"""
        try:
            stats = self.data_access.get_statistics()
            return {
                'databases': len(stats),
                'status': 'healthy'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


class UserServiceIntegration:
    """用户服务整合"""
    
    def __init__(self):
        self.data_access = get_unified_data_access()
    
    def execute(self, action: str, params: Dict) -> Any:
        """执行用户服务操作"""
        if action == 'get_user':
            return self.get_user(params.get('user_id'))
        elif action == 'save_activity':
            return self.save_activity(params)
        elif action == 'get_favorites':
            return self.get_favorites(params.get('user_id'))
        elif action == 'save_favorite':
            return self.save_favorite(params.get('user_id'), params.get('school_id'))
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        return self.data_access.get_user_info(user_id)
    
    def save_activity(self, activity: Dict) -> bool:
        """保存用户活动"""
        return self.data_access.save_user_activity(activity)
    
    def get_favorites(self, user_id: str) -> List[Dict]:
        """获取用户收藏"""
        return self.data_access.get_favorites(user_id)
    
    def save_favorite(self, user_id: str, school_id: str) -> bool:
        """保存收藏"""
        return self.data_access.save_favorite(user_id, school_id)
    
    def health_check(self) -> Dict:
        """健康检查"""
        try:
            # 简单的健康检查
            return {
                'status': 'healthy'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# 全局实例
_service_integration = None


def get_service_integration() -> ServiceIntegration:
    """获取服务整合实例（单例）"""
    global _service_integration
    if _service_integration is None:
        _service_integration = ServiceIntegration()
    return _service_integration


if __name__ == '__main__':
    # 测试服务整合
    integration = ServiceIntegration()
    
    print("=" * 60)
    print("基础服务整合测试")
    print("=" * 60)
    
    # 测试服务状态
    print("\n📊 服务状态:")
    status = integration.get_service_status()
    for service_name, service_info in status['services'].items():
        print(f"{service_name}: {service_info['status']}")
    
    # 测试AI服务
    print("\n🤖 测试AI服务:")
    result = integration.process_request({
        'service': 'ai_service',
        'action': 'chat',
        'params': {
            'message': '你好，我想了解未央中学'
        }
    })
    print(f"响应: {result.get('data', '')[:100]}...")
    
    # 测试数据服务
    print("\n📚 测试数据服务:")
    result = integration.process_request({
        'service': 'data_service',
        'action': 'search',
        'params': {
            'keyword': '未央',
            'search_type': 'schools'
        }
    })
    print(f"找到 {len(result.get('data', []))} 条结果")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
