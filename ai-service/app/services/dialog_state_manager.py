#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话状态管理器
负责对话状态追踪、断点续传和多话题并行处理
"""

import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)


class DialogState:
    """对话状态类"""
    
    # 对话状态枚举
    class Status:
        INITIAL = 'initial'           # 初始状态
        ACTIVE = 'active'             # 进行中
        WAITING_CLARIFICATION = 'waiting_clarification'  # 待澄清
        COMPLETED = 'completed'       # 已完成
        ERROR = 'error'               # 错误状态
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.status = DialogState.Status.INITIAL
        self.current_topic = None
        self.topics = {}  # topic_id -> topic_info
        self.current_step = 0
        self.last_activity_time = datetime.now()
        self.context = {}
        self.user_profile = {}
        self.intent_history = []
        self.clarification_pending = None
        self.error_count = 0
        
    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity_time = datetime.now()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """检查对话是否过期"""
        return datetime.now() - self.last_activity_time > timedelta(minutes=timeout_minutes)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'status': self.status,
            'current_topic': self.current_topic,
            'topics': self.topics,
            'current_step': self.current_step,
            'last_activity_time': self.last_activity_time.isoformat(),
            'context': self.context,
            'user_profile': self.user_profile,
            'intent_history': self.intent_history,
            'clarification_pending': self.clarification_pending,
            'error_count': self.error_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogState':
        """从字典恢复"""
        state = cls(data['session_id'])
        state.status = data['status']
        state.current_topic = data['current_topic']
        state.topics = data['topics']
        state.current_step = data['current_step']
        state.last_activity_time = datetime.fromisoformat(data['last_activity_time'])
        state.context = data['context']
        state.user_profile = data['user_profile']
        state.intent_history = data['intent_history']
        state.clarification_pending = data['clarification_pending']
        state.error_count = data['error_count']
        return state


class DialogStateManager:
    """对话状态管理器"""
    
    def __init__(self):
        self._sessions: Dict[str, DialogState] = {}
        self._session_timeout = 30  # 默认超时30分钟
        self._max_error_count = 3   # 最大错误次数
        logger.info("对话状态管理器初始化完成")
    
    def create_session(self) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = DialogState(session_id)
        logger.info(f"创建新会话: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[DialogState]:
        """获取会话状态"""
        if session_id not in self._sessions:
            return None
        
        state = self._sessions[session_id]
        
        # 检查会话是否过期
        if state.is_expired(self._session_timeout):
            logger.warning(f"会话已过期: {session_id}")
            del self._sessions[session_id]
            return None
        
        return state
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """更新会话状态"""
        state = self.get_session(session_id)
        if not state:
            return False
        
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)
        
        state.update_activity()
        logger.debug(f"更新会话状态: {session_id}, 更新: {list(updates.keys())}")
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"删除会话: {session_id}")
            return True
        return False
    
    def set_status(self, session_id: str, status: str) -> bool:
        """设置会话状态"""
        return self.update_session(session_id, {'status': status})
    
    def add_topic(self, session_id: str, topic_name: str, 
                  topic_data: Optional[Dict[str, Any]] = None) -> str:
        """添加话题"""
        state = self.get_session(session_id)
        if not state:
            return ""
        
        topic_id = str(uuid.uuid4())[:8]
        state.topics[topic_id] = {
            'name': topic_name,
            'data': topic_data or {},
            'created_at': datetime.now().isoformat(),
            'active': False
        }
        
        # 如果是第一个话题，设为当前话题
        if not state.current_topic:
            state.current_topic = topic_id
            state.topics[topic_id]['active'] = True
        
        logger.debug(f"添加话题: {session_id}, topic_id: {topic_id}, name: {topic_name}")
        return topic_id
    
    def switch_topic(self, session_id: str, topic_id: str) -> bool:
        """切换话题"""
        state = self.get_session(session_id)
        if not state or topic_id not in state.topics:
            return False
        
        # 取消当前话题的活跃状态
        if state.current_topic in state.topics:
            state.topics[state.current_topic]['active'] = False
        
        # 设置新话题
        state.current_topic = topic_id
        state.topics[topic_id]['active'] = True
        state.update_activity()
        
        logger.debug(f"切换话题: {session_id}, topic_id: {topic_id}")
        return True
    
    def get_topics(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """获取所有话题"""
        state = self.get_session(session_id)
        if not state:
            return None
        
        topics_list = []
        for topic_id, topic_info in state.topics.items():
            topics_list.append({
                'topic_id': topic_id,
                'name': topic_info['name'],
                'active': topic_info['active'],
                'created_at': topic_info['created_at']
            })
        
        return topics_list
    
    def set_context(self, session_id: str, context: Dict[str, Any]) -> bool:
        """设置上下文"""
        return self.update_session(session_id, {'context': context})
    
    def update_context(self, session_id: str, key: str, value: Any) -> bool:
        """更新上下文中的某个字段"""
        state = self.get_session(session_id)
        if not state:
            return False
        
        state.context[key] = value
        state.update_activity()
        logger.debug(f"更新上下文: {session_id}, {key} = {value}")
        return True
    
    def get_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取上下文"""
        state = self.get_session(session_id)
        return state.context if state else None
    
    def add_intent(self, session_id: str, intent: str, confidence: float):
        """添加意图历史"""
        state = self.get_session(session_id)
        if not state:
            return False
        
        state.intent_history.append({
            'intent': intent,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        })
        
        # 保留最近10条意图记录
        if len(state.intent_history) > 10:
            state.intent_history = state.intent_history[-10:]
        
        state.update_activity()
        return True
    
    def set_clarification_pending(self, session_id: str, clarification_info: Dict[str, Any]):
        """设置待澄清信息"""
        return self.update_session(session_id, {'clarification_pending': clarification_info})
    
    def clear_clarification_pending(self, session_id: str):
        """清除待澄清信息"""
        return self.update_session(session_id, {'clarification_pending': None})
    
    def increment_error_count(self, session_id: str) -> int:
        """增加错误计数"""
        state = self.get_session(session_id)
        if not state:
            return 0
        
        state.error_count += 1
        state.update_activity()
        
        # 检查是否超过最大错误次数
        if state.error_count >= self._max_error_count:
            state.status = DialogState.Status.ERROR
            logger.warning(f"会话错误次数过多: {session_id}, 错误次数: {state.error_count}")
        
        return state.error_count
    
    def reset_error_count(self, session_id: str):
        """重置错误计数"""
        return self.update_session(session_id, {'error_count': 0})
    
    def can_continue(self, session_id: str) -> Tuple[bool, Optional[str]]:
        """检查会话是否可以继续"""
        state = self.get_session(session_id)
        if not state:
            return False, "会话不存在或已过期"
        
        if state.status == DialogState.Status.COMPLETED:
            return False, "会话已完成"
        
        if state.status == DialogState.Status.ERROR:
            return False, "会话错误次数过多"
        
        return True, None
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话摘要"""
        state = self.get_session(session_id)
        if not state:
            return None
        
        return {
            'session_id': state.session_id,
            'status': state.status,
            'current_topic': state.topics.get(state.current_topic, {}).get('name') if state.current_topic else None,
            'topic_count': len(state.topics),
            'context_keys': list(state.context.keys()),
            'intent_count': len(state.intent_history),
            'error_count': state.error_count,
            'last_activity': state.last_activity_time.isoformat()
        }
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        expired_sessions = []
        for session_id, state in self._sessions.items():
            if state.is_expired(self._session_timeout):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
        
        if expired_sessions:
            logger.info(f"清理过期会话: {len(expired_sessions)} 个")
        
        return len(expired_sessions)
    
    def get_session_count(self) -> int:
        """获取当前会话数量"""
        return len(self._sessions)


# 全局实例
dialog_state_manager = DialogStateManager()


def get_dialog_state_manager() -> DialogStateManager:
    """获取对话状态管理器实例"""
    return dialog_state_manager


if __name__ == '__main__':
    print("=" * 70)
    print("对话状态管理器测试")
    print("=" * 70)
    
    manager = DialogStateManager()
    
    # 测试1: 创建会话
    print("\n1. 测试创建会话")
    print("-" * 50)
    session_id = manager.create_session()
    print(f"创建会话ID: {session_id}")
    
    # 测试2: 获取会话状态
    print("\n2. 测试获取会话状态")
    print("-" * 50)
    state = manager.get_session(session_id)
    print(f"会话状态: {state.status}")
    print(f"当前话题: {state.current_topic}")
    
    # 测试3: 添加话题
    print("\n3. 测试添加话题")
    print("-" * 50)
    topic_id1 = manager.add_topic(session_id, '学校查询')
    topic_id2 = manager.add_topic(session_id, '志愿填报')
    print(f"添加话题1: {topic_id1} - 学校查询")
    print(f"添加话题2: {topic_id2} - 志愿填报")
    
    topics = manager.get_topics(session_id)
    print(f"\n当前话题列表:")
    for topic in topics:
        status = "活跃" if topic['active'] else "非活跃"
        print(f"  - {topic['topic_id']}: {topic['name']} ({status})")
    
    # 测试4: 切换话题
    print("\n4. 测试切换话题")
    print("-" * 50)
    manager.switch_topic(session_id, topic_id2)
    topics = manager.get_topics(session_id)
    print(f"切换后话题状态:")
    for topic in topics:
        status = "活跃" if topic['active'] else "非活跃"
        print(f"  - {topic['topic_id']}: {topic['name']} ({status})")
    
    # 测试5: 更新上下文
    print("\n5. 测试上下文管理")
    print("-" * 50)
    manager.update_context(session_id, 'score', 650)
    manager.update_context(session_id, 'school', '昆一中')
    context = manager.get_context(session_id)
    print(f"当前上下文: {context}")
    
    # 测试6: 添加意图历史
    print("\n6. 测试意图历史")
    print("-" * 50)
    manager.add_intent(session_id, '查询学校', 0.92)
    manager.add_intent(session_id, '查询分数线', 0.87)
    state = manager.get_session(session_id)
    print(f"意图历史数量: {len(state.intent_history)}")
    for intent in state.intent_history:
        print(f"  - {intent['intent']} (置信度: {intent['confidence']})")
    
    # 测试7: 设置待澄清
    print("\n7. 测试待澄清设置")
    print("-" * 50)
    manager.set_clarification_pending(session_id, {'type': 'score', 'question': '你的分数是多少？'})
    state = manager.get_session(session_id)
    print(f"待澄清信息: {state.clarification_pending}")
    manager.clear_clarification_pending(session_id)
    print(f"清除后待澄清: {state.clarification_pending}")
    
    # 测试8: 错误计数
    print("\n8. 测试错误计数")
    print("-" * 50)
    for i in range(4):
        count = manager.increment_error_count(session_id)
        print(f"第{i+1}次错误: 错误计数={count}")
    
    state = manager.get_session(session_id)
    print(f"会话状态: {state.status}")
    
    # 测试9: 会话摘要
    print("\n9. 测试会话摘要")
    print("-" * 50)
    summary = manager.get_session_summary(session_id)
    print(f"会话摘要:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # 测试10: 会话数量和清理
    print("\n10. 测试会话管理")
    print("-" * 50)
    print(f"当前会话数量: {manager.get_session_count()}")
    manager.delete_session(session_id)
    print(f"删除后会话数量: {manager.get_session_count()}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)