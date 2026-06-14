import logging
import os
from datetime import datetime

# 日志目录
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 日志文件名
log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')

def setup_logger(name, log_file, level=logging.INFO):
    """设置日志记录器"""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 应用日志记录器
app_logger = setup_logger('app', log_file, logging.INFO)

# 错误日志记录器
error_logger = setup_logger('error', os.path.join(log_dir, f'error_{datetime.now().strftime("%Y%m%d")}.log'), logging.ERROR)

# AI服务日志记录器
ai_logger = setup_logger('ai', os.path.join(log_dir, f'ai_{datetime.now().strftime("%Y%m%d")}.log'), logging.INFO)

# 爬虫日志记录器
crawler_logger = setup_logger('crawler', os.path.join(log_dir, f'crawler_{datetime.now().strftime("%Y%m%d")}.log'), logging.INFO)

# 日志记录函数
def log_info(message, logger=app_logger):
    """记录信息日志"""
    logger.info(message)

def log_error(message, logger=error_logger):
    """记录错误日志"""
    logger.error(message)

def log_debug(message, logger=app_logger):
    """记录调试日志"""
    logger.debug(message)

def log_warning(message, logger=app_logger):
    """记录警告日志"""
    logger.warning(message)

def log_access(message, *args, logger=app_logger):
    """记录访问日志"""
    logger.info(f"[ACCESS] {message}", *args)

def monitor(message, logger=app_logger):
    """记录监控日志"""
    logger.info(f"[MONITOR] {message}")

def record_request(process_time, status_code, request_type, logger=app_logger):
    """记录请求信息"""
    logger.info(f"[REQUEST] 处理时间: {process_time:.4f}s, 状态码: {status_code}, 请求类型: {request_type}")

# 为了保持兼容性，创建一个monitor对象
class Monitor:
    def record_request(self, process_time, status_code, request_type):
        record_request(process_time, status_code, request_type)
    
    def update_system_metrics(self, metrics=None):
        """更新系统指标"""
        logger = app_logger
        if metrics:
            logger.info(f"[SYSTEM_METRICS] {metrics}")
        else:
            logger.info("[SYSTEM_METRICS] 系统指标更新")

# 创建全局monitor对象
monitor = Monitor()
