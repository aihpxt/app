# AI服务系统运维部署手册

## 版本信息
- **文档版本**: v1.0
- **创建日期**: 2026年5月
- **适用系统**: 云南省AI全域赋能中考择校智能决策平台

---

## 目录
1. [环境准备指南](#1-环境准备指南)
   - 1.1 开发环境
   - 1.2 测试环境
   - 1.3 生产环境
   - 1.4 环境差异对比
2. [部署步骤说明](#2-部署步骤说明)
   - 2.1 Docker Compose 部署（推荐）
   - 2.2 Kubernetes 部署
   - 2.3 手动部署
3. [配置文件说明](#3-配置文件说明)
   - 3.1 后端配置
   - 3.2 AI服务配置
   - 3.3 前端配置
4. [监控和故障排查指南](#4-监控和故障排查指南)
   - 4.1 监控指标
   - 4.2 日志管理
   - 4.3 常见故障排查

---

## 1. 环境准备指南

### 1.1 开发环境

#### 硬件要求
| 资源类型 | 最低配置 | 推荐配置 |
|---------|---------|---------|
| CPU | 4核 | 8核 |
| 内存 | 8GB | 16GB |
| 存储 | 50GB | 100GB |

#### 软件要求
| 软件 | 版本 | 用途 |
|-----|------|-----|
| Python | 3.10+ | AI服务运行环境 |
| Node.js | 18+ | 前端构建 |
| Java | 21+ | 后端服务 |
| Redis | 7.0+ | 缓存服务 |
| SQLite | 3.30+ | 开发数据库 |
| Docker | 24.0+ | 容器化部署 |

#### 环境变量配置文件: `.env.development`
```bash
# 开发环境配置
ENV=development
DEBUG=true
LOG_LEVEL=debug

# 数据库配置
DB_PATH=./data/aiphxt.db

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# AI服务配置
AI_SERVICE_URL=http://localhost:8000
DEEPSEEK_API_KEY=your-deepseek-api-key

# JWT配置
JWT_SECRET=development-secret-key
JWT_EXPIRES_IN=3600

# 端口配置
FRONTEND_PORT=3000
BACKEND_PORT=8081
AI_SERVICE_PORT=8000
```

### 1.2 测试环境

#### 硬件要求
| 资源类型 | 最低配置 | 推荐配置 |
|---------|---------|---------|
| CPU | 8核 | 16核 |
| 内存 | 16GB | 32GB |
| 存储 | 100GB | 200GB |

#### 软件要求
| 软件 | 版本 | 用途 |
|-----|------|-----|
| Python | 3.10+ | AI服务运行环境 |
| Node.js | 18+ | 前端构建 |
| Java | 21+ | 后端服务 |
| MySQL | 8.0+ | 测试数据库 |
| Redis | 7.0+ | 缓存服务 |
| RabbitMQ | 3.12+ | 消息队列 |
| Nacos | 2.2+ | 服务注册 |
| Docker | 24.0+ | 容器化部署 |

#### 环境变量配置文件: `.env.testing`
```bash
# 测试环境配置
ENV=testing
DEBUG=false
LOG_LEVEL=info

# MySQL数据库配置
DB_HOST=mysql
DB_PORT=3306
DB_NAME=school_platform
DB_USER=test_user
DB_PASSWORD=test_password

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=1

# RabbitMQ配置
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# AI服务配置
AI_SERVICE_URL=http://ai-service:8000
DEEPSEEK_API_KEY=your-deepseek-api-key

# JWT配置
JWT_SECRET=testing-secret-key
JWT_EXPIRES_IN=3600

# 端口配置
FRONTEND_PORT=3000
BACKEND_PORT=8080
AI_SERVICE_PORT=8000
```

### 1.3 生产环境

#### 硬件要求（单节点）
| 资源类型 | 最低配置 | 推荐配置 |
|---------|---------|---------|
| CPU | 16核 | 32核 |
| 内存 | 32GB | 64GB |
| 存储 | 500GB SSD | 1TB SSD |
| 网络 | 100Mbps | 1Gbps |

#### 软件要求
| 软件 | 版本 | 用途 |
|-----|------|-----|
| Python | 3.10+ | AI服务运行环境 |
| Node.js | 18+ | 前端构建 |
| Java | 21+ | 后端服务 |
| MySQL | 8.0+ | 生产数据库（主从架构） |
| Redis | 7.0+ | 缓存服务（集群模式） |
| RabbitMQ | 3.12+ | 消息队列（集群模式） |
| Nacos | 2.2+ | 服务注册（集群模式） |
| Docker | 24.0+ | 容器化部署 |
| Kubernetes | 1.28+ | 容器编排 |
| Nginx | 1.24+ | 反向代理 |

#### 环境变量配置文件: `.env.production`
```bash
# 生产环境配置
ENV=production
DEBUG=false
LOG_LEVEL=warn

# MySQL数据库配置（主从）
DB_HOST=mysql-primary
DB_PORT=3306
DB_NAME=school_platform
DB_USER=prod_user
DB_PASSWORD=production-secure-password

# Redis配置（集群）
REDIS_HOST=redis-cluster
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=redis-secure-password

# RabbitMQ配置（集群）
RABBITMQ_HOST=rabbitmq-cluster
RABBITMQ_PORT=5672
RABBITMQ_USER=prod_user
RABBITMQ_PASSWORD=rabbitmq-secure-password

# Nacos配置（集群）
NACOS_SERVER_ADDR=nacos-cluster:8848

# AI服务配置
AI_SERVICE_URL=http://ai-service:8000
DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}

# JWT配置
JWT_SECRET=${JWT_SECRET}
JWT_EXPIRES_IN=86400

# 安全配置
CORS_ALLOWED_ORIGINS=https://your-domain.com
SSL_ENABLED=true

# 端口配置
FRONTEND_PORT=80
BACKEND_PORT=8080
AI_SERVICE_PORT=8000
```

### 1.4 环境差异对比

| 维度 | 开发环境 | 测试环境 | 生产环境 |
|-----|---------|---------|---------|
| **数据库** | SQLite | MySQL | MySQL（主从） |
| **缓存** | Redis（单节点） | Redis（单节点） | Redis（集群） |
| **日志级别** | DEBUG | INFO | WARN/ERROR |
| **调试模式** | 开启 | 关闭 | 关闭 |
| **数据量** | 少量测试数据 | 完整测试数据 | 真实业务数据 |
| **并发能力** | 低 | 中 | 高 |
| **安全配置** | 宽松 | 中等 | 严格 |
| **备份策略** | 按需 | 每日 | 实时 + 每日备份 |

---

## 2. 部署步骤说明

### 2.1 Docker Compose 部署（推荐）

#### 前置条件
- Docker 24.0+ 已安装
- Docker Compose 已安装
- 至少 8GB 内存可用

#### 部署步骤

1. **克隆代码仓库**
```bash
git clone <repository-url>
cd aiphxt-app
```

2. **配置环境变量**
```bash
# 复制并修改环境配置文件
cp .env.development .env

# 根据实际环境修改 .env 文件内容
```

3. **启动所有服务**
```bash
# 方式一：使用 docker-compose 直接启动
docker-compose up -d

# 方式二：使用启动脚本
./start_all.bat  # Windows
./start_all.sh   # Linux/Mac
```

4. **验证服务状态**
```bash
# 查看容器状态
docker-compose ps

# 查看服务日志
docker-compose logs -f

# 验证各服务是否正常运行
curl http://localhost:3000    # 前端
curl http://localhost:8080/api/health  # 后端
curl http://localhost:8000/api/v1/health  # AI服务
```

5. **停止服务**
```bash
docker-compose down

# 停止并删除数据卷（谨慎使用）
docker-compose down -v
```

### 2.2 Kubernetes 部署

#### 前置条件
- Kubernetes 1.28+ 集群已就绪
- kubectl 已配置
- Helm 3.0+ 已安装

#### 部署步骤

1. **创建命名空间**
```bash
kubectl apply -f k8s/namespace.yaml
```

2. **部署 MySQL**
```bash
kubectl apply -f k8s/mysql-deployment.yaml
```

3. **部署 Redis**
```bash
kubectl apply -f k8s/redis-deployment.yaml
```

4. **部署后端服务**
```bash
kubectl apply -f k8s/backend-deployment.yaml
```

5. **部署 AI服务**
```bash
kubectl apply -f k8s/ai-service-deployment.yaml
```

6. **部署前端服务**
```bash
kubectl apply -f k8s/frontend-deployment.yaml
```

7. **部署 Ingress**
```bash
kubectl apply -f k8s/ingress.yaml
```

8. **验证部署**
```bash
# 查看所有部署
kubectl get deployments -n yunnan-ai-school

# 查看所有 Pod
kubectl get pods -n yunnan-ai-school

# 查看服务
kubectl get services -n yunnan-ai-school

# 查看 Ingress
kubectl get ingress -n yunnan-ai-school
```

### 2.3 手动部署

#### 2.3.1 后端服务部署

1. **安装依赖**
```bash
cd backend
mvn clean install -DskipTests
```

2. **启动服务**
```bash
# 开发模式
mvn spring-boot:run

# 生产模式
java -jar target/backend-1.0.0.jar --spring.profiles.active=production
```

#### 2.3.2 AI服务部署

1. **创建虚拟环境**
```bash
cd ai-service
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动服务**
```bash
# 开发模式
uvicorn app.core.app:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn app.core.app:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 2.3.3 前端部署

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **构建项目**
```bash
# 开发环境构建
npm run build:dev

# 生产环境构建
npm run build:prod
```

3. **启动服务**
```bash
# 使用 Vite 开发服务器
npm run dev

# 使用静态文件服务器（生产环境）
npm run preview
```

---

## 3. 配置文件说明

### 3.1 后端配置 (`backend/src/main/resources/application.yml`)

#### 核心配置项

| 配置项 | 说明 | 示例值 |
|-------|------|-------|
| `server.port` | 服务端口 | 8081 |
| `server.servlet.context-path` | 上下文路径 | /api |
| `spring.datasource.url` | 数据库连接URL | jdbc:sqlite:./data/aiphxt.db |
| `spring.jpa.hibernate.ddl-auto` | DDL策略 | validate/production |
| `jwt.secret` | JWT密钥 | 32位以上随机字符串 |
| `jwt.expiration` | JWT过期时间（毫秒） | 3600000 |
| `ai.service.url` | AI服务地址 | http://localhost:8000 |

#### 多环境配置
```yaml
# 默认配置（开发环境）
spring:
  profiles:
    active: development

---
# 生产环境配置
spring:
  config:
    activate:
      on-profile: production
  datasource:
    url: ${DB_URL}
  jpa:
    show-sql: false
logging:
  level:
    root: warn
```

### 3.2 AI服务配置 (`ai-service/config.py`)

#### 核心配置项

| 配置项 | 说明 | 示例值 |
|-------|------|-------|
| `DEEPSEEK_CONFIG.api_key` | DeepSeek API密钥 | sk-xxx |
| `DEEPSEEK_CONFIG.base_url` | API基础URL | https://api.deepseek.com/v1 |
| `DEEPSEEK_CONFIG.model` | 模型名称 | deepseek-chat |
| `DEEPSEEK_CONFIG.max_tokens` | 最大token数 | 1024 |
| `DEEPSEEK_CONFIG.temperature` | 温度参数 | 0.5 |
| `DEEPSEEK_CONFIG.timeout` | 请求超时时间 | 30 |

#### 系统提示词配置
```python
SYSTEM_PROMPTS = {
    "policy_interpretation": "你是云南省中考政策解读专家...",
    "school_recommendation": "你是云南省中考择校顾问...",
    "volunteer_planning": "你是中考志愿填报专家...",
    "general_qa": "你是云南省中考择校智能助手..."
}
```

### 3.3 前端配置 (`frontend/.env`)

#### 环境变量配置

| 变量名 | 说明 | 示例值 |
|-------|------|-------|
| `VITE_API_BASE_URL` | 后端API地址 | http://localhost:8081/api |
| `VITE_AI_SERVICE_URL` | AI服务地址 | http://localhost:8000 |
| `VITE_APP_TITLE` | 应用标题 | AI择校助手 |
| `VITE_DEBUG` | 调试模式 | false |

#### 多环境配置文件
- `.env` - 默认配置
- `.env.development` - 开发环境
- `.env.production` - 生产环境

---

## 4. 监控和故障排查指南

### 4.1 监控指标

#### 4.1.1 服务健康检查

| 服务 | 健康检查端点 | 预期响应 |
|-----|------------|---------|
| 前端 | `GET /` | 返回HTML页面 |
| 后端 | `GET /api/health` | `{"status": "UP"}` |
| AI服务 | `GET /api/v1/health` | `{"status": "healthy"}` |
| MySQL | `mysql -h host -u user -p` | 成功连接 |
| Redis | `redis-cli ping` | `PONG` |
| RabbitMQ | `curl http://host:15672/api/health` | `{"status":"ok"}` |

#### 4.1.2 关键性能指标

| 指标类型 | 监控内容 | 告警阈值 |
|---------|---------|---------|
| **CPU使用率** | 各服务CPU占用 | >80% |
| **内存使用率** | 各服务内存占用 | >85% |
| **磁盘使用率** | 存储占用 | >90% |
| **响应时间** | API响应耗时 | >2s |
| **错误率** | HTTP错误比例 | >5% |
| **请求量** | QPS | 根据业务调整 |
| **队列长度** | RabbitMQ消息堆积 | >1000 |
| **缓存命中率** | Redis缓存命中 | <80% |

### 4.2 日志管理

#### 4.2.1 日志文件位置

| 服务 | 日志路径 | 日志文件名 |
|-----|---------|-----------|
| AI服务 | `ai-service/logs/` | app.log, error.log, access.log |
| 后端服务 | `backend/logs/` | application.log |
| 前端服务 | `frontend/logs/` | nginx.log |
| MySQL | `/var/log/mysql/` | error.log, slow.log |
| Redis | `/var/log/redis/` | redis-server.log |

#### 4.2.2 日志级别配置

| 级别 | 说明 | 适用场景 |
|-----|------|---------|
| DEBUG | 详细调试信息 | 开发环境 |
| INFO | 一般运行信息 | 测试环境 |
| WARN | 警告信息 | 生产环境 |
| ERROR | 错误信息 | 生产环境 |
| FATAL | 致命错误 | 生产环境 |

#### 4.2.3 日志轮转配置
```logrotate
/var/log/ai-service/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 640 www-data www-data
    sharedscripts
    postrotate
        /usr/bin/killall -HUP uvicorn
    endscript
}
```

### 4.3 常见故障排查

#### 4.3.1 服务启动失败

**问题现象**: 服务无法启动
**排查步骤**:
1. 检查端口是否被占用
```bash
netstat -ano | findstr :8000  # Windows
netstat -tlnp | grep :8000    # Linux
```
2. 检查依赖服务是否正常运行
```bash
docker-compose ps  # 检查容器状态
kubectl get pods   # Kubernetes环境
```
3. 查看启动日志
```bash
docker-compose logs ai-service
kubectl logs <pod-name> -n yunnan-ai-school
```
4. 检查配置文件是否正确
```bash
# 验证环境变量
echo $DEEPSEEK_API_KEY
echo $DB_PASSWORD
```

#### 4.3.2 数据库连接失败

**问题现象**: 后端服务无法连接数据库
**排查步骤**:
1. 检查数据库服务状态
```bash
docker-compose ps mysql
systemctl status mysql
```
2. 验证数据库连接参数
```bash
mysql -h localhost -u root -p -e "SELECT 1"
```
3. 检查网络连通性
```bash
ping mysql
telnet mysql 3306
```
4. 查看数据库日志
```bash
docker-compose logs mysql
cat /var/log/mysql/error.log
```

#### 4.3.3 API响应超时

**问题现象**: 前端调用API超时
**排查步骤**:
1. 检查后端服务状态
```bash
curl -v http://localhost:8080/api/health
```
2. 检查AI服务响应时间
```bash
curl -w "Response time: %{time_total}s\n" http://localhost:8000/api/v1/health
```
3. 检查数据库查询性能
```sql
EXPLAIN ANALYZE SELECT * FROM schools WHERE ...;
```
4. 查看慢查询日志
```bash
cat /var/log/mysql/slow.log
```

#### 4.3.4 Redis缓存问题

**问题现象**: 缓存数据不一致
**排查步骤**:
1. 检查Redis连接状态
```bash
redis-cli ping
redis-cli info stats
```
2. 检查缓存键是否存在
```bash
redis-cli KEYS "*school*"
redis-cli GET "school:1"
```
3. 检查缓存过期时间
```bash
redis-cli TTL "school:1"
```
4. 检查内存使用情况
```bash
redis-cli info memory
```

#### 4.3.5 AI服务API调用失败

**问题现象**: AI服务返回错误
**排查步骤**:
1. 检查API密钥是否正确
```bash
echo $DEEPSEEK_API_KEY
```
2. 验证API调用
```bash
curl -v -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Hello"}]}' \
     https://api.deepseek.com/v1/chat/completions
```
3. 检查网络代理设置
```bash
echo $HTTP_PROXY
echo $HTTPS_PROXY
```
4. 查看AI服务日志
```bash
cat ai-service/logs/error.log
```

### 4.3.6 前端页面无法访问

**问题现象**: 浏览器无法加载页面
**排查步骤**:
1. 检查前端服务状态
```bash
docker-compose ps frontend
curl http://localhost:3000
```
2. 检查Nginx配置
```bash
nginx -t
cat /etc/nginx/conf.d/default.conf
```
3. 检查网络配置
```bash
curl -I http://localhost:3000
nslookup your-domain.com
```
4. 查看浏览器控制台错误
```bash
# 在浏览器开发者工具中查看 Console 和 Network 标签
```

---

## 附录

### A. 常用命令速查

```bash
# Docker Compose 相关
docker-compose up -d          # 启动服务
docker-compose down           # 停止服务
docker-compose logs -f        # 查看日志
docker-compose ps             # 查看状态

# Kubernetes 相关
kubectl get pods             # 查看Pod
kubectl get services         # 查看服务
kubectl logs <pod-name>      # 查看Pod日志
kubectl exec -it <pod-name> -- bash  # 进入Pod

# 数据库相关
mysql -h host -u user -p     # 连接MySQL
redis-cli                    # 连接Redis
sqlite3 data/aiphxt.db       # 连接SQLite

# 服务健康检查
curl http://localhost:8080/api/health
curl http://localhost:8000/api/v1/health
```

### B. 紧急恢复流程

1. **备份当前状态**
```bash
# 备份数据库
mysqldump -u root -p school_platform > backup.sql

# 备份配置文件
cp -r config/ config_backup/

# 备份日志
cp -r logs/ logs_backup/
```

2. **停止所有服务**
```bash
docker-compose down
```

3. **恢复数据库**
```bash
mysql -u root -p school_platform < backup.sql
```

4. **启动服务**
```bash
docker-compose up -d
```

5. **验证恢复**
```bash
curl http://localhost:8080/api/health
curl http://localhost:3000
```

---

**文档版本**: v1.0  
**最后更新**: 2026年5月  
**维护人**: 运维团队