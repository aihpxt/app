import os
import sqlite3

os.chdir(r'D:\aiphxt-app\ai-service')

print('=== 检查 app.db 的 users 表 ===')
conn = sqlite3.connect('app.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
print('users 表结构:')
for col in columns:
    print(f'  {col}')

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
print(f'\n现有记录数: {len(rows)}')
for row in rows:
    print(f'  {row}')
conn.close()

print()
print('=== 检查 sqlite/data/unified_school_data.db 的 users 表 ===')
conn2 = sqlite3.connect('sqlite/data/unified_school_data.db')
cursor2 = conn2.cursor()

cursor2.execute("PRAGMA table_info(users)")
columns2 = cursor2.fetchall()
print('users 表结构:')
for col in columns2:
    print(f'  {col}')

cursor2.execute("SELECT * FROM users")
rows2 = cursor2.fetchall()
print(f'\n现有记录数: {len(rows2)}')
for row in rows2[:5]:
    print(f'  {row}')
conn2.close()
