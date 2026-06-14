"""
用户画像系统单元测试
覆盖用户管理核心模块
"""
import unittest
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 直接导入模块以避免循环导入问题
from openclaw.user_profile import UserProfileSystem


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
        # 检查user_id是否存在且不为空
        self.assertIn("user_id", profile)
        self.assertTrue(len(profile.get("user_id", "")) > 0)
    
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
    
    def test_create_profile_duplicate_user_id(self):
        """测试创建重复用户ID的画像"""
        profile1 = self.user_profile_system.create_profile(user_id="duplicate_user")
        profile2 = self.user_profile_system.create_profile(user_id="duplicate_user")
        
        self.assertIs(profile1, profile2)  # 应该返回同一个对象
    
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
        # 高风险容忍度 + 主动学习风格
        profile1 = {"risk_tolerance": "high", "learning_style": "active"}
        self.assertEqual(self.user_profile_system._analyze_personality(profile1), "冒险型学习者")
        
        # 高风险容忍度 + 非主动学习风格
        profile2 = {"risk_tolerance": "high", "learning_style": "visual"}
        self.assertEqual(self.user_profile_system._analyze_personality(profile2), "谨慎型决策者")
        
        # 低风险容忍度
        profile3 = {"risk_tolerance": "low"}
        self.assertEqual(self.user_profile_system._analyze_personality(profile3), "保守型学习者")
        
        # 中等风险容忍度（默认）
        profile4 = {"risk_tolerance": "medium"}
        self.assertEqual(self.user_profile_system._analyze_personality(profile4), "平衡型学习者")
    
    def test_generate_recommendations(self):
        """测试生成推荐功能"""
        # 高分学生
        profile1 = {"score_level": "high", "learning_style": "visual"}
        recommendations1 = self.user_profile_system._generate_recommendations(profile1)
        self.assertIn("建议冲刺重点高中", recommendations1)
        self.assertIn("建议多使用图表和可视化学习材料", recommendations1)
        
        # 中等分数学生
        profile2 = {"score_level": "medium", "learning_style": "auditory"}
        recommendations2 = self.user_profile_system._generate_recommendations(profile2)
        self.assertIn("建议选择适合自己能力的学校", recommendations2)
        self.assertIn("建议多听讲座和音频资料", recommendations2)
        
        # 低分学生
        profile3 = {"score_level": "low", "learning_style": "kinesthetic"}
        recommendations3 = self.user_profile_system._generate_recommendations(profile3)
        self.assertIn("建议关注职业教育和特色学校", recommendations3)
        self.assertIn("建议多进行实践和动手操作", recommendations3)
    
    def test_suggest_schools(self):
        """测试推荐学校功能"""
        # 高分学生
        high_profile = {"score_level": "high"}
        high_schools = self.user_profile_system._suggest_schools(high_profile)
        self.assertEqual(len(high_schools), 2)
        self.assertEqual(high_schools[0]["name"], "云南师范大学附属中学")
        self.assertEqual(high_schools[1]["name"], "昆明市第一中学")
        
        # 中等分数学生
        medium_profile = {"score_level": "medium"}
        medium_schools = self.user_profile_system._suggest_schools(medium_profile)
        self.assertEqual(len(medium_schools), 2)
        self.assertEqual(medium_schools[0]["name"], "昆明市第八中学")
        self.assertEqual(medium_schools[1]["name"], "昆明市第十中学")
        
        # 低分学生
        low_profile = {"score_level": "low"}
        low_schools = self.user_profile_system._suggest_schools(low_profile)
        self.assertEqual(len(low_schools), 2)
        self.assertEqual(low_schools[0]["name"], "昆明市第十二中学")
    
    def test_suggest_learning_strategy(self):
        """测试学习策略建议功能"""
        # 视觉学习者
        visual_profile = {"learning_style": "visual"}
        visual_strategy = self.user_profile_system._suggest_learning_strategy(visual_profile)
        self.assertIn("使用思维导图整理知识点", visual_strategy["study_plan"])
        
        # 听觉学习者
        auditory_profile = {"learning_style": "auditory"}
        auditory_strategy = self.user_profile_system._suggest_learning_strategy(auditory_profile)
        self.assertIn("听录音和讲座", auditory_strategy["study_plan"])
        
        # 动觉学习者（默认）
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
        self.assertEqual(profile["score_level"], "high")  # 平均分650，属于高分
    
    def test_analyze_student_performance_no_profile(self):
        """测试分析不存在的学生表现（应自动创建）"""
        # 平均分523，根据代码逻辑（>=550为medium），应判定为low
        performance_data = {"scores": [500, 520, 550]}
        
        profile = self.user_profile_system.analyze_student_performance(
            "new_user_for_performance",
            performance_data
        )
        
        self.assertIsNotNone(profile)
        # 平均分(500+520+550)/3=523，根据代码判定标准，<550为low
        self.assertEqual(profile["score_level"], "low")
    
    def test_get_profile_stats(self):
        """测试获取画像统计信息"""
        # 创建一些测试画像
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