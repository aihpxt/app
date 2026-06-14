#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自适应学习系统
根据用户反馈持续优化对话效果
"""

import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
from threading import Lock
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FeedbackRecord:
    """反馈记录"""
    feedback_id: str
    session_id: str
    user_input: str
    response: str
    rating: int  # 1-5星
    comment: str = ""
    timestamp: float = field(default_factory=lambda: time.time())
    context: Dict = field(default_factory=dict)


@dataclass
class ResponsePattern:
    """响应模式"""
    pattern_id: str
    trigger_keywords: List[str]
    response_template: str
    usage_count: int = 0
    success_count: int = 0
    avg_rating: float = 0.0
    last_updated: float = field(default_factory=lambda: time.time())


class AdaptiveLearningSystem:
    """自适应学习系统"""
    
    def __init__(self):
        self.feedback_records: Dict[str, FeedbackRecord] = {}
        self.response_patterns: Dict[str, ResponsePattern] = {}
        self.session_feedback: Dict[str, List[str]] = defaultdict(list)
        self.lock = Lock()
        self._load_patterns()
    
    def _load_patterns(self):
        """加载初始响应模式"""
        # 初始化一些基础模式
        initial_patterns = [
            {
                "pattern_id": "school_recommendation",
                "trigger_keywords": ["推荐", "学校", "高中", "分数", "能上"],
                "response_template": "根据您的分数和位置，为您推荐以下学校：\n{schools}"
            },
            {
                "pattern_id": "fee_inquiry",
                "trigger_keywords": ["学费", "费用", "多少钱", "收费"],
                "response_template": "{school}的学费标准如下：\n{fee_info}"
            },
            {
                "pattern_id": "policy_question",
                "trigger_keywords": ["政策", "中考", "志愿", "填报"],
                "response_template": "关于{topic}的政策如下：\n{policy_info}"
            },
            {
                "pattern_id": "encouragement",
                "trigger_keywords": ["焦虑", "担心", "压力", "怎么办"],
                "response_template": "我理解您的心情，{encouragement}"
            }
        ]
        
        for pattern in initial_patterns:
            self.response_patterns[pattern["pattern_id"]] = ResponsePattern(
                pattern_id=pattern["pattern_id"],
                trigger_keywords=pattern["trigger_keywords"],
                response_template=pattern["response_template"]
            )
    
    def record_feedback(self, session_id: str, user_input: str, 
                        response: str, rating: int, comment: str = "",
                        context: Dict = None) -> str:
        """记录用户反馈"""
        feedback_id = self._generate_id(f"{session_id}_{user_input[:20]}")
        
        record = FeedbackRecord(
            feedback_id=feedback_id,
            session_id=session_id,
            user_input=user_input,
            response=response,
            rating=rating,
            comment=comment,
            context=context or {}
        )
        
        with self.lock:
            self.feedback_records[feedback_id] = record
            self.session_feedback[session_id].append(feedback_id)
        
        logger.info(f"反馈已记录: {feedback_id}, 评分: {rating}星")
        
        # 触发学习更新
        self._update_patterns(record)
        
        return feedback_id
    
    def _generate_id(self, text: str) -> str:
        """生成唯一ID"""
        return hashlib.md5(f"{text}_{time.time()}".encode()).hexdigest()[:16]
    
    def _update_patterns(self, feedback: FeedbackRecord):
        """根据反馈更新响应模式"""
        # 找到匹配的模式
        matched_pattern = self._find_matching_pattern(feedback.user_input)
        
        if matched_pattern:
            with self.lock:
                pattern = self.response_patterns[matched_pattern]
                pattern.usage_count += 1
                
                # 更新成功率和评分
                if feedback.rating >= 4:
                    pattern.success_count += 1
                
                # 更新平均评分
                pattern.avg_rating = (pattern.avg_rating * (pattern.usage_count - 1) + feedback.rating) / pattern.usage_count
                pattern.last_updated = time.time()
            
            logger.info(f"模式已更新: {matched_pattern}, 成功率: {pattern.success_count/pattern.usage_count:.2%}")
            
            # 如果评分较低，尝试优化响应
            if feedback.rating <= 2:
                self._optimize_pattern(matched_pattern, feedback)
    
    def _find_matching_pattern(self, user_input: str) -> Optional[str]:
        """查找匹配的响应模式"""
        user_lower = user_input.lower()
        
        for pattern_id, pattern in self.response_patterns.items():
            for keyword in pattern.trigger_keywords:
                if keyword in user_lower:
                    return pattern_id
        
        return None
    
    def _optimize_pattern(self, pattern_id: str, feedback: FeedbackRecord):
        """优化响应模式"""
        logger.info(f"尝试优化模式: {pattern_id}")
        
        # 分析反馈，生成改进建议
        improvement = self._analyze_feedback_for_improvement(feedback)
        
        if improvement:
            with self.lock:
                pattern = self.response_patterns.get(pattern_id)
                if pattern:
                    # 根据反馈调整模板
                    if feedback.comment:
                        # 可以在这里调用LLM来优化响应模板
                        logger.info(f"模式优化建议: {improvement}")
    
    def _analyze_feedback_for_improvement(self, feedback: FeedbackRecord) -> Optional[str]:
        """分析反馈并生成改进建议"""
        suggestions = []
        
        if feedback.rating <= 2:
            if feedback.comment:
                suggestions.append(f"用户反馈: {feedback.comment}")
            
            # 分析问题类型
            if "不够详细" in feedback.comment or "太简单" in feedback.comment:
                suggestions.append("建议增加更多详细信息")
            elif "不准确" in feedback.comment or "错误" in feedback.comment:
                suggestions.append("建议验证信息准确性")
            elif "不相关" in feedback.comment:
                suggestions.append("建议改进意图识别")
        
        return "; ".join(suggestions) if suggestions else None
    
    def get_pattern_performance(self, pattern_id: str = None) -> Dict:
        """获取模式性能数据"""
        if pattern_id:
            pattern = self.response_patterns.get(pattern_id)
            if pattern:
                return {
                    "pattern_id": pattern_id,
                    "usage_count": pattern.usage_count,
                    "success_rate": pattern.success_count / pattern.usage_count if pattern.usage_count > 0 else 0,
                    "avg_rating": pattern.avg_rating,
                    "last_updated": datetime.fromtimestamp(pattern.last_updated).isoformat()
                }
            return {}
        
        # 返回所有模式的性能
        return {
            pattern_id: self.get_pattern_performance(pattern_id)
            for pattern_id in self.response_patterns
        }
    
    def get_session_feedback(self, session_id: str) -> List[Dict]:
        """获取会话的所有反馈"""
        feedback_list = []
        with self.lock:
            for feedback_id in self.session_feedback.get(session_id, []):
                record = self.feedback_records.get(feedback_id)
                if record:
                    feedback_list.append({
                        "feedback_id": record.feedback_id,
                        "user_input": record.user_input,
                        "response": record.response,
                        "rating": record.rating,
                        "comment": record.comment,
                        "timestamp": datetime.fromtimestamp(record.timestamp).isoformat()
                    })
        
        return feedback_list
    
    def get_overall_performance(self) -> Dict:
        """获取整体性能统计"""
        total_feedback = len(self.feedback_records)
        avg_rating = sum(r.rating for r in self.feedback_records.values()) / total_feedback if total_feedback > 0 else 0
        
        # 按评分分布统计
        rating_dist = defaultdict(int)
        for record in self.feedback_records.values():
            rating_dist[record.rating] += 1
        
        return {
            "total_feedback": total_feedback,
            "avg_rating": round(avg_rating, 2),
            "rating_distribution": dict(rating_dist),
            "patterns_count": len(self.response_patterns),
            "updated_patterns": sum(1 for p in self.response_patterns.values() if p.usage_count > 0)
        }
    
    def suggest_response_improvement(self, user_input: str, current_response: str) -> Dict:
        """建议响应改进"""
        # 查找类似的成功响应
        similar_feedback = self._find_similar_feedback(user_input)
        
        if similar_feedback:
            # 分析成功案例
            successful_responses = [
                fb for fb in similar_feedback 
                if fb.rating >= 4
            ]
            
            if successful_responses:
                # 返回改进建议
                return {
                    "suggestion": "参考成功案例改进响应",
                    "similar_count": len(successful_responses),
                    "avg_successful_rating": sum(f.rating for f in successful_responses) / len(successful_responses)
                }
        
        return {"suggestion": "暂无改进建议"}
    
    def _find_similar_feedback(self, user_input: str, threshold: float = 0.5) -> List[FeedbackRecord]:
        """查找相似的反馈记录"""
        similar = []
        user_words = set(user_input.lower().split())
        
        for record in self.feedback_records.values():
            record_words = set(record.user_input.lower().split())
            intersection = user_words & record_words
            
            if len(intersection) > 0:
                similarity = len(intersection) / max(len(user_words), len(record_words))
                if similarity >= threshold:
                    similar.append(record)
        
        return sorted(similar, key=lambda x: x.rating, reverse=True)[:5]
    
    def export_feedback_data(self) -> List[Dict]:
        """导出反馈数据用于分析"""
        return [
            {
                "feedback_id": record.feedback_id,
                "session_id": record.session_id,
                "user_input": record.user_input,
                "response": record.response,
                "rating": record.rating,
                "comment": record.comment,
                "timestamp": datetime.fromtimestamp(record.timestamp).isoformat(),
                "context": record.context
            }
            for record in self.feedback_records.values()
        ]
    
    def analyze_recent_feedback(self, hours: int = 24):
        """分析最近的反馈数据"""
        cutoff_time = time.time() - (hours * 3600)
        recent_feedback = [
            record for record in self.feedback_records.values()
            if record.timestamp >= cutoff_time
        ]
        
        if recent_feedback:
            avg_rating = sum(r.rating for r in recent_feedback) / len(recent_feedback)
            low_rating_count = sum(1 for r in recent_feedback if r.rating <= 2)
            
            logger.info(f"最近{hours}小时反馈分析: 总数={len(recent_feedback)}, 平均评分={avg_rating:.2f}, 低分反馈={low_rating_count}")
            
            return {
                "total_recent": len(recent_feedback),
                "avg_rating": round(avg_rating, 2),
                "low_rating_count": low_rating_count
            }
        return {"total_recent": 0, "avg_rating": 0.0, "low_rating_count": 0}
    
    def record_observation(self, observation: Dict):
        """记录观察数据（用于无评分反馈）"""
        session_id = observation.get("session_id")
        user_input = observation.get("user_input", "")
        response = observation.get("response", "")
        
        if session_id:
            # 创建一个虚拟的反馈记录（评分设为0表示无评分）
            feedback_id = self._generate_id(f"obs_{session_id}")
            record = FeedbackRecord(
                feedback_id=feedback_id,
                session_id=session_id,
                user_input=user_input,
                response=response,
                rating=0,  # 0表示无评分
                context=observation.get("context", {})
            )
            
            with self.lock:
                self.feedback_records[feedback_id] = record
                self.session_feedback[session_id].append(feedback_id)
            
            logger.debug(f"观察数据已记录: {feedback_id}")


# 全局实例
learning_system = AdaptiveLearningSystem()


# 示例用法
def example_usage():
    """示例用法"""
    # 记录反馈
    feedback_id = learning_system.record_feedback(
        session_id="test_session",
        user_input="680分推荐学校",
        response="推荐师大附中、昆一中",
        rating=4,
        comment="很好，很有帮助"
    )
    
    # 获取性能数据
    performance = learning_system.get_overall_performance()
    print(f"整体性能: {json.dumps(performance, ensure_ascii=False, indent=2)}")
    
    # 获取模式性能
    pattern_perf = learning_system.get_pattern_performance("school_recommendation")
    print(f"模式性能: {json.dumps(pattern_perf, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    example_usage()