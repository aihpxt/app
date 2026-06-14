# AI 服务平台

一个基于 FastAPI 的智能对话与数据管理平台。

## 📋 项目概述

AI 服务平台提供以下核心功能：

- 🤖 **智能对话** - 基于 AI Agent 的智能问答系统
- 📚 **学校数据管理** - 学校信息、政策法规的查询与管理
- 🔧 **智能体编排** - Hermes Agent 智能分派系统
- 🕷️ **数据采集** - OpenClaw 爬虫系统
- 📊 **监控告警** - 实时系统监控与告警管理
- 💾 **缓存管理** - 多级缓存机制（L1内存 + L2 Redis）
- 🔄 **熔断器** - 服务容错保护机制

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境

```bash
cp .env.example .env
# 编辑 .env 配置必要的参数
```

### 启动服务

```bash
# 开发模式
python main.py

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行核心模块测试
pytest tests/test_core_modules.py tests/test_core_services.py -v
```

## 📁 项目结构

```
ai-service/
├── app/                    # 核心应用
│   ├── api/               # API 路由
│   ├── auth/              # 认证授权
│   ├── core/              # 核心模块
│   │   ├── cache.py       # 缓存管理
│   │   ├── tiered_cache.py # 多级缓存
│   │   ├── circuit_breaker.py # 熔断器
│   │   ├── alert_manager.py # 告警管理
│   │   └── monitoring.py  # 监控模块
│   ├── services/          # 业务服务
│   └── security/          # 安全模块
├── agents/                # AI 智能体
│   ├── registry.py        # 智能体注册
│   ├── orchestrator.py   # 智能体编排
│   └── specialists.py     # 专业智能体
├── openclaw/              # 爬虫系统
├── routers/               # API 路由
├── tests/                 # 测试文件
├── docs/                  # 文档
├── main.py                # 主入口
└── config.py              # 配置
```

## 📊 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| 数据库 | SQLite / PostgreSQL |
| 缓存 | Redis + LRU Memory Cache |
| 认证 | JWT + RBAC |
| 监控 | Prometheus + 自定义监控 |
| AI | OpenAI API / 多模型支持 |

## 🧪 测试覆盖

| 测试文件 | 测试数 | 状态 |
|----------|--------|------|
| test_api_endpoints.py | 13 | ✅ 通过 |
| test_core_modules.py | 26 | ✅ 通过 |
| test_core_services.py | 17 | ✅ 通过 |
| test_monitoring.py | 14 | ✅ 通过 |
| test_database_exceptions.py | 8 | ✅ 通过 |
| test_auth.py | 21 | ✅ 通过 |
| **总计** | **99+** | **✅ 全部通过** |

## 📖 文档

- [快速入门](QUICKSTART.md) - 快速开始使用
- [系统文档](SYSTEM_DOCUMENTATION.md) - 完整系统文档
- [部署指南](DEPLOYMENT_GUIDE.md) - 服务器部署指南
- [API 文档](API_DOCS.md) - API 接口文档

## 🐳 Docker 部署

```bash
# 构建镜像
docker build -t ai-service .

# 运行容器
docker run -d -p 8000:8000 ai-service

# 或使用 docker-compose
docker-compose up -d
```

## 🔧 配置

在 `.env` 文件中配置：

```env
# 数据库
DATABASE_URL=sqlite:///./app.db

# JWT 密钥
JWT_SECRET_KEY=your-secret-key

# Redis（可选）
REDIS_URL=redis://localhost:6379/0

# OpenAI API
OPENAI_API_KEY=sk-your-api-key
```

## 📝 License

MIT License

## 📞 支持

如遇问题，请查看：
- [系统文档](SYSTEM_DOCUMENTATION.md)
- [部署指南](DEPLOYMENT_GUIDE.md)
- 日志文件：`logs/`

---

**版本**: v1.0.0
**更新日期**: 2026-05-25
