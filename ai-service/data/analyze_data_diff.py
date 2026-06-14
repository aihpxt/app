#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深度分析各数据库学校数据差异"""

import sqlite3
from pathlib import Path

data_dir = Path(r'E:\aiphxt-app\ai-service\data')

def get_schools(db_path, school_table='schools'):
    """获取学校数据"""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        schools = cursor.execute(f'SELECT id, name, city, type, is_public, is_key, min_score, one_rate FROM {school_table}').fetchall()
        conn.close()
        return schools
    except Exception as e:
        return []

def analyze_differences():
    # 加载各个数据库的学校
    platform = {s[1]: s for s in get_schools(data_dir / 'school_platform.db')}
    backup_new = {s[1]: s for s in get_schools(data_dir / 'backups' / 'school_platform_20260522_125029.db')}
    backup_old = {s[1]: s for s in get_schools(data_dir / 'backups' / 'school_platform_20260521_124931.db')}
    wechat = {s[1]: s for s in get_schools(data_dir / 'wechat_data.db', 'schools')}

    print("="*70)
    print("📊 数据库学校数量统计")
    print("="*70)
    print(f"  school_platform.db:           {len(platform)} 所")
    print(f"  backup_20260522:              {len(backup_new)} 所")
    print(f"  backup_20260521:              {len(backup_old)} 所")
    print(f"  wechat_data.db (去重前):     {len(wechat)} 所 (有重复)")
    print()

    # 找出差异
    all_names = set(platform.keys()) | set(backup_new.keys()) | set(backup_old.keys()) | set(wechat.keys())

    only_in_backup_new = set(backup_new.keys()) - set(platform.keys())
    only_in_backup_old = set(backup_old.keys()) - set(platform.keys())
    only_in_wechat = set(wechat.keys()) - set(platform.keys())

    print("="*70)
    print("🔍 数据差异分析")
    print("="*70)

    print(f"\n1️⃣ backup_20260522 独有的学校 ({len(only_in_backup_new)} 所):")
    for name in sorted(list(only_in_backup_new)[:10]):
        print(f"   - {name}")
    if len(only_in_backup_new) > 10:
        print(f"   ... 还有 {len(only_in_backup_new) - 10} 所")

    print(f"\n2️⃣ backup_20260521 独有的学校 ({len(only_in_backup_old)} 所):")
    for name in sorted(list(only_in_backup_old)[:10]):
        print(f"   - {name}")
    if len(only_in_backup_old) > 10:
        print(f"   ... 还有 {len(only_in_backup_old) - 10} 所")

    print(f"\n3️⃣ wechat_data.db 独有的学校 ({len(only_in_wechat)} 所):")
    for name in sorted(list(only_in_wechat)[:10]):
        print(f"   - {name}")
    if len(only_in_wechat) > 10:
        print(f"   ... 还有 {len(only_in_wechat) - 10} 所")

    # 检查 wechat 的重复学校
    print("\n" + "="*70)
    print("⚠️ wechat_data.db 重复学校 (前10组):")
    print("="*70)
    try:
        conn = sqlite3.connect(str(data_dir / 'wechat_data.db'))
        dup = conn.execute('''
            SELECT name, COUNT(*) as cnt
            FROM schools
            GROUP BY name
            HAVING COUNT(*) > 1
        ''').fetchall()
        conn.close()
        for name, cnt in dup[:10]:
            print(f"   {name}: {cnt}条")
    except Exception as e:
        print(f"   错误: {e}")

    # 找出完整的最优数据集
    print("\n" + "="*70)
    print("💡 数据整合建议")
    print("="*70)

    # 合并所有数据源
    merged = {}
    for db_name, db_data in [('platform', platform), ('backup_new', backup_new),
                               ('backup_old', backup_old), ('wechat', wechat)]:
        for name, school in db_data.items():
            if name not in merged:
                merged[name] = {'data': school, 'sources': [db_name]}
            else:
                merged[name]['sources'].append(db_name)

    # 统计
    single_source = [k for k, v in merged.items() if len(v['sources']) == 1]
    multi_source = [k for k, v in merged.items() if len(v['sources']) > 1]

    print(f"  合并后总学校数: {len(merged)}")
    print(f"  单一数据源: {len(single_source)} 所")
    print(f"  多数据源: {len(multi_source)} 所")

    print("\n  多数据源学校列表 (前20):")
    for name in sorted(multi_source)[:20]:
        sources = merged[name]['sources']
        print(f"    {name}: {sources}")

if __name__ == '__main__':
    analyze_differences()
