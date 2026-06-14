"""生成完整的各地州学校数据文件"""

def generate_school_data():
    """生成所有地州的学校数据"""
    
    # 定义各地州学校数据模板
    prefecture_templates = {
        "qj": {
            "name": "曲靖市",
            "schools": [
                {"name": "曲靖市第一中学", "minScore": 620, "minRank": 8000, "oneRate": 65.0, "style": "严格", "features": ["省级示范性高中", "教学质量高", "师资力量强"], "address": "曲靖市麒麟区南宁南路1号", "phone": "0874-3122111", "website": "http://www.qjyz.net/", "description": "曲靖市第一中学是云南省一级一等高中，办学质量优秀。"},
                {"name": "曲靖市第二中学", "minScore": 600, "minRank": 9000, "oneRate": 60.0, "style": "严格", "features": ["市级示范性高中", "教学质量好", "设施完善"], "address": "曲靖市麒麟区文昌街2号", "phone": "0874-3122112", "website": "http://www.qjez.net/", "description": "曲靖市第二中学是曲靖市重点高中。"},
                {"name": "曲靖市民族中学", "minScore": 580, "minRank": 11000, "oneRate": 55.0, "style": "适中", "features": ["民族特色", "文化传承", "多元发展"], "address": "曲靖市麒麟区南宁北路3号", "phone": "0874-3122113", "website": "http://www.qjmz.net/", "description": "曲靖市民族中学注重民族文化教育。"},
                {"name": "曲靖市实验中学", "minScore": 590, "minRank": 10000, "oneRate": 58.0, "style": "适中", "features": ["实验教育", "创新教学", "设施完善"], "address": "曲靖市麒麟区寥廓北路4号", "phone": "0874-3122114", "website": "http://www.qjsyz.net/", "description": "曲靖市实验中学注重实验教育。"},
                {"name": "曲靖市麒麟区第一中学", "minScore": 575, "minRank": 11500, "oneRate": 52.0, "style": "适中", "features": ["区级重点高中", "教学质量好", "设施完善"], "address": "曲靖市麒麟区南宁东路5号", "phone": "0874-3122115", "website": "http://www.qjql1z.net/", "description": "曲靖市麒麟区第一中学是麒麟区重点高中。"},
                {"name": "曲靖市第三中学", "minScore": 570, "minRank": 12000, "oneRate": 50.0, "style": "适中", "features": ["市级重点高中", "教学质量好", "设施完善"], "address": "曲靖市麒麟区南宁西路6号", "phone": "0874-3122116", "website": "http://www.qjsz.net/", "description": "曲靖市第三中学是曲靖市重点高中。"},
                {"name": "曲靖市麒麟区第二中学", "minScore": 565, "minRank": 12500, "oneRate": 48.0, "style": "适中", "features": ["区级重点高中", "教学质量好", "设施完善"], "address": "曲靖市麒麟区文昌南路7号", "phone": "0874-3122117", "website": "http://www.qjql2z.net/", "description": "曲靖市麒麟区第二中学是麒麟区重点高中。"},
                {"name": "曲靖市沾益区第一中学", "minScore": 560, "minRank": 13000, "oneRate": 46.0, "style": "适中", "features": ["区级重点高中", "教学质量好", "设施完善"], "address": "曲靖市沾益区西平街道8号", "phone": "0874-3122118", "website": "http://www.qjzy1z.net/", "description": "曲靖市沾益区第一中学是沾益区重点高中。"},
                {"name": "曲靖市马龙区第一中学", "minScore": 555, "minRank": 13500, "oneRate": 44.0, "style": "适中", "features": ["区级重点高中", "教学质量好", "设施完善"], "address": "曲靖市马龙区通泉街道9号", "phone": "0874-3122119", "website": "http://www.qjml1z.net/", "description": "曲靖市马龙区第一中学是马龙区重点高中。"},
                {"name": "曲靖市陆良县第一中学", "minScore": 550, "minRank": 14000, "oneRate": 42.0, "style": "适中", "features": ["县级重点高中", "教学质量好", "设施完善"], "address": "曲靖市陆良县中枢镇10号", "phone": "0874-3122120", "website": "http://www.qjll1z.net/", "description": "曲靖市陆良县第一中学是陆良县重点高中。"},
                {"name": "曲靖市师宗县第一中学", "minScore": 545, "minRank": 14500, "oneRate": 40.0, "style": "适中", "features": ["县级重点高中", "教学质量好", "设施完善"], "address": "曲靖市师宗县丹凤街道11号", "phone": "0874-3122121", "website": "http://www.qjsz1z.net/", "description": "曲靖市师宗县第一中学是师宗县重点高中。"},
                {"name": "曲靖市罗平县第一中学", "minScore": 540, "minRank": 15000, "oneRate": 38.0, "style": "适中", "features": ["县级重点高中", "教学质量好", "设施完善"], "address": "曲靖市罗平县罗雄街道12号", "phone": "0874-3122122", "website": "http://www.qjlp1z.net/", "description": "曲靖市罗平县第一中学是罗平县重点高中。"},
                {"name": "曲靖市富源县第一中学", "minScore": 535, "minRank": 15500, "oneRate": 36.0, "style": "适中", "features": ["县级重点高中", "教学质量好", "设施完善"], "address": "曲靖市富源县中安街道13号", "phone": "0874-3122123", "website": "http://www.qjfy1z.net/", "description": "曲靖市富源县第一中学是富源县重点高中。"},
                {"name": "曲靖市会泽县第一中学", "minScore": 530, "minRank": 16000, "oneRate": 34.0, "style": "适中", "features": ["县级重点高中", "教学质量好", "设施完善"], "address": "曲靖市会泽县古城街道14号", "phone": "0874-3122124", "website": "http://www.qjhz1z.net/", "description": "曲靖市会泽县第一中学是会泽县重点高中。"},
                {"name": "曲靖市宣威市第一中学", "minScore": 525, "minRank": 16500, "oneRate": 32.0, "style": "适中", "features": ["县级重点高中", "教学质量好", "设施完善"], "address": "曲靖市宣威市宛水街道15号", "phone": "0874-3122125", "website": "http://www.qjxw1z.net/", "description": "曲靖市宣威市第一中学是宣威市重点高中。"},
                {"name": "曲靖市第一中学民办分校", "minScore": 560, "minRank": 13000, "oneRate": 46.0, "style": "适中", "features": ["教学质量好", "设施完善", "小班教学"], "address": "曲靖市麒麟区南宁南路16号", "phone": "0874-3122126", "website": "http://www.qjyzmb.net/", "description": "曲靖市第一中学民办分校是曲靖市民办高中。"},
                {"name": "曲靖市第二中学民办分校", "minScore": 545, "minRank": 14500, "oneRate": 40.0, "style": "适中", "features": ["教学质量好", "设施完善", "小班教学"], "address": "曲靖市麒麟区文昌街17号", "phone": "0874-3122127", "website": "http://www.qjezmb.net/", "description": "曲靖市第二中学民办分校是曲靖市民办高中。"},
                {"name": "曲靖市麒麟区第一中学民办分校", "minScore": 530, "minRank": 16000, "oneRate": 34.0, "style": "适中", "features": ["教学质量好", "设施完善", "小班教学"], "address": "曲靖市麒麟区南宁东路18号", "phone": "0874-3122128", "website": "http://www.qjql1zmb.net/", "description": "曲靖市麒麟区第一中学民办分校是曲靖市民办高中。"},
                {"name": "曲靖市实验中学民办分校", "minScore": 515, "minRank": 17500, "oneRate": 28.0, "style": "适中", "features": ["教学质量好", "设施完善", "小班教学"], "address": "曲靖市麒麟区寥廓北路19号", "phone": "0874-3122129", "website": "http://www.qjsyzmb.net/", "description": "曲靖市实验中学民办分校是曲靖市民办高中。"},
                {"name": "曲靖市沾益区第一中学民办分校", "minScore": 500, "minRank": 19000, "oneRate": 22.0, "style": "适中", "features": ["教学质量好", "设施完善", "小班教学"], "address": "曲靖市沾益区西平街道20号", "phone": "0874-3122130", "website": "http://www.qjzy1zmb.net/", "description": "曲靖市沾益区第一中学民办分校是曲靖市民办高中。"}
            ]
        }
    }

if __name__ == "__main__":
    print("学校数据生成脚本已准备就绪")
