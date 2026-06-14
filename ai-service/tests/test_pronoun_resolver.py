"""
指代词解析器单元测试
"""

import pytest
from agents.pronoun_resolver import (
    PronounResolver, 
    EntityTracker, 
    ContextualQueryClassifier,
    ResolvedEntity,
    resolve_pronouns,
    classify_query
)


class TestPronounResolver:
    """指代词解析器测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.resolver = PronounResolver()
    
    def test_extract_pronouns_basic(self):
        """测试提取基本指代词"""
        pronouns = self.resolver._extract_pronouns("它的分数线是多少")
        assert "它" in pronouns
    
    def test_extract_pronouns_compound(self):
        """测试提取复合指代词"""
        pronouns = self.resolver._extract_pronouns("这所学校的学费贵吗")
        assert "这所学校" in pronouns
    
    def test_extract_pronouns_multiple(self):
        """测试提取多个指代词"""
        pronouns = self.resolver._extract_pronouns("它们和这所学校相比怎么样")
        assert "它们" in pronouns
        assert "这所学校" in pronouns
    
    def test_extract_schools(self):
        """测试提取学校名称"""
        schools = self.resolver._extract_schools("师大附中是一所好学校")
        assert len(schools) > 0
        assert "师大附中" in schools
    
    def test_extract_schools_complex(self):
        """测试提取复杂学校名称"""
        schools = self.resolver._extract_schools("云南省昆明第三中学和云南师范大学附属中学")
        assert len(schools) >= 2
    
    def test_resolve_basic(self):
        """测试基本指代词解析"""
        history = [
            {'role': 'user', 'content': '师大附中怎么样'},
            {'role': 'assistant', 'content': '云南师范大学附属中学是一所优秀的学校'}
        ]
        resolved_text, entity = self.resolver.resolve("它的分数线是多少", history)
        
        assert entity is not None
        assert entity.entity_type == 'school'
        # 检查是否包含学校相关关键词
        assert any(kw in entity.entity_name for kw in ['附中', '师范', '中学'])
    
    def test_resolve_this_school(self):
        """测试"这所学校"解析"""
        history = [
            {'role': 'user', 'content': '昆明市第三中学好不好'},
            {'role': 'assistant', 'content': '昆明市第三中学是一所优质高中'}
        ]
        resolved_text, entity = self.resolver.resolve("这所学校的学费是多少", history)
        
        assert entity is not None
        assert '昆明市第三中学' in entity.entity_name
    
    def test_resolve_that_school(self):
        """测试"那所学校"解析"""
        history = [
            {'role': 'user', 'content': '云南大学附属中学'},
            {'role': 'assistant', 'content': '云大附中是云南省一级一等完中'}
        ]
        resolved_text, entity = self.resolver.resolve("那所学校的录取分数线是多少", history)
        
        assert entity is not None
        assert entity.entity_type == 'school'
        # 检查是否包含学校相关关键词
        assert any(kw in entity.entity_name for kw in ['附中', '大学', '中学', '一级'])
    
    def test_resolve_no_pronoun(self):
        """测试无指代词情况"""
        history = [
            {'role': 'user', 'content': '师大附中怎么样'}
        ]
        resolved_text, entity = self.resolver.resolve("师大附中的分数线", history)
        
        assert entity is None
        assert resolved_text == "师大附中的分数线"
    
    def test_resolve_no_history(self):
        """测试无历史对话情况"""
        resolved_text, entity = self.resolver.resolve("它的分数线是多少", [])
        
        assert entity is None
        assert resolved_text == "它的分数线是多少"
    
    def test_replace_pronouns(self):
        """测试指代词替换"""
        entity = ResolvedEntity(
            entity_type='school',
            entity_name='昆明市第三中学',
            confidence=0.95,
            original_pronoun='它'
        )
        result = self.resolver._replace_pronouns("它的分数线是多少", entity)
        
        assert "昆明市第三中学" in result
    
    def test_replace_compound_pronoun(self):
        """测试复合指代词替换"""
        entity = ResolvedEntity(
            entity_type='school',
            entity_name='云南师范大学附属中学',
            confidence=0.95,
            original_pronoun='这所学校'
        )
        result = self.resolver._replace_pronouns("这所学校怎么样", entity)
        
        assert "云南师范大学附属中学" in result
        assert "这所学校" not in result


class TestEntityTracker:
    """实体追踪器测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.tracker = EntityTracker()
    
    def test_track_entity(self):
        """测试跟踪实体"""
        self.tracker.track_entity('school', '师大附中')
        entities = self.tracker.get_recent_entities()
        
        assert len(entities) == 1
        assert entities[0]['name'] == '师大附中'
    
    def test_track_multiple_entities(self):
        """测试跟踪多个实体"""
        self.tracker.track_entity('school', '师大附中')
        self.tracker.track_entity('school', '昆三中')
        entities = self.tracker.get_recent_entities()
        
        assert len(entities) == 2
    
    def test_get_last_school(self):
        """测试获取最后学校"""
        self.tracker.track_entity('school', '师大附中')
        self.tracker.track_entity('school', '昆三中')
        
        last_school = self.tracker.get_last_school()
        assert last_school == '昆三中'
    
    def test_update_from_history(self):
        """测试从历史更新"""
        history = [
            {'content': '师大附中怎么样', 'created_at': '2024-01-01'},
            {'content': '昆三中的分数线', 'created_at': '2024-01-02'}
        ]
        self.tracker.update_from_history(history)
        
        entities = self.tracker.get_recent_entities()
        assert len(entities) >= 1


class TestContextualQueryClassifier:
    """上下文查询分类器测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.classifier = ContextualQueryClassifier()
    
    def test_classify_score_inquiry(self):
        """测试分类分数查询"""
        result = self.classifier.classify("它的分数线是多少")
        assert result == 'score_inquiry'
    
    def test_classify_fee_inquiry(self):
        """测试分类费用查询"""
        result = self.classifier.classify("这所学校的学费是多少")
        assert result == 'fee_inquiry'
    
    def test_classify_feature_inquiry(self):
        """测试分类特色查询"""
        result = self.classifier.classify("师大附中怎么样")
        assert result == 'feature_inquiry'
    
    def test_classify_admission_inquiry(self):
        """测试分类录取查询"""
        result = self.classifier.classify("如何报考这所学校")
        assert result == 'admission_inquiry'
    
    def test_classify_general(self):
        """测试分类通用查询"""
        result = self.classifier.classify("你好")
        assert result == 'general'
    
    def test_generate_response(self):
        """测试生成响应"""
        entity = ResolvedEntity(
            entity_type='school',
            entity_name='师大附中',
            confidence=0.95,
            original_pronoun='它'
        )
        response = self.classifier.generate_response('score_inquiry', entity)
        
        assert '师大附中' in response


class TestPronounResolverIntegration:
    """指代词解析器集成测试"""
    
    def test_full_conversation_flow(self):
        """测试完整对话流程"""
        resolver = PronounResolver()
        
        # 第一轮：询问学校
        history1 = []
        resolved_text1, entity1 = resolver.resolve("师大附中怎么样", history1)
        assert entity1 is None  # 第一次对话没有指代词
        
        # 更新历史
        history2 = [
            {'role': 'user', 'content': '师大附中怎么样'},
            {'role': 'assistant', 'content': '云南师范大学附属中学是云南省一级一等高中'}
        ]
        
        # 第二轮：使用指代词"它"
        resolved_text2, entity2 = resolver.resolve("它的分数线是多少", history2)
        assert entity2 is not None
        assert entity2.entity_type == 'school'
        assert '分数线' in resolved_text2
        
        # 更新历史
        history3 = history2 + [
            {'role': 'user', 'content': '它的分数线是多少'},
            {'role': 'assistant', 'content': '师大附中去年录取线约620分'}
        ]
        
        # 第三轮：使用指代词"该校"
        resolved_text3, entity3 = resolver.resolve("该校的学费贵吗", history3)
        assert entity3 is not None
        assert entity3.entity_type == 'school'
        
        # 第四轮：使用指代词"这所学校"
        history4 = history3 + [
            {'role': 'user', 'content': '该校的学费贵吗'},
            {'role': 'assistant', 'content': '公办学校学费相对较低'}
        ]
        resolved_text4, entity4 = resolver.resolve("这所学校好吗", history4)
        assert entity4 is not None
        assert entity4.entity_type == 'school'
    
    def test_pronoun_variations(self):
        """测试各种指代词变体"""
        resolver = PronounResolver()
        
        history = [
            {'role': 'user', 'content': '云南师范大学附属中学'},
            {'role': 'assistant', 'content': '云南师范大学附属中学是一所知名高中'}
        ]
        
        # 测试各种指代词
        pronouns_to_test = [
            "它的分数线",
            "该校的分数线",
            "这所学校的分数线",
            "那所学校的分数线",
            "这所中学的分数线",
            "那所中学的分数线"
        ]
        
        for pronoun_query in pronouns_to_test:
            resolved_text, entity = resolver.resolve(pronoun_query, history.copy())
            assert entity is not None, f"Failed to resolve: {pronoun_query}"
            assert entity.entity_type == 'school'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])