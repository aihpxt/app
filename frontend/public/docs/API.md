# 云南省AI全域赋能中考择校智能决策平台 API 文档

## 基础信息

- **基础URL**: `http://localhost:8080/api`
- **请求格式**: JSON
- **响应格式**: JSON
- **认证方式**: Bearer Token

## 通用响应格式

```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

## 用户模块

### 1. 用户注册

- **URL**: `/user/register`
- **Method**: POST
- **请求参数**:

```json
{
  "phone": "13800138000",
  "password": "123456",
  "nickname": "测试用户"
}
```

- **响应示例**:

```json
{
  "success": true,
  "message": "注册成功",
  "data": null
}
```

### 2. 用户登录

- **URL**: `/user/login`
- **Method**: POST
- **请求参数**:

```json
{
  "phone": "13800138000",
  "password": "123456"
}
```

- **响应示例**:

```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "mock_token_123456",
    "userId": 1,
    "phone": "13800138000",
    "role": 1
  }
}
```

### 3. 获取用户信息

- **URL**: `/user/info`
- **Method**: GET
- **Headers**: `Authorization: Bearer {token}`
- **响应示例**:

```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "id": 1,
    "phone": "13800138000",
    "nickname": "测试用户",
    "role": 1,
    "avatar": ""
  }
}
```

### 4. 更新用户信息

- **URL**: `/user/info`
- **Method**: PUT
- **Headers**: `Authorization: Bearer {token}`
- **请求参数**:

```json
{
  "nickname": "新昵称",
  "avatar": "https://example.com/avatar.jpg"
}
```

### 5. 学籍核验

- **URL**: `/user/student/verify`
- **Method**: POST
- **Headers**: `Authorization: Bearer {token}`
- **请求参数**:

```json
{
  "examId": "2026010001",
  "idCard": "530102201001011234"
}
```

### 6. 获取考生信息

- **URL**: `/user/student/info`
- **Method**: GET
- **Headers**: `Authorization: Bearer {token}`

### 7. 保存考生信息

- **URL**: `/user/student/info`
- **Method**: POST
- **Headers**: `Authorization: Bearer {token}`
- **请求参数**:

```json
{
  "name": "张三",
  "idCard": "530102201001011234",
  "examId": "2026010001",
  "city": "昆明市",
  "district": "五华区",
  "school": "昆明市第五中学",
  "totalScore": 650,
  "rank": 2000
}
```

## 学校模块

### 1. 获取学校列表

- **URL**: `/school/list`
- **Method**: GET
- **查询参数**:
  - `name`: 学校名称（可选）
  - `city`: 所在州市（可选）
  - `type`: 学校类型（可选）
  - `page`: 页码（默认1）
  - `size`: 每页数量（默认10）

- **响应示例**:

```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "云南省第一中学",
        "code": "YN00001",
        "type": 2,
        "city": "昆明市",
        "district": "五华区",
        "address": "昆明市五华区一二一大街",
        "contact": "0871-65123456",
        "intro": "云南省重点中学，历史悠久，师资力量雄厚",
        "features": "省级重点,百年名校,师资优秀",
        "logo": ""
      }
    ],
    "total": 3,
    "page": 1,
    "size": 10
  }
}
```

### 2. 获取学校详情

- **URL**: `/school/{id}`
- **Method**: GET

### 3. 获取学校录取数据

- **URL**: `/school/{id}/admission`
- **Method**: GET

### 4. 学校对比

- **URL**: `/school/compare`
- **Method**: POST
- **请求参数**:

```json
[1, 2, 3]
```

## AI模块

### 1. 录取概率预测

- **URL**: `/ai/predict`
- **Method**: POST
- **请求参数**:

```json
{
  "totalScore": 650,
  "rank": 2000,
  "city": "昆明市",
  "targetSchoolId": 1
}
```

- **响应示例**:

```json
{
  "success": true,
  "message": "预测成功",
  "data": {
    "admissionProbability": 88.5,
    "confidence": 92.5,
    "analysis": "基于历史数据和AI模型分析，您的分数和排名在目标学校的录取范围内"
  }
}
```

### 2. 智能推荐学校

- **URL**: `/ai/recommend`
- **Method**: POST
- **请求参数**:

```json
{
  "studentData": {
    "totalScore": 650,
    "rank": 2000,
    "city": "昆明市",
    "district": "五华区"
  }
}
```

- **响应示例**:

```json
{
  "success": true,
  "message": "推荐成功",
  "data": {
    "recommendations": [
      {
        "schoolId": 1,
        "schoolName": "云南省第一中学",
        "matchScore": 95.0,
        "admissionProbability": 88.0,
        "reason": "分数和排名均达到录取要求，匹配度极高"
      }
    ],
    "totalCount": 4,
    "analysisSummary": "根据您的分数和排名，为您推荐4所匹配度较高的学校"
  }
}
```

### 3. 政策解读

- **URL**: `/ai/interpret`
- **Method**: POST
- **请求参数**:

```json
{
  "policyContent": "云南省2026年中考招生政策规定..."
}
```

### 4. 分数校准

- **URL**: `/ai/calibrate`
- **Method**: POST
- **请求参数**:

```json
{
  "originalScore": 650,
  "city": "昆明市",
  "year": 2026
}
```

### 5. 健康检查

- **URL**: `/ai/health`
- **Method**: GET

## 政策模块

### 1. 获取政策列表

- **URL**: `/policy/list`
- **Method**: GET
- **查询参数**:
  - `title`: 政策标题（可选）
  - `city`: 适用地区（可选）
  - `page`: 页码（默认1）
  - `size`: 每页数量（默认10）

### 2. 获取政策详情

- **URL**: `/policy/{id}`
- **Method**: GET

### 3. 搜索政策

- **URL**: `/policy/search`
- **Method**: POST
- **请求参数**:

```json
{
  "keyword": "加分政策"
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 测试账号

### 用户账号
- 手机号：13800138000
- 密码：123456
- 角色：考生/家长

### 管理员账号
- 手机号：13800138001
- 密码：123456
- 角色：管理员