"""内容风险控制系统"""

import re
from typing import Dict, List, Tuple


class ContentRiskControl:
    """内容风险控制系统，用于检测和过滤敏感内容"""
    
    def __init__(self):
        """初始化风险控制系统"""
        # 敏感词列表
        self.sensitive_words = [
            '违法', '违规', '赌博', '色情', '暴力',
            '毒品', '政治', '敏感', '隐私', '个人信息'
        ]
        
        # 正则表达式模式
        self.patterns = {
            'phone': r'1[3-9]\d{9}',  # 手机号码
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # 邮箱
            'id_card': r'[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]'  # 身份证号
        }
    
    def check_content(self, content: str) -> Dict:
        """检查内容是否存在风险
        
        Args:
            content: 待检查的内容
            
        Returns:
            风险检查结果
        """
        result = {
            'has_risk': False,
            'risk_level': 'low',
            'risks': [],
            'suggestions': []
        }
        
        # 检查敏感词
        sensitive_risks = self._check_sensitive_words(content)
        if sensitive_risks:
            result['has_risk'] = True
            result['risks'].extend(sensitive_risks)
            result['suggestions'].append('请移除敏感词汇')
        
        # 检查个人信息
        personal_info_risks = self._check_personal_info(content)
        if personal_info_risks:
            result['has_risk'] = True
            result['risks'].extend(personal_info_risks)
            result['suggestions'].append('请保护个人隐私信息')
        
        # 评估风险等级
        result['risk_level'] = self._evaluate_risk_level(result['risks'])
        
        return result
    
    def _check_sensitive_words(self, content: str) -> List[Dict]:
        """检查敏感词
        
        Args:
            content: 待检查的内容
            
        Returns:
            敏感词风险列表
        """
        risks = []
        
        for word in self.sensitive_words:
            if word in content:
                risks.append({
                    'type': 'sensitive_word',
                    'detail': f'包含敏感词: {word}',
                    'level': 'medium'
                })
        
        return risks
    
    def _check_personal_info(self, content: str) -> List[Dict]:
        """检查个人信息
        
        Args:
            content: 待检查的内容
            
        Returns:
            个人信息风险列表
        """
        risks = []
        
        # 检查手机号
        phone_matches = re.findall(self.patterns['phone'], content)
        if phone_matches:
            risks.append({
                'type': 'personal_info',
                'detail': '包含手机号码',
                'level': 'high'
            })
        
        # 检查邮箱
        email_matches = re.findall(self.patterns['email'], content)
        if email_matches:
            risks.append({
                'type': 'personal_info',
                'detail': '包含邮箱地址',
                'level': 'medium'
            })
        
        # 检查身份证号
        id_card_matches = re.findall(self.patterns['id_card'], content)
        if id_card_matches:
            risks.append({
                'type': 'personal_info',
                'detail': '包含身份证号码',
                'level': 'high'
            })
        
        return risks
    
    def _evaluate_risk_level(self, risks: List[Dict]) -> str:
        """评估风险等级
        
        Args:
            risks: 风险列表
            
        Returns:
            风险等级: low, medium, high
        """
        if not risks:
            return 'low'
        
        high_risk_count = sum(1 for r in risks if r['level'] == 'high')
        medium_risk_count = sum(1 for r in risks if r['level'] == 'medium')
        
        if high_risk_count > 0:
            return 'high'
        elif medium_risk_count > 0:
            return 'medium'
        else:
            return 'low'
    
    def filter_content(self, content: str) -> str:
        """过滤内容中的敏感信息
        
        Args:
            content: 待过滤的内容
            
        Returns:
            过滤后的内容
        """
        filtered_content = content
        
        # 过滤敏感词
        for word in self.sensitive_words:
            filtered_content = filtered_content.replace(word, '*' * len(word))
        
        # 过滤手机号
        filtered_content = re.sub(self.patterns['phone'], '***-****-****', filtered_content)
        
        # 过滤邮箱
        filtered_content = re.sub(self.patterns['email'], '***@***', filtered_content)
        
        # 过滤身份证号
        filtered_content = re.sub(self.patterns['id_card'], '******************', filtered_content)
        
        return filtered_content
    
    def validate_user_input(self, user_input: str) -> Dict:
        """验证用户输入
        
        Args:
            user_input: 用户输入内容
            
        Returns:
            验证结果
        """
        # 检查输入长度
        if len(user_input) > 1000:
            return {
                'valid': False,
                'message': '输入内容过长，请控制在1000字以内',
                'code': 'length_exceeded'
            }
        
        if len(user_input) < 1:
            return {
                'valid': False,
                'message': '输入内容不能为空',
                'code': 'empty_input'
            }
        
        # 检查内容风险
        risk_result = self.check_content(user_input)
        if risk_result['risk_level'] == 'high':
            return {
                'valid': False,
                'message': '输入内容存在高风险，请修改后重试',
                'code': 'high_risk_content',
                'details': risk_result
            }
        
        return {
            'valid': True,
            'message': '输入内容验证通过',
            'code': 'valid'
        }
