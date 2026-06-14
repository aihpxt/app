# 云南中考择校智能平台 - 系统架构文档

## 1. 系统组件概览

本系统由以下几个核心组件构成，它们之间通过标准化的API接口进行通信：

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端应用 (Frontend)                       │
│              Vue.js 应用 (端口 3001) / 移动端                     │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ HTTP/REST API
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API 网关层 (API Gateway)                    │
│                    FastAPI 应用 (端口 8001)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │  学校路由   │  │  AI路由     │  │ Agent路由   │  │ Chat路由 │ │
│  │ schools.py  │  │   ai.py     │  │ agents.py   │  │ chat.py  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌───────────┐   ┌──────────┐
    │ SQLite   │   │ 智能体层   │   │ 缓存层   │
    │ 数据库    │   │ (Agents)  │   │ (Redis) │
    └──────────┘   └─────┬─────┘   └──────────┘
                        │
            ┌───────────┼───────────┐
            │           │           │
            ▼           ▼           ▼
      ┌──────────┐ ┌──────────┐ ┌──────────┐
      │学校专家  │ │中考政策   │ │择校顾问  │
      │智能体    │ │专家智能体 │ │智能体    │
      └──────────┘ └──────────┘ └──────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   Hermes服务      │
              │   (高级AI能力)    │
              │    端口 8888     │
              └──────────────────┘
```

## 1.1 Hermes服务 - 高级AI能力中心

Hermes是系统中的高级AI能力中心，提供增强的智能服务：

### 1.1.1 核心能力

| 能力 | 说明 | 作用 |
|------|------|------|
| 会话状态管理 | 跟踪用户对话上下文 | 多轮对话支持 |
| 用户画像分析 | 提取用户特征信息 | 个性化服务 |
| 情感分析 | 识别用户情绪状态 | 情感化响应 |
| 意图识别 | 分类用户查询意图 | 精准路由 |
| 洞察生成 | 提供个性化建议 | 智能跟进 |

### 1.1.2 集成方式

```python
# 基础集成
from hermes_enhanced_integration import HermesManager

hermes = HermesManager()
if hermes.is_available():
    emotion = hermes.analyze_emotion("孩子考不上怎么办")
    # {'emotion': '焦虑', 'urgency': '高', ...}
```

### 1.1.3 降级策略

当Hermes服务不可用时，系统自动降级到本地实现：
- 本地情感分析（基于规则）
- 本地意图分类（关键词匹配）
- 基础响应生成

详见: [HERMES_INTEGRATION_GUIDE.md](file:///e:/aiphxt-app/ai-service/HERMES_INTEGRATION_GUIDE.md)

## 2. 数据库设计

### 2.1 学校数据库 (schools)

**文件位置**: `data/wechat_data.db`

```sql
CREATE TABLE schools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,           -- 学校名称
    city TEXT NOT NULL,           -- 所在城市
    district TEXT,                -- 区县
    school_type TEXT,             -- 学校类型（普通高中/重点高中）
    level TEXT,                   -- 学校等级（一级一等/一级二等）
    is_public INTEGER,             -- 是否公办（1=公办，0=民办）
    is_key INTEGER,               -- 是否重点
    address TEXT,                 -- 地址
    phone TEXT,                   -- 联系电话
    website TEXT,                  -- 官方网站
    description TEXT,              -- 学校简介
    minScore INTEGER,             -- 最低录取分数
    minRank INTEGER,              -- 最低录取排名
    oneRate REAL,                 -- 一本上线率
    boarding INTEGER,             -- 是否提供住宿
    tuition INTEGER,              -- 学费标准
    prefecture TEXT,              -- 所属州市
    level_detail TEXT,            -- 等级详情
    features TEXT,                -- 办学特色
    created_at TEXT,              -- 创建时间
    updated_at TEXT               -- 更新时间
);
```

### 2.2 对话历史数据库 (chat_messages)

**文件位置**: `data/school_platform.db`

```sql
-- 新表结构（推荐）
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,     -- 会话ID
    role TEXT NOT NULL,           -- 角色（user/assistant）
    content TEXT NOT NULL,        -- 消息内容
    created_at TEXT NOT NULL      -- 创建时间
);

-- 索引
CREATE INDEX idx_session_id ON chat_messages(session_id);
CREATE INDEX idx_created_at ON chat_messages(created_at);
```

### 2.3 用户反馈数据库

```sql
CREATE TABLE user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER,
    school_name TEXT,
    feedback_type TEXT,           -- 反馈类型
    feedback_content TEXT,        -- 反馈内容
    contact_info TEXT,            -- 联系方式
    status TEXT DEFAULT 'pending',-- 处理状态
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (school_id) REFERENCES schools(id)
);
```

### 2.4 更新日志数据库

```sql
CREATE TABLE update_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    update_type TEXT,             -- 更新类型
    school_count INTEGER,         -- 学校数量
    success_count INTEGER,        -- 成功数量
    failure_count INTEGER,        -- 失败数量
    details TEXT,                 -- 详细信息
    created_at TEXT
);
```

## 3. 核心组件详解

### 3.1 对话助手路由 (AI Routes)

**文件**: `app/api/routes/ai.py`

**核心功能**:
- `/api/v1/chat` - AI对话接口
- `/api/v1/compare/schools` - 学校对比接口

**数据流程**:
```
1. 接收用户消息
   ↓
2. 获取/生成 session_id
   ↓
3. 从数据库加载会话历史
   ↓
4. 调用上下文生成函数
   ↓
5. 保存用户消息到数据库
   ↓
6. 生成AI响应
   ↓
7. 保存AI响应到数据库
   ↓
8. 返回响应给前端
```

### 3.2 智能体编排器 (Agent Orchestrator)

**文件**: `agents/agent_orchestrator.py`

**核心职责**:
- 智能体生命周期管理
- 任务分派和路由
- 上下文管理
- 响应聚合

**关键方法**:
```python
def dispatch_task(agent_id, user_input, context):
    """分派任务到指定智能体"""

def get_agent(agent_id):
    """获取指定智能体实例"""

def get_agents():
    """获取所有注册的智能体"""
```

### 3.3 专家智能体 (Specialist Agents)

**文件**: `agents/specialists.py`

**主要智能体**:

#### 3.3.1 学校信息专家 (SchoolInfoAgent)
- 负责回答学校基本信息查询
- 提供学校详细介绍、联系方式等

#### 3.3.2 中考政策专家 (PolicyAgent)
- 解读云南省中考政策
- 志愿填报指导
- 录取规则说明

#### 3.3.3 择校顾问 (ControlCenterSpecialistAgent)
- 核心对话智能体
- 指代词理解
- 上下文保持
- 多轮对话管理
- 智能跟进问题生成

**上下文管理流程**:
```python
# 1. 从数据库加载历史消息
history = load_history_from_db(session_id)

# 2. 提取上下文学校名称
context_school = extract_school_from_history(history)

# 3. 检测指代词
if has_pronoun(user_input):
    # 使用 context_school 解析指代词
    response = handle_pronoun_reference(context_school, user_input)

# 4. 保存会话状态到缓存
save_session_to_cache(session_id, topic, conversation_history)
```

### 3.4 Hermes服务 (高级AI能力)

**文件**: `hermes_server.py`

**端口**: 8888

**核心能力**:

#### 3.4.1 会话状态管理
```python
_conversation_states = {
    "session_id": {
        "turn_count": 0,           # 对话轮次
        "topic_history": [],        # 话题历史
        "current_topic": None,      # 当前话题
        "user_info": {},            # 用户信息
        "sentiment_history": [],    # 情感历史
        "stage": "intro",           # 对话阶段
    }
}
```

#### 3.4.2 意图识别
- 分析用户输入的潜在意图
- 识别关键实体（学校名、分数等）

#### 3.4.3 情感分析
- 检测用户情绪状态
- 调整回复语气和内容

#### 3.4.4 个性化推荐
- 基于用户画像的智能推荐
- 历史行为分析

#### 3.4.5 洞察生成
```python
def generate_insight(session_id, user_input, context):
    """生成对话洞察"""
    return {
        "missing_info": ["分数", "地区"],  # 缺失信息
        "followup_topic": "请告诉我孩子的成绩",  # 跟进话题
        "emotion": "期待",              # 检测到的情感
        "urgency": "中"                 # 紧迫程度
    }
```

## 4. 数据流与调用关系

### 4.1 完整对话流程

```
┌──────────────┐
│   用户输入    │
│ "它的分数线   │
│  是多少"     │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│           API路由层 (ai.py)                   │
│  1. 获取 session_id                           │
│  2. 查询会话历史 from chat_messages           │
└────────────────────┬─────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│       上下文生成 (generate_response)          │
│  1. 提取历史学校名称                          │
│  2. 检测指代词 "它"                          │
│  3. 解析为 "师大附中"                         │
└────────────────────┬─────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│      智能体层 (ControlCenterSpecialistAgent)   │
│  1. 基于上下文生成响应                        │
│  2. 添加智能跟进问题                          │
│  3. 保存会话状态到Redis缓存                   │
└────────────────────┬─────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│       Hermes服务 (可选，增强模式)              │
│  1. 情感分析                                 │
│  2. 意图识别                                 │
│  3. 个性化增强                               │
└────────────────────┬─────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│           API路由层 (ai.py)                   │
│  1. 保存助手响应 to chat_messages             │
│  2. 返回响应给前端                           │
└──────────────────────────────────────────────┘
```

### 4.2 学校查询流程

```
┌──────────────┐
│   用户查询    │
│ "师大附中    │
│  的分数线"   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│           API路由层 (schools.py)              │
└────────────────────┬─────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│           学校数据库 (SQLite)                 │
│  SELECT * FROM schools WHERE name LIKE '%师大附中%' │
└────────────────────┬─────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────┐
│           返回学校详细信息                     │
│  minScore, minRank, oneRate 等              │
└──────────────────────────────────────────────┘
```

## 5. 缓存策略

### 5.1 Redis缓存使用

**会话状态缓存**:
```python
key: f"session:{session_id}"
value: {
    "topic": "昆明学校",
    "conversation_history": [...],
    "last_question": "...",
    "last_answer": "...",
    "timestamp": 1234567890
}
TTL: 7200秒 (2小时)
```

**会话统计缓存**:
```python
key: "sessions:stats"
value: {
    "total_count": 100,
    "active_count": 10,
    "topic_distribution": {...}
}
```

### 5.2 缓存更新策略

1. **写入时更新**: 每次对话后更新缓存
2. **读取时检查**: 查询前检查缓存是否存在
3. **定期清理**: 自动清理过期会话（10分钟间隔）
4. **持久化**: 会话状态定期保存到磁盘

## 6. 优化建议

### 6.1 当前架构问题

#### 问题1: 数据库表结构不统一
- `chat_messages` 表存在新旧两种结构
- 需要兼容处理增加代码复杂度

#### 问题2: 缓存与数据库不同步
- 会话状态同时存在于Redis和SQLite
- 可能出现数据不一致

#### 问题3: Hermes服务依赖
- 系统依赖Hermes服务的可用性
- 需要优雅的降级策略

#### 问题4: 指代词处理逻辑复杂
- 多个条件分支容易出错
- 难以维护和扩展

### 6.2 优化方案

#### 方案1: 统一数据库表结构
```sql
-- 迁移到统一的新结构
ALTER TABLE chat_messages ADD COLUMN role TEXT;
ALTER TABLE chat_messages ADD COLUMN message_type TEXT DEFAULT 'text';
```

#### 方案2: 引入消息队列
```
用户消息 → API → 消息队列 → 异步处理 → 智能体 → 响应
```

#### 方案3: 完善降级策略
```python
def get_response(user_input, context):
    try:
        # 1. 尝试使用智能体
        response = agent.handle(user_input, context)
    except AgentException:
        # 2. 降级到规则引擎
        response = rule_engine.handle(user_input, context)
    except LLMException:
        # 3. 最后降级到FAQ匹配
        response = faq_matcher.match(user_input)
```

#### 方案4: 简化指代词处理
```python
# 使用统一的指代词解析服务
class PronounResolver:
    def resolve(self, user_input, history):
        # 1. 提取指代词
        pronouns = self.extract_pronouns(user_input)
        # 2. 从历史中查找实体
        entity = self.find_entity(pronouns, history)
        # 3. 替换指代词
        return self.replace_pronouns(user_input, entity)
```

## 7. 未来扩展方向

### 7.1 微服务架构
- 将各组件拆分为独立微服务
- 使用Kubernetes进行容器编排
- 引入API网关（Kong/Nginx）

### 7.2 机器学习模型
- 训练自定义意图识别模型
- 开发知识图谱增强检索
- 引入推荐系统算法

### 7.3 数据分析平台
- 用户行为分析
- 对话质量评估
- 热点问题统计

### 7.4 多渠道接入
- 微信公众号集成
- 小程序支持
- 电话机器人接口

## 8. 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                        负载均衡器                           │
│                      (Nginx/云LB)                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
  ┌──────────┐     ┌──────────┐      ┌──────────┐
  │ API实例1 │     │ API实例2 │      │ API实例3 │
  │ (8001)   │     │ (8001)   │      │ (8001)   │
  └────┬─────┘     └────┬─────┘      └────┬─────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
                         ▼
                 ┌───────────────┐
                 │    Redis      │
                 │   集群        │
                 └───────┬───────┘
                         │
                         ▼
                 ┌───────────────┐
                 │   SQLite     │
                 │  主数据库    │
                 └───────────────┘
```

## 9. 监控与运维

### 9.1 关键指标
- API响应时间 (P50/P95/P99)
- 对话成功率
- 缓存命中率
- 错误率分布

### 9.2 日志体系
- 结构化日志 (JSON格式)
- 请求追踪 (Trace ID)
- 错误聚合分析

### 9.3 告警策略
- 错误率 > 1% 触发告警
- 响应时间 > 3s 触发告警
- 缓存命中率 < 80% 触发告警

## 10. 总结

本系统采用分层架构设计，核心组件包括：

1. **数据层**: SQLite数据库存储学校信息和对话历史
2. **缓存层**: Redis提供高性能会话状态管理
3. **智能体层**: 专家智能体处理不同类型的用户查询
4. **增强层**: Hermes服务提供高级AI能力
5. **接口层**: FastAPI提供标准化REST API

各组件通过定义良好的接口进行通信，确保系统的可扩展性和可维护性。
