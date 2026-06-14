#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据同步机制
实现各系统间的数据同步
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
import threading
import time
from pathlib import Path

from data.unified_data_access import get_unified_data_access

logger = logging.getLogger(__name__)


class DataSyncManager:
    """数据同步管理器"""
    
    def __init__(self):
        self.data_access = get_unified_data_access()
        self.sync_tasks = {}
        self.sync_history = []
        self._init_sync_tasks()
    
    def _init_sync_tasks(self):
        """初始化同步任务"""
        self.sync_tasks = {
            'school_data': {
                'source': 'schools',
                'target': 'school_platform',
                'table': 'schools',
                'interval': 3600,  # 1小时
                'last_sync': None,
                'enabled': True
            },
            'wechat_data': {
                'source': 'wechat',
                'target': 'school_platform',
                'table': 'wechat_schools',
                'interval': 7200,  # 2小时
                'last_sync': None,
                'enabled': True
            },
            'call_records': {
                'source': 'call_center',
                'target': 'app',
                'table': 'call_records',
                'interval': 300,  # 5分钟
                'last_sync': None,
                'enabled': True
            },
            'user_activities': {
                'source': 'app',
                'target': 'school_platform',
                'table': 'user_activities',
                'interval': 600,  # 10分钟
                'last_sync': None,
                'enabled': True
            }
        }
        
        logger.info(f"Initialized {len(self.sync_tasks)} sync tasks")
    
    def sync_task(self, task_name: str) -> Dict[str, Any]:
        """执行同步任务"""
        task = self.sync_tasks.get(task_name)
        if not task:
            return {
                'success': False,
                'error': f'Task {task_name} not found'
            }
        
        if not task.get('enabled'):
            return {
                'success': False,
                'error': f'Task {task_name} is disabled'
            }
        
        # 检查是否需要同步
        if self._should_sync(task):
            return self._perform_sync(task_name, task)
        else:
            return {
                'success': True,
                'message': f'Task {task_name} does not need sync yet',
                'next_sync': self._get_next_sync_time(task)
            }
    
    def _should_sync(self, task: Dict) -> bool:
        """检查是否需要同步"""
        last_sync = task.get('last_sync')
        if not last_sync:
            return True
        
        interval = task.get('interval', 3600)
        elapsed = (datetime.now() - last_sync).total_seconds()
        
        return elapsed >= interval
    
    def _perform_sync(self, task_name: str, task: Dict) -> Dict[str, Any]:
        """执行同步"""
        source = task.get('source')
        target = task.get('target')
        table = task.get('table')
        
        logger.info(f"Starting sync: {source}.{table} -> {target}.{table}")
        start_time = datetime.now()
        
        try:
            # 执行同步
            success = self.data_access.sync_data(source, target, table)
            
            # 更新最后同步时间
            self.sync_tasks[task_name]['last_sync'] = datetime.now()
            
            # 记录同步历史
            sync_record = {
                'task_name': task_name,
                'source': source,
                'target': target,
                'table': table,
                'success': success,
                'start_time': start_time,
                'end_time': datetime.now(),
                'duration': (datetime.now() - start_time).total_seconds()
            }
            self.sync_history.append(sync_record)
            
            if success:
                logger.info(f"Sync completed: {task_name} in {sync_record['duration']:.2f}s")
                return {
                    'success': True,
                    'task_name': task_name,
                    'duration': sync_record['duration'],
                    'message': f'Sync completed successfully',
                    'next_sync': self._get_next_sync_time(task)
                }
            else:
                logger.error(f"Sync failed: {task_name}")
                return {
                    'success': False,
                    'task_name': task_name,
                    'error': 'Sync failed'
                }
        
        except Exception as e:
            logger.error(f"Sync error for {task_name}: {e}")
            return {
                'success': False,
                'task_name': task_name,
                'error': str(e)
            }
    
    def _get_next_sync_time(self, task: Dict) -> str:
        """获取下次同步时间"""
        interval = task.get('interval', 3600)
        next_sync = datetime.now() + timedelta(seconds=interval)
        return next_sync.isoformat()
    
    def sync_all(self) -> Dict[str, Any]:
        """同步所有任务"""
        results = {}
        
        for task_name in self.sync_tasks:
            result = self.sync_task(task_name)
            results[task_name] = result
        
        return {
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def enable_task(self, task_name: str) -> bool:
        """启用同步任务"""
        if task_name in self.sync_tasks:
            self.sync_tasks[task_name]['enabled'] = True
            logger.info(f"Sync task enabled: {task_name}")
            return True
        return False
    
    def disable_task(self, task_name: str) -> bool:
        """禁用同步任务"""
        if task_name in self.sync_tasks:
            self.sync_tasks[task_name]['enabled'] = False
            logger.info(f"Sync task disabled: {task_name}")
            return True
        return False
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        status = {}
        
        for task_name, task in self.sync_tasks.items():
            last_sync = task.get('last_sync')
            interval = task.get('interval', 3600)
            
            if last_sync:
                elapsed = (datetime.now() - last_sync).total_seconds()
                next_sync = last_sync + timedelta(seconds=interval)
                needs_sync = elapsed >= interval
            else:
                elapsed = None
                next_sync = datetime.now()
                needs_sync = True
            
            status[task_name] = {
                'enabled': task.get('enabled', False),
                'last_sync': last_sync.isoformat() if last_sync else None,
                'elapsed_seconds': elapsed,
                'interval_seconds': interval,
                'next_sync': next_sync.isoformat(),
                'needs_sync': needs_sync
            }
        
        return {
            'tasks': status,
            'total_tasks': len(self.sync_tasks),
            'enabled_tasks': len([t for t in self.sync_tasks.values() if t.get('enabled')]),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_sync_history(self, limit: int = 10) -> List[Dict]:
        """获取同步历史"""
        return self.sync_history[-limit:]
    
    def start_auto_sync(self):
        """启动自动同步"""
        def sync_loop():
            while True:
                try:
                    # 同步所有任务
                    self.sync_all()
                    
                    # 等待下一次检查
                    time.sleep(60)  # 每分钟检查一次
                
                except Exception as e:
                    logger.error(f"Auto sync error: {e}")
                    time.sleep(60)
        
        # 在后台线程中运行
        sync_thread = threading.Thread(target=sync_loop, daemon=True)
        sync_thread.start()
        
        logger.info("Auto sync started")


class RealtimeDataSync:
    """实时数据同步"""
    
    def __init__(self):
        self.data_access = get_unified_data_access()
        self.subscribers = {}
        self._init_subscribers()
    
    def _init_subscribers(self):
        """初始化订阅者"""
        self.subscribers = {
            'school_updates': [],
            'policy_updates': [],
            'user_activities': [],
            'call_records': []
        }
    
    def subscribe(self, event_type: str, callback):
        """订阅事件"""
        if event_type in self.subscribers:
            self.subscribers[event_type].append(callback)
            logger.info(f"Subscribed to {event_type}")
    
    def publish(self, event_type: str, data: Dict[str, Any]):
        """发布事件"""
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Callback error for {event_type}: {e}")
    
    def sync_school_update(self, school_id: str, update_data: Dict):
        """同步学校更新"""
        # 更新数据库
        self.data_access.execute_update(
            "UPDATE schools SET name=?, city=?, level=? WHERE id=?",
            (
                update_data.get('name'),
                update_data.get('city'),
                update_data.get('level'),
                school_id
            )
        )
        
        # 发布事件
        self.publish('school_updates', {
            'school_id': school_id,
            'update_data': update_data,
            'timestamp': datetime.now().isoformat()
        })
    
    def sync_user_activity(self, user_id: str, activity: Dict):
        """同步用户活动"""
        # 保存到数据库
        self.data_access.save_user_activity(activity)
        
        # 发布事件
        self.publish('user_activities', {
            'user_id': user_id,
            'activity': activity,
            'timestamp': datetime.now().isoformat()
        })
    
    def sync_call_record(self, call_record: Dict):
        """同步通话记录"""
        # 保存到数据库
        self.data_access.save_user_activity({
            'user_id': call_record.get('phone_number'),
            'activity_type': 'phone_call',
            'content': call_record,
            'channel': 'phone'
        })
        
        # 发布事件
        self.publish('call_records', {
            'call_record': call_record,
            'timestamp': datetime.now().isoformat()
        })


# 全局实例
_data_sync_manager = None
_realtime_sync = None


def get_data_sync_manager() -> DataSyncManager:
    """获取数据同步管理器实例（单例）"""
    global _data_sync_manager
    if _data_sync_manager is None:
        _data_sync_manager = DataSyncManager()
    return _data_sync_manager


def get_realtime_sync() -> RealtimeDataSync:
    """获取实时同步实例（单例）"""
    global _realtime_sync
    if _realtime_sync is None:
        _realtime_sync = RealtimeDataSync()
    return _realtime_sync


if __name__ == '__main__':
    # 测试数据同步
    sync_manager = DataSyncManager()
    realtime_sync = RealtimeDataSync()
    
    print("=" * 60)
    print("数据同步机制测试")
    print("=" * 60)
    
    # 获取同步状态
    print("\n📊 同步状态:")
    status = sync_manager.get_sync_status()
    print(f"总任务数: {status['total_tasks']}")
    print(f"启用任务数: {status['enabled_tasks']}")
    
    for task_name, task_status in status['tasks'].items():
        enabled = "✓" if task_status['enabled'] else "✗"
        needs_sync = "需要同步" if task_status['needs_sync'] else "无需同步"
        print(f"\n{enabled} {task_name}:")
        print(f"  状态: {needs_sync}")
        print(f"  上次同步: {task_status['last_sync']}")
        print(f"  下次同步: {task_status['next_sync']}")
    
    # 测试实时同步
    print("\n🔄 测试实时同步:")
    
    # 订阅事件
    def on_school_update(data):
        print(f"  学校更新: {data.get('school_id')}")
    
    def on_user_activity(data):
        print(f"  用户活动: {data.get('user_id')}")
    
    realtime_sync.subscribe('school_updates', on_school_update)
    realtime_sync.subscribe('user_activities', on_user_activity)
    
    # 发布事件
    print("\n发布学校更新事件:")
    realtime_sync.sync_school_update('school123', {
        'name': '未央中学',
        'city': '丘北县',
        'level': '高中'
    })
    
    print("\n发布用户活动事件:")
    realtime_sync.sync_user_activity('user123', {
        'activity_type': 'login',
        'timestamp': datetime.now().isoformat()
    })
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
