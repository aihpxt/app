#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据访问层 - 提供统一的数据接口
"""

import os
import sqlite3
import json
from typing import Dict, Any, List, Optional

class UnifiedDataAccessLayer:
    """统一数据访问层"""
    
    def __init__(self, db_path: Optional[str] = None):
        # 支持环境变量配置数据库路径
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = os.environ.get(
                'DB_PATH',
                os.path.join(os.path.dirname(__file__), 'sqlite', 'data', 'unified_school_data.db')
            )
        self._ensure_connection()
    
    def _ensure_connection(self):
        """确保数据库连接"""
        if not os.path.exists(self.db_path):
            print(f"警告：数据库文件不存在: {self.db_path}")
    
    def get_school_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取学校信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM schools 
            WHERE name LIKE ? OR name LIKE ?
        ''', (f'%{name}%', f'%{name}%'))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = ['id', 'name', 'city', 'district', 'prefecture', 'type', 'type_name', 
                       'school_type', 'level', 'is_public', 'is_key', 'address', 'phone', 
                       'website', 'description', 'features', 'logo', 'min_score', 'min_rank', 
                       'max_score', 'avg_score', 'one_rate', 'student_count', 'teacher_count', 
                       'area', 'tuition', 'boarding', 'view_count', 'style', 'created_at', 'updated_at']
            result = dict(zip(columns, row))
            # 解析features字段
            if result['features']:
                try:
                    result['features'] = json.loads(result['features'])
                except:
                    pass
            return result
        return None
    
    def search_schools(self, keyword: str, prefecture: str = None) -> List[Dict[str, Any]]:
        """搜索学校"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM schools 
            WHERE (name LIKE ? OR city LIKE ? OR prefecture LIKE ?)
        '''
        params = (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
        
        if prefecture:
            query += ' AND prefecture LIKE ?'
            params += (f'%{prefecture}%',)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'name', 'city', 'district', 'prefecture', 'type', 'type_name', 
                   'school_type', 'level', 'is_public', 'is_key', 'address', 'phone', 
                   'website', 'description', 'features', 'logo', 'min_score', 'min_rank', 
                   'max_score', 'avg_score', 'one_rate', 'student_count', 'teacher_count', 
                   'area', 'tuition', 'boarding', 'view_count', 'style', 'created_at', 'updated_at']
        
        results = []
        for row in rows:
            result = dict(zip(columns, row))
            if result['features']:
                try:
                    result['features'] = json.loads(result['features'])
                except:
                    pass
            results.append(result)
        
        return results
    
    def get_schools_by_prefecture(self, prefecture: str) -> List[Dict[str, Any]]:
        """根据地州获取学校列表"""
        return self.search_schools('', prefecture)
    
    def get_policy_by_prefecture(self, prefecture_code: str) -> Optional[Dict[str, Any]]:
        """获取地州政策"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 尝试从schools表获取政策相关信息
        cursor.execute('SELECT * FROM schools WHERE prefecture LIKE ? LIMIT 1', (f'%{prefecture_code}%',))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = ['id', 'name', 'city', 'district', 'prefecture', 'type', 'type_name', 
                       'school_type', 'level', 'is_public', 'is_key', 'address', 'phone', 
                       'website', 'description', 'features', 'logo', 'min_score', 'min_rank', 
                       'max_score', 'avg_score', 'one_rate', 'student_count', 'teacher_count', 
                       'area', 'tuition', 'boarding', 'view_count', 'style', 'created_at', 'updated_at']
            result = dict(zip(columns, row))
            return {'prefecture_name': result.get('prefecture', prefecture_code), 'title': f'{prefecture_code}招生政策'}
        return None
    
    def get_all_prefectures(self) -> List[str]:
        """获取所有地州列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT prefecture FROM schools ORDER BY prefecture')
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows if row[0]]
    
    def get_school_count(self) -> int:
        """获取学校总数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM schools')
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def generate_school_info_text(self, school: Dict[str, Any]) -> str:
        """生成学校信息文本"""
        return (
            f"🏫 {school['name']}\n\n"
            f"【学校类型】{school.get('type_name', '')} {school.get('level', '')}\n"
            f"【所在城市】{school.get('city', '')}\n"
            f"【学校地址】{school.get('address', '')}\n"
            f"【联系电话】{school.get('phone', '')}\n"
            f"【录取分数】{school.get('min_score', '')}分\n"
            f"【学校简介】{school.get('description', '')}"
        )
    
    def generate_policy_text(self, prefecture_code: str, prefecture_name: str) -> str:
        """生成政策信息文本"""
        policy = self.get_policy_by_prefecture(prefecture_code)
        if not policy:
            return f"暂无{prefecture_name}的政策信息"
        
        return (
            f"📋 {prefecture_name}中考招生政策\n\n"
            f"【政策标题】{policy.get('title', '')}\n\n"
            f"如需了解详细政策，请访问当地教育局官网或咨询学校招生办。"
        )

# 创建全局实例
unified_data_access = None

def get_unified_data_access() -> UnifiedDataAccessLayer:
    """获取统一数据访问层实例"""
    global unified_data_access
    if unified_data_access is None:
        unified_data_access = UnifiedDataAccessLayer()
    return unified_data_access

def main():
    """测试统一数据访问层"""
    print("=" * 60)
    print("统一数据访问层测试")
    print("=" * 60)
    
    dal = get_unified_data_access()
    
    # 测试获取学校
    print("\n[测试1] 获取师大附中信息:")
    school = dal.get_school_by_name("师大附中")
    if school:
        print(dal.generate_school_info_text(school))
    else:
        print("未找到学校")
    
    # 测试搜索
    print("\n[测试2] 搜索昆明的学校:")
    schools = dal.get_schools_by_prefecture("昆明市")
    print(f"找到 {len(schools)} 所学校")
    for s in schools[:5]:
        print(f"  • {s['name']} - {s.get('min_score', '')}分")
    
    # 测试统计
    print(f"\n[测试3] 学校总数: {dal.get_school_count()}")
    
    # 测试地州列表
    print("\n[测试4] 地州列表:")
    prefectures = dal.get_all_prefectures()
    print(f"找到 {len(prefectures)} 个地州")
    print(", ".join(prefectures[:10]) + ("..." if len(prefectures) > 10 else ""))
    
    print("\n✅ 统一数据访问层测试完成！")

if __name__ == "__main__":
    main()