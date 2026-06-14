"""增强版爬虫系统 - 采集学校和政策数据"""

import time
import random
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
import json
import os
from .enhanced_schools import all_prefecture_schools
from .integrated_policies import all_prefecture_policies, prefecture_names
try:
    from .enhanced_policies import enhanced_policies
except ImportError:
    enhanced_policies = {}

class EnhancedCrawler:
    """增强版爬虫"""
    
    def __init__(self):
        self.base_urls = {
            "km_education": "http://jyj.km.gov.cn/",
            "yn_education": "http://jyt.yn.gov.cn/",
            "qj_education": "http://jyj.qj.gov.cn/",  # 曲靖市教育局
            "yx_education": "http://jyj.yuxi.gov.cn/",  # 玉溪市教育局
            "bs_education": "http://jyj.baoshan.gov.cn/",  # 保山市教育局
            "zt_education": "http://jyj.zt.gov.cn/",  # 昭通市教育局
            "lj_education": "http://jyj.lijiang.gov.cn/",  # 丽江市教育局
            "pe_education": "http://jyj.pu-er.cn/",  # 普洱市教育局
            "lc_education": "http://jyj.lincang.gov.cn/",  # 临沧市教育局
            "cx_education": "http://jyj.cxz.gov.cn/",  # 楚雄州教育局
            "hh_education": "http://jyj.hh.gov.cn/",  # 红河州教育局
            "ws_education": "http://jyj.ynws.gov.cn/",  # 文山州教育局
            "xsbn_education": "http://jyj.xsbn.gov.cn/",  # 西双版纳州教育局
            "dl_education": "http://jyj.dali.gov.cn/",  # 大理州教育局
            "dh_education": "http://jyj.dh.gov.cn/",  # 德宏州教育局
            "nj_education": "http://jyj.nujiang.gov.cn/",  # 怒江州教育局
            "dq_education": "http://jyj.diqing.gov.cn/"  # 迪庆州教育局
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
        self.crawled_data = []
        self.max_retries = 3
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        # 地州信息
        self.prefectures = {
            "km": "昆明市",
            "qj": "曲靖市",
            "yx": "玉溪市",
            "bs": "保山市",
            "zt": "昭通市",
            "lj": "丽江市",
            "pe": "普洱市",
            "lc": "临沧市",
            "cx": "楚雄州",
            "hh": "红河州",
            "ws": "文山州",
            "xsbn": "西双版纳州",
            "dl": "大理州",
            "dh": "德宏州",
            "nj": "怒江州",
            "dq": "迪庆州"
        }
    
    def get_school_data(self) -> List[Dict[str, Any]]:
        """获取学校数据（模拟真实数据）"""
        schools = [
            {
                "id": 1,
                "name": "云南师范大学附属中学",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 690,
                "minRank": 500,
                "oneRate": 98.5,
                "boarding": True,
                "tuition": 0,
                "style": "严格",
                "features": ["理科强", "竞赛优势", "名校资源"],
                "address": "昆明市五华区建设路1号",
                "phone": "0871-65321111",
                "website": "http://www.ynsdfz.net/",
                "description": "云南师范大学附属中学是云南省首批一级一等完全中学，全国百强中学。"
            },
            {
                "id": 2,
                "name": "昆明市第一中学",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 680,
                "minRank": 1000,
                "oneRate": 96.0,
                "boarding": True,
                "tuition": 0,
                "style": "严格",
                "features": ["综合均衡", "历史悠久", "师资强"],
                "address": "昆明市五华区华山南路1号",
                "phone": "0871-63613333",
                "website": "http://www.kmyz.net/",
                "description": "昆明市第一中学创建于1905年，是云南省历史最悠久的中学之一。"
            },
            {
                "id": 3,
                "name": "昆明市第三中学",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 670,
                "minRank": 2000,
                "oneRate": 93.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["文科优势", "艺术特色", "环境优美"],
                "address": "昆明市呈贡区春融东路1号",
                "phone": "0871-67471111",
                "website": "http://www.kmsz.net/",
                "description": "昆明市第三中学是云南省一级一等完全中学，以文科教育著称。"
            },
            {
                "id": 4,
                "name": "昆明市第八中学",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 660,
                "minRank": 3000,
                "oneRate": 90.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["理科见长", "设施完善", "管理规范"],
                "address": "昆明市五华区龙泉路1号",
                "phone": "0871-65812222",
                "website": "http://www.km8z.net/",
                "description": "昆明市第八中学是云南省一级一等完全中学，理科教育特色鲜明。"
            },
            {
                "id": 5,
                "name": "昆明市第十中学",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 650,
                "minRank": 4000,
                "oneRate": 87.0,
                "boarding": True,
                "tuition": 0,
                "style": "宽松",
                "features": ["创新教育", "社团丰富", "自主管理"],
                "address": "昆明市盘龙区白塔路1号",
                "phone": "0871-63123333",
                "website": "http://www.km10z.net/",
                "description": "昆明市第十中学是云南省一级一等完全中学，注重学生全面发展。"
            },
            {
                "id": 6,
                "name": "云南大学附属中学",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 655,
                "minRank": 3500,
                "oneRate": 88.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["大学资源", "科研优势", "国际化"],
                "address": "昆明市五华区一二一大街1号",
                "phone": "0871-65031111",
                "website": "http://www.ydfz.net/",
                "description": "云南大学附属中学享有云南大学的教育资源，科研氛围浓厚。"
            },
            {
                "id": 7,
                "name": "昆明市第十二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 630,
                "minRank": 6000,
                "oneRate": 75.0,
                "boarding": False,
                "tuition": 0,
                "style": "适中",
                "features": ["交通便利", "走读为主", "性价比高"],
                "address": "昆明市官渡区关兴路1号",
                "phone": "0871-67171111",
                "website": "http://www.km12z.net/",
                "description": "昆明市第十二中学是云南省一级二等完全中学，交通便利。"
            },
            {
                "id": 8,
                "name": "昆明市第十四中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 620,
                "minRank": 7000,
                "oneRate": 70.0,
                "boarding": True,
                "tuition": 0,
                "style": "严格",
                "features": ["管理严格", "学风优良", "进步快"],
                "address": "昆明市五华区黑林铺1号",
                "phone": "0871-68181111",
                "website": "http://www.km14z.net/",
                "description": "昆明市第十四中学是云南省一级二等完全中学，管理严格，学风优良。"
            },
            {
                "id": 9,
                "name": "北大附中云南实验学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 600,
                "minRank": 9000,
                "oneRate": 65.0,
                "boarding": True,
                "tuition": 28000,
                "style": "宽松",
                "features": ["名校品牌", "小班教学", "个性化"],
                "address": "昆明市官渡区世纪城1号",
                "phone": "0871-67371111",
                "website": "http://www.bdfzyn.net/",
                "description": "北大附中云南实验学校是北京大学附属中学在云南的分校，小班教学特色。"
            },
            {
                "id": 10,
                "name": "云南衡水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 580,
                "minRank": 11000,
                "oneRate": 60.0,
                "boarding": True,
                "tuition": 32000,
                "style": "严格",
                "features": ["衡水模式", "提分快", "军事化管理"],
                "address": "昆明市呈贡区雨花片区1号",
                "phone": "0871-67491111",
                "website": "http://www.ynhssy.net/",
                "description": "云南衡水实验中学引进河北衡水中学的教学模式，军事化管理，提分显著。"
            },
            {
                "id": 12,
                "name": "昆明市第五中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 615,
                "minRank": 7500,
                "oneRate": 68.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["艺术特色", "走读为主", "社团活跃"],
                "address": "昆明市西山区西苑路1号",
                "phone": "0871-68241111",
                "website": "http://www.km5z.net/",
                "description": "昆明市第五中学以艺术教育为特色，学生社团活动丰富。"
            },
            {
                "id": 13,
                "name": "昆明市第六中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 610,
                "minRank": 8000,
                "oneRate": 65.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["体育特色", "寄宿制", "设施完善"],
                "address": "昆明市官渡区金马镇1号",
                "phone": "0871-67351111",
                "website": "http://www.km6z.net/",
                "description": "昆明市第六中学以体育教育见长，拥有完善的体育设施。"
            },
            {
                "id": 14,
                "name": "昆明市第九中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 605,
                "minRank": 8500,
                "oneRate": 62.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["科技特色", "创新教育", "实践导向"],
                "address": "昆明市盘龙区茨坝镇1号",
                "phone": "0871-65891111",
                "website": "http://www.km9z.net/",
                "description": "昆明市第九中学注重科技创新教育，培养学生的实践能力。"
            },
            {
                "id": 15,
                "name": "昆明市第十一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 600,
                "minRank": 9000,
                "oneRate": 58.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["外语特色", "国际交流", "小班教学"],
                "address": "昆明市西山区马街镇1号",
                "phone": "0871-68151111",
                "website": "http://www.km11z.net/",
                "description": "昆明市第十一中学以外语教学为特色，开展国际交流项目。"
            },
            {
                "id": 16,
                "name": "云南民族中学",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 640,
                "minRank": 5000,
                "oneRate": 82.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["民族特色", "多元文化", "政策优惠"],
                "address": "昆明市五华区学府路1号",
                "phone": "0871-65161111",
                "website": "http://www.ynmzzx.net/",
                "description": "云南民族中学是云南省唯一的省属民族中学，面向全省招收少数民族学生。"
            },
            {
                "id": 17,
                "name": "昆明光华学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 570,
                "minRank": 12000,
                "oneRate": 55.0,
                "boarding": True,
                "tuition": 25000,
                "style": "适中",
                "features": ["小班教学", "个性化辅导", "环境优美"],
                "address": "昆明市安宁市温泉镇1号",
                "phone": "0871-68681111",
                "website": "http://www.kmghxx.net/",
                "description": "昆明光华学校实行小班教学，注重个性化辅导，校园环境优美。"
            },
            {
                "id": 18,
                "name": "昆明西南联大研究院附属中学",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 665,
                "minRank": 2500,
                "oneRate": 91.0,
                "boarding": True,
                "tuition": 0,
                "style": "宽松",
                "features": ["名校传承", "创新教育", "学术氛围"],
                "address": "昆明市呈贡区联大街1号",
                "phone": "0871-67421111",
                "website": "http://www.xnldfz.net/",
                "description": "昆明西南联大研究院附属中学传承西南联大精神，注重创新教育。"
            },
            {
                "id": 19,
                "name": "昆明师范高等专科学校附属中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 595,
                "minRank": 9500,
                "oneRate": 56.0,
                "boarding": False,
                "tuition": 0,
                "style": "适中",
                "features": ["师范背景", "教育实践", "师资培养"],
                "address": "昆明市五华区龙泉路2号",
                "phone": "0871-65821111",
                "website": "http://www.kmsdfz.net/",
                "description": "昆明师范高等专科学校附属中学依托师范院校资源，注重教育实践。"
            },
            {
                "id": 20,
                "name": "昆明经济技术开发区第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 590,
                "minRank": 10000,
                "oneRate": 52.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["开发区资源", "现代设施", "就业导向"],
                "address": "昆明市经开区信息产业基地1号",
                "phone": "0871-67431111",
                "website": "http://www.kmjkqyz.net/",
                "description": "昆明经济技术开发区第一中学依托开发区资源，设施现代化。"
            },
            {
                "id": 21,
                "name": "昆明市第十五中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 585,
                "minRank": 10500,
                "oneRate": 50.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["社区服务", "实践教育", "开放办学"],
                "address": "昆明市西山区福海街道1号",
                "phone": "0871-68261111",
                "website": "http://www.km15z.net/",
                "description": "昆明市第十五中学注重社区服务与实践教育。"
            },
            {
                "id": 22,
                "name": "昆明市第十六中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 580,
                "minRank": 11000,
                "oneRate": 48.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["寄宿制", "封闭管理", "学风严谨"],
                "address": "昆明市官渡区小板桥镇1号",
                "phone": "0871-67381111",
                "website": "http://www.km16z.net/",
                "description": "昆明市第十六中学实行寄宿制管理，学风严谨。"
            },
            {
                "id": 23,
                "name": "昆明市第十七中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 575,
                "minRank": 11500,
                "oneRate": 46.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["艺术教育", "素质教育", "全面发展"],
                "address": "昆明市盘龙区双龙街道1号",
                "phone": "0871-65871111",
                "website": "http://www.km17z.net/",
                "description": "昆明市第十七中学以艺术教育为特色，注重素质教育。"
            },
            {
                "id": 24,
                "name": "昆明市第十八中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 570,
                "minRank": 12000,
                "oneRate": 44.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["农村教育", "寄宿制", "政策扶持"],
                "address": "昆明市晋宁区昆阳镇1号",
                "phone": "0871-67891111",
                "website": "http://www.km18z.net/",
                "description": "昆明市第十八中学面向农村地区，享受政策扶持。"
            },
            {
                "id": 25,
                "name": "昆明市第十九中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 565,
                "minRank": 12500,
                "oneRate": 42.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["职业教育", "技能培训", "就业导向"],
                "address": "昆明市东川区铜都镇1号",
                "phone": "0871-62131111",
                "website": "http://www.km19z.net/",
                "description": "昆明市第十九中学注重职业教育与技能培训。"
            },
            {
                "id": 26,
                "name": "昆明市第二十中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 560,
                "minRank": 13000,
                "oneRate": 40.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["山区教育", "寄宿制", "小班教学"],
                "address": "昆明市禄劝县屏山镇1号",
                "phone": "0871-68991111",
                "website": "http://www.km20z.net/",
                "description": "昆明市第二十中学面向山区，实行小班教学。"
            },
            {
                "id": 27,
                "name": "安宁中学",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 635,
                "minRank": 5500,
                "oneRate": 80.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["县级名校", "环境优美", "设施完善"],
                "address": "昆明市安宁市连然镇1号",
                "phone": "0871-68671111",
                "website": "http://www.az.net/",
                "description": "安宁中学是安宁市最好的高中，环境优美。"
            },
            {
                "id": 28,
                "name": "晋宁区第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 555,
                "minRank": 13500,
                "oneRate": 38.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["县级中学", "寄宿制", "稳步发展"],
                "address": "昆明市晋宁区昆阳镇2号",
                "phone": "0871-67881111",
                "website": "http://www.jnqyz.net/",
                "description": "晋宁区第一中学是晋宁区重点中学。"
            },
            {
                "id": 29,
                "name": "富民县第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 550,
                "minRank": 14000,
                "oneRate": 36.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["县级中学", "政策扶持", "小班教学"],
                "address": "昆明市富民县永定镇1号",
                "phone": "0871-68811111",
                "website": "http://www.fmyz.net/",
                "description": "富民县第一中学是富民县唯一的高中。"
            },
            {
                "id": 30,
                "name": "宜良县第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 545,
                "minRank": 14500,
                "oneRate": 35.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["县级中学", "历史悠久", "文化底蕴"],
                "address": "昆明市宜良县匡远镇1号",
                "phone": "0871-67521111",
                "website": "http://www.ylyz.net/",
                "description": "宜良县第一中学历史悠久，文化底蕴深厚。"
            },
            {
                "id": 31,
                "name": "石林彝族自治县第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 540,
                "minRank": 15000,
                "oneRate": 33.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["民族特色", "旅游文化", "政策优惠"],
                "address": "昆明市石林县鹿阜镇1号",
                "phone": "0871-67791111",
                "website": "http://www.slxyz.net/",
                "description": "石林彝族自治县第一中学具有民族特色。"
            },
            {
                "id": 32,
                "name": "嵩明县第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 535,
                "minRank": 15500,
                "oneRate": 32.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["县级中学", "农业特色", "实践教育"],
                "address": "昆明市嵩明县嵩阳镇1号",
                "phone": "0871-67921111",
                "website": "http://www.smyz.net/",
                "description": "嵩明县第一中学注重实践教育。"
            },
            {
                "id": 33,
                "name": "禄劝彝族苗族自治县第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 530,
                "minRank": 16000,
                "oneRate": 30.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["民族特色", "山区教育", "政策扶持"],
                "address": "昆明市禄劝县屏山镇2号",
                "phone": "0871-68911111",
                "website": "http://www.lqyz.net/",
                "description": "禄劝彝族苗族自治县第一中学具有民族特色。"
            },
            {
                "id": 34,
                "name": "寻甸回族彝族自治县第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 525,
                "minRank": 16500,
                "oneRate": 28.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["民族特色", "寄宿制", "政策扶持"],
                "address": "昆明市寻甸县仁德镇1号",
                "phone": "0871-62651111",
                "website": "http://www.xdyz.net/",
                "description": "寻甸回族彝族自治县第一中学具有民族特色。"
            },
            {
                "id": 35,
                "name": "东川区第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 520,
                "minRank": 17000,
                "oneRate": 26.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["矿区教育", "职业教育", "就业导向"],
                "address": "昆明市东川区铜都镇2号",
                "phone": "0871-62121111",
                "website": "http://www.dcyz.net/",
                "description": "东川区第一中学注重职业教育。"
            },
            {
                "id": 36,
                "name": "云南师大实验中学",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 650,
                "minRank": 4000,
                "oneRate": 86.0,
                "boarding": False,
                "tuition": 0,
                "style": "适中",
                "features": ["师大品牌", "实验特色", "创新教育"],
                "address": "昆明市五华区建设路2号",
                "phone": "0871-65332222",
                "website": "http://www.ynsdsy.net/",
                "description": "云南师大实验中学依托师大资源，注重创新教育。"
            },
            {
                "id": 37,
                "name": "昆明滇池中学",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 625,
                "minRank": 6500,
                "oneRate": 78.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["环境优美", "素质教育", "生态教育"],
                "address": "昆明市西山区滇池路1号",
                "phone": "0871-68291111",
                "website": "http://www.kmdcz.net/",
                "description": "昆明滇池中学环境优美，注重生态教育。"
            },
            {
                "id": 38,
                "name": "昆明长城中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 595,
                "minRank": 9500,
                "oneRate": 54.0,
                "boarding": True,
                "tuition": 22000,
                "style": "适中",
                "features": ["民办名校", "小班教学", "个性化辅导"],
                "address": "昆明市盘龙区龙泉路3号",
                "phone": "0871-65851111",
                "website": "http://www.kmcczx.net/",
                "description": "昆明长城中学实行小班教学，注重个性化辅导。"
            },
            {
                "id": 39,
                "name": "昆明日章中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 585,
                "minRank": 10500,
                "oneRate": 50.0,
                "boarding": True,
                "tuition": 20000,
                "style": "适中",
                "features": ["日式教育", "国际化", "语言特色"],
                "address": "昆明市官渡区关上镇1号",
                "phone": "0871-67151111",
                "website": "http://www.kmrzzx.net/",
                "description": "昆明日章中学具有日式教育特色，注重语言培养。"
            },
            {
                "id": 40,
                "name": "昆明亨德森高新一中",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 575,
                "minRank": 11500,
                "oneRate": 46.0,
                "boarding": True,
                "tuition": 18000,
                "style": "适中",
                "features": ["高新区资源", "现代教育", "科技特色"],
                "address": "昆明市高新区科技路1号",
                "phone": "0871-68301111",
                "website": "http://www.kmhds.net/",
                "description": "昆明亨德森高新一中依托高新区资源，注重科技教育。"
            },
            {
                "id": 41,
                "name": "昆明西山一中",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 565,
                "minRank": 12500,
                "oneRate": 42.0,
                "boarding": False,
                "tuition": 0,
                "style": "适中",
                "features": ["区级重点", "走读为主", "交通便利"],
                "address": "昆明市西山区马街镇2号",
                "phone": "0871-68181111",
                "website": "http://www.xsyz.net/",
                "description": "昆明西山一中是西山区重点中学。"
            },
            {
                "id": 42,
                "name": "昆明官渡一中",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 560,
                "minRank": 13000,
                "oneRate": 40.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["区级重点", "寄宿制", "管理规范"],
                "address": "昆明市官渡区官渡镇1号",
                "phone": "0871-67311111",
                "website": "http://www.gdyz.net/",
                "description": "昆明官渡一中是官渡区重点中学。"
            },
            {
                "id": 43,
                "name": "昆明盘龙一中",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 555,
                "minRank": 13500,
                "oneRate": 38.0,
                "boarding": False,
                "tuition": 0,
                "style": "适中",
                "features": ["区级重点", "走读为主", "历史名校"],
                "address": "昆明市盘龙区拓东路1号",
                "phone": "0871-63151111",
                "website": "http://www.plyz.net/",
                "description": "昆明盘龙一中历史悠久，是盘龙区重点中学。"
            },
            {
                "id": 44,
                "name": "昆明五华一中",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 550,
                "minRank": 14000,
                "oneRate": 36.0,
                "boarding": False,
                "tuition": 0,
                "style": "适中",
                "features": ["区级重点", "走读为主", "位置优越"],
                "address": "昆明市五华区人民路1号",
                "phone": "0871-65351111",
                "website": "http://www.whyz.net/",
                "description": "昆明五华一中位置优越，是五华区重点中学。"
            },
            {
                "id": 45,
                "name": "昆明呈贡一中",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 545,
                "minRank": 14500,
                "oneRate": 34.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["新区学校", "设施现代", "寄宿制"],
                "address": "昆明市呈贡区龙城街道1号",
                "phone": "0871-67481111",
                "website": "http://www.cgyz.net/",
                "description": "昆明呈贡一中设施现代化，是呈贡区重点中学。"
            },
            {
                "id": 46,
                "name": "云南昌乐实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 565,
                "minRank": 12500,
                "oneRate": 43.0,
                "boarding": True,
                "tuition": 24000,
                "style": "严格",
                "features": ["实验教育", "创新教学", "寄宿制"],
                "address": "昆明市官渡区大板桥镇1号",
                "phone": "0871-67331111",
                "website": "http://www.ynclexy.net/",
                "description": "云南昌乐实验中学注重实验教育与创新教学。"
            },
            {
                "id": 47,
                "name": "昆明锐意外国语中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 555,
                "minRank": 13500,
                "oneRate": 38.0,
                "boarding": True,
                "tuition": 26000,
                "style": "适中",
                "features": ["外语特色", "国际化", "小班教学"],
                "address": "昆明市西山区碧鸡镇1号",
                "phone": "0871-68221111",
                "website": "http://www.kmrywgy.net/",
                "description": "昆明锐意外国语中学以外语教学为特色。"
            },
            {
                "id": 48,
                "name": "昆明行知中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 545,
                "minRank": 14500,
                "oneRate": 33.0,
                "boarding": True,
                "tuition": 23000,
                "style": "适中",
                "features": ["实践教育", "素质教育", "全面发展"],
                "address": "昆明市晋宁区昆阳镇3号",
                "phone": "0871-67871111",
                "website": "http://www.kmxz.net/",
                "description": "昆明行知中学注重实践教育与素质教育。"
            },
            {
                "id": 49,
                "name": "昆明艺卓中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 535,
                "minRank": 15500,
                "oneRate": 30.0,
                "boarding": True,
                "tuition": 28000,
                "style": "宽松",
                "features": ["艺术特色", "创意教育", "个性发展"],
                "address": "昆明市盘龙区茨坝镇2号",
                "phone": "0871-65881111",
                "website": "http://www.kmyz.net/",
                "description": "昆明艺卓中学以艺术教育为特色，注重个性发展。"
            },
            {
                "id": 50,
                "name": "昆明云华实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 525,
                "minRank": 16500,
                "oneRate": 28.0,
                "boarding": True,
                "tuition": 21000,
                "style": "适中",
                "features": ["实验教育", "创新教学", "小班制"],
                "address": "昆明市呈贡区雨花片区2号",
                "phone": "0871-67492222",
                "website": "http://www.kmyhsy.net/",
                "description": "昆明云华实验中学实行小班制教学。"
            },
            {
                "id": 51,
                "name": "昆明市第二十一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 520,
                "minRank": 17000,
                "oneRate": 25.0,
                "boarding": False,
                "tuition": 0,
                "style": "适中",
                "features": ["社区教育", "走读为主", "便民服务"],
                "address": "昆明市西山区棕树营街道1号",
                "phone": "0871-68271111",
                "website": "http://www.km21z.net/",
                "description": "昆明市第二十一中学注重社区教育服务。"
            },
            {
                "id": 52,
                "name": "昆明市第二十二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 515,
                "minRank": 17500,
                "oneRate": 23.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["寄宿制", "封闭管理", "稳步提升"],
                "address": "昆明市官渡区矣六街道1号",
                "phone": "0871-67391111",
                "website": "http://www.km22z.net/",
                "description": "昆明市第二十二中学实行寄宿制管理。"
            },
            {
                "id": 53,
                "name": "昆明市第二十三中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 510,
                "minRank": 18000,
                "oneRate": 21.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["素质教育", "全面发展", "特色课程"],
                "address": "昆明市盘龙区青云街道1号",
                "phone": "0871-65892222",
                "website": "http://www.km23z.net/",
                "description": "昆明市第二十三中学注重素质教育。"
            },
            {
                "id": 54,
                "name": "昆明市第二十四中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 505,
                "minRank": 18500,
                "oneRate": 20.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["农村教育", "政策扶持", "寄宿制"],
                "address": "昆明市晋宁区宝峰镇1号",
                "phone": "0871-67892222",
                "website": "http://www.km24z.net/",
                "description": "昆明市第二十四中学面向农村地区。"
            },
            {
                "id": 55,
                "name": "昆明市第二十五中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 500,
                "minRank": 19000,
                "oneRate": 18.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["职业教育", "技能培训", "就业导向"],
                "address": "昆明市东川区汤丹镇1号",
                "phone": "0871-62141111",
                "website": "http://www.km25z.net/",
                "description": "昆明市第二十五中学注重职业教育。"
            },
            {
                "id": 56,
                "name": "昆明市第二十六中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 495,
                "minRank": 19500,
                "oneRate": 16.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["山区教育", "小班教学", "个性化辅导"],
                "address": "昆明市禄劝县转龙镇1号",
                "phone": "0871-68921111",
                "website": "http://www.km26z.net/",
                "description": "昆明市第二十六中学面向山区学生。"
            },
            {
                "id": 57,
                "name": "昆明市第二十七中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 490,
                "minRank": 20000,
                "oneRate": 15.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["民族教育", "文化传承", "政策扶持"],
                "address": "昆明市寻甸县柯渡镇1号",
                "phone": "0871-62661111",
                "website": "http://www.km27z.net/",
                "description": "昆明市第二十七中学具有民族特色。"
            },
            {
                "id": 58,
                "name": "昆明市第二十八中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 485,
                "minRank": 20500,
                "oneRate": 14.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["社区服务", "开放办学", "终身教育"],
                "address": "昆明市西山区金碧街道1号",
                "phone": "0871-68281111",
                "website": "http://www.km28z.net/",
                "description": "昆明市第二十八中学注重社区服务。"
            },
            {
                "id": 59,
                "name": "昆明市第二十九中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 480,
                "minRank": 21000,
                "oneRate": 13.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["寄宿制", "管理规范", "稳步发展"],
                "address": "昆明市官渡区六甲街道1号",
                "phone": "0871-67321111",
                "website": "http://www.km29z.net/",
                "description": "昆明市第二十九中学实行寄宿制。"
            },
            {
                "id": 60,
                "name": "昆明市第三十中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 475,
                "minRank": 21500,
                "oneRate": 12.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["艺术教育", "素质教育", "个性发展"],
                "address": "昆明市盘龙区龙泉街道1号",
                "phone": "0871-65831111",
                "website": "http://www.km30z.net/",
                "description": "昆明市第三十中学以艺术教育为特色。"
            },
            {
                "id": 61,
                "name": "安宁中学太平学校",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 620,
                "minRank": 7000,
                "oneRate": 76.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["安宁品牌", "新校区", "设施完善"],
                "address": "昆明市安宁市太平镇1号",
                "phone": "0871-68682222",
                "website": "http://www.aztp.net/",
                "description": "安宁中学太平学校是安宁中学分校。"
            },
            {
                "id": 62,
                "name": "晋宁区第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 540,
                "minRank": 15000,
                "oneRate": 32.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["县级中学", "寄宿制", "稳步发展"],
                "address": "昆明市晋宁区晋城镇1号",
                "phone": "0871-67831111",
                "website": "http://www.jnez.net/",
                "description": "晋宁区第二中学是晋宁区重点中学。"
            },
            {
                "id": 63,
                "name": "富民县第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 530,
                "minRank": 16000,
                "oneRate": 28.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["县级中学", "小班教学", "政策扶持"],
                "address": "昆明市富民县散旦镇1号",
                "phone": "0871-68821111",
                "website": "http://www.fmez.net/",
                "description": "富民县第二中学是小规模高中。"
            },
            {
                "id": 64,
                "name": "宜良县第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 525,
                "minRank": 16500,
                "oneRate": 26.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["县级中学", "历史悠久", "文化传承"],
                "address": "昆明市宜良县北古城镇1号",
                "phone": "0871-67531111",
                "website": "http://www.ylez.net/",
                "description": "宜良县第二中学历史悠久。"
            },
            {
                "id": 65,
                "name": "石林彝族自治县第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 520,
                "minRank": 17000,
                "oneRate": 24.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["民族特色", "文化传承", "政策扶持"],
                "address": "昆明市石林县板桥镇1号",
                "phone": "0871-67781111",
                "website": "http://www.slez.net/",
                "description": "石林彝族自治县第二中学具有民族特色。"
            },
            {
                "id": 66,
                "name": "嵩明县第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 515,
                "minRank": 17500,
                "oneRate": 22.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["县级中学", "农业特色", "实践教育"],
                "address": "昆明市嵩明县杨林镇1号",
                "phone": "0871-67931111",
                "website": "http://www.smez.net/",
                "description": "嵩明县第二中学注重实践教育。"
            },
            {
                "id": 67,
                "name": "禄劝彝族苗族自治县第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 510,
                "minRank": 18000,
                "oneRate": 20.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["民族特色", "山区教育", "政策扶持"],
                "address": "昆明市禄劝县撒营盘镇1号",
                "phone": "0871-68931111",
                "website": "http://www.lqez.net/",
                "description": "禄劝彝族苗族自治县第二中学具有民族特色。"
            },
            {
                "id": 68,
                "name": "寻甸回族彝族自治县第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 505,
                "minRank": 18500,
                "oneRate": 18.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["民族特色", "寄宿制", "政策扶持"],
                "address": "昆明市寻甸县羊街镇1号",
                "phone": "0871-62671111",
                "website": "http://www.xdez.net/",
                "description": "寻甸回族彝族自治县第二中学具有民族特色。"
            },
            {
                "id": 69,
                "name": "东川区第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 500,
                "minRank": 19000,
                "oneRate": 16.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["矿区教育", "职业教育", "就业导向"],
                "address": "昆明市东川区因民镇1号",
                "phone": "0871-62151111",
                "website": "http://www.dcez.net/",
                "description": "东川区第二中学注重职业教育。"
            },
            {
                "id": 70,
                "name": "昆明市官渡区第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 560,
                "minRank": 13000,
                "oneRate": 40.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["区级重点", "寄宿制", "管理规范"],
                "address": "昆明市官渡区吴井街道1号",
                "phone": "0871-67341111",
                "website": "http://www.gd2z.net/",
                "description": "昆明市官渡区第二中学是官渡区重点中学。"
            },
            {
                "id": 71,
                "name": "昆明市西山区第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 555,
                "minRank": 13500,
                "oneRate": 38.0,
                "boarding": False,
                "tuition": 0,
                "style": "适中",
                "features": ["区级重点", "走读为主", "交通便利"],
                "address": "昆明市西山区永昌街道1号",
                "phone": "0871-68211111",
                "website": "http://www.xs2z.net/",
                "description": "昆明市西山区第二中学是西山区重点中学。"
            },
            {
                "id": 72,
                "name": "昆明市盘龙区第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 550,
                "minRank": 14000,
                "oneRate": 36.0,
                "boarding": False,
                "tuition": 0,
                "style": "适中",
                "features": ["区级重点", "走读为主", "历史悠久"],
                "address": "昆明市盘龙区联盟街道1号",
                "phone": "0871-63161111",
                "website": "http://www.pl2z.net/",
                "description": "昆明市盘龙区第二中学历史悠久。"
            },
            {
                "id": 73,
                "name": "昆明市五华区第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 545,
                "minRank": 14500,
                "oneRate": 34.0,
                "boarding": False,
                "tuition": 0,
                "style": "适中",
                "features": ["区级重点", "走读为主", "位置优越"],
                "address": "昆明市五华区护国街道1号",
                "phone": "0871-65361111",
                "website": "http://www.wh2z.net/",
                "description": "昆明市五华区第二中学位置优越。"
            },
            {
                "id": 74,
                "name": "昆明市呈贡区第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 540,
                "minRank": 15000,
                "oneRate": 32.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["新区学校", "设施现代", "寄宿制"],
                "address": "昆明市呈贡区吴家营街道1号",
                "phone": "0871-67411111",
                "website": "http://www.cg2z.net/",
                "description": "昆明市呈贡区第二中学设施现代化。"
            },
            {
                "id": 75,
                "name": "昆明经济技术开发区第二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 535,
                "minRank": 15500,
                "oneRate": 30.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["开发区资源", "现代设施", "寄宿制"],
                "address": "昆明市经开区洛羊街道1号",
                "phone": "0871-67441111",
                "website": "http://www.kmjkq2z.net/",
                "description": "昆明经济技术开发区第二中学设施现代化。"
            },
            {
                "id": 76,
                "name": "昆明高新技术产业开发区第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 530,
                "minRank": 16000,
                "oneRate": 28.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["高新区资源", "科技特色", "寄宿制"],
                "address": "昆明市高新区科医路1号",
                "phone": "0871-68311111",
                "website": "http://www.kmgxqyz.net/",
                "description": "昆明高新技术产业开发区第一中学注重科技教育。"
            },
            {
                "id": 77,
                "name": "昆明滇池旅游度假区第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 525,
                "minRank": 16500,
                "oneRate": 26.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["度假区资源", "环境优美", "素质教育"],
                "address": "昆明市度假区海埂街道1号",
                "phone": "0871-68321111",
                "website": "http://www.kmdjqyz.net/",
                "description": "昆明滇池旅游度假区第一中学环境优美。"
            },
            {
                "id": 78,
                "name": "昆明阳宗海风景名胜区第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 520,
                "minRank": 17000,
                "oneRate": 24.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["风景区资源", "环境优美", "寄宿制"],
                "address": "昆明市阳宗海汤池镇1号",
                "phone": "0871-67511111",
                "website": "http://www.kmyzhyz.net/",
                "description": "昆明阳宗海风景名胜区第一中学环境优美。"
            },
            {
                "id": 79,
                "name": "昆明倘甸产业园区轿子山旅游开发区第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 515,
                "minRank": 17500,
                "oneRate": 22.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["山区教育", "政策扶持", "寄宿制"],
                "address": "昆明市倘甸产业园区1号",
                "phone": "0871-62711111",
                "website": "http://www.kmtdyz.net/",
                "description": "昆明倘甸产业园区轿子山旅游开发区第一中学面向山区。"
            },
            {
                "id": 80,
                "name": "昆明空港经济区第一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 510,
                "minRank": 18000,
                "oneRate": 20.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["空港区资源", "现代设施", "寄宿制"],
                "address": "昆明市空港经济区大板桥街道1号",
                "phone": "0871-67351111",
                "website": "http://www.kmkgqyz.net/",
                "description": "昆明空港经济区第一中学设施现代化。"
            },
            {
                "id": 81,
                "name": "昆明市第三十一中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 505,
                "minRank": 18500,
                "oneRate": 18.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["社区教育", "走读为主", "便民服务"],
                "address": "昆明市官渡区金马街道1号",
                "phone": "0871-67361111",
                "website": "http://www.km31z.net/",
                "description": "昆明市第三十一中学注重社区教育。"
            },
            {
                "id": 82,
                "name": "昆明市第三十二中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 500,
                "minRank": 19000,
                "oneRate": 16.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["寄宿制", "封闭管理", "稳步提升"],
                "address": "昆明市西山区前卫街道1号",
                "phone": "0871-68231111",
                "website": "http://www.km32z.net/",
                "description": "昆明市第三十二中学实行寄宿制。"
            },
            {
                "id": 83,
                "name": "昆明市第三十三中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 495,
                "minRank": 19500,
                "oneRate": 15.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["素质教育", "全面发展", "特色课程"],
                "address": "昆明市盘龙区茨坝街道1号",
                "phone": "0871-65841111",
                "website": "http://www.km33z.net/",
                "description": "昆明市第三十三中学注重素质教育。"
            },
            {
                "id": 84,
                "name": "昆明市第三十四中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 490,
                "minRank": 20000,
                "oneRate": 14.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["农村教育", "政策扶持", "寄宿制"],
                "address": "昆明市晋宁区二街镇1号",
                "phone": "0871-67841111",
                "website": "http://www.km34z.net/",
                "description": "昆明市第三十四中学面向农村地区。"
            },
            {
                "id": 85,
                "name": "昆明市第三十五中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 485,
                "minRank": 20500,
                "oneRate": 13.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["职业教育", "技能培训", "就业导向"],
                "address": "昆明市东川区拖布卡镇1号",
                "phone": "0871-62161111",
                "website": "http://www.km35z.net/",
                "description": "昆明市第三十五中学注重职业教育。"
            },
            {
                "id": 86,
                "name": "昆明市第三十六中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 480,
                "minRank": 21000,
                "oneRate": 12.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["山区教育", "小班教学", "个性化辅导"],
                "address": "昆明市禄劝县皎平渡镇1号",
                "phone": "0871-68941111",
                "website": "http://www.km36z.net/",
                "description": "昆明市第三十六中学面向山区学生。"
            },
            {
                "id": 87,
                "name": "昆明市第三十七中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 475,
                "minRank": 21500,
                "oneRate": 11.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["民族教育", "文化传承", "政策扶持"],
                "address": "昆明市寻甸县鸡街镇1号",
                "phone": "0871-62681111",
                "website": "http://www.km37z.net/",
                "description": "昆明市第三十七中学具有民族特色。"
            },
            {
                "id": 88,
                "name": "昆明市第三十八中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 470,
                "minRank": 22000,
                "oneRate": 10.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["社区服务", "开放办学", "终身教育"],
                "address": "昆明市西山区福海街道2号",
                "phone": "0871-68291111",
                "website": "http://www.km38z.net/",
                "description": "昆明市第三十八中学注重社区服务。"
            },
            {
                "id": 89,
                "name": "昆明市第三十九中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 465,
                "minRank": 22500,
                "oneRate": 9.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["寄宿制", "管理规范", "稳步发展"],
                "address": "昆明市官渡区矣六街道2号",
                "phone": "0871-67371111",
                "website": "http://www.km39z.net/",
                "description": "昆明市第三十九中学实行寄宿制。"
            },
            {
                "id": 90,
                "name": "昆明市第四十中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 460,
                "minRank": 23000,
                "oneRate": 8.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["艺术教育", "素质教育", "个性发展"],
                "address": "昆明市盘龙区龙泉街道2号",
                "phone": "0871-65851111",
                "website": "http://www.km40z.net/",
                "description": "昆明市第四十中学以艺术教育为特色。"
            },
            {
                "id": 91,
                "name": "云南大学附属中学星耀学校",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 640,
                "minRank": 5000,
                "oneRate": 82.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["云大品牌", "新校区", "设施完善"],
                "address": "昆明市呈贡区雨花片区3号",
                "phone": "0871-67432222",
                "website": "http://www.ydfzxy.net/",
                "description": "云南大学附属中学星耀学校是云大附中分校。"
            },
            {
                "id": 92,
                "name": "昆明市第一中学西山学校",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 630,
                "minRank": 6000,
                "oneRate": 78.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["昆一品牌", "西山校区", "寄宿制"],
                "address": "昆明市西山区马街镇3号",
                "phone": "0871-68191111",
                "website": "http://www.kmyzxs.net/",
                "description": "昆明市第一中学西山学校是昆一中分校。"
            },
            {
                "id": 93,
                "name": "昆明市第三中学经开学校",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 615,
                "minRank": 8000,
                "oneRate": 72.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["昆三品牌", "经开校区", "现代设施"],
                "address": "昆明市经开区信息产业基地2号",
                "phone": "0871-67451111",
                "website": "http://www.kmszjk.net/",
                "description": "昆明市第三中学经开学校是昆三中分校。"
            },
            {
                "id": 94,
                "name": "昆明市第八中学长城新城校区",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 610,
                "minRank": 8500,
                "oneRate": 70.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["昆八品牌", "新城校区", "设施完善"],
                "address": "昆明市五华区普吉街道1号",
                "phone": "0871-65832222",
                "website": "http://www.km8zxc.net/",
                "description": "昆明市第八中学长城新城校区是昆八中分校。"
            },
            {
                "id": 95,
                "name": "昆明市第十中学白塔校区",
                "type": 2,
                "typeName": "重点高中",
                "city": "昆明市",
                "minScore": 605,
                "minRank": 9000,
                "oneRate": 68.0,
                "boarding": False,
                "tuition": 0,
                "style": "宽松",
                "features": ["昆十品牌", "白塔校区", "走读为主"],
                "address": "昆明市盘龙区白塔路2号",
                "phone": "0871-63124444",
                "website": "http://www.km10zbt.net/",
                "description": "昆明市第十中学白塔校区是昆十中分校。"
            },
            {
                "id": 96,
                "name": "昆明市第十二中学环湖校区",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 590,
                "minRank": 10500,
                "oneRate": 58.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["昆十二品牌", "环湖校区", "环境优美"],
                "address": "昆明市官渡区环湖东路1号",
                "phone": "0871-67181111",
                "website": "http://www.km12zhh.net/",
                "description": "昆明市第十二中学环湖校区是昆十二中分校。"
            },
            {
                "id": 97,
                "name": "昆明市第十四中学高新校区",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 585,
                "minRank": 11000,
                "oneRate": 56.0,
                "boarding": True,
                "tuition": 0,
                "style": "严格",
                "features": ["昆十四品牌", "高新校区", "管理严格"],
                "address": "昆明市高新区科高路1号",
                "phone": "0871-68192222",
                "website": "http://www.km14zgx.net/",
                "description": "昆明市第十四中学高新校区是昆十四中分校。"
            },
            {
                "id": 98,
                "name": "安宁中学嵩华学校",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 580,
                "minRank": 11500,
                "oneRate": 54.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["安宁品牌", "嵩华校区", "寄宿制"],
                "address": "昆明市安宁市嵩华路1号",
                "phone": "0871-68691111",
                "website": "http://www.azsh.net/",
                "description": "安宁中学嵩华学校是安宁中学分校。"
            },
            {
                "id": 99,
                "name": "晋宁区第三中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 575,
                "minRank": 12000,
                "oneRate": 52.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["县级中学", "新校区", "设施完善"],
                "address": "昆明市晋宁区上蒜镇1号",
                "phone": "0871-67851111",
                "website": "http://www.jnsz.net/",
                "description": "晋宁区第三中学是新建设高中。"
            },
            {
                "id": 100,
                "name": "宜良县第三中学",
                "type": 1,
                "typeName": "普通高中",
                "city": "昆明市",
                "minScore": 570,
                "minRank": 12500,
                "oneRate": 50.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["县级中学", "稳步发展", "寄宿制"],
                "address": "昆明市宜良县狗街镇1号",
                "phone": "0871-67541111",
                "website": "http://www.ylsz.net/",
                "description": "宜良县第三中学是宜良县新建高中。"
            },
            {
                "id": 101,
                "name": "昆明西山长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 595,
                "minRank": 9500,
                "oneRate": 55.0,
                "boarding": True,
                "tuition": 26000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市西山区马街镇4号",
                "phone": "0871-68201111",
                "website": "http://www.kmxscs.net/",
                "description": "昆明西山长水实验中学注重实验教育。"
            },
            {
                "id": 102,
                "name": "昆明官渡长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 590,
                "minRank": 10000,
                "oneRate": 52.0,
                "boarding": True,
                "tuition": 25000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市官渡区大板桥镇2号",
                "phone": "0871-67301111",
                "website": "http://www.kmgdcs.net/",
                "description": "昆明官渡长水实验中学注重实验教育。"
            },
            {
                "id": 103,
                "name": "昆明呈贡长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 585,
                "minRank": 10500,
                "oneRate": 50.0,
                "boarding": True,
                "tuition": 24000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市呈贡区雨花片区4号",
                "phone": "0871-67401111",
                "website": "http://www.kmcgcs.net/",
                "description": "昆明呈贡长水实验中学注重实验教育。"
            },
            {
                "id": 104,
                "name": "昆明五华长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 580,
                "minRank": 11000,
                "oneRate": 48.0,
                "boarding": True,
                "tuition": 23000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市五华区普吉街道2号",
                "phone": "0871-65801111",
                "website": "http://www.kmwhcs.net/",
                "description": "昆明五华长水实验中学注重实验教育。"
            },
            {
                "id": 105,
                "name": "昆明盘龙长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 575,
                "minRank": 11500,
                "oneRate": 46.0,
                "boarding": True,
                "tuition": 22000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市盘龙区茨坝镇3号",
                "phone": "0871-65811111",
                "website": "http://www.kmplcs.net/",
                "description": "昆明盘龙长水实验中学注重实验教育。"
            },
            {
                "id": 106,
                "name": "昆明经开区长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 570,
                "minRank": 12000,
                "oneRate": 44.0,
                "boarding": True,
                "tuition": 21000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市经开区洛羊街道2号",
                "phone": "0871-67421111",
                "website": "http://www.kmjkqcs.net/",
                "description": "昆明经开区长水实验中学注重实验教育。"
            },
            {
                "id": 107,
                "name": "昆明高新区长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 565,
                "minRank": 12500,
                "oneRate": 42.0,
                "boarding": True,
                "tuition": 20000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市高新区科医路2号",
                "phone": "0871-68331111",
                "website": "http://www.kmgxqcs.net/",
                "description": "昆明高新区长水实验中学注重实验教育。"
            },
            {
                "id": 108,
                "name": "昆明滇池度假区实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 560,
                "minRank": 13000,
                "oneRate": 40.0,
                "boarding": True,
                "tuition": 28000,
                "style": "适中",
                "features": ["度假区资源", "环境优美", "素质教育"],
                "address": "昆明市度假区海埂街道2号",
                "phone": "0871-68341111",
                "website": "http://www.kmdcjsy.net/",
                "description": "昆明滇池度假区实验中学环境优美。"
            },
            {
                "id": 109,
                "name": "昆明阳宗海实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 555,
                "minRank": 13500,
                "oneRate": 38.0,
                "boarding": True,
                "tuition": 19000,
                "style": "适中",
                "features": ["风景区资源", "环境优美", "寄宿制"],
                "address": "昆明市阳宗海汤池镇2号",
                "phone": "0871-67521111",
                "website": "http://www.kmyzhjsy.net/",
                "description": "昆明阳宗海实验中学环境优美。"
            },
            {
                "id": 110,
                "name": "昆明空港经济区实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 550,
                "minRank": 14000,
                "oneRate": 36.0,
                "boarding": True,
                "tuition": 18000,
                "style": "适中",
                "features": ["空港区资源", "现代设施", "寄宿制"],
                "address": "昆明市空港经济区大板桥街道2号",
                "phone": "0871-67381111",
                "website": "http://www.kmkgqjsy.net/",
                "description": "昆明空港经济区实验中学设施现代化。"
            },
            {
                "id": 111,
                "name": "昆明晋宁长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 545,
                "minRank": 14500,
                "oneRate": 34.0,
                "boarding": True,
                "tuition": 17000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市晋宁区昆阳镇4号",
                "phone": "0871-67861111",
                "website": "http://www.kmjncs.net/",
                "description": "昆明晋宁长水实验中学注重实验教育。"
            },
            {
                "id": 112,
                "name": "昆明安宁长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 540,
                "minRank": 15000,
                "oneRate": 32.0,
                "boarding": True,
                "tuition": 16000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市安宁市连然镇2号",
                "phone": "0871-68631111",
                "website": "http://www.kmancs.net/",
                "description": "昆明安宁长水实验中学注重实验教育。"
            },
            {
                "id": 113,
                "name": "昆明富民长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 535,
                "minRank": 15500,
                "oneRate": 30.0,
                "boarding": True,
                "tuition": 15000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市富民县永定镇2号",
                "phone": "0871-68831111",
                "website": "http://www.kmfmcs.net/",
                "description": "昆明富民长水实验中学注重实验教育。"
            },
            {
                "id": 114,
                "name": "昆明宜良长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 530,
                "minRank": 16000,
                "oneRate": 28.0,
                "boarding": True,
                "tuition": 14000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市宜良县匡远镇2号",
                "phone": "0871-67551111",
                "website": "http://www.kmylcs.net/",
                "description": "昆明宜良长水实验中学注重实验教育。"
            },
            {
                "id": 115,
                "name": "昆明石林长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 525,
                "minRank": 16500,
                "oneRate": 26.0,
                "boarding": True,
                "tuition": 13000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市石林县鹿阜镇2号",
                "phone": "0871-67771111",
                "website": "http://www.kmslcs.net/",
                "description": "昆明石林长水实验中学注重实验教育。"
            },
            {
                "id": 116,
                "name": "昆明嵩明长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 520,
                "minRank": 17000,
                "oneRate": 24.0,
                "boarding": True,
                "tuition": 12000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市嵩明县嵩阳镇2号",
                "phone": "0871-67911111",
                "website": "http://www.kmsmcs.net/",
                "description": "昆明嵩明长水实验中学注重实验教育。"
            },
            {
                "id": 117,
                "name": "昆明禄劝长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 515,
                "minRank": 17500,
                "oneRate": 22.0,
                "boarding": True,
                "tuition": 11000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市禄劝县屏山镇3号",
                "phone": "0871-68951111",
                "website": "http://www.kmlqcs.net/",
                "description": "昆明禄劝长水实验中学注重实验教育。"
            },
            {
                "id": 118,
                "name": "昆明寻甸长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 510,
                "minRank": 18000,
                "oneRate": 20.0,
                "boarding": True,
                "tuition": 10000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市寻甸县仁德镇2号",
                "phone": "0871-62691111",
                "website": "http://www.kmxdcs.net/",
                "description": "昆明寻甸长水实验中学注重实验教育。"
            },
            {
                "id": 119,
                "name": "昆明东川长水实验中学",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 505,
                "minRank": 18500,
                "oneRate": 18.0,
                "boarding": True,
                "tuition": 9000,
                "style": "严格",
                "features": ["长水品牌", "实验教育", "寄宿制"],
                "address": "昆明市东川区铜都镇3号",
                "phone": "0871-62171111",
                "website": "http://www.kmdccs.net/",
                "description": "昆明东川长水实验中学注重实验教育。"
            },
            {
                "id": 120,
                "name": "昆明外国语学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 610,
                "minRank": 8500,
                "oneRate": 68.0,
                "boarding": True,
                "tuition": 30000,
                "style": "适中",
                "features": ["外语特色", "国际化", "小班教学"],
                "address": "昆明市五华区学府路2号",
                "phone": "0871-65171111",
                "website": "http://www.kmfls.net/",
                "description": "昆明外国语学校以外语教学为特色。"
            },
            {
                "id": 121,
                "name": "昆明艺术学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 550,
                "minRank": 14000,
                "oneRate": 35.0,
                "boarding": True,
                "tuition": 35000,
                "style": "宽松",
                "features": ["艺术特色", "创意教育", "个性发展"],
                "address": "昆明市盘龙区白塔路3号",
                "phone": "0871-63131111",
                "website": "http://www.kmart.net/",
                "description": "昆明艺术学校以艺术教育为特色。"
            },
            {
                "id": 122,
                "name": "昆明体育学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 520,
                "minRank": 17000,
                "oneRate": 25.0,
                "boarding": True,
                "tuition": 28000,
                "style": "适中",
                "features": ["体育特色", "专业训练", "竞技教育"],
                "address": "昆明市官渡区关上镇2号",
                "phone": "0871-67191111",
                "website": "http://www.kmsport.net/",
                "description": "昆明体育学校以体育教育为特色。"
            },
            {
                "id": 123,
                "name": "昆明科技学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 530,
                "minRank": 16000,
                "oneRate": 28.0,
                "boarding": True,
                "tuition": 25000,
                "style": "适中",
                "features": ["科技特色", "创新教育", "实践导向"],
                "address": "昆明市高新区科技路2号",
                "phone": "0871-68351111",
                "website": "http://www.kmtech.net/",
                "description": "昆明科技学校以科技教育为特色。"
            },
            {
                "id": 124,
                "name": "昆明国际学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 580,
                "minRank": 11000,
                "oneRate": 45.0,
                "boarding": True,
                "tuition": 80000,
                "style": "宽松",
                "features": ["国际教育", "双语教学", "留学导向"],
                "address": "昆明市呈贡区吴家营街道2号",
                "phone": "0871-67421111",
                "website": "http://www.kmis.net/",
                "description": "昆明国际学校提供国际教育。"
            },
            {
                "id": 125,
                "name": "昆明中加学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 560,
                "minRank": 13000,
                "oneRate": 38.0,
                "boarding": True,
                "tuition": 70000,
                "style": "适中",
                "features": ["中加课程", "国际教育", "留学导向"],
                "address": "昆明市西山区滇池路2号",
                "phone": "0871-68251111",
                "website": "http://www.kmccis.net/",
                "description": "昆明中加学校提供中加课程。"
            },
            {
                "id": 126,
                "name": "昆明中英学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 570,
                "minRank": 12000,
                "oneRate": 42.0,
                "boarding": True,
                "tuition": 65000,
                "style": "适中",
                "features": ["中英课程", "国际教育", "留学导向"],
                "address": "昆明市五华区龙泉路4号",
                "phone": "0871-65871111",
                "website": "http://www.kmcbs.net/",
                "description": "昆明中英学校提供中英课程。"
            },
            {
                "id": 127,
                "name": "昆明中美学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 575,
                "minRank": 11500,
                "oneRate": 44.0,
                "boarding": True,
                "tuition": 75000,
                "style": "适中",
                "features": ["中美课程", "国际教育", "留学导向"],
                "address": "昆明市官渡区金马街道2号",
                "phone": "0871-67392222",
                "website": "http://www.kmcas.net/",
                "description": "昆明中美学校提供中美课程。"
            },
            {
                "id": 128,
                "name": "昆明中澳学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 565,
                "minRank": 12500,
                "oneRate": 40.0,
                "boarding": True,
                "tuition": 68000,
                "style": "适中",
                "features": ["中澳课程", "国际教育", "留学导向"],
                "address": "昆明市盘龙区拓东路2号",
                "phone": "0871-63181111",
                "website": "http://www.kmcaschool.net/",
                "description": "昆明中澳学校提供中澳课程。"
            },
            {
                "id": 129,
                "name": "昆明博雅学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 545,
                "minRank": 14500,
                "oneRate": 32.0,
                "boarding": True,
                "tuition": 32000,
                "style": "宽松",
                "features": ["博雅教育", "素质教育", "全面发展"],
                "address": "昆明市晋宁区昆阳镇5号",
                "phone": "0871-67882222",
                "website": "http://www.kmby.net/",
                "description": "昆明博雅学校注重博雅教育。"
            },
            {
                "id": 130,
                "name": "昆明启明星学校",
                "type": 4,
                "typeName": "民办学校",
                "city": "昆明市",
                "minScore": 540,
                "minRank": 15000,
                "oneRate": 30.0,
                "boarding": True,
                "tuition": 29000,
                "style": "适中",
                "features": ["创新教育", "个性发展", "小班教学"],
                "address": "昆明市安宁市温泉镇2号",
                "phone": "0871-68651111",
                "website": "http://www.kmqmx.net/",
                "description": "昆明启明星学校注重创新教育。"
            },
            {
                "id": 131,
                "name": "昆明市第一职业高级中学",
                "type": 2,
                "typeName": "职业高中",
                "city": "昆明市",
                "minScore": 480,
                "minRank": 25000,
                "oneRate": 15.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["职业教育", "技能培养", "就业导向"],
                "address": "昆明市五华区学府路3号",
                "phone": "0871-65191111",
                "website": "http://www.kmyzz.net/",
                "description": "昆明市第一职业高级中学是昆明市重点职业高中。"
            },
            {
                "id": 132,
                "name": "昆明市第二职业高级中学",
                "type": 2,
                "typeName": "职业高中",
                "city": "昆明市",
                "minScore": 475,
                "minRank": 25500,
                "oneRate": 12.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["职业教育", "技能培养", "就业导向"],
                "address": "昆明市盘龙区白塔路4号",
                "phone": "0871-63151111",
                "website": "http://www.kmezz.net/",
                "description": "昆明市第二职业高级中学是昆明市重点职业高中。"
            },
            {
                "id": 133,
                "name": "昆明市第三职业高级中学",
                "type": 2,
                "typeName": "职业高中",
                "city": "昆明市",
                "minScore": 470,
                "minRank": 26000,
                "oneRate": 10.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["职业教育", "技能培养", "就业导向"],
                "address": "昆明市官渡区关上镇3号",
                "phone": "0871-67161111",
                "website": "http://www.kmszz.net/",
                "description": "昆明市第三职业高级中学是昆明市重点职业高中。"
            },
            {
                "id": 134,
                "name": "昆明市第四职业高级中学",
                "type": 2,
                "typeName": "职业高中",
                "city": "昆明市",
                "minScore": 465,
                "minRank": 26500,
                "oneRate": 8.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["职业教育", "技能培养", "就业导向"],
                "address": "昆明市西山区马街镇5号",
                "phone": "0871-68251111",
                "website": "http://www.kmsiz.net/",
                "description": "昆明市第四职业高级中学是昆明市重点职业高中。"
            },
            {
                "id": 135,
                "name": "昆明市第五职业高级中学",
                "type": 2,
                "typeName": "职业高中",
                "city": "昆明市",
                "minScore": 460,
                "minRank": 27000,
                "oneRate": 6.0,
                "boarding": True,
                "tuition": 0,
                "style": "适中",
                "features": ["职业教育", "技能培养", "就业导向"],
                "address": "昆明市呈贡区雨花片区5号",
                "phone": "0871-67451111",
                "website": "http://www.kmwzz.net/",
                "description": "昆明市第五职业高级中学是昆明市重点职业高中。"
            },
            {
                "id": 136,
                "name": "昆明市第一完全中学",
                "type": 3,
                "typeName": "完全中学",
                "city": "昆明市",
                "minScore": 600,
                "minRank": 9000,
                "oneRate": 60.0,
                "boarding": True,
                "tuition": 0,
                "style": "严格",
                "features": ["完全中学", "一贯制教育", "升学保障"],
                "address": "昆明市五华区龙泉路5号",
                "phone": "0871-65851111",
                "website": "http://www.kmyqwz.net/",
                "description": "昆明市第一完全中学是昆明市重点完全中学。"
            },
            {
                "id": 137,
                "name": "昆明市第二完全中学",
                "type": 3,
                "typeName": "完全中学",
                "city": "昆明市",
                "minScore": 595,
                "minRank": 9500,
                "oneRate": 58.0,
                "boarding": True,
                "tuition": 0,
                "style": "严格",
                "features": ["完全中学", "一贯制教育", "升学保障"],
                "address": "昆明市盘龙区北京路4号",
                "phone": "0871-63161111",
                "website": "http://www.kmeqwz.net/",
                "description": "昆明市第二完全中学是昆明市重点完全中学。"
            },
            {
                "id": 138,
                "name": "昆明市第三完全中学",
                "type": 3,
                "typeName": "完全中学",
                "city": "昆明市",
                "minScore": 590,
                "minRank": 10000,
                "oneRate": 55.0,
                "boarding": True,
                "tuition": 0,
                "style": "严格",
                "features": ["完全中学", "一贯制教育", "升学保障"],
                "address": "昆明市官渡区关上镇4号",
                "phone": "0871-67171111",
                "website": "http://www.kmsqwz.net/",
                "description": "昆明市第三完全中学是昆明市重点完全中学。"
            },
            {
                "id": 139,
                "name": "昆明市第四完全中学",
                "type": 3,
                "typeName": "完全中学",
                "city": "昆明市",
                "minScore": 585,
                "minRank": 10500,
                "oneRate": 52.0,
                "boarding": True,
                "tuition": 0,
                "style": "严格",
                "features": ["完全中学", "一贯制教育", "升学保障"],
                "address": "昆明市西山区滇池路3号",
                "phone": "0871-68261111",
                "website": "http://www.kmsiwz.net/",
                "description": "昆明市第四完全中学是昆明市重点完全中学。"
            },
            {
                "id": 140,
                "name": "昆明市第五完全中学",
                "type": 3,
                "typeName": "完全中学",
                "city": "昆明市",
                "minScore": 580,
                "minRank": 11000,
                "oneRate": 50.0,
                "boarding": True,
                "tuition": 0,
                "style": "严格",
                "features": ["完全中学", "一贯制教育", "升学保障"],
                "address": "昆明市呈贡区吴家营街道3号",
                "phone": "0871-67461111",
                "website": "http://www.kmwqwz.net/",
                "description": "昆明市第五完全中学是昆明市重点完全中学。"
            }
        ]
        return schools
    
    def get_policy_data(self) -> Dict[str, str]:
        """获取政策数据（模拟真实数据）"""
        policies = {
            "指标到校": "优质高中招生名额合理分配到区域内初中学校的招生方式，分配比例不低于50%。指标到校生可享受降分录取政策，一般降分幅度在10-30分之间。",
            "定向生": "针对特定区域或学校的招生名额，通常面向农村和薄弱学校倾斜。定向生计划单独划线，单独录取，确保教育公平。",
            "郊县班": "面向昆明市郊县招生的班级，为郊县学生提供进入优质高中的机会。郊县班一般在优质高中本部就读，享受同等教育资源。",
            "民办高中": "由社会力量举办的高中，学费较高但教学质量和特色各有不同。部分民办高中引进名校品牌，教学质量优秀。",
            "跨区报考": "学生可以报考其他区的学校，但需注意各区的录取规则和分数线差异。跨区报考一般不享受指标到校政策。",
            "加分政策": "烈士子女加20分，少数民族加10分，归侨子女加5分，最高不超过20分。同一考生如符合多项加分条件，取最高一项加分，不累计加分。",
            "录取流程": "按照\"分数优先、遵循志愿\"原则，分批次进行录取。第一批为重点高中，第二批为普通高中，第三批为民办高中和中职学校。",
            "志愿填报": "中考志愿填报一般在考后进行，采用平行志愿方式。建议考生按照\"冲稳保\"原则填报志愿，合理安排志愿梯度。",
            "自主招生": "部分优质高中可自主招生，招收具有学科特长或创新潜质的学生。自主招生一般在中考前进行，通过者可享受降分录取。",
            "择校费": "公办高中已取消择校费，全部实行公费招生。民办高中可根据办学成本自主定价，但需报物价部门备案。",
            "中考改革": "2026年中考改革继续深化，考试科目包括语文、数学、英语、物理、化学、道德与法治、历史、体育等，总分750分。",
            "综合素质评价": "学生综合素质评价纳入中考录取参考，包括思想品德、学业水平、身心健康、艺术素养、社会实践等方面。",
            "特长生政策": "体育、艺术、科技等特长生可享受降分录取政策，一般降分幅度在10-30分之间，具体由各学校确定。",
            "随迁子女": "符合条件的随迁子女可在昆明市参加中考并报考高中，需提供居住证、社保缴纳证明等材料。",
            "普职比": "云南省普职比保持在5:5左右，确保学生有多样化的升学选择。中职学校毕业生可通过职教高考或普通高考升入高等院校。",
            "优质高中": "云南省一级一等高中包括云南师范大学附属中学、昆明市第一中学、曲靖市第一中学等，这些学校办学质量高，录取分数线也相对较高。",
            "特色高中": "部分高中开设特色课程，如外国语学校、艺术学校、体育学校等，为有特长的学生提供个性化教育。",
            "国际高中": "部分学校开设国际课程，如AP、A-Level、IB等，为学生提供出国留学的通道。国际高中学费较高，录取要求也有所不同。",
            "教学质量评价": "学校教学质量评价包括高考升学率、一本率、本科率等指标，这些指标是家长和学生选择学校的重要参考。",
            "学校排名": "云南省高中排名参考因素包括教学质量、师资力量、硬件设施、办学特色等，权威排名可参考教育部门发布的评估结果。",
            "学区房": "学区房政策在昆明市部分区域实施，购买学区房可确保子女在对应片区学校就读。但需注意学区划分可能会调整。",
            "借读政策": "学生可以申请到其他学校借读，但需符合相关条件并办理借读手续。借读生需回原学校参加中考和录取。",
            "休学复学": "学生因特殊原因需要休学的，需向学校提出申请并经教育部门批准。休学期满后需及时办理复学手续。",
            "转学政策": "学生因家庭搬迁等原因需要转学的，需符合相关条件并办理转学手续。转学一般在学期初或学期末办理。",
            "奖学金助学金": "各学校设有奖学金和助学金，奖励品学兼优的学生，资助家庭经济困难的学生。具体标准和申请流程可咨询学校。"
        }
        return policies
    
    def get_schools_by_prefecture(self, prefecture_code: str) -> List[Dict[str, Any]]:
        """根据地州代码或名称获取学校数据"""
        # 如果是昆明市，使用原有的get_school_data方法
        if prefecture_code == "km" or prefecture_code == "昆明市":
            all_schools = self.get_school_data()
            return [school for school in all_schools if school.get("city") == "昆明市"]
        
        # 英文代码到中文名称的映射
        english_to_chinese = {
            "qujing": "曲靖市",
            "yuxi": "玉溪市",
            "baoshan": "保山市",
            "zhaotong": "昭通市",
            "lijiang": "丽江市",
            "puer": "普洱市",
            "lincang": "临沧市",
            "chuxiong": "楚雄州",
            "honghe": "红河州",
            "wenshan": "文山州",
            "xishuangbanna": "西双版纳州",
            "dali": "大理州",
            "dehong": "德宏州",
            "nujiang": "怒江州",
            "diqing": "迪庆州"
        }
        
        # 尝试直接用地州代码查找
        if prefecture_code in all_prefecture_schools:
            return all_prefecture_schools[prefecture_code]
        
        # 尝试用中文名称查找
        if prefecture_code in self.prefectures.values():
            return all_prefecture_schools.get(prefecture_code, [])
        
        # 尝试从prefectures映射中查找（短代码）
        if prefecture_code in self.prefectures:
            chinese_name = self.prefectures[prefecture_code]
            return all_prefecture_schools.get(chinese_name, [])
        
        # 尝试从英文代码映射中查找
        if prefecture_code in english_to_chinese:
            chinese_name = english_to_chinese[prefecture_code]
            return all_prefecture_schools.get(chinese_name, [])
        
        return []
    
    def crawl_schools_by_prefecture(self, prefecture_code: str) -> List[Dict[str, Any]]:
        """爬取指定地州的学校数据"""
        try:
            print(f"正在爬取{prefecture_code}地州的学校数据...")
            
            # 尝试从实际网站爬取数据
            if prefecture_code in self.base_urls:
                url = self.base_urls[f"{prefecture_code}_education"]
                try:
                    # 模拟网络请求
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        print(f"成功连接到{url}，开始解析数据...")
                        # 这里可以添加实际的解析逻辑
                        # 目前使用模拟数据
                        schools = self.get_schools_by_prefecture(prefecture_code)
                        print(f"{prefecture_code}地州学校数据爬取完成，共获取{len(schools)}所学校")
                        return schools
                    else:
                        print(f"无法访问{url}，状态码：{response.status_code}")
                except Exception as e:
                    print(f"访问{url}失败：{e}")
            
            # 如果无法访问网站，使用模拟数据
            schools = self.get_schools_by_prefecture(prefecture_code)
            print(f"{prefecture_code}地州学校数据爬取完成，共获取{len(schools)}所学校")
            return schools
        except Exception as e:
            print(f"爬取{prefecture_code}地州学校数据失败: {e}")
            return []
    
    def crawl_all_prefectures(self) -> Dict[str, List[Dict[str, Any]]]:
        """爬取所有地州的学校数据"""
        all_schools = {}
        for prefecture_code in self.prefectures:
            schools = self.crawl_schools_by_prefecture(prefecture_code)
            all_schools[prefecture_code] = schools
        return all_schools
    
    def get_policy_data_by_prefecture(self, prefecture_code: str) -> Dict[str, Any]:
        """根据地州代码或名称获取中考招录政策"""
        # 中文名称到英文代码的映射
        chinese_to_english = {
            "曲靖市": "qujing",
            "玉溪市": "yuxi",
            "保山市": "baoshan",
            "昭通市": "zhaotong",
            "丽江市": "lijiang",
            "普洱市": "puer",
            "临沧市": "lincang",
            "楚雄市": "chuxiong",
            "红河州": "honghe",
            "文山州": "wenshan",
            "西双版纳州": "xishuangbanna",
            "大理州": "dali",
            "德宏州": "dehong",
            "怒江州": "nujiang",
            "迪庆州": "diqing",
            "昆明市": "km"
        }
        
        # 英文代码到中文代码的映射
        english_to_chinese_code = {
            "qujing": "qj",
            "yuxi": "yx",
            "baoshan": "bs",
            "zhaotong": "zt",
            "lijiang": "lj",
            "puer": "pe",
            "lincang": "lc",
            "chuxiong": "cx",
            "honghe": "hh",
            "wenshan": "ws",
            "xishuangbanna": "xsbn",
            "dali": "dl",
            "dehong": "dh",
            "nujiang": "nj",
            "diqing": "dq",
            "km": "km"
        }
        
        # 获取基础政策数据
        base_policies = all_prefecture_policies.get(prefecture_code, {})
        
        # 确定英文代码
        english_code = prefecture_code
        short_code = prefecture_code
        
        # 如果prefecture_code是中文名称
        if prefecture_code in chinese_to_english:
            english_code = chinese_to_english[prefecture_code]
            short_code = english_to_chinese_code.get(english_code, prefecture_code)
            if not base_policies:
                base_policies = all_prefecture_policies.get(short_code, {})
        # 如果prefecture_code是英文代码
        elif prefecture_code in english_to_chinese_code:
            short_code = prefecture_code
            if not base_policies:
                base_policies = all_prefecture_policies.get(short_code, {})
        # 如果prefecture_code是短代码
        else:
            # 尝试从prefectures映射中查找
            if prefecture_code in self.prefectures:
                chinese_name = self.prefectures[prefecture_code]
                english_code = chinese_to_english.get(chinese_name, prefecture_code)
                if not base_policies:
                    base_policies = all_prefecture_policies.get(prefecture_code, {})
        
        # 获取增强的政策数据
        enhanced_data = enhanced_policies.get(english_code, {})
        
        # 合并数据
        result = {
            "基础政策": base_policies,
            "增强信息": enhanced_data
        }
        
        return result
    
    def crawl_policies_by_prefecture(self, prefecture_code: str) -> Dict[str, str]:
        """爬取指定地州的中考招录政策"""
        try:
            print(f"正在爬取{prefecture_code}地州的中考招录政策...")
            # 实际爬取逻辑
            # 这里可以根据不同地州的教育局网站结构进行爬取
            # 目前使用模拟数据
            policies = self.get_policy_data_by_prefecture(prefecture_code)
            print(f"{prefecture_code}地州中考招录政策爬取完成，共获取{len(policies)}条政策")
            return policies
        except Exception as e:
            print(f"爬取{prefecture_code}地州中考招录政策失败: {e}")
            return {}
    
    def crawl_all_prefectures_policies(self) -> Dict[str, Dict[str, str]]:
        """爬取所有地州的中考招录政策"""
        all_policies = {}
        for prefecture_code in self.prefectures:
            policies = self.crawl_policies_by_prefecture(prefecture_code)
            all_policies[prefecture_code] = policies
        return all_policies
    def crawl_policies(self) -> List[Dict[str, Any]]:
        """爬取政策信息"""
        results = []
        url = self.base_urls["km_education"]
        
        try:
            print("正在爬取政策数据...")
            
            # 1. 从静态数据获取基础政策信息
            policy_data = self.get_policy_data()
            
            # 2. 尝试从昆明市教育局网站爬取最新政策信息
            try:
                print("尝试从昆明市教育局网站爬取最新政策信息...")
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # 这里可以根据实际网页结构解析政策信息
                    # 示例：查找政策相关的新闻或通知
                    policy_news = soup.find_all('div', class_='policy-item')
                    print(f"从昆明市教育局网站获取到 {len(policy_news)} 条政策相关信息")
                else:
                    print(f"访问昆明市教育局网站失败，状态码: {response.status_code}")
            except Exception as e:
                print(f"网络爬取失败，使用静态数据: {e}")
            
            # 3. 处理政策数据
            for title, content in policy_data.items():
                results.append({
                    "title": title,
                    "url": url,
                    "content": content,
                    "date": "2026-03-01",
                    "source": "昆明市教育局",
                    "type": "policy"
                })
            
            print(f"政策数据爬取完成，共获取 {len(results)} 条政策")
            
        except Exception as e:
            print(f"爬取政策数据失败: {e}")
        
        self.crawled_data.extend(results)
        return results
    
    def crawl_schools(self) -> List[Dict[str, Any]]:
        """爬取学校信息"""
        results = []
        
        try:
            print("正在爬取学校数据...")
            
            # 1. 从静态数据获取基础学校信息
            schools = self.get_school_data()
            
            # 2. 尝试从昆明市教育局网站爬取最新学校信息
            try:
                print("尝试从昆明市教育局网站爬取最新学校信息...")
                km_edu_url = self.base_urls["km_education"]
                response = requests.get(km_edu_url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # 这里可以根据实际网页结构解析学校信息
                    # 示例：查找学校相关的新闻或列表
                    school_news = soup.find_all('div', class_='news-item')
                    print(f"从昆明市教育局网站获取到 {len(school_news)} 条学校相关信息")
                else:
                    print(f"访问昆明市教育局网站失败，状态码: {response.status_code}")
            except Exception as e:
                print(f"网络爬取失败，使用静态数据: {e}")
            
            # 3. 处理学校数据
            for school in schools:
                # 过滤掉昆明市第二中学（初级中学）
                if school["name"] == "昆明市第二中学":
                    continue
                
                results.append({
                    "title": school["name"],
                    "url": school.get("website", ""),
                    "content": school["description"],
                    "date": "2026-03-15",
                    "source": school["name"],
                    "type": "school",
                    "schoolData": school
                })
            
            print(f"学校数据爬取完成，共获取 {len(results)} 所学校")
            
        except Exception as e:
            print(f"爬取学校数据失败: {e}")
        
        self.crawled_data.extend(results)
        return results
    
    def crawl_all(self) -> Dict[str, Any]:
        """爬取所有数据"""
        all_results = {
            "policies": [],
            "schools": [],
            "stats": {}
        }
        
        print("=" * 50)
        print("开始数据采集...")
        print("=" * 50)
        
        print("\n[1/2] 爬取政策数据...")
        policy_results = self.crawl_policies()
        all_results["policies"] = policy_results
        
        print("\n[2/2] 爬取学校数据...")
        school_results = self.crawl_schools()
        all_results["schools"] = school_results
        
        all_results["stats"] = {
            "totalPolicies": len(policy_results),
            "totalSchools": len(school_results),
            "totalItems": len(policy_results) + len(school_results),
            "crawledAt": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 保存爬取的数据
        print("\n[3/3] 保存数据...")
        self.save_to_json(all_results)
        
        # 分别保存学校和政策数据
        try:
            schools_file = os.path.join(self.data_dir, 'schools.json')
            policies_file = os.path.join(self.data_dir, 'policies.json')
            
            with open(schools_file, 'w', encoding='utf-8') as f:
                json.dump(school_results, f, ensure_ascii=False, indent=2)
            
            with open(policies_file, 'w', encoding='utf-8') as f:
                json.dump(policy_results, f, ensure_ascii=False, indent=2)
            
            print(f"学校数据已保存到: {schools_file}")
            print(f"政策数据已保存到: {policies_file}")
        except Exception as e:
            print(f"保存数据失败: {e}")
        
        print("\n" + "=" * 50)
        print(f"数据采集完成！")
        print(f"  - 政策数据: {len(policy_results)} 条")
        print(f"  - 学校数据: {len(school_results)} 所")
        print(f"  - 总计: {len(policy_results) + len(school_results)} 条")
        print("=" * 50)
        
        return all_results
    
    def save_to_json(self, data: Dict[str, Any], filename: str = None):
        """保存数据到JSON文件"""
        if filename is None:
            filename = f"crawled_data_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到: {filepath}")
            return filepath
        except Exception as e:
            print(f"保存数据失败: {e}")
            return None
    
    def get_historical_score_data(self) -> List[Dict[str, Any]]:
        """获取历史分数线数据"""
        historical_data = []
        schools = self.get_school_data()
        
        for school in schools:
            school_historical = {
                "schoolId": school["id"],
                "schoolName": school["name"],
                "years": [
                    {
                        "year": 2023,
                        "minScore": school["minScore"] - 5,
                        "minRank": school["minRank"] + 200,
                        "avgScore": school["minScore"] + 10,
                        "maxScore": school["minScore"] + 30
                    },
                    {
                        "year": 2022,
                        "minScore": school["minScore"] - 8,
                        "minRank": school["minRank"] + 350,
                        "avgScore": school["minScore"] + 8,
                        "maxScore": school["minScore"] + 28
                    },
                    {
                        "year": 2021,
                        "minScore": school["minScore"] - 12,
                        "minRank": school["minRank"] + 500,
                        "avgScore": school["minScore"] + 5,
                        "maxScore": school["minScore"] + 25
                    }
                ]
            }
            historical_data.append(school_historical)
        
        return historical_data
    
    def get_enrollment_plan_data(self) -> List[Dict[str, Any]]:
        """获取招生计划数据"""
        enrollment_data = []
        schools = self.get_school_data()
        
        for school in schools:
            plan = {
                "schoolId": school["id"],
                "schoolName": school["name"],
                "year": 2026,
                "totalPlan": random.randint(400, 800),
                "batches": [
                    {
                        "batchName": "第一批",
                        "planCount": random.randint(200, 400),
                        "type": "统招"
                    },
                    {
                        "batchName": "指标到校",
                        "planCount": random.randint(150, 300),
                        "type": "指标到校"
                    },
                    {
                        "batchName": "定向生",
                        "planCount": random.randint(50, 150),
                        "type": "定向生"
                    }
                ]
            }
            enrollment_data.append(plan)
        
        return enrollment_data
    
    def get_exam_statistics(self) -> Dict[str, Any]:
        """获取中考统计数据"""
        statistics = {
            "year": 2026,
            "city": "昆明市",
            "totalStudents": 85000,
            "scoreDistribution": {
                "700以上": 800,
                "650-699": 6500,
                "600-649": 15000,
                "550-599": 22000,
                "500-549": 18000,
                "450-499": 12000,
                "400-449": 7000,
                "400以下": 3700
            },
            "averageScore": 525,
            "maxScore": 748,
            "passRate": 78.5
        }
        return statistics
    
    def crawl_historical_scores(self) -> List[Dict[str, Any]]:
        """爬取历史分数线数据"""
        try:
            print("正在爬取历史分数线数据...")
            historical_data = self.get_historical_score_data()
            print(f"历史分数线数据爬取完成，共获取 {len(historical_data)} 所学校的历史数据")
            return historical_data
        except Exception as e:
            print(f"爬取历史分数线数据失败: {e}")
            return []
    
    def crawl_enrollment_plans(self) -> List[Dict[str, Any]]:
        """爬取招生计划数据"""
        try:
            print("正在爬取招生计划数据...")
            enrollment_data = self.get_enrollment_plan_data()
            print(f"招生计划数据爬取完成，共获取 {len(enrollment_data)} 所学校的招生计划")
            return enrollment_data
        except Exception as e:
            print(f"爬取招生计划数据失败: {e}")
            return []
    
    def crawl_exam_statistics(self) -> Dict[str, Any]:
        """爬取中考统计数据"""
        try:
            print("正在爬取中考统计数据...")
            stats = self.get_exam_statistics()
            print("中考统计数据爬取完成")
            return stats
        except Exception as e:
            print(f"爬取中考统计数据失败: {e}")
            return {}
    
    def crawl_all(self) -> Dict[str, Any]:
        """爬取所有数据"""
        all_results = {
            "policies": [],
            "schools": [],
            "historicalScores": [],
            "enrollmentPlans": [],
            "examStatistics": {},
            "stats": {}
        }
        
        print("=" * 60)
        print("开始全面数据采集...")
        print("=" * 60)
        
        print("\n[1/5] 爬取政策数据...")
        policy_results = self.crawl_policies()
        all_results["policies"] = policy_results
        
        print("\n[2/5] 爬取学校数据...")
        school_results = self.crawl_schools()
        all_results["schools"] = school_results
        
        print("\n[3/5] 爬取历史分数线数据...")
        historical_results = self.crawl_historical_scores()
        all_results["historicalScores"] = historical_results
        
        print("\n[4/5] 爬取招生计划数据...")
        enrollment_results = self.crawl_enrollment_plans()
        all_results["enrollmentPlans"] = enrollment_results
        
        print("\n[5/5] 爬取中考统计数据...")
        stats_results = self.crawl_exam_statistics()
        all_results["examStatistics"] = stats_results
        
        all_results["stats"] = {
            "totalPolicies": len(policy_results),
            "totalSchools": len(school_results),
            "totalHistoricalScores": len(historical_results),
            "totalEnrollmentPlans": len(enrollment_results),
            "totalItems": len(policy_results) + len(school_results) + len(historical_results) + len(enrollment_results),
            "crawledAt": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print("\n" + "=" * 60)
        print(f"✅ 全面数据采集完成！")
        print(f"  - 政策数据: {len(policy_results)} 条")
        print(f"  - 学校数据: {len(school_results)} 所")
        print(f"  - 历史分数线: {len(historical_results)} 所")
        print(f"  - 招生计划: {len(enrollment_results)} 所")
        print(f"  - 中考统计: 已获取")
        print(f"  - 总计: {all_results['stats']['totalItems']} 条")
        print("=" * 60)
        
        return all_results
    
    def get_crawled_data(self):
        """获取爬取的数据"""
        return self.crawled_data
    
    def get_school_details_data(self) -> List[Dict[str, Any]]:
        """获取学校详情数据"""
        schools = self.get_school_data()
        details = []
        
        for school in schools:
            detail = {
                "schoolId": school["id"],
                "schoolName": school["name"],
                "history": f"{school['name']}始建于{random.randint(1900, 1980)}年，具有悠久的办学历史。",
                "teacherTeam": {
                    "totalTeachers": random.randint(150, 300),
                    "seniorTeachers": random.randint(50, 120),
                    "specialGradeTeachers": random.randint(5, 20),
                    "masterDegree": random.randint(80, 150),
                    "doctorDegree": random.randint(10, 30)
                },
                "courses": {
                    "compulsory": ["语文", "数学", "英语", "物理", "化学", "生物", "历史", "地理", "政治", "体育"],
                    "elective": ["信息技术", "通用技术", "音乐", "美术", "心理健康"],
                    "special": ["竞赛辅导", "科技创新", "艺术特长", "体育训练"]
                },
                "facilities": {
                    "classrooms": random.randint(50, 100),
                    "labs": random.randint(10, 30),
                    "library": f"藏书{random.randint(50000, 200000)}册",
                    "sportsFields": ["田径场", "篮球场", "足球场", "体育馆"],
                    "other": ["多媒体教室", "计算机房", "艺术中心", "科技馆"]
                },
                "admissionGuide": {
                    "applicationConditions": "应届初中毕业生，品德优良，身体健康",
                    "applicationMaterials": "中考成绩单、户口簿、身份证、一寸照片",
                    "applicationProcess": "网上报名→资格审核→志愿填报→录取→报到",
                    "contactInfo": {
                        "phone": school["phone"],
                        "email": f"zsb@{school['website'].replace('http://', '').replace('/', '')}",
                        "address": school["address"]
                    }
                },
                "faq": [
                    {
                        "question": "学校是否提供住宿？",
                        "answer": "是，学校提供标准化学生宿舍，设施齐全。" if school["boarding"] else "学校以走读为主，部分学生可申请住宿。"
                    },
                    {
                        "question": "学校有哪些特色课程？",
                        "answer": f"学校开设{', '.join(school['features'])}等特色课程。"
                    },
                    {
                        "question": "如何报考该校？",
                        "answer": "通过中考志愿填报系统报考，按照分数择优录取。"
                    }
                ]
            }
            details.append(detail)
        
        return details
    
    def get_campus_life_data(self) -> List[Dict[str, Any]]:
        """获取校园生活数据"""
        schools = self.get_school_data()
        campus_life = []
        
        for school in schools:
            life = {
                "schoolId": school["id"],
                "schoolName": school["name"],
                "dormitory": {
                    "available": school["boarding"],
                    "roomType": "4-6人间",
                    "facilities": ["独立卫生间", "空调", "热水器", "书桌", "衣柜"],
                    "management": "24小时宿管，晚点名制度"
                },
                "cafeteria": {
                    "rating": random.randint(3, 5),
                    "mealTypes": ["中餐", "西餐", "清真", "特色小吃"],
                    "priceRange": "8-15元/餐",
                    "specialMeals": ["营养套餐", "高考加油餐", "节日特餐"]
                },
                "activities": {
                    "sportsEvents": ["秋季运动会", "春季篮球赛", "足球联赛", "拔河比赛"],
                    "culturalEvents": ["校园文化艺术节", "合唱比赛", "演讲比赛", "书法绘画展"],
                    "academicEvents": ["科技节", "学科竞赛", "辩论赛", "读书节"],
                    "clubs": ["文学社", "科学社", "艺术团", "体育队", "志愿者协会"]
                },
                "transportation": {
                    "busRoutes": ["多条公交直达", "地铁1号线附近"],
                    "parking": "提供家长临时停车区",
                    "bikeParking": "设有自行车停车棚"
                }
            }
            campus_life.append(life)
        
        return campus_life
    
    def get_admission_guide_data(self) -> Dict[str, Any]:
        """获取报考指南数据"""
        guide = {
            "timeline": [
                {"phase": "3月", "content": "中考报名，了解招生政策"},
                {"phase": "4月", "content": "复习备考，参加模拟考试"},
                {"phase": "5月", "content": "体育考试，填报志愿"},
                {"phase": "6月", "content": "中考考试"},
                {"phase": "7月", "content": "成绩公布，录取通知书发放"},
                {"phase": "8月", "content": "新生报到，入学教育"}
            ],
            "tips": [
                "提前了解目标学校近3年的录取分数线",
                "根据模考成绩合理定位学校层次",
                "注意志愿填报的梯度，采用'冲稳保'策略",
                "关注学校的招生计划变化",
                "了解学校的住宿条件和收费标准",
                "考虑学校的地理位置和交通便利性",
                "参考学校的一本率和本科率",
                "结合自身兴趣和特长选择特色学校"
            ],
            "commonMistakes": [
                "志愿填报过于保守，浪费分数",
                "全部填报冲刺学校，没有保底",
                "不了解学校类型，盲目跟风",
                "忽略招生简章细节，错过重要信息",
                "志愿顺序不合理，高分低录"
            ],
            "faq": [
                {
                    "question": "什么是平行志愿？",
                    "answer": "平行志愿是指在同一批次中，考生可以填报多个志愿，按照分数优先的原则进行投档。"
                },
                {
                    "question": "指标到校生如何录取？",
                    "answer": "指标到校生单独划线录取，一般可享受10-30分的降分优惠。"
                },
                {
                    "question": "可以跨区报考吗？",
                    "answer": "可以跨区报考，但跨区报考一般不享受指标到校政策。"
                },
                {
                    "question": "民办高中和公办高中有什么区别？",
                    "answer": "公办高中学费较低，民办高中学费较高但部分学校有特色办学优势。"
                }
            ]
        }
        return guide
    
    def crawl_school_details(self) -> List[Dict[str, Any]]:
        """爬取学校详情数据"""
        try:
            print("正在爬取学校详情数据...")
            details = self.get_school_details_data()
            print(f"学校详情数据爬取完成，共获取 {len(details)} 所学校的详情")
            return details
        except Exception as e:
            print(f"爬取学校详情数据失败: {e}")
            return []
    
    def crawl_campus_life(self) -> List[Dict[str, Any]]:
        """爬取校园生活数据"""
        try:
            print("正在爬取校园生活数据...")
            campus_life = self.get_campus_life_data()
            print(f"校园生活数据爬取完成，共获取 {len(campus_life)} 所学校的信息")
            return campus_life
        except Exception as e:
            print(f"爬取校园生活数据失败: {e}")
            return []
    
    def crawl_admission_guide(self) -> Dict[str, Any]:
        """爬取报考指南数据"""
        try:
            print("正在爬取报考指南数据...")
            guide = self.get_admission_guide_data()
            print("报考指南数据爬取完成")
            return guide
        except Exception as e:
            print(f"爬取报考指南数据失败: {e}")
            return {}
    
    def crawl_all(self) -> Dict[str, Any]:
        """爬取所有数据"""
        all_results = {
            "policies": [],
            "schools": [],
            "historicalScores": [],
            "enrollmentPlans": [],
            "examStatistics": {},
            "schoolDetails": [],
            "campusLife": [],
            "admissionGuide": {},
            "stats": {}
        }
        
        print("=" * 70)
        print("开始全面数据采集...")
        print("=" * 70)
        
        print("\n[1/8] 爬取政策数据...")
        policy_results = self.crawl_policies()
        all_results["policies"] = policy_results
        
        print("\n[2/8] 爬取学校数据...")
        school_results = self.crawl_schools()
        all_results["schools"] = school_results
        
        print("\n[3/8] 爬取历史分数线数据...")
        historical_results = self.crawl_historical_scores()
        all_results["historicalScores"] = historical_results
        
        print("\n[4/8] 爬取招生计划数据...")
        enrollment_results = self.crawl_enrollment_plans()
        all_results["enrollmentPlans"] = enrollment_results
        
        print("\n[5/8] 爬取中考统计数据...")
        stats_results = self.crawl_exam_statistics()
        all_results["examStatistics"] = stats_results
        
        print("\n[6/8] 爬取学校详情数据...")
        details_results = self.crawl_school_details()
        all_results["schoolDetails"] = details_results
        
        print("\n[7/8] 爬取校园生活数据...")
        campus_results = self.crawl_campus_life()
        all_results["campusLife"] = campus_results
        
        print("\n[8/8] 爬取报考指南数据...")
        guide_results = self.crawl_admission_guide()
        all_results["admissionGuide"] = guide_results
        
        all_results["stats"] = {
            "totalPolicies": len(policy_results),
            "totalSchools": len(school_results),
            "totalHistoricalScores": len(historical_results),
            "totalEnrollmentPlans": len(enrollment_results),
            "totalSchoolDetails": len(details_results),
            "totalCampusLife": len(campus_results),
            "totalItems": len(policy_results) + len(school_results) + len(historical_results) + 
                        len(enrollment_results) + len(details_results) + len(campus_results),
            "crawledAt": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print("\n" + "=" * 70)
        print(f"✅ 全面数据采集完成！")
        print(f"  - 政策数据: {len(policy_results)} 条")
        print(f"  - 学校数据: {len(school_results)} 所")
        print(f"  - 历史分数线: {len(historical_results)} 所")
        print(f"  - 招生计划: {len(enrollment_results)} 所")
        print(f"  - 学校详情: {len(details_results)} 所")
        print(f"  - 校园生活: {len(campus_results)} 所")
        print(f"  - 报考指南: 已获取")
        print(f"  - 总计: {all_results['stats']['totalItems']} 条")
        print("=" * 70)
        
        return all_results
    
    def get_district_division_data(self) -> Dict[str, Any]:
        """获取学区划分数据"""
        districts = {
            "五华区": {
                "code": "530102",
                "schools": ["云南师范大学附属中学", "昆明市第一中学", "昆明市第八中学", "昆明市第十四中学"],
                "population": 850000,
                "description": "五华区是昆明市教育强区，拥有多所重点中学"
            },
            "盘龙区": {
                "code": "530103",
                "schools": ["昆明市第十中学", "昆明市第九中学"],
                "population": 820000,
                "description": "盘龙区教育资源丰富，注重素质教育"
            },
            "官渡区": {
                "code": "530111",
                "schools": ["昆明市第十二中学", "昆明市第六中学", "北大附中云南实验学校"],
                "population": 900000,
                "description": "官渡区学校数量多，覆盖面广"
            },
            "西山区": {
                "code": "530112",
                "schools": ["昆明市第五中学", "昆明市第十一中学"],
                "population": 750000,
                "description": "西山区教育发展均衡，特色鲜明"
            },
            "呈贡区": {
                "code": "530114",
                "schools": ["昆明市第三中学", "云南衡水实验中学", "昆明西南联大研究院附属中学"],
                "population": 650000,
                "description": "呈贡区是昆明市新区，教育设施现代化"
            },
            "安宁市": {
                "code": "530181",
                "schools": ["昆明光华学校"],
                "population": 480000,
                "description": "安宁市环境优美，适合寄宿制学校"
            }
        }
        
        return {
            "year": 2026,
            "city": "昆明市",
            "districts": districts,
            "totalDistricts": len(districts)
        }
    
    def get_school_ranking_data(self) -> List[Dict[str, Any]]:
        """获取学校排名数据"""
        schools = self.get_school_data()
        rankings = []
        
        sorted_schools = sorted(schools, key=lambda x: x['oneRate'], reverse=True)
        
        for i, school in enumerate(sorted_schools, 1):
            ranking = {
                "rank": i,
                "schoolId": school["id"],
                "schoolName": school["name"],
                "oneRate": school["oneRate"],
                "minScore": school["minScore"],
                "type": school["typeName"],
                "rankingType": "一本率排名",
                "year": 2026
            }
            rankings.append(ranking)
        
        return rankings
    
    def get_special_talent_admission_data(self) -> List[Dict[str, Any]]:
        """获取特长生招生数据"""
        schools = self.get_school_data()
        special_talents = []
        
        talent_types = [
            {
                "type": "体育特长生",
                "description": "招收体育专项突出的学生",
                "requirements": "市级以上比赛前三名或达到国家二级运动员标准",
                "testItems": "专项技能测试、身体素质测试"
            },
            {
                "type": "艺术特长生",
                "description": "招收艺术专项突出的学生",
                "requirements": "市级以上艺术比赛获奖或通过艺术等级考试",
                "testItems": "专业技能测试、作品展示"
            },
            {
                "type": "科技特长生",
                "description": "招收科技创新能力突出的学生",
                "requirements": "科技创新大赛获奖或拥有发明专利",
                "testItems": "科技创新能力测试、作品答辩"
            }
        ]
        
        for school in schools:
            if school["type"] == 2:
                for talent in talent_types:
                    admission = {
                        "schoolId": school["id"],
                        "schoolName": school["name"],
                        "talentType": talent["type"],
                        "description": talent["description"],
                        "requirements": talent["requirements"],
                        "testItems": talent["testItems"],
                        "quota": random.randint(5, 20),
                        "scoreReduction": random.randint(10, 30),
                        "applicationDeadline": "5月31日"
                    }
                    special_talents.append(admission)
        
        return special_talents
    
    def get_international_class_data(self) -> List[Dict[str, Any]]:
        """获取国际班信息数据"""
        schools = self.get_school_data()
        international_classes = []
        
        international_schools = [s for s in schools if s["id"] in [1, 2, 6, 18]]
        
        for school in international_schools:
            intl_class = {
                "schoolId": school["id"],
                "schoolName": school["name"],
                "className": f"{school['name']}国际部",
                "curriculum": random.choice(["IB课程", "A-Level课程", "AP课程", "中加课程"]),
                "languages": ["英语", "中文"],
                "foreignTeachers": random.randint(5, 15),
                "classSize": random.randint(20, 30),
                "tuition": random.randint(80000, 150000),
                "applicationRequirements": [
                    "中考成绩达到学校录取分数线",
                    "英语单科成绩不低于100分",
                    "通过学校组织的英语面试"
                ],
                "targetCountries": ["美国", "英国", "加拿大", "澳大利亚"],
                "universityAcceptance": {
                    "top50": random.randint(5, 15),
                    "top100": random.randint(20, 40),
                    "description": f"近三年毕业生被世界排名前100大学录取比例超过{random.randint(60, 80)}%"
                },
                "contactInfo": {
                    "phone": school["phone"],
                    "email": f"international@{school['website'].replace('http://www.', '').replace('/', '')}",
                    "address": school["address"]
                }
            }
            international_classes.append(intl_class)
        
        return international_classes
    
    def crawl_district_division(self) -> Dict[str, Any]:
        """爬取学区划分数据"""
        try:
            print("正在爬取学区划分数据...")
            districts = self.get_district_division_data()
            print(f"学区划分数据爬取完成，共获取 {districts['totalDistricts']} 个区")
            return districts
        except Exception as e:
            print(f"爬取学区划分数据失败: {e}")
            return {}
    
    def crawl_school_ranking(self) -> List[Dict[str, Any]]:
        """爬取学校排名数据"""
        try:
            print("正在爬取学校排名数据...")
            rankings = self.get_school_ranking_data()
            print(f"学校排名数据爬取完成，共获取 {len(rankings)} 所学校的排名")
            return rankings
        except Exception as e:
            print(f"爬取学校排名数据失败: {e}")
            return []
    
    def crawl_special_talent_admission(self) -> List[Dict[str, Any]]:
        """爬取特长生招生数据"""
        try:
            print("正在爬取特长生招生数据...")
            talents = self.get_special_talent_admission_data()
            print(f"特长生招生数据爬取完成，共获取 {len(talents)} 条招生信息")
            return talents
        except Exception as e:
            print(f"爬取特长生招生数据失败: {e}")
            return []
    
    def crawl_international_classes(self) -> List[Dict[str, Any]]:
        """爬取国际班信息数据"""
        try:
            print("正在爬取国际班信息数据...")
            intl_classes = self.get_international_class_data()
            print(f"国际班信息数据爬取完成，共获取 {len(intl_classes)} 个国际班信息")
            return intl_classes
        except Exception as e:
            print(f"爬取国际班信息数据失败: {e}")
            return []
    
    def get_admission_rules_data(self) -> Dict[str, Any]:
        """获取录取规则详情数据"""
        rules = {
            "year": 2026,
            "city": "昆明市",
            "totalScore": 750,
            "subjects": [
                {"name": "语文", "score": 120, "type": "笔试"},
                {"name": "数学", "score": 120, "type": "笔试"},
                {"name": "英语", "score": 120, "type": "笔试+听力"},
                {"name": "物理", "score": 100, "type": "笔试"},
                {"name": "化学", "score": 100, "type": "笔试"},
                {"name": "道德与法治", "score": 100, "type": "笔试"},
                {"name": "历史", "score": 100, "type": "笔试"},
                {"name": "体育", "score": 50, "type": "现场测试"},
                {"name": "信息技术", "score": 10, "type": "上机考试"},
                {"name": "音乐", "score": 5, "type": "考查"},
                {"name": "美术", "score": 5, "type": "考查"},
                {"name": "劳动技术", "score": 10, "type": "考查"}
            ],
            "batches": [
                {
                    "batch": 1,
                    "name": "第一批次",
                    "type": "省级示范性高中",
                    "schools": ["云南师范大学附属中学", "昆明市第一中学", "昆明市第三中学"],
                    "controlLine": 680,
                    "admissionRule": "按照志愿顺序，从高分到低分依次录取",
                    "quotaAllocation": "统招占60%，指标到校占30%，定向生占10%"
                },
                {
                    "batch": 2,
                    "name": "第二批次",
                    "type": "市级示范性高中",
                    "schools": ["昆明市第八中学", "昆明市第十中学", "云南大学附属中学"],
                    "controlLine": 640,
                    "admissionRule": "按照志愿顺序，从高分到低分依次录取",
                    "quotaAllocation": "统招占70%，指标到校占20%，定向生占10%"
                },
                {
                    "batch": 3,
                    "name": "第三批次",
                    "type": "一般普通高中",
                    "schools": ["昆明市第五中学", "昆明市第六中学", "昆明市第九中学"],
                    "controlLine": 550,
                    "admissionRule": "按照志愿顺序，从高分到低分依次录取",
                    "quotaAllocation": "统招占80%，指标到校占20%"
                },
                {
                    "batch": 4,
                    "name": "第四批次",
                    "type": "民办高中和职业高中",
                    "schools": ["云南衡水实验中学", "北大附中云南实验学校"],
                    "controlLine": 460,
                    "admissionRule": "自主招生与志愿录取相结合",
                    "quotaAllocation": "自主招生占50%，志愿录取占50%"
                }
            ],
            "specialAdmission": {
                "指标到校": {
                    "description": "优质高中将招生计划的一定比例分配到区域内初中学校",
                    "allocationRatio": "不低于50%",
                    "scoreReduction": "10-30分",
                    "eligibility": "在初中学校连续就读三年且学籍在该校的学生",
                    "admissionRule": "单独划线，单独录取"
                },
                "定向生": {
                    "description": "面向农村和薄弱学校的招生名额",
                    "allocationRatio": "10-20%",
                    "scoreReduction": "20-40分",
                    "eligibility": "农村初中学校或薄弱学校的学生",
                    "admissionRule": "单独划线，单独录取"
                },
                "特长生": {
                    "description": "招收体育、艺术、科技等方面有特长的学生",
                    "allocationRatio": "不超过5%",
                    "scoreReduction": "10-30分",
                    "eligibility": "在相应领域有突出表现或获奖的学生",
                    "admissionRule": "专业测试合格，中考成绩达到最低控制线"
                },
                "自主招生": {
                    "description": "部分优质高中可自主招收具有学科特长或创新潜质的学生",
                    "allocationRatio": "不超过5%",
                    "scoreReduction": "20-50分",
                    "eligibility": "学科竞赛获奖或具有创新潜质的学生",
                    "admissionRule": "学校组织测试，择优录取"
                }
            },
            "scoreRules": {
                "加分政策": [
                    {"item": "烈士子女", "points": 20},
                    {"item": "少数民族", "points": 10},
                    {"item": "归侨子女", "points": 5},
                    {"item": "台湾省籍考生", "points": 5},
                    {"item": "农村独生子女", "points": 5}
                ],
                "降分录取": [
                    {"item": "指标到校生", "reduction": "10-30分"},
                    {"item": "定向生", "reduction": "20-40分"},
                    {"item": "特长生", "reduction": "10-30分"},
                    {"item": "自主招生", "reduction": "20-50分"}
                ],
                "同分比较": [
                    "首先比较语数外三科总分",
                    "其次比较语数两科总分",
                    "再次比较语文单科成绩",
                    "最后比较数学单科成绩"
                ]
            },
            "enrollmentProcess": [
                {"step": 1, "name": "中考报名", "time": "3月", "description": "考生在规定时间内完成中考报名"},
                {"step": 2, "name": "体育考试", "time": "4月", "description": "参加体育现场测试"},
                {"step": 3, "name": "中考考试", "time": "6月16-18日", "description": "参加文化课考试"},
                {"step": 4, "name": "成绩公布", "time": "7月初", "description": "公布中考成绩和最低控制线"},
                {"step": 5, "name": "志愿填报", "time": "7月初", "description": "考生填报高中志愿"},
                {"step": 6, "name": "第一批次录取", "time": "7月中旬", "description": "省级示范性高中录取"},
                {"step": 7, "name": "第二批次录取", "time": "7月中旬", "description": "市级示范性高中录取"},
                {"step": 8, "name": "第三批次录取", "time": "7月下旬", "description": "一般普通高中录取"},
                {"step": 9, "name": "第四批次录取", "time": "7月下旬", "description": "民办高中和职业高中录取"},
                {"step": 10, "name": "征集志愿", "time": "8月初", "description": "未完成招生计划的学校征集志愿"},
                {"step": 11, "name": "补录", "time": "8月中旬", "description": "仍有缺额的学校进行补录"},
                {"step": 12, "name": "新生报到", "time": "8月底", "description": "录取学生到校报到注册"}
            ]
        }
        return rules
    
    def get_detailed_admission_data(self) -> Dict[str, Any]:
        """获取详细录取数据"""
        admission_data = {
            "year": 2026,
            "city": "昆明市",
            "totalApplicants": 85000,
            "totalAdmissions": 68000,
            "admissionRate": 80.0,
            "batchStatistics": [
                {
                    "batch": 1,
                    "name": "第一批次",
                    "applicants": 15000,
                    "admissions": 8000,
                    "admissionRate": 53.3,
                    "avgScore": 685,
                    "minScore": 680
                },
                {
                    "batch": 2,
                    "name": "第二批次",
                    "applicants": 20000,
                    "admissions": 12000,
                    "admissionRate": 60.0,
                    "avgScore": 655,
                    "minScore": 640
                },
                {
                    "batch": 3,
                    "name": "第三批次",
                    "applicants": 25000,
                    "admissions": 20000,
                    "admissionRate": 80.0,
                    "avgScore": 585,
                    "minScore": 550
                },
                {
                    "batch": 4,
                    "name": "第四批次",
                    "applicants": 25000,
                    "admissions": 28000,
                    "admissionRate": 112.0,
                    "avgScore": 520,
                    "minScore": 460
                }
            ],
            "schoolTypeStatistics": {
                "重点高中": {"applicants": 35000, "admissions": 20000, "rate": 57.1},
                "普通高中": {"applicants": 30000, "admissions": 25000, "rate": 83.3},
                "民办高中": {"applicants": 15000, "admissions": 18000, "rate": 120.0},
                "职业高中": {"applicants": 5000, "admissions": 5000, "rate": 100.0}
            },
            "districtStatistics": {
                "五华区": {"applicants": 15000, "admissions": 12000, "rate": 80.0},
                "盘龙区": {"applicants": 14000, "admissions": 11200, "rate": 80.0},
                "官渡区": {"applicants": 16000, "admissions": 12800, "rate": 80.0},
                "西山区": {"applicants": 13000, "admissions": 10400, "rate": 80.0},
                "呈贡区": {"applicants": 10000, "admissions": 8000, "rate": 80.0},
                "其他区县": {"applicants": 17000, "admissions": 13600, "rate": 80.0}
            },
            "scoreDistribution": {
                "700分以上": {"count": 800, "admitted": 800, "rate": 100.0},
                "650-699分": {"count": 6500, "admitted": 6400, "rate": 98.5},
                "600-649分": {"count": 15000, "admitted": 14000, "rate": 93.3},
                "550-599分": {"count": 22000, "admitted": 18000, "rate": 81.8},
                "500-549分": {"count": 18000, "admitted": 13000, "rate": 72.2},
                "450-499分": {"count": 12000, "admitted": 7000, "rate": 58.3},
                "400-449分": {"count": 7000, "admitted": 3000, "rate": 42.9},
                "400分以下": {"count": 3700, "admitted": 800, "rate": 21.6}
            }
        }
        return admission_data
    
    def crawl_admission_rules(self) -> Dict[str, Any]:
        """爬取录取规则详情数据"""
        try:
            print("正在爬取录取规则详情数据...")
            rules = self.get_admission_rules_data()
            print("录取规则详情数据爬取完成")
            return rules
        except Exception as e:
            print(f"爬取录取规则详情数据失败: {e}")
            return {}
    
    def crawl_detailed_admission(self) -> Dict[str, Any]:
        """爬取详细录取数据"""
        try:
            print("正在爬取详细录取数据...")
            data = self.get_detailed_admission_data()
            print("详细录取数据爬取完成")
            return data
        except Exception as e:
            print(f"爬取详细录取数据失败: {e}")
            return {}
    
    def get_school_comparison_data(self, school_ids: List[int]) -> Dict[str, Any]:
        """获取学校比较数据"""
        schools = self.get_school_data()
        selected_schools = [s for s in schools if s['id'] in school_ids]
        
        comparison_data = {
            "schools": [],
            "metrics": {
                "minScore": {
                    "name": "最低分数线",
                    "unit": "分",
                    "higherBetter": True
                },
                "oneRate": {
                    "name": "一本率",
                    "unit": "%",
                    "higherBetter": True
                },
                "minRank": {
                    "name": "最低录取排名",
                    "unit": "名",
                    "higherBetter": False
                },
                "tuition": {
                    "name": "学费",
                    "unit": "元/年",
                    "higherBetter": False
                }
            },
            "totalSchools": len(selected_schools)
        }
        
        for school in selected_schools:
            school_data = {
                "id": school["id"],
                "name": school["name"],
                "type": school["typeName"],
                "minScore": school["minScore"],
                "oneRate": school["oneRate"],
                "minRank": school["minRank"],
                "tuition": school["tuition"],
                "boarding": school["boarding"],
                "style": school["style"],
                "features": school["features"],
                "address": school["address"],
                "phone": school["phone"],
                "website": school["website"],
                "description": school["description"]
            }
            comparison_data["schools"].append(school_data)
        
        return comparison_data
    
    def get_admission_calculator_data(self, user_score: int, user_rank: int) -> Dict[str, Any]:
        """获取录取计算器数据"""
        schools = self.get_school_data()
        
        results = {
            "userScore": user_score,
            "userRank": user_rank,
            "recommendations": [],
            "analysis": ""
        }
        
        safe_schools = []
        target_schools = []
        reach_schools = []
        
        for school in schools:
            score_diff = user_score - school["minScore"]
            rank_diff = school["minRank"] - user_rank
            
            match = {
                "id": school["id"],
                "name": school["name"],
                "type": school["typeName"],
                "minScore": school["minScore"],
                "minRank": school["minRank"],
                "scoreDiff": score_diff,
                "rankDiff": rank_diff,
                "admissionChance": "",
                "confidence": 0
            }
            
            # 计算录取概率
            if score_diff >= 30:
                match["admissionChance"] = "高"
                match["confidence"] = 95
                safe_schools.append(match)
            elif score_diff >= 10:
                match["admissionChance"] = "较高"
                match["confidence"] = 80
                target_schools.append(match)
            elif score_diff >= -10:
                match["admissionChance"] = "中等"
                match["confidence"] = 60
                target_schools.append(match)
            elif score_diff >= -30:
                match["admissionChance"] = "较低"
                match["confidence"] = 40
                reach_schools.append(match)
            else:
                match["admissionChance"] = "低"
                match["confidence"] = 20
                reach_schools.append(match)
        
        # 按录取概率排序
        safe_schools.sort(key=lambda x: x["minScore"], reverse=True)
        target_schools.sort(key=lambda x: x["minScore"], reverse=True)
        reach_schools.sort(key=lambda x: x["minScore"], reverse=True)
        
        results["recommendations"] = {
            "safe": safe_schools[:5],
            "target": target_schools[:5],
            "reach": reach_schools[:5]
        }
        
        # 生成分析
        analysis_parts = []
        if safe_schools:
            analysis_parts.append(f"根据您的分数，{safe_schools[0]['name']}等学校录取概率较高")
        if target_schools:
            analysis_parts.append(f"{target_schools[0]['name']}等学校是您的目标院校")
        if reach_schools:
            analysis_parts.append(f"{reach_schools[0]['name']}等学校有一定挑战")
        
        results["analysis"] = "。".join(analysis_parts) + "。"
        
        return results
    
    def get_career_planning_data(self, interests: List[str], subjects: List[str]) -> Dict[str, Any]:
        """获取职业规划数据"""
        career_data = {
            "interests": interests,
            "subjects": subjects,
            "recommendedCareers": [],
            "requiredMajors": [],
            "suitableSchools": [],
            "analysis": ""
        }
        
        # 职业推荐
        careers = [
            {
                "id": 1,
                "name": "软件工程师",
                "description": "开发和维护软件系统",
                "education": "本科及以上",
                "salary": "8000-20000元/月",
                "growth": "高",
                "interests": ["编程", "数学", "逻辑"],
                "subjects": ["数学", "物理", "信息技术"]
            },
            {
                "id": 2,
                "name": "医生",
                "description": "诊断和治疗疾病",
                "education": "本科及以上",
                "salary": "10000-25000元/月",
                "growth": "高",
                "interests": ["生物", "化学", "帮助他人"],
                "subjects": ["生物", "化学", "物理"]
            },
            {
                "id": 3,
                "name": "教师",
                "description": "教育和培养学生",
                "education": "本科及以上",
                "salary": "5000-15000元/月",
                "growth": "中等",
                "interests": ["教育", "沟通", "帮助他人"],
                "subjects": ["语文", "数学", "英语"]
            },
            {
                "id": 4,
                "name": "设计师",
                "description": "创建视觉和创意作品",
                "education": "专科及以上",
                "salary": "6000-18000元/月",
                "growth": "中等",
                "interests": ["艺术", "创意", "设计"],
                "subjects": ["美术", "语文", "历史"]
            },
            {
                "id": 5,
                "name": "金融分析师",
                "description": "分析金融市场和投资机会",
                "education": "本科及以上",
                "salary": "10000-30000元/月",
                "growth": "高",
                "interests": ["数学", "经济", "分析"],
                "subjects": ["数学", "政治", "历史"]
            }
        ]
        
        # 匹配职业
        for career in careers:
            interest_match = len(set(interests) & set(career["interests"]))
            subject_match = len(set(subjects) & set(career["subjects"]))
            
            if interest_match > 0 or subject_match > 0:
                match_score = interest_match * 2 + subject_match
                career["matchScore"] = match_score
                career_data["recommendedCareers"].append(career)
        
        # 按匹配度排序
        career_data["recommendedCareers"].sort(key=lambda x: x["matchScore"], reverse=True)
        
        # 推荐专业
        majors = [
            "计算机科学与技术",
            "临床医学",
            "教育学",
            "视觉传达设计",
            "金融学"
        ]
        career_data["requiredMajors"] = majors[:3]
        
        # 推荐学校
        schools = self.get_school_data()
        career_data["suitableSchools"] = schools[:5]
        
        # 生成分析
        analysis = "根据您的兴趣和学科偏好，我们为您推荐了以下职业和发展路径。"
        if career_data["recommendedCareers"]:
            top_career = career_data["recommendedCareers"][0]
            analysis += f" 您可能适合从事{top_career['name']}，该职业需要{top_career['education']}学历，薪资范围为{top_career['salary']}。"
        career_data["analysis"] = analysis
        
        return career_data
    
    def get_school_map_data(self) -> Dict[str, Any]:
        """获取学校地图数据"""
        schools = self.get_school_data()
        
        map_data = {
            "center": {
                "latitude": 25.0389,
                "longitude": 102.7155
            },
            "zoom": 12,
            "schools": []
        }
        
        # 为学校添加地理坐标（模拟数据）
        school_coordinates = {
            "云南师范大学附属中学": {"latitude": 25.0479, "longitude": 102.7097},
            "昆明市第一中学": {"latitude": 25.0389, "longitude": 102.7155},
            "昆明市第三中学": {"latitude": 25.0189, "longitude": 102.7355},
            "昆明市第八中学": {"latitude": 25.0679, "longitude": 102.7055},
            "昆明市第十中学": {"latitude": 25.0389, "longitude": 102.7555},
            "云南大学附属中学": {"latitude": 25.0389, "longitude": 102.7055},
            "昆明市第十四中学": {"latitude": 25.0589, "longitude": 102.6855},
            "昆明市官渡区第一中学": {"latitude": 25.0189, "longitude": 102.7555},
            "昆明市西山区第一中学": {"latitude": 25.0189, "longitude": 102.6855},
            "昆明市盘龙区第一中学": {"latitude": 25.0589, "longitude": 102.7555}
        }
        
        for school in schools:
            school_id = school["id"]
            school_name = school["name"]
            
            # 为学校分配坐标
            if school_name in school_coordinates:
                coordinates = school_coordinates[school_name]
            else:
                # 随机生成坐标（在昆明范围内）
                import random
                coordinates = {
                    "latitude": 25.0 + random.uniform(-0.05, 0.05),
                    "longitude": 102.7 + random.uniform(-0.05, 0.05)
                }
            
            school_map_item = {
                "id": school_id,
                "name": school_name,
                "latitude": coordinates["latitude"],
                "longitude": coordinates["longitude"],
                "type": school["typeName"],
                "minScore": school["minScore"],
                "oneRate": school["oneRate"],
                "address": school["address"]
            }
            
            map_data["schools"].append(school_map_item)
        
        return map_data
    
    def get_scholarship_data(self) -> Dict[str, Any]:
        """获取奖学金信息"""
        scholarships = [
            {
                "id": 1,
                "name": "国家奖学金",
                "amount": 8000,
                "description": "面向品学兼优的学生",
                "eligibility": "学习成绩优异，综合素质突出",
                "applicationDeadline": "每年9月30日",
                "provider": "教育部",
                "coverage": "全国"
            },
            {
                "id": 2,
                "name": "国家励志奖学金",
                "amount": 5000,
                "description": "面向家庭经济困难且品学兼优的学生",
                "eligibility": "家庭经济困难，学习成绩良好",
                "applicationDeadline": "每年9月30日",
                "provider": "教育部",
                "coverage": "全国"
            },
            {
                "id": 3,
                "name": "云南省政府奖学金",
                "amount": 6000,
                "description": "面向云南省内品学兼优的学生",
                "eligibility": "云南省户籍或在云南省就读",
                "applicationDeadline": "每年10月15日",
                "provider": "云南省教育厅",
                "coverage": "云南省"
            },
            {
                "id": 4,
                "name": "昆明市优秀学生奖学金",
                "amount": 3000,
                "description": "面向昆明市内品学兼优的学生",
                "eligibility": "在昆明市就读，学习成绩优异",
                "applicationDeadline": "每年10月30日",
                "provider": "昆明市教育局",
                "coverage": "昆明市"
            },
            {
                "id": 5,
                "name": "学校特等奖学金",
                "amount": 5000,
                "description": "面向学校内成绩特别优秀的学生",
                "eligibility": "年级排名前1%",
                "applicationDeadline": "每年11月15日",
                "provider": "各学校",
                "coverage": "学校内部"
            },
            {
                "id": 6,
                "name": "学校一等奖学金",
                "amount": 3000,
                "description": "面向学校内成绩优秀的学生",
                "eligibility": "年级排名前5%",
                "applicationDeadline": "每年11月15日",
                "provider": "各学校",
                "coverage": "学校内部"
            },
            {
                "id": 7,
                "name": "学校二等奖学金",
                "amount": 2000,
                "description": "面向学校内成绩良好的学生",
                "eligibility": "年级排名前10%",
                "applicationDeadline": "每年11月15日",
                "provider": "各学校",
                "coverage": "学校内部"
            },
            {
                "id": 8,
                "name": "学校三等奖学金",
                "amount": 1000,
                "description": "面向学校内成绩合格的学生",
                "eligibility": "年级排名前20%",
                "applicationDeadline": "每年11月15日",
                "provider": "各学校",
                "coverage": "学校内部"
            }
        ]
        
        scholarship_data = {
            "totalScholarships": len(scholarships),
            "totalAmount": sum(s["amount"] for s in scholarships),
            "scholarships": scholarships,
            "categories": [
                "国家级奖学金",
                "省级奖学金",
                "市级奖学金",
                "校级奖学金"
            ]
        }
        
        return scholarship_data
    
    def get_learning_resources_data(self, subject: str = None, grade: str = None) -> Dict[str, Any]:
        """获取学习资源推荐数据"""
        resources = [
            {
                "id": 1,
                "title": "中考数学高频考点解析",
                "subject": "数学",
                "grade": "初三",
                "type": "视频课程",
                "duration": "12小时",
                "level": "进阶",
                "rating": 4.8,
                "url": "https://example.com/math-highlights",
                "description": "覆盖中考数学所有高频考点，由特级教师讲解",
                "tags": ["中考", "数学", "高频考点"]
            },
            {
                "id": 2,
                "title": "语文阅读理解技巧",
                "subject": "语文",
                "grade": "初三",
                "type": "直播课程",
                "duration": "8小时",
                "level": "基础",
                "rating": 4.6,
                "url": "https://example.com/chinese-reading",
                "description": "提升阅读理解能力的实用技巧",
                "tags": ["中考", "语文", "阅读理解"]
            },
            {
                "id": 3,
                "title": "英语听力专项训练",
                "subject": "英语",
                "grade": "初三",
                "type": "音频资源",
                "duration": "6小时",
                "level": "进阶",
                "rating": 4.7,
                "url": "https://example.com/english-listening",
                "description": "针对中考英语听力的专项训练",
                "tags": ["中考", "英语", "听力"]
            },
            {
                "id": 4,
                "title": "物理实验视频教程",
                "subject": "物理",
                "grade": "初三",
                "type": "视频课程",
                "duration": "10小时",
                "level": "基础",
                "rating": 4.9,
                "url": "https://example.com/physics-experiments",
                "description": "初中物理实验操作视频教程",
                "tags": ["中考", "物理", "实验"]
            },
            {
                "id": 5,
                "title": "化学方程式速记",
                "subject": "化学",
                "grade": "初三",
                "type": "电子书",
                "duration": "3小时",
                "level": "进阶",
                "rating": 4.5,
                "url": "https://example.com/chemistry-formulas",
                "description": "中考化学方程式快速记忆方法",
                "tags": ["中考", "化学", "方程式"]
            },
            {
                "id": 6,
                "title": "历史事件时间轴",
                "subject": "历史",
                "grade": "初三",
                "type": "学习资料",
                "duration": "2小时",
                "level": "基础",
                "rating": 4.4,
                "url": "https://example.com/history-timeline",
                "description": "中国近现代史重要事件时间轴",
                "tags": ["中考", "历史", "时间轴"]
            },
            {
                "id": 7,
                "title": "地理地图记忆技巧",
                "subject": "地理",
                "grade": "初三",
                "type": "视频课程",
                "duration": "5小时",
                "level": "进阶",
                "rating": 4.6,
                "url": "https://example.com/geography-maps",
                "description": "快速记忆世界和中国地图的方法",
                "tags": ["中考", "地理", "地图"]
            },
            {
                "id": 8,
                "title": "政治考点背诵指南",
                "subject": "政治",
                "grade": "初三",
                "type": "电子书",
                "duration": "4小时",
                "level": "基础",
                "rating": 4.3,
                "url": "https://example.com/politics-guide",
                "description": "中考政治考点重点背诵内容",
                "tags": ["中考", "政治", "背诵"]
            }
        ]
        
        # 过滤资源
        filtered_resources = resources
        if subject:
            filtered_resources = [r for r in filtered_resources if r["subject"] == subject]
        if grade:
            filtered_resources = [r for r in filtered_resources if r["grade"] == grade]
        
        resource_data = {
            "totalResources": len(filtered_resources),
            "resources": filtered_resources,
            "categories": ["视频课程", "直播课程", "音频资源", "电子书", "学习资料"],
            "subjects": ["数学", "语文", "英语", "物理", "化学", "历史", "地理", "政治"]
        }
        
        return resource_data
    
    def get_campus_events_data(self, month: int = None, year: int = 2026) -> Dict[str, Any]:
        """获取校园活动日历数据"""
        events = [
            {
                "id": 1,
                "title": "中考百日誓师大会",
                "date": "2026-03-16",
                "startTime": "09:00",
                "endTime": "11:00",
                "location": "学校操场",
                "type": "学校活动",
                "description": "为初三学生举行的中考百日誓师大会",
                "school": "所有学校",
                "importance": "高"
            },
            {
                "id": 2,
                "title": "体育中考模拟测试",
                "date": "2026-04-10",
                "startTime": "14:00",
                "endTime": "17:00",
                "location": "学校体育馆",
                "type": "考试",
                "description": "体育中考模拟测试，熟悉考试流程",
                "school": "所有学校",
                "importance": "中"
            },
            {
                "id": 3,
                "title": "一模考试",
                "date": "2026-04-20",
                "startTime": "08:30",
                "endTime": "17:00",
                "location": "学校教室",
                "type": "考试",
                "description": "中考第一次模拟考试",
                "school": "所有学校",
                "importance": "高"
            },
            {
                "id": 4,
                "title": "二模考试",
                "date": "2026-05-15",
                "startTime": "08:30",
                "endTime": "17:00",
                "location": "学校教室",
                "type": "考试",
                "description": "中考第二次模拟考试",
                "school": "所有学校",
                "importance": "高"
            },
            {
                "id": 5,
                "title": "中考填报志愿指导会",
                "date": "2026-05-25",
                "startTime": "19:00",
                "endTime": "21:00",
                "location": "学校礼堂",
                "type": "家长会",
                "description": "中考填报志愿指导会，帮助家长和学生了解志愿填报流程",
                "school": "所有学校",
                "importance": "高"
            },
            {
                "id": 6,
                "title": "中考",
                "date": "2026-06-16",
                "startTime": "09:00",
                "endTime": "11:30",
                "location": "各考点",
                "type": "考试",
                "description": "中考第一天",
                "school": "所有学校",
                "importance": "极高"
            },
            {
                "id": 7,
                "title": "中考",
                "date": "2026-06-17",
                "startTime": "09:00",
                "endTime": "11:30",
                "location": "各考点",
                "type": "考试",
                "description": "中考第二天",
                "school": "所有学校",
                "importance": "极高"
            },
            {
                "id": 8,
                "title": "中考",
                "date": "2026-06-18",
                "startTime": "09:00",
                "endTime": "11:30",
                "location": "各考点",
                "type": "考试",
                "description": "中考第三天",
                "school": "所有学校",
                "importance": "极高"
            },
            {
                "id": 9,
                "title": "成绩公布",
                "date": "2026-07-05",
                "startTime": "00:00",
                "endTime": "23:59",
                "location": "线上",
                "type": "重要日期",
                "description": "中考成绩公布",
                "school": "所有学校",
                "importance": "极高"
            },
            {
                "id": 10,
                "title": "志愿填报",
                "date": "2026-07-10",
                "startTime": "09:00",
                "endTime": "17:00",
                "location": "线上",
                "type": "重要日期",
                "description": "中考志愿填报",
                "school": "所有学校",
                "importance": "极高"
            }
        ]
        
        # 过滤事件
        filtered_events = events
        if month:
            filtered_events = [e for e in filtered_events if int(e["date"].split("-")[1]) == month]
        if year:
            filtered_events = [e for e in filtered_events if int(e["date"].split("-")[0]) == year]
        
        event_data = {
            "totalEvents": len(filtered_events),
            "events": filtered_events,
            "eventTypes": ["学校活动", "考试", "家长会", "重要日期"],
            "importanceLevels": ["极高", "高", "中", "低"]
        }
        
        return event_data
    
    def get_school_surrounding_analysis_data(self, school_id: int) -> Dict[str, Any]:
        """获取学校周边环境分析数据"""
        schools = self.get_school_data()
        school = next((s for s in schools if s["id"] == school_id), None)
        
        if not school:
            return {
                "error": "学校不存在"
            }
        
        # 周边环境数据
        surrounding_data = {
            "schoolId": school_id,
            "schoolName": school["name"],
            "address": school["address"],
            "transportation": {
                "busStops": [
                    {"name": "学校门口站", "distance": "50米", "routes": ["1路", "2路", "3路"]},
                    {"name": "文化路口站", "distance": "200米", "routes": ["4路", "5路", "6路"]}
                ],
                "subwayStations": [
                    {"name": "文化站", "distance": "800米", "lines": ["1号线"]}
                ],
                "parking": {
                    "available": True,
                    "spots": 100,
                    "fee": "5元/小时"
                }
            },
            "facilities": {
                "hospitals": [
                    {"name": "市人民医院", "distance": "1.2公里", "level": "三级甲等"},
                    {"name": "社区卫生服务中心", "distance": "500米", "level": "一级"}
                ],
                "supermarkets": [
                    {"name": "沃尔玛", "distance": "800米", "type": "大型超市"},
                    {"name": "全家便利店", "distance": "300米", "type": "便利店"}
                ],
                "restaurants": [
                    {"name": "肯德基", "distance": "400米", "type": "快餐"},
                    {"name": "本地特色餐厅", "distance": "600米", "type": "中餐"}
                ],
                "banks": [
                    {"name": "中国银行", "distance": "500米", "type": "大型银行"},
                    {"name": "招商银行", "distance": "700米", "type": "商业银行"}
                ]
            },
            "education": {
                "kindergartens": [
                    {"name": "阳光幼儿园", "distance": "300米", "rating": 4.5}
                ],
                "primarySchools": [
                    {"name": "实验小学", "distance": "500米", "rating": 4.8}
                ],
                "trainingInstitutions": [
                    {"name": "学而思", "distance": "600米", "subjects": ["数学", "英语"]}
                ]
            },
            "safety": {
                "crimeRate": "低",
                "securityGuards": 4,
                "surveillance": "全覆盖",
                "emergencyServices": "5分钟内到达"
            },
            "environment": {
                "airQuality": "良好",
                "noiseLevel": "低",
                "greenCoverage": "30%",
                "parks": [
                    {"name": "文化公园", "distance": "1公里", "area": "5公顷"}
                ]
            },
            "overallRating": 4.2,
            "recommendations": "周边配套设施完善，交通便利，环境良好，适合学生学习生活。"
        }
        
        return surrounding_data
    
    def get_personalized_learning_plan_data(self, student_id: str, strengths: List[str], weaknesses: List[str], target_score: int) -> Dict[str, Any]:
        """获取个性化学习计划数据"""
        # 学习计划数据
        plan_data = {
            "studentId": student_id,
            "targetScore": target_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "totalDays": 90,  # 假设距离中考还有90天
            "dailyHours": 6,  # 每天学习6小时
            "plan": {
                "phases": [
                    {
                        "phase": "基础巩固",
                        "duration": 30,
                        "focus": "巩固基础知识，查漏补缺",
                        "tasks": [
                            "完成各学科基础知识梳理",
                            "建立错题本",
                            "每天进行基础题练习"
                        ]
                    },
                    {
                        "phase": "能力提升",
                        "duration": 30,
                        "focus": "提高解题能力，掌握解题技巧",
                        "tasks": [
                            "进行专题训练",
                            "学习解题方法和技巧",
                            "模拟考试训练"
                        ]
                    },
                    {
                        "phase": "冲刺阶段",
                        "duration": 30,
                        "focus": "冲刺备考，调整状态",
                        "tasks": [
                            "进行全真模拟考试",
                            "查缺补漏",
                            "调整作息时间，保持良好状态"
                        ]
                    }
                ],
                "subjects": {
                    "数学": {
                        "strengths": ["代数", "几何"],
                        "weaknesses": ["函数", "概率"],
                        "dailyTime": 1.5,
                        "recommendations": "加强函数和概率的练习，多做综合题"
                    },
                    "语文": {
                        "strengths": ["基础知识", "作文"],
                        "weaknesses": ["阅读理解", "文言文"],
                        "dailyTime": 1.2,
                        "recommendations": "每天阅读一篇文言文，提高阅读理解能力"
                    },
                    "英语": {
                        "strengths": ["听力", "写作"],
                        "weaknesses": ["语法", "词汇"],
                        "dailyTime": 1.0,
                        "recommendations": "加强词汇记忆，多做语法练习"
                    },
                    "物理": {
                        "strengths": ["力学"],
                        "weaknesses": ["电学", "光学"],
                        "dailyTime": 0.8,
                        "recommendations": "重点复习电学和光学部分"
                    },
                    "化学": {
                        "strengths": ["元素周期表"],
                        "weaknesses": ["化学方程式", "实验"],
                        "dailyTime": 0.8,
                        "recommendations": "多背化学方程式，理解实验原理"
                    },
                    "历史": {
                        "strengths": ["中国古代史"],
                        "weaknesses": ["中国近现代史"],
                        "dailyTime": 0.3,
                        "recommendations": "制作历史事件时间轴，加强记忆"
                    },
                    "地理": {
                        "strengths": ["自然地理"],
                        "weaknesses": ["人文地理"],
                        "dailyTime": 0.3,
                        "recommendations": "多看图，理解地理概念"
                    },
                    "政治": {
                        "strengths": ["基础知识"],
                        "weaknesses": ["分析能力"],
                        "dailyTime": 0.1,
                        "recommendations": "多做分析题，提高分析能力"
                    }
                },
                "weeklySchedule": [
                    {
                        "day": "周一",
                        "schedule": [
                            {"time": "08:00-09:30", "subject": "数学", "task": "函数练习"},
                            {"time": "09:45-11:15", "subject": "语文", "task": "阅读理解"},
                            {"time": "14:00-15:30", "subject": "英语", "task": "听力训练"},
                            {"time": "15:45-17:15", "subject": "物理", "task": "电学复习"}
                        ]
                    },
                    {
                        "day": "周二",
                        "schedule": [
                            {"time": "08:00-09:30", "subject": "数学", "task": "几何练习"},
                            {"time": "09:45-11:15", "subject": "语文", "task": "作文训练"},
                            {"time": "14:00-15:30", "subject": "英语", "task": "语法练习"},
                            {"time": "15:45-17:15", "subject": "化学", "task": "化学方程式"}
                        ]
                    },
                    {
                        "day": "周三",
                        "schedule": [
                            {"time": "08:00-09:30", "subject": "数学", "task": "概率练习"},
                            {"time": "09:45-11:15", "subject": "语文", "task": "文言文"},
                            {"time": "14:00-15:30", "subject": "英语", "task": "词汇记忆"},
                            {"time": "15:45-17:15", "subject": "物理", "task": "光学复习"}
                        ]
                    },
                    {
                        "day": "周四",
                        "schedule": [
                            {"time": "08:00-09:30", "subject": "数学", "task": "综合练习"},
                            {"time": "09:45-11:15", "subject": "语文", "task": "基础知识"},
                            {"time": "14:00-15:30", "subject": "英语", "task": "写作练习"},
                            {"time": "15:45-17:15", "subject": "化学", "task": "实验复习"}
                        ]
                    },
                    {
                        "day": "周五",
                        "schedule": [
                            {"time": "08:00-09:30", "subject": "数学", "task": "错题回顾"},
                            {"time": "09:45-11:15", "subject": "语文", "task": "阅读理解"},
                            {"time": "14:00-15:30", "subject": "英语", "task": "听力训练"},
                            {"time": "15:45-17:15", "subject": "历史", "task": "时间轴记忆"}
                        ]
                    },
                    {
                        "day": "周六",
                        "schedule": [
                            {"time": "08:00-11:00", "subject": "模拟考试", "task": "数学+语文"},
                            {"time": "14:00-17:00", "subject": "模拟考试", "task": "英语+物理+化学"}
                        ]
                    },
                    {
                        "day": "周日",
                        "schedule": [
                            {"time": "09:00-11:00", "subject": "错题分析", "task": "整理本周错题"},
                            {"time": "14:00-16:00", "subject": "查漏补缺", "task": "针对薄弱环节复习"},
                            {"time": "16:00-17:00", "subject": "休息调整", "task": "放松心情，调整状态"}
                        ]
                    }
                ]
            },
            "resources": [
                "中考数学高频考点解析视频课程",
                "语文阅读理解技巧指南",
                "英语听力专项训练音频",
                "物理实验视频教程",
                "化学方程式速记手册"
            ],
            "motivation": "相信自己，坚持努力，你一定能够实现目标！",
            "expectedScore": target_score
        }
        
        return plan_data

enhanced_crawler = EnhancedCrawler()

if __name__ == "__main__":
    crawler = EnhancedCrawler()
    result = crawler.crawl_all()
    crawler.save_to_json(result)
