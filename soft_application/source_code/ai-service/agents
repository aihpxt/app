#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招生政策智能体
专门处理云南省中考招生政策咨询
具备行政区划智能判断能力
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import sys
from pathlib import Path

# 添加知识库路径
sys.path.append(str(Path(__file__).parent.parent / 'knowledge'))

from yunnan_administrative import get_administrative_knowledge

logger = logging.getLogger(__name__)


class PolicyEnrollmentAgent:
    """
    招生政策智能体
    负责解答招生政策相关问题，具备行政区划智能判断
    """
    
    def __init__(self):
        self.name = "招生政策专家"
        self.description = "专门解答云南省中考招生政策问题"
        self.admin_knowledge = get_administrative_knowledge()
        
        # 常见关键词映射
        self.district_keywords = {
            '江川': '江川区',
            '丘北': '丘北县',
            '五华': '五华区',
            '盘龙': '盘龙区',
            '官渡': '官渡区',
            '西山': '西山区',
            '呈贡': '呈贡区',
            '安宁': '安宁市',
            '宜良': '宜良县',
            '石林': '石林彝族自治县',
            '嵩明': '嵩明县',
            '禄劝': '禄劝彝族苗族自治县',
            '寻甸': '寻甸回族彝族自治县',
            '东川': '东川区',
            '麒麟': '麒麟区',
            '宣威': '宣威市',
            '大理': '大理市',
            '个旧': '个旧市',
            '开远': '开远市',
            '蒙自': '蒙自市',
            '弥勒': '弥勒市',
            '文山': '文山市',
            '砚山': '砚山县',
            '广南': '广南县',
            '富宁': '富宁县',
            '景洪': '景洪市',
            '瑞丽': '瑞丽市',
            '芒市': '芒市',
            '香格里拉': '香格里拉市'
        }
    
    def extract_district(self, user_input: str) -> str:
        """从用户输入中提取区县信息"""
        user_input = user_input.strip()
        
        # 直接匹配关键词
        for keyword, full_name in self.district_keywords.items():
            if keyword in user_input:
                return full_name
        
        # 尝试匹配完整区县名
        for district in self.admin_knowledge.district_to_prefecture.keys():
            if district in user_input:
                return district
        
        return None
    
    def analyze_enrollment_policy(self, district: str) -> Dict[str, Any]:
        """分析招生政策"""
        policy = self.admin_knowledge.get_enrollment_policy(district)
        recommended_schools = self.admin_knowledge.get_recommended_schools(district)
        
        return {
            'policy': policy,
            'recommended_schools': recommended_schools
        }
    
    def generate_response(self, user_input: str, context: Dict = None) -> str:
        """生成政策咨询回复"""
        if context is None:
            context = {}
        
        # 提取区县信息
        district = self.extract_district(user_input)
        
        if not district:
            return self._generate_general_response()
        
        # 分析政策
        analysis = self.analyze_enrollment_policy(district)
        policy = analysis['policy']
        schools = analysis['recommended_schools']
        
        # 生成回复
        response_parts = []
        
        # 1. 行政区划确认
        response_parts.append(f"📍 **行政区划确认**：{district}属于**{policy['prefecture']}**")
        
        # 2. 报考资格判断
        response_parts.append(f"\n🎓 **报考资格**：")
        if policy['can_apply_kunming']:
            response_parts.append(f"✅ {district}属于昆明市，可以正常报考昆明主城区高中")
            response_parts.append(f"   - 可报考公办高中（通过正常批次）")
            response_parts.append(f"   - 可报考民办高中")
        else:
            response_parts.append(f"❌ {district}属于{policy['prefecture']}，**不能跨州市报考昆明高中**")
            response_parts.append(f"   - 云南省实行各州市独立招生政策")
            response_parts.append(f"   - 只能报考{policy['prefecture']}内高中")
            response_parts.append(f"   - 少数省级学校可能有全省招生资格（需单独咨询）")
        
        # 3. 推荐学校
        if schools:
            response_parts.append(f"\n🏫 **{policy['prefecture']}优质高中推荐**：")
            for i, school in enumerate(schools[:5], 1):
                response_parts.append(f"   {i}. {school['name']}")
        
        # 4. 建议
        response_parts.append(f"\n💡 **建议**：")
        if policy['can_apply_kunming']:
            response_parts.append(f"   - 重点了解昆明市各高中的录取分数线和招生计划")
            response_parts.append(f"   - 合理设置冲刺、稳妥、保底志愿")
        else:
            response_parts.append(f"   - 重点了解{policy['prefecture']}内各高中的招生政策")
            response_parts.append(f"   - 关注{policy['prefecture']}教育局发布的招生简章")
            response_parts.append(f"   - 如有特殊情况需跨州市报考，请咨询当地教育局")
        
        return "\n".join(response_parts)
    
    def _generate_general_response(self) -> str:
        """生成通用回复（当无法识别区县时）"""
        return """您好！我是云南省中考招生政策智能助手。

为了给您提供准确的招生政策咨询，请告诉我您的**户籍所在地**（具体到区县），例如：
- 我在五华区
- 我的户籍在江川区
- 我是丘北县的

我将根据您的户籍所在地，为您分析：
1. 您所属的州市
2. 能否报考昆明高中
3. 您所在州市的优质高中推荐
4. 相关报考建议

**重要提示**：云南省实行各州市独立招生政策，一般情况下不能跨州市报考高中。"""
    
    def handle_query(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """处理用户查询"""
        response = self.generate_response(user_input, context)
        
        # 提取区县信息用于上下文
        district = self.extract_district(user_input)
        
        return {
            'success': True,
            'agent': 'policy_enrollment',
            'response': response,
            'extracted_district': district,
            'timestamp': datetime.now().isoformat()
        }


# 全局实例
_policy_agent = None


def get_policy_enrollment_agent() -> PolicyEnrollmentAgent:
    """获取招生政策智能体实例（单例）"""
    global _policy_agent
    if _policy_agent is None:
        _policy_agent = PolicyEnrollmentAgent()
    return _policy_agent


if __name__ == '__main__':
    # 测试招生政策智能体
    agent = PolicyEnrollmentAgent()
    
    print("=" * 70)
    print("招生政策智能体测试")
    print("=" * 70)
    
    # 测试用例
    test_cases = [
        "江川区",
        "丘北县",
        "五华区",
        "我是麒麟区的",
        "我的户籍在大理",
        "你好"
    ]
    
    for test_input in test_cases:
        print(f"\n{'='*70}")
        print(f"用户输入: {test_input}")
        print(f"{'='*70}")
        
        result = agent.handle_query(test_input)
        print(result['response'])
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)
