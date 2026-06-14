#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导入器 - 使用统一数据访问层（保持向后兼容）
"""

import os
import sys
from typing import Dict, Any, List

class SchoolDataImporter:
    """学校数据导入器 - 使用统一数据访问层"""
    
    def __init__(self):
        # 添加项目根目录到Python路径（延迟导入）
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        self.dal = None
        self.use_unified_dal = False
        self.school_data = {}
        self.policy_data = {}
    
    def _get_dal(self):
        """延迟获取数据访问层"""
        if self.dal is None:
            try:
                from unified_data_access import get_unified_data_access
                self.dal = get_unified_data_access()
                self.use_unified_dal = True
                print("✓ 已连接统一数据访问层")
            except Exception as e:
                self.use_unified_dal = False
                print(f"✗ 无法连接统一数据访问层: {e}")
        return self.dal
    
    def load_crawled_data(self):
        """加载数据（现在使用统一数据访问层）"""
        self._get_dal()
        if self.use_unified_dal:
            print("✓ 使用统一数据访问层")
        else:
            # 备用：加载本地JSON文件
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            schools_file = os.path.join(data_dir, 'schools_data.json')
            if os.path.exists(schools_file):
                import json
                with open(schools_file, 'r', encoding='utf-8') as f:
                    self.school_data = json.load(f)
                print(f"✓ 已加载学校数据")
            policies_file = os.path.join(data_dir, 'policies_data.json')
            if os.path.exists(policies_file):
                import json
                with open(policies_file, 'r', encoding='utf-8') as f:
                    self.policy_data = json.load(f)
                print(f"✓ 已加载政策数据")
    
    def get_school_by_name(self, school_name: str) -> dict:
        """根据学校名称查找学校信息"""
        self._get_dal()
        if self.use_unified_dal and self.dal:
            return self.dal.get_school_by_name(school_name)
        
        # 备用：使用旧数据
        school_name_lower = school_name.lower()
        for prefecture_code, schools in self.school_data.items():
            for school in schools:
                if school['name'].lower().find(school_name_lower) != -1:
                    return school
                for keyword in school_name.split():
                    if keyword in school['name']:
                        return school
        return None
    
    def get_schools_by_prefecture(self, prefecture_code: str) -> List[dict]:
        """根据地州代码获取学校列表"""
        self._get_dal()
        if self.use_unified_dal and self.dal:
            # 地州代码映射
            prefecture_map = {
                'km': '昆明市',
                'ws': '文山州',
                'dl': '大理州',
                'qj': '曲靖市',
                'yx': '玉溪市',
                'cx': '楚雄州',
                'hh': '红河州',
                'bs': '保山市',
                'zt': '昭通市',
                'lj': '丽江市',
                'pe': '普洱市',
                'lc': '临沧市',
                'xsbn': '西双版纳州',
                'dh': '德宏州',
                'nj': '怒江州',
                'dq': '迪庆州'
            }
            prefecture_name = prefecture_map.get(prefecture_code, prefecture_code)
            return self.dal.get_schools_by_prefecture(prefecture_name)
        
        # 备用：使用旧数据
        return self.school_data.get(prefecture_code, [])
    
    def get_policy_by_prefecture(self, prefecture_code: str) -> dict:
        """根据地州代码获取政策信息"""
        self._get_dal()
        if self.use_unified_dal and self.dal:
            return self.dal.get_policy_by_prefecture(prefecture_code)
        
        # 备用：使用旧数据
        return self.policy_data.get(prefecture_code, {})
    
    def search_schools(self, keyword: str) -> List[dict]:
        """搜索学校"""
        self._get_dal()
        if self.use_unified_dal and self.dal:
            return self.dal.search_schools(keyword)
        
        # 备用：使用旧数据
        keyword_lower = keyword.lower()
        results = []
        for prefecture_code, schools in self.school_data.items():
            for school in schools:
                if (keyword_lower in school['name'].lower() or
                    keyword_lower in school['description'].lower() or
                    keyword_lower in school['type'].lower()):
                    results.append(school)
        return results
    
    def generate_school_info_text(self, school: dict) -> str:
        """生成学校信息文本"""
        self._get_dal()
        if self.use_unified_dal and self.dal:
            return self.dal.generate_school_info_text(school)
        
        # 备用：使用旧格式
        return (
            f"🏫 {school['name']}\n\n"
            f"【学校类型】{school.get('type', '')} {school.get('level', '')}\n"
            f"【学校地址】{school.get('address', '')}\n"
            f"【联系电话】{school.get('phone', '')}\n"
            f"【录取分数】{school.get('min_score', '')}分\n"
            f"【学校简介】{school.get('description', '')}"
        )
    
    def generate_policy_text(self, prefecture_code: str, prefecture_name: str) -> str:
        """生成政策信息文本"""
        self._get_dal()
        if self.use_unified_dal and self.dal:
            return self.dal.generate_policy_text(prefecture_code, prefecture_name)
        
        # 备用：使用旧格式
        policy = self.policy_data.get(prefecture_code, {})
        if not policy:
            return f"暂无{prefecture_name}的政策信息"
        
        return (
            f"📋 {prefecture_name}中考招生政策\n\n"
            f"【政策标题】{policy.get('title', '')}\n\n"
            f"【志愿批次】{policy.get('volunteer_batch', '')}\n\n"
            f"【特殊政策】{policy.get('special_policy', '')}\n\n"
            f"【报名时间】{policy.get('registration_time', '')}\n\n"
            f"【咨询电话】{policy.get('contact', '')}"
        )

# 创建全局数据导入器实例
school_data_importer = None

def get_school_data_importer() -> SchoolDataImporter:
    """获取学校数据导入器实例"""
    global school_data_importer
    if school_data_importer is None:
        school_data_importer = SchoolDataImporter()
        school_data_importer.load_crawled_data()
    return school_data_importer

def main():
    """测试数据导入"""
    print("=" * 60)
    print("数据导入器测试（使用统一数据访问层）")
    print("=" * 60)
    
    importer = get_school_data_importer()
    
    # 测试搜索学校
    print("\n[测试1] 搜索学校 '师大附中':")
    school = importer.get_school_by_name("师大附中")
    if school:
        print(importer.generate_school_info_text(school))
    else:
        print("未找到学校")
    
    # 测试获取地州学校
    print("\n[测试2] 获取昆明学校列表:")
    km_schools = importer.get_schools_by_prefecture("km")
    for s in km_schools[:5]:
        print(f"  - {s['name']}")
    
    # 测试搜索功能
    print("\n[测试3] 搜索 '公办' 学校:")
    results = importer.search_schools("公办")
    print(f"找到 {len(results)} 所学校")
    
    print("\n✅ 数据导入器测试完成！")

if __name__ == "__main__":
    main()