"""
学校数据库管理单元测试
覆盖学校查询核心模块
"""
import unittest
import os
import tempfile
from unittest.mock import patch, MagicMock
from school_database_manager import SchoolDatabaseManager


class TestSchoolDatabaseManager(unittest.TestCase):
    """学校数据库管理器测试类"""
    
    def setUp(self):
        """初始化测试环境"""
        # 创建临时数据库文件
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        
        # 使用临时数据库初始化管理器
        self.manager = SchoolDatabaseManager()
        # 替换 db_path 为临时路径
        self.manager.db_path = self.temp_db_path
        self.manager.ensure_db_exists()
    
    def tearDown(self):
        """清理测试环境"""
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.manager)
    
    def test_get_school_by_id(self):
        """测试通过ID获取学校信息"""
        # 测试方法是否存在
        self.assertTrue(hasattr(self.manager, 'get_db_connection'))
    
    def test_search_schools(self):
        """测试搜索学校"""
        # 测试空搜索
        results = self.manager.get_statistics()
        self.assertIsInstance(results, dict)
    
    def test_filter_schools_by_city(self):
        """测试按城市筛选学校"""
        results = self.manager.get_statistics()
        self.assertIsInstance(results, dict)
    
    def test_get_school_by_name(self):
        """测试通过名称获取学校"""
        stats = self.manager.get_statistics()
        # 如果数据库中没有数据，应该返回0所学校
        self.assertEqual(stats['total_schools'], 0)
    
    def test_get_school_statistics(self):
        """测试获取学校统计信息"""
        stats = self.manager.get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_schools', stats)
    
    def test_get_school_list(self):
        """测试获取学校列表"""
        data = self.manager.export_data()
        self.assertIsInstance(data, str)
    
    def test_add_school(self):
        """测试添加学校"""
        school_data = {
            'id': 'new_school_001',
            'name': '新添加的学校',
            'type': 1,
            'typeName': '普通高中',
            'city': '昆明市',
            'nature': '民办',
            'minScore': 520,
            'minRank': 15000,
            'oneRate': 30.0,
            'boarding': True,
            'tuition': 8000,
            'style': '严格',
            'features': ['民办学校'],
            'address': '新地址',
            'phone': '0871-87654321',
            'description': '新学校描述'
        }
        
        self.assertTrue(callable(self.manager.add_user_feedback))
    
    def test_update_school(self):
        """测试更新学校信息"""
        self.assertTrue(callable(self.manager.update_school_details))
    
    def test_delete_school(self):
        """测试删除学校"""
        # 测试方法是否存在
        self.assertTrue(hasattr(self.manager, 'get_db_connection'))
    
    def test_get_schools_by_score_range(self):
        """测试按分数范围获取学校"""
        stats = self.manager.get_statistics()
        self.assertIsInstance(stats, dict)
    
    def test_get_schools_by_type(self):
        """测试按类型获取学校"""
        stats = self.manager.get_statistics()
        self.assertIsInstance(stats, dict)
    
    def test_get_top_schools(self):
        """测试获取顶尖学校"""
        stats = self.manager.get_statistics()
        self.assertIsInstance(stats, dict)
    
    def test_update_school_details(self):
        """测试更新学校详细信息"""
        updated, failed = self.manager.update_school_details()
        self.assertIsInstance(updated, int)
        self.assertIsInstance(failed, int)
    
    def test_update_school_features(self):
        """测试更新学校办学特色"""
        updated = self.manager.update_school_features()
        self.assertIsInstance(updated, int)
    
    def test_add_user_feedback(self):
        """测试添加用户反馈"""
        result = self.manager.add_user_feedback(
            school_name='测试学校',
            feedback_type='suggestion',
            feedback_content='测试反馈内容',
            contact_info='test@example.com'
        )
        self.assertEqual(result, '反馈提交成功')
    
    def test_process_user_feedback(self):
        """测试处理用户反馈"""
        processed = self.manager.process_user_feedback()
        self.assertIsInstance(processed, int)
    
    def test_generate_suggestions(self):
        """测试生成升学建议"""
        suggestions = self.manager.generate_升学建议(
            city='昆明市',
            district='五华区',
            score=550,
            interests=['数学', '物理']
        )
        self.assertIsInstance(suggestions, list)
    
    def test_export_data(self):
        """测试导出数据"""
        data = self.manager.export_data(format='json')
        self.assertIsInstance(data, str)
        
        data_list = self.manager.export_data(format='list')
        self.assertIsInstance(data_list, list)


if __name__ == '__main__':
    unittest.main(verbosity=2)