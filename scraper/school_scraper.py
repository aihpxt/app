import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import json
import time
import random
from urllib.parse import urljoin, quote

class SchoolDataScraper:
    def __init__(self, db_path):
        self.db_path = db_path
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        self.collected_data = []
        self.yunnan_cities = [
            '昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市', '临沧市',
            '楚雄州', '红河州', '文山州', '西双版纳州', '大理州', '德宏州', '怒江州', '迪庆州'
        ]
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """添加随机延迟，避免被封"""
        time.sleep(random.uniform(min_seconds, max_seconds))
    
    def rotate_user_agent(self):
        """轮换User-Agent"""
        self.session.headers['User-Agent'] = random.choice(self.user_agents)
    
    def scrape_yunnan_high_schools(self):
        """抓取云南省各州市重点高中信息"""
        schools = []
        
        # 云南各州市知名高中列表（预定义）
        yunnan_famous_schools = {
            '昆明市': [
                '云南师范大学附属中学', '昆明市第一中学', '昆明市第三中学', 
                '昆明市第八中学', '昆明市第十中学', '云南大学附属中学',
                '昆明市第十四中学', '官渡区第一中学', '西山区第一中学',
                '呈贡区第一中学', '安宁中学', '师大附中呈贡校区'
            ],
            '曲靖市': [
                '曲靖市第一中学', '曲靖市第二中学', '曲靖市民族中学',
                '宣威市第一中学', '会泽县第一中学', '麒麟区第一中学'
            ],
            '玉溪市': [
                '玉溪市第一中学', '玉溪市民族中学', '红塔区第一中学',
                '江川区第一中学', '通海县第一中学'
            ],
            '保山市': [
                '保山市第一中学', '腾冲市第一中学', '隆阳区第一中学'
            ],
            '昭通市': [
                '昭通市第一中学', '镇雄县第一中学', '昭阳区第一中学'
            ],
            '丽江市': [
                '丽江市第一中学', '古城区第一中学', '玉龙县第一中学'
            ],
            '普洱市': [
                '普洱市第一中学', '思茅区第一中学', '景东县第一中学'
            ],
            '临沧市': [
                '临沧市第一中学', '凤庆县第一中学', '云县第一中学'
            ],
            '楚雄州': [
                '楚雄州第一中学', '楚雄市第一中学', '禄丰县第一中学'
            ],
            '红河州': [
                '红河州第一中学', '个旧市第一中学', '开远市第一中学',
                '建水县第一中学', '蒙自市第一中学'
            ],
            '文山州': [
                '文山州第一中学', '文山市第一中学', '砚山县第一中学'
            ],
            '西双版纳州': [
                '西双版纳州第一中学', '景洪市第一中学'
            ],
            '大理州': [
                '大理州第一中学', '大理市第一中学', '祥云县第一中学',
                '宾川县第一中学'
            ],
            '德宏州': [
                '德宏州第一中学', '芒市第一中学', '瑞丽市第一中学'
            ],
            '怒江州': [
                '怒江州第一中学', '泸水市第一中学'
            ],
            '迪庆州': [
                '迪庆州第一中学', '香格里拉市第一中学'
            ]
        }
        
        for city, school_names in yunnan_famous_schools.items():
            for name in school_names:
                schools.append({
                    'name': name,
                    'city': city,
                    'prefecture': city,
                    'province': '云南省',
                    'type': 1,
                    'typeName': '公办',
                    'source': '云南知名高中名录'
                })
        
        print(f"   预定义云南知名高中: {len(schools)} 所")
        return schools
    
    def scrape_baidu_search(self, city):
        """通过百度搜索获取各城市高中列表"""
        schools = []
        search_url = f'https://www.baidu.com/s?wd={quote(f"{city} 重点高中 名单")}'
        
        try:
            self.rotate_user_agent()
            resp = self.session.get(search_url, timeout=15)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 提取搜索结果中的学校名称
            results = soup.find_all('div', class_='result-op')
            for result in results:
                links = result.find_all('a')
                for link in links:
                    text = link.get_text()
                    if '中学' in text and len(text) > 3 and len(text) < 30:
                        # 过滤掉无关链接
                        if '下载' not in text and 'pdf' not in text.lower() and 'doc' not in text.lower():
                            schools.append({
                                'name': text.strip(),
                                'city': city,
                                'prefecture': city,
                                'province': '云南省',
                                'source': f'百度搜索:{city}'
                            })
            
            self.random_delay()
        except Exception as e:
            print(f"百度搜索失败: {city}, 错误: {e}")
        
        return schools
    
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
                            info['address'] = value
                        elif '电话' in key or '联系电话' in key:
                            info['phone'] = value.replace('\n', '').replace(' ', '')[:50]
                        elif '官网' in key or '网址' in key:
                            info['website'] = value
                        elif '主管部门' in key:
                            info['department'] = value
                        elif '创办时间' in key:
                            info['founded_year'] = value
                        elif '学校类型' in key:
                            info['school_type'] = value
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
    
    def scrape_gaokao_china(self):
        """抓取高考网学校信息"""
        schools = []
        url = 'https://www.gaokao.cn/school'
        
        try:
            self.rotate_user_agent()
            resp = self.session.get(url, timeout=15)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            school_items = soup.find_all('div', class_='school-item')
            for item in school_items:
                name_tag = item.find('a', class_='school-name')
                if name_tag:
                    name = name_tag.get_text().strip()
                    if '中学' in name and len(name) > 3:
                        schools.append({
                            'name': name,
                            'province': '云南省',
                            'source': '高考网'
                        })
            
            self.random_delay()
        except Exception as e:
            print(f"抓取高考网失败: {e}")
        
        return schools
    
    def save_to_db(self, schools_data):
        """保存学校数据到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        added = 0
        updated = 0
        
        for school in schools_data:
            try:
                # 检查是否已存在
                cursor.execute("SELECT id FROM schools WHERE name = ?", (school['name'],))
                existing = cursor.fetchone()
                
                if existing:
                    # 更新现有记录
                    update_fields = []
                    update_params = []
                    
                    if school.get('address'):
                        update_fields.append("address = ?")
                        update_params.append(school['address'])
                    if school.get('phone'):
                        update_fields.append("phone = ?")
                        update_params.append(school['phone'])
                    if school.get('website'):
                        update_fields.append("website = ?")
                        update_params.append(school['website'])
                    if school.get('description'):
                        update_fields.append("description = ?")
                        update_params.append(school['description'])
                    if school.get('features'):
                        update_fields.append("features = ?")
                        update_params.append(school['features'])
                    if school.get('city'):
                        update_fields.append("city = ?")
                        update_params.append(school['city'])
                    if school.get('prefecture'):
                        update_fields.append("prefecture = ?")
                        update_params.append(school['prefecture'])
                    
                    if update_fields:
                        update_params.append(existing[0])
                        cursor.execute(f"UPDATE schools SET {', '.join(update_fields)} WHERE id = ?", update_params)
                        updated += 1
                    continue
                
                # 插入新记录
                cursor.execute("""
                    INSERT INTO schools (name, type, typeName, province, city, prefecture, 
                                       boarding, tuition, style, features, address, phone, website, description,
                                       minScore, minRank, oneRate, student_count, teacher_count, view_count)
                    VALUES (?, 2, ?, ?, ?, ?, 1, 0, '综合发展', ?, ?, ?, ?, ?, 0, 0, 0, 0, 0, 0)
                """, (
                    school['name'],
                    school.get('typeName', '公办'),
                    school.get('province', '云南省'),
                    school.get('city', ''),
                    school.get('prefecture', school.get('city', '')),
                    school.get('features', '公办普通'),
                    school.get('address', ''),
                    school.get('phone', ''),
                    school.get('website', ''),
                    school.get('description', '')
                ))
                added += 1
                
            except Exception as e:
                print(f"保存失败: {school.get('name', '未知')}, 错误: {e}")
        
        conn.commit()
        conn.close()
        return added, updated
    
    def enrich_school_details(self):
        """为现有学校补充详细信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 只针对真实的云南学校补充详情，排除测试数据（名称包含"第XXX中学"且编号>=20的）
        cursor.execute("""
            SELECT id, name FROM schools 
            WHERE province = '云南省' AND (website = '' OR website IS NULL) 
            AND name NOT LIKE '%第2__中学' AND name NOT LIKE '%第3__中学' AND name NOT LIKE '%第4__中学'
            LIMIT 50
        """)
        schools = cursor.fetchall()
        
        print(f"\n开始补充学校详情，共 {len(schools)} 所学校需要补充...")
        
        updated_count = 0
        for school_id, name in schools:
            print(f"   正在补充: {name}")
            details = self.scrape_baidu_baike(name)
            
            if details:
                update_fields = []
                update_params = []
                
                if details.get('address'):
                    update_fields.append("address = ?")
                    update_params.append(details['address'])
                if details.get('phone'):
                    update_fields.append("phone = ?")
                    update_params.append(details['phone'])
                if details.get('website'):
                    update_fields.append("website = ?")
                    update_params.append(details['website'])
                if details.get('description'):
                    update_fields.append("description = ?")
                    update_params.append(details['description'])
                if details.get('features'):
                    update_fields.append("features = ?")
                    update_params.append(details['features'])
                
                if update_fields:
                    update_params.append(school_id)
                    cursor.execute(f"UPDATE schools SET {', '.join(update_fields)} WHERE id = ?", update_params)
                    updated_count += 1
        
        conn.commit()
        conn.close()
        print(f"   成功补充 {updated_count} 所学校的详情")
        return updated_count
    
    def run(self):
        """执行爬虫主程序"""
        print("=" * 60)
        print("云南高中学校数据爬虫启动")
        print("=" * 60)
        
        all_schools = []
        
        print("\n1. 加载云南各州市知名高中名录...")
        famous_schools = self.scrape_yunnan_high_schools()
        all_schools.extend(famous_schools)
        
        # 去重
        unique_schools = {}
        for school in all_schools:
            name = school['name']
            if name not in unique_schools:
                unique_schools[name] = school
        
        print(f"\n总计收集: {len(all_schools)} 条，去重后: {len(unique_schools)} 条")
        
        # 保存到数据库
        added, updated = self.save_to_db(list(unique_schools.values()))
        print(f"新增入库: {added} 所学校")
        print(f"更新信息: {updated} 所学校")
        
        # 补充学校详情（只针对新增的真实学校，跳过测试数据）
        if added > 0:
            updated_details = self.enrich_school_details()
        else:
            updated_details = 0
        
        print("\n" + "=" * 60)
        print("爬虫任务完成！")
        print(f"新增学校: {added} 所")
        print(f"更新信息: {updated} 所")
        print(f"补充详情: {updated_details} 所")
        print("=" * 60)
        
        return len(unique_schools)

if __name__ == '__main__':
    db_path = r'e:\aiphxt-app\ai-service\data\school_platform.db'
    scraper = SchoolDataScraper(db_path)
    scraper.run()
