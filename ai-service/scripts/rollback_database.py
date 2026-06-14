#!/usr/bin/env python3
"""
数据库回滚脚本
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime

def get_latest_backup(backup_dir):
    """获取最新的备份文件"""
    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith('school_platform_') and file.endswith('.db'):
            file_path = os.path.join(backup_dir, file)
            backups.append((file_path, os.path.getmtime(file_path)))
    
    if not backups:
        return None
    
    backups.sort(key=lambda x: x[1], reverse=True)
    return backups[0][0]

def verify_backup(backup_file):
    """验证备份文件完整性"""
    try:
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM schools")
        count = cursor.fetchone()[0]
        conn.close()
        return True, f"备份验证通过，包含 {count} 条学校记录"
    except Exception as e:
        return False, f"备份验证失败: {e}"

def rollback_database(db_file, backup_file):
    """执行数据库回滚"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rollback_before = db_file + f".rollback_before_{timestamp}"
        shutil.copy2(db_file, rollback_before)
        print(f"已创建回滚前备份: {rollback_before}")
        
        shutil.copy2(backup_file, db_file)
        return True, "数据库回滚成功"
    except Exception as e:
        return False, f"数据库回滚失败: {e}"

def main():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    db_file = os.path.join(data_dir, 'school_platform.db')
    backup_dir = os.path.join(data_dir, 'backups')
    
    backup_file = get_latest_backup(backup_dir)
    if not backup_file:
        print("错误：未找到备份文件")
        sys.exit(1)
    
    print(f"找到最新备份: {backup_file}")
    
    success, msg = verify_backup(backup_file)
    print(msg)
    if not success:
        sys.exit(1)
    
    success, msg = rollback_database(db_file, backup_file)
    print(msg)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
