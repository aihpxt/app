#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能推荐引擎
基于用户画像、成绩、偏好等多维度进行智能推荐
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class School:
    """学校信息"""
    id: str
    name: str
    district: str
    prefecture: str
    type: str  # public, private, key
    min_score: int
    max_score: int
    average_score: int
    ranking: int
    features: List[str]
    address: str
    phone: str = None


@dataclass
class Recommendation:
    """推荐结果"""
    school: School
    match_score: float
    reason: str
    priority: int  # 1-5, 1为最推荐


class IntelligentRecommendationEngine:
    """智能推荐引擎"""
    
    def __init__(self):
        self._schools = self._load_school_data()
        self._district_weights = {
            '五华区': 1.0, '盘龙区': 0.95, '官渡区': 0.95, '西山区': 0.9,
            '呈贡区': 0.85, '安宁市': 0.8, '东川区': 0.7
        }
        logger.info("智能推荐引擎初始化完成")
    
    def _load_school_data(self) -> List[School]:
        """加载学校数据（模拟数据）"""
        schools = [
            # 昆明主城区优质高中
            School(
                id='1', name='云南师范大学附属中学', district='五华区', prefecture='昆明市',
                type='key', min_score=580, max_score=620, average_score=600,
                ranking=1, features=['省级重点', '升学率高', '师资雄厚', '理科强'],
                address='昆明市五华区一二一大街298号'
            ),
            School(
                id='2', name='昆明市第一中学', district='五华区', prefecture='昆明市',
                type='key', min_score=570, max_score=615, average_score=592,
                ranking=2, features=['省级重点', '历史悠久', '文科强', '校园文化丰富'],
                address='昆明市五华区西昌路233号'
            ),
            School(
                id='3', name='昆明市第三中学', district='呈贡区', prefecture='昆明市',
                type='key', min_score=565, max_score=610, average_score=587,
                ranking=3, features=['省级重点', '环境优美', '寄宿制', '综合素质教育'],
                address='昆明市呈贡区春融西路666号'
            ),
            School(
                id='4', name='昆明滇池中学', district='西山区', prefecture='昆明市',
                type='key', min_score=555, max_score=600, average_score=577,
                ranking=4, features=['省级重点', '滇池旁', '体育强', '艺术教育'],
                address='昆明市西山区滇池路118号'
            ),
            School(
                id='5', name='昆明市第十中学', district='盘龙区', prefecture='昆明市',
                type='key', min_score=550, max_score=595, average_score=572,
                ranking=5, features=['省级重点', '科技教育', '社团活跃', '交通便利'],
                address='昆明市盘龙区白塔路247号'
            ),
            # 优质民办高中
            School(
                id='6', name='云南衡水实验中学', district='呈贡区', prefecture='昆明市',
                type='private', min_score=540, max_score=590, average_score=565,
                ranking=6, features=['民办', '衡水模式', '管理严格', '提分快'],
                address='昆明市呈贡区景明北路吴家营街道'
            ),
            School(
                id='7', name='昆明海贝中英文学校', district='官渡区', prefecture='昆明市',
                type='private', min_score=530, max_score=580, average_score=555,
                ranking=7, features=['民办', '双语教学', '国际化', '小班教学'],
                address='昆明市官渡区世纪城迎宾路1号'
            ),
            # 其他优质高中
            School(
                id='8', name='昆明市第十四中学', district='五华区', prefecture='昆明市',
                type='public', min_score=525, max_score=575, average_score=550,
                ranking=8, features=['市级重点', '性价比高', '校风好', '升学稳定'],
                address='昆明市五华区黑林铺前街50号'
            ),
            School(
                id='9', name='昆明市实验中学', district='盘龙区', prefecture='昆明市',
                type='public', min_score=520, max_score=570, average_score=545,
                ranking=9, features=['市级重点', '艺术特色', '体育特长', '校园活动多'],
                address='昆明市盘龙区人民东路300号'
            ),
            School(
                id='10', name='官渡区第一中学', district='官渡区', prefecture='昆明市',
                type='public', min_score=515, max_score=565, average_score=540,
                ranking=10, features=['市级重点', '新建校区', '设施先进', '发展潜力大'],
                address='昆明市官渡区云秀路2998号'
            )
        ]
        return schools
    
    def calculate_match_score(self, user_profile: Dict[str, Any], school: School) -> Tuple[float, str]:
        """
        计算用户与学校的匹配度
        
        Args:
            user_profile: 用户画像（包含district, score等）
            school: 学校信息
        
        Returns:
            (匹配分数, 匹配原因)
        """
        score = 0.0
        reasons = []
        
        user_score = int(user_profile.get('score', 0))
        user_district = user_profile.get('district', '')
        user_pref_type = user_profile.get('preferred_type', '')
        
        # 1. 分数匹配 (40%)
        if school.min_score <= user_score <= school.max_score:
            score += 40
            reasons.append(f"分数({user_score}分)符合录取要求")
        elif user_score > school.max_score:
            score += 35
            reasons.append(f"分数优秀，超出录取要求")
        elif user_score >= school.min_score - 15:
            score += 25
            reasons.append(f"分数接近录取线，建议冲刺")
        elif user_score >= school.min_score - 30:
            score += 15
            reasons.append(f"分数有差距，可作为保底")
        
        # 2. 地区匹配 (20%)
        if user_district and school.district == user_district:
            score += 20
            reasons.append(f"同属{user_district}")
        elif user_district:
            weight = self._district_weights.get(user_district, 0.5)
            score += 10 * weight
            reasons.append(f"位于{school.district}")
        
        # 3. 学校类型偏好 (15%)
        if user_pref_type:
            if school.type == user_pref_type:
                score += 15
                reasons.append(f"符合{user_pref_type}学校偏好")
            else:
                score += 5
        else:
            score += 10
        
        # 4. 学校排名 (15%)
        if school.ranking <= 3:
            score += 15
            reasons.append(f"排名靠前（第{school.ranking}名）")
        elif school.ranking <= 6:
            score += 10
            reasons.append(f"排名较好（第{school.ranking}名）")
        else:
            score += 5
        
        # 5. 特色匹配 (10%)
        user_features = user_profile.get('features', [])
        matched_features = [f for f in user_features if f in school.features]
        if matched_features:
            score += min(10, len(matched_features) * 5)
            reasons.append(f"符合偏好: {', '.join(matched_features)}")
        
        return min(score, 100), "; ".join(reasons)
    
    def recommend_schools(self, user_profile: Dict[str, Any], top_n: int = 5) -> List[Recommendation]:
        """
        推荐学校
        
        Args:
            user_profile: 用户画像
            top_n: 返回推荐数量
        
        Returns:
            推荐结果列表
        """
        recommendations = []
        
        for school in self._schools:
            match_score, reason = self.calculate_match_score(user_profile, school)
            if match_score >= 20:  # 最低匹配阈值
                recommendations.append(Recommendation(
                    school=school,
                    match_score=match_score,
                    reason=reason,
                    priority=self._calculate_priority(match_score)
                ))
        
        # 按匹配分数排序
        recommendations.sort(key=lambda r: r.match_score, reverse=True)
        
        return recommendations[:top_n]
    
    def _calculate_priority(self, match_score: float) -> int:
        """计算推荐优先级"""
        if match_score >= 85:
            return 1
        elif match_score >= 70:
            return 2
        elif match_score >= 55:
            return 3
        elif match_score >= 40:
            return 4
        else:
            return 5
    
    def generate_recommendation_report(self, user_profile: Dict[str, Any]) -> str:
        """
        生成推荐报告
        
        Args:
            user_profile: 用户画像
        
        Returns:
            推荐报告文本
        """
        recommendations = self.recommend_schools(user_profile, top_n=5)
        
        if not recommendations:
            return """😔 抱歉，暂时没有找到适合你的学校推荐。
            
请检查一下是否提供了足够的信息，或者尝试调整筛选条件。"""
        
        user_score = user_profile.get('score', '未知')
        user_district = user_profile.get('district', '未知')
        
        report = f"""🎯 中考择校推荐报告
        
📋 用户信息
• 户籍地区：{user_district}
• 预估分数：{user_score}分

🏫 推荐学校（按匹配度排序）
"""
        
        for i, rec in enumerate(recommendations, 1):
            priority_stars = '⭐' * rec.priority
            report += f"""
{i}. {rec.school.name} {priority_stars}
   📍 位置：{rec.school.district}
   📊 录取分数：{rec.school.min_score}-{rec.school.max_score}分
   🎯 匹配度：{int(rec.match_score)}%
   💡 推荐理由：{rec.reason}
"""
        
        report += """
📌 填报建议
1. 冲刺校：匹配度70%以上的学校，可以冲刺一下
2. 稳妥校：匹配度55-70%的学校，录取把握较大
3. 保底校：匹配度40-55%的学校，确保有学可上

💬 需要我为你详细介绍某所学校吗？可以告诉我学校名称！"""
        
        return report
    
    def get_school_details(self, school_name: str) -> Optional[str]:
        """
        获取学校详细信息
        
        Args:
            school_name: 学校名称
        
        Returns:
            学校详细信息
        """
        school = next((s for s in self._schools if school_name in s.name), None)
        
        if not school:
            return None
        
        type_map = {
            'key': '省级重点',
            'public': '公办',
            'private': '民办'
        }
        
        features_str = '\n• '.join(school.features)
        
        return f"""🏫 {school.name}
        
📋 基本信息
• 类型：{type_map.get(school.type, school.type)}
• 地区：{school.prefecture}{school.district}
• 排名：昆明市第{school.ranking}名
• 地址：{school.address}

📊 录取信息
• 录取分数范围：{school.min_score}-{school.max_score}分
• 平均录取分数：{school.average_score}分

✨ 学校特色
• {features_str}

💡 综合评价：
这是一所在{school.district}的优质{type_map.get(school.type, school.type)}高中，
以{school.features[0]}为特色，非常适合追求{school.features[1]}的学生。"""


# 全局实例
recommendation_engine = IntelligentRecommendationEngine()


def get_recommendation_engine() -> IntelligentRecommendationEngine:
    """获取智能推荐引擎实例"""
    return recommendation_engine


# 便捷函数
def recommend_schools(user_profile: Dict[str, Any]) -> List[Recommendation]:
    """便捷函数：推荐学校"""
    return recommendation_engine.recommend_schools(user_profile)


def generate_report(user_profile: Dict[str, Any]) -> str:
    """便捷函数：生成推荐报告"""
    return recommendation_engine.generate_recommendation_report(user_profile)


if __name__ == '__main__':
    # 测试推荐引擎
    print("=" * 70)
    print("智能推荐引擎测试")
    print("=" * 70)
    
    # 测试用例
    user_profile = {
        'district': '五华区',
        'score': 580,
        'preferred_type': 'key',
        'features': ['理科强', '升学率高']
    }
    
    print("\n👤 用户画像:")
    print(f"   地区: {user_profile['district']}")
    print(f"   分数: {user_profile['score']}分")
    print(f"   偏好类型: {user_profile['preferred_type']}")
    print(f"   偏好特色: {user_profile['features']}")
    
    print("\n" + "=" * 70)
    print("推荐报告")
    print("=" * 70)
    
    report = generate_report(user_profile)
    print(report)
    
    print("\n" + "=" * 70)
    print("学校详情")
    print("=" * 70)
    
    details = recommendation_engine.get_school_details("云南师范大学附属中学")
    if details:
        print(details)
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)