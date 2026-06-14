#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库结构脚本
"""

import sqlite3
from pathlib import Path

def check_db_structure(db_path):
    """检查数据库结构"""
    print(f"\n检查数据库: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("  没有找到表")
            conn.close()
            return
        
        for table in tables:
            table_name = table[0]
            print(f"  表: {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for column in columns:
                col_id, col_name, col_type, col_notnull, col_default, col_pk = column
                print(f"    列: {col_name} ({col_type})")
        
        conn.close()
    except Exception as e:
        print(f"  错误: {e}")

if __name__ == '__main__':
    base_dir = Path(__file__).parent
    
    # 检查 school_platform.db
    school_platform_db = base_dir / 'school_platform.db'
    if school_platform_db.exists():
        check_db_structure(str(school_platform_db))
    else:
        print(f"文件不存在: {school_platform_db}")
    
    # 检查 app.db
    app_db = base_dir / 'app.db'
    if app_db.exists():
        check_db_structure(str(app_db))
    else:
        print(f"文件不存在: {app_db}")
    
    # 检查 wechat_data.db
    wechat_db = base_dir / 'wechat_data.db'
    if wechat_db.exists():
        check_db_structure(str(wechat_db))
    else:
        print(f"文件不存在: {wechat_db}")
