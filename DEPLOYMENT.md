# 小龙虾择校系统 - 生产环境部署清单

## 环境要求

### 后端
- Python 3.9+
- pip 包管理器

### 前端
- Node.js 18+
- npm 或 yarn

## 部署步骤

### 1. 后端部署

```bash
# 进入后端目录
cd ai-service

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp ../.env.production ../.env
# 编辑 .env 文件，填入真实的配置值

# 初始化数据库
python init_db.py

# 启动服务（开发模式）
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080

# 启动服务（生产模式）
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
```

### 2. 前端部署

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview
```

### 3. Nginx 配置（生产环境）

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/aiphxt-app/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket支持（如需要）
    location /ws {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 4. 系统服务（Linux systemd）

创建 `/etc/systemd/system/xiaolongxia-api.service`:

```ini
[Unit]
Description=小龙虾择校API服务
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/aiphxt-app/ai-service
Environment="PATH=/path/to/aiphxt-app/ai-service/venv/bin"
ExecStart=/path/to/aiphxt-app/ai-service/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl daemon-reload
sudo systemctl enable xiaolongxia-api
sudo systemctl start xiaolongxia-api
```

## 数据库备份

```bash
# 手动备份
python backup_db.py

# 查看备份列表
python backup_db.py list

# 恢复备份
python backup_db.py restore backups/schools_backup_xxx.db
```

## 定时任务

设置 crontab 定时备份:
```bash
# 每天凌晨2点备份
0 2 * * * cd /path/to/aiphxt-app/ai-service && python backup_db.py
```

## 健康检查

- 基础检查: `GET /health`
- 详细检查: `GET /health/detailed`
- 就绪检查: `GET /health/ready`

## 日志

- 日志位置: `logs/app.log`
- 日志轮转: 自动按大小轮转
- 日志级别: 通过 .env 文件配置

## 安全配置

1. 修改 `.env` 中的敏感配置:
   - JWT_SECRET_KEY
   - DEEPSEEK_API_KEY
   - SMTP_PASSWORD

2. 配置防火墙:
   - 只开放 80/443 端口
   - 内部服务端口不对外开放

3. 启用 HTTPS:
   - 使用 Let's Encrypt 免费证书
   - 配置 SSL 证书自动续期

## 监控告警

建议配置:
- 服务进程监控
- 端口存活监控
- API响应时间监控
- 数据库大小监控
- 磁盘空间监控
