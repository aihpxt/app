#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect(r'E:\aiphxt-app\ai-service\data\unified_school_data.db')
cursor = conn.cursor()

# 检查表
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('所有表:', [t[0] for t in tables])

# 检查 schools 表
if 'schools' in [t[0] for t in tables]:
    count = cursor.execute('SELECT COUNT(*) FROM schools').fetchone()[0]
    print(f'schools 表记录数: {count}')

    # 检查表结构
    cols = cursor.execute('PRAGMA table_info(schools)').fetchall()
    print('schools 表结构:')
    for col in cols:
        print(f'  {col}')

    # 前3条数据
    rows = cursor.execute('SELECT id, name, city, type FROM schools LIMIT 3').fetchall()
    print('前3条数据:')
    for row in rows:
        print(f'  {row}')
else:
    print('没有找到 schools 表')

conn.close()
