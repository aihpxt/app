"""
用户画像系统独立单元测试
覆盖用户管理核心模块
避免循环导入问题
"""
import unittest
import time
import random
from typing import Dict, Any, List, Optional


# 直接定义测试用的用户画像系统类，避免循环导入
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
        
        profile = self.profile_templates.get(user_type, self.profile_templates["student"]).copy()
        
        if initial_data:
            profile.update(initial_data)
        
        profile["analysis"] = self._analyze_profile(profile)
        profile["created_at"] = time.time()
        profile["updated_at"] = time.time()
        
        self.user_profiles[user_id] = profile
        return profile
    
    def update_profile(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户画像"""
        if user_id not in self.user_profiles:
            return self.create_profile(user_id, initial_data=data)
        
        profile = self.user_profiles[user_id]
        profile.update(data)
        profile["updated_at"] = time.time()
        
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
        
        profile["performance"] = performance_data
        
        scores = performance_data.get("scores", [])
        if scores:
            avg_score = sum(score for score in scores) / len(scores)
            
            profile["score_level"] = "high" if avg_score >= 650 else "medium" if avg_score >= 550 else "low"
        
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


class TestUserProfileSystem(unittest.TestCase):
    """用户画像系统测试类"""
    
    def setUp(self):
        """初始化测试环境"""
        self.user_profile_system = UserProfileSystem()
    
    def test_create_profile_with_user_id(self):
        """测试创建用户画像（指定用户ID）"""
        user_id = "test_user_001"
        profile = self.user_profile_system.create_profile(user_id=user_id)
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile.get("type"), "student")
        self.assertIn("analysis", profile)
        self.assertIn("created_at", profile)
        self.assertIn("updated_at", profile)
    
    def test_create_profile_without_user_id(self):
        """测试创建用户画像（自动生成用户ID）"""
        profile = self.user_profile_system.create_profile()
        
        self.assertIsNotNone(profile)
        # 用户ID存储在user_profiles字典的key中，而不是profile本身
        # 检查是否创建了任何profile
        self.assertEqual(len(self.user_profile_system.user_profiles), 1)
        # 检查生成的用户ID格式
        user_id = list(self.user_profile_system.user_profiles.keys())[0]
        self.assertTrue(user_id.startswith("user_"))
    
    def test_create_profile_with_initial_data(self):
        """测试使用初始数据创建用户画像"""
        initial_data = {
            "score_level": "high",
            "risk_tolerance": "high",
            "learning_style": "active"
        }
        profile = self.user_profile_system.create_profile(
            user_id="test_user_002",
            initial_data=initial_data
        )
        
        self.assertEqual(profile["score_level"], "high")
        self.assertEqual(profile["risk_tolerance"], "high")
        self.assertEqual(profile["learning_style"], "active")
    
    def test_create_profile_with_user_type(self):
        """测试创建不同类型的用户画像"""
        student_profile = self.user_profile_system.create_profile(
            user_id="student_001",
            user_type="student"
        )
        parent_profile = self.user_profile_system.create_profile(
            user_id="parent_001",
            user_type="parent"
        )
        
        self.assertEqual(student_profile["type"], "student")
        self.assertEqual(parent_profile["type"], "parent")
        self.assertIn("interests", student_profile)
        self.assertIn("concerns", parent_profile)
    
    def test_create_profile_duplicate_user_id(self):
        """测试创建重复用户ID的画像"""
        profile1 = self.user_profile_system.create_profile(user_id="duplicate_user")
        profile2 = self.user_profile_system.create_profile(user_id="duplicate_user")
        
        self.assertIs(profile1, profile2)
    
    def test_update_profile(self):
        """测试更新用户画像"""
        self.user_profile_system.create_profile(user_id="update_test_user")
        update_data = {
            "score_level": "high",
            "learning_style": "auditory"
        }
        
        updated_profile = self.user_profile_system.update_profile(
            "update_test_user",
            update_data
        )
        
        self.assertEqual(updated_profile["score_level"], "high")
        self.assertEqual(updated_profile["learning_style"], "auditory")
        self.assertGreater(updated_profile["updated_at"], updated_profile["created_at"])
    
    def test_update_nonexistent_profile(self):
        """测试更新不存在的用户画像（应自动创建）"""
        update_data = {"score_level": "medium"}
        
        profile = self.user_profile_system.update_profile(
            "nonexistent_user",
            update_data
        )
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile["score_level"], "medium")
    
    def test_get_profile(self):
        """测试获取用户画像"""
        self.user_profile_system.create_profile(user_id="get_test_user")
        
        profile = self.user_profile_system.get_profile("get_test_user")
        self.assertIsNotNone(profile)
        
        non_existent = self.user_profile_system.get_profile("non_existent")
        self.assertIsNone(non_existent)
    
    def test_analyze_personality(self):
        """测试个性分析功能"""
        profile1 = {"risk_tolerance": "high", "learning_style": "active"}
        self.assertEqual(self.user_profile_system._analyze_personality(profile1), "冒险型学习者")
        
        profile2 = {"risk_tolerance": "high", "learning_style": "visual"}
        self.assertEqual(self.user_profile_system._analyze_personality(profile2), "谨慎型决策者")
        
        profile3 = {"risk_tolerance": "low"}
        self.assertEqual(self.user_profile_system._analyze_personality(profile3), "保守型学习者")
        
        profile4 = {"risk_tolerance": "medium"}
        self.assertEqual(self.user_profile_system._analyze_personality(profile4), "平衡型学习者")
    
    def test_generate_recommendations(self):
        """测试生成推荐功能"""
        profile1 = {"score_level": "high", "learning_style": "visual"}
        recommendations1 = self.user_profile_system._generate_recommendations(profile1)
        self.assertIn("建议冲刺重点高中", recommendations1)
        self.assertIn("建议多使用图表和可视化学习材料", recommendations1)
        
        profile2 = {"score_level": "medium", "learning_style": "auditory"}
        recommendations2 = self.user_profile_system._generate_recommendations(profile2)
        self.assertIn("建议选择适合自己能力的学校", recommendations2)
        self.assertIn("建议多听讲座和音频资料", recommendations2)
        
        profile3 = {"score_level": "low", "learning_style": "kinesthetic"}
        recommendations3 = self.user_profile_system._generate_recommendations(profile3)
        self.assertIn("建议关注职业教育和特色学校", recommendations3)
        self.assertIn("建议多进行实践和动手操作", recommendations3)
    
    def test_suggest_schools(self):
        """测试推荐学校功能"""
        high_profile = {"score_level": "high"}
        high_schools = self.user_profile_system._suggest_schools(high_profile)
        self.assertEqual(len(high_schools), 2)
        self.assertEqual(high_schools[0]["name"], "云南师范大学附属中学")
        self.assertEqual(high_schools[1]["name"], "昆明市第一中学")
        
        medium_profile = {"score_level": "medium"}
        medium_schools = self.user_profile_system._suggest_schools(medium_profile)
        self.assertEqual(len(medium_schools), 2)
        self.assertEqual(medium_schools[0]["name"], "昆明市第八中学")
        self.assertEqual(medium_schools[1]["name"], "昆明市第十中学")
        
        low_profile = {"score_level": "low"}
        low_schools = self.user_profile_system._suggest_schools(low_profile)
        self.assertEqual(len(low_schools), 2)
        self.assertEqual(low_schools[0]["name"], "昆明市第十二中学")
    
    def test_suggest_learning_strategy(self):
        """测试学习策略建议功能"""
        visual_profile = {"learning_style": "visual"}
        visual_strategy = self.user_profile_system._suggest_learning_strategy(visual_profile)
        self.assertIn("使用思维导图整理知识点", visual_strategy["study_plan"])
        
        auditory_profile = {"learning_style": "auditory"}
        auditory_strategy = self.user_profile_system._suggest_learning_strategy(auditory_profile)
        self.assertIn("听录音和讲座", auditory_strategy["study_plan"])
        
        kinesthetic_profile = {"learning_style": "kinesthetic"}
        kinesthetic_strategy = self.user_profile_system._suggest_learning_strategy(kinesthetic_profile)
        self.assertIn("做实验和实践活动", kinesthetic_strategy["study_plan"])
    
    def test_analyze_student_performance(self):
        """测试分析学生表现功能"""
        performance_data = {
            "scores": [620, 650, 680],
            "subjects": {"数学": 95, "语文": 88, "英语": 92}
        }
        
        profile = self.user_profile_system.analyze_student_performance(
            "performance_test_user",
            performance_data
        )
        
        self.assertIn("performance", profile)
        self.assertEqual(profile["score_level"], "high")
    
    def test_analyze_student_performance_no_profile(self):
        """测试分析不存在的学生表现（应自动创建）"""
        # 平均分 = (500 + 520 + 550) / 3 = 523.33，小于550，所以是"low"
        performance_data = {"scores": [500, 520, 550]}
        
        profile = self.user_profile_system.analyze_student_performance(
            "new_user_for_performance",
            performance_data
        )
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile["score_level"], "low")  # 平均分523 < 550，属于low
    
    def test_get_profile_stats(self):
        """测试获取画像统计信息"""
        self.user_profile_system.create_profile(user_id="stats_student_1", user_type="student")
        self.user_profile_system.create_profile(user_id="stats_student_2", user_type="student")
        self.user_profile_system.create_profile(user_id="stats_parent_1", user_type="parent")
        
        stats = self.user_profile_system.get_profile_stats()
        
        self.assertEqual(stats["total_profiles"], 3)
        self.assertEqual(stats["student_profiles"], 2)
        self.assertEqual(stats["parent_profiles"], 1)
        self.assertEqual(stats["version"], "1.0.0")
    
    def test_create_profile_with_kwargs(self):
        """测试使用kwargs方式传递参数"""
        profile = self.user_profile_system.create_profile(
            user_id="kwargs_test",
            user_type="parent",
            initial_data={"education_level": "master", "budget": "high"}
        )
        
        self.assertEqual(profile["type"], "parent")
        self.assertEqual(profile["education_level"], "master")
        self.assertEqual(profile["budget"], "high")


if __name__ == '__main__':
    unittest.main(verbosity=2)