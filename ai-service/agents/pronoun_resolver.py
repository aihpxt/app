"""
统一的指代词解析服务
解决指代词处理逻辑分散、难以维护的问题
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from collections import OrderedDict


@dataclass
class ResolvedEntity:
    """解析后的实体"""
    entity_type: str  # 'school', 'policy', 'score', etc.
    entity_name: str
    confidence: float
    original_pronoun: str
    source_message: str = ""


class PronounResolver:
    """指代词解析器"""

    # 指代词映射表 - 扩展支持更多指代词
    PRONOUNS = {
        # 人称代词
        "它": "third_person",
        "他们": "third_person_plural",
        "她们": "third_person_plural",
        "它们": "third_person_plural",
        
        # 指示代词
        "这个": "demonstrative_this",
        "那个": "demonstrative_that",
        "这些": "demonstrative_these",
        "那些": "demonstrative_those",
        
        # 正式用语
        "此": "formal_this",
        "其": "formal_that",
        
        # 学校相关指代词
        "该校": "school_reference",
        "这所学校": "school_reference",
        "那所学校": "school_reference",
        "这所中学": "school_reference",
        "那所中学": "school_reference",
        "这所高中": "school_reference",
        "那所高中": "school_reference",
        "该中学": "school_reference",
        "该高中": "school_reference",
        
        # 其他
        "那个学校": "school_reference",
        "这个学校": "school_reference",
        "那间学校": "school_reference",
        "这间学校": "school_reference",
    }

    # 学校相关关键词
    SCHOOL_KEYWORDS = ['中学', '高中', '一中', '二中', '三中', '四中', '五中', 
                       '附中', '附小', '实验中学', '外国语', '民族中学', '职业中学']

    # 学校类型关键词
    SCHOOL_TYPES = ['小学', '初中', '高中', '完中', '职中', '中专']

    def __init__(self, context_window_size: int = 10):
        self.resolution_cache = {}
        self.context_window_size = context_window_size
        self.entity_tracker = EntityTracker()

    def resolve(self, user_input: str, history: List[Dict[str, Any]],
                context: Optional[Dict] = None) -> Tuple[str, Optional[ResolvedEntity]]:
        """
        解析用户输入中的指代词

        Args:
            user_input: 用户输入文本
            history: 对话历史消息列表
            context: 可选的上下文信息

        Returns:
            Tuple[替换后的文本, 解析出的实体对象]
        """
        if not user_input:
            return user_input, None

        # 1. 更新实体追踪器
        self.entity_tracker.update_from_history(history)

        # 2. 检测输入中是否包含指代词
        pronouns_in_input = self._extract_pronouns(user_input)
        if not pronouns_in_input:
            return user_input, None

        # 3. 获取候选实体（从追踪器和历史中）
        entities = self.entity_tracker.get_recent_entities()
        if not entities:
            entities = self._find_entities_in_history(history)

        if not entities:
            return user_input, None

        # 4. 根据指代词类型选择最合适的实体
        resolved_entity = self._select_best_entity(pronouns_in_input, entities, context)

        if resolved_entity:
            # 更新追踪器
            self.entity_tracker.track_entity(resolved_entity.entity_type, 
                                             resolved_entity.entity_name)
            
            # 5. 替换指代词为实体名称
            resolved_text = self._replace_pronouns(user_input, resolved_entity)
            return resolved_text, resolved_entity

        return user_input, None

    def _extract_pronouns(self, text: str) -> List[str]:
        """提取文本中的指代词"""
        pronouns_found = []
        
        # 优先检查复合指代词（如"这所学校"），避免被拆分成单个词
        for pronoun in sorted(self.PRONOUNS.keys(), key=len, reverse=True):
            if pronoun in text:
                pronouns_found.append(pronoun)
        
        return pronouns_found

    def _find_entities_in_history(self, history: List[Dict[str, Any]]) -> List[Dict]:
        """从历史消息中查找实体"""
        entities = []

        # 按时间倒序遍历历史，限制窗口大小
        recent_history = history[-self.context_window_size:]
        
        for msg in reversed(recent_history):
            content = msg.get('content', '')
            role = msg.get('role', '')
            created_at = msg.get('created_at', '')

            # 查找学校名称
            schools = self._extract_schools(content)
            for school in schools:
                entities.append({
                    'type': 'school',
                    'name': school,
                    'from_role': role,
                    'from_message': content[:100],
                    'created_at': created_at,
                    'confidence': self._calculate_entity_confidence(school, content)
                })

            # 查找政策关键词
            policies = self._extract_policies(content)
            for policy in policies:
                entities.append({
                    'type': 'policy',
                    'name': policy,
                    'from_role': role,
                    'from_message': content[:100],
                    'created_at': created_at,
                    'confidence': 0.7
                })

            # 查找分数相关实体
            scores = self._extract_scores(content)
            for score in scores:
                entities.append({
                    'type': 'score',
                    'name': score,
                    'from_role': role,
                    'from_message': content[:100],
                    'created_at': created_at,
                    'confidence': 0.85
                })

            # 如果找到足够的实体就停止
            if len(entities) >= 5:
                break

        # 按置信度排序
        entities.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        return entities

    def _extract_schools(self, text: str) -> List[str]:
        """从文本中提取学校名称"""
        schools = []
        
        # 使用滑动窗口方法在文本中查找学校名称
        # 移除标点符号但保留中文
        cleaned_text = re.sub(r'[，。？！、；：""''（）()[]{}《》<>]', ' ', text)
        
        # 方法1：使用正则表达式提取
        school_patterns = [
            # 精确匹配学校名称模式
            r'(云南省[\u4e00-\u9fa5]{1,4}市?[\u4e00-\u9fa5]{1,6}中学)',   # 云南省XX(市)XX中学
            r'([\u4e00-\u9fa5]{1,4}市[\u4e00-\u9fa5]{1,6}中学)',          # XX市XX中学  
            r'([\u4e00-\u9fa5]{2,8}第[一二三四五六七八九十]+中学)',         # XX第一中学等
            r'([\u4e00-\u9fa5]{2,8}[一中二中三中四中五中])',              # XX一中、XX二中等
            r'([\u4e00-\u9fa5]{2,8}附属中学)',                            # XX附属中学
            r'([\u4e00-\u9fa5]{2,8}高级中学)',                            # XX高级中学
            r'([\u4e00-\u9fa5]{2,8}[实验外国语民族职业]中学)',             # 特殊类型中学
            r'([\u4e00-\u9fa5]{2,4}附中)',                                # XX附中
        ]
        
        for pattern in school_patterns:
            matches = re.findall(pattern, cleaned_text)
            for match in matches:
                if self._is_valid_school_name(match) and match not in schools:
                    schools.append(match)
        
        # 方法2：滑动窗口查找（作为补充）
        if not schools:
            text_length = len(cleaned_text)
            # 从长到短查找，避免匹配到较短的子串
            for window_size in range(12, 3, -1):
                for i in range(text_length - window_size + 1):
                    candidate = cleaned_text[i:i+window_size].strip()
                    if self._is_valid_school_name(candidate) and candidate not in schools:
                        schools.append(candidate)
        
        return schools
    
    def _is_valid_school_name(self, name: str) -> bool:
        """判断是否为有效的学校名称"""
        if len(name) < 4:
            return False
        
        # 排除常见的非学校名称结尾
        invalid_suffixes = ['完中', '完', '高等', '一级', '二级']
        for suffix in invalid_suffixes:
            if name.endswith(suffix):
                return False
        
        # 必须包含学校关键词
        has_keyword = any(kw in name for kw in ['中学', '高中', '附中', '附小'])
        if not has_keyword:
            return False
        
        return True

    def _extract_policies(self, text: str) -> List[str]:
        """从文本中提取政策关键词"""
        policies = []
        policy_keywords = [
            '中考政策', '志愿填报', '录取规则', '招生计划', 
            '分数线', '加分政策', '定向招生', '自主招生',
            '中考', '志愿', '填报', '录取', '招生'
        ]

        for keyword in policy_keywords:
            if keyword in text:
                policies.append(keyword)

        return policies

    def _extract_scores(self, text: str) -> List[str]:
        """从文本中提取分数"""
        scores = []
        
        # 匹配分数模式
        score_patterns = [
            r'(\d{3,4})分',      # 三位数或四位数分数
            r'(\d{3,4})\s*分',
            r'分数线[\u4e00-\u9fa5]*(\d{3,4})',
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, text)
            scores.extend(matches)

        return scores

    def _calculate_entity_confidence(self, entity_name: str, context: str) -> float:
        """计算实体置信度"""
        confidence = 0.7
        
        # 如果实体名称包含更多字符，置信度更高
        if len(entity_name) >= 6:
            confidence += 0.1
        
        # 如果在上下文中多次出现
        if context.count(entity_name) >= 2:
            confidence += 0.1
        
        # 如果包含明确的学校关键词
        for kw in ['中学', '高中', '附中']:
            if kw in entity_name:
                confidence += 0.05
                break
        
        return min(confidence, 0.95)

    def _select_best_entity(self, pronouns: List[str], entities: List[Dict],
                            context: Optional[Dict]) -> Optional[ResolvedEntity]:
        """根据上下文选择最合适的实体"""
        if not entities:
            return None

        # 分析指代词类型
        pronoun_types = set(self.PRONOUNS[p] for p in pronouns)
        
        # 优先选择学校实体（这是中考择校场景的核心）
        school_entities = [e for e in entities if e['type'] == 'school']
        if school_entities:
            # 选择置信度最高的学校
            best_school = max(school_entities, key=lambda x: x.get('confidence', 0))
            return ResolvedEntity(
                entity_type='school',
                entity_name=best_school['name'],
                confidence=best_school.get('confidence', 0.95),
                original_pronoun=', '.join(pronouns),
                source_message=best_school.get('from_message', '')
            )

        # 如果没有学校，根据指代词类型选择
        if entities:
            entity = entities[0]
            return ResolvedEntity(
                entity_type=entity['type'],
                entity_name=entity['name'],
                confidence=entity.get('confidence', 0.8),
                original_pronoun=', '.join(pronouns),
                source_message=entity.get('from_message', '')
            )

        return None

    def _replace_pronouns(self, text: str, entity: ResolvedEntity) -> str:
        """将指代词替换为实体名称"""
        result = text

        # 按长度排序，优先替换长指代词
        pronouns_sorted = sorted(self.PRONOUNS.keys(), key=len, reverse=True)
        
        for pronoun in pronouns_sorted:
            if pronoun in result:
                # 根据实体类型和指代词决定替换方式
                if entity.entity_type == 'school':
                    # 对于学校，使用自然的表达方式
                    if pronoun in ['这所学校', '那所学校', '该校', '这个学校', '那个学校']:
                        result = result.replace(pronoun, entity.entity_name)
                    elif pronoun in ['这所中学', '那所中学', '该中学']:
                        result = result.replace(pronoun, entity.entity_name)
                    elif pronoun in ['这所高中', '那所高中', '该高中']:
                        result = result.replace(pronoun, entity.entity_name)
                    else:
                        # 其他指代词，添加引号
                        result = result.replace(pronoun, f"'{entity.entity_name}'")
                else:
                    result = result.replace(pronoun, entity.entity_name)

        return result


class EntityTracker:
    """实体追踪器 - 跟踪对话中提到的实体"""

    def __init__(self, max_tracked: int = 5):
        self.max_tracked = max_tracked
        self.entities = OrderedDict()  # {entity_name: {'type': ..., 'count': ..., 'last_seen': ...}}
        self.school_entities = OrderedDict()  # 专门跟踪学校实体

    def update_from_history(self, history: List[Dict[str, Any]]):
        """从历史消息中更新实体追踪"""
        from datetime import datetime
        
        for msg in history:
            content = msg.get('content', '')
            created_at = msg.get('created_at', datetime.now().isoformat())
            
            # 提取学校
            school_patterns = [
                r'([\u4e00-\u9fa5]{2,8}[中学高中])',
                r'([\u4e00-\u9fa5]+附属[中学])',
            ]
            
            for pattern in school_patterns:
                matches = re.findall(pattern, content)
                for school in matches:
                    self.track_entity('school', school, created_at)

    def track_entity(self, entity_type: str, entity_name: str, timestamp: str = None):
        """跟踪实体"""
        from datetime import datetime
        
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        # 更新通用实体追踪
        if entity_name in self.entities:
            self.entities[entity_name]['count'] += 1
            self.entities[entity_name]['last_seen'] = timestamp
        else:
            self.entities[entity_name] = {
                'type': entity_type,
                'count': 1,
                'last_seen': timestamp
            }
        
        # 对于学校实体，额外跟踪
        if entity_type == 'school':
            if entity_name in self.school_entities:
                self.school_entities[entity_name]['count'] += 1
                self.school_entities[entity_name]['last_seen'] = timestamp
            else:
                self.school_entities[entity_name] = {
                    'count': 1,
                    'last_seen': timestamp
                }
        
        # 限制数量
        self._trim()

    def _trim(self):
        """修剪超出限制的实体"""
        # 保持最近的实体
        self.entities = OrderedDict(list(self.entities.items())[-self.max_tracked:])
        self.school_entities = OrderedDict(list(self.school_entities.items())[-self.max_tracked:])

    def get_recent_entities(self) -> List[Dict]:
        """获取最近跟踪的实体"""
        entities = []
        
        # 优先返回学校实体
        for name, info in reversed(self.school_entities.items()):
            entities.append({
                'type': 'school',
                'name': name,
                'confidence': min(0.7 + info['count'] * 0.1, 0.95),
                'from_message': '',
                'created_at': info['last_seen']
            })
        
        # 添加其他实体
        for name, info in reversed(self.entities.items()):
            if info['type'] != 'school':
                entities.append({
                    'type': info['type'],
                    'name': name,
                    'confidence': min(0.6 + info['count'] * 0.1, 0.85),
                    'from_message': '',
                    'created_at': info['last_seen']
                })
        
        return entities

    def get_last_school(self) -> Optional[str]:
        """获取最后提到的学校"""
        if self.school_entities:
            return next(reversed(self.school_entities.keys()))
        return None


class ContextualQueryClassifier:
    """上下文查询分类器"""

    # 查询类型模式
    QUERY_PATTERNS = {
        'score_inquiry': {
            'keywords': ['分数线', '录取线', '多少分', '分数', '录取分数', '投档线'],
            'context_keywords': ['学校', '高中', '中学', '附中'],
            'response_template': "根据您提到的{school}，我来为您查询相关信息。\n\n{school}的录取分数线会因年份和地区而有所不同。一般来说：\n\n• 一级一等高完中：580-650分\n• 一级二等高完中：540-580分\n• 普通高完中：480-540分\n\n建议您使用我们的学校查询功能获取最新、最准确的录取分数线信息。"
        },
        'fee_inquiry': {
            'keywords': ['学费', '费用', '收费', '多少钱', '价格', '缴费'],
            'response_template': "关于{school}的费用情况：\n\n【公办高中（重点高中）】\n• 学费：约200-400元/学期\n• 住宿费：约300-600元/学期\n\n【民办高中】\n• 学费：约5000-20000元/学期不等\n\n具体费用以{school}官方公布为准。"
        },
        'feature_inquiry': {
            'keywords': ['怎么样', '好吗', '好不好', '特色', '优势', '评价'],
            'response_template': "关于{school}的情况，我来为您详细介绍：\n\n【学校简介】\n{school}是云南省内的知名学校...\n\n需要了解更多详细信息吗？"
        },
        'admission_inquiry': {
            'keywords': ['录取', '招生', '报考', '报名', '入学', '条件'],
            'response_template': "{school}的招生录取信息如下：\n\n【录取方式】\n• 按中考成绩录取\n• 部分学校有自主招生名额\n\n【报名时间】\n一般在中考成绩公布后进行志愿填报\n\n建议关注{school}官方网站获取最新招生信息。"
        },
        'campus_inquiry': {
            'keywords': ['校园', '环境', '宿舍', '食堂', '设施', '住宿'],
            'response_template': "关于{school}的校园环境：\n\n• 校园占地面积：待补充\n• 宿舍条件：待补充\n• 食堂情况：待补充\n\n如需更详细信息，建议联系学校招生办。"
        }
    }

    def classify(self, user_input: str, resolved_entity: Optional[ResolvedEntity] = None) -> str:
        """分类查询类型"""
        user_input_lower = user_input.lower()

        for query_type, pattern in self.QUERY_PATTERNS.items():
            # 检查关键词
            if any(kw in user_input_lower for kw in pattern['keywords']):
                return query_type

        return 'general'

    def generate_response(self, query_type: str, entity: ResolvedEntity) -> str:
        """根据查询类型和实体生成响应"""
        template = self.QUERY_PATTERNS.get(query_type, {}).get('response_template', '')

        if not template:
            return ''

        # 替换模板中的占位符
        response = template.replace('{school}', entity.entity_name)

        return response


# 全局实例
pronoun_resolver = PronounResolver()
query_classifier = ContextualQueryClassifier()


# 便捷函数
def resolve_pronouns(user_input: str, history: List[Dict], context: Optional[Dict] = None) -> Tuple[str, Optional[ResolvedEntity]]:
    """便捷函数：解析指代词"""
    return pronoun_resolver.resolve(user_input, history, context)


def classify_query(user_input: str, entity: Optional[ResolvedEntity] = None) -> str:
    """便捷函数：分类查询类型"""
    return query_classifier.classify(user_input, entity)
