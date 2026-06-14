#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并政策数据
"""

import sqlite3
import json

def get_connection():
    """获取数据库连接"""
    db_path = r"e:\aiphxt-app\ai-service\sqlite\data\unified_school_data.db"
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def merge_policies():
    """合并政策数据"""
    print("=" * 60)
    print("📋 合并政策数据")
    print("=" * 60)
    
    json_path = r"e:\aiphxt-app\ai-service\openclaw\data\policies_data.json"
    conn = get_connection()
    cursor = conn.cursor()
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    policies = data.get('policies', [])
    print(f"  JSON数据: {len(policies)} 条政策")
    
    # 查看当前政策数量
    cursor.execute("SELECT COUNT(*) FROM policies;")
    before = cursor.fetchone()[0]
    print(f"  当前数据库: {before} 条")
    
    # 合并数据
    count = 0
    for policy in policies:
        title = policy.get('title', '').strip()
        if not title:
            continue
        
        content = policy.get('content', '')
        category = policy.get('category', '招生政策')
        publish_date = policy.get('publish_date', '')
        source = policy.get('source', '')
        
        # 检查是否已存在
        cursor.execute("SELECT COUNT(*) FROM policies WHERE title = ?;", (title,))
        if cursor.fetchone()[0] > 0:
            continue
        
        cursor.execute("""
            INSERT INTO policies (title, content, category, publish_date, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP);
        """, (title, content, category, publish_date))
        count += 1
    
    conn.commit()
    print(f"  ✅ 新增: {count} 条政策")
    
    # 验证
    cursor.execute("SELECT COUNT(*) FROM policies;")
    after = cursor.fetchone()[0]
    print(f"  合并后总计: {after} 条")
    
    # 显示最新政策
    print("\n  最新政策 (Top 5):")
    cursor.execute("""
        SELECT title, category, publish_date
        FROM policies
        ORDER BY id DESC
        LIMIT 5;
    """)
    for row in cursor.fetchall():
        print(f"    - {row[0][:40]}... [{row[2]}]")
    
    conn.close()

def main():
    print("=" * 60)
    print("🔄 政策数据合并")
    print("=" * 60)
    
    merge_policies()
    
    print("\n" + "=" * 60)
    print("✅ 政策数据合并完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()