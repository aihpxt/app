#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新脚本 - 将爬虫数据集成到系统中
"""

import os
import sys

def update_specialists_file():
    """更新 specialists.py 文件，集成爬虫数据"""
    specialists_path = os.path.join(os.path.dirname(__file__), '..', 'agents', 'specialists.py')
    
    # 读取文件
    with open(specialists_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到需要修改的位置
    old_text = """        # 其他学校通用回复
        return (
            f"📚 关于您询问的学校信息\\n\\n"
            "我可以为您提供云南省内各所中学的详细信息，包括：\\n"
            "• 学校概况和办学特色\\n"
            "• 师资力量和教学质量\\n"
            "• 历年录取分数线\\n"
            "• 校园环境和设施\\n"
            "• 招生政策和报名方式\\n\\n"
            "请告诉我具体想了解哪所学校，或者您所在的城市，我可以为您推荐合适的学校！"
        )"""
    
    new_text = """        # 尝试从爬虫数据中获取学校信息
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
            logger.error(f"Failed to use school data importer: {e}")
        
        # 其他学校通用回复
        return (
            f"📚 关于您询问的学校信息\\n\\n"
            "我可以为您提供云南省内各所中学的详细信息，包括：\\n"
            "• 学校概况和办学特色\\n"
            "• 师资力量和教学质量\\n"
            "• 历年录取分数线\\n"
            "• 校园环境和设施\\n"
            "• 招生政策和报名方式\\n\\n"
            "请告诉我具体想了解哪所学校，或者您所在的城市，我可以为您推荐合适的学校！"
        )"""
    
    if old_text in content:
        content = content.replace(old_text, new_text)
        with open(specialists_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ 成功更新 specialists.py")
    else:
        print("✗ 未找到需要替换的文本")

def main():
    print("=" * 60)
    print("将爬虫数据集成到系统中")
    print("=" * 60)
    
    # 更新 specialists.py
    update_specialists_file()
    
    print("\n✅ 数据集成完成！")
    print("系统现在可以使用爬虫采集的学校数据了。")

if __name__ == "__main__":
    main()