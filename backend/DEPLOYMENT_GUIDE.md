# 后端服务部署和使用指南

## 1. 环境要求

- Java 17 或更高版本
- Maven 3.8 或更高版本
- MySQL 8.0 或更高版本
- Redis 7.0 或更高版本（可选，用于缓存）

## 2. 数据库配置

1. 创建 MySQL 数据库：
   ```sql
   CREATE DATABASE aiphxt CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. 修改 `application.yml` 文件中的数据库连接信息：
   ```yaml
   spring:
     datasource:
       url: jdbc:mysql://localhost:3306/aiphxt?useUnicode=true&characterEncoding=utf-8&useSSL=false&serverTimezone=Asia/Shanghai
       username: root
       password: 123456
   ```

## 3. 构建项目

1. 进入后端项目目录：
   ```bash
   cd backend
   ```

2. 构建项目：
   ```bash
   mvn clean package
   ```

3. 构建成功后，在 `target` 目录中会生成 `backend-1.0.0.jar` 文件。

## 4. 运行服务

1. 直接运行 jar 文件：
   ```bash
   java -jar target/backend-1.0.0.jar
   ```

2. 或者使用 Spring Boot Maven 插件运行：
   ```bash
   mvn spring-boot:run
   ```

3. 服务默认运行在 `http://localhost:8080/api`。

## 5. Docker 部署

1. 构建 Docker 镜像：
   ```bash
   docker build -t aiphxt-backend .
   ```

2. 运行 Docker 容器：
   ```bash
   docker run -p 8080:8080 --name aiphxt-backend \
     -e SPRING_DATASOURCE_URL=jdbc:mysql://host.docker.internal:3306/aiphxt \
     -e SPRING_DATASOURCE_USERNAME=root \
     -e SPRING_DATASOURCE_PASSWORD=123456 \
     -e AI_SERVICE_URL=http://host.docker.internal:8000 \
     aiphxt-backend
   ```

## 6. API 接口

### 6.1 认证接口

- **注册**：`POST /api/auth/register`
  - 请求体：
    ```json
    {
      "username": "user1",
      "email": "user1@example.com",
      "hashedPassword": "password123"
    }
    ```

- **登录**：`POST /api/auth/login`
  - 请求体：
    ```json
    {
      "username": "user1",
      "password": "password123"
    }
    ```

### 6.2 AI 服务接口

- **推荐学校**：`POST /api/ai/recommend`
  - 请求体：
    ```json
    {
      "score": 680,
      "rank": 2000,
      "district": "昆明",
      "interests": ["科学", "技术"],
      "features": ["省一级一等", "寄宿"]
    }
    ```

- **预测录取概率**：`POST /api/ai/predict`
  - 请求体：
    ```json
    {
      "schoolId": 1,
      "score": 680,
      "rank": 2000
    }
    ```

- **生成志愿规划**：`POST /api/ai/generate-plan`
  - 请求体：
    ```json
    {
      "score": 680,
      "rank": 2000,
      "district": "昆明",
      "schools": [1, 2, 3]
    }
    ```

- **解读政策**：`POST /api/ai/interpret-policy`
  - 请求体：
    ```json
    {
      "policyText": "云南省中考实行平行志愿录取模式...",
      "question": "平行志愿是什么意思？"
    }
    ```

## 7. 集成前端

前端项目需要修改 `vite.config.js` 文件中的代理设置，指向后端服务：

```javascript
server: {
  port: 3000,
  host: '0.0.0.0',
  open: true,
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true,
      rewrite: (path) => path
    }
  }
}
```

## 8. 监控和日志

- 服务日志：`logs/` 目录
- Spring Boot Actuator 监控：`http://localhost:8080/api/actuator`

## 9. 注意事项

1. 确保 AI 服务（FastAPI）运行在 `http://localhost:8000`，或者修改 `application.yml` 中的 `ai.service.url` 配置。
2. 第一次运行时，系统会自动创建数据库表结构。
3. 生产环境中，需要修改 `application.yml` 中的 `jwt.secret` 配置，使用安全的密钥。
4. 生产环境中，建议启用 HTTPS 并配置合适的安全措施。

## 10. 故障排查

1. **数据库连接失败**：检查数据库服务是否运行，连接信息是否正确。
2. **AI 服务连接失败**：检查 AI 服务是否运行，URL 是否正确。
3. **端口占用**：检查 8080 端口是否被占用，可修改 `application.yml` 中的 `server.port` 配置。
4. **权限问题**：检查数据库用户权限，确保有足够的权限创建和修改表结构。

## 11. 性能优化

1. **缓存**：启用 Redis 缓存，提高响应速度。
2. **数据库索引**：为频繁查询的字段添加索引。
3. **连接池**：配置合适的数据库连接池大小。
4. **异步处理**：对于耗时操作，使用异步处理。
5. **负载均衡**：在生产环境中，可使用负载均衡提高系统可用性。