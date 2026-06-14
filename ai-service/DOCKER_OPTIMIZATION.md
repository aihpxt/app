# Docker容器化优化指南

## 概述

本文档记录了AI服务平台Docker容器化优化的实施情况和建议。

---

## 当前优化措施

### 1. 多阶段构建

#### Dockerfile.optimized
```dockerfile
# 第一阶段：构建
FROM python:3.10-slim as builder
RUN pip install --no-cache-dir --user -r requirements.txt

# 第二阶段：运行
FROM python:3.10-slim
COPY --from=builder /root/.local /root/.local
```

**优势**:
- 减小最终镜像大小（只包含运行时依赖）
- 构建依赖不在最终镜像中
- 提高安全性

### 2. 非Root用户

```dockerfile
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser
```

**优势**:
- 提高容器安全性
- 符合最小权限原则
- 避免容器逃逸风险

### 3. 环境变量优化

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
```

**优势**:
- 减少镜像体积
- 提高Python性能
- 优化日志输出

### 4. .dockerignore优化

已配置排除:
- Python缓存文件
- 测试文件
- 数据库文件
- 日志文件
- 临时文件
- 环境配置文件

**优势**:
- 减小构建上下文
- 加快构建速度
- 减少镜像体积

### 5. 健康检查

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1
```

**优势**:
- 自动监控容器健康状态
- 支持Docker健康检查
- 便于编排系统管理

---

## 建议的额外优化

### 6. 镜像构建优化

#### 使用构建缓存
```dockerfile
# 按依赖变更频率排序，先复制不变的文件
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY package*.json ./
RUN npm ci --only=production

COPY . .
```

#### 并行构建
```bash
docker build -t aiphxt-service:latest --progress=plain .
```

### 7. 镜像大小优化

#### 当前镜像大小估算
- python:3.10-slim: ~45MB
- 依赖包: ~100-200MB
- 应用代码: ~50MB
- **总计**: ~200-300MB

#### 优化建议
1. 使用alpine基础镜像（更小但需额外配置）
2. 清理不必要的文件
3. 使用.dockerignore排除不必要文件
4. 分离开发和生产依赖

### 8. 资源限制配置

#### docker-compose.yml
```yaml
services:
  ai-service:
    build: .
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

#### Kubernetes
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

### 9. 安全加固

#### 只读文件系统
```yaml
securityContext:
  readOnlyRootFilesystem: true
```

#### 禁止特权模式
```yaml
securityContext:
  privileged: false
  allowPrivilegeEscalation: false
```

#### 限制Capabilities
```yaml
securityContext:
  capabilities:
    drop:
      - ALL
```

### 10. 网络配置

#### 使用自定义网络
```yaml
networks:
  app-network:
    driver: bridge

services:
  ai-service:
    networks:
      - app-network
```

---

## 部署指南

### 使用优化后的Dockerfile

```bash
# 构建镜像
docker build -t aiphxt-service:optimized -f Dockerfile.optimized .

# 运行容器
docker run -d \
  --name aiphxt-service \
  -p 8001:8001 \
  --health-cmd="python -c 'import urllib.request; urllib.request.urlopen(\"http://localhost:8001/health\")'" \
  --memory="2g" \
  --cpus="2" \
  aiphxt-service:optimized

# 检查健康状态
docker inspect --format='{{.State.Health.Status}}' aiphxt-service
```

### 使用docker-compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f ai-service

# 查看健康状态
docker-compose ps
```

---

## 镜像构建最佳实践

### 1. 构建优化
- [x] 使用多阶段构建
- [x] 使用 slim 基础镜像
- [x] 清理不必要的文件
- [x] 使用.dockerignore

### 2. 安全优化
- [x] 使用非root用户
- [ ] 配置只读文件系统
- [ ] 限制Capabilities
- [ ] 扫描安全漏洞

### 3. 性能优化
- [x] 配置健康检查
- [ ] 配置资源限制
- [ ] 优化启动时间
- [ ] 优化构建缓存

### 4. 可维护性
- [x] 清晰的Dockerfile结构
- [x] 详细的注释
- [ ] 使用构建参数
- [ ] 多平台构建支持

---

## 性能测试

### 镜像大小对比

| 版本 | 基础镜像 | 预估大小 | 优化效果 |
|------|----------|----------|----------|
| 原版 | python:3.10-alpine | ~300MB | - |
| 优化版 | python:3.10-slim | ~250MB | 17%减小 |
| 精简版 | python:3.10-alpine | ~150MB | 50%减小 |

### 构建时间对比

| 操作 | 首次构建 | 使用缓存 |
|------|----------|----------|
| 原版 | ~3分钟 | ~30秒 |
| 优化版 | ~2.5分钟 | ~20秒 |

---

## 监控和日志

### 容器监控
```bash
# 查看资源使用
docker stats

# 查看容器进程
docker top aiphxt-service

# 查看健康检查日志
docker inspect aiphxt-service | grep -A 10 Health
```

### 日志管理
```bash
# 查看日志
docker logs aiphxt-service

# 实时查看日志
docker logs -f aiphxt-service

# 日志轮转配置
docker run -d \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  aiphxt-service
```

---

## 故障排查

### 常见问题

#### 1. 容器启动失败
```bash
# 查看错误日志
docker logs aiphxt-service

# 进入容器调试
docker run -it aiphxt-service /bin/sh
```

#### 2. 健康检查失败
```bash
# 检查健康端点
curl http://localhost:8001/health

# 检查容器网络
docker exec aiphxt-service ping redis
```

#### 3. 资源不足
```bash
# 查看资源使用
docker stats

# 增加资源限制
docker update --memory=4g aiphxt-service
```

---

## 总结

当前Docker配置已经具备基本的优化措施，包括：
- ✅ 多阶段构建
- ✅ 非root用户
- ✅ 环境变量优化
- ✅ .dockerignore配置
- ✅ 健康检查

建议的后续优化包括：
- ⏳ 安全加固（只读文件系统、Capabilities限制）
- ⏳ 资源限制配置
- ⏳ 镜像扫描和签名
- ⏳ 多平台构建支持

通过实施这些优化，可以显著提升容器安全性、可维护性和性能。
