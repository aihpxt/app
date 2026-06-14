import sqlite3
import subprocess
import sys
import os

def install_dependencies():
    packages = ['requests', 'beautifulsoup4']
    for package in packages:
        try:
            if package == 'beautifulsoup4':
                __import__('bs4')
            else:
                __import__(package)
        except ImportError:
            print(f"安装依赖: {package}")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])

def check_db_status(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM schools")
    school_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM policies")
    policy_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT province, COUNT(*) FROM schools GROUP BY province")
    by_province = cursor.fetchall()
    
    conn.close()
    
    return {
        'schools': school_count,
        'policies': policy_count,
        'by_province': dict(by_province)
    }

def run_all_scrapers():
    db_path = 'e:/aiphxt-app/ai-service/data/school_platform.db'
    
    print("=" * 70)
    print("一键数据收集工具")
    print("=" * 70)
    
    print("\n检查依赖...")
    install_dependencies()
    
    print("\n当前数据库状态:")
    status = check_db_status(db_path)
    print(f"   学校总数: {status['schools']} 所")
    print(f"   政策总数: {status['policies']} 条")
    for province, count in status['by_province'].items():
        print(f"   {province}: {count} 所")
    
    print("\n" + "=" * 70)
    print("1. 运行网络爬虫...")
    print("=" * 70)
    try:
        result = subprocess.run([sys.executable, 'e:/aiphxt-app/scraper/school_scraper.py'], 
                              capture_output=True, text=True, timeout=120)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except Exception as e:
        print(f"网络爬虫运行失败: {e}")
    
    print("\n" + "=" * 70)
    print("2. 运行微信公众号抓取...")
    print("=" * 70)
    try:
        result = subprocess.run([sys.executable, 'e:/aiphxt-app/scraper/wechat_scraper.py'], 
                              capture_output=True, text=True, timeout=120)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except Exception as e:
        print(f"微信公众号抓取失败: {e}")
    
    print("\n" + "=" * 70)
    print("更新后数据库状态:")
    print("=" * 70)
    status = check_db_status(db_path)
    print(f"   学校总数: {status['schools']} 所")
    print(f"   政策总数: {status['policies']} 条")
    for province, count in status['by_province'].items():
        print(f"   {province}: {count} 所")
    
    print("\n数据收集完成！")

if __name__ == '__main__':
    run_all_scrapers()
