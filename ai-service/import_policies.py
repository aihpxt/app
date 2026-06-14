#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导入政策数据到数据库"""

import json
import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'school_platform.db')
JSON_PATH = os.path.join(os.path.dirname(__file__), 'openclaw', 'data', 'policies_data.json')

def import_policies():
    """导入政策数据"""
    print("开始导入政策数据...")
    
    # 读取JSON文件
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    policies = data.get('policies', [])
    print(f"从JSON文件读取到 {len(policies)} 条政策数据")
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建 policies 表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            category TEXT,
            publish_date TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 清空现有数据
    cursor.execute('DELETE FROM policies')
    print("清空现有政策数据")
    
    # 插入新数据
    inserted_count = 0
    for policy in policies:
        cursor.execute('''
            INSERT INTO policies (title, content, category, publish_date, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            policy.get('title', ''),
            policy.get('content', ''),
            policy.get('category', ''),
            policy.get('publish_date', ''),
            policy.get('source', '')
        ))
        inserted_count += 1
    
    conn.commit()
    
    # 验证导入结果
    cursor.execute('SELECT COUNT(*) FROM policies')
    count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"成功导入 {inserted_count} 条政策数据")
    print(f"数据库中共有 {count} 条政策数据")
    
    return True

if __name__ == '__main__':
    import_policies()
