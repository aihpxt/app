#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持续学习机制服务
负责用户反馈收集、在线学习、问答质量评估
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)


class FeedbackRecord:
    """反馈记录类"""
    
    def __init__(self, feedback_id: str, session_id: str, question: str, 
                 answer: str, rating: int, comment: str = ""):
        self.feedback_id = feedback_id
        self.session_id = session_id
        self.question = question
        self.answer = answer
        self.rating = rating  # 1-5分
        self.comment = comment
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'feedback_id': self.feedback_id,
            'session_id': self.session_id,
            'question': self.question,
            'answer': self.answer,
            'rating': self.rating,
            'comment': self.comment,
            'timestamp': self.timestamp
        }


class QualityMetrics:
    """质量评估指标"""
    
    def __init__(self):
        self.accuracy = 0.0
        self.relevance = 0.0
        self.completeness = 0.0
        self.user_satisfaction = 0.0
        self.response_time_ms = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'accuracy': self.accuracy,
            'relevance': self.relevance,
            'completeness': self.completeness,
            'user_satisfaction': self.user_satisfaction,
            'response_time_ms': self.response_time_ms
        }


class ContinuousLearningService:
    """持续学习机制服务"""
    
    def __init__(self):
        self.feedbacks: List[FeedbackRecord] = []
        self.model_updates: List[Dict[str, Any]] = []
        self.quality_history: List[Dict[str, Any]] = []
        self.learning_enabled = True
        self.feedback_threshold = 10  # 每10条反馈触发一次学习
        
        # 模拟学习率和模型参数
        self.learning_rate = 0.01
        self.model_confidence = 0.85
        
        # 反馈文件路径
        self.feedback_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'feedbacks.json')
        self._ensure_data_dir()
        
        logger.info("持续学习机制服务初始化完成")
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        data_dir = os.path.dirname(self.feedback_file)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def collect_feedback(self, session_id: str, question: str, answer: str, 
                        rating: int, comment: str = "") -> str:
        """
        收集用户反馈
        
        Args:
            session_id: 会话ID
            question: 用户问题
            answer: 系统回答
            rating: 用户评分(1-5)
            comment: 用户评论
        
        Returns:
            反馈记录ID
        """
        import uuid
        feedback_id = str(uuid.uuid4())
        
        record = FeedbackRecord(
            feedback_id=feedback_id,
            session_id=session_id,
            question=question,
            answer=answer,
            rating=rating,
            comment=comment
        )
        
        self.feedbacks.append(record)
        self._save_feedback(record)
        
        logger.info(f"收集反馈: feedback_id={feedback_id}, rating={rating}")
        
        # 检查是否需要触发学习
        if len(self.feedbacks) % self.feedback_threshold == 0 and self.learning_enabled:
            self.trigger_online_learning()
        
        return feedback_id
    
    def _save_feedback(self, record: FeedbackRecord):
        """保存反馈到文件"""
        try:
            # 读取现有数据
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
            
            # 添加新记录
            data.append(record.to_dict())
            
            # 保存
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存反馈失败: {e}")
    
    def analyze_feedbacks(self, limit: int = 100) -> Dict[str, Any]:
        """
        分析反馈数据
        
        Args:
            limit: 分析最近的反馈数量
        
        Returns:
            分析结果
        """
        recent_feedbacks = self.feedbacks[-limit:] if self.feedbacks else []
        
        if not recent_feedbacks:
            return {
                'total_count': 0,
                'avg_rating': 0.0,
                'positive_rate': 0.0,
                'topics': {},
                'common_comments': []
            }
        
        # 计算平均分
        avg_rating = sum(f.rating for f in recent_feedbacks) / len(recent_feedbacks)
        
        # 计算好评率(4-5分为好评)
        positive_count = sum(1 for f in recent_feedbacks if f.rating >= 4)
        positive_rate = positive_count / len(recent_feedbacks)
        
        # 分析常见主题
        topics = {}
        topic_keywords = {
            '学校查询': ['学校', '中学', '高中', '附中'],
            '分数线': ['分数', '录取线', '分数线'],
            '志愿填报': ['志愿', '填报', '录取'],
            '政策咨询': ['政策', '加分', '定向']
        }
        
        for feedback in recent_feedbacks:
            for topic, keywords in topic_keywords.items():
                if any(keyword in feedback.question for keyword in keywords):
                    topics[topic] = topics.get(topic, 0) + 1
        
        # 提取常见评论
        comments = [f.comment for f in recent_feedbacks if f.comment]
        common_comments = comments[:5]  # 取前5条
        
        return {
            'total_count': len(recent_feedbacks),
            'avg_rating': round(avg_rating, 2),
            'positive_rate': round(positive_rate * 100, 2),
            'topics': topics,
            'common_comments': common_comments
        }
    
    def trigger_online_learning(self):
        """触发在线学习"""
        if not self.learning_enabled:
            logger.info("学习功能已禁用")
            return
        
        logger.info("触发在线学习...")
        
        # 获取最近的反馈数据
        feedbacks = self.feedbacks[-self.feedback_threshold:]
        
        # 分析反馈
        analysis = self.analyze_feedbacks(self.feedback_threshold)
        
        # 更新模型参数（模拟）
        improvement = self._update_model(feedbacks, analysis)
        
        # 记录更新
        update_record = {
            'timestamp': datetime.now().isoformat(),
            'feedback_count': len(feedbacks),
            'avg_rating_before': analysis['avg_rating'],
            'improvement': improvement,
            'model_confidence': self.model_confidence
        }
        
        self.model_updates.append(update_record)
        
        logger.info(f"在线学习完成: 改进={improvement}%, 模型置信度={self.model_confidence}")
    
    def _update_model(self, feedbacks: List[FeedbackRecord], analysis: Dict[str, Any]) -> float:
        """
        模拟模型更新
        
        Args:
            feedbacks: 反馈列表
            analysis: 分析结果
        
        Returns:
            改进百分比
        """
        # 基于好评率调整模型置信度
        positive_rate = analysis['positive_rate'] / 100
        adjustment = (positive_rate - 0.7) * self.learning_rate
        
        # 更新模型置信度
        self.model_confidence = min(0.99, max(0.5, self.model_confidence + adjustment))
        
        # 计算改进值
        improvement = adjustment * 100
        
        return round(improvement, 2)
    
    def evaluate_quality(self, question: str, answer: str) -> QualityMetrics:
        """
        评估问答质量
        
        Args:
            question: 用户问题
            answer: 系统回答
        
        Returns:
            质量指标
        """
        metrics = QualityMetrics()
        
        # 评估相关性
        question_keywords = ['学校', '分数', '录取', '志愿', '政策']
        answer_keywords = ['学校', '分', '录取', '志愿', '政策']
        
        question_has_keyword = any(k in question for k in question_keywords)
        answer_has_keyword = any(k in answer for k in answer_keywords)
        
        if question_has_keyword and answer_has_keyword:
            metrics.relevance = 0.85 + (len(set(question_keywords) & set(answer_keywords)) / len(question_keywords)) * 0.15
        else:
            metrics.relevance = 0.5
        
        # 评估完整性（基于回答长度）
        answer_length = len(answer)
        if answer_length > 100:
            metrics.completeness = 0.9
        elif answer_length > 50:
            metrics.completeness = 0.7
        else:
            metrics.completeness = 0.5
        
        # 评估准确性（基于模型置信度）
        metrics.accuracy = self.model_confidence
        
        # 用户满意度（默认值，实际应从反馈获取）
        metrics.user_satisfaction = 0.75
        
        return metrics
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """获取学习摘要"""
        analysis = self.analyze_feedbacks()
        recent_updates = self.model_updates[-5:] if self.model_updates else []
        
        return {
            'total_feedbacks': len(self.feedbacks),
            'total_updates': len(self.model_updates),
            'current_confidence': round(self.model_confidence, 4),
            'avg_rating': analysis['avg_rating'],
            'positive_rate': analysis['positive_rate'],
            'recent_updates': recent_updates,
            'learning_enabled': self.learning_enabled
        }
    
    def toggle_learning(self, enabled: bool):
        """开启/关闭学习功能"""
        self.learning_enabled = enabled
        logger.info(f"学习功能{'开启' if enabled else '关闭'}")
    
    def get_feedback_by_session(self, session_id: str) -> List[FeedbackRecord]:
        """获取指定会话的反馈"""
        return [f for f in self.feedbacks if f.session_id == session_id]
    
    def export_feedbacks(self, file_path: str = None) -> str:
        """
        导出反馈数据
        
        Args:
            file_path: 导出文件路径
        
        Returns:
            导出文件路径
        """
        if not file_path:
            file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 
                                   f"feedbacks_export_{datetime.now().strftime('%Y%m%d')}.json")
        
        data = [f.to_dict() for f in self.feedbacks]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"导出反馈数据: {len(data)} 条记录")
        return file_path


# 全局实例
continuous_learning_service = ContinuousLearningService()


def get_continuous_learning_service() -> ContinuousLearningService:
    """获取持续学习服务实例"""
    return continuous_learning_service


if __name__ == '__main__':
    print("=" * 70)
    print("持续学习机制服务测试")
    print("=" * 70)
    
    service = ContinuousLearningService()
    
    # 测试1: 收集反馈
    print("\n1. 测试收集反馈")
    print("-" * 50)
    feedback_ids = []
    test_feedbacks = [
        ("123", "昆一中怎么样？", "昆一中是省级重点中学...", 5, "回答很详细"),
        ("123", "中考总分多少？", "云南省中考总分700分", 4, ""),
        ("123", "志愿怎么填？", "建议按照分数梯度填报", 3, "希望更详细"),
        ("456", "昆三中录取线", "大约650分左右", 5, ""),
        ("456", "加分政策", "少数民族可加5-10分", 4, "清楚明了"),
    ]
    
    for session_id, question, answer, rating, comment in test_feedbacks:
        feedback_id = service.collect_feedback(session_id, question, answer, rating, comment)
        feedback_ids.append(feedback_id)
        print(f"收集反馈: {feedback_id[:8]}... 评分: {rating}")
    
    # 测试2: 分析反馈
    print("\n2. 测试分析反馈")
    print("-" * 50)
    analysis = service.analyze_feedbacks()
    print(f"反馈总数: {analysis['total_count']}")
    print(f"平均评分: {analysis['avg_rating']}")
    print(f"好评率: {analysis['positive_rate']}%")
    print(f"主题分布: {analysis['topics']}")
    
    # 测试3: 评估质量
    print("\n3. 测试质量评估")
    print("-" * 50)
    metrics = service.evaluate_quality("昆一中怎么样？", "昆一中是省级重点中学，一本率92%")
    print(f"相关性: {metrics.relevance:.2f}")
    print(f"完整性: {metrics.completeness:.2f}")
    print(f"准确性: {metrics.accuracy:.2f}")
    print(f"用户满意度: {metrics.user_satisfaction:.2f}")
    
    # 测试4: 学习摘要
    print("\n4. 测试学习摘要")
    print("-" * 50)
    summary = service.get_learning_summary()
    print(f"总反馈数: {summary['total_feedbacks']}")
    print(f"总更新次数: {summary['total_updates']}")
    print(f"当前模型置信度: {summary['current_confidence']}")
    print(f"学习功能: {'开启' if summary['learning_enabled'] else '关闭'}")
    
    # 测试5: 触发在线学习
    print("\n5. 测试在线学习")
    print("-" * 50)
    # 添加更多反馈触发学习
    for i in range(5):
        service.collect_feedback("789", f"测试问题{i+1}", f"测试回答{i+1}", 4)
    
    summary = service.get_learning_summary()
    print(f"在线学习后模型置信度: {summary['current_confidence']}")
    print(f"更新次数: {summary['total_updates']}")
    
    # 测试6: 导出反馈
    print("\n6. 测试导出反馈")
    print("-" * 50)
    export_path = service.export_feedbacks()
    print(f"反馈导出到: {export_path}")
    
    # 测试7: 按会话查询反馈
    print("\n7. 测试按会话查询反馈")
    print("-" * 50)
    session_feedbacks = service.get_feedback_by_session("123")
    print(f"会话123的反馈数量: {len(session_feedbacks)}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)