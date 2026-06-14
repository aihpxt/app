# 审计日志系统说明

## 功能概述

审计日志系统提供以下功能：

1. **自动记录所有API请求** - 通过中间件自动记录HTTP请求
2. **操作审计** - 记录用户登录登出、数据操作等
3. **安全事件追踪** - 记录异常和安全相关事件
4. **日志查询** - 支持按日期、操作类型、用户等条件查询
5. **统计分析** - 提供审计统计信息

## 记录的操作类型

- `LOGIN` - 用户登录
- `LOGOUT` - 用户登出
- `API_ACCESS` - API访问
- `DATA_CREATE` - 数据创建
- `DATA_UPDATE` - 数据更新
- `DATA_DELETE` - 数据删除
- `CONFIG_CHANGE` - 配置变更
- `SECURITY_EVENT` - 安全事件
- `SYSTEM_EVENT` - 系统事件

## 日志级别

- `INFO` - 信息
- `WARNING` - 警告
- `ERROR` - 错误
- `CRITICAL` - 严重

## API接口

### 查询审计日志

```bash
GET /api/audit/logs
```

参数：
- `start_date`: 开始日期 (YYYYMMDD)
- `end_date`: 结束日期 (YYYYMMDD)
- `action`: 操作类型
- `level`: 日志级别
- `limit`: 返回数量 (默认100)

### 获取审计统计

```bash
GET /api/audit/statistics?days=7
```

### 获取登录历史

```bash
GET /api/audit/login-history?user_id=xxx&limit=50
```

### 获取安全事件

```bash
GET /api/audit/security-events?limit=50
```

## 日志文件

审计日志保存在 `logs/audit/` 目录，按日期分割：

```
logs/audit/
├── audit_20260518.log
├── audit_20260519.log
└── ...
```

## 手动记录审计日志

```python
from app.core.audit_logger import audit_logger, AuditAction, AuditLevel

# 记录审计日志
audit_logger.log(
    action=AuditAction.DATA_CREATE,
    level=AuditLevel.INFO,
    user_id="user123",
    resource="/api/data",
    details={"item_id": "123"},
    ip_address="192.168.1.1",
    status="SUCCESS"
)
```

## 使用装饰器

```python
from app.core.audit_logger import audit_log, AuditAction, AuditLevel

@audit_log(action=AuditAction.DATA_CREATE, resource="/api/data")
async def create_data(data):
    # 你的业务逻辑
    pass
```

## 安全建议

1. **定期审查** - 定期查看审计日志，识别异常行为
2. **日志保护** - 确保审计日志文件权限正确，防止篡改
3. **存储容量** - 监控日志存储使用，设置合理的保留策略
4. **敏感数据** - 审计日志已对用户ID等敏感信息进行哈希处理
5. **告警机制** - 配置异常操作告警（如频繁登录失败）
