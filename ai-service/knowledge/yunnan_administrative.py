#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
云南省行政区划知识库
用于智能判断用户所属州市和招生政策适用性
"""

from typing import Dict, List, Optional, Tuple


class YunnanAdministrativeKnowledge:
    """云南省行政区划知识"""
    
    def __init__(self):
        self.prefecture_city_map = {
            # 昆明市
            '昆明市': ['五华区', '盘龙区', '官渡区', '西山区', '呈贡区', '晋宁区', '安宁市', '富民县', '宜良县', '石林彝族自治县', '嵩明县', '禄劝彝族苗族自治县', '寻甸回族彝族自治县', '东川区'],
            # 曲靖市
            '曲靖市': ['麒麟区', '沾益区', '马龙区', '宣威市', '富源县', '罗平县', '师宗县', '陆良县', '会泽县'],
            # 玉溪市
            '玉溪市': ['红塔区', '江川区', '通海县', '华宁县', '易门县', '峨山彝族自治县', '新平彝族傣族自治县', '元江哈尼族彝族傣族自治县', '澄江市'],
            # 保山市
            '保山市': ['隆阳区', '腾冲市', '施甸县', '龙陵县', '昌宁县'],
            # 昭通市
            '昭通市': ['昭阳区', '水富市', '鲁甸县', '巧家县', '盐津县', '大关县', '永善县', '绥江县', '镇雄县', '彝良县', '威信县'],
            # 丽江市
            '丽江市': ['古城区', '永胜县', '华坪县', '玉龙纳西族自治县', '宁蒗彝族自治县'],
            # 普洱市
            '普洱市': ['思茅区', '宁洱哈尼族彝族自治县', '墨江哈尼族自治县', '景东彝族自治县', '景谷傣族彝族自治县', '镇沅彝族哈尼族拉祜族自治县', '江城哈尼族彝族自治县', '孟连傣族拉祜族佤族自治县', '澜沧拉祜族自治县', '西盟佤族自治县'],
            # 临沧市
            '临沧市': ['临翔区', '凤庆县', '云县', '永德县', '镇康县', '双江拉祜族佤族布朗族傣族自治县', '耿马傣族佤族自治县', '沧源佤族自治县'],
            # 楚雄彝族自治州
            '楚雄彝族自治州': ['楚雄市', '禄丰市', '双柏县', '牟定县', '南华县', '姚安县', '大姚县', '永仁县', '元谋县', '武定县'],
            # 红河哈尼族彝族自治州
            '红河哈尼族彝族自治州': ['个旧市', '开远市', '蒙自市', '弥勒市', '屏边苗族自治县', '建水县', '石屏县', '泸西县', '元阳县', '红河县', '金平苗族瑶族傣族自治县', '绿春县', '河口瑶族自治县'],
            # 文山壮族苗族自治州
            '文山壮族苗族自治州': ['文山市', '砚山县', '西畴县', '麻栗坡县', '马关县', '丘北县', '广南县', '富宁县'],
            # 西双版纳傣族自治州
            '西双版纳傣族自治州': ['景洪市', '勐海县', '勐腊县'],
            # 大理白族自治州
            '大理白族自治州': ['大理市', '漾濞彝族自治县', '祥云县', '宾川县', '弥渡县', '南涧彝族自治县', '巍山彝族回族自治县', '永平县', '云龙县', '洱源县', '剑川县', '鹤庆县'],
            # 德宏傣族景颇族自治州
            '德宏傣族景颇族自治州': ['瑞丽市', '芒市', '梁河县', '盈江县', '陇川县'],
            # 怒江傈僳族自治州
            '怒江傈僳族自治州': ['泸水市', '福贡县', '贡山独龙族怒族自治县', '兰坪白族普米族自治县'],
            # 迪庆藏族自治州
            '迪庆藏族自治州': ['香格里拉市', '德钦县', '维西傈僳族自治县']
        }
        
        # 反向映射：区县 -> 州市
        self.district_to_prefecture = {}
        for prefecture, districts in self.prefecture_city_map.items():
            for district in districts:
                self.district_to_prefecture[district] = prefecture
    
    def get_prefecture_by_district(self, district: str) -> Optional[str]:
        """根据区县获取所属州市"""
        # 处理可能的简写
        district = district.replace('县', '').replace('区', '').replace('市', '')
        
        for full_district, prefecture in self.district_to_prefecture.items():
            if district in full_district or full_district in district:
                return prefecture
        
        return None
    
    def get_all_districts_by_prefecture(self, prefecture: str) -> List[str]:
        """获取州市下的所有区县"""
        return self.prefecture_city_map.get(prefecture, [])
    
    def is_same_prefecture(self, district1: str, district2: str) -> bool:
        """判断两个区县是否属于同一州市"""
        prefecture1 = self.get_prefecture_by_district(district1)
        prefecture2 = self.get_prefecture_by_district(district2)
        
        if prefecture1 and prefecture2:
            return prefecture1 == prefecture2
        return False
    
    def can_apply_to_kunming(self, district: str) -> Tuple[bool, str]:
        """
        判断某区县学生是否可以报考昆明高中
        返回: (是否可以报考, 原因说明)
        """
        prefecture = self.get_prefecture_by_district(district)
        
        if not prefecture:
            return False, f"无法识别{district}所属州市"
        
        if prefecture == '昆明市':
            return True, f"{district}属于昆明市，可以正常报考昆明高中"
        else:
            return False, f"{district}属于{prefecture}，根据云南省招生政策，各州市独立招生，不能跨州市报考昆明高中"
    
    def get_enrollment_policy(self, district: str) -> Dict:
        """获取某区县的招生政策说明"""
        prefecture = self.get_prefecture_by_district(district)
        
        if not prefecture:
            return {
                'error': f'无法识别{district}所属州市',
                'can_apply_kunming': False
            }
        
        can_apply, reason = self.can_apply_to_kunming(district)
        
        policy = {
            'district': district,
            'prefecture': prefecture,
            'can_apply_kunming': can_apply,
            'policy_explanation': reason,
            'applicable_schools': []
        }
        
        if can_apply:
            policy['applicable_schools'] = [
                '昆明市主城区公办高中',
                '昆明市主城区民办高中',
                f'{prefecture}内高中'
            ]
        else:
            policy['applicable_schools'] = [
                f'{prefecture}内高中',
                '少数具有全省招生资格的省级学校（需单独咨询）'
            ]
        
        return policy
    
    def get_recommended_schools(self, district: str) -> List[Dict]:
        """获取推荐学校列表"""
        prefecture = self.get_prefecture_by_district(district)
        
        if not prefecture:
            return []
        
        # 各州市优质高中推荐
        recommended = {
            '昆明市': ['昆明第一中学', '昆明第三中学', '昆明第八中学', '昆明第十中学', '昆明第十四中学', '云南师范大学附属中学'],
            '曲靖市': ['曲靖第一中学', '曲靖第二中学', '宣威第六中学'],
            '玉溪市': ['玉溪第一中学', '玉溪师范学院附属中学', '江川区第一中学'],
            '保山市': ['保山第一中学', '腾冲第一中学'],
            '昭通市': ['昭通第一中学', '昭通实验中学'],
            '丽江市': ['丽江市第一高级中学'],
            '普洱市': ['普洱第一中学'],
            '临沧市': ['临沧市第一中学'],
            '楚雄彝族自治州': ['楚雄第一中学', '楚雄东兴中学'],
            '红河哈尼族彝族自治州': ['红河州第一中学', '蒙自第一中学', '个旧第一中学'],
            '文山壮族苗族自治州': ['文山州第一中学', '文山州民族中学', '广南县第一中学'],
            '西双版纳傣族自治州': ['西双版纳州第一中学'],
            '大理白族自治州': ['大理第一中学', '下关第一中学'],
            '德宏傣族景颇族自治州': ['德宏州民族第一中学'],
            '怒江傈僳族自治州': ['怒江州民族中学'],
            '迪庆藏族自治州': ['香格里拉市第一中学']
        }
        
        return [
            {
                'name': school,
                'prefecture': prefecture,
                'type': '公办'
            }
            for school in recommended.get(prefecture, [])
        ]


# 全局实例
_knowledge_base = None


def get_administrative_knowledge() -> YunnanAdministrativeKnowledge:
    """获取行政区划知识库实例（单例）"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = YunnanAdministrativeKnowledge()
    return _knowledge_base


if __name__ == '__main__':
    # 测试行政区划知识库
    knowledge = YunnanAdministrativeKnowledge()
    
    print("=" * 60)
    print("云南省行政区划知识库测试")
    print("=" * 60)
    
    # 测试区县识别
    test_districts = ['江川区', '丘北县', '五华区', '麒麟区', '大理市']
    
    print("\n📍 区县所属州市判断：")
    for district in test_districts:
        prefecture = knowledge.get_prefecture_by_district(district)
        print(f"  {district} -> {prefecture}")
    
    # 测试报考资格
    print("\n🎓 报考昆明高中资格判断：")
    for district in test_districts:
        can_apply, reason = knowledge.can_apply_to_kunming(district)
        status = "✅ 可以" if can_apply else "❌ 不可以"
        print(f"  {district}: {status}")
        print(f"    {reason}")
    
    # 测试招生政策
    print("\n📋 招生政策详情（江川区）：")
    policy = knowledge.get_enrollment_policy('江川区')
    print(f"  所属州市: {policy['prefecture']}")
    print(f"  能否报考昆明: {'可以' if policy['can_apply_kunming'] else '不可以'}")
    print(f"  政策说明: {policy['policy_explanation']}")
    print(f"  可报考学校: {', '.join(policy['applicable_schools'])}")
    
    # 测试推荐学校
    print("\n🏫 推荐学校（江川区）：")
    schools = knowledge.get_recommended_schools('江川区')
    for school in schools[:3]:
        print(f"  - {school['name']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
