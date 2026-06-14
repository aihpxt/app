import os
import sys

os.chdir(r'D:\aiphxt-app\ai-service')

print('=== 数据库配置检查 ===')
print('环境变量 DATABASE_URL:', os.environ.get('DATABASE_URL', '<未设置>'))
print('默认 DATABASE_URL: sqlite:///./app.db')
print('当前目录:', os.getcwd())

for db_file in ['app.db', 'sqlite/data/unified_school_data.db', 'data/school_platform.db']:
    path = os.path.join(os.getcwd(), db_file)
    exists = os.path.exists(path)
    print(f'  {db_file}: {"存在" if exists else "不存在"} ({path})')

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import NullPool

print()
print('=== SQLAlchemy 测试 (app.db) ===')
db_url = 'sqlite:///./app.db'
print('尝试连接:', db_url)
try:
    engine = create_engine(db_url, connect_args={'check_same_thread': False}, poolclass=NullPool)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print('表列表:', tables)
    print('是否存在 users 表:', any('users' in t.lower() for t in tables))
except Exception as e:
    print('错误:', e)

print()
print('=== 统一数据库检查 (sqlite/data/unified_school_data.db) ===')
db_url2 = 'sqlite:///sqlite/data/unified_school_data.db'
print('尝试连接:', db_url2)
try:
    engine2 = create_engine(db_url2, connect_args={'check_same_thread': False}, poolclass=NullPool)
    inspector2 = inspect(engine2)
    tables2 = inspector2.get_table_names()
    print('表列表:', tables2)
    print('是否存在 users 表:', any('users' in t.lower() for t in tables2))
except Exception as e:
    print('错误:', e)

print()
print('=== 测试注册流程 (模拟) ===')
try:
    import bcrypt
    from app.models.user import User, Base
    print('导入 User 模型成功')
    print('User 模型表名:', User.__tablename__)
    print('User 模型字段:', [c.name for c in User.__table__.columns])
except Exception as e:
    print('导入失败:', e)
    import traceback
    traceback.print_exc()
