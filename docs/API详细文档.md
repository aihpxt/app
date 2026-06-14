# 云南省AI择校平台 - API详细文档

**版本**: 1.0.0  
**最后更新**: 2026-05-18

---

## 目录

1. [概述](#1-概述)
2. [认证](#2-认证)
3. [基础URL](#3-基础url)
4. [API端点](#4-api端点)
   - [健康检查](#41-健康检查)
   - [认证接口](#42-认证接口)
   - [学校接口](#43-学校接口)
   - [AI接口](#44-ai接口)
   - [用户接口](#45-用户接口)
5. [错误码](#5-错误码)
6. [速率限制](#6-速率限制)
7. [Swagger文档](#7-swagger文档)

---

## 1. 概述

本文档描述了云南省AI择校平台的所有REST API接口。

### 1.1 数据格式

所有请求和响应均使用 JSON 格式：
```http
Content-Type: application/json
```

### 1.2 HTTP状态码

| 状态码 | 描述 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 2. 认证

### 2.1 获取Token

使用用户名和密码获取访问令牌：

**请求：**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 2.2 使用Token

在需要认证的接口请求头中添加：

```http
Authorization: Bearer <access_token>
```

### 2.3 Token过期

Token有效期为30分钟。过期后需要重新登录获取新的Token。

---

## 3. 基础URL

### 开发环境
```
http://localhost:8001
```

### 生产环境
```
https://your-domain.com
```

---

## 4. API端点

### 4.1 健康检查

#### 4.1.1 基础健康检查

检查服务是否正常运行。

**请求：**
```http
GET /health
```

**响应：**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-18T10:30:00Z"
}
```

#### 4.1.2 详细健康检查

检查所有依赖服务的状态。

**请求：**
```http
GET /health/detailed
```

**响应：**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-18T10:30:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "ai_service": "healthy"
  },
  "version": "1.0.0"
}
```

#### 4.1.3 就绪检查

检查服务是否准备好接收流量。

**请求：**
```http
GET /health/ready
```

**响应：**
```json
{
  "ready": true,
  "timestamp": "2026-05-18T10:30:00Z"
}
```

---

### 4.2 认证接口

#### 4.2.1 用户注册

**请求：**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "phone": "13800138000"
}
```

**响应：**
```json
{
  "success": true,
  "message": "注册成功",
  "user_id": 1
}
```

#### 4.2.2 用户登录

**请求：**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user"
  }
}
```

#### 4.2.3 刷新Token

**请求：**
```http
POST /api/v1/auth/refresh
Authorization: Bearer <access_token>
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### 4.3 学校接口

#### 4.3.1 获取学校列表

**请求：**
```http
GET /api/v1/schools?page=1&limit=20&keyword=&region=
```

**查询参数：**
| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| limit | int | 否 | 每页数量，默认20 |
| keyword | string | 否 | 搜索关键词 |
| region | string | 否 | 地区筛选 |

**响应：**
```json
{
  "data": [
    {
      "id": 1,
      "name": "昆明市第一中学",
      "region": "昆明市",
      "type": "公办",
      "address": "昆明市五华区",
      "phone": "0871-12345678",
      "scores": {
        "2025": 550,
        "2024": 545
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

#### 4.3.2 获取学校详情

**请求：**
```http
GET /api/v1/schools/{id}
```

**响应：**
```json
{
  "id": 1,
  "name": "昆明市第一中学",
  "region": "昆明市",
  "type": "公办",
  "address": "昆明市五华区",
  "phone": "0871-12345678",
  "description": "学校简介...",
  "scores": {
    "2025": 550,
    "2024": 545,
    "2023": 540
  },
  "features": ["重点高中", "示范学校"],
  "images": ["url1.jpg", "url2.jpg"]
}
```

#### 4.3.3 搜索学校

**请求：**
```http
GET /api/v1/schools/search?q=一中
```

**响应：**
```json
{
  "data": [
    {
      "id": 1,
      "name": "昆明市第一中学",
      "region": "昆明市",
      "type": "公办"
    }
  ]
}
```

---

### 4.4 AI接口

#### 4.4.1 AI智能推荐

**请求：**
```http
POST /api/v1/ai/recommend
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "score": 550,
  "region": "昆明市",
  "interest": "理科",
  "preferences": []
}
```

**响应：**
```json
{
  "recommendations": [
    {
      "school": {
        "id": 1,
        "name": "昆明市第一中学"
      },
      "probability": "高",
      "reason": "分数匹配，学校特色符合",
      "suggestion": "建议填报第一志愿"
    }
  ]
}
```

#### 4.4.2 分数预测

**请求：**
```http
POST /api/v1/ai/predict-score
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "mock_scores": [520, 530, 540],
  "target_school": "昆明市第一中学"
}
```

**响应：**
```json
{
  "predicted_score": 545,
  "confidence": 0.85,
  "suggestions": ["重点复习数学", "保持当前状态"]
}
```

#### 4.4.3 AI助手对话

**请求：**
```http
POST /api/v1/ai/chat
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "昆明一中历年分数线是多少？",
  "context": []
}
```

**响应：**
```json
{
  "response": "昆明市第一中学2025年分数线为550分，2024年为545分...",
  "context": [...]
}
```

---

### 4.5 用户接口

#### 4.5.1 获取用户信息

**请求：**
```http
GET /api/v1/user/profile
Authorization: Bearer <access_token>
```

**响应：**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "phone": "13800138000",
  "avatar": "avatar.jpg",
  "created_at": "2026-01-01T00:00:00Z"
}
```

#### 4.5.2 更新用户信息

**请求：**
```http
PUT /api/v1/user/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "phone": "13900139000",
  "avatar": "new_avatar.jpg"
}
```

**响应：**
```json
{
  "success": true,
  "message": "更新成功"
}
```

#### 4.5.3 收藏学校

**请求：**
```http
POST /api/v1/user/favorites
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "school_id": 1
}
```

**响应：**
```json
{
  "success": true,
  "message": "收藏成功"
}
```

#### 4.5.4 获取收藏列表

**请求：**
```http
GET /api/v1/user/favorites
Authorization: Bearer <access_token>
```

**响应：**
```json
{
  "data": [
    {
      "id": 1,
      "school": {
        "id": 1,
        "name": "昆明市第一中学"
      },
      "created_at": "2026-05-01T00:00:00Z"
    }
  ]
}
```

---

## 5. 错误码

| 错误码 | 描述 |
|--------|------|
| 40001 | 请求参数错误 |
| 40101 | 未授权 |
| 40102 | Token过期 |
| 40301 | 无权限访问 |
| 40401 | 资源不存在 |
| 42901 | 请求过于频繁 |
| 50001 | 服务器内部错误 |

**错误响应格式：**
```json
{
  "error": {
    "code": "40001",
    "message": "请求参数错误",
    "details": "username不能为空"
  }
}
```

---

## 6. 速率限制

为了保护服务，API实施速率限制：

- **普通用户**: 100次/分钟
- **管理员**: 1000次/分钟

超过限制会返回 `429 Too Many Requests`。

---

## 7. Swagger文档

### 7.1 在线文档

系统启动后，访问以下地址查看交互式API文档：

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`
- **OpenAPI JSON**: `http://localhost:8001/openapi.json`

### 7.2 导出为HTML/PDF

#### 使用Swagger UI导出

1. 访问 `http://localhost:8001/docs`
2. 点击「Print」按钮
3. 选择「保存为PDF」

#### 使用工具导出

**安装工具：**
```bash
npm install -g @redocly/cli
```

**导出HTML：**
```bash
redocly build-docs http://localhost:8001/openapi.json -o api-docs.html
```

**导出PDF（需要puppeteer）：**
```bash
npm install -g @microsoft/rush
node -e "
const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:8001/docs', {waitUntil: 'networkidle0'});
  await page.pdf({path: 'api-docs.pdf', format: 'A4'});
  await browser.close();
})();
"
```

---

## 附录

### A. 示例代码

#### JavaScript (Axios)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 设置Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 登录
async function login(username, password) {
  const response = await api.post('/api/v1/auth/login', { username, password });
  localStorage.setItem('token', response.data.access_token);
  return response.data;
}

// 获取学校列表
async function getSchools(params) {
  const response = await api.get('/api/v1/schools', { params });
  return response.data;
}
```

#### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8001"

def login(username, password):
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    return response.json()

def get_schools(token, params=None):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/schools",
        headers=headers,
        params=params
    )
    return response.json()
```

### B. 联系支持

如有API相关问题，请联系：
- 技术支持邮箱：dev@example.com
- API版本更新：每月1日

---

*更多API详情请访问在线Swagger文档！*
