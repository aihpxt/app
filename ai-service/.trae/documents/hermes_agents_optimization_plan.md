# Hermes、智能体与AI服务系统性优化重构计划

## 1. 现状分析

### 1.1 项目结构概览

```
ai-service/
├── agents/                    # 智能体层
│   ├── agent_orchestrator.py  # 智能体编排器
│   ├── specialists.py         # 专家智能体（核心对话逻辑）
│   ├── pronoun_resolver.py    # 指代词解析器
│   └── control_center.py      # 控制中心
├── app/
│   ├── api/routes/            # API路由层
│   │   ├── ai.py              # AI聊天接口
│   │   └── agents.py          # 智能体接口
│   ├── core/                  # 核心模块
│   └── utils/                 # 工具模块
├── hermes_server.py           # Hermes服务主文件
├── hermes_enhanced_integration.py  # Hermes集成模块
└── hermes_decorators.py       # Hermes装饰器
```

### 1.2 当前问题识别

| 问题类别 | 问题描述 | 影响范围 | 优先级 |
|---------|---------|---------|--------|
| **架构设计** | 智能体层与路由层耦合度高 | 整体系统 | 高 |
| **代码重复** | 数据库操作逻辑重复 | `ai.py`, `agents.py`, `specialists.py` | 高 |
| **可维护性** | `specialists.py` 文件过大（>1500行） | 智能体开发 | 高 |
| **扩展性** | 缺少统一的智能体注册机制 | 新增智能体 | 中 |
| **错误处理** | 异常处理不一致 | 全局 | 中 |
| **测试覆盖** | 缺少系统化测试 | 全局 | 中 |
| **文档缺失** | 架构文档不完整 | 维护人员 | 低 |

### 1.3 技术债务评估

```
┌─────────────────────────────────────────────────────────────┐
│                      技术债务分析                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🔴 高优先级:                                                │
│     ├── specialists.py 代码行数超限 (>1500行)                 │
│     ├── 指代词处理逻辑分散                                   │
│     ├── 数据库操作重复                                       │
│                                                             │
│  🟡 中优先级:                                                │
│     ├── 缺少统一的智能体管理                                 │
│     ├── 异常处理不统一                                       │
│     ├── 配置管理混乱                                         │
│                                                             │
│  🟢 低优先级:                                                │
│     ├── 文档不完整                                           │
│     ├── 测试覆盖率不足                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 重构目标

### 2.1 架构目标

| 目标 | 描述 | 衡量标准 |
|------|------|---------|
| **低耦合** | 智能体层与路由层解耦 | 通过接口交互 |
| **高内聚** | 单一职责原则 | 每个模块职责明确 |
| **可扩展** | 支持动态添加智能体 | 注册机制 |
| **可测试** | 易于单元测试 | 依赖注入 |
| **可维护** | 代码结构清晰 | 文件大小<500行 |

### 2.2 功能目标

1. **Hermes集成优化**: 统一Hermes调用接口，支持多级别增强
2. **智能体架构重构**: 建立智能体注册、调度、生命周期管理机制
3. **对话助手优化**: 统一上下文管理、消息处理流程
4. **数据库访问层**: 统一数据访问接口，消除重复代码

---

## 3. 重构方案

### 3.1 架构优化

#### 3.1.1 四层架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway层                         │
│           (FastAPI路由 - ai.py, agents.py)                  │
├─────────────────────────────────────────────────────────────┤
│                      服务层 (Service Layer)                  │
│         ┌─────────────┐  ┌──────────────────┐              │
│         │ ChatService │  │ AgentService     │              │
│         │ (对话管理)   │  │ (智能体调度)      │              │
│         └─────────────┘  └──────────────────┘              │
├─────────────────────────────────────────────────────────────┤
│                      智能体层 (Agent Layer)                  │
│         ┌─────────────┐  ┌──────────────────┐              │
│         │ AgentPool   │  │ AgentOrchestrator│              │
│         │ (智能体池)   │  │ (智能体编排)      │              │
│         └─────────────┘  └──────────────────┘              │
├─────────────────────────────────────────────────────────────┤
│                      数据访问层 (DAL)                        │
│            ┌──────────────────────────────┐                 │
│            │ UnifiedDatabaseManager       │                 │
│            │ (统一数据库访问)              │                 │
│            └──────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

#### 3.1.2 组件职责划分

| 组件 | 职责 | 文件位置 |
|------|------|---------|
| **API层** | 接收请求、参数校验、返回响应 | `app/api/routes/` |
| **Service层** | 业务逻辑编排、事务管理 | `app/services/` (新建) |
| **Agent层** | 智能体注册、调度、执行 | `agents/` |
| **DAL层** | 数据库操作封装 | `app/utils/unified_data_access.py` |
| **Hermes层** | 高级AI能力增强 | `hermes_enhanced_integration.py` |

### 3.2 智能体架构重构

#### 3.2.1 智能体注册机制

```python
# 新建: agents/registry.py
class AgentRegistry:
    """智能体注册中心"""
    
    def __init__(self):
        self._agents = {}
    
    def register(self, agent_id: str, agent_class, **kwargs):
        """注册智能体"""
        self._agents[agent_id] = {
            'class': agent_class,
            'instance': None,
            'kwargs': kwargs,
            'metadata': {}
        }
    
    def get_agent(self, agent_id: str):
        """获取智能体实例（懒加载）"""
        if agent_id not in self._agents:
            raise AgentNotFoundError(f"Agent {agent_id} not found")
        
        entry = self._agents[agent_id]
        if entry['instance'] is None:
            entry['instance'] = entry['class'](**entry['kwargs'])
        return entry['instance']
    
    def list_agents(self):
        """列出所有注册的智能体"""
        return list(self._agents.keys())
```

#### 3.2.2 智能体基类定义

```python
# 新建: agents/base_agent.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """智能体基类"""
    
    agent_id: str = None
    agent_name: str = None
    description: str = None
    
    @abstractmethod
    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """处理用户输入"""
        pass
    
    def can_handle(self, user_input: str) -> float:
        """判断是否能处理该请求（返回置信度）"""
        return 0.0
    
    def get_supported_intents(self) -> list:
        """获取支持的意图列表"""
        return []
```

### 3.3 对话服务重构

#### 3.3.1 统一对话服务

```python
# 新建: app/services/chat_service.py
class ChatService:
    """统一对话服务"""
    
    def __init__(self):
        self._agent_registry = AgentRegistry()
        self._hermes = HermesManager()
        self._db_manager = UnifiedDatabaseManager()
    
    async def process_message(self, session_id: str, user_input: str) -> dict:
        """处理用户消息（完整流程）"""
        # 1. 加载会话历史
        history = self._db_manager.get_conversation_history(session_id)
        
        # 2. 意图识别（通过Hermes）
        intent = self._hermes.classify_intent(user_input)
        
        # 3. 智能体分派
        agent = self._agent_registry.get_agent(intent.get('agent_id', 'default'))
        
        # 4. 构建上下文
        context = {
            'session_id': session_id,
            'history': history,
            'intent': intent,
            'user_profile': {}
        }
        
        # 5. 智能体处理
        response = agent.handle(user_input, context)
        
        # 6. Hermes增强
        enhanced_response, _ = self._hermes.enhance(
            session_id, user_input, response, context
        )
        
        # 7. 保存消息
        self._db_manager.save_message(session_id, 'user', user_input)
        self._db_manager.save_message(session_id, 'assistant', enhanced_response)
        
        return {
            'success': True,
            'content': enhanced_response,
            'session_id': session_id
        }
```

### 3.4 数据库访问层优化

#### 3.4.1 统一数据访问接口

**文件**: `app/utils/unified_data_access.py` (已有，需完善)

| 方法 | 功能 | 状态 |
|------|------|------|
| `save_message()` | 保存消息 | ✅ |
| `get_conversation_history()` | 获取会话历史 | ✅ |
| `get_school_by_name()` | 查询学校 | ✅ |
| `search_schools()` | 搜索学校 | ✅ |
| `save_feedback()` | 保存反馈 | ✅ |
| `get_conversation_stats()` | 获取统计 | ✅ |

### 3.5 Hermes集成优化

#### 3.5.1 统一调用接口

**文件**: `hermes_enhanced_integration.py` (已有)

| 增强级别 | 功能 | 适用场景 |
|---------|------|---------|
| `NONE` | 无增强 | 测试/调试 |
| `BASIC` | 情感分析 | 基础响应 |
| `STANDARD` | 情感+意图+会话 | 生产环境 |
| `FULL` | 所有功能 | 高级个性化 |

---

## 4. 实施计划

### 4.1 第一阶段：架构基础搭建（1-2周）

| 任务 | 描述 | 负责人 | 预计时间 |
|------|------|--------|---------|
| T1.1 | 创建智能体基类 `base_agent.py` | 开发 | 1天 |
| T1.2 | 创建智能体注册中心 `registry.py` | 开发 | 1天 |
| T1.3 | 创建统一对话服务 `chat_service.py` | 开发 | 2天 |
| T1.4 | 完善统一数据访问层 | 开发 | 2天 |

### 4.2 第二阶段：智能体重构（2-3周）

| 任务 | 描述 | 负责人 | 预计时间 |
|------|------|--------|---------|
| T2.1 | 拆分 `specialists.py` 为多个模块 | 开发 | 3天 |
| T2.2 | 实现专家智能体继承 `BaseAgent` | 开发 | 2天 |
| T2.3 | 注册现有智能体到注册中心 | 开发 | 1天 |
| T2.4 | 测试智能体调度功能 | 测试 | 2天 |

### 4.3 第三阶段：路由层重构（1周）

| 任务 | 描述 | 负责人 | 预计时间 |
|------|------|--------|---------|
| T3.1 | 简化 `ai.py`，调用 `ChatService` | 开发 | 2天 |
| T3.2 | 简化 `agents.py`，调用 `AgentService` | 开发 | 2天 |
| T3.3 | 测试API接口 | 测试 | 2天 |

### 4.4 第四阶段：Hermes深度集成（1周）

| 任务 | 描述 | 负责人 | 预计时间 |
|------|------|--------|---------|
| T4.1 | 集成Hermes到对话服务 | 开发 | 2天 |
| T4.2 | 实现情感自适应响应 | 开发 | 2天 |
| T4.3 | 测试增强功能 | 测试 | 2天 |

### 4.5 第五阶段：测试与文档（1周）

| 任务 | 描述 | 负责人 | 预计时间 |
|------|------|--------|---------|
| T5.1 | 编写单元测试 | 开发 | 3天 |
| T5.2 | 更新架构文档 | 文档 | 2天 |
| T5.3 | 性能测试 | 测试 | 2天 |

---

## 5. 文件修改清单

### 5.1 新建文件

| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `agents/base_agent.py` | 智能体基类 | 新建 |
| `agents/registry.py` | 智能体注册中心 | 新建 |
| `agents/intent_dispatcher.py` | 意图分派器 | 新建 |
| `app/services/chat_service.py` | 对话服务 | 新建 |
| `app/services/agent_service.py` | 智能体服务 | 新建 |
| `tests/test_chat_service.py` | 对话服务测试 | 新建 |
| `tests/test_agent_registry.py` | 注册中心测试 | 新建 |

### 5.2 修改文件

| 文件路径 | 修改内容 | 优先级 |
|---------|---------|--------|
| `agents/specialists.py` | 拆分模块，继承 `BaseAgent` | 高 |
| `agents/agent_orchestrator.py` | 使用注册中心 | 高 |
| `app/api/routes/ai.py` | 调用 `ChatService` | 高 |
| `app/api/routes/agents.py` | 调用 `AgentService` | 高 |
| `app/utils/db.py` | 标记为废弃 | 中 |

### 5.3 删除文件

| 文件路径 | 原因 |
|---------|------|
| `hermes_decorators.py` | 功能整合到 `ChatService` |

---

## 6. 风险评估

### 6.1 高风险项

| 风险 | 描述 | 影响 | 缓解措施 |
|------|------|------|---------|
| R1 | `specialists.py` 拆分复杂 | 功能回归 | 编写测试用例 |
| R2 | 智能体接口变更 | 现有调用失效 | 渐进式迁移 |
| R3 | Hermes服务依赖 | 服务不可用 | 降级策略 |

### 6.2 风险缓解策略

1. **R1 - 拆分风险**:
   - 先编写单元测试覆盖核心功能
   - 逐步拆分，保持接口兼容
   - 分阶段部署

2. **R2 - 接口变更**:
   - 保持旧接口兼容（标记为deprecated）
   - 提供迁移指南
   - 双版本并行运行

3. **R3 - 服务依赖**:
   - 使用断路器模式
   - 实现本地降级
   - 健康检查机制

---

## 7. 测试计划

### 7.1 单元测试

| 模块 | 测试内容 | 覆盖率目标 |
|------|---------|-----------|
| `AgentRegistry` | 注册、获取、列表 | 100% |
| `ChatService` | 消息处理流程 | 80% |
| `UnifiedDatabaseManager` | CRUD操作 | 100% |
| `HermesIntegration` | 增强功能 | 80% |

### 7.2 集成测试

| 场景 | 测试内容 |
|------|---------|
| 完整对话流程 | 用户输入 → 智能体处理 → 响应返回 |
| 上下文保持 | 多轮对话、指代词解析 |
| Hermes降级 | 服务不可用时的降级行为 |
| 智能体分派 | 基于意图的智能体选择 |

### 7.3 性能测试

| 指标 | 目标 |
|------|------|
| API响应时间 | P50 < 200ms, P95 < 500ms |
| 并发处理 | 100请求/秒 |
| 数据库查询 | < 50ms |

---

## 8. 部署计划

### 8.1 部署策略

采用蓝绿部署策略：

1. **蓝环境**: 当前生产版本
2. **绿环境**: 重构后版本

### 8.2 回滚方案

```bash
# 回滚命令
git revert <commit-hash>
docker-compose down && docker-compose up -d
```

### 8.3 监控指标

| 指标 | 告警阈值 |
|------|---------|
| 错误率 | > 1% |
| 响应时间 | P95 > 1s |
| 服务可用性 | < 99% |

---

## 9. 成功标准

### 9.1 功能验证

- ✅ 智能体注册机制正常工作
- ✅ 对话流程完整可用
- ✅ Hermes增强功能正常
- ✅ 上下文保持测试通过

### 9.2 代码质量

- ✅ 文件大小 < 500行
- ✅ 测试覆盖率 > 80%
- ✅ 无重复代码
- ✅ 符合PEP8规范

### 9.3 性能指标

- ✅ API响应时间 P50 < 200ms
- ✅ 并发处理能力 100 req/s
- ✅ 错误率 < 0.1%

---

## 10. 附录

### 10.1 参考文档

- [ARCHITECTURE_OVERVIEW.md](file:///e:/aiphxt-app/ai-service/ARCHITECTURE_OVERVIEW.md)
- [HERMES_INTEGRATION_GUIDE.md](file:///e:/aiphxt-app/ai-service/HERMES_INTEGRATION_GUIDE.md)
- [DATA_FLOW_GUIDE.md](file:///e:/aiphxt-app/ai-service/DATA_FLOW_GUIDE.md)

### 10.2 代码参考

| 文件 | 路径 |
|------|------|
| 当前智能体实现 | [agents/specialists.py](file:///e:/aiphxt-app/ai-service/agents/specialists.py) |
| 当前AI路由 | [app/api/routes/ai.py](file:///e:/aiphxt-app/ai-service/app/api/routes/ai.py) |
| Hermes集成 | [hermes_enhanced_integration.py](file:///e:/aiphxt-app/ai-service/hermes_enhanced_integration.py) |
| 统一数据访问 | [app/utils/unified_data_access.py](file:///e:/aiphxt-app/ai-service/app/utils/unified_data_access.py) |

---

**计划版本**: v1.0  
**创建日期**: 2026-05-23  
**预计完成**: 6-8周