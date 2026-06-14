#!/usr/bin/env python3
import sqlite3

db_path = r'E:\aiphxt-app\ai-service\data\unified_school_data.db'
print(f"测试数据库: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 测试查询
    cursor.execute("SELECT COUNT(*) FROM schools")
    count = cursor.fetchone()[0]
    print(f"学校数量: {count}")

    # 获取前3条数据
    cursor.execute("SELECT id, name, city FROM schools LIMIT 3")
    rows = cursor.fetchall()
    print("前3条数据:")
    for row in rows:
        print(f"  {row}")

    conn.close()
    print("数据库连接测试成功!")
except Exception as e:
    print(f"数据库连接测试失败: {e}")
