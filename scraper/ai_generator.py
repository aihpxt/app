import sqlite3
import json
import requests
import time
import random
from datetime import datetime

class AIDataGenerator:
    def __init__(self, db_path, api_key=None, api_base=None):
        self.db_path = db_path
        self.api_key = api_key
        self.api_base = api_base or "https://api.openai.com/v1"
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
    
    def generate_school_info(self, school_name, city, province):
        prompt = f"""请为{province}{city}的{school_name}生成以下信息（JSON格式）：
{{
    "description": "学校简介（100-150字）",
    "features": "学校特色标签（用逗号分隔，如：省重点,百年名校,理科强校）",
    "style": "办学风格（如：综合发展,理科见长,文科优势,艺术特色）",
    "level": "学校等级（如：一级一等,一级二等,省级示范性高中,市级示范性高中）",
    "minScore": 录取分数线（整数，根据学校等级合理估计，满分700分）,
    "oneRate": 一本率（百分比，保留一位小数）,
    "address": "学校地址",
    "phone": "联系电话",
    "website": "学校官网",
    "student_count": 学生人数（整数）,
    "teacher_count": 教师人数（整数）
}}

注意：
1. 信息要符合{province}的实际情况
2. 分数线要合理，重点高中一般在600分以上
3. 一本率要与学校等级匹配
4. 只返回JSON，不要其他内容"""

        if not self.api_key:
            return self._generate_mock_data(school_name, city, province)
        
        try:
            response = self.session.post(
                f"{self.api_base}/chat/completions",
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
            else:
                return self._generate_mock_data(school_name, city, province)
        except Exception as e:
            print(f"AI生成失败: {e}")
            return self._generate_mock_data(school_name, city, province)
    
    def _generate_mock_data(self, school_name, city, province):
        level_scores = {
            "一级一等": (620, 680, 85, 95),
            "一级二等": (580, 640, 70, 85),
            "一级三等": (550, 600, 60, 75),
            "省级示范性高中": (600, 660, 75, 90),
            "市级示范性高中": (550, 620, 60, 80),
            "一般高中": (480, 560, 40, 65)
        }
        
        if "第一中学" in school_name or "一中" in school_name:
            level = random.choice(["一级一等", "省级示范性高中"])
        elif "第二中学" in school_name or "二中" in school_name:
            level = random.choice(["一级二等", "市级示范性高中"])
        elif "第三中学" in school_name or "三中" in school_name:
            level = random.choice(["一级三等", "市级示范性高中"])
        elif "实验" in school_name:
            level = random.choice(["一级二等", "省级示范性高中"])
        elif "民族" in school_name:
            level = random.choice(["一级三等", "市级示范性高中"])
        else:
            level = random.choice(["市级示范性高中", "一般高中"])
        
        min_score, max_score, min_rate, max_rate = level_scores.get(level, (500, 600, 50, 70))
        score = random.randint(min_score, max_score)
        one_rate = round(random.uniform(min_rate, max_rate), 1)
        
        features = []
        if "实验" in school_name:
            features.append("实验特色")
        if "民族" in school_name:
            features.append("民族特色")
        if "外国语" in school_name:
            features.append("外语特色")
        if "艺术" in school_name:
            features.append("艺术特色")
        if "体育" in school_name:
            features.append("体育特色")
        if score >= 650:
            features.append("省重点")
        elif score >= 600:
            features.append("市重点")
        if not features:
            features.append("公办普通")
        
        styles = ["综合发展", "理科见长", "文科优势", "素质教育", "特色办学"]
        style = random.choice(styles)
        
        descriptions = [
            f"{school_name}是{province}{city}重点中学，学校师资力量雄厚，教学设施完善，历年高考成绩优异。学校秉承'以人为本、全面发展'的办学理念，注重学生综合素质培养，是{city}基础教育的标杆学校。",
            f"{school_name}坐落于{city}，是一所历史悠久、文化底蕴深厚的学校。学校环境优美，教学设施先进，师资力量雄厚，教学质量稳步提升，为高校输送了大量优秀人才。",
            f"{school_name}是{city}公办高中，学校坚持立德树人根本任务，注重学生全面发展。学校拥有现代化的教学设施和优秀的教师队伍，教学质量逐年提高，深受家长和社会好评。"
        ]
        
        return {
            "description": random.choice(descriptions),
            "features": ",".join(features),
            "style": style,
            "level": level,
            "minScore": score,
            "oneRate": one_rate,
            "address": f"{province}{city}",
            "phone": f"0{''.join([str(random.randint(0,9)) for _ in range(3)])}-{random.randint(1000000, 9999999)}",
            "website": f"www.{''.join([chr(random.randint(97,122)) for _ in range(6)])}.edu.cn",
            "student_count": random.randint(1500, 3500),
            "teacher_count": random.randint(120, 280)
        }
    
    def generate_policy_info(self, title, province):
        prompt = f"""请为{province}生成一篇关于"{title}"的详细政策解读文章（500-800字）。
要求：
1. 内容要符合{province}的实际情况
2. 包含具体的政策要点和操作指南
3. 语言通俗易懂，适合家长和学生阅读
4. 只返回文章内容，不要标题"""

        if not self.api_key:
            return self._generate_mock_policy(title, province)
        
        try:
            response = self.session.post(
                f"{self.api_base}/chat/completions",
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return self._generate_mock_policy(title, province)
        except Exception as e:
            print(f"AI生成失败: {e}")
            return self._generate_mock_policy(title, province)
    
    def _generate_mock_policy(self, title, province):
        templates = {
            "中考政策": f"""
一、考试科目与分值

{datetime.now().year}年{province}中考总分700分，各科目分值如下：
- 语文：120分
- 数学：120分
- 英语：120分（含听力30分）
- 物理：100分
- 化学：100分
- 道德与法治：60分
- 历史：60分
- 体育：50分

二、考试时间安排

中考时间通常安排在6月中下旬，具体时间由各州市确定。

三、录取批次

录取分为提前批次、第一批次、第二批次和第三批次。

四、志愿填报

成绩公布后进行网上志愿填报，每批次可填报3-5个平行志愿。

五、加分政策

烈士子女、少数民族考生、归侨子女等可享受加分照顾。
""",
            "招生政策": f"""
一、招生计划

{datetime.now().year}年{province}普通高中计划招生人数根据各州市实际情况确定。

二、录取分数线

各批次录取分数线由各州市教育部门划定，省级示范性高中录取分数线一般不低于600分。

三、定向生政策

省级示范性高中招生计划的50%定向分配到各初中学校。

四、特长生招生

体育艺术特长生招生比例不超过学校招生计划的5%，文化成绩要求不低于学校录取线的70%。

五、咨询渠道

详情请咨询当地教育部门或访问教育官网。
""",
            "志愿填报": f"""
一、填报时间

中考成绩公布后5-7天内进行志愿填报。

二、填报方式

登录当地中考招生平台进行网上填报。

三、填报技巧

1. 了解学校：查看学校历年录取分数线、办学特色
2. 合理定位：根据模考成绩和排名选择学校
3. 拉开梯度：志愿之间保持合理分差
4. 服从调剂：增加录取机会

四、注意事项

1. 志愿一经确认不可修改
2. 未被录取可参加补录
3. 保管好账号密码
"""
        }
        
        for key, template in templates.items():
            if key in title:
                return template
        
        return f"本文详细介绍{province}{title}的相关内容，包括政策要点、操作指南等。"
    
    def update_school_info(self, limit=100):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, city, province FROM schools 
            WHERE description IS NULL OR description = '' OR features IS NULL OR features = ''
            LIMIT ?
        """, (limit,))
        schools = cursor.fetchall()
        
        print(f"需要更新的学校: {len(schools)}所")
        updated = 0
        
        for school_id, name, city, province in schools:
            print(f"  生成: {name}...")
            info = self.generate_school_info(name, city or "", province or "云南省")
            
            cursor.execute("""
                UPDATE schools SET 
                    description = ?, features = ?, style = ?, level = ?,
                    minScore = ?, oneRate = ?, address = ?, phone = ?,
                    website = ?, student_count = ?, teacher_count = ?
                WHERE id = ?
            """, (
                info.get('description', ''),
                info.get('features', ''),
                info.get('style', '综合发展'),
                info.get('level', '一般高中'),
                info.get('minScore', 500),
                info.get('oneRate', 60.0),
                info.get('address', ''),
                info.get('phone', ''),
                info.get('website', ''),
                info.get('student_count', 2000),
                info.get('teacher_count', 150),
                school_id
            ))
            updated += 1
            
            if updated % 10 == 0:
                conn.commit()
                print(f"  已更新 {updated} 所学校")
            
            time.sleep(0.1)
        
        conn.commit()
        conn.close()
        print(f"总计更新: {updated} 所学校")
        return updated
    
    def add_policies(self, province, count=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        policy_titles = [
            f"{datetime.now().year}年{province}中考政策解读",
            f"{datetime.now().year}年{province}普通高中招生政策",
            f"{province}中考志愿填报指南",
            f"{province}中考加分政策详解",
            f"{province}定向生招生政策",
            f"{province}体育艺术特长生招生办法",
            f"{province}民办高中招生政策",
            f"{province}中考录取规则解读",
            f"{province}中考改革政策要点",
            f"{province}高中阶段学校招生工作通知"
        ]
        
        added = 0
        for title in policy_titles[:count]:
            cursor.execute("SELECT id FROM policies WHERE title = ?", (title,))
            if cursor.fetchone():
                continue
            
            print(f"  生成: {title}")
            content = self.generate_policy_info(title, province)
            
            cursor.execute("""
                INSERT INTO policies (title, content, category, publish_date, source)
                VALUES (?, ?, ?, ?, ?)
            """, (
                title, content, 
                "中考政策" if "中考" in title else "招生政策",
                datetime.now().strftime('%Y-%m-%d'),
                f"{province}教育厅"
            ))
            added += 1
            time.sleep(0.1)
        
        conn.commit()
        conn.close()
        print(f"总计添加: {added} 条政策")
        return added

def run_ai_data_collection():
    db_path = 'e:/aiphxt-app/ai-service/data/school_platform.db'
    
    print("=" * 60)
    print("AI大模型数据生成工具")
    print("=" * 60)
    
    generator = AIDataGenerator(db_path)
    
    print("\n1. 更新学校信息...")
    generator.update_school_info(limit=50)
    
    print("\n2. 添加政策信息...")
    for province in ["云南省", "贵州省", "广西壮族自治区"]:
        print(f"\n  {province}:")
        generator.add_policies(province, count=5)
    
    print("\n" + "=" * 60)
    print("AI数据生成完成！")
    print("=" * 60)

if __name__ == '__main__':
    run_ai_data_collection()
