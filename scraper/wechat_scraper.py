import requests
import sqlite3
import re
import json
import time
import hashlib
import os

class WeChatScraper:
    def __init__(self, db_path):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.policies = []
    
    def get_wechat_articles(self, keyword, max_count=20):
        articles = []
        search_urls = [
            f'https://weixin.sogou.com/weixin?type=2&query={keyword}&ie=utf8',
        ]
        
        for url in search_urls:
            try:
                resp = self.session.get(url, timeout=15)
                resp.encoding = 'utf-8'
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.find_all('div', class_='vrwrap')
                
                for item in items[:max_count]:
                    try:
                        title_elem = item.find('a')
                        if not title_elem:
                            continue
                        title = title_elem.get_text().strip()
                        link = title_elem.get('href', '')
                        
                        if not link.startswith('http'):
                            link = 'https://weixin.sogou.com' + link
                        
                        article = {
                            'title': title,
                            'url': link,
                            'keyword': keyword,
                            'publish_date': ''
                        }
                        
                        time_elem = item.find('span', class_='time')
                        if time_elem:
                            article['publish_date'] = time_elem.get_text().strip()
                        
                        articles.append(article)
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"搜索失败: {keyword}, 错误: {e}")
            
            time.sleep(2)
        
        return articles
    
    def extract_school_info(self, article):
        info = {'schools': [], 'scores': [], 'policies': []}
        
        title = article.get('title', '')
        content_url = article.get('url', '')
        
        if '中考' in title or '招生' in title or '分数线' in title:
            schools = re.findall(r'([\u4e00-\u9fa5]{4,10}(?:中学|高中|学校))', title)
            info['schools'].extend(schools)
            
            scores = re.findall(r'(\d{2,3})分', title)
            info['scores'].extend(scores)
            
            if '政策' in title:
                info['policies'].append(title)
        
        try:
            resp = self.session.get(content_url, timeout=15)
            resp.encoding = 'utf-8'
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            content = soup.find('div', id='js_content') or soup.find('div', class_='rich_media_content')
            if content:
                text = content.get_text()
                
                school_names = re.findall(r'([\u4e00-\u9fa5]{4,10}(?:中学|高中|学校))', text)
                info['schools'].extend(school_names)
                
                score_patterns = re.findall(r'录取分数[线为]?[:：]?\s*(\d{2,3})', text)
                info['scores'].extend(score_patterns)
                
                policies = re.findall(r'([\u4e00-\u9fa5]{10,30}政策[\u4e00-\u9fa5]*)', text)
                info['policies'].extend(policies)
                
        except Exception as e:
            print(f"提取文章内容失败: {content_url}, 错误: {e}")
        
        info['schools'] = list(set(info['schools']))[:10]
        info['scores'] = list(set(info['scores']))[:5]
        info['policies'] = list(set(info['policies']))[:3]
        
        return info
    
    def scrape_education_wechat(self):
        keywords = [
            '昆明中考招生',
            '云南中考分数线',
            '贵州中考政策',
            '广西中考招生',
            '高中录取分数线',
            '中考志愿填报',
            '云南教育',
            '贵州教育',
            '广西教育'
        ]
        
        all_articles = []
        
        print("\n搜索微信公众号文章...")
        for keyword in keywords:
            print(f"  搜索: {keyword}")
            articles = self.get_wechat_articles(keyword, max_count=10)
            all_articles.extend(articles)
            time.sleep(1)
        
        print(f"\n共获取 {len(all_articles)} 篇文章")
        
        collected_data = []
        for i, article in enumerate(all_articles[:30]):
            print(f"  处理文章 {i+1}/{min(len(all_articles), 30)}: {article['title'][:30]}...")
            info = self.extract_school_info(article)
            
            if info['schools'] or info['policies']:
                collected_data.append({
                    'article': article,
                    'info': info
                })
        
        return collected_data
    
    def save_policies_to_db(self, policies_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        added = 0
        
        for item in policies_data:
            info = item['info']
            article = item['article']
            
            if info['policies']:
                for policy_title in info['policies']:
                    try:
                        cursor.execute("SELECT id FROM policies WHERE title = ?", (policy_title,))
                        if cursor.fetchone():
                            continue
                        
                        cursor.execute("""
                            INSERT INTO policies (title, content, category, publish_date, source)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            policy_title,
                            f"来源：微信公众号\n\n{article.get('title', '')}\n\n{article.get('url', '')}",
                            '招生政策',
                            article.get('publish_date', ''),
                            article.get('keyword', '微信公众号')
                        ))
                        added += 1
                    except Exception as e:
                        pass
        
        conn.commit()
        conn.close()
        return added
    
    def save_schools_to_db(self, schools_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        added = 0
        
        existing_schools = set()
        cursor.execute("SELECT name FROM schools")
        for row in cursor.fetchall():
            existing_schools.add(row[0])
        
        for item in schools_data:
            info = item['info']
            article = item['article']
            
            for school_name in info['schools']:
                if school_name in existing_schools:
                    continue
                if len(school_name) < 4:
                    continue
                
                try:
                    province = '云南省'
                    if '贵州' in article.get('title', ''):
                        province = '贵州省'
                    elif '广西' in article.get('title', ''):
                        province = '广西壮族自治区'
                    
                    cursor.execute("""
                        INSERT INTO schools (name, type, typeName, province, style, features, description)
                        VALUES (?, 2, '公办', ?, '综合发展', '公办普通', ?)
                    """, (school_name, province, f"来源：{article.get('title', '')}"))
                    existing_schools.add(school_name)
                    added += 1
                except Exception as e:
                    pass
        
        conn.commit()
        conn.close()
        return added
    
    def run(self):
        print("=" * 60)
        print("开始微信公众号数据收集")
        print("=" * 60)
        
        collected = self.scrape_education_wechat()
        
        print(f"\n收集到 {len(collected)} 条有效数据")
        
        policy_added = self.save_policies_to_db(collected)
        print(f"新增政策: {policy_added} 条")
        
        school_added = self.save_schools_to_db(collected)
        print(f"新增学校: {school_added} 所")
        
        return collected

if __name__ == '__main__':
    db_path = 'e:/aiphxt-app/ai-service/data/school_platform.db'
    scraper = WeChatScraper(db_path)
    scraper.run()
