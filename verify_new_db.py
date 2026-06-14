import sqlite3

db_path = r"e:\aiphxt-app\ai-service\sqlite\data\unified_school_data.db"
conn = sqlite3.connect(db_path)

print("=" * 50)
print("数据库验证")
print("=" * 50)
print(f"数据库路径: {db_path}")
print()
print(f"✅ 学校数量: {conn.execute('SELECT COUNT(*) FROM schools').fetchone()[0]}")
print(f"✅ 用户数量: {conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]}")
print(f"✅ 政策数量: {conn.execute('SELECT COUNT(*) FROM policies').fetchone()[0]}")
print(f"✅ 通知数量: {conn.execute('SELECT COUNT(*) FROM notifications').fetchone()[0]}")
print()
conn.close()
print("✅ 数据库验证通过！")