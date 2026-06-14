# Hermes 智能服务集成指南

## 1. Hermes服务概述

### 1.1 什么是Hermes

Hermes是系统中提供高级AI能力的增强服务，类似于一个智能助手大脑，负责：

- **会话状态管理** - 跟踪用户对话的上下文
- **用户画像分析** - 从对话中提取用户信息（年级、地区、分数、偏好）
- **情感分析** - 识别用户的情绪状态（焦虑、期待、困惑等）
- **意图识别** - 分类用户的查询意图
- **洞察生成** - 提供个性化的跟进建议

### 1.2 Hermes在系统中的位置

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户交互层                               │
│                    (Web/移动端应用)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API 路由层                                 │
│              (FastAPI - 端口 8001)                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
      ┌────────────┐  ┌────────────┐  ┌────────────┐
      │ 智能体层    │  │ 缓存层     │  │ 增强层     │
      │ Specialists │  │  Redis    │  │ Hermes    │
      │            │  │           │  │ (端口8888) │
      └─────┬──────┘  └───────────┘  └──────┬─────┘
            │                               │
            │        ◄────── 深度集成 ──────►
            │
            ▼
      ┌────────────┐
      │  SQLite   │
      │  数据库    │
      └────────────┘
```

### 1.3 服务状态

- **运行中**: 端口 8888 可用
- **降级模式**: 本地实现接管，功能受限
- **完全离线**: 仅基础响应，无增强

## 2. 核心能力详解

### 2.1 会话状态管理

```python
class ConversationState:
    session_id: str
    turn_count: int           # 对话轮次
    topic_history: List[str]  # 话题历史
    current_topic: str        # 当前话题
    user_info: Dict           # 用户信息
    sentiment_history: List   # 情感历史
    stage: str                # 对话阶段 (intro/exploration/decision)
```

**示例**:
```python
# 初始状态
{
    "turn_count": 0,
    "topic_history": [],
    "current_topic": None,
    "stage": "intro",
    "sentiment_history": []
}

# 多轮对话后
{
    "turn_count": 5,
    "topic_history": ["昆明学校", "中考政策"],
    "current_topic": "分数推荐",
    "stage": "exploration",
    "sentiment_history": [
        {"emotion": "期待", "urgency": "中"},
        {"emotion": "焦虑", "urgency": "高"}
    ]
}
```

### 2.2 用户画像分析

从对话中自动提取以下信息：

| 字段 | 说明 | 提取关键词 |
|------|------|-----------|
| grade | 年级 | 初三、九年级 |
| location | 地区 | 昆明、文山、丘北 |
| score | 预估分数 | 680分、能考650 |
| budget | 预算 | 便宜、适中、贵 |
| concerns | 关注点 | 升学率、学费、师资 |
| boarding_preference | 住宿偏好 | 住校、走读 |
| education_type_preference | 学校类型 | 公办、民办 |
| special_needs | 特殊需求 | 特长生、民族加分 |

**示例**:
```python
用户: "我是昆明的，初三学生，预估640分，想了解师大附中"
                    │
                    ▼
{
    "grade": "初三",
    "location": "昆明",
    "score": 640,
    "school_preferences": ["师大附中"],
    "concerns": ["录取难度"]
}
```

### 2.3 情感分析

**情感类型**:
- **积极**: 感谢、满意、赞扬
- **期待**: 有明确需求，寻求帮助
- **焦虑**: 担忧、不安、压力
- **困惑**: 不理解、需要澄清
- **消极**: 拒绝、否定、放弃
- **兴奋**: 非常高兴、激动
- **中性**: 平淡陈述

**紧迫程度**:
- 高: 紧急/压力场景
- 中: 正常咨询
- 低: 轻松随意

**示例**:
```python
用户输入: "孩子成绩不好怎么办"
分析结果: {
    "emotion": "焦虑",
    "urgency": "高",
    "sentiment": "焦虑",
    "needs_support": true,
    "confidence": 0.9
}
```

### 2.4 意图识别

**支持的意图类型**:

| 意图 | 说明 | 关键词 |
|------|------|--------|
| school_inquiry | 学校查询 | 学校、高中、分数线 |
| policy_inquiry | 政策咨询 | 政策、中考、志愿 |
| fee_inquiry | 费用咨询 | 学费、费用、收费 |
| school_compare | 学校比较 | 比较、对比、哪个好 |
| score_recommendation | 分数推荐 | 分、推荐、能上 |
| application_inquiry | 报名咨询 | 报名、招生 |
| campus_visit | 预约看校 | 预约、参观、开放日 |
| general_question | 一般咨询 | 其他 |

### 2.5 洞察生成

根据上下文生成个性化建议：

```python
{
    "missing_info": ["考生成绩", "所在地区"],
    "followup_topics": [
        "请问您孩子的中考成绩大概是多少？",
        "您家在哪个城市呢？"
    ],
    "emotion_signal": "期待",
    "urgency": "medium"
}
```

## 3. 集成方式

### 3.1 基础集成（HermesManager）

**文件**: `hermes_enhanced_integration.py`

```python
from hermes_enhanced_integration import HermesManager, EnhancementLevel

# 获取管理器
hermes = HermesManager()

# 检查可用性
if hermes.is_available():
    print("Hermes服务在线")
else:
    print("使用本地降级")

# 情感分析
emotion = hermes.analyze_emotion("孩子考不上怎么办")
# {'emotion': '焦虑', 'urgency': '高', ...}

# 意图分类
intent = hermes.classify_intent("师大附中的分数线是多少")
# {'intent': 'school_inquiry', 'confidence': 0.8}

# 响应增强
enhanced_response, enhancement = hermes.enhance(
    session_id="user123",
    user_input="它的学费是多少",
    base_response="师大附中的学费...",
    context={"context_school": "师大附中"},
    level=EnhancementLevel.STANDARD
)
```

### 3.2 装饰器集成

**文件**: `hermes_decorators.py`

```python
from hermes_decorators import (
    hermes_enhanced,
    track_conversation,
    analyze_and_enhance,
    emotion_adaptive
)

# 方式1：自动增强响应
@hermes_enhanced(level=EnhancementLevel.STANDARD)
def handle_message(session_id, user_input, context):
    return generate_response(user_input, context)

# 方式2：跟踪会话状态
@track_conversation
def process_input(session_id, message, context):
    return generate_response(message, context)

# 方式3：情感自适应
@emotion_adaptive
def generate_response(user_input, context):
    # 自动根据用户情感调整响应
    pass
```

### 3.3 类继承集成

```python
from hermes_decorators import HermesAware

class MyAgent(HermesAware):
    def __init__(self):
        super().__init__()
        # Hermes功能已可用

    def handle(self, session_id, user_input, context):
        # 分析情感
        emotion = self.analyze_emotion(user_input, session_id)

        # 生成响应
        response = self._generate_response(user_input, context)

        # 增强响应
        if self.hermes_available:
            response = self.enhance_response(
                session_id, user_input, response, context
            )

        return response
```

## 4. 增强级别

```python
from hermes_enhanced_integration import EnhancementLevel

# 0级：无增强
EnhancementLevel.NONE

# 1级：基础增强（情感分析）
EnhancementLevel.BASIC

# 2级：标准增强（情感+意图+洞察）
EnhancementLevel.STANDARD

# 3级：完全增强（所有功能）
EnhancementLevel.FULL
```

### 级别对比

| 功能 | NONE | BASIC | STANDARD | FULL |
|------|------|-------|----------|------|
| 情感分析 | - | ✓ | ✓ | ✓ |
| 意图分类 | - | - | ✓ | ✓ |
| 会话跟踪 | - | - | ✓ | ✓ |
| 用户画像 | - | - | ✓ | ✓ |
| 洞察生成 | - | - | - | ✓ |
| 技能推荐 | - | - | - | ✓ |

## 5. 降级策略

当Hermes服务不可用时，系统会自动降级到本地实现：

### 5.1 本地情感分析

```python
# Hermes不可用时的降级实现
{
    "焦虑": ["怎么办", "担心", "考不上"],
    "积极": ["谢谢", "很好", "不错"],
    "期待": ["多少", "推荐", "可以"]
}
```

### 5.2 本地意图分类

```python
# 基于关键词的简单分类
{
    "school_inquiry": ["学校", "高中", "录取", "分数线"],
    "policy_inquiry": ["政策", "中考", "志愿", "填报"],
    "fee_inquiry": ["学费", "费用", "收费"]
}
```

## 6. 使用示例

### 6.1 完整对话流程

```python
from hermes_enhanced_integration import HermesManager, EnhancementLevel

hermes = HermesManager()
session_id = "user_session_123"

# 第一轮：用户询问学校
user_input = "我想了解师大附中"
response = "师大附中是云南省顶尖的重点高中..."

# 情感分析（了解用户心态）
emotion = hermes.analyze_emotion(user_input, session_id)
print(f"用户情感: {emotion['emotion']}")  # 期待

# 意图分类
intent = hermes.classify_intent(user_input)
print(f"用户意图: {intent['intent']}")  # school_inquiry

# 第二轮：用户追问（带情感增强）
user_input2 = "它的分数线是多少"
response2 = "师大附中的录取分数线..."

# 增强响应（添加跟进建议）
enhanced2, _ = hermes.enhance(
    session_id=session_id,
    user_input=user_input2,
    base_response=response2,
    context={"context_school": "师大附中"},
    level=EnhancementLevel.STANDARD
)
print(enhanced2)
# 输出可能包含：
# "师大附中的录取分数线是..."
# "\n\n您可能还想了解："
# "1. 师大附中的学费是多少？"
# "2. 师大附中的师资情况？"
```

### 6.2 焦虑情绪安抚

```python
from hermes_decorators import emotion_adaptive

@emotion_adaptive
def generate_response(user_input, context):
    # 基础响应生成
    response = "根据您孩子的情况，可能需要考虑一些备选方案..."

    # 装饰器自动检测到焦虑情绪
    # 自动添加安慰语："别担心，"
    return response

# 用户输入: "孩子成绩不好，考不上好学校怎么办"
# 输出: "别担心，根据您孩子的情况，可能需要考虑一些备选方案..."
```

### 6.3 会话跟踪

```python
from hermes_decorators import track_conversation

@track_conversation
def chat_handler(session_id, message, context):
    # 自动跟踪会话状态
    # 自动更新用户画像
    return generate_response(message, context)

# 多次调用后，Hermes中的用户画像会自动完善
```

## 7. API端点

### 7.1 健康检查
```
GET /health
Response: {"status": "healthy", "name": "Hermes Agent", "version": "1.0.0"}
```

### 7.2 情感分析
```
POST /v1/analyze
Body: {"data": {"input": "...", "session_id": "...", "analysis_type": "emotion"}}
Response: {"success": true, "data": {"emotion": "期待", "urgency": "中", ...}}
```

### 7.3 意图分类
```
POST /v1/classify
Body: {"data": {"input": "...", "classification_type": "intent"}}
Response: {"success": true, "data": {"intent": "school_inquiry", "confidence": 0.8}}
```

### 7.4 会话跟踪
```
POST /v1/track
Body: {"data": {"session_id": "...", "input": "...", "context": {...}}}
Response: {"success": true, "data": {"turn_count": 3, "stage": "exploration"}}
```

### 7.5 洞察生成
```
POST /v1/insights
Body: {"data": {"session_id": "...", "input": "...", "context": {...}}}
Response: {"success": true, "data": {"missing_info": [...], "followup_topics": [...]}}
```

### 7.6 技能推荐
```
POST /v1/agent
Body: {"data": {"input": "...", "type": "dispatch"}}
Response: {"success": true, "data": {"recommended_skills": ["search", "data-analyzer"]}}
```

### 7.7 反馈提交
```
POST /v1/feedback
Body: {"data": {"session_id": "...", "type": "...", "score": 0.8, "details": {...}}}
Response: {"success": true}
```

## 8. 配置说明

### 8.1 服务地址配置

```python
# 默认配置
hermes = HermesManager(base_url="http://localhost:8888")

# 自定义地址
hermes = HermesManager(base_url="http://hermes-server:8888")
```

### 8.2 超时配置

```python
# 默认超时2秒
hermes = HermesManager(timeout=2.0)

# 调整超时
hermes = HermesManager(timeout=5.0)
```

### 8.3 环境变量

```bash
# .env 文件
HERMES_URL=http://localhost:8888
HERMES_TIMEOUT=2.0
HERMES_ENABLED=true
```

## 9. 监控指标

### 9.1 服务可用性
- `hermes.available`: 服务是否在线
- `hermes.health_check()`: 执行健康检查

### 9.2 请求统计
```python
# 获取Hermes指标
response = requests.get("http://localhost:8888/metrics")
# 返回: {"request_count": 100, "success_rate": 0.95, "avg_latency": 0.5}
```

### 9.3 日志记录
```
2026-05-23 10:30:00 - hermes_integration - INFO - Hermes服务可用
2026-05-23 10:30:01 - hermes_integration - WARNING - Hermes响应超时，使用本地降级
2026-05-23 10:30:05 - hermes_integration - ERROR - Hermes服务连接失败
```

## 10. 故障排查

### 10.1 服务无法连接

**症状**: `Hermes服务不可用`

**排查**:
1. 检查Hermes服务是否启动
   ```bash
   curl http://localhost:8888/health
   ```

2. 检查端口是否被占用
   ```bash
   netstat -ano | findstr :8888
   ```

3. 检查防火墙设置

**解决**:
```bash
# 启动Hermes服务
python hermes_server.py
```

### 10.2 增强功能失效

**症状**: 响应中没有跟进建议或情感调整

**排查**:
1. 检查增强级别设置
2. 查看日志中的增强结果

**解决**:
```python
# 提高增强级别
hermes.enhance(
    ...,
    level=EnhancementLevel.FULL
)
```

### 10.3 本地降级不工作

**症状**: Hermes不可用时响应质量下降

**解决**: 检查本地降级实现是否正确加载

```python
# 强制使用本地实现
from hermes_enhanced_integration import HermesLocalFallback

emotion = HermesLocalFallback.analyze_emotion_local("用户输入")
```

## 11. 性能优化

### 11.1 异步处理
```python
# 使用线程池异步调用
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)

# 异步提交Hermes请求
future = executor.submit(hermes.analyze_emotion, user_input, session_id)
# 继续处理其他逻辑
result = future.result(timeout=2)
```

### 11.2 缓存策略
```python
# 缓存频繁查询的结果
@cache(ttl=300)  # 5分钟缓存
def get_user_profile(session_id):
    return hermes.get_session_report(session_id)
```

### 11.3 批量处理
```python
# 批量提交请求
requests = [
    {"session_id": "s1", "input": "..."},
    {"session_id": "s2", "input": "..."},
    {"session_id": "s3", "input": "..."}
]

# 批量执行
results = executor.map(process_single, requests)
```

## 12. 安全考虑

### 12.1 输入验证
```python
def validate_hermes_input(user_input: str) -> str:
    # 限制输入长度
    max_length = 1000
    if len(user_input) > max_length:
        user_input = user_input[:max_length]

    # 过滤特殊字符
    import re
    user_input = re.sub(r'[<>]', '', user_input)

    return user_input
```

### 12.2 速率限制
```python
# 限制Hermes请求频率
from ratelimit import limits

@limits(calls=100, period=60)
def hermes_request(*args, **kwargs):
    return hermes.analyze_emotion(*args, **kwargs)
```

### 12.3 数据脱敏
```python
def sanitize_for_hermes(data: dict) -> dict:
    # 移除敏感信息
    sensitive_fields = ["password", "token", "secret"]
    for field in sensitive_fields:
        data.pop(field, None)
    return data
```

## 13. 扩展开发

### 13.1 添加新的情感类型
```python
class HermesService:
    def _detect_new_emotion(self, user_input: str) -> dict:
        # 添加新的情感检测逻辑
        if "惊喜" in user_input:
            return {
                "emotion": "惊喜",
                "urgency": "低",
                "sentiment": "开心",
                "confidence": 0.9
            }
        return None
```

### 13.2 自定义意图分类器
```python
class CustomHermesIntegration(HermesIntegration):
    def classify_intent(self, user_input: str) -> Dict:
        # 自定义分类逻辑
        if "住宿" in user_input:
            return {"intent": "boarding_inquiry", "confidence": 0.9}
        return super().classify_intent(user_input)
```

### 13.3 本地降级扩展
```python
class ExtendedFallback(HermesLocalFallback):
    @staticmethod
    def classify_intent_local(user_input: str) -> Dict:
        # 扩展意图分类
        if "师资" in user_input:
            return {"intent": "faculty_inquiry", "confidence": 0.9}
        return HermesLocalFallback.classify_intent_local(user_input)
```

## 14. 版本历史

### v1.0.0 (当前)
- 会话状态管理
- 用户画像分析
- 情感分析（规则+LLM）
- 意图识别
- 洞察生成
- 增强响应

### 未来版本规划
- v1.1: 多轮对话记忆优化
- v1.2: 个性化推荐算法
- v1.3: 实时语音集成
- v2.0: 微服务架构

## 15. 联系方式

如有问题，请联系：
- 技术支持: support@aiphxt.com
- 文档反馈: docs@aiphxt.com
