# 云南省AI全域赋能中考择校智能决策平台启动说明

## 项目结构

```
├── frontend/          # 前端项目（Vue3 + Element Plus）
├── backend/           # 后端服务（SpringBoot 3.2.x）
├── ai-service/        # AI模型服务（FastAPI + Python）
├── sql/               # 数据库脚本
├── docker-compose.yml # Docker Compose配置
├── README.md          # 项目说明
└── START.md           # 启动说明
```

## 快速启动（Docker方式）

### 环境要求
- Docker 20.10+ 
- Docker Compose 1.29+

### 启动步骤

1. **克隆项目**
   ```bash
   git clone <项目地址>
   cd yunnan-ai-school-platform
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **服务访问**
   - Web端：http://localhost:3000
   - API文档：http://localhost:8080/api-docs
   - AI服务：http://localhost:8000/docs
   - Nacos控制台：http://localhost:8848/nacos
   - RabbitMQ管理：http://localhost:15672

4. **停止服务**
   ```bash
   docker-compose down
   ```

## 本地开发启动

### 环境要求
- JDK 17+
- Python 3.10+
- Node.js 16+
- MySQL 8.0+
- Redis 7.2+
- RabbitMQ 3.12+
- Nacos 2.2.0+

### 启动步骤

1. **初始化数据库**
   ```bash
   # 启动MySQL服务
   # 执行数据库脚本
   mysql -u root -p < sql/init.sql
   ```

2. **启动后端服务**
   ```bash
   cd backend
   mvn clean install
   mvn spring-boot:run
   ```

3. **启动AI服务**
   ```bash
   cd ai-service
   pip install -r requirements.txt
   python main.py
   ```

4. **启动前端服务**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **服务访问**
   - Web端：http://localhost:3000
   - API文档：http://localhost:8080/api-docs
   - AI服务：http://localhost:8000/docs

## 项目功能模块

### 1. 用户模块
- 注册登录（手机号+验证码、微信授权）
- 个人信息管理
- 考生信息录入与核验
- 权限管理（四级权限）

### 2. 学校数据模块
- 学校信息管理
- 学校检索与筛选
- 学校对比分析
- 录取数据展示

### 3. AI择校决策模块
- 录取概率预测
- 志愿智能推荐
- 分数校准
- 个性化择校方案

### 4. 政策服务模块
- 政策智能解读
- 政策查询与筛选
- 智能问答

### 5. 统计分析模块
- 数据可视化分析
- 趋势分析
- 区域对比

## 测试账号

### 用户账号
- 手机号：13800138000
- 密码：123456
- 角色：考生/家长

### 管理员账号
- 手机号：13800138001
- 密码：123456
- 角色：管理员

## 技术支持

- 技术团队：AI教育技术团队
- 邮箱：support@yunnan-ai-education.com
- 电话：0871-65123456

## 注意事项

1. **首次启动**：使用Docker方式启动时，系统会自动初始化数据库并加载测试数据
2. **数据安全**：生产环境请修改默认密码和配置
3. **性能优化**：生产环境建议使用Redis集群和MySQL主从复制
4. **监控告警**：生产环境建议配置Prometheus + Grafana监控

---

**项目启动成功后，您可以通过Web端访问平台，开始使用AI赋能的中考择校智能决策服务！**