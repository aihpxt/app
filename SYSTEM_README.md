# 云南省AI全域赋能中考择校智能决策平台

## 项目概述

本项目是一个基于人工智能的中考择校智能决策平台，为云南省学生和家长提供全方位的择校辅助服务。

### 核心功能

- **AI智能助手** - 小龙虾智能助手，提供个性化咨询服务
- **学校查询** - 全省学校信息检索与详情查看
- **AI择校推荐** - 基于分数和偏好的智能学校推荐
- **志愿填报** - 智能化志愿填报指导
- **政策解读** - 最新中考政策解析
- **学习计划** - 个性化学习方案生成

## 技术架构

### 后端技术栈

- **框架**: FastAPI
- **语言**: Python 3.9+
- **数据库**: SQLite (可扩展为 PostgreSQL/MySQL)
- **认证**: JWT
- **AI模型**: DeepSeek API
- **缓存**: Redis (可选)
- **监控**: Prometheus + 自定义告警系统

### 前端技术栈

- **框架**: Vue 3
- **UI**: Element Plus
- **构建**: Vite
- **路由**: Vue Router
- **状态管理**: Pinia

## 项目结构

```
aiphxt-app/
├── ai-service/              # 后端服务
│   ├── app/                # 应用核心
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心功能
│   │   └── auth/           # 认证模块
│   ├── agents/             # 智能体系统
│   ├── data/               # 数据文件
│   └── docs/               # 后端文档
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 公共组件
│   │   └── api/            # API封装
│   └── dist/               # 构建输出
└── [系统文档]
```

## 快速开始

### 环境要求

- **Python**: 3.9+
- **Node.js**: 18+
- **npm**: 9+

### 后端启动

```bash
cd ai-service

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入配置

# 启动服务
python start_service.py
```

后端服务默认运行在: `http://localhost:8001`

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build
```

前端服务默认运行在: `http://localhost:3001`

## 配置说明

### 后端环境变量 (.env)

```env
# 服务配置
HOST=0.0.0.0
PORT=8001

# JWT认证
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# DeepSeek AI
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_API_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# 数据库
DATABASE_URL=sqlite:///./data/unified_school_data.db

# Redis (可选)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 前端环境变量

```env
# .env.production
VITE_API_BASE_URL=http://your-backend-url/api/v1
```

## API文档

启动后端服务后访问:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

主要API端点:

| 功能 | 端点 | 说明 |
|------|------|------|
| 健康检查 | `/health` | 服务健康状态 |
| 用户认证 | `/api/v1/auth/*` | 登录、注册、JWT管理 |
| 智能聊天 | `/api/v1/agent/chat` | AI助手对话 |
| 学校查询 | `/api/v1/schools/*` | 学校信息检索 |
| 政策查询 | `/api/v1/policies/*` | 政策文档 |
| 性能监控 | `/api/v1/performance/*` | 系统性能指标 |
| 告警系统 | `/api/v1/alerts/*` | 告警管理 |

## 部署指南

### Docker部署

```bash
# 构建镜像
cd ai-service
docker build -t ai-service:latest .

cd ../frontend
docker build -t ai-frontend:latest .

# 使用docker-compose
docker-compose up -d
```

### 传统部署

详细部署步骤请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

### Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 监控与维护

### 系统监控

- **Prometheus指标**: `/metrics`
- **性能仪表盘**: `/api/v1/performance/dashboard`
- **告警系统**: 自动检测异常并触发告警

### 日志管理

```
ai-service/logs/
├── app.log              # 应用日志
├── ai_service.log       # AI服务日志
├── error.log            # 错误日志
└── audit/               # 审计日志
```

### 数据库备份

```bash
cd ai-service
python backup_database.py
```

## 测试

### E2E测试

```bash
cd ai-service
python e2e_test.py
```

测试覆盖率: ~100%

### 主要测试场景

- 健康检查
- 认证流程
- AI聊天接口
- 学校查询
- 性能指标
- 告警系统

## 安全建议

1. **生产环境必须修改默认密码和密钥**
2. **启用HTTPS**
3. **配置防火墙规则**
4. **定期更新依赖包**
5. **启用审计日志**
6. **配置备份策略**

## 常见问题

### 前端页面闪烁

已修复，通过路由就绪等待机制解决。

### AI响应缓慢

- 检查DeepSeek API密钥配置
- 查看网络连接
- 启用Redis缓存

### 端口冲突

修改对应服务的端口配置即可。

## 更新日志

### v2.0 (2026-05-19)
- ✅ E2E测试通过率100%
- ✅ 修复前端页面闪烁
- ✅ 优化AI智能体响应
- ✅ 完善告警系统
- ✅ 更新系统文档

### v1.0 (2026-04)
- 🎉 系统初始上线
- 🎯 基础功能完善

## 技术支持

如有问题，请查看:
- [OPS_DEPLOYMENT_GUIDE.md](./OPS_DEPLOYMENT_GUIDE.md) - 运维部署指南
- [API_DOCS.md](./API_DOCS.md) - API详细文档
- [系统完善总结.md](./系统完善总结.md) - 系统优化记录

## 许可证

© 2026 云南省AI全域赋能中考择校智能决策平台. All rights reserved.
