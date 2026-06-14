# 多阶段构建：构建阶段
FROM python:3.10-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt ./

# 安装依赖到临时目录
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt


# 多阶段构建：运行阶段
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 创建非root用户
RUN useradd --create-home --shell /bin/bash appuser

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖
COPY --from=builder /app/deps ./deps

# 设置Python路径
ENV PYTHONPATH=/app/deps

# 复制代码
COPY --chown=appuser:appuser . .

# 创建必要的目录
RUN mkdir -p /app/data /app/logs && chown appuser:appuser /app/data /app/logs

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 8001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# 启动服务
CMD ["python", "-m", "uvicorn", "app.core.app:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "4"]