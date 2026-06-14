#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库数据脚本
"""

import sqlite3
from pathlib import Path

def check_db_data():
    """检查数据库数据"""
    db_path = Path(__file__).parent / 'school_platform.db'
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 统计学校总数
        cursor.execute('SELECT COUNT(*) FROM schools')
        school_count = cursor.fetchone()[0]
        print(f"学校总数: {school_count}")
        
        # 统计政策总数
        cursor.execute('SELECT COUNT(*) FROM policies')
        policy_count = cursor.fetchone()[0]
        print(f"政策总数: {policy_count}")
        
        # 统计文山州学校
        cursor.execute("SELECT name, city, prefecture FROM schools WHERE prefecture LIKE '%文山%'")
        wenshan_schools = cursor.fetchall()
        print(f"\n文山州学校 ({len(wenshan_schools)}所):")
        for school in wenshan_schools:
            print(f"  - {school[0]} ({school[1]})")
        
        # 检查未央中学是否存在
        cursor.execute("SELECT * FROM schools WHERE name = '丘北未央中学'")
        weiyang = cursor.fetchone()
        if weiyang:
            print("\n✓ 丘北未央中学已存在于数据库中")
        else:
            print("\n✗ 丘北未央中学不存在于数据库中")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据时出错: {e}")

if __name__ == '__main__':
    check_db_data()
