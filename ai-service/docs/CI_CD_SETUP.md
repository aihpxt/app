# CI/CD 流水线搭建说明

## 概述

本项目支持多种CI/CD平台：
- GitHub Actions
- GitLab CI
- Jenkins
- 本地脚本

## 1. GitHub Actions

### 设置 Secrets

在 GitHub 仓库设置中添加以下 Secrets：

```
DOCKERHUB_USERNAME    - Docker Hub 用户名
DOCKERHUB_TOKEN       - Docker Hub 访问令牌
SERVER_HOST          - 服务器地址
SERVER_USER          - 服务器用户名
SERVER_SSH_KEY       - SSH 私钥
```

### 工作流触发

- **Push**: main 和 develop 分支
- **Pull Request**: main 分支
- **手动触发**: 通过 GitHub API

### 流水线阶段

1. **Test** - 运行单元测试和覆盖率
2. **Lint** - 代码检查（flake8, black）
3. **Build** - 构建 Docker 镜像
4. **Security Scan** - 安全扫描（bandit, safety）
5. **Deploy** - 部署到服务器（仅 main 分支）

## 2. GitLab CI

### 设置 CI/CD 变量

在 GitLab 项目设置中添加：

```
CI_REGISTRY_USER      - Docker Registry 用户名
CI_REGISTRY_PASSWORD  - Docker Registry 密码
CI_REGISTRY_IMAGE     - 镜像地址
DEPLOY_HOST          - 部署服务器地址
DEPLOY_USER          - 部署服务器用户名
```

### Runner 配置

确保 Runner 标签为 `docker` 或 `linux`。

## 3. Jenkins

### 插件要求

- Docker Pipeline
- JUnit Plugin
- HTML Publisher Plugin
- Credentials Plugin
- SSH Agent Plugin

### 凭证配置

添加以下凭证：
- Docker Registry 凭证
- 服务器 SSH 密钥

## 4. 本地使用

### 使用 Makefile

```bash
# 安装依赖
make install

# 运行测试
make test

# 代码检查
make lint

# 格式化代码
make format

# 构建 Docker 镜像
make docker-build

# 运行 Docker 容器
make docker-run

# 部署
make deploy DEPLOY_USER=user DEPLOY_HOST=server.com
```

### 使用脚本

```bash
# CI 模式（安装 + 检查 + 测试）
./scripts/ci.sh ci

# 仅安装依赖
./scripts/ci.sh install

# 仅测试
./scripts/ci.sh test

# 仅检查代码
./scripts/ci.sh lint

# 构建 Docker
./scripts/ci.sh build

# 部署
DEPLOY_USER=user DEPLOY_HOST=server.com ./scripts/ci.sh deploy
```

## 5. Docker Compose 部署

### 快速启动

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重新构建
docker-compose up -d --build
```

### 服务说明

- **redis**: 缓存服务
- **ai-service**: 主服务
- **prometheus**: 监控服务

## 6. 生产环境部署

### 服务器准备

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
apt-get install docker-compose

# 创建应用目录
mkdir -p /opt/ai-service
cd /opt/ai-service

# 克隆代码
git clone <repo-url> .
```

### 环境配置

创建 `.env` 文件：

```bash
REDIS_HOST=redis
REDIS_PORT=6379
DEBUG=False
LOG_LEVEL=INFO
HTTPS_ENABLED=true
SSL_CERT_FILE=/app/certs/server.crt
SSL_KEY_FILE=/app/certs/server.key
```

### 启动服务

```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f ai-service
```

### HTTPS 配置

1. 获取 SSL 证书
2. 将证书复制到 `certs/` 目录
3. 设置 `HTTPS_ENABLED=true`
4. 重启服务

## 7. 自动化部署流程

### GitHub Actions 自动部署

1. 提交代码到 develop 分支
2. 自动触发测试和构建
3. 手动确认后部署到 staging
4. 合并到 main 分支
5. 自动部署到生产环境

### 回滚策略

```bash
# 查看历史版本
docker images ai-service

# 回滚到指定版本
docker tag ai-service:<version> ai-service:latest
docker-compose up -d
```

## 8. 监控和告警

### Prometheus 配置

访问 http://localhost:9090 查看监控数据。

### Grafana 集成

1. 添加 Prometheus 数据源
2. 导入监控面板模板
3. 设置告警规则

## 9. 安全建议

1. **定期更新依赖**: `pip install -r requirements.txt --upgrade`
2. **密钥管理**: 使用 CI/CD 平台的密钥管理功能
3. **容器安全**: 定期运行安全扫描
4. **日志审计**: 启用审计日志并定期审查
5. **HTTPS**: 生产环境必须启用 HTTPS
