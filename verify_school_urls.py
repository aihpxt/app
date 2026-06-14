#!/usr/bin/env python3
"""验证学校网址有效性的爬虫脚本"""

import sqlite3
import os
import asyncio
import aiohttp
from datetime import datetime

async def check_url(session, url, timeout=10):
    """检查单个URL是否可访问"""
    if not url:
        return False, "URL为空"
    
    # 确保URL以http/https开头
    if not url.startswith('http'):
        url = f'http://{url}'
    
    try:
        async with session.get(url, timeout=timeout, allow_redirects=True) as response:
            if response.status in [200, 301, 302]:
                return True, f"状态码: {response.status}"
            else:
                return False, f"状态码: {response.status}"
    except asyncio.TimeoutError:
        return False, "超时"
    except aiohttp.ClientError as e:
        return False, f"连接错误: {str(e)[:30]}"
    except Exception as e:
        return False, f"未知错误: {str(e)[:30]}"

async def main():
    db_path = os.path.join('ai-service', 'data', 'school_platform.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.execute('SELECT id, name, website FROM schools WHERE website IS NOT NULL AND website != ""')
    rows = cursor.fetchall()
    conn.close()
    
    print(f"共找到 {len(rows)} 所学校需要验证")
    
    results = []
    timeout = aiohttp.ClientTimeout(total=15)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = []
        for id, name, website in rows:
            task = asyncio.create_task(check_url(session, website))
            tasks.append((id, name, website, task))
        
        for id, name, website, task in tasks:
            success, message = await task
            results.append({
                'id': id,
                'name': name,
                'website': website,
                'success': success,
                'message': message
            })
            
            # 每10个输出一次进度
            if len(results) % 10 == 0:
                success_count = sum(1 for r in results if r['success'])
                print(f"已验证 {len(results)}/{len(rows)} 所学校, 有效: {success_count}")
    
    # 统计结果
    success_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - success_count
    
    print("\n" + "="*60)
    print(f"验证完成!")
    print(f"总学校数: {len(results)}")
    print(f"有效网址: {success_count} ({(success_count/len(results)):.1%})")
    print(f"无效网址: {failed_count} ({(failed_count/len(results)):.1%})")
    
    # 输出无效网址列表
    if failed_count > 0:
        print("\n无效网址列表:")
        for r in results[:20] if failed_count > 20 else results:
            if not r['success']:
                print(f"  {r['name']}: {r['website']} - {r['message']}")
    
    # 保存结果到文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f'url_verification_{timestamp}.txt', 'w', encoding='utf-8') as f:
        f.write("学校网址验证结果\n")
        f.write("="*60 + "\n")
        f.write(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总学校数: {len(results)}\n")
        f.write(f"有效网址: {success_count}\n")
        f.write(f"无效网址: {failed_count}\n")
        f.write("="*60 + "\n")
        f.write("详细结果:\n\n")
        
        for r in results:
            status = "✓ 有效" if r['success'] else "✗ 无效"
            f.write(f"{status} | {r['name']}\n")
            f.write(f"    URL: {r['website']}\n")
            f.write(f"    原因: {r['message']}\n\n")
    
    print(f"\n详细结果已保存到: url_verification_{timestamp}.txt")

if __name__ == "__main__":
    asyncio.run(main())