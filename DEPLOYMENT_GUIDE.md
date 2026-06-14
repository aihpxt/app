# AI Service 服务器部署指南

## 📦 部署包信息

- **文件名**: ai-service-deploy-YYYYMMDD-HHMMSS.zip
- **包含内容**: 完整的 AI 服务源代码
- **文件数量**: 263 个文件
- **压缩包大小**: ~7.27 MB

## 🚀 快速部署步骤

### 1. 上传并解压

```bash
# 上传压缩包到服务器
scp ai-service-deploy-YYYYMMDD-HHMMSS.zip user@server:/path/to/deploy/

# SSH登录服务器
ssh user@server

# 进入部署目录
cd /path/to/deploy/

# 解压
unzip ai-service-deploy-YYYYMMDD-HHMMSS.zip
```

### 2. 配置环境变量

```bash
# 进入 ai-service 目录
cd ai-service

# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
nano .env
```

**必需配置项**:
```env
# 数据库配置
DATABASE_URL=sqlite:///./app.db

# Redis配置（可选，用于缓存）
REDIS_URL=redis://localhost:6379/0

# JWT密钥（必须修改为强密钥）
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production

# OpenAI API密钥（用于AI功能）
OPENAI_API_KEY=sk-your-api-key

# 服务端口
PORT=8000
HOST=0.0.0.0
```

### 3. 安装依赖

```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
# 初始化数据库
python -c "from app.core.database_pool import DatabaseManager; dm = DatabaseManager(); print('数据库初始化完成')"
```

### 5. 启动服务

```bash
# 开发模式
python main.py

# 或使用 uvicorn（生产环境推荐）
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📁 部署目录结构

```
ai-service/
├── app/                    # 核心应用代码
│   ├── api/               # API接口
│   ├── core/              # 核心模块
│   ├── models/            # 数据模型
│   └── services/          # 服务层
├── openclaw/              # 爬虫和数据采集
├── routers/               # API路由
├── services/              # 业务服务
├── plugins/               # 插件系统
├── skills/                # 技能模块
├── tools/                 # 工具脚本
├── main.py               # 主入口
├── config.py             # 配置文件
├── requirements.txt      # Python依赖
└── .env                  # 环境变量（需创建）
```

## 🐳 Docker 部署（可选）

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 构建镜像
docker build -t ai-service .

# 运行容器
docker run -d -p 8000:8000 --env-file .env ai-service
```

## 🔒 安全建议

1. **修改默认密钥**: 生产环境务必修改 JWT_SECRET_KEY
2. **配置防火墙**: 只开放 8000 端口
3. **使用HTTPS**: 配置 Nginx 反向代理并启用 SSL
4. **定期备份**: 定期备份数据库和配置文件
5. **日志管理**: 配置日志轮转，避免磁盘空间问题

## 📊 常用命令

```bash
# 查看服务状态
ps aux | grep python

# 重启服务
pkill -f "python main.py"
python main.py &

# 查看日志
tail -f logs/app.log

# 备份数据库
cp app.db app.db.backup.$(date +%Y%m%d)
```

## 🔧 故障排查

### 服务无法启动
```bash
# 检查端口占用
netstat -tlnp | grep 8000

# 检查Python环境
python --version
pip list
```

### 数据库错误
```bash
# 重新初始化
rm app.db
python -c "from app.core.database_pool import DatabaseManager; dm = DatabaseManager()"
```

### 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 安装编译依赖（Ubuntu）
sudo apt-get install python3-dev build-essential

# 重新安装依赖
pip install -r requirements.txt --no-cache-dir
```

## 📞 技术支持

如遇问题，请检查：
1. 环境变量是否正确配置
2. 依赖是否完整安装
3. 端口是否被占用
4. 日志文件中的错误信息

---

**版本**: 1.0.0
**更新时间**: 2026-05-25
