# 数据库表结构修复和 Redis 服务配置指南

## 一、数据库表结构修复

### 问题分析
从日志中发现以下数据库表结构问题：
1. `no such table: version` - 缺少版本表
2. `no such column: school_type` - schools 表缺少 school_type 字段

### 修复步骤

1. **创建版本表**
   - 版本表用于记录各个表的版本信息，便于后续的数据更新和迁移

2. **更新 schools 表**
   - 添加缺失的 school_type 字段
   - 确保其他必要字段也存在

3. **执行修复脚本**

### 修复脚本

```python
#!/usr/bin/env python3
"""
数据库表结构修复脚本
"""

import sqlite3
import os

# 数据库文件路径
data_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(data_dir, exist_ok=True)
db_file = os.path.join(data_dir, 'school_platform.db')

# 连接数据库
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print("开始修复数据库表结构...")

# 1. 创建版本表
try:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS version (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT UNIQUE NOT NULL,
            version INTEGER NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ 创建版本表成功")
except Exception as e:
    print(f"❌ 创建版本表失败: {e}")

# 2. 创建或更新 schools 表
try:
    # 检查 schools 表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schools'")
    if cursor.fetchone():
        # 表存在，检查是否缺少 school_type 字段
        cursor.execute("PRAGMA table_info(schools)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'school_type' not in columns:
            # 添加 school_type 字段
            cursor.execute("ALTER TABLE schools ADD COLUMN school_type TEXT")
            print("✅ 添加 school_type 字段成功")
        else:
            print("✅ school_type 字段已存在")
    else:
        # 表不存在，创建新表
        cursor.execute("""
            CREATE TABLE schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT,
                district TEXT,
                school_type TEXT,
                level TEXT,
                is_public INTEGER,
                is_key INTEGER,
                address TEXT,
                phone TEXT,
                website TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ 创建 schools 表成功")
except Exception as e:
    print(f"❌ 处理 schools 表失败: {e}")

# 3. 插入版本信息
try:
    # 检查 schools 表的版本信息
    cursor.execute("SELECT version FROM version WHERE table_name = 'schools'")
    version_record = cursor.fetchone()
    if version_record:
        # 更新版本信息
        cursor.execute("UPDATE version SET version = 1, last_updated = CURRENT_TIMESTAMP WHERE table_name = 'schools'")
    else:
        # 插入版本信息
        cursor.execute("INSERT INTO version (table_name, version) VALUES (?, ?)", ('schools', 1))
    print("✅ 更新版本信息成功")
except Exception as e:
    print(f"❌ 更新版本信息失败: {e}")

# 4. 提交事务并关闭连接
conn.commit()
conn.close()

print("数据库表结构修复完成！")
```

## 二、Redis 服务配置

### 问题分析
- Redis 连接失败：`Redis缓存不可用: Error 10061 connecting to localhost:6379. 由于目标计算机积极拒绝，无法连接。`
- 系统已经配置了 Redis 连接，但 Redis 服务没有运行

### 配置步骤

1. **下载和安装 Redis**
   - 访问 [Redis 官方网站](https://redis.io/download/) 下载最新版本的 Redis
   - 或者使用 Chocolatey 安装：`choco install redis-64`

2. **启动 Redis 服务**
   - 方法 1：使用 Redis 服务管理器启动
   - 方法 2：在命令行中运行：`redis-server`

3. **验证 Redis 连接**
   - 运行：`redis-cli ping`
   - 如果返回 `PONG`，说明 Redis 服务正常运行

4. **配置 Redis 连接参数**
   - 确保 `app/core/config.py` 中的 Redis 配置正确：
     ```python
     # Redis配置
     REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
     REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
     REDIS_DB = int(os.getenv("REDIS_DB", "0"))
     ```

5. **测试 Redis 缓存**
   - 启动应用后，访问 `/api/health/cache` 接口查看缓存状态

### Redis 服务管理

- **启动 Redis 服务**：`redis-server`
- **停止 Redis 服务**：`redis-cli shutdown`
- **查看 Redis 状态**：`redis-cli ping`
- **查看 Redis 信息**：`redis-cli info`

## 三、验证修复效果

1. **运行数据库修复脚本**
   ```bash
   python fix_database.py
   ```

2. **启动 Redis 服务**
   ```bash
   redis-server
   ```

3. **启动应用**
   ```bash
   python -m uvicorn app.core.app:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **测试健康检查接口**
   ```bash
   curl http://localhost:8000/api/health
   ```

5. **测试 OpenClaw 聊天接口**
   ```bash
   curl -X POST http://localhost:8000/api/v1/agents/chat -H "Content-Type: application/json" -d '{"question":"云大附中怎么样？"}'
   ```

## 四、注意事项

1. **数据库备份**：在执行修复脚本前，建议备份现有的数据库文件
2. **Redis 服务**：确保 Redis 服务在应用启动前已运行
3. **防火墙设置**：如果 Redis 服务无法连接，检查防火墙设置是否允许 6379 端口
4. **日志监控**：启动应用后，检查日志是否有错误信息

通过以上步骤，应该能够修复数据库表结构问题并配置好 Redis 服务，确保系统所有功能正常运行。
