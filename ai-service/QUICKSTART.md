# AI 服务平台 - 快速入门指南

## 🚀 快速启动

### 1. 本地开发环境

```bash
# 1. 克隆代码
git clone <repository_url>
cd ai-service

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置必要的参数

# 5. 启动服务
python main.py
```

服务启动后访问: http://localhost:8000

### 2. Docker 部署

```bash
# 构建镜像
docker build -t ai-service .

# 运行容器
docker run -d -p 8000:8000 --env-file .env ai-service
```

### 3. Docker Compose 部署（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

---

## 📁 项目结构

```
ai-service/
├── app/                    # 核心应用
│   ├── api/               # API 路由
│   ├── auth/             # 认证授权
│   ├── core/             # 核心模块
│   ├── services/         # 业务服务
│   └── security/         # 安全模块
├── agents/               # AI 智能体
├── openclaw/             # 爬虫系统
├── routers/              # API 路由
├── tests/                # 测试文件
├── main.py               # 主入口
└── config.py             # 配置
```

---

## 🔧 核心功能

### 🤖 智能对话

```python
# 调用 AI 对话接口
POST /api/v1/chat
{
  "message": "你好",
  "session_id": "xxx"
}
```

### 📚 数据查询

```python
# 获取学校列表
GET /api/v1/schools

# 获取政策列表
GET /api/v1/policies

# 获取文章列表
GET /api/v1/articles
```

### 📊 Dashboard

```python
# 获取系统仪表盘
GET /api/v1/dashboard
```

---

## 🧪 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_api_endpoints.py -v

# 生成覆盖率报告
pytest tests/ --cov=app --cov-report=html
```

---

## 📝 常用命令

| 命令 | 说明 |
|------|------|
| `python main.py` | 启动服务 |
| `pytest tests/` | 运行测试 |
| `python backup_database.py` | 备份数据库 |
| `python cache_warmer.py` | 预热缓存 |

---

## 🔒 安全配置

编辑 `.env` 文件：

```env
# JWT 配置
JWT_SECRET_KEY=your-super-secret-key

# 数据库配置
DATABASE_URL=sqlite:///./app.db

# Redis 配置（可选）
REDIS_URL=redis://localhost:6379/0

# OpenAI API（用于 AI 功能）
OPENAI_API_KEY=sk-your-api-key
```

---

## 🐛 故障排查

### 服务无法启动

```bash
# 检查端口占用
netstat -tlnp | grep 8000

# 检查 Python 环境
python --version
pip list
```

### 数据库错误

```bash
# 重新初始化
rm app.db
python -c "from app.core.database_pool import DatabaseManager; dm = DatabaseManager()"
```

---

## 📚 更多文档

- [完整系统文档](SYSTEM_DOCUMENTATION.md) - 详细的系统架构和模块说明
- [部署指南](DEPLOYMENT_GUIDE.md) - 服务器部署详细步骤
- [API 文档](API_DOCS.md) - API 接口文档

---

**版本**: v1.0.0
**更新日期**: 2026-05-25
