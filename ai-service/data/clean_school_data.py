#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""彻底清洗和整合学校数据"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

data_dir = Path(r'E:\aiphxt-app\ai-service\data')
backup_dir = data_dir / 'backups'
unified_db = data_dir / 'unified_school_data.db'

def load_schools_from_db(db_path, table_name='schools'):
    """从数据库加载学校数据"""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 获取表字段
        cols = cursor.execute(f'PRAGMA table_info({table_name})').fetchall()
        col_names = [c[1] for c in cols]

        # 查询所有数据
        rows = cursor.execute(f'SELECT * FROM {table_name}').fetchall()
        conn.close()

        return col_names, rows
    except Exception as e:
        print(f"  ❌ 加载失败 {db_path}: {e}")
        return [], []

def clean_and_merge():
    print("="*70)
    print("🧹 学校数据清洗与整合")
    print("="*70)

    # 加载各个数据源
    sources = {}

    # 1. school_platform.db
    print("\n📂 加载 school_platform.db...")
    cols, rows = load_schools_from_db(data_dir / 'school_platform.db')
    if rows:
        sources['platform'] = {'cols': cols, 'rows': rows, 'count': len(rows)}
        print(f"   ✅ 加载了 {len(rows)} 条数据")
        print(f"   字段: {cols}")

    # 2. wechat_data.db
    print("\n📂 加载 wechat_data.db...")
    cols, rows = load_schools_from_db(data_dir / 'wechat_data.db')
    if rows:
        sources['wechat'] = {'cols': cols, 'rows': rows, 'count': len(rows)}
        print(f"   ✅ 加载了 {len(rows)} 条数据")

        # 检查重复
        conn = sqlite3.connect(str(data_dir / 'wechat_data.db'))
        dup = conn.execute('SELECT name, COUNT(*) FROM schools GROUP BY name HAVING COUNT(*) > 1').fetchall()
        conn.close()
        print(f"   ⚠️ 发现 {len(dup)} 组重复数据")

    # 3. 最新备份
    backup_path = backup_dir / 'school_platform_20260522_125029.db'
    if backup_path.exists():
        print(f"\n📂 加载 {backup_path.name}...")
        cols, rows = load_schools_from_db(backup_path)
        if rows:
            sources['backup'] = {'cols': cols, 'rows': rows, 'count': len(rows)}
            print(f"   ✅ 加载了 {len(rows)} 条数据")

    # 合并数据
    print("\n" + "="*70)
    print("🔗 合并数据...")
    print("="*70)

    all_schools = {}  # name -> {data, sources}

    for source_name, source_data in sources.items():
        for row in source_data['rows']:
            # 尝试获取学校名称
            try:
                name_idx = source_data['cols'].index('name')
                name = row[name_idx]
                if not name:
                    continue
            except (ValueError, IndexError):
                continue

            if name not in all_schools:
                all_schools[name] = {
                    'data': row,
                    'cols': source_data['cols'],
                    'sources': [source_name]
                }
            else:
                all_schools[name]['sources'].append(source_name)

    print(f"\n✅ 合并完成: 共 {len(all_schools)} 所唯一学校")

    # 统计来源
    source_stats = {}
    for school in all_schools.values():
        for src in school['sources']:
            source_stats[src] = source_stats.get(src, 0) + 1

    print("\n📊 数据来源统计:")
    for src, cnt in sorted(source_stats.items(), key=lambda x: -x[1]):
        print(f"   {src}: {cnt} 所")

    # 创建统一数据库
    print("\n" + "="*70)
    print("💾 创建统一数据库...")
    print("="*70)

    # 备份旧的 unified 数据库（如果存在且可访问）
    if unified_db.exists():
        try:
            backup_name = f'unified_school_data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
            shutil.copy(unified_db, backup_dir / backup_name)
            print(f"   📦 备份旧数据库到: {backup_name}")
        except Exception as e:
            print(f"   ⚠️ 备份跳过: {e}")

    # 创建新的统一数据库
    if unified_db.exists():
        try:
            unified_db.unlink()
        except Exception as e:
            print(f"   ⚠️ 删除旧数据库跳过: {e}")

    conn = sqlite3.connect(unified_db)
    cursor = conn.cursor()

    # 创建 schools 表 - 使用最完整的字段结构
    cursor.execute('''
        CREATE TABLE schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            city TEXT,
            district TEXT,
            prefecture TEXT,
            type INTEGER,
            type_name TEXT,
            school_type TEXT,
            level TEXT,
            is_public INTEGER,
            is_key INTEGER,
            address TEXT,
            phone TEXT,
            website TEXT,
            description TEXT,
            features TEXT,
            logo TEXT,
            min_score REAL,
            min_rank INTEGER,
            max_score REAL,
            avg_score REAL,
            one_rate REAL,
            student_count INTEGER,
            teacher_count INTEGER,
            area TEXT,
            tuition INTEGER,
            boarding INTEGER,
            view_count INTEGER,
            style TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建索引
    cursor.execute('CREATE INDEX idx_schools_name ON schools(name)')
    cursor.execute('CREATE INDEX idx_schools_city ON schools(city)')
    cursor.execute('CREATE INDEX idx_schools_type ON schools(type)')
    cursor.execute('CREATE INDEX idx_schools_is_key ON schools(is_key)')

    # 插入数据
    inserted = 0
    for name, school_info in all_schools.items():
        row = school_info['data']
        cols = school_info['cols']

        # 提取各字段值，提供默认值
        def get_val(col_name, default=None):
            try:
                idx = cols.index(col_name)
                return row[idx] if idx < len(row) else default
            except (ValueError, IndexError):
                return default

        # 转换字段
        school_type = get_val('school_type')  # wechat用的是这个
        type_val = get_val('type')  # platform用的是这个
        type_name = school_type or (type_val if isinstance(type_val, str) else None)

        cursor.execute('''
            INSERT OR IGNORE INTO schools (
                name, city, district, prefecture, type, type_name, school_type,
                level, is_public, is_key, address, phone, website, description,
                features, logo, min_score, min_rank, max_score, avg_score,
                one_rate, student_count, teacher_count, area, tuition, boarding,
                view_count, style
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            get_val('city'),
            get_val('district'),
            get_val('prefecture'),
            type_val if isinstance(type_val, int) else None,
            type_name,
            school_type,
            get_val('level'),
            get_val('is_public'),
            get_val('is_key'),
            get_val('address'),
            get_val('phone'),
            get_val('website'),
            get_val('description'),
            get_val('features'),
            get_val('logo'),
            get_val('min_score'),
            get_val('min_rank'),
            get_val('max_score'),
            get_val('avg_score'),
            get_val('one_rate'),
            get_val('student_count'),
            get_val('teacher_count'),
            get_val('area'),
            get_val('tuition'),
            get_val('boarding'),
            get_val('view_count'),
            get_val('style')
        ))
        inserted += 1

    conn.commit()

    # 验证
    final_count = cursor.execute('SELECT COUNT(*) FROM schools').fetchone()[0]
    conn.close()

    print(f"\n✅ 统一数据库创建完成!")
    print(f"   📁 文件: {unified_db}")
    print(f"   📊 学校总数: {final_count}")

    # 生成报告
    report = f"""
================================================================================
学校数据清洗报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================

数据来源统计:
"""
    for src, cnt in sorted(source_stats.items(), key=lambda x: -x[1]):
        report += f"  - {src}: {cnt} 所\n"

    report += f"""
合并结果:
  - 原始去重后: {len(all_schools)} 所
  - 最终入库: {final_count} 所

字段统一:
  - type: 整数类型 (1=普通高中, 2=重点高中等)
  - type_name: 字符串类型 (完全中学, 重点高中等)
  - school_type: 保留原始类型

新建统一数据库:
  - 路径: {unified_db}
  - 字段: id, name, city, district, type, type_name, school_type, level,
          is_public, is_key, address, phone, website, description, features,
          min_score, one_rate, view_count 等

下一步:
  1. 将 unified_school_data.db 复制到后端数据目录
  2. 更新后端配置指向新的数据库
  3. 重启后端服务
================================================================================
"""

    print(report)

    # 保存报告
    report_path = data_dir / 'clean_data_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n📄 报告已保存: {report_path}")

    return final_count

if __name__ == '__main__':
    clean_and_merge()
