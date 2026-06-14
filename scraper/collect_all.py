import sqlite3
import subprocess
import sys
import os
from datetime import datetime

def check_db_status(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM schools")
    school_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM policies")
    policy_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT province, COUNT(*) FROM schools GROUP BY province")
    by_province = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE description IS NOT NULL AND description != ''")
    with_desc = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM schools WHERE minScore > 0")
    with_score = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'schools': school_count,
        'policies': policy_count,
        'by_province': dict(by_province),
        'with_desc': with_desc,
        'with_score': with_score
    }

def run_all_collectors():
    db_path = 'e:/aiphxt-app/ai-service/data/school_platform.db'
    
    print("=" * 70)
    print("        综合数据收集工具 - 一键运行")
    print("=" * 70)
    
    print("\n[当前数据库状态]")
    status = check_db_status(db_path)
    print(f"   学校总数: {status['schools']} 所")
    print(f"   政策总数: {status['policies']} 条")
    print(f"   有简介: {status['with_desc']} 所")
    print(f"   有分数线: {status['with_score']} 所")
    for p, c in status['by_province'].items():
        print(f"   {p}: {c} 所")
    
    print("\n" + "-" * 70)
    print("[1/3] AI大模型数据生成...")
    print("-" * 70)
    try:
        result = subprocess.run([sys.executable, 'e:/aiphxt-app/scraper/ai_generator.py'], 
                              capture_output=True, text=True, timeout=300)
        print(result.stdout)
        if result.stderr and 'error' in result.stderr.lower():
            print(f"警告: {result.stderr[:200]}")
    except Exception as e:
        print(f"AI生成失败: {e}")
    
    print("\n" + "-" * 70)
    print("[2/3] 微信公众号数据收集...")
    print("-" * 70)
    try:
        result = subprocess.run([sys.executable, 'e:/aiphxt-app/scraper/wechat_collector.py'], 
                              capture_output=True, text=True, timeout=120)
        print(result.stdout)
        if result.stderr and 'error' in result.stderr.lower():
            print(f"警告: {result.stderr[:200]}")
    except Exception as e:
        print(f"微信收集失败: {e}")
    
    print("\n" + "-" * 70)
    print("[3/3] 快速数据补充...")
    print("-" * 70)
    try:
        result = subprocess.run([sys.executable, 'e:/aiphxt-app/scraper/data_collector.py'], 
                              capture_output=True, text=True, timeout=120)
        print(result.stdout)
    except Exception as e:
        print(f"快速补充失败: {e}")
    
    print("\n" + "=" * 70)
    print("[更新后数据库状态]")
    print("=" * 70)
    status = check_db_status(db_path)
    print(f"   学校总数: {status['schools']} 所")
    print(f"   政策总数: {status['policies']} 条")
    print(f"   有简介: {status['with_desc']} 所 ({status['with_desc']/status['schools']*100:.1f}%)")
    print(f"   有分数线: {status['with_score']} 所 ({status['with_score']/status['schools']*100:.1f}%)")
    for p, c in status['by_province'].items():
        print(f"   {p}: {c} 所")
    
    print("\n" + "=" * 70)
    print(f"数据收集完成！时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == '__main__':
    run_all_collectors()
