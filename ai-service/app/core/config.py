"""核心配置模块"""

import os
from typing import Optional, Dict, Any

try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
        else:
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
            if os.path.exists(env_path):
                load_dotenv(env_path)
except ImportError:
    pass

# 应用配置
APP_NAME = "AI Service"
APP_VERSION = "1.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 服务器配置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8001))

# CORS配置
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", os.getenv("CORS_ORIGINS", "*")).split(",")

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Redis配置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Hermes服务配置
HERMES_URL = os.getenv("HERMES_URL", "http://localhost:8888/v1/agent")

# 安全配置
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# HTTPS配置
HTTPS_ENABLED = os.getenv("HTTPS_ENABLED", "false").lower() == "true"
SSL_CERT_FILE = os.getenv("SSL_CERT_FILE", "certs/server.crt")
SSL_KEY_FILE = os.getenv("SSL_KEY_FILE", "certs/server.key")
SSL_CA_FILE = os.getenv("SSL_CA_FILE", "")
SSL_VERIFY_CLIENT = os.getenv("SSL_VERIFY_CLIENT", "false").lower() == "true"

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", 10485760))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

# DeepSeek API配置
DEEPSEEK_CONFIG = {
    "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
    "base_url": os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1"),
    "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    "max_tokens": int(os.getenv("DEEPSEEK_MAX_TOKENS", "1024")),
    "temperature": float(os.getenv("DEEPSEEK_TEMPERATURE", "0.5")),
    "timeout": int(os.getenv("DEEPSEEK_TIMEOUT", "30"))
}

# 系统提示词
SYSTEM_PROMPT = """你是云南省全域赋能中考择校智能决策平台的AI助手"小龙虾"。你的职责是：

1. 回答用户关于云南省中考政策、学校信息、志愿填报的问题
2. 根据用户的分数、兴趣等信息，推荐合适的学校
3. 帮助用户分析各学校的优势和特点
4. 提供中考备考建议和志愿填报策略
5. 解答各地州的招录政策疑问

请用专业、友好、耐心的态度回答用户的问题。如果涉及具体学校推荐，请尽可能详细说明推荐理由。

重要提示：
- 始终保持严谨、准确的信息提供
- 对于不确定的信息，建议用户参考官方渠道
- 尊重用户隐私，不索取个人敏感信息
- 保持积极向上的沟通态度
"""

# AI择校系统提示词
SCHOOL_SELECTION_PROMPT = """你是专业的中考志愿填报顾问。请根据用户提供的信息：
1. 中考分数
2. 所在地区（州市/区县）
3. 兴趣方向（如：理科、文科、艺术、体育等）
4. 家庭经济情况
5. 其他特殊需求

分析并推荐3-5所最适合的学校，包括：
- 学校名称和基本信息
- 历年录取分数线参考
- 学校特色和优势
- 录取概率评估
- 志愿填报建议

请用表格形式清晰展示推荐结果。"""

# 高中衔接课程提示词
TRANSITION_PROMPT = """你是高中学习规划专家。请根据学生的初中学习情况和目标高中，提供：
1. 高中课程特点介绍
2. 各学科学习方法建议
3. 暑假预习计划
4. 高中生活适应指南
5. 学习心态调整建议

请提供具体、可操作的建议，帮助学生顺利完成从初中到高中的过渡。"""

# 数据配置
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 学校数据文件
SCHOOLS_DATA_FILE = os.path.join(DATA_DIR, "schools.json")
POLICIES_DATA_FILE = os.path.join(DATA_DIR, "policies.json")

# Startup validation
if not DEEPSEEK_CONFIG.get("api_key"):
    import warnings
    warnings.warn("DEEPSEEK_API_KEY is not set. AI-powered features may not work.", RuntimeWarning)

if not SECRET_KEY:
    if DEBUG:
        import secrets
        SECRET_KEY = secrets.token_hex(32)
        import warnings
        warnings.warn("SECRET_KEY not set, using random key for development. DO NOT use in production!", RuntimeWarning)
    else:
        raise RuntimeError(
            "SECRET_KEY environment variable is required for JWT token signing. "
            "Please set SECRET_KEY in your .env file or environment."
        )