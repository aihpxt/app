#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库优化脚本
为频繁查询的字段添加索引
"""

import sqlite3
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """数据库优化器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def connect(self) -> sqlite3.Connection:
        """连接数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            return None
    
    def add_index(self, table: str, column: str, index_name: str = None):
        """添加索引"""
        if not index_name:
            index_name = f"idx_{table}_{column}"
        
        conn = self.connect()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            # 检查索引是否已存在
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name=?
            """, (index_name,))
            
            if cursor.fetchone():
                logger.info(f"索引 {index_name} 已存在，跳过")
                conn.close()
                return True
            
            # 创建索引
            cursor.execute(f"""
                CREATE INDEX {index_name} 
                ON {table} ({column})
            """)
            conn.commit()
            logger.info(f"成功为 {table}.{column} 添加索引 {index_name}")
            conn.close()
            return True
        except Exception as e:
            logger.error(f"添加索引失败: {e}")
            conn.close()
            return False
    
    def add_compound_index(self, table: str, columns: list, index_name: str = None):
        """添加复合索引"""
        if not index_name:
            index_name = f"idx_{table}_{'_'.join(columns)}"
        
        conn = self.connect()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            # 检查索引是否已存在
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name=?
            """, (index_name,))
            
            if cursor.fetchone():
                logger.info(f"索引 {index_name} 已存在，跳过")
                conn.close()
                return True
            
            # 创建复合索引
            columns_str = ', '.join(columns)
            cursor.execute(f"""
                CREATE INDEX {index_name} 
                ON {table} ({columns_str})
            """)
            conn.commit()
            logger.info(f"成功为 {table}.{columns_str} 添加复合索引 {index_name}")
            conn.close()
            return True
        except Exception as e:
            logger.error(f"添加复合索引失败: {e}")
            conn.close()
            return False
    
    def optimize(self):
        """优化数据库"""
        # 这里可以添加具体的优化操作
        pass

class SchoolPlatformOptimizer(DatabaseOptimizer):
    """学校平台数据库优化器"""
    
    def optimize(self):
        """优化学校平台数据库"""
        logger.info("开始优化 school_platform.db")
        
        # users 表索引
        self.add_index('users', 'id')
        self.add_index('users', 'username')
        self.add_index('users', 'email')
        
        # schools 表索引
        self.add_index('schools', 'id')
        self.add_index('schools', 'name')
        self.add_index('schools', 'city')
        self.add_index('schools', 'district')
        self.add_index('schools', 'level')
        self.add_index('schools', 'type')
        
        # policies 表索引
        self.add_index('policies', 'id')
        self.add_index('policies', 'category')
        self.add_index('policies', 'publish_date')
        
        # user_activities 表索引
        self.add_index('user_activities', 'id')
        self.add_index('user_activities', 'username')
        self.add_index('user_activities', 'activity_type')
        self.add_index('user_activities', 'timestamp')
        
        # favorites 表索引
        self.add_index('favorites', 'id')
        self.add_index('favorites', 'username')
        self.add_index('favorites', 'school_id')
        self.add_index('favorites', 'created_at')
        
        # collections 表索引
        self.add_index('collections', 'id')
        self.add_index('collections', 'username')
        self.add_index('collections', 'item_type')
        
        # notifications 表索引
        self.add_index('notifications', 'id')
        self.add_index('notifications', 'username')
        self.add_index('notifications', 'is_read')
        
        # chat_sessions 表索引
        self.add_index('chat_sessions', 'id')
        self.add_index('chat_sessions', 'user_id')
        
        # chat_messages 表索引
        self.add_index('chat_messages', 'id')
        self.add_index('chat_messages', 'session_id')
        
        logger.info("school_platform.db 优化完成")

class AppDatabaseOptimizer(DatabaseOptimizer):
    """应用数据库优化器"""
    
    def optimize(self):
        """优化应用数据库"""
        logger.info("开始优化 app.db")
        
        # wechat_articles 表索引
        self.add_index('wechat_articles', 'id')
        self.add_index('wechat_articles', 'title')
        self.add_index('wechat_articles', 'platform')
        self.add_index('wechat_articles', 'keyword')
        
        # bytedance_content 表索引
        self.add_index('bytedance_content', 'id')
        self.add_index('bytedance_content', 'title')
        self.add_index('bytedance_content', 'platform')
        self.add_index('bytedance_content', 'keyword')
        
        # school_info 表索引
        self.add_index('school_info', 'id')
        self.add_index('school_info', 'name')
        self.add_index('school_info', 'city')
        self.add_index('school_info', 'type')
        self.add_index('school_info', 'level')
        
        # exam_policy 表索引
        self.add_index('exam_policy', 'id')
        self.add_index('exam_policy', 'title')
        self.add_index('exam_policy', 'region')
        
        # app_images 表索引
        self.add_index('app_images', 'id')
        self.add_index('app_images', 'filename')
        
        # image_info 表索引
        self.add_index('image_info', 'id')
        self.add_index('image_info', 'filename')
        self.add_index('image_info', 'type')
        
        logger.info("app.db 优化完成")

class WechatDatabaseOptimizer(DatabaseOptimizer):
    """微信数据库优化器"""
    
    def optimize(self):
        """优化微信数据库"""
        logger.info("开始优化 wechat_data.db")
        
        # wechat_articles 表索引
        self.add_index('wechat_articles', 'id')
        self.add_index('wechat_articles', 'title')
        self.add_index('wechat_articles', 'source')
        self.add_index('wechat_articles', 'category')
        
        # wechat_accounts 表索引
        self.add_index('wechat_accounts', 'id')
        self.add_index('wechat_accounts', 'name')
        self.add_index('wechat_accounts', 'wechat_id')
        
        # policies 表索引
        self.add_index('policies', 'id')
        self.add_index('policies', 'title')
        self.add_index('policies', 'publish_time')
        
        # school_updates 表索引
        self.add_index('school_updates', 'id')
        self.add_index('school_updates', 'school_name')
        self.add_index('school_updates', 'update_type')
        
        # schools 表索引
        self.add_index('schools', 'id')
        self.add_index('schools', 'name')
        self.add_index('schools', 'city')
        self.add_index('schools', 'district')
        self.add_index('schools', 'school_type')
        
        # user_feedback 表索引
        self.add_index('user_feedback', 'id')
        self.add_index('user_feedback', 'school_id')
        self.add_index('user_feedback', 'status')
        
        logger.info("wechat_data.db 优化完成")

class CallCenterDatabaseOptimizer(DatabaseOptimizer):
    """电话中心数据库优化器"""
    
    def optimize(self):
        """优化电话中心数据库"""
        logger.info("开始优化 call_center.db")
        
        # 跳过不存在的数据库
        logger.info("call_center.db 不存在，跳过")
        
        logger.info("call_center.db 优化完成")

def main():
    """主函数"""
    base_dir = Path(__file__).parent
    
    # 优化 school_platform.db
    school_platform_db = base_dir / 'school_platform.db'
    if school_platform_db.exists():
        optimizer = SchoolPlatformOptimizer(str(school_platform_db))
        optimizer.optimize()
    else:
        logger.warning(f"文件不存在: {school_platform_db}")
    
    # 优化 app.db
    app_db = base_dir / 'app.db'
    if app_db.exists():
        optimizer = AppDatabaseOptimizer(str(app_db))
        optimizer.optimize()
    else:
        logger.warning(f"文件不存在: {app_db}")
    
    # 优化 wechat_data.db
    wechat_db = base_dir / 'wechat_data.db'
    if wechat_db.exists():
        optimizer = WechatDatabaseOptimizer(str(wechat_db))
        optimizer.optimize()
    else:
        logger.warning(f"文件不存在: {wechat_db}")
    
    # 优化 call_center.db
    call_center_db = base_dir.parent.parent / '智能招办电话系统' / 'call_center.db'
    if call_center_db.exists():
        optimizer = CallCenterDatabaseOptimizer(str(call_center_db))
        optimizer.optimize()
    else:
        logger.warning(f"文件不存在: {call_center_db}")
    
    logger.info("数据库优化完成")

if __name__ == '__main__':
    main()
