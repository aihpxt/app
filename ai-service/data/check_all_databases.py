#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查所有数据库文件的学校数据"""

import sqlite3
import os
from pathlib import Path

data_dir = Path(r'E:\aiphxt-app\ai-service\data')
dbs_to_check = [
    'school_platform.db',
    'unified_school_data.db',
    'wechat_data.db',
    'backups/school_platform_20260522_125029.db',
    'backups/school_platform_20260521_124931.db'
]

def check_db(db_path):
    print(f"\n{'='*60}")
    print(f"📁 {db_path}")
    print('='*60)

    if not db_path.exists():
        print(f"   ❌ 文件不存在")
        return

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 获取所有表
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        table_names = [t[0] for t in tables]

        print(f"   📊 所有表: {len(table_names)} 个")
        print(f"   表名: {[t for t in table_names if not t.startswith('sqlite')]}")

        # 检查学校表
        school_count = 0
        school_fields = []

        if 'schools' in table_names:
            school_count = cursor.execute('SELECT COUNT(*) FROM schools').fetchone()[0]
            school_fields = [desc[0] for desc in cursor.execute('PRAGMA table_info(schools)').fetchall()]
        elif 'school' in table_names:
            school_count = cursor.execute('SELECT COUNT(*) FROM school').fetchone()[0]
            school_fields = [desc[0] for desc in cursor.execute('PRAGMA table_info(school)').fetchall()]

        print(f"\n   🏫 学校表数据:")
        print(f"      记录数: {school_count} 条")
        if school_fields:
            print(f"      字段: {school_fields}")

        # 检查是否有重复学校
        if 'schools' in table_names:
            dup_check = cursor.execute('''
                SELECT name, COUNT(*) as cnt
                FROM schools
                GROUP BY name
                HAVING COUNT(*) > 1
            ''').fetchall()
            if dup_check:
                print(f"      ⚠️ 重复学校: {len(dup_check)} 组")
                for name, cnt in dup_check[:5]:
                    print(f"         - {name}: {cnt}条")
            else:
                print(f"      ✅ 无重复学校")

            # 检查关键字段的完整性
            null_names = cursor.execute('SELECT COUNT(*) FROM schools WHERE name IS NULL OR name = ""').fetchone()[0]
            null_cities = cursor.execute('SELECT COUNT(*) FROM schools WHERE city IS NULL OR city = ""').fetchone()[0]

            print(f"      📋 数据完整性:")
            print(f"         - name为空: {null_names}")
            print(f"         - city为空: {null_cities}")

            # 显示样例数据
            samples = cursor.execute('SELECT id, name, city, type, is_public FROM schools LIMIT 3').fetchall()
            print("      📝 样例数据:")
            for s in samples:
                print(f"         {s}")

        conn.close()

    except Exception as e:
        print(f"   ❌ 错误: {e}")

# 检查后端数据库
backend_db = Path(r'E:\aiphxt-app\backend\src\main\resources\aiphxt.db')
if backend_db.exists():
    check_db(backend_db)
else:
    print(f"\n⚠️ 后端数据库不存在: {backend_db}")

# 检查 AI service 数据库
for db_name in dbs_to_check:
    db_path = data_dir / db_name
    check_db(db_path)

print("\n" + "="*60)
print("💡 建议:")
print("   1. 统一使用 unified_school_data.db 作为主数据源")
print("   2. 清理重复数据，保留最新最完整的数据")
print("   3. 同步到后端 aiphxt.db")
print("="*60)
