#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库文件复制脚本
"""

import shutil
import os

def main():
    # 源文件路径
    source_db = r"e:\aiphxt-app\ai-service\data\unified_school_data.db"
    dest_db = r"e:\aiphxt-app\ai-service\sqlite\data\unified_school_data.db"
    
    print(f"源文件: {source_db}")
    print(f"目标文件: {dest_db}")
    
    try:
        # 检查源文件是否存在
        if not os.path.exists(source_db):
            print(f"错误：源文件不存在 - {source_db}")
            return
        
        # 复制文件
        shutil.copy2(source_db, dest_db)
        print(f"✅ 数据库文件复制成功！")
        
        # 验证复制
        if os.path.exists(dest_db):
            source_size = os.path.getsize(source_db)
            dest_size = os.path.getsize(dest_db)
            print(f"源文件大小: {source_size} bytes")
            print(f"目标文件大小: {dest_size} bytes")
            
            if source_size == dest_size:
                print("✅ 文件完整性验证通过！")
            else:
                print("❌ 文件完整性验证失败！")
        else:
            print("❌ 目标文件创建失败！")
            
    except Exception as e:
        print(f"❌ 复制失败: {e}")

if __name__ == '__main__':
    main()