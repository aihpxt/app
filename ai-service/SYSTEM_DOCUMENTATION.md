# AI 服务平台 - 完整系统文档

## 📋 文档信息

| 项目 | 信息 |
|------|------|
| 版本 | v1.0.0 |
| 更新日期 | 2026-05-25 |
| 框架 | FastAPI + Python 3.14 |
| 数据库 | SQLite / PostgreSQL |
| 缓存 | Redis + LRU Memory Cache |

---

## 📑 目录

1. [系统概述](#1-系统概述)
2. [系统架构](#2-系统架构)
3. [核心模块](#3-核心模块)
4. [API接口](#4-api接口)
5. [数据模型](#5-数据模型)
6. [服务组件](#6-服务组件)
7. [测试报告](#7-测试报告)
8. [部署指南](#8-部署指南)
9. [运维指南](#9-运维指南)

---

## 1. 系统概述

### 1.1 系统简介

AI 服务平台是一个基于 FastAPI 框架构建的智能对话与数据管理服务，提供以下核心功能：

- 🤖 **智能对话** - 基于 AI Agent 的智能问答系统
- 📚 **学校数据管理** - 学校信息、政策法规的查询与管理
- 🔧 **智能体编排** - Hermes Agent 智能分派系统
- 🕷️ **数据采集** - OpenClaw 爬虫系统
- 📊 **监控告警** - 实时系统监控与告警管理
- 💾 **缓存管理** - 多级缓存机制（L1内存 + L2 Redis）
- 🔄 **熔断器** - 服务容错保护机制

### 1.2 技术栈

| 组件 | 技术选型 |
|------|----------|
| 后端框架 | FastAPI + Uvicorn |
| 数据库 | SQLite / PostgreSQL |
| 缓存 | Redis + LRU Memory Cache |
| 认证 | JWT + RBAC |
| 监控 | Prometheus + 自定义监控 |
| 日志 | Python Logging |
| AI | OpenAI API / 多模型支持 |

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      客户端应用                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway                              │
│  ┌─────────────┬─────────────┬─────────────┐               │
│  │ 认证/授权    │  限流保护    │  请求路由   │               │
│  └─────────────┴─────────────┴─────────────┘               │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ AI Service │   │ Hermes   │   │ OpenClaw │
    │  (主服务)  │   │ Agent    │   │  Crawler │
    └──────────┘   └──────────┘   └──────────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ SQLite   │   │  Redis   │   │ 外部API  │
    │ Database │   │  Cache   │   │  数据源   │
    └──────────┘   └──────────┘   └──────────┘
```

### 2.2 目录结构

```
ai-service/
├── app/                         # 核心应用
│   ├── api/                     # API路由
│   │   ├── routes/              # 路由定义
│   │   └── middlewares/         # 中间件
│   ├── auth/                    # 认证授权
│   │   ├── jwt_handler.py       # JWT处理
│   │   └── rbac.py              # RBAC权限管理
│   ├── core/                    # 核心模块
│   │   ├── cache.py             # 缓存管理
│   │   ├── tiered_cache.py      # 多级缓存
│   │   ├── circuit_breaker.py    # 熔断器
│   │   ├── alert_manager.py      # 告警管理
│   │   ├── monitoring.py        # 监控模块
│   │   └── exceptions.py        # 异常定义
│   ├── services/                # 业务服务
│   └── security/                # 安全模块
├── agents/                      # AI智能体
│   ├── registry.py              # 智能体注册
│   ├── orchestrator.py         # 智能体编排
│   ├── specialists.py          # 专业智能体
│   └── pronoun_resolver.py     # 指代消解
├── openclaw/                    # 爬虫系统
│   ├── crawler.py              # 爬虫核心
│   ├── school_crawler.py       # 学校数据采集
│   └── policy_crawler.py       # 政策采集
├── routers/                    # API路由
├── tests/                      # 测试文件
│   ├── test_api_endpoints.py   # API测试
│   ├── test_core_modules.py   # 核心模块测试
│   ├── test_core_services.py   # 服务测试
│   ├── test_monitoring.py      # 监控测试
│   └── test_auth.py            # 认证测试
├── docs/                       # 文档
├── main.py                     # 主入口
├── config.py                  # 配置
└── requirements.txt           # 依赖
```

---

## 3. 核心模块

### 3.1 缓存系统 (Cache)

**位置**: `app/core/cache.py`

**特性**:
- LRU (最近最少使用) 淘汰策略
- TTL (生存时间) 支持
- 统计信息（命中率、大小等）

**方法**:
```python
class Cache:
    def set(self, key: str, value: Any, ttl: int = 3600)
    def get(self, key: str) -> Optional[Any]
    def delete(self, key: str)
    def clear(self)
    def get_stats() -> Dict
```

### 3.2 多级缓存 (TieredCache)

**位置**: `app/core/tiered_cache.py`

**架构**:
```
L1 Cache (内存) ←→ L2 Cache (Redis) ←→ Database
```

**特性**:
- 自动逐级回源
- 写入时双写 L1 + L2
- 缓存预热
- 性能指标监控

### 3.3 熔断器 (CircuitBreaker)

**位置**: `app/core/circuit_breaker.py`

**状态**:
```
CLOSED ──→ OPEN ──→ HALF_OPEN ──→ CLOSED
   ↑                          │
   └──────────────────────────┘
```

**参数**:
| 参数 | 默认值 | 说明 |
|------|--------|------|
| failure_threshold | 5 | 失败阈值 |
| recovery_timeout | 60 | 恢复超时(秒) |
| half_open_max_calls | 3 | 半开状态最大调用数 |

### 3.4 告警管理 (AlertManager)

**位置**: `app/core/alert_manager.py`

**特性**:
- 多级告警 (INFO/WARNING/ERROR/CRITICAL)
- 告警冷却机制
- 告警聚合
- 告警抑制

### 3.5 智能重试 (SmartRetry)

**位置**: `app/core/retry_decorator.py`

**策略**:
- 指数退避
- 可配置重试次数
- 可配置超时时间
- 异常过滤

---

## 4. API接口

### 4.1 健康检查

```
GET /api/v1/health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": 1716652800,
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

### 4.2 学校列表

```
GET /api/v1/schools
GET /api/v1/schools/{school_id}
```

### 4.3 政策列表

```
GET /api/v1/policies
GET /api/v1/policies/{policy_id}
```

### 4.4 AI 对话

```
POST /api/v1/chat
```

**请求**:
```json
{
  "message": "你好",
  "session_id": "xxx",
  "user_id": "user_123"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "content": "你好！有什么可以帮助你的吗？",
    "session_id": "xxx",
    "agent": "hermes"
  }
}
```

### 4.5 Dashboard

```
GET /api/v1/dashboard
```

**响应**:
```json
{
  "success": true,
  "data": {
    "total_schools": 100,
    "total_policies": 50,
    "total_chats": 1000,
    "cache_hit_rate": 0.85,
    "uptime": 86400
  }
}
```

---

## 5. 数据模型

### 5.1 学校模型 (School)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 学校名称 |
| type | String | 学校类型 |
| district | String | 所在区县 |
| address | String | 地址 |
| phone | String | 联系电话 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 5.2 政策模型 (Policy)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| title | String | 标题 |
| content | Text | 内容 |
| category | String | 分类 |
| published_date | Date | 发布日期 |
| source | String | 来源 |
| created_at | DateTime | 创建时间 |

### 5.3 用户模型 (User)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String | 用户名 |
| email | String | 邮箱 |
| role | String | 角色 |
| created_at | DateTime | 创建时间 |

---

## 6. 服务组件

### 6.1 Hermes Agent 系统

**位置**: `hermes_agent_coordinator.py`

**功能**:
- 意图分析
- 智能体分派
- 多智能体协作
- 上下文管理

### 6.2 OpenClaw 爬虫系统

**位置**: `openclaw/`

**模块**:
- `crawler.py` - 爬虫核心
- `school_crawler.py` - 学校数据采集
- `policy_crawler.py` - 政策数据采集
- `proxy_pool.py` - 代理池管理

**特性**:
- User-Agent 轮换
- 速率限制
- 结构化日志
- 代理验证

### 6.3 数据同步服务

**位置**: `auto_data_sync.py`

**功能**:
- 定时数据同步
- 数据质量检查
- 自动清理

---

## 7. 测试报告

### 7.1 测试覆盖率

| 测试文件 | 测试数 | 状态 |
|----------|--------|------|
| test_api_endpoints.py | 13 | ✅ 通过 |
| test_core_modules.py | 26 | ✅ 通过 |
| test_core_services.py | 17 | ✅ 通过 |
| test_monitoring.py | 14 | ✅ 通过 |
| test_database_exceptions.py | 8 | ✅ 通过 |
| test_auth.py | 21 | ✅ 通过 |
| test_agents.py | 16 | ✅ 通过 |
| test_chat_service.py | 11 | ✅ 通过 |
| **总计** | **126+** | **✅ 全部通过** |

### 7.2 测试执行

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_api_endpoints.py -v

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

---

## 8. 部署指南

### 8.1 环境要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2 Core | 4 Core |
| 内存 | 4 GB | 8 GB |
| 磁盘 | 10 GB | 20 GB |
| Python | 3.10+ | 3.11+ |

### 8.2 依赖安装

```bash
# 克隆代码
git clone <repository_url>
cd ai-service

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置
```

### 8.3 启动服务

```bash
# 开发模式
python main.py

# 生产模式 (使用 uvicorn)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker 部署
docker-compose up -d
```

---

## 9. 运维指南

### 9.1 日志管理

**日志位置**: `logs/`

| 日志文件 | 内容 |
|----------|------|
| app.log | 应用日志 |
| audit.log | 审计日志 |
| crawler.log | 爬虫日志 |
| hermes.log | Hermes 日志 |

### 9.2 监控指标

| 指标 | 说明 |
|------|------|
| cache_hit_rate | 缓存命中率 |
| response_time | 响应时间 |
| error_rate | 错误率 |
| active_sessions | 活跃会话数 |

### 9.3 备份策略

```bash
# 数据库备份
python backup_database.py

# 配置备份
cp .env .env.backup.$(date +%Y%m%d)
```

### 9.4 故障排查

**常见问题**:

1. **服务无法启动**
   - 检查端口占用
   - 检查数据库连接
   - 检查日志文件

2. **缓存未命中**
   - 检查 Redis 服务
   - 检查缓存配置

3. **API 响应慢**
   - 检查数据库索引
   - 检查缓存命中率
   - 查看慢查询日志

---

## 📞 技术支持

如遇问题，请检查：
1. 日志文件 (`logs/`)
2. 数据库连接状态
3. Redis 服务状态
4. 环境变量配置

---

**文档版本**: v1.0.0
**最后更新**: 2026-05-25
**维护团队**: AI Platform Team
