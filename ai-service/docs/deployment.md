# 部署指南

## 环境要求
- Python 3.8+
- FastAPI
- Uvicorn

## 安装依赖
```bash
pip install -r requirements.txt
```

## 启动服务
```bash
uvicorn app.core.app:app --host 0.0.0.0 --port 8000
```

## 配置说明
复制.env.example为.env并修改配置
