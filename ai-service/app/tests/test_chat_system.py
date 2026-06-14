#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话系统综合测试套件
验证所有核心服务的功能和性能
"""

import unittest
import time
import random
import sys
import os

# 添加服务路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.semantic_analyzer import get_semantic_analyzer
from services.context_manager import get_enhanced_context_manager
from services.personalization_engine import get_personalization_engine
from services.knowledge_graph_service import get_knowledge_graph_service
from services.clarification_engine import get_clarification_engine
from services.dialog_state_manager import get_dialog_state_manager
from services.error_recovery_service import get_error_recovery_service
from services.continuous_learning_service import get_continuous_learning_service


class TestSemanticAnalyzer(unittest.TestCase):
    """语义分析器测试"""
    
    def setUp(self):
        self.analyzer = get_semantic_analyzer()
    
    def test_synonym_expansion(self):
        """测试同义词扩展"""
        result = self.analyzer.expand_synonyms("中考")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
    
    def test_coreference_resolution(self):
        """测试指代消解"""
        context = [{'role': 'user', 'content': '昆一中怎么样？'}]
        result = self.analyzer.resolve_coreference("它的录取分数线是多少？", context)
        self.assertIsInstance(result, tuple)
        self.assertTrue(len(result) == 2)
    
    def test_multi_intent_recognition(self):
        """测试多意图识别"""
        result = self.analyzer.recognize_intents("帮我分析一下昆一中和师大附中")
        self.assertIsInstance(result, list)
    
    def test_analyze(self):
        """测试完整语义分析"""
        context = []
        result = self.analyzer.analyze("昆一中怎么样？", context)
        self.assertIsNotNone(result)


class TestContextManager(unittest.TestCase):
    """上下文管理器测试"""
    
    def setUp(self):
        self.manager = get_enhanced_context_manager()
    
    def test_add_and_get_context(self):
        """测试添加和获取上下文"""
        session_id = "test_session_1"
        self.manager.add_message(session_id, 'user', '昆一中怎么样？')
        context = self.manager.get_context(session_id)
        self.assertEqual(len(context), 1)
    
    def test_topic_tracking(self):
        """测试主题追踪"""
        session_id = "test_session_2"
        self.manager.add_message(session_id, 'user', '昆一中怎么样？')
        topic = self.manager.get_current_topic(session_id)
        self.assertIsNotNone(topic)
    
    def test_summary_generation(self):
        """测试摘要生成"""
        session_id = "test_session_3"
        self.manager.add_message(session_id, 'user', '昆一中怎么样？')
        self.manager.add_message(session_id, 'bot', '昆一中是省级重点中学')
        summary = self.manager.generate_summary(session_id)
        self.assertTrue(len(summary) > 0)
    
    def test_dominant_topic(self):
        """测试主导主题识别"""
        session_id = "test_session_4"
        self.manager.add_message(session_id, 'user', '昆一中的录取分数线是多少？')
        dominant = self.manager.get_dominant_topic(session_id)
        self.assertIsNotNone(dominant)


class TestKnowledgeGraphService(unittest.TestCase):
    """知识图谱服务测试"""
    
    def setUp(self):
        self.service = get_knowledge_graph_service()
    
    def test_school_query(self):
        """测试学校查询"""
        school = self.service.query_school('师大附中')
        self.assertIsNotNone(school)
        self.assertEqual(school['name'], '云南师范大学附属中学')
    
    def test_policy_query(self):
        """测试政策查询"""
        policy = self.service.query_policy('录取分数线')
        self.assertIsNotNone(policy)
    
    def test_admission_probability(self):
        """测试录取概率推理"""
        probability, explanation = self.service.infer_admission_probability(650, '昆一中')
        self.assertTrue(0 <= probability <= 100)
        self.assertTrue(len(explanation) > 0)
    
    def test_school_compare(self):
        """测试学校对比"""
        result = self.service.compare_schools(['师大附中', '昆一中'])
        self.assertIn('schools', result)
    
    def test_school_statistics(self):
        """测试学校统计"""
        stats = self.service.get_school_statistics()
        self.assertIn('total_schools', stats)


class TestClarificationEngine(unittest.TestCase):
    """澄清引擎测试"""
    
    def setUp(self):
        self.engine = get_clarification_engine()
    
    def test_missing_info_detection(self):
        """测试缺失信息检测"""
        missing = self.engine.detect_missing_info("我想了解昆一中", {})
        self.assertIsInstance(missing, list)
    
    def test_clarification_generation(self):
        """测试澄清生成"""
        needs_clarify, message = self.engine.analyze_and_clarify("帮我推荐学校", {})
        self.assertTrue(needs_clarify)
        self.assertTrue(len(message) > 0)
    
    def test_intent_confirmation(self):
        """测试意图确认"""
        confirm = self.engine.confirm_intent('查询录取分数线', 0.65)
        self.assertIsNotNone(confirm)
    
    def test_response_validation(self):
        """测试响应验证"""
        self.assertTrue(self.engine.validate_response('650分', 'score'))
        self.assertFalse(self.engine.validate_response('abc', 'score'))


class TestDialogStateManager(unittest.TestCase):
    """对话状态管理器测试"""
    
    def setUp(self):
        self.manager = get_dialog_state_manager()
        self.session_id = self.manager.create_session()
    
    def test_session_creation(self):
        """测试会话创建"""
        self.assertIsNotNone(self.manager.get_session(self.session_id))
    
    def test_topic_management(self):
        """测试话题管理"""
        topic_id = self.manager.add_topic(self.session_id, '学校查询')
        self.assertTrue(len(topic_id) > 0)
    
    def test_context_update(self):
        """测试上下文更新"""
        self.manager.update_context(self.session_id, 'score', 650)
        context = self.manager.get_context(self.session_id)
        self.assertEqual(context['score'], 650)
    
    def test_session_summary(self):
        """测试会话摘要"""
        summary = self.manager.get_session_summary(self.session_id)
        self.assertIsNotNone(summary)
    
    def test_switch_topic(self):
        """测试话题切换"""
        topic_id1 = self.manager.add_topic(self.session_id, '话题1')
        topic_id2 = self.manager.add_topic(self.session_id, '话题2')
        result = self.manager.switch_topic(self.session_id, topic_id2)
        self.assertTrue(result)


class TestErrorRecoveryService(unittest.TestCase):
    """错误恢复服务测试"""
    
    def setUp(self):
        self.service = get_error_recovery_service()
    
    def test_unanswerable_detection(self):
        """测试无法回答检测"""
        self.assertTrue(self.service.is_unanswerable("你好"))
        self.assertFalse(self.service.is_unanswerable("昆一中怎么样？"))
    
    def test_input_validation(self):
        """测试输入验证"""
        valid, msg = self.service.validate_input("正常问题")
        self.assertTrue(valid)
        
        valid, msg = self.service.validate_input("")
        self.assertFalse(valid)
    
    def test_friendly_error(self):
        """测试友好错误提示"""
        msg = self.service.generate_friendly_error('unanswerable')
        self.assertTrue(len(msg) > 0)
    
    def test_retry_mechanism(self):
        """测试重试机制"""
        def success_on_second():
            success_on_second.count = getattr(success_on_second, 'count', 0) + 1
            if success_on_second.count >= 2:
                return "成功"
            raise ValueError("失败")
        
        success_on_second.count = 0
        success, result = self.service.retry_with_backoff(success_on_second)
        self.assertTrue(success)


class TestContinuousLearningService(unittest.TestCase):
    """持续学习服务测试"""
    
    def setUp(self):
        self.service = get_continuous_learning_service()
    
    def test_feedback_collection(self):
        """测试反馈收集"""
        feedback_id = self.service.collect_feedback("test", "问题", "回答", 5)
        self.assertTrue(len(feedback_id) > 0)
    
    def test_quality_evaluation(self):
        """测试质量评估"""
        metrics = self.service.evaluate_quality("问题", "回答")
        self.assertTrue(0 <= metrics.accuracy <= 1)
    
    def test_feedback_analysis(self):
        """测试反馈分析"""
        analysis = self.service.analyze_feedbacks()
        self.assertIn('total_count', analysis)
    
    def test_learning_summary(self):
        """测试学习摘要"""
        summary = self.service.get_learning_summary()
        self.assertIn('total_feedbacks', summary)


class TestPerformance(unittest.TestCase):
    """性能测试"""
    
    def test_response_time(self):
        """测试响应时间"""
        analyzer = get_semantic_analyzer()
        kg_service = get_knowledge_graph_service()
        
        start_time = time.time()
        for _ in range(10):
            analyzer.analyze("昆一中怎么样？", [])
            kg_service.query_school('昆一中')
        elapsed = time.time() - start_time
        
        avg_time = elapsed / 10
        self.assertLess(avg_time, 0.5, f"平均响应时间{avg_time:.3f}秒超过0.5秒")
    
    def test_concurrent_sessions(self):
        """测试并发会话支持"""
        manager = get_dialog_state_manager()
        session_ids = []
        
        start_time = time.time()
        for i in range(50):
            session_id = manager.create_session()
            session_ids.append(session_id)
            manager.add_topic(session_id, f'话题{i}')
        elapsed = time.time() - start_time
        
        self.assertLess(elapsed, 2.0, f"创建50个会话耗时{elapsed:.3f}秒超过2秒")
        
        # 清理
        for session_id in session_ids:
            manager.delete_session(session_id)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_conversation_flow(self):
        """测试完整对话流程"""
        # 初始化服务
        semantic_analyzer = get_semantic_analyzer()
        state_manager = get_dialog_state_manager()
        kg_service = get_knowledge_graph_service()
        clarification_engine = get_clarification_engine()
        
        # 创建会话
        session_id = state_manager.create_session()
        
        # 处理用户消息
        user_message = "我考了650分，想了解昆一中"
        
        # 语义分析
        analysis = semantic_analyzer.analyze(user_message, [])
        
        # 更新上下文
        state_manager.update_context(session_id, 'message', user_message)
        
        # 检查是否需要澄清
        context = state_manager.get_context(session_id)
        needs_clarify, _ = clarification_engine.analyze_and_clarify(user_message, context)
        
        # 查询知识图谱
        school = kg_service.query_school('昆一中')
        
        # 推理录取概率
        probability, _ = kg_service.infer_admission_probability(650, '昆一中')
        
        # 验证结果
        self.assertIsNotNone(analysis)
        self.assertIsNotNone(school)
        self.assertTrue(0 <= probability <= 100)


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("对话系统综合测试套件")
    print("=" * 70)
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试用例
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestSemanticAnalyzer))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestContextManager))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestKnowledgeGraphService))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestClarificationEngine))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestDialogStateManager))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestErrorRecoveryService))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestContinuousLearningService))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestPerformance))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出统计
    print("\n" + "=" * 70)
    print("测试统计")
    print("=" * 70)
    print(f"运行测试数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    print(f"跳过数: {len(result.skipped)}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n成功率: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
