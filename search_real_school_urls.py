#!/usr/bin/env python3
"""搜索真实学校网址"""

import sqlite3
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin

async def search_school_url(session, school_name):
    """搜索学校官网"""
    search_url = f"https://www.baidu.com/s?wd={school_name} 官网"
    
    try:
        async with session.get(search_url, timeout=10) as response:
            if response.status != 200:
                return None
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            for result in soup.find_all('div', class_='result-op'):
                link = result.find('a')
                if link and 'href' in link.attrs:
                    url = link['href']
                    # 尝试获取真实URL（百度跳转链接）
                    if url.startswith('/link?url='):
                        continue
                    # 检查是否是教育相关域名
                    if any(domain in url.lower() for domain in ['edu.cn', 'school', 'zhongxue', 'highschool']):
                        return url
                    
            # 搜索普通结果
            for result in soup.find_all('h3', class_='t'):
                link = result.find('a')
                if link and 'href' in link.attrs:
                    url = link['href']
                    if url.startswith('http') and ('edu.cn' in url or school_name[0:2] in url):
                        return url
                        
            return None
    except Exception as e:
        return None

async def main():
    db_path = os.path.join('ai-service', 'data', 'school_platform.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.execute('SELECT id, name, website FROM schools WHERE website IS NOT NULL')
    rows = cursor.fetchall()
    conn.close()
    
    print(f"共找到 {len(rows)} 所学校")
    
    timeout = aiohttp.ClientTimeout(total=30)
    updated_count = 0
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        conn = sqlite3.connect(db_path)
        
        for i, (id, name, website) in enumerate(rows):
            if i > 50:  # 先测试前50所学校
                break
                
            # 跳过已有有效网址的学校
            if website and (website.startswith('http') or '.' in website):
                continue
                
            print(f"正在搜索: {name}")
            real_url = await search_school_url(session, name)
            
            if real_url:
                print(f"  找到: {real_url}")
                conn.execute('UPDATE schools SET website = ? WHERE id = ?', (real_url, id))
                updated_count += 1
            else:
                print(f"  未找到")
                
        conn.commit()
        conn.close()
    
    print(f"\n搜索完成! 找到 {updated_count} 个真实网址")

if __name__ == "__main__":
    asyncio.run(main())