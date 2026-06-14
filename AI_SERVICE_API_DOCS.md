# AI中考择校顾问系统 - API文档

## 概述

AI中考择校顾问系统是一个基于FastAPI的智能对话系统，为家长和学生提供云南省各高中录取分数线分析、学校推荐与对比、政策咨询等服务。

## 基础信息

- **API地址**: `http://localhost:8001`
- **API版本**: v1
- **基础路径**: `/api/v1`

## 认证方式

当前版本无需认证，直接使用。

---

## 核心API

### 1. 智能体对话接口

与AI择校顾问进行对话。

**请求**
```http
POST /api/v1/agent/chat
Content-Type: application/json

{
    "message": "师大附中怎么样",
    "agent_id": "zk-master",
    "session_id": "可选的会话ID"
}
```

**参数说明**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | ✅ | 用户输入的问题或消息 |
| agent_id | string | ✅ | 智能体ID，固定为 `zk-master` |
| session_id | string | ❌ | 会话ID，不提供则自动生成 |

**响应**
```json
{
    "success": true,
    "response": "🏫 云南师范大学附属中学（师大附中）\n\n【学校简介】\n...",
    "session_id": "7af4e374f675b9fb05164257c3a37793",
    "data": {
        "agent_id": "zk-master",
        "agent_name": "中考择校顾问",
        "response": "...",
        "skills_used": [],
        "skill_results": {},
        "input_analysis": {...},
        "processing_time": 0.234,
        "timestamp": "2025-05-19T10:30:00"
    }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| response | string | AI顾问的回复文本 |
| session_id | string | 会话ID，用于上下文关联 |
| data.agent_id | string | 智能体ID |
| data.agent_name | string | 智能体名称 |
| data.processing_time | float | 处理时间（秒） |
| data.timestamp | string | 响应时间戳 |

---

## 支持的功能

### 1. 学校信息查询

**示例问题**
- "师大附中怎么样"
- "昆一中录取分数线是多少"
- "昆明有哪些好高中"

**返回内容**
- 学校简介、办学优势、录取分数线、联系方式等

### 2. 分数推荐学校

**示例问题**
- "680分能上什么学校"
- "我孩子考了650分，推荐一下"
- "多少分能上昆一中"

**返回内容**
- 根据分数推荐的学校列表及录取建议

### 3. 学校对比

**示例问题**
- "昆一中和昆三中哪个好"
- "师大附中和云大附中对比"
- "对比一下这几所学校"

**返回内容**
- 两所学校的详细对比信息表

### 4. 中考政策咨询

**示例问题**
- "中考志愿怎么填报"
- "昆明中考政策是什么"
- "定向生是什么意思"

**返回内容**
- 云南省/昆明市中考政策要点

### 5. 学费及费用咨询

**示例问题**
- "重点高中学费多少"
- "昆一中年费多少"
- "民办高中学费贵吗"

**返回内容**
- 公办/民办高中收费标准参考

### 6. 地区学校查询

**示例问题**
- "文山有哪些好高中"
- "丘北未央中学怎么样"
- "昆明重点高中有哪些"

**返回内容**
- 指定地区的优质学校推荐

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 智能体不存在 |
| 500 | 服务器内部错误 |

---

## 使用示例

### Python示例

```python
import requests

url = "http://localhost:8001/api/v1/agent/chat"
payload = {
    "message": "680分推荐学校",
    "agent_id": "zk-master"
}

response = requests.post(url, json=payload)
data = response.json()

print(data.get("response"))
```

### JavaScript示例

```javascript
const response = await fetch("http://localhost:8001/api/v1/agent/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
        message: "师大附中怎么样",
        agent_id: "zk-master"
    })
});

const data = await response.json();
console.log(data.response);
```

---

## 会话管理

系统使用session_id来维护对话上下文。建议：

1. **首次对话**：不提供session_id，系统会自动生成
2. **后续对话**：使用首次返回的session_id，以保持上下文连贯

### 示例流程

```python
# 第一次请求
r1 = requests.post(url, json={"message": "你好", "agent_id": "zk-master"})
session_id = r1.json().get("session_id")

# 第二次请求（带session_id）
r2 = requests.post(url, json={
    "message": "学费多少",
    "agent_id": "zk-master",
    "session_id": session_id  # 保持上下文
})
```

---

## 限制与注意事项

1. **输入长度**：建议单条消息不超过500字
2. **并发限制**：单节点支持约1000并发
3. **响应时间**：P95响应时间 < 500ms
4. **数据更新**：学校信息和政策可能需要定期更新

---

## 联系方式

如有问题或建议，请联系开发团队。
