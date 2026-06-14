#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
政策数据准确性检查工具
"""

import json
import sqlite3
from typing import Dict, Any, List

class PolicyDataValidator:
    """政策数据验证器"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def add_error(self, message):
        """添加错误信息"""
        self.errors.append(message)
    
    def add_warning(self, message):
        """添加警告信息"""
        self.warnings.append(message)
    
    def validate_json_file(self, file_path: str) -> Dict[str, Any]:
        """验证JSON文件"""
        print(f"📋 检查文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                self.add_error(f"文件格式错误：期望dict，实际为 {type(data).__name__}")
                return {}
            
            return data
        except json.JSONDecodeError as e:
            self.add_error(f"JSON解析错误: {e}")
            return {}
        except FileNotFoundError:
            self.add_error(f"文件不存在: {file_path}")
            return {}
        except Exception as e:
            self.add_error(f"读取文件失败: {e}")
            return {}
    
    def validate_policy_entry(self, code: str, policy: Dict[str, Any], expected_fields: List[str]):
        """验证单个政策条目"""
        print(f"\n🔍 验证地州 {code} 的政策...")
        
        # 检查必填字段
        for field in expected_fields:
            if field not in policy:
                self.add_error(f"地州 {code} 缺少字段: {field}")
            elif policy[field] is None or policy[field] == '':
                self.add_warning(f"地州 {code} 的字段 {field} 值为空")
        
        # 验证年份
        if 'title' in policy:
            title = policy['title']
            if '2026' not in title and '2025' not in title:
                self.add_warning(f"地州 {code} 的政策标题未包含年份: {title}")
        
        # 验证地州编码
        valid_codes = {'km', 'ws', 'dl', 'qj', 'yx', 'cx', 'hh', 'bs', 'zt', 'lj', 'pe', 'lc', 'xsbn', 'dh', 'nj', 'dq'}
        if code not in valid_codes:
            self.add_warning(f"地州编码 {code} 不在标准编码列表中")
        
        # 验证地州名称
        prefecture_map = {
            'km': '昆明市', 'ws': '文山州', 'dl': '大理州', 'qj': '曲靖市',
            'yx': '玉溪市', 'cx': '楚雄州', 'hh': '红河州', 'bs': '保山市',
            'zt': '昭通市', 'lj': '丽江市', 'pe': '普洱市', 'lc': '临沧市',
            'xsbn': '西双版纳州', 'dh': '德宏州', 'nj': '怒江州', 'dq': '迪庆州'
        }
        if code in prefecture_map:
            expected_name = prefecture_map[code]
            actual_name = policy.get('prefecture_name', '')
            if actual_name != expected_name:
                self.add_warning(f"地州 {code} 的名称不匹配: 期望 '{expected_name}'，实际 '{actual_name}'")
        
        # 打印政策摘要
        print(f"   标题: {policy.get('title', 'N/A')}")
        print(f"   地州名称: {policy.get('prefecture_name', 'N/A')}")
        print(f"   志愿批次: {'有' if policy.get('volunteer_batch') else '无'}")
        print(f"   特殊政策: {'有' if policy.get('special_policy') else '无'}")
        print(f"   报名时间: {'有' if policy.get('registration_time') else '无'}")
    
    def validate_database_policies(self):
        """验证数据库中的政策数据"""
        print("\n" + "=" * 60)
        print("验证数据库中的政策数据")
        print("=" * 60)
        
        conn = sqlite3.connect('data/unified_school_data.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM policies ORDER BY prefecture_code')
        policies = cursor.fetchall()
        
        print(f"数据库中政策总数: {len(policies)}")
        
        expected_fields = ['prefecture_code', 'prefecture_name', 'title', 'volunteer_batch', 
                          'special_policy', 'registration_time', 'contact']
        
        for p in policies:
            policy_dict = {
                'prefecture_code': p[1],
                'prefecture_name': p[2],
                'title': p[3],
                'volunteer_batch': p[4],
                'special_policy': p[5],
                'registration_time': p[6],
                'contact': p[7]
            }
            self.validate_policy_entry(p[1], policy_dict, expected_fields)
        
        conn.close()
    
    def validate_json_policies(self, file_path: str):
        """验证JSON文件中的政策数据"""
        print("\n" + "=" * 60)
        print("验证JSON文件中的政策数据")
        print("=" * 60)
        
        data = self.validate_json_file(file_path)
        if not data:
            return
        
        expected_fields = ['prefecture_code', 'prefecture_name', 'title', 'volunteer_batch', 
                          'special_policy', 'registration_time', 'contact']
        
        for code, policy in sorted(data.items()):
            self.validate_policy_entry(code, policy, expected_fields)
    
    def generate_report(self):
        """生成检查报告"""
        print("\n" + "=" * 60)
        print("政策数据准确性检查报告")
        print("=" * 60)
        
        print(f"\n📊 检查结果统计:")
        print(f"   错误数量: {len(self.errors)}")
        print(f"   警告数量: {len(self.warnings)}")
        
        if self.errors:
            print("\n❌ 发现的错误:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        if self.warnings:
            print("\n⚠️ 发现的警告:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ 所有政策数据验证通过！")
        elif not self.errors:
            print("\n⚠️ 政策数据基本正确，但有一些警告需要关注")
        else:
            print("\n❌ 政策数据存在错误，请修复后再使用")
        
        return len(self.errors) == 0
    
    def run(self):
        """执行检查流程"""
        print("=" * 60)
        print("政策数据准确性检查工具")
        print("=" * 60)
        
        # 验证JSON文件
        self.validate_json_policies('openclaw/data/policies_data.json')
        
        # 验证数据库
        self.validate_database_policies()
        
        # 生成报告
        return self.generate_report()

if __name__ == "__main__":
    validator = PolicyDataValidator()
    validator.run()