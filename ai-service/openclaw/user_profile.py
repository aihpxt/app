"""AI用户画像系统"""

import time
import random
from typing import Dict, Any, List, Optional

class UserProfileSystem:
    """AI用户画像系统"""
    
    def __init__(self):
        self.user_profiles = {}
        self.profile_templates = {
            "student": {
                "type": "student",
                "score_level": "medium",
                "risk_tolerance": "medium",
                "learning_style": "visual",
                "family_background": "middle",
                "interests": [],
                "strengths": [],
                "weaknesses": []
            },
            "parent": {
                "type": "parent",
                "education_level": "college",
                "concerns": ["academic", "future"],
                "expectations": "high",
                "budget": "medium",
                "involvement": "high"
            }
        }
    
    def create_profile(self, user_id: str = None, user_type: str = "student", initial_data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """创建用户画像"""
        # 支持灵活的参数传递
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
        if 'initial_data' in kwargs:
            initial_data = kwargs['initial_data']
        if 'user_type' in kwargs:
            user_type = kwargs['user_type']
        
        if not user_id:
            user_id = f"user_{int(time.time())}_{random.randint(1000, 9999)}"
        
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        
        # 基于模板创建画像
        profile = self.profile_templates.get(user_type, self.profile_templates["student"]).copy()
        
        # 填充初始数据
        if initial_data:
            profile.update(initial_data)
        
        # 生成初始分析
        profile["analysis"] = self._analyze_profile(profile)
        profile["created_at"] = time.time()
        profile["updated_at"] = time.time()
        profile["user_id"] = user_id  # 添加user_id到profile
        
        self.user_profiles[user_id] = profile
        return profile
    
    def update_profile(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户画像"""
        if user_id not in self.user_profiles:
            return self.create_profile(user_id, initial_data=data)
        
        # 更新画像数据
        profile = self.user_profiles[user_id]
        profile.update(data)
        profile["updated_at"] = time.time()
        
        # 更新分析
        profile["analysis"] = self._analyze_profile(profile)
        
        return profile
    
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户画像"""
        return self.user_profiles.get(user_id)
    
    def _analyze_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """分析用户画像"""
        analysis = {
            "personality_type": self._analyze_personality(profile),
            "recommendations": self._generate_recommendations(profile),
            "suitable_schools": self._suggest_schools(profile),
            "learning_strategy": self._suggest_learning_strategy(profile)
        }
        return analysis
    
    def _analyze_personality(self, profile: Dict[str, Any]) -> str:
        """分析个性类型"""
        if profile.get("risk_tolerance") == "high":
            if profile.get("learning_style") == "active":
                return "冒险型学习者"
            else:
                return "谨慎型决策者"
        elif profile.get("risk_tolerance") == "low":
            return "保守型学习者"
        else:
            return "平衡型学习者"
    
    def _generate_recommendations(self, profile: Dict[str, Any]) -> List[str]:
        """生成推荐"""
        recommendations = []
        
        if profile.get("score_level") == "high":
            recommendations.append("建议冲刺重点高中")
        elif profile.get("score_level") == "medium":
            recommendations.append("建议选择适合自己能力的学校")
        else:
            recommendations.append("建议关注职业教育和特色学校")
        
        if profile.get("learning_style") == "visual":
            recommendations.append("建议多使用图表和可视化学习材料")
        elif profile.get("learning_style") == "auditory":
            recommendations.append("建议多听讲座和音频资料")
        elif profile.get("learning_style") == "kinesthetic":
            recommendations.append("建议多进行实践和动手操作")
        
        return recommendations
    
    def _suggest_schools(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """推荐适合的学校"""
        schools = []
        
        if profile.get("score_level") == "high":
            schools.extend([
                {"name": "云南师范大学附属中学", "match": 0.95, "reason": "学术水平高，适合高分学生"},
                {"name": "昆明市第一中学", "match": 0.9, "reason": "综合实力强，适合全面发展"}
            ])
        elif profile.get("score_level") == "medium":
            schools.extend([
                {"name": "昆明市第八中学", "match": 0.85, "reason": "教学质量好，适合中等水平学生"},
                {"name": "昆明市第十中学", "match": 0.8, "reason": "注重创新教育，适合有特长的学生"}
            ])
        else:
            schools.extend([
                {"name": "昆明市第十二中学", "match": 0.75, "reason": "办学特色鲜明，适合基础薄弱学生"},
                {"name": "云南衡水实验中学", "match": 0.7, "reason": "管理严格，适合需要提升的学生"}
            ])
        
        return schools
    
    def _suggest_learning_strategy(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """建议学习策略"""
        strategy = {
            "study_plan": [],
            "time_management": "",
            "exam_strategy": ""
        }
        
        if profile.get("learning_style") == "visual":
            strategy["study_plan"] = [
                "使用思维导图整理知识点",
                "多做图表和笔记",
                "观看教学视频"
            ]
        elif profile.get("learning_style") == "auditory":
            strategy["study_plan"] = [
                "听录音和讲座",
                "与同学讨论学习内容",
                "大声朗读教材"
            ]
        else:
            strategy["study_plan"] = [
                "做实验和实践活动",
                "使用实物教具",
                "通过运动辅助学习"
            ]
        
        strategy["time_management"] = "建议制定详细的学习计划，合理分配时间"
        strategy["exam_strategy"] = "建议多做模拟题，熟悉考试题型"
        
        return strategy
    
    def analyze_student_performance(self, user_id: str, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析学生表现"""
        profile = self.get_profile(user_id)
        if not profile:
            profile = self.create_profile(user_id)
        
        # 更新表现数据
        profile["performance"] = performance_data
        
        # 分析成绩趋势
        scores = performance_data.get("scores", [])
        if scores:
            avg_score = sum(score for score in scores) / len(scores)
            trend = "上升" if len(scores) >= 2 and scores[-1] > scores[0] else "稳定"
            
            profile["score_level"] = "high" if avg_score >= 650 else "medium" if avg_score >= 550 else "low"
        
        # 更新画像
        return self.update_profile(user_id, profile)
    
    def get_profile_stats(self) -> Dict[str, Any]:
        """获取画像统计信息"""
        stats = {
            "total_profiles": len(self.user_profiles),
            "student_profiles": sum(1 for p in self.user_profiles.values() if p.get("type") == "student"),
            "parent_profiles": sum(1 for p in self.user_profiles.values() if p.get("type") == "parent"),
            "version": "1.0.0"
        }
        return stats

# 全局用户画像系统实例
user_profile_system = UserProfileSystem()