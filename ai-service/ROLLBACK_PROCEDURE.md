# AI服务系统回滚流程文档

## 文档版本
| 版本 | 日期 | 作者 | 描述 |
|------|------|------|------|
| 1.0 | 2026-05-17 | 运维团队 | 初始版本 |

---

## 1. 回滚触发条件定义

### 1.1 触发条件分类

| 触发类别 | 触发条件 | 严重程度 | 回滚优先级 |
|----------|----------|----------|------------|
| **服务故障** | API服务持续5分钟无法响应 | 高 | P0 |
| **服务故障** | 服务进程崩溃且自动重启失败超过3次 | 高 | P0 |
| **数据异常** | 数据库数据损坏或丢失 | 高 | P0 |
| **数据异常** | 缓存数据与数据库数据不一致且无法自动同步 | 中 | P1 |
| **功能故障** | 核心业务功能完全不可用 | 高 | P0 |
| **功能故障** | 核心业务功能响应时间超过10秒持续5分钟 | 中 | P1 |
| **性能问题** | CPU使用率持续超过90%达10分钟 | 中 | P1 |
| **性能问题** | 内存使用率持续超过85%达10分钟 | 中 | P1 |
| **安全事件** | 检测到未授权访问或数据泄露 | 高 | P0 |
| **部署失败** | 新版本部署后服务无法启动 | 高 | P0 |
| **部署失败** | 新版本引入严重bug导致业务中断 | 高 | P0 |

### 1.2 触发条件检测机制

#### 1.2.1 自动检测
- **健康检查监控**: 系统监控服务每分钟检查 `/api/health` 接口
- **告警阈值**: 
  - 连续3次健康检查失败触发告警
  - 响应时间超过5秒触发告警
  - 服务不可用超过1分钟触发自动回滚评估

#### 1.2.2 手动触发
- 运维人员通过监控面板手动触发回滚
- 紧急情况下通过命令行直接执行回滚脚本

---

## 2. 详细回滚步骤

### 2.1 回滚前准备

#### 2.1.1 确认回滚必要性
```bash
# 检查当前服务状态
python -c "import requests; print(requests.get('http://localhost:8001/api/health').json())"

# 查看最近的备份文件
ls -la data/backups/

# 查看最近的部署记录
cat logs/deployment.log | tail -20
```

#### 2.1.2 记录当前状态
```bash
# 记录当前进程状态
ps aux | grep -E "(uvicorn|hermes)" > /tmp/rollback_pre_state.txt

# 记录当前数据库状态
sqlite3 data/school_platform.db ".schema" > /tmp/rollback_db_schema.txt

# 记录当前配置
cp .env /tmp/rollback_env_backup.env
```

### 2.2 回滚执行步骤

#### 步骤1: 停止所有服务

```bash
# 停止AI服务
pkill -f "uvicorn main:app"

# 停止Hermes服务
pkill -f "hermes_server.py"

# 停止监控服务
pkill -f "monitor_service.py"

# 停止缓存预热服务
pkill -f "cache_warmer.py"

# 验证服务已停止
sleep 5
ps aux | grep -E "(uvicorn|hermes|monitor|cache_warmer)"
```

#### 步骤2: 备份当前状态（用于问题分析）

```bash
# 创建问题状态快照目录
SNAPSHOT_DIR="rollback_snapshot_$(date +%Y%m%d_%H%M%S)"
mkdir -p data/snapshots/$SNAPSHOT_DIR

# 备份当前数据库
cp data/school_platform.db data/snapshots/$SNAPSHOT_DIR/

# 备份当前日志
cp logs/*.log data/snapshots/$SNAPSHOT_DIR/

# 备份当前配置
cp .env data/snapshots/$SNAPSHOT_DIR/

echo "问题状态已备份至: data/snapshots/$SNAPSHOT_DIR"
```

#### 步骤3: 数据回滚（数据库）

```bash
# 查看可用备份列表
ls -la data/backups/

# 选择最新的有效备份（手动选择）
BACKUP_FILE="data/backups/school_platform_20260517_020000.db"

# 验证备份文件完整性
sqlite3 "$BACKUP_FILE" "SELECT COUNT(*) FROM schools;"

# 执行数据库回滚
cp "$BACKUP_FILE" data/school_platform.db

# 验证回滚结果
sqlite3 data/school_platform.db "SELECT COUNT(*) FROM schools;"
```

#### 步骤4: 缓存清理

```bash
# 连接Redis并清空缓存
redis-cli FLUSHALL

# 验证缓存已清空
redis-cli DBSIZE
```

#### 步骤5: 配置回滚

```bash
# 恢复到上一个稳定版本的配置
cp config/backup/config_stable.env .env

# 验证配置
cat .env | grep -E "(APP_VERSION|DATABASE_URL|REDIS_HOST)"
```

#### 步骤6: 启动服务

```bash
# 启动Redis服务（确保可用）
redis-server --daemonize yes

# 启动AI服务
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4 > logs/app.log 2>&1 &

# 等待服务启动
sleep 10

# 启动Hermes服务
nohup python hermes_server.py > logs/hermes.log 2>&1 &

# 等待服务启动
sleep 5

# 启动监控服务
nohup python monitor_service.py > logs/monitor.log 2>&1 &

# 启动缓存预热服务
nohup python cache_warmer.py > logs/cache_warmer.log 2>&1 &
```

#### 步骤7: 验证回滚结果

```bash
# 健康检查
curl -s http://localhost:8001/api/health | python -m json.tool

# 服务状态检查
ps aux | grep -E "(uvicorn|hermes|monitor|cache_warmer)"

# 数据库连接验证
sqlite3 data/school_platform.db "SELECT name FROM sqlite_master WHERE type='table';"

# Redis连接验证
redis-cli PING
```

### 2.3 回滚后操作

#### 2.3.1 通知相关人员
- 通过邮件/钉钉通知开发团队
- 通过邮件/钉钉通知产品团队
- 记录回滚事件到事件管理系统

#### 2.3.2 问题分析
- 收集回滚前的状态快照
- 分析日志定位问题根源
- 编写问题分析报告

---

## 3. 回滚脚本验证

### 3.1 回滚脚本清单

| 脚本名称 | 路径 | 功能描述 |
|----------|------|----------|
| `rollback_database.py` | scripts/ | 数据库回滚主脚本 |
| `rollback_config.py` | scripts/ | 配置文件回滚脚本 |
| `rollback_services.py` | scripts/ | 服务重启脚本 |
| `verify_rollback.py` | scripts/ | 回滚验证脚本 |

### 3.2 脚本内容

#### 3.2.1 数据库回滚脚本 `scripts/rollback_database.py`

```python
#!/usr/bin/env python3
"""
数据库回滚脚本
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime

def get_latest_backup(backup_dir):
    """获取最新的备份文件"""
    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith('school_platform_') and file.endswith('.db'):
            file_path = os.path.join(backup_dir, file)
            backups.append((file_path, os.path.getmtime(file_path)))
    
    if not backups:
        return None
    
    backups.sort(key=lambda x: x[1], reverse=True)
    return backups[0][0]

def verify_backup(backup_file):
    """验证备份文件完整性"""
    try:
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM schools")
        count = cursor.fetchone()[0]
        conn.close()
        return True, f"备份验证通过，包含 {count} 条学校记录"
    except Exception as e:
        return False, f"备份验证失败: {e}"

def rollback_database(db_file, backup_file):
    """执行数据库回滚"""
    try:
        # 创建回滚前备份
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rollback_before = db_file + f".rollback_before_{timestamp}"
        shutil.copy2(db_file, rollback_before)
        print(f"已创建回滚前备份: {rollback_before}")
        
        # 执行回滚
        shutil.copy2(backup_file, db_file)
        return True, "数据库回滚成功"
    except Exception as e:
        return False, f"数据库回滚失败: {e}"

def main():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    db_file = os.path.join(data_dir, 'school_platform.db')
    backup_dir = os.path.join(data_dir, 'backups')
    
    # 获取最新备份
    backup_file = get_latest_backup(backup_dir)
    if not backup_file:
        print("错误：未找到备份文件")
        sys.exit(1)
    
    print(f"找到最新备份: {backup_file}")
    
    # 验证备份
    success, msg = verify_backup(backup_file)
    print(msg)
    if not success:
        sys.exit(1)
    
    # 执行回滚
    success, msg = rollback_database(db_file, backup_file)
    print(msg)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
```

#### 3.2.2 配置回滚脚本 `scripts/rollback_config.py`

```python
#!/usr/bin/env python3
"""
配置文件回滚脚本
"""

import os
import shutil
from datetime import datetime

def main():
    env_file = '.env'
    config_backup_dir = 'config/backup'
    
    # 检查配置备份目录
    if not os.path.exists(config_backup_dir):
        print("错误：配置备份目录不存在")
        return
    
    # 获取最新的稳定配置
    backups = []
    for file in os.listdir(config_backup_dir):
        if file.startswith('config_stable'):
            file_path = os.path.join(config_backup_dir, file)
            backups.append((file_path, os.path.getmtime(file_path)))
    
    if not backups:
        print("错误：未找到稳定配置备份")
        return
    
    backups.sort(key=lambda x: x[1], reverse=True)
    stable_config = backups[0][0]
    
    print(f"找到稳定配置: {stable_config}")
    
    # 备份当前配置
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    current_backup = f"{env_file}.backup_{timestamp}"
    shutil.copy2(env_file, current_backup)
    print(f"已备份当前配置: {current_backup}")
    
    # 恢复稳定配置
    shutil.copy2(stable_config, env_file)
    print("配置回滚成功")

if __name__ == "__main__":
    main()
```

#### 3.2.3 服务重启脚本 `scripts/rollback_services.py`

```python
#!/usr/bin/env python3
"""
服务重启脚本
"""

import subprocess
import time
import os

def stop_service(process_name):
    """停止服务"""
    try:
        result = subprocess.run(['pkill', '-f', process_name], capture_output=True)
        if result.returncode == 0:
            print(f"已停止服务: {process_name}")
        return result.returncode == 0
    except Exception as e:
        print(f"停止服务失败 {process_name}: {e}")
        return False

def start_service(service_cmd, log_file):
    """启动服务"""
    try:
        log_path = os.path.join('logs', log_file)
        with open(log_path, 'w') as f:
            subprocess.Popen(service_cmd, stdout=f, stderr=subprocess.STDOUT)
        print(f"已启动服务: {service_cmd[0]}")
        return True
    except Exception as e:
        print(f"启动服务失败 {service_cmd[0]}: {e}")
        return False

def main():
    # 停止所有服务
    services_to_stop = [
        "uvicorn main:app",
        "hermes_server.py",
        "monitor_service.py",
        "cache_warmer.py"
    ]
    
    for service in services_to_stop:
        stop_service(service)
    
    # 等待服务停止
    time.sleep(5)
    
    # 启动服务
    services_to_start = [
        (['python', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8001', '--workers', '4'], 'app.log'),
        (['python', 'hermes_server.py'], 'hermes.log'),
        (['python', 'monitor_service.py'], 'monitor.log'),
        (['python', 'cache_warmer.py'], 'cache_warmer.log')
    ]
    
    for cmd, log_file in services_to_start:
        start_service(cmd, log_file)
        time.sleep(3)
    
    print("所有服务已重启")

if __name__ == "__main__":
    main()
```

#### 3.2.4 回滚验证脚本 `scripts/verify_rollback.py`

```python
#!/usr/bin/env python3
"""
回滚验证脚本
"""

import requests
import sqlite3
import redis
import time

def check_health():
    """检查服务健康状态"""
    try:
        response = requests.get('http://localhost:8001/api/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data', {}).get('status') == 'healthy':
                return True, "API服务健康检查通过"
            else:
                return False, f"API服务状态异常: {data}"
        else:
            return False, f"API服务响应异常: {response.status_code}"
    except Exception as e:
        return False, f"API服务健康检查失败: {e}"

def check_database():
    """检查数据库连接"""
    try:
        conn = sqlite3.connect('data/school_platform.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM schools")
        count = cursor.fetchone()[0]
        conn.close()
        return True, f"数据库连接正常，包含 {count} 条学校记录"
    except Exception as e:
        return False, f"数据库连接失败: {e}"

def check_redis():
    """检查Redis连接"""
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        response = r.ping()
        if response:
            return True, "Redis连接正常"
        else:
            return False, "Redis连接异常"
    except Exception as e:
        return False, f"Redis连接失败: {e}"

def main():
    print("=== 回滚验证开始 ===")
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(15)
    
    # 执行验证
    checks = [
        check_health,
        check_database,
        check_redis
    ]
    
    all_passed = True
    for check in checks:
        success, msg = check()
        print(f"[{check.__name__}] {msg}")
        if not success:
            all_passed = False
    
    print("=== 回滚验证结束 ===")
    
    if all_passed:
        print("✓ 所有验证项均通过")
        return 0
    else:
        print("✗ 部分验证项未通过")
        return 1

if __name__ == "__main__":
    exit(main())
```

### 3.3 脚本验证流程

```bash
# 1. 创建脚本目录
mkdir -p scripts

# 2. 将上述脚本保存到对应位置

# 3. 赋予执行权限
chmod +x scripts/*.py

# 4. 测试脚本
python scripts/rollback_database.py
python scripts/rollback_config.py
python scripts/verify_rollback.py
```

---

## 4. 数据回滚策略

### 4.1 数据分类

| 数据类型 | 存储方式 | 回滚策略 | 备份频率 |
|----------|----------|----------|----------|
| **核心业务数据** | SQLite数据库 | 完全回滚至备份点 | 每24小时 |
| **缓存数据** | Redis | 清空后自动重建 | - |
| **日志数据** | 文件系统 | 保留用于分析 | - |
| **配置数据** | .env文件 | 恢复至稳定版本 | 每次部署前 |

### 4.2 数据库回滚策略

#### 4.2.1 备份策略
- **自动备份**: 每天凌晨2点自动执行全量备份
- **手动备份**: 部署前手动执行备份
- **备份保留**: 保留最近7天的备份

#### 4.2.2 回滚策略
```
数据库回滚流程图:

[检测到数据异常]
        ↓
[确认需要回滚]
        ↓
[停止所有服务]
        ↓
[备份当前状态(用于分析)]
        ↓
[选择目标备份点]
        ↓
[执行数据库恢复]
        ↓
[验证数据完整性]
        ↓
[启动服务]
        ↓
[验证服务状态]
        ↓
[完成回滚]
```

### 4.3 缓存回滚策略

#### 4.3.1 回滚方式
- **清空缓存**: `redis-cli FLUSHALL`
- **缓存预热**: 启动后自动执行缓存预热脚本

#### 4.3.2 预热流程
```bash
# 缓存预热命令
python cache_warmer.py
```

### 4.4 配置回滚策略

#### 4.4.1 配置备份
- 每次部署前自动备份当前配置到 `config/backup/`
- 标记稳定版本配置为 `config_stable.env`

#### 4.4.2 回滚流程
```bash
# 恢复稳定配置
cp config/backup/config_stable.env .env
```

---

## 5. 回滚验证机制

### 5.1 验证指标

| 验证项 | 验证方法 | 成功标准 |
|--------|----------|----------|
| **服务可用性** | 访问 `/api/health` | 返回状态码200，status为healthy |
| **数据库连接** | SQLite连接测试 | 成功连接并查询数据 |
| **Redis连接** | Redis PING命令 | 返回PONG |
| **核心API** | 测试关键接口 | 返回预期数据结构 |
| **数据完整性** | 校验数据条数 | 与备份时数据量一致 |

### 5.2 验证命令

```bash
# 完整验证流程
echo "=== 服务健康检查 ==="
curl -s http://localhost:8001/api/health | python -m json.tool

echo ""
echo "=== 数据库验证 ==="
sqlite3 data/school_platform.db "SELECT COUNT(*) FROM schools;"

echo ""
echo "=== Redis验证 ==="
redis-cli PING

echo ""
echo "=== 核心API测试 ==="
curl -s http://localhost:8001/api/v1/ai/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}' | python -m json.tool
```

### 5.3 自动验证脚本

见 `scripts/verify_rollback.py`

---

## 6. 回滚流程责任矩阵

| 角色 | 职责 | 联系方式 |
|------|------|----------|
| **运维工程师** | 执行回滚操作、验证回滚结果 | ops@example.com |
| **开发工程师** | 分析问题根因、修复bug | dev@example.com |
| **产品经理** | 确认业务影响、协调沟通 | product@example.com |
| **系统管理员** | 管理服务器资源、监控告警 | admin@example.com |

---

## 7. 回滚文档版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0 | 2026-05-17 | 初始版本，包含回滚触发条件、步骤、脚本和策略 |

---

**文档状态**: 已批准，生效日期 2026-05-17

**审批人**: 运维团队负责人

**文档位置**: `ai-service/ROLLBACK_PROCEDURE.md`
