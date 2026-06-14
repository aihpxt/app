#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱服务
提供学校信息查询、招生政策查询和问答推理能力
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class SchoolKnowledgeBase:
    """学校知识库（模拟知识图谱）"""
    
    # 学校信息数据
    SCHOOLS = {
        '师大附中': {
            'name': '云南师范大学附属中学',
            'type': '省级重点',
            'location': '昆明市五华区',
            'founded': 1940,
            'students': 3000,
            'teachers': 200,
            'rate_一本': 95,
            'rate_本科': 99,
            'tuition': 1500,
            'features': ['百年名校', '师资雄厚', '升学率高', '寄宿制'],
            'phone': '0871-65321234',
            'address': '昆明市五华区东风西路198号'
        },
        '昆一中': {
            'name': '昆明市第一中学',
            'type': '省级重点',
            'location': '昆明市五华区',
            'founded': 1905,
            'students': 2800,
            'teachers': 180,
            'rate_一本': 92,
            'rate_本科': 98,
            'tuition': 1500,
            'features': ['历史悠久', '学风严谨', '体育强'],
            'phone': '0871-65154123',
            'address': '昆明市五华区西昌路233号'
        },
        '昆三中': {
            'name': '昆明市第三中学',
            'type': '省级重点',
            'location': '昆明市呈贡区',
            'founded': 1907,
            'students': 2500,
            'teachers': 160,
            'rate_一本': 88,
            'rate_本科': 97,
            'tuition': 1500,
            'features': ['新校区', '设施先进', '科技创新'],
            'phone': '0871-67478899',
            'address': '昆明市呈贡区惠通路678号'
        },
        '昆八中': {
            'name': '昆明市第八中学',
            'type': '省级重点',
            'location': '昆明市五华区',
            'founded': 1952,
            'students': 2600,
            'teachers': 170,
            'rate_一本': 85,
            'rate_本科': 96,
            'tuition': 1500,
            'features': ['管理严格', '竞赛强', '艺术特色'],
            'phone': '0871-65157678',
            'address': '昆明市五华区龙泉路628号'
        },
        '云大附中': {
            'name': '云南大学附属中学',
            'type': '省级重点',
            'location': '昆明市五华区',
            'founded': 1927,
            'students': 3200,
            'teachers': 220,
            'rate_一本': 90,
            'rate_本科': 98,
            'tuition': 8000,
            'features': ['民办名校', '小班教学', '国际化'],
            'phone': '0871-65033855',
            'address': '昆明市五华区一二一大街247号'
        },
        '滇池中学': {
            'name': '昆明市滇池中学',
            'type': '市级重点',
            'location': '昆明市西山区',
            'founded': 1988,
            'students': 2000,
            'teachers': 140,
            'rate_一本': 75,
            'rate_本科': 92,
            'tuition': 1500,
            'features': ['滇池畔', '环境优美', '文科强'],
            'phone': '0871-64612345',
            'address': '昆明市西山区滇池路118号'
        },
        '民族中学': {
            'name': '昆明市民族中学',
            'type': '市级重点',
            'location': '昆明市盘龙区',
            'founded': 1981,
            'students': 1800,
            'teachers': 130,
            'rate_一本': 68,
            'rate_本科': 88,
            'tuition': 1500,
            'features': ['民族特色', '多元文化', '寄宿制'],
            'phone': '0871-65157654',
            'address': '昆明市盘龙区环城东路488号'
        },
        '实验中学': {
            'name': '昆明市实验中学',
            'type': '普通中学',
            'location': '昆明市官渡区',
            'founded': 2003,
            'students': 1500,
            'teachers': 100,
            'rate_一本': 45,
            'rate_本科': 75,
            'tuition': 1000,
            'features': ['年轻学校', '潜力大', '社区学校'],
            'phone': '0871-67178900',
            'address': '昆明市官渡区日新路366号'
        }
    }
    
    # 招生政策数据
    POLICIES = {
        '录取分数线': {
            'description': '云南省中考录取分数线由各州市教育局根据当年考生成绩和招生计划划定',
            'key_points': [
                '省级重点中学录取线通常在650分以上',
                '州市级重点中学录取线通常在600-650分之间',
                '普通中学录取线通常在500-600分之间',
                '民办学校录取线相对灵活',
                '每年分数线会根据考生整体成绩有所浮动'
            ],
            'year_2024': {
                '省级重点': 650,
                '市级重点': 600,
                '普通中学': 500
            }
        },
        '志愿填报': {
            'description': '云南省中考实行平行志愿填报制度',
            'key_points': [
                '考生可填报多个志愿，按分数优先原则投档',
                '第一志愿非常重要，建议填报与自己分数匹配的学校',
                '可填报公办、民办、中外合作等不同类型学校',
                '志愿填报时间通常在中考后一周内',
                '未被录取的考生可参加补录'
            ],
            'volunteer_count': 8
        },
        '加分政策': {
            'description': '云南省中考加分政策旨在促进教育公平',
            'key_points': [
                '少数民族考生可加5-10分',
                '独生子女考生可加5分',
                '体育、艺术特长生可加分',
                '军人子女、烈士子女有特殊照顾',
                '加分政策逐年收紧，注重综合素质评价'
            ],
            'max_points': 20
        },
        '定向生': {
            'description': '定向生政策旨在促进教育均衡发展',
            'key_points': [
                '优质高中将一定比例的招生名额分配到薄弱初中',
                '定向生录取分数线通常低于统招线20-30分',
                '定向生需符合相应的资格条件',
                '定向生政策向农村地区倾斜'
            ],
            'ratio': 0.3
        },
        '跨州市报考': {
            'description': '云南省中考原则上实行属地招生',
            'key_points': [
                '考生通常需在户籍所在地或学籍所在地报考',
                '跨州市报考需符合特定条件',
                '优质民办学校可面向全省招生',
                '省级重点中学有少量全省招生名额'
            ],
            'allowed': True
        }
    }
    
    # 常见问题
    FAQ = {
        '中考总分': {
            'question': '云南省中考总分是多少？',
            'answer': '云南省中考总分700分，包括：语文120分、数学120分、英语120分、物理80分、化学50分、体育50分、道德与法治40分、历史40分、生物学30分、地理30分。',
            'category': '考试科目'
        },
        '考试时间': {
            'question': '中考什么时候考？',
            'answer': '云南省中考通常在每年6月16-18日进行，具体时间以当年教育厅通知为准。',
            'category': '考试安排'
        },
        '志愿数量': {
            'question': '可以填几个志愿？',
            'answer': '昆明市考生可填报8个平行志愿，其他州市略有不同，具体以当地教育局规定为准。',
            'category': '志愿填报'
        },
        '复读政策': {
            'question': '中考可以复读吗？',
            'answer': '云南省允许中考复读，但复读生不能享受定向生政策，且部分学校可能对复读生有限制。',
            'category': '政策规定'
        },
        '特长生': {
            'question': '特长生怎么报考？',
            'answer': '特长生需参加学校组织的专业测试，达到合格线后可获得加分或优先录取资格。',
            'category': '特殊招生'
        }
    }


class KnowledgeGraphService:
    """知识图谱服务"""
    
    def __init__(self):
        self._knowledge_base = SchoolKnowledgeBase()
        logger.info("知识图谱服务初始化完成")
    
    def query_school(self, school_name: str) -> Optional[Dict[str, Any]]:
        """
        查询学校信息
        
        Args:
            school_name: 学校名称
        
        Returns:
            学校信息字典，如果未找到返回None
        """
        # 尝试精确匹配
        if school_name in self._knowledge_base.SCHOOLS:
            return self._knowledge_base.SCHOOLS[school_name]
        
        # 尝试模糊匹配
        for key in self._knowledge_base.SCHOOLS:
            if school_name in key or key in school_name:
                return self._knowledge_base.SCHOOLS[key]
        
        return None
    
    def query_school_by_type(self, school_type: str) -> List[Dict[str, Any]]:
        """
        按类型查询学校
        
        Args:
            school_type: 学校类型（省级重点、市级重点、普通中学、民办等）
        
        Returns:
            学校列表
        """
        results = []
        for school in self._knowledge_base.SCHOOLS.values():
            if school_type in school['type'] or school['type'] in school_type:
                results.append(school)
        return results
    
    def query_school_by_location(self, location: str) -> List[Dict[str, Any]]:
        """
        按地区查询学校
        
        Args:
            location: 地区名称
        
        Returns:
            学校列表
        """
        results = []
        for school in self._knowledge_base.SCHOOLS.values():
            if location in school['location'] or school['location'] in location:
                results.append(school)
        return results
    
    def query_policy(self, policy_name: str) -> Optional[Dict[str, Any]]:
        """
        查询招生政策
        
        Args:
            policy_name: 政策名称
        
        Returns:
            政策信息字典，如果未找到返回None
        """
        # 尝试精确匹配
        if policy_name in self._knowledge_base.POLICIES:
            return self._knowledge_base.POLICIES[policy_name]
        
        # 尝试模糊匹配
        for key in self._knowledge_base.POLICIES:
            if policy_name in key or key in policy_name:
                return self._knowledge_base.POLICIES[key]
        
        return None
    
    def list_policies(self) -> List[str]:
        """获取所有政策名称"""
        return list(self._knowledge_base.POLICIES.keys())
    
    def query_faq(self, question: str) -> Optional[Dict[str, Any]]:
        """
        查询常见问题
        
        Args:
            question: 问题关键词
        
        Returns:
            FAQ信息字典，如果未找到返回None
        """
        question_lower = question.lower()
        
        for key, faq in self._knowledge_base.FAQ.items():
            if any(keyword in question_lower for keyword in ['总分', '分数', '多少分']):
                if '总分' in key.lower():
                    return faq
            if any(keyword in question_lower for keyword in ['时间', '什么时候', '几号']):
                if '时间' in key.lower():
                    return faq
            if any(keyword in question_lower for keyword in ['志愿', '填几个', '几个志愿']):
                if '志愿' in key.lower():
                    return faq
            if any(keyword in question_lower for keyword in ['复读', '重读', '再考']):
                if '复读' in key.lower():
                    return faq
            if any(keyword in question_lower for keyword in ['特长', '艺术', '体育']):
                if '特长' in key.lower():
                    return faq
        
        return None
    
    def infer_admission_probability(self, score: int, school_name: str) -> Tuple[int, str]:
        """
        推理录取概率
        
        Args:
            score: 分数
            school_name: 学校名称
        
        Returns:
            (概率百分比, 说明)
        """
        school = self.query_school(school_name)
        if not school:
            return 0, "未找到该学校信息"
        
        school_type = school['type']
        rate_一本 = school.get('rate_一本', 0)
        
        # 根据学校类型确定基准分数线
        base_score = {
            '省级重点': 650,
            '市级重点': 600,
            '普通中学': 500,
            '民办': 550
        }.get(school_type, 550)
        
        # 计算概率
        if score >= base_score + 30:
            probability = 90
            explanation = f"你的分数{score}分高于{school['name']}的预期录取线，可以冲刺！"
        elif score >= base_score + 10:
            probability = 75
            explanation = f"你的分数{score}分略高于{school['name']}的预期录取线，有较大把握！"
        elif score >= base_score:
            probability = 60
            explanation = f"你的分数{score}分接近{school['name']}的预期录取线，有一定机会！"
        elif score >= base_score - 20:
            probability = 40
            explanation = f"你的分数{score}分略低于{school['name']}的预期录取线，可以尝试！"
        elif score >= base_score - 40:
            probability = 20
            explanation = f"你的分数{score}分低于{school['name']}的预期录取线，机会较小。"
        else:
            probability = 5
            explanation = f"你的分数{score}分与{school['name']}的录取线差距较大，建议考虑其他学校。"
        
        return probability, explanation
    
    def compare_schools(self, school_names: List[str]) -> Dict[str, Any]:
        """
        对比多所学校
        
        Args:
            school_names: 学校名称列表
        
        Returns:
            对比结果
        """
        schools = []
        for name in school_names:
            school = self.query_school(name)
            if school:
                schools.append(school)
        
        if len(schools) < 2:
            return {'error': '至少需要对比2所学校'}
        
        # 提取关键指标进行对比
        comparison = {
            'schools': [],
            'comparison_matrix': []
        }
        
        for school in schools:
            school_data = {
                'name': school['name'],
                'type': school['type'],
                'location': school['location'],
                'rate_一本': school.get('rate_一本', 0),
                'rate_本科': school.get('rate_本科', 0),
                'tuition': school.get('tuition', 0),
                'features': school.get('features', [])
            }
            comparison['schools'].append(school_data)
        
        # 生成对比矩阵
        metrics = ['rate_一本', 'rate_本科', 'tuition']
        for metric in metrics:
            values = [(s['name'], s[metric]) for s in comparison['schools']]
            comparison['comparison_matrix'].append({
                'metric': metric,
                'values': values,
                'best': max(values, key=lambda x: x[1])[0] if metric != 'tuition' else min(values, key=lambda x: x[1])[0]
            })
        
        return comparison
    
    def get_school_statistics(self) -> Dict[str, Any]:
        """获取学校统计信息"""
        schools = list(self._knowledge_base.SCHOOLS.values())
        
        stats = {
            'total_schools': len(schools),
            'avg_students': sum(s['students'] for s in schools) // len(schools),
            'avg_teachers': sum(s['teachers'] for s in schools) // len(schools),
            'avg_rate_一本': sum(s.get('rate_一本', 0) for s in schools) // len(schools),
            'types': {}
        }
        
        for school in schools:
            school_type = school['type']
            stats['types'][school_type] = stats['types'].get(school_type, 0) + 1
        
        return stats


# 全局实例
knowledge_graph_service = KnowledgeGraphService()


def get_knowledge_graph_service() -> KnowledgeGraphService:
    """获取知识图谱服务实例"""
    return knowledge_graph_service


if __name__ == '__main__':
    print("=" * 70)
    print("知识图谱服务测试")
    print("=" * 70)
    
    kg_service = KnowledgeGraphService()
    
    # 测试1: 查询学校信息
    print("\n1. 查询学校信息")
    print("-" * 50)
    school = kg_service.query_school('师大附中')
    print(f"学校名称: {school['name']}")
    print(f"类型: {school['type']}")
    print(f"位置: {school['location']}")
    print(f"一本率: {school['rate_一本']}%")
    print(f"学费: {school['tuition']}元/学期")
    print(f"特色: {', '.join(school['features'])}")
    
    # 测试2: 查询政策
    print("\n2. 查询招生政策")
    print("-" * 50)
    policy = kg_service.query_policy('录取分数线')
    print(f"政策名称: 录取分数线")
    print(f"描述: {policy['description']}")
    print("要点:")
    for point in policy['key_points']:
        print(f"  - {point}")
    
    # 测试3: 推理录取概率
    print("\n3. 录取概率推理")
    print("-" * 50)
    probability, explanation = kg_service.infer_admission_probability(660, '昆一中')
    print(f"分数: 660分")
    print(f"目标学校: 昆一中")
    print(f"录取概率: {probability}%")
    print(f"说明: {explanation}")
    
    # 测试4: 学校对比
    print("\n4. 学校对比")
    print("-" * 50)
    comparison = kg_service.compare_schools(['师大附中', '昆一中'])
    for school in comparison['schools']:
        print(f"\n{school['name']} ({school['type']}):")
        print(f"  一本率: {school['rate_一本']}%")
        print(f"  本科率: {school['rate_本科']}%")
        print(f"  学费: {school['tuition']}元/学期")
    
    # 测试5: 查询FAQ
    print("\n5. 查询常见问题")
    print("-" * 50)
    faq = kg_service.query_faq('中考总分')
    print(f"问题: {faq['question']}")
    print(f"答案: {faq['answer']}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)