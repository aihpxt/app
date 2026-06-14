#!/usr/bin/env python3
"""
数据库备份脚本
用于定期备份数据库文件
"""

import os
import sys
import time
import shutil
import logging
import schedule

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(__file__), 'logs', 'backup.log'),
    filemode='a'
)

# 数据库配置
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_FILE = os.path.join(DATA_DIR, 'school_platform.db')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
BACKUP_INTERVAL = 24  # 备份间隔，单位：小时
MAX_BACKUPS = 7  # 最大备份数量

# 创建备份目录
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup_database():
    """备份数据库"""
    try:
        # 检查数据库文件是否存在
        if not os.path.exists(DB_FILE):
            logging.error(f"数据库文件不存在: {DB_FILE}")
            return
        
        # 生成备份文件名
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(BACKUP_DIR, f'school_platform_{timestamp}.db')
        
        # 备份数据库文件
        shutil.copy2(DB_FILE, backup_file)
        logging.info(f"数据库备份成功: {backup_file}")
        
        # 清理过期备份
        clean_old_backups()
    except Exception as e:
        logging.error(f"备份数据库失败: {e}")

def clean_old_backups():
    """清理过期备份"""
    try:
        # 获取所有备份文件
        backups = []
        for file in os.listdir(BACKUP_DIR):
            if file.startswith('school_platform_') and file.endswith('.db'):
                file_path = os.path.join(BACKUP_DIR, file)
                backups.append((file_path, os.path.getmtime(file_path)))
        
        # 按修改时间排序
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # 保留最新的 MAX_BACKUPS 个备份
        if len(backups) > MAX_BACKUPS:
            for backup_file, _ in backups[MAX_BACKUPS:]:
                os.remove(backup_file)
                logging.info(f"清理过期备份: {backup_file}")
    except Exception as e:
        logging.error(f"清理过期备份失败: {e}")

def main():
    """主函数"""
    logging.info("开始数据库备份任务...")
    
    # 立即执行一次备份
    backup_database()
    
    # 定时执行备份
    schedule.every(BACKUP_INTERVAL).hours.do(backup_database)
    
    # 运行定时任务
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            logging.info("备份任务已停止")
            break
        except Exception as e:
            logging.error(f"备份任务运行过程中发生错误: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
