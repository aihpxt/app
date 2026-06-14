import os
import sys
import traceback
import json

os.chdir(r'D:\aiphxt-app\ai-service')

print('=== 模拟注册流程测试 ===')
print('当前目录:', os.getcwd())

try:
    import bcrypt
    print('bcrypt 版本:', bcrypt.__version__ if hasattr(bcrypt, '__version__') else 'OK')
except Exception as e:
    print('bcrypt 导入失败:', e)

try:
    from app.core.database_pool import get_db_manager
    from app.models.user import User
    print('模块导入成功')
except Exception as e:
    print('模块导入失败:', e)
    traceback.print_exc()
    sys.exit(1)

try:
    print('\n=== 测试数据库连接 ===')
    db_manager = get_db_manager()
    print('数据库管理器:', db_manager)
    print('数据库 URL:', db_manager.database_url)
    
    session = db_manager.get_session()
    print('会话获取成功')
    
    # 测试查询
    existing = session.query(User).first()
    print('查询成功, 首条用户:', existing)
    
    # 测试密码哈希
    print('\n=== 测试密码哈希 ===')
    test_password = 'test123456'
    password_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print('哈希成功:', password_hash[:30] + '...')
    
    # 测试创建用户
    print('\n=== 测试创建用户 ===')
    new_user = User(
        username='test_register_' + str(os.getpid()),
        password_hash=password_hash,
        email='test@example.com',
        phone='13800000001',
        role='student'
    )
    print('用户对象创建成功:', new_user.username)
    
    session.add(new_user)
    print('用户加入会话')
    
    session.commit()
    print('提交成功, 用户ID:', new_user.id)
    
    session.refresh(new_user)
    print('刷新成功')
    
    # 测试返回 UserInfo 格式
    from datetime import datetime
    user_info = {
        'user_id': str(new_user.id),
        'username': new_user.username,
        'email': new_user.email,
        'phone': new_user.phone,
        'roles': [new_user.role],
        'created_at': new_user.created_at.isoformat() if new_user.created_at else datetime.now().isoformat()
    }
    print('\n返回的 UserInfo:', json.dumps(user_info, ensure_ascii=False, indent=2))
    
    session.close()
    print('\n✅ 注册流程测试成功!')
    
except Exception as e:
    print('\n❌ 错误:', e)
    print('\n完整栈追踪:')
    traceback.print_exc()
    try:
        session.close()
    except:
        pass
