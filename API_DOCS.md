# 云南省AI全域赋能中考择校智能决策平台 API文档

## 1. 系统架构

### 1.1 技术栈
- **前端**：Vue 3 + Vite + Element Plus
- **后端**：Spring Boot 3.2.x + MySQL 8.0 + Redis 7.2
- **AI服务**：FastAPI + Python 3.10+

### 1.2 服务地址
- **前端**：http://localhost:3000
- **后端API**：http://localhost:8080
- **AI服务API**：http://localhost:8000

## 2. 后端API

### 2.1 认证相关

#### 2.1.1 登录
- **接口**：`POST /api/auth/login`
- **参数**：
  - `username`：用户名
  - `password`：密码
- **返回**：
  - `token`：JWT令牌
  - `user`：用户信息

#### 2.1.2 注册
- **接口**：`POST /api/auth/register`
- **参数**：
  - `username`：用户名
  - `password`：密码
  - `email`：邮箱
- **返回**：
  - `success`：是否成功
  - `message`：提示信息

### 2.2 学校相关

#### 2.2.1 获取学校列表
- **接口**：`GET /api/schools`
- **参数**：
  - `page`：页码
  - `size`：每页数量
  - `type`：学校类型
  - `city`：城市
- **返回**：
  - `total`：总数
  - `schools`：学校列表

#### 2.2.2 获取学校详情
- **接口**：`GET /api/schools/{id}`
- **参数**：
  - `id`：学校ID
- **返回**：
  - 学校详细信息

### 2.3 政策相关

#### 2.3.1 获取政策列表
- **接口**：`GET /api/policies`
- **参数**：
  - `page`：页码
  - `size`：每页数量
  - `category`：政策类别
- **返回**：
  - `total`：总数
  - `policies`：政策列表

#### 2.3.2 获取政策详情
- **接口**：`GET /api/policies/{id}`
- **参数**：
  - `id`：政策ID
- **返回**：
  - 政策详细信息

## 3. AI服务API

### 3.1 AI模型预测

#### 3.1.1 学校推荐
- **接口**：`POST /api/ai/recommend`
- **参数**：
  - `score`：分数
  - `rank`：位次
  - `district`：地区
  - `interests`：兴趣爱好
  - `features`：学校特色
- **返回**：
  - `schools`：推荐学校列表
  - `probability`：录取概率
  - `match_score`：匹配度

#### 3.1.2 录取概率预测
- **接口**：`POST /api/ai/predict`
- **参数**：
  - `school_id`：学校ID
  - `score`：分数
  - `rank`：位次
- **返回**：
  - `probability`：录取概率
  - `suggestion`：建议

#### 3.1.3 志愿规划
- **接口**：`POST /api/ai/generate-plan`
- **参数**：
  - `score`：分数
  - `rank`：位次
  - `district`：地区
  - `schools`：目标学校列表
- **返回**：
  - `sprint`：冲刺学校
  - `safe`：稳妥学校
  - `backup`：保底学校
  - `advice`：建议

#### 3.1.4 政策解读
- **接口**：`POST /api/ai/interpret-policy`
- **参数**：
  - `policy_text`：政策文本
  - `question`：问题
- **返回**：
  - `summary`：政策摘要
  - `details`：详细解读
  - `answer`：问题答案
  - `related_policies`：相关政策

### 3.2 数据管理

#### 3.2.1 获取学校数据
- **接口**：`GET /api/data/schools`
- **参数**：
  - `page`：页码
  - `size`：每页数量
- **返回**：
  - `total`：总数
  - `schools`：学校列表

#### 3.2.2 获取政策数据
- **接口**：`GET /api/data/policies`
- **参数**：
  - `page`：页码
  - `size`：每页数量
- **返回**：
  - `total`：总数
  - `policies`：政策列表

### 3.3 智能体服务

#### 3.3.1 智能体对话
- **接口**：`POST /api/agents/chat`
- **参数**：
  - `message`：消息内容
  - `agent_id`：智能体ID
  - `context`：上下文信息
- **返回**：
  - `response`：智能体回复
  - `thought`：智能体思考过程
  - `actions`：执行的动作

#### 3.3.2 获取智能体列表
- **接口**：`GET /api/agents`
- **返回**：
  - `agents`：智能体列表

## 4. 前端API调用示例

### 4.1 登录
```javascript
import request from '@/utils/request';

export function login(data) {
  return request({
    url: '/api/auth/login',
    method: 'post',
    data
  });
}
```

### 4.2 获取学校列表
```javascript
export function getSchools(params) {
  return request({
    url: '/api/schools',
    method: 'get',
    params
  });
}
```

### 4.3 AI学校推荐
```javascript
export function recommendSchools(data) {
  return request({
    url: '/api/ai/recommend',
    method: 'post',
    data
  });
}
```

## 5. 认证与授权

### 5.1 JWT认证
- 登录成功后获取JWT令牌
- 在请求头中添加 `Authorization: Bearer {token}`
- 令牌有效期为30分钟

### 5.2 权限管理
- **普通用户**：可查看学校和政策信息，使用AI服务
- **管理员**：可管理学校和政策数据，审核用户贡献

## 6. 错误处理

### 6.1 错误码
- `400`：参数错误
- `401`：未认证
- `403`：未授权
- `404`：资源不存在
- `500`：服务器内部错误

### 6.2 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误信息"
  }
}
```

## 7. 性能优化

### 7.1 缓存策略
- 使用Redis缓存热点数据
- 接口响应缓存1小时
- 定期清理过期缓存

### 7.2 速率限制
- 每个IP每分钟最多100个请求
- 超过限制将返回429错误

## 8. 安全措施

### 8.1 数据加密
- 密码使用bcrypt加密存储
- JWT令牌使用环境变量中的密钥
- 敏感数据传输使用HTTPS

### 8.2 防护措施
- CORS配置限制来源域名
- 安全头部设置
- CSRF令牌验证
- 输入参数验证

## 9. 部署与维护

### 9.1 部署方式
- Docker Compose一键部署
- Kubernetes集群部署

### 9.2 维护命令
- 启动服务：`docker-compose up -d`
- 查看日志：`docker-compose logs -f`
- 重启服务：`docker-compose restart`

## 10. 测试账号

- **手机号**：13800138000
- **密码**：123456

## 11. 联系我们

- **官方网站**：https://aiphxt.com
- **邮箱**：contact@aiphxt.com
- **技术支持**：support@aiphxt.com
