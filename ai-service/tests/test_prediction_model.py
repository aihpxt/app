"""
录取预测模型单元测试
覆盖录取预测核心模块
"""
import unittest
from prediction_model import PredictionModel


class TestPredictionModel(unittest.TestCase):
    """预测模型测试类"""
    
    def setUp(self):
        """初始化测试环境"""
        self.model = PredictionModel()
    
    def test_initialization(self):
        """测试模型初始化"""
        self.assertIsNotNone(self.model)
        self.assertIsNotNone(self.model._model)
        self.assertEqual(self.model._model["status"], "loaded")
    
    def test_get_model(self):
        """测试获取模型"""
        model = self.model.get_model()
        
        self.assertIsNotNone(model)
        self.assertEqual(model["status"], "loaded")
    
    def test_predict(self):
        """测试预测功能"""
        test_data = {
            "score": 650,
            "rank": 5000,
            "school_preferences": ["云南师范大学附属中学", "昆明市第一中学"],
            "district": "昆明市",
            "subject_scores": {
                "语文": 110,
                "数学": 120,
                "英语": 115,
                "物理": 95,
                "化学": 90,
                "道法": 80,
                "历史": 85
            }
        }
        
        result = self.model.predict(test_data)
        
        self.assertIsNotNone(result)
        self.assertIn("prediction", result)
    
    def test_predict_empty_data(self):
        """测试使用空数据预测"""
        result = self.model.predict({})
        
        self.assertIsNotNone(result)
        self.assertIn("prediction", result)
    
    def test_predict_with_incomplete_data(self):
        """测试使用不完整数据预测"""
        incomplete_data = {
            "score": 580,
            "school_preferences": ["昆明市第八中学"]
        }
        
        result = self.model.predict(incomplete_data)
        
        self.assertIsNotNone(result)
        self.assertIn("prediction", result)
    
    def test_predict_with_high_score(self):
        """测试高分数据预测"""
        high_score_data = {
            "score": 680,
            "rank": 1500,
            "school_preferences": ["云南师范大学附属中学", "昆一中"]
        }
        
        result = self.model.predict(high_score_data)
        
        self.assertIsNotNone(result)
        self.assertIn("prediction", result)
    
    def test_predict_with_medium_score(self):
        """测试中等分数数据预测"""
        medium_score_data = {
            "score": 580,
            "rank": 12000,
            "school_preferences": ["昆明市第八中学", "昆明市第十中学"]
        }
        
        result = self.model.predict(medium_score_data)
        
        self.assertIsNotNone(result)
        self.assertIn("prediction", result)
    
    def test_predict_with_low_score(self):
        """测试低分数据预测"""
        low_score_data = {
            "score": 480,
            "rank": 25000,
            "school_preferences": ["昆明市第十二中学", "云南衡水实验中学"]
        }
        
        result = self.model.predict(low_score_data)
        
        self.assertIsNotNone(result)
        self.assertIn("prediction", result)
    
    def test_predict_with_different_districts(self):
        """测试不同地区数据预测"""
        districts = ["昆明市", "曲靖市", "玉溪市", "文山州"]
        
        for district in districts:
            data = {
                "score": 550,
                "rank": 15000,
                "district": district,
                "school_preferences": ["当地重点中学"]
            }
            
            result = self.model.predict(data)
            
            self.assertIsNotNone(result)
            self.assertIn("prediction", result)
    
    def test_predict_with_subject_scores(self):
        """测试包含科目分数的数据预测"""
        data_with_subjects = {
            "score": 620,
            "rank": 8000,
            "subject_scores": {
                "语文": 105,
                "数学": 115,
                "英语": 110,
                "物理": 90,
                "化学": 85,
                "道法": 75,
                "历史": 80
            }
        }
        
        result = self.model.predict(data_with_subjects)
        
        self.assertIsNotNone(result)
        self.assertIn("prediction", result)


if __name__ == '__main__':
    unittest.main(verbosity=2)