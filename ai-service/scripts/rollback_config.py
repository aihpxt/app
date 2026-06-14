#!/usr/bin/env python3
"""
配置文件回滚脚本
"""

import os
import shutil
from datetime import datetime

def main():
    env_file = '.env'
    config_backup_dir = 'config/backup'
    
    if not os.path.exists(config_backup_dir):
        print("错误：配置备份目录不存在")
        return
    
    backups = []
    for file in os.listdir(config_backup_dir):
        if file.startswith('config_stable'):
            file_path = os.path.join(config_backup_dir, file)
            backups.append((file_path, os.path.getmtime(file_path)))
    
    if not backups:
        print("错误：未找到稳定配置备份")
        return
    
    backups.sort(key=lambda x: x[1], reverse=True)
    stable_config = backups[0][0]
    
    print(f"找到稳定配置: {stable_config}")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    current_backup = f"{env_file}.backup_{timestamp}"
    shutil.copy2(env_file, current_backup)
    print(f"已备份当前配置: {current_backup}")
    
    shutil.copy2(stable_config, env_file)
    print("配置回滚成功")

if __name__ == "__main__":
    main()
