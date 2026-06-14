# API文档

## 接口列表

### 健康检查
GET /api/health

### 聊天接口
POST /api/v1/agent/chat
参数:
- message: 消息内容
- agent_id: 代理ID
- session_id: 会话ID

## 响应格式
```json
{
    "response": "回复内容",
    "status": "success",
    "session_id": "会话ID"
}
```
