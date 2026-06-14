#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新脚本 - 将 specialists.py 迁移到统一数据访问层
"""

import os
import sys

def update_specialists_to_unified_dal():
    """更新 specialists.py 使用统一数据访问层"""
    specialists_path = os.path.join(os.path.dirname(__file__), 'agents', 'specialists.py')
    
    with open(specialists_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 添加统一数据访问层的导入
    old_import = "import json"
    new_import = """import json
try:
    from unified_data_access import get_unified_data_access
    UNIFIED_DAL_AVAILABLE = True
except ImportError:
    UNIFIED_DAL_AVAILABLE = False"""
    
    content = content.replace(old_import, new_import)
    
    # 2. 替换 _get_school_info 方法中的爬虫数据导入器为统一数据访问层
    old_code = """        # 尝试从爬虫数据中获取学校信息
        try:
            from openclaw.school_data_importer import get_school_data_importer
            importer = get_school_data_importer()
            
            # 搜索学校
            results = importer.search_schools(user_input)
            if results:
                response = "🏫 为您找到以下学校：\\n\\n"
                for i, school in enumerate(results[:3], 1):
                    response += f"{i}. {school['name']}\\n"
                    response += f"   • 类型：{school['type']} {school['level']}\\n"
                    response += f"   • 地址：{school['address']}\\n"
                    response += f"   • 分数线：{school['min_score']}分\\n"
                    response += f"   • 简介：{school['description']}\\n\\n"
                response += "需要了解哪所学校的详细信息？"
                return response
        except Exception as e:
            logger.error(f"Failed to use school data importer: {e}")"""
    
    new_code = """        # 使用统一数据访问层获取学校信息
        if UNIFIED_DAL_AVAILABLE:
            try:
                dal = get_unified_data_access()
                
                # 搜索学校
                results = dal.search_schools(user_input)
                if results:
                    response = "🏫 为您找到以下学校：\\n\\n"
                    for i, school in enumerate(results[:3], 1):
                        school_name = school.get('name', '')
                        school_type = school.get('type_name', '')
                        school_level = school.get('level', '')
                        school_address = school.get('address', '')
                        min_score = school.get('min_score', '')
                        description = school.get('description', '')
                        
                        response += f"{i}. {school_name}\\n"
                        response += f"   • 类型：{school_type} {school_level}\\n"
                        response += f"   • 地址：{school_address}\\n"
                        response += f"   • 分数线：{min_score}分\\n"
                        response += f"   • 简介：{description}\\n\\n"
                    response += "需要了解哪所学校的详细信息？"
                    return response
            except Exception as e:
                logger.error(f"Failed to use unified data access layer: {e}")"""
    
    content = content.replace(old_code, new_code)
    
    with open(specialists_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ 成功更新 specialists.py 使用统一数据访问层")

def main():
    print("=" * 60)
    print("将系统迁移到统一数据访问层")
    print("=" * 60)
    
    update_specialists_to_unified_dal()
    
    print("\n✅ 迁移完成！")
    print("系统现在使用统一数据访问层获取学校数据")

if __name__ == "__main__":
    main()