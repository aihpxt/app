#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
政策数据清洗脚本
清理数据库中重复和不一致的政策数据
"""

import sqlite3
from collections import defaultdict

class PolicyDataCleaner:
    """政策数据清洗器"""
    
    def __init__(self, db_path='data/unified_school_data.db'):
        self.db_path = db_path
        self.conn = None
        self.deleted_count = 0
        self.updated_count = 0
    
    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def analyze_policies(self):
        """分析政策数据"""
        cursor = self.conn.cursor()
        
        # 查询所有政策
        cursor.execute('SELECT * FROM policies')
        policies = cursor.fetchall()
        
        print(f"📊 政策总数: {len(policies)}")
        
        # 按地州分组
        prefecture_policies = defaultdict(list)
        for p in policies:
            code = p['prefecture_code']
            prefecture_policies[code].append(p)
        
        # 统计问题
        duplicate_count = 0
        null_title_count = 0
        issues = []
        
        for code, pols in sorted(prefecture_policies.items()):
            if len(pols) > 1:
                duplicate_count += len(pols) - 1
                issues.append(f"地州 {code} 有 {len(pols)} 条政策（重复）")
            
            for p in pols:
                if not p['title']:
                    null_title_count += 1
        
        print(f"⚠️ 重复政策数量: {duplicate_count}")
        print(f"⚠️ 标题为空的政策数量: {null_title_count}")
        
        return prefecture_policies, issues
    
    def clean_duplicate_policies(self):
        """清理重复政策"""
        cursor = self.conn.cursor()
        
        # 地州编码映射（标准编码 -> 完整名称）
        prefecture_map = {
            'km': '昆明市', 'ws': '文山州', 'dl': '大理州', 'qj': '曲靖市',
            'yx': '玉溪市', 'cx': '楚雄州', 'hh': '红河州', 'bs': '保山市',
            'zt': '昭通市', 'lj': '丽江市', 'pe': '普洱市', 'lc': '临沧市',
            'xsbn': '西双版纳州', 'dh': '德宏州', 'nj': '怒江州', 'dq': '迪庆州'
        }
        
        # 查询所有政策并按地州分组
        cursor.execute('SELECT * FROM policies')
        policies = cursor.fetchall()
        
        prefecture_policies = defaultdict(list)
        for p in policies:
            code = p['prefecture_code']
            # 标准化地州编码
            if code in prefecture_map.values():
                # 已经是完整名称，找到对应的缩写
                for k, v in prefecture_map.items():
                    if v == code:
                        normalized_code = k
                        break
            else:
                normalized_code = code
            
            prefecture_policies[normalized_code].append(p)
        
        # 清理重复数据
        deleted_ids = []
        
        for code, pols in prefecture_policies.items():
            if len(pols) <= 1:
                continue
            
            print(f"\n🔍 处理地州 {code}:")
            
            # 找到有标题的政策（优先保留）
            valid_policies = [p for p in pols if p['title']]
            invalid_policies = [p for p in pols if not p['title']]
            
            if valid_policies:
                # 保留有标题的政策，删除无标题的
                keep_id = valid_policies[0]['id']
                print(f"   ✓ 保留政策 ID:{keep_id}, 标题:{valid_policies[0]['title']}")
                
                for p in invalid_policies:
                    print(f"   ✗ 删除政策 ID:{p['id']}（标题为空）")
                    cursor.execute('DELETE FROM policies WHERE id = ?', (p['id'],))
                    deleted_ids.append(p['id'])
                    self.deleted_count += 1
            else:
                # 所有政策都没有标题，保留第一条
                keep_id = pols[0]['id']
                print(f"   ✓ 保留政策 ID:{keep_id}（第一条）")
                
                for p in pols[1:]:
                    print(f"   ✗ 删除政策 ID:{p['id']}（重复）")
                    cursor.execute('DELETE FROM policies WHERE id = ?', (p['id'],))
                    deleted_ids.append(p['id'])
                    self.deleted_count += 1
        
        # 清理地州名称格式不一致的问题（使用缩写形式）
        for code in prefecture_map.keys():
            full_name = prefecture_map[code]
            # 更新使用完整名称的记录为缩写
            cursor.execute(
                'UPDATE policies SET prefecture_code = ? WHERE prefecture_code = ?',
                (code, full_name)
            )
            updated = cursor.rowcount
            if updated > 0:
                print(f"\n📝 更新地州名称 '{full_name}' -> '{code}': {updated} 条")
                self.updated_count += updated
        
        self.conn.commit()
        return deleted_ids
    
    def validate_cleaned_data(self):
        """验证清洗后的数据"""
        cursor = self.conn.cursor()
        
        # 检查重复
        cursor.execute('''
            SELECT prefecture_code, COUNT(*) as cnt 
            FROM policies 
            GROUP BY prefecture_code 
            HAVING COUNT(*) > 1
        ''')
        duplicates = cursor.fetchall()
        
        # 检查空标题
        cursor.execute('SELECT COUNT(*) FROM policies WHERE title IS NULL OR title = ""')
        null_titles = cursor.fetchone()[0]
        
        # 检查地州编码格式
        valid_codes = {'km', 'ws', 'dl', 'qj', 'yx', 'cx', 'hh', 'bs', 'zt', 'lj', 'pe', 'lc', 'xsbn', 'dh', 'nj', 'dq'}
        cursor.execute('SELECT DISTINCT prefecture_code FROM policies')
        codes = {row['prefecture_code'] for row in cursor.fetchall()}
        invalid_codes = codes - valid_codes
        
        print("\n✅ 数据验证结果:")
        print(f"   重复政策: {'无' if not duplicates else len(duplicates)} 组")
        print(f"   空标题政策: {null_titles} 条")
        print(f"   无效地州编码: {invalid_codes if invalid_codes else '无'}")
        
        # 统计最终政策数量
        cursor.execute('SELECT COUNT(*) FROM policies')
        total = cursor.fetchone()[0]
        print(f"   清洗后政策总数: {total} 条")
        
        return not duplicates and null_titles == 0 and not invalid_codes
    
    def run(self):
        """执行清洗流程"""
        print("=" * 60)
        print("政策数据清洗工具")
        print("=" * 60)
        
        try:
            self.connect()
            
            print("\n【1】分析政策数据...")
            _, issues = self.analyze_policies()
            
            if issues:
                print("\n发现的问题:")
                for issue in issues:
                    print(f"  • {issue}")
            
            print("\n【2】清理重复政策...")
            deleted_ids = self.clean_duplicate_policies()
            print(f"\n删除了 {len(deleted_ids)} 条重复政策")
            
            print("\n【3】验证清洗结果...")
            is_valid = self.validate_cleaned_data()
            
            if is_valid:
                print("\n🎉 数据清洗完成！所有验证通过！")
            else:
                print("\n⚠️ 数据清洗完成，但部分验证未通过")
            
            print(f"\n📊 清洗统计:")
            print(f"   删除记录: {self.deleted_count} 条")
            print(f"   更新记录: {self.updated_count} 条")
            
        finally:
            self.close()

if __name__ == "__main__":
    cleaner = PolicyDataCleaner()
    cleaner.run()