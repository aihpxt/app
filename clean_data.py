import sqlite3

db_path = r'e:\aiphxt-app\ai-service\data\school_platform.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== 开始清理数据库数据 ===')

# 1. 清理typeName字段的空格
print('1. 清理typeName字段的空格...')
cursor.execute("UPDATE schools SET typeName = TRIM(typeName)")
cursor.execute("UPDATE schools SET typeName = REPLACE(typeName, ' ', '')")
fixed_type_name = cursor.rowcount
print(f'   修复了 {fixed_type_name} 条记录')

# 2. 清理city字段的空格
print('2. 清理city字段的空格...')
cursor.execute("UPDATE schools SET city = TRIM(city)")
fixed_city = cursor.rowcount
print(f'   修复了 {fixed_city} 条记录')

# 3. 清理prefecture字段的空格
print('3. 清理prefecture字段的空格...')
cursor.execute("UPDATE schools SET prefecture = TRIM(prefecture)")
fixed_prefecture = cursor.rowcount
print(f'   修复了 {fixed_prefecture} 条记录')

# 4. 清理logo字段的反引号
print('4. 清理logo字段的反引号...')
cursor.execute("UPDATE schools SET logo = REPLACE(logo, '`', '')")
fixed_logo = cursor.rowcount
print(f'   修复了 {fixed_logo} 条记录')

# 5. 检查修复后的结果
print('\n=== 修复后检查 ===')
cursor.execute('SELECT id, name, typeName FROM schools WHERE typeName LIKE "% %" LIMIT 5')
rows = cursor.fetchall()
if len(rows) == 0:
    print('1. typeName字段空格已清理完毕')
else:
    print(f'1. 仍有 {len(rows)} 条记录typeName含空格')

cursor.execute('SELECT COUNT(*) as count FROM schools WHERE city IN ("昆明市", "曲靖市", "玉溪市", "保山市", "昭通市", "丽江市", "普洱市", "临沧市", "楚雄州", "红河州", "文山州", "西双版纳州", "大理州", "德宏州", "怒江州", "迪庆州")')
yunnan_count = cursor.fetchone()[0]
print(f'2. 云南省学校数量: {yunnan_count}')

conn.commit()
conn.close()

print('\n=== 数据清理完成 ===')
