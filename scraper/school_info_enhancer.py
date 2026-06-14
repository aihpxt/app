import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import time
import random
from urllib.parse import quote

class SchoolInfoEnhancer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def rotate_user_agent(self):
        self.session.headers['User-Agent'] = random.choice(self.user_agents)
    
    def scrape_baidu_baike(self, school_name):
        """抓取百度百科学校详情"""
        url = f'https://baike.baidu.com/item/{quote(school_name)}'
        info = {}
        
        try:
            self.rotate_user_agent()
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 获取简介
            summary = soup.find('div', class_='lemma-summary')
            if summary:
                info['description'] = summary.get_text().strip()[:800]
            
            # 获取基本信息表
            info_table = soup.find('div', class_='basic-info')
            if info_table:
                dt_list = info_table.find_all('dt', class_='basicInfo-item name')
                for dt in dt_list:
                    key = dt.get_text().strip()
                    dd = dt.find_next_sibling('dd', class_='basicInfo-item value')
                    if dd:
                        value = dd.get_text().strip()
                        if '地址' in key:
                            info['address'] = value[:100]
                        elif '电话' in key or '联系电话' in key:
                            info['phone'] = value.replace('\n', '').replace(' ', '')[:50]
                        elif '官网' in key or '网址' in key:
                            info['website'] = value
                        elif '主管部门' in key:
                            info['department'] = value[:50]
                        elif '创办时间' in key:
                            info['founded_year'] = value
                        elif '学校类型' in key:
                            info['school_type'] = value[:50]
                        elif '办学性质' in key:
                            if '公办' in value:
                                info['is_public'] = 1
                            else:
                                info['is_public'] = 0
        
            # 获取学校特色
            features_section = soup.find('div', id='t_feature')
            if features_section:
                features = features_section.find_next('div', class_='para')
                if features:
                    info['features'] = features.get_text().strip()[:200]
            
            self.random_delay(1, 2)
        except Exception as e:
            print(f"抓取百度百科失败: {school_name}, 错误: {e}")
        
        return info
    
    def scrape_gaokao_info(self, school_name):
        """抓取高考网学校信息"""
        url = f'https://www.gaokao.cn/school/search?keyword={quote(school_name)}'
        info = {}
        
        try:
            self.rotate_user_agent()
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            school_card = soup.find('div', class_='school-card')
            if school_card:
                # 获取学校简介
                intro = school_card.find('div', class_='school-intro')
                if intro:
                    info['description'] = intro.get_text().strip()[:500]
                
                # 获取联系方式
                contact = school_card.find('div', class_='contact-info')
                if contact:
                    phone = contact.find('span', class_='phone')
                    if phone:
                        info['phone'] = phone.get_text().strip()[:50]
                    address = contact.find('span', class_='address')
                    if address:
                        info['address'] = address.get_text().strip()[:100]
            
            self.random_delay()
        except Exception as e:
            print(f"抓取高考网失败: {school_name}, 错误: {e}")
        
        return info
    
    def scrape_school_detail(self, school_name):
        """综合多个来源获取学校详情"""
        info = {}
        
        # 优先从百度百科获取
        baike_info = self.scrape_baidu_baike(school_name)
        info.update(baike_info)
        
        # 如果百度百科没有获取到足够信息，尝试高考网
        if not info.get('address') or not info.get('description'):
            gaokao_info = self.scrape_gaokao_info(school_name)
            if not info.get('address') and gaokao_info.get('address'):
                info['address'] = gaokao_info['address']
            if not info.get('description') and gaokao_info.get('description'):
                info['description'] = gaokao_info['description']
        
        return info
    
    def enhance_school_info(self):
        """增强数据库中学校的详细信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取需要补充信息的学校（没有网址或简介的）
        cursor.execute("""
            SELECT id, name FROM schools 
            WHERE province = '云南省' 
            AND (website IS NULL OR website = '' OR website = 'http://www.example.com')
            ORDER BY RANDOM() LIMIT 30
        """)
        schools = cursor.fetchall()
        
        print(f"发现 {len(schools)} 所学校需要补充信息")
        
        updated_count = 0
        failed_count = 0
        
        for school_id, name in schools:
            print(f"\n正在处理: {name}")
            
            try:
                info = self.scrape_school_detail(name)
                
                if info:
                    update_fields = []
                    update_params = []
                    
                    if info.get('address'):
                        update_fields.append("address = ?")
                        update_params.append(info['address'])
                    if info.get('phone'):
                        update_fields.append("phone = ?")
                        update_params.append(info['phone'])
                    if info.get('website'):
                        update_fields.append("website = ?")
                        update_params.append(info['website'])
                    if info.get('description'):
                        update_fields.append("description = ?")
                        update_params.append(info['description'])
                    if info.get('features'):
                        update_fields.append("features = ?")
                        update_params.append(info['features'])
                    if 'is_public' in info:
                        update_fields.append("is_public = ?")
                        update_params.append(info['is_public'])
                    
                    if update_fields:
                        update_params.append(school_id)
                        cursor.execute(f"UPDATE schools SET {', '.join(update_fields)} WHERE id = ?", update_params)
                        updated_count += 1
                        print(f"   ✅ 成功更新")
                    else:
                        print(f"   ⚠️ 未获取到新信息")
                else:
                    print(f"   ❌ 未获取到信息")
                    failed_count += 1
            
            except Exception as e:
                print(f"   ❌ 处理失败: {e}")
                failed_count += 1
        
        conn.commit()
        conn.close()
        
        return updated_count, failed_count
    
    def run(self):
        print("=" * 60)
        print("学校信息增强爬虫启动")
        print("=" * 60)
        
        updated, failed = self.enhance_school_info()
        
        print("\n" + "=" * 60)
        print("爬虫任务完成！")
        print(f"成功更新: {updated} 所学校")
        print(f"获取失败: {failed} 所学校")
        print("=" * 60)

if __name__ == '__main__':
    db_path = r'e:\aiphxt-app\ai-service\data\school_platform.db'
    enhancer = SchoolInfoEnhancer(db_path)
    enhancer.run()
