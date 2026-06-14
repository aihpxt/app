#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据访问层
提供统一的数据访问接口，整合所有数据库
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """确保数据库文件存在"""
        db_file = Path(self.db_path)
        if not db_file.exists():
            db_file.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Database file created: {self.db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """执行查询"""
        with self.lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                conn.close()
                return results
            except Exception as e:
                logger.error(f"Query error: {e}")
                return []
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """执行更新"""
        with self.lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                logger.error(f"Update error: {e}")
                return False


class UnifiedDataAccess:
    """统一数据访问类"""
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent / 'data'
        
        self.base_dir = Path(base_dir)
        self.databases = {
            'school_platform': DatabaseManager(str(self.base_dir / 'school_platform.db')),
            'schools': DatabaseManager(str(self.base_dir / 'schools.db')),
            'wechat': DatabaseManager(str(self.base_dir / 'wechat_data.db')),
            'app': DatabaseManager(str(self.base_dir / 'app.db')),
            'call_center': DatabaseManager(str(Path(__file__).parent.parent.parent / '智能招办电话系统' / 'call_center.db'))
        }
        
        logger.info(f"UnifiedDataAccess initialized with {len(self.databases)} databases")
    
    def get_school_info(self, school_id: str) -> Optional[Dict]:
        """获取学校信息（从多个数据源）"""
        # 优先从school_platform查询
        result = self.databases['school_platform'].execute_query(
            "SELECT * FROM schools WHERE id = ? OR name = ?",
            (school_id, school_id)
        )
        
        if result:
            return result[0]
        
        # 从schools数据库查询
        result = self.databases['schools'].execute_query(
            "SELECT * FROM schools WHERE id = ? OR name = ?",
            (school_id, school_id)
        )
        
        return result[0] if result else None
    
    def get_all_schools(self, filters: Dict = None) -> List[Dict]:
        """获取所有学校"""
        query = "SELECT * FROM schools"
        params = ()
        
        if filters:
            conditions = []
            if filters.get('city'):
                conditions.append("city = ?")
                params += (filters['city'],)
            if filters.get('level'):
                conditions.append("level = ?")
                params += (filters['level'],)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        return self.databases['school_platform'].execute_query(query, params)
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """获取用户信息"""
        result = self.databases['app'].execute_query(
            "SELECT * FROM users WHERE id = ? OR phone = ?",
            (user_id, user_id)
        )
        
        return result[0] if result else None
    
    def save_user_activity(self, activity: Dict) -> bool:
        """保存用户活动"""
        query = """
        INSERT INTO user_activities 
        (user_id, activity_type, content, timestamp, channel)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            activity.get('user_id'),
            activity.get('activity_type'),
            json.dumps(activity.get('content', {}), ensure_ascii=False),
            datetime.now().isoformat(),
            activity.get('channel', 'web')
        )
        
        return self.databases['app'].execute_update(query, params)
    
    def get_policies(self, filters: Dict = None) -> List[Dict]:
        """获取政策信息"""
        query = "SELECT * FROM policies"
        params = ()
        
        if filters:
            conditions = []
            if filters.get('city'):
                conditions.append("city = ?")
                params += (filters['city'],)
            if filters.get('year'):
                conditions.append("year = ?")
                params += (filters['year'],)
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        return self.databases['school_platform'].execute_query(query, params)
    
    def get_call_records(self, phone_number: str = None) -> List[Dict]:
        """获取电话记录"""
        query = "SELECT * FROM call_records"
        params = ()
        
        if phone_number:
            query += " WHERE phone_number = ?"
            params = (phone_number,)
        
        return self.databases['call_center'].execute_query(query, params)
    
    def get_wechat_info(self, school_name: str) -> Optional[Dict]:
        """获取微信公众号信息"""
        result = self.databases['wechat'].execute_query(
            "SELECT * FROM wechat_schools WHERE school_name = ?",
            (school_name,)
        )
        
        return result[0] if result else None
    
    def save_favorite(self, user_id: str, school_id: str) -> bool:
        """保存收藏"""
        query = """
        INSERT OR REPLACE INTO favorites (user_id, school_id, created_at)
        VALUES (?, ?, ?)
        """
        params = (user_id, school_id, datetime.now().isoformat())
        
        return self.databases['app'].execute_update(query, params)
    
    def get_favorites(self, user_id: str) -> List[Dict]:
        """获取用户收藏"""
        query = """
        SELECT f.*, s.name as school_name, s.city, s.level
        FROM favorites f
        LEFT JOIN schools s ON f.school_id = s.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
        """
        
        return self.databases['app'].execute_query(query, (user_id,))
    
    def sync_data(self, source_db: str, target_db: str, table: str) -> bool:
        """数据同步"""
        try:
            # 从源数据库读取数据
            source_manager = self.databases.get(source_db)
            target_manager = self.databases.get(target_db)
            
            if not source_manager or not target_manager:
                logger.error(f"Database not found: {source_db} or {target_db}")
                return False
            
            data = source_manager.execute_query(f"SELECT * FROM {table}")
            
            # 写入目标数据库
            for row in data:
                # 构建INSERT语句
                columns = ', '.join(row.keys())
                placeholders = ', '.join(['?' for _ in row])
                values = tuple(row.values())
                
                query = f"""
                INSERT OR REPLACE INTO {table} ({columns})
                VALUES ({placeholders})
                """
                
                target_manager.execute_update(query, values)
            
            logger.info(f"Synced {len(data)} records from {source_db}.{table} to {target_db}.{table}")
            return True
        
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {}
        
        for db_name, db_manager in self.databases.items():
            try:
                # 获取表列表
                tables = db_manager.execute_query(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                
                db_stats = {}
                for table in tables:
                    table_name = table['name']
                    count = db_manager.execute_query(
                        f"SELECT COUNT(*) as count FROM {table_name}"
                    )
                    db_stats[table_name] = count[0]['count'] if count else 0
                
                stats[db_name] = db_stats
            
            except Exception as e:
                logger.error(f"Error getting stats for {db_name}: {e}")
                stats[db_name] = {"error": str(e)}
        
        return stats
    
    def search_unified(self, keyword: str, search_type: str = 'all') -> List[Dict]:
        """统一搜索"""
        results = []
        
        if search_type in ['all', 'schools']:
            # 搜索学校
            school_results = self.databases['school_platform'].execute_query(
                "SELECT * FROM schools WHERE name LIKE ? OR city LIKE ? OR description LIKE ?",
                (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
            )
            for result in school_results:
                result['type'] = 'school'
                results.append(result)
        
        if search_type in ['all', 'policies']:
            # 搜索政策
            policy_results = self.databases['school_platform'].execute_query(
                "SELECT * FROM policies WHERE title LIKE ? OR content LIKE ?",
                (f'%{keyword}%', f'%{keyword}%')
            )
            for result in policy_results:
                result['type'] = 'policy'
                results.append(result)
        
        return results


# 全局实例
_unified_data_access = None


def get_unified_data_access() -> UnifiedDataAccess:
    """获取统一数据访问实例（单例）"""
    global _unified_data_access
    if _unified_data_access is None:
        _unified_data_access = UnifiedDataAccess()
    return _unified_data_access


if __name__ == '__main__':
    # 测试统一数据访问
    uda = UnifiedDataAccess()
    
    print("=" * 60)
    print("统一数据访问层测试")
    print("=" * 60)
    
    # 获取统计信息
    stats = uda.get_statistics()
    print("\n📊 数据库统计:")
    for db_name, db_stats in stats.items():
        print(f"\n{db_name}:")
        for table, count in db_stats.items():
            if isinstance(count, int):
                print(f"  {table}: {count} 条记录")
    
    # 测试搜索
    print("\n🔍 测试搜索:")
    results = uda.search_unified('未央')
    print(f"找到 {len(results)} 条结果")
    for result in results[:3]:
        print(f"  - {result.get('name', result.get('title', '未知'))} ({result.get('type', '未知')})")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
