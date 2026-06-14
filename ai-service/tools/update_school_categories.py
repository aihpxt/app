#!/usr/bin/env python3
"""批量更新学校分类字段（公办/民办/重点）"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'school_platform.db')

class SchoolCategoryUpdater:
    """学校分类更新器"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
    
    def update_categories(self):
        """批量更新学校分类"""
        print("=" * 60)
        print("批量更新学校分类字段")
        print("=" * 60)
        
        # 获取所有学校
        self.cursor.execute("SELECT id, name, typeName, level, tuition, school_type FROM schools")
        schools = self.cursor.fetchall()
        
        total = len(schools)
        updated_public = 0
        updated_key = 0
        
        for school_id, name, type_name, level, tuition, school_type in schools:
            is_public = None
            is_key = None
            
            # 判断公办/民办
            if school_type == '公办':
                is_public = 1
            elif school_type == '民办':
                is_public = 0
            elif type_name:
                if '公办' in type_name or '公立' in type_name:
                    is_public = 1
                elif '民办' in type_name or '私立' in type_name:
                    is_public = 0
            elif name:
                if '民办' in name or '私立' in name:
                    is_public = 0
                else:
                    is_public = 1  # 默认公办
            
            # 判断是否重点高中
            if level:
                if '一级' in level or '重点' in level or '示范' in level:
                    is_key = 1
                else:
                    is_key = 0
            elif type_name:
                if '重点' in type_name or '一级' in type_name:
                    is_key = 1
                else:
                    is_key = 0
            else:
                is_key = 0  # 默认非重点
            
            # 更新数据库
            if is_public is not None:
                self.cursor.execute("UPDATE schools SET is_public = ? WHERE id = ?", (is_public, school_id))
                updated_public += 1
            if is_key is not None:
                self.cursor.execute("UPDATE schools SET is_key = ? WHERE id = ?", (is_key, school_id))
                updated_key += 1
        
        self.conn.commit()
        print(f"\n更新完成！")
        print(f"✓ 更新公办/民办字段: {updated_public} 所学校")
        print(f"✓ 更新重点高中字段: {updated_key} 所学校")
        
        # 统计结果
        self.cursor.execute("SELECT COUNT(*) FROM schools WHERE is_public = 1")
        public_count = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM schools WHERE is_public = 0")
        private_count = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM schools WHERE is_key = 1")
        key_count = self.cursor.fetchone()[0]
        
        print(f"\n📊 更新后统计:")
        print(f"   学校总数: {total} 所")
        print(f"   公办学校: {public_count} 所")
        print(f"   民办学校: {private_count} 所")
        print(f"   重点高中: {key_count} 所")
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    updater = SchoolCategoryUpdater()
    updater.update_categories()
    updater.close()