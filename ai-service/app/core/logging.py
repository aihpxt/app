"""日志配置模块"""

import logging
import os
from logging.handlers import RotatingFileHandler
from app.core.config import LOG_LEVEL, LOG_FILE, LOG_MAX_SIZE, LOG_BACKUP_COUNT

# 创建日志目录
log_dir = os.path.dirname(LOG_FILE)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# 配置日志格式
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 创建文件处理器
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=LOG_MAX_SIZE,
    backupCount=LOG_BACKUP_COUNT
)
file_handler.setFormatter(log_format)
file_handler.setLevel(getattr(logging, LOG_LEVEL))

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
console_handler.setLevel(logging.INFO)

# 配置根日志器
root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, LOG_LEVEL))
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# 配置第三方库日志
logging.getLogger('uvicorn').setLevel(logging.WARNING)
logging.getLogger('fastapi').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.ERROR)  # 减少 asyncio 的错误日志，特别是 ConnectionResetError

print(f"日志配置完成，日志级别: {LOG_LEVEL}, 日志文件: {LOG_FILE}")
