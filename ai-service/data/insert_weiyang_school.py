#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插入未央中学数据到数据库
"""

import sqlite3
from pathlib import Path

def insert_weiyang_school():
    """插入未央中学数据"""
    db_path = Path(__file__).parent / 'school_platform.db'
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查是否已存在
        cursor.execute("SELECT id FROM schools WHERE name = ?", ('丘北未央中学',))
        if cursor.fetchone():
            print("丘北未央中学已存在于数据库中")
            conn.close()
            return
        
        # 插入未央中学数据
        school_data = {
            'name': '丘北未央中学',
            'type': 1,  # 民办
            'typeName': '民办',
            'minScore': 420.0,
            'minRank': 0,
            'oneRate': 75.0,
            'boarding': True,
            'tuition': 4900,
            'style': '综合发展',
            'features': '州一中直管,教学管理同步,全封闭管理,师资优质',
            'address': '丘北县锦屏镇文秀路129号',
            'phone': '0876-4122666',
            'website': '',
            'description': '丘北未央中学（文山州一中丘北校区）是文山州一中教育集团核心成员校，非营利性民办完全中学，与州一中本部实行教学同步、管理同步、考核同步。',
            'city': '丘北县',
            'district': '锦屏镇',
            'province': '云南省',
            'level': '州一中直管校区',
            'student_count': 2000,
            'teacher_count': 150,
            'area': '文山壮族苗族自治州',
            'prefecture': '文山壮族苗族自治州',
            'school_type': '完全中学',
            'is_public': 0,
            'is_key': 1
        }
        
        cursor.execute("""
            INSERT INTO schools (name, type, typeName, minScore, minRank, oneRate, boarding, tuition,
                               style, features, address, phone, website, description, city, district,
                               province, level, student_count, teacher_count, area, prefecture,
                               school_type, is_public, is_key)
            VALUES (:name, :type, :typeName, :minScore, :minRank, :oneRate, :boarding, :tuition,
                    :style, :features, :address, :phone, :website, :description, :city, :district,
                    :province, :level, :student_count, :teacher_count, :area, :prefecture,
                    :school_type, :is_public, :is_key)
        """, school_data)
        
        conn.commit()
        print("成功插入丘北未央中学数据")
        
        # 插入招生政策
        policy_data = {
            'title': '丘北未央中学2026年招生政策',
            'content': '''丘北未央中学2026年招生政策：
一、初中部招生：
1. 招收对象：小学六年级毕业生
2. 招生计划：400人（英才班50人、实验班150人、平行班200人）
3. 学费标准：
   - 公费生（英才班）：语数平均分≥180分，学费0元/学期
   - 自费生A类（实验班）：语数平均分160-179分，学费3900元/学期
   - 自费生B类（平行班）：语数平均分＜160分，学费4900元/学期
   - 住宿费：600元/学期
4. 奖学金：语数总分200分奖励5万元，199分奖励4万元，198分奖励3万元

二、高中部招生：
1. 招收对象：初中毕业生
2. 招生计划：600人（鹏程班50人、英才班150人、实验班400人）
3. 学费标准（按中考裸分）：
   - 620分以上：学费0元，住宿费0元
   - 600-619分：学费800元，住宿费600元
   - 570-599分：学费2000元，住宿费600元
   - 540-569分：学费2500元，住宿费600元
   - 510-539分：学费3000元，住宿费600元
   - 480-509分：学费3500元，住宿费600元
   - 450-479分：学费4000元，住宿费600元
   - 420-449分：学费5000元，住宿费600元
4. 奖学金：中考全州第1名奖励30万元，第2名25万元，第3名20万元

三、报名方式：携带户口本、成绩单、学籍证明等材料到学校招生办现场办理

四、联系方式：
招生热线：0876-4122666
地址：丘北县锦屏镇文秀路129号（弘毅楼一楼招生办）
工作时间：工作日8:30-17:00，周末9:00-16:00''',
            'category': '招生政策',
            'publish_date': '2026-01-01',
            'source': '丘北未央中学'
        }
        
        cursor.execute("""
            INSERT INTO policies (title, content, category, publish_date, source)
            VALUES (:title, :content, :category, :publish_date, :source)
        """, policy_data)
        
        conn.commit()
        print("成功插入丘北未央中学招生政策")
        
        conn.close()
        
    except Exception as e:
        print(f"插入数据时出错: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == '__main__':
    insert_weiyang_school()
