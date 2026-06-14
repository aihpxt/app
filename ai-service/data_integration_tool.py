#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据整合方案 - 检查并合并系统中分散的数据
"""

import os
import json
import sqlite3
from typing import Dict, Any, List

class DataIntegrationAnalyzer:
    """数据整合分析器"""
    
    def __init__(self):
        self.data_files = []
        self.database_files = []
        self.school_data_sources = {}
        self.conflicts = []
    
    def scan_data_files(self):
        """扫描所有数据文件"""
        base_path = os.path.dirname(__file__)
        
        # 扫描JSON数据文件
        json_patterns = [
            'data/*.json',
            'openclaw/data/*.json',
            '*.json'
        ]
        
        import glob
        for pattern in json_patterns:
            for file_path in glob.glob(os.path.join(base_path, pattern)):
                if os.path.isfile(file_path):
                    filename = os.path.basename(file_path)
                    if filename.startswith('e2e_test') or filename.startswith('high_concurrency'):
                        continue  # 跳过测试报告
                    self.data_files.append(file_path)
        
        # 扫描数据库文件
        db_patterns = [
            'data/*.db',
            '*.db'
        ]
        
        for pattern in db_patterns:
            for file_path in glob.glob(os.path.join(base_path, pattern)):
                if os.path.isfile(file_path):
                    self.database_files.append(file_path)
    
    def analyze_json_files(self):
        """分析JSON文件中的学校数据"""
        school_name_key = '学校名称'
        score_key = '最低分数'
        
        for file_path in self.data_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                filename = os.path.basename(file_path)
                
                # 处理数组类型
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            # 提取学校名称
                            name = item.get('name') or item.get('school_name') or item.get(school_name_key)
                            if name:
                                score = item.get('minScore') or item.get('min_score') or item.get(score_key)
                                if score:
                                    if name not in self.school_data_sources:
                                        self.school_data_sources[name] = []
                                    self.school_data_sources[name].append({
                                        'source': filename,
                                        'score': score,
                                        'data': item
                                    })
                
                # 处理字典类型
                elif isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict):
                                    name = item.get('name') or item.get('school_name') or item.get(school_name_key)
                                    if name:
                                        score = item.get('minScore') or item.get('min_score') or item.get(score_key)
                                        if score:
                                            if name not in self.school_data_sources:
                                                self.school_data_sources[name] = []
                                            self.school_data_sources[name].append({
                                                'source': filename,
                                                'score': score,
                                                'data': item
                                            })
            except Exception as e:
                print(f"✗ 无法解析 {file_path}: {e}")
    
    def detect_conflicts(self):
        """检测数据冲突"""
        for school_name, sources in self.school_data_sources.items():
            if len(sources) > 1:
                scores = [s['score'] for s in sources]
                unique_scores = set(scores)
                if len(unique_scores) > 1:
                    self.conflicts.append({
                        'school': school_name,
                        'sources': sources,
                        'conflicting_scores': list(unique_scores)
                    })
    
    def generate_report(self):
        """生成整合报告"""
        print("=" * 80)
        print("数据整合分析报告")
        print("=" * 80)
        
        # 数据文件统计
        print("\n【1】数据文件统计")
        print(f"   JSON文件数量: {len(self.data_files)}")
        print(f"   数据库文件数量: {len(self.database_files)}")
        print(f"   涉及学校数量: {len(self.school_data_sources)}")
        
        # 数据来源分布
        print("\n【2】数据来源分布")
        source_counts = {}
        for sources in self.school_data_sources.values():
            for s in sources:
                source = s['source']
                source_counts[source] = source_counts.get(source, 0) + 1
        
        for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
            print(f"   • {source}: {count}所学校")
        
        # 冲突检测
        print("\n【3】数据冲突检测")
        if self.conflicts:
            print(f"   发现 {len(self.conflicts)} 处数据冲突:")
            for i, conflict in enumerate(self.conflicts, 1):
                print(f"\n   {i}. {conflict['school']}")
                for source in conflict['sources']:
                    print(f"      - {source['source']}: 分数线={source['score']}")
                print(f"      冲突分数: {conflict['conflicting_scores']}")
        else:
            print("   ✅ 未发现数据冲突")
        
        # 整合建议
        print("\n【4】整合建议")
        print("   • 将所有学校数据合并到统一的数据库表中")
        print("   • 建立数据来源优先级机制")
        print("   • 清理重复的JSON文件")
        print("   • 建立数据更新流程")
        
        return {
            'total_files': len(self.data_files),
            'total_databases': len(self.database_files),
            'total_schools': len(self.school_data_sources),
            'conflicts': self.conflicts,
            'source_counts': source_counts
        }

class DataIntegrator:
    """数据整合器"""
    
    def __init__(self):
        self.unified_db_path = os.path.join(os.path.dirname(__file__), 'data', 'unified_school_data.db')
    
    def create_unified_database(self):
        """创建统一数据库"""
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        # 创建统一学校表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unified_schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                type TEXT,
                type_name TEXT,
                min_score REAL,
                min_rank INTEGER,
                one_rate REAL,
                boarding BOOLEAN,
                tuition INTEGER,
                style TEXT,
                features TEXT,
                address TEXT,
                phone TEXT,
                website TEXT,
                description TEXT,
                city TEXT,
                prefecture TEXT,
                level TEXT,
                source TEXT,
                source_priority INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建政策表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prefecture_code TEXT,
                prefecture_name TEXT,
                title TEXT,
                volunteer_batch TEXT,
                special_policy TEXT,
                registration_time TEXT,
                contact TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✓ 创建统一数据库: {self.unified_db_path}")
    
    def integrate_school_data(self, analyzer):
        """整合学校数据"""
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        # 数据来源优先级
        priority_map = {
            'official_school_data.json': 10,
            'prefecture_schools.json': 9,
            'school_list.json': 8,
            'schools.json': 7,
            'schools_data.json': 6,
            'school_data.json': 5,
            'map_school_data.json': 4,
            'crawler_data.json': 3,
            'prefecture_policies.json': 2,
            'policies_data.json': 1
        }
        
        for school_name, sources in analyzer.school_data_sources.items():
            # 选择优先级最高的数据
            sources.sort(key=lambda x: priority_map.get(x['source'], 0), reverse=True)
            best_source = sources[0]
            data = best_source['data']
            source = best_source['source']
            priority = priority_map.get(source, 0)
            
            # 提取字段
            name = data.get('name') or data.get('school_name') or data.get('学校名称')
            school_type = data.get('type')
            type_name = data.get('typeName') or data.get('nature') or data.get('学校类型')
            min_score = data.get('minScore') or data.get('min_score') or data.get('最低分数')
            min_rank = data.get('minRank') or data.get('最低排名')
            one_rate = data.get('oneRate') or data.get('一本率')
            boarding = data.get('boarding')
            tuition = data.get('tuition')
            style = data.get('style')
            features = json.dumps(data.get('features', [])) if isinstance(data.get('features'), list) else data.get('features')
            address = data.get('address') or data.get('地址')
            phone = data.get('phone') or data.get('contact') or data.get('电话')
            website = data.get('website')
            description = data.get('description') or data.get('简介')
            city = data.get('city') or data.get('城市')
            prefecture = data.get('prefecture') or data.get('地州') or city
            level = data.get('level') or data.get('等级')
            
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO unified_schools
                    (name, type, type_name, min_score, min_rank, one_rate, boarding, 
                     tuition, style, features, address, phone, website, description, 
                     city, prefecture, level, source, source_priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, school_type, type_name, min_score, min_rank, one_rate, boarding,
                      tuition, style, features, address, phone, website, description,
                      city, prefecture, level, source, priority))
            except Exception as e:
                print(f"✗ 插入 {name} 失败: {e}")
        
        conn.commit()
        
        # 统计插入数量
        cursor.execute('SELECT COUNT(*) FROM unified_schools')
        count = cursor.fetchone()[0]
        print(f"✓ 成功整合 {count} 所学校数据")
        
        conn.close()
    
    def integrate_policy_data(self):
        """整合政策数据"""
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        # 加载政策数据
        policy_files = [
            'openclaw/data/policies_data.json',
            'data/policies_2026.json',
            'openclaw/data/prefecture_policies.json'
        ]
        
        inserted = 0
        for file_name in policy_files:
            file_path = os.path.join(os.path.dirname(__file__), file_name)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, dict):
                    for prefecture_code, policy in data.items():
                        try:
                            cursor.execute('''
                                INSERT OR IGNORE INTO policies
                                (prefecture_code, prefecture_name, title, volunteer_batch, 
                                 special_policy, registration_time, contact, source)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (prefecture_code, policy.get('name'), policy.get('title'), 
                                  policy.get('volunteer_batch'), policy.get('special_policy'),
                                  policy.get('registration_time'), policy.get('contact'), file_name))
                            inserted += 1
                        except Exception as e:
                            pass
        
        conn.commit()
        print(f"✓ 成功整合 {inserted} 条政策数据")
        conn.close()
    
    def verify_integration(self):
        """验证整合结果"""
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM unified_schools')
        school_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM policies')
        policy_count = cursor.fetchone()[0]
        
        # 获取来源分布
        cursor.execute('SELECT source, COUNT(*) FROM unified_schools GROUP BY source')
        source_dist = cursor.fetchall()
        
        conn.close()
        
        print("\n【验证结果】")
        print(f"   学校数据: {school_count} 条")
        print(f"   政策数据: {policy_count} 条")
        print("\n   数据来源分布:")
        for source, count in source_dist:
            print(f"      • {source}: {count}条")
        
        return {
            'school_count': school_count,
            'policy_count': policy_count,
            'source_distribution': dict(source_dist)
        }

def main():
    """主函数"""
    print("=" * 80)
    print("数据整合工具 - 检测并合并分散的数据")
    print("=" * 80)
    
    # 分析数据
    analyzer = DataIntegrationAnalyzer()
    analyzer.scan_data_files()
    analyzer.analyze_json_files()
    analyzer.detect_conflicts()
    report = analyzer.generate_report()
    
    # 整合数据
    integrator = DataIntegrator()
    integrator.create_unified_database()
    integrator.integrate_school_data(analyzer)
    integrator.integrate_policy_data()
    integrator.verify_integration()
    
    print("\n✅ 数据整合完成！")
    print("建议：")
    print("   1. 更新系统代码使用统一数据库")
    print("   2. 删除重复的JSON文件")
    print("   3. 建立数据更新机制")

if __name__ == "__main__":
    main()