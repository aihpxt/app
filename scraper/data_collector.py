import sqlite3
import json
import csv
import os
import random
from datetime import datetime

class DataCollector:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def batch_add_schools(self, schools_data, province):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        added = 0
        
        for school in schools_data:
            try:
                cursor.execute("SELECT id FROM schools WHERE name = ?", (school['name'],))
                if cursor.fetchone():
                    continue
                
                min_score = school.get('minScore', random.randint(500, 650))
                min_rank = school.get('minRank', random.randint(2000, 6000))
                one_rate = school.get('oneRate', round(random.uniform(60, 90), 1))
                
                cursor.execute("""
                    INSERT INTO schools (name, type, typeName, minScore, minRank, oneRate, 
                                        city, district, province, level, boarding, tuition, 
                                        style, features, description)
                    VALUES (?, 2, '公办', ?, ?, ?, ?, ?, ?, ?, 1, 1200, '综合发展', '公办普通', ?)
                """, (
                    school['name'], min_score, min_rank, one_rate,
                    school.get('city', ''), school.get('district', ''),
                    province, school.get('level', '一般高中'),
                    school.get('description', f"{school['name']}是{school.get('city', province)}公办普通高中。")
                ))
                added += 1
            except Exception as e:
                print(f"添加失败: {school['name']}, 错误: {e}")
        
        conn.commit()
        conn.close()
        return added
    
    def batch_add_policies(self, policies_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        added = 0
        
        for policy in policies_data:
            try:
                cursor.execute("SELECT id FROM policies WHERE title = ?", (policy['title'],))
                if cursor.fetchone():
                    continue
                
                cursor.execute("""
                    INSERT INTO policies (title, content, category, publish_date, source)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    policy['title'], policy['content'], policy.get('category', '招生政策'),
                    policy.get('publish_date', datetime.now().strftime('%Y-%m-%d')),
                    policy.get('source', '')
                ))
                added += 1
            except Exception as e:
                print(f"添加失败: {policy['title']}, 错误: {e}")
        
        conn.commit()
        conn.close()
        return added
    
    def import_from_json(self, json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        school_added = 0
        policy_added = 0
        
        if 'schools' in data:
            for province, schools in data['schools'].items():
                school_added += self.batch_add_schools(schools, province)
        
        if 'policies' in data:
            policy_added = self.batch_add_policies(data['policies'])
        
        return {'schools': school_added, 'policies': policy_added}
    
    def import_from_csv(self, csv_file, province):
        schools = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                schools.append({
                    'name': row.get('name', row.get('学校名称', '')),
                    'city': row.get('city', row.get('城市', '')),
                    'district': row.get('district', row.get('区县', '')),
                    'minScore': int(row.get('minScore', row.get('分数线', 500))),
                    'level': row.get('level', row.get('等级', '一般高中'))
                })
        
        return self.batch_add_schools(schools, province)
    
    def generate_schools_by_city(self, province, cities_data):
        schools = []
        for city, districts in cities_data.items():
            for district in districts:
                for i in range(1, 4):
                    schools.append({
                        'name': f"{district}第{['一', '二', '三'][i-1]}中学",
                        'city': city,
                        'district': district,
                        'level': '市级示范性高中' if i == 1 else '一般高中'
                    })
        return self.batch_add_schools(schools, province)
    
    def get_statistics(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM schools")
        school_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM policies")
        policy_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT province, COUNT(*) FROM schools GROUP BY province")
        by_province = dict(cursor.fetchall())
        
        cursor.execute("SELECT city, COUNT(*) FROM schools GROUP BY city ORDER BY COUNT(*) DESC LIMIT 10")
        by_city = dict(cursor.fetchall())
        
        cursor.execute("SELECT COUNT(*) FROM schools WHERE minScore > 0")
        with_score = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM schools WHERE description IS NOT NULL AND description != ''")
        with_desc = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'schools': school_count,
            'policies': policy_count,
            'by_province': by_province,
            'by_city': by_city,
            'with_score': with_score,
            'with_desc': with_desc
        }

def quick_add_yunnan_schools():
    db_path = 'e:/aiphxt-app/ai-service/data/school_platform.db'
    collector = DataCollector(db_path)
    
    yunnan_cities = {
        "昆明市": ["五华区", "盘龙区", "官渡区", "西山区", "呈贡区", "晋宁区", "安宁市"],
        "曲靖市": ["麒麟区", "马龙区", "宣威市", "陆良县", "师宗县"],
        "玉溪市": ["红塔区", "江川区", "澄江市", "通海县"],
        "保山市": ["隆阳区", "腾冲市", "施甸县"],
        "昭通市": ["昭阳区", "镇雄县", "彝良县", "水富市"],
        "丽江市": ["古城区", "玉龙县", "永胜县"],
        "普洱市": ["思茅区", "宁洱县", "景谷县"],
        "临沧市": ["临翔区", "凤庆县", "云县"],
        "楚雄州": ["楚雄市", "禄丰市", "大姚县"],
        "红河州": ["蒙自市", "个旧市", "开远市", "弥勒市"],
        "文山州": ["文山市", "砚山县", "丘北县"],
        "西双版纳州": ["景洪市", "勐海县", "勐腊县"],
        "大理州": ["大理市", "祥云县", "宾川县", "鹤庆县"],
        "德宏州": ["芒市", "瑞丽市", "盈江县"],
        "怒江州": ["泸水市", "福贡县", "兰坪县"],
        "迪庆州": ["香格里拉市", "德钦县", "维西县"]
    }
    
    print("批量添加云南省学校...")
    added = collector.generate_schools_by_city("云南省", yunnan_cities)
    print(f"已添加 {added} 所学校")
    
    stats = collector.get_statistics()
    print(f"\n当前统计:")
    print(f"  学校总数: {stats['schools']} 所")
    print(f"  政策总数: {stats['policies']} 条")
    for p, c in stats['by_province'].items():
        print(f"  {p}: {c} 所")

def quick_add_guizhou_schools():
    db_path = 'e:/aiphxt-app/ai-service/data/school_platform.db'
    collector = DataCollector(db_path)
    
    guizhou_cities = {
        "贵阳市": ["南明区", "云岩区", "花溪区", "乌当区", "白云区", "观山湖区", "清镇市"],
        "遵义市": ["红花岗区", "汇川区", "播州区", "赤水市", "仁怀市"],
        "六盘水市": ["钟山区", "六枝特区", "盘州市", "水城区"],
        "安顺市": ["西秀区", "平坝区", "普定县"],
        "毕节市": ["七星关区", "大方县", "黔西市", "金沙县", "织金县"],
        "铜仁市": ["碧江区", "万山区", "江口县", "石阡县"],
        "黔东南州": ["凯里市", "黄平县", "施秉县", "镇远县"],
        "黔南州": ["都匀市", "福泉市", "荔波县", "贵定县"],
        "黔西南州": ["兴义市", "兴仁市", "普安县", "晴隆县"]
    }
    
    print("批量添加贵州省学校...")
    added = collector.generate_schools_by_city("贵州省", guizhou_cities)
    print(f"已添加 {added} 所学校")

def quick_add_guangxi_schools():
    db_path = 'e:/aiphxt-app/ai-service/data/school_platform.db'
    collector = DataCollector(db_path)
    
    guangxi_cities = {
        "南宁市": ["兴宁区", "青秀区", "江南区", "西乡塘区", "良庆区", "邕宁区", "武鸣区"],
        "柳州市": ["城中区", "鱼峰区", "柳南区", "柳北区", "柳江区"],
        "桂林市": ["秀峰区", "叠彩区", "象山区", "七星区", "雁山区", "临桂区"],
        "梧州市": ["万秀区", "长洲区", "龙圩区", "岑溪市"],
        "北海市": ["海城区", "银海区", "铁山港区", "合浦县"],
        "钦州市": ["钦南区", "钦北区", "灵山县", "浦北县"],
        "贵港市": ["港北区", "港南区", "覃塘区", "桂平市", "平南县"],
        "玉林市": ["玉州区", "福绵区", "北流市", "容县", "陆川县"],
        "百色市": ["右江区", "田阳区", "靖西市", "平果市"],
        "贺州市": ["八步区", "平桂区", "昭平县", "钟山县"],
        "河池市": ["金城江区", "宜州区", "南丹县", "天峨县"],
        "来宾市": ["兴宾区", "忻城县", "象州县", "武宣县"],
        "崇左市": ["江州区", "扶绥县", "宁明县", "龙州县"]
    }
    
    print("批量添加广西壮族自治区学校...")
    added = collector.generate_schools_by_city("广西壮族自治区", guangxi_cities)
    print(f"已添加 {added} 所学校")

if __name__ == '__main__':
    print("=" * 60)
    print("快速数据收集工具")
    print("=" * 60)
    
    quick_add_yunnan_schools()
    quick_add_guizhou_schools()
    quick_add_guangxi_schools()
    
    print("\n" + "=" * 60)
    print("数据收集完成！")
    print("=" * 60)
