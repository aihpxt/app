"""AI规则引擎"""

from typing import Dict, Any, List, Optional

class RuleEngine:
    """AI规则引擎"""
    
    def __init__(self):
        self.rules = {
            "batch_rules": self._load_batch_rules(),
            "area_rules": self._load_area_rules(),
            "quota_rules": self._load_quota_rules(),
            "admission_rules": self._load_admission_rules()
        }
    
    def _load_batch_rules(self) -> Dict[str, Any]:
        """加载批次规则"""
        return {
            "第一批": {
                "schools": ["云南师范大学附属中学", "昆明市第一中学", "昆明市第三中学"],
                "score_min": 650,
                "rank_max": 3000
            },
            "第二批": {
                "schools": ["昆明市第八中学", "昆明市第十中学", "云南大学附属中学"],
                "score_min": 620,
                "rank_max": 6000
            },
            "第三批": {
                "schools": ["昆明市第十二中学", "昆明市第十四中学"],
                "score_min": 580,
                "rank_max": 9000
            },
            "第四批": {
                "schools": ["北大附中云南实验学校", "云南衡水实验中学"],
                "score_min": 550,
                "rank_max": 12000
            }
        }
    
    def _load_area_rules(self) -> Dict[str, Any]:
        """加载区域规则"""
        return {
            "五华区": {
                "schools": ["云南师范大学附属中学", "昆明市第一中学"],
                "quota": 2000
            },
            "盘龙区": {
                "schools": ["昆明市第十中学", "昆明市第十四中学"],
                "quota": 1800
            },
            "官渡区": {
                "schools": ["昆明市第三中学", "昆明市第十二中学"],
                "quota": 1900
            },
            "西山区": {
                "schools": ["昆明市第八中学", "云南大学附属中学"],
                "quota": 1700
            }
        }
    
    def _load_quota_rules(self) -> Dict[str, Any]:
        """加载名额规则"""
        return {
            "指标到校": {
                "ratio": 0.5,
                "eligibility": ["初中在籍在读", "连续就读满3年"]
            },
            "定向生": {
                "ratio": 0.2,
                "eligibility": ["农村户籍", "薄弱学校"]
            },
            "郊县班": {
                "ratio": 0.1,
                "eligibility": ["郊县户籍", "初中在郊县就读"]
            }
        }
    
    def _load_admission_rules(self) -> Dict[str, Any]:
        """加载录取规则"""
        return {
            "score_priority": "分数优先",
            "volunteer_follow": "遵循志愿",
            "tie_breaker": "综合素质评价",
            "process": [
                "资格审查",
                "分数排序",
                "志愿检索",
                "录取确认",
                "公示录取结果"
            ]
        }
    
    def check_batch_eligibility(self, score: float, rank: int, prefecture: str = None) -> List[str]:
        """检查批次 eligibility"""
        eligible_batches = []
        for batch, rules in self.rules["batch_rules"].items():
            if score >= rules["score_min"] and rank <= rules["rank_max"]:
                eligible_batches.append(batch)
        return eligible_batches
    
    def check_area_eligibility(self, district: str) -> Dict[str, Any]:
        """检查区域 eligibility"""
        if district in self.rules["area_rules"]:
            return {
                "eligible": True,
                "schools": self.rules["area_rules"][district]["schools"],
                "quota": self.rules["area_rules"][district]["quota"]
            }
        return {
            "eligible": False,
            "message": "区域不在招生范围内"
        }
    
    def check_quota_eligibility(self, quota_type: str, student_info: Dict[str, Any]) -> Dict[str, Any]:
        """检查名额 eligibility"""
        if quota_type not in self.rules["quota_rules"]:
            return {
                "eligible": False,
                "message": "名额类型不存在"
            }
        
        rules = self.rules["quota_rules"][quota_type]
        eligibility = rules["eligibility"]
        
        # 检查资格
        eligible = True
        reasons = []
        
        for req in eligibility:
            if req == "初中在籍在读" and not student_info.get("in_school", True):
                eligible = False
                reasons.append("需初中在籍在读")
            elif req == "连续就读满3年" and student_info.get("study_years", 3) < 3:
                eligible = False
                reasons.append("需连续就读满3年")
            elif req == "农村户籍" and student_info.get("rural_household", False):
                eligible = True
            elif req == "薄弱学校" and student_info.get("weak_school", False):
                eligible = True
            elif req == "郊县户籍" and student_info.get("county_household", False):
                eligible = True
            elif req == "初中在郊县就读" and student_info.get("county_school", False):
                eligible = True
        
        return {
            "eligible": eligible,
            "reasons": reasons,
            "quota_ratio": rules["ratio"]
        }
    
    def generate_volunteer_strategy(self, student_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成志愿策略"""
        score = student_info.get("score", 0)
        rank = student_info.get("rank", 0)
        district = student_info.get("district", "")
        
        # 检查批次 eligibility
        eligible_batches = self.check_batch_eligibility(score, rank)
        
        # 检查区域 eligibility
        area_info = self.check_area_eligibility(district)
        
        # 生成志愿策略
        strategy = {
            "eligible_batches": eligible_batches,
            "area_info": area_info,
            "recommendations": [],
            "risk_level": "低"
        }
        
        # 生成推荐志愿
        if eligible_batches:
            for batch in eligible_batches[:2]:  # 只取前两个批次
                schools = self.rules["batch_rules"][batch]["schools"]
                for school in schools[:2]:  # 每个批次推荐2所学校
                    strategy["recommendations"].append({
                        "school": school,
                        "batch": batch,
                        "probability": "高" if batch == eligible_batches[0] else "中"
                    })
        
        # 评估风险
        if len(eligible_batches) < 2:
            strategy["risk_level"] = "高"
        elif len(eligible_batches) == 2:
            strategy["risk_level"] = "中"
        
        return strategy
    
    def validate_volunteer_table(self, volunteer_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证志愿表"""
        # 提取志愿表和学生信息
        volunteer_table = volunteer_data.get('volunteer_table', [])
        student_info = volunteer_data.get('student_info', {})
        
        score = student_info.get("score", 0)
        rank = student_info.get("rank", 0)
        
        issues = []
        warnings = []
        
        # 检查志愿数量
        if len(volunteer_table) < 3:
            warnings.append("志愿数量不足，建议至少填报3个志愿")
        
        # 检查志愿梯度
        batch_order = list(self.rules["batch_rules"].keys())
        for i in range(len(volunteer_table) - 1):
            current_batch = volunteer_table[i].get("batch", "")
            next_batch = volunteer_table[i + 1].get("batch", "")
            
            if current_batch and next_batch:
                current_index = batch_order.index(current_batch) if current_batch in batch_order else 999
                next_index = batch_order.index(next_batch) if next_batch in batch_order else 999
                
                if current_index > next_index:
                    issues.append("志愿批次顺序错误，应按批次优先级从高到低排列")
        
        # 检查分数匹配
        for volunteer in volunteer_table:
            school = volunteer.get("school", "")
            batch = volunteer.get("batch", "")
            
            if batch in self.rules["batch_rules"]:
                min_score = self.rules["batch_rules"][batch]["score_min"]
                if score < min_score - 20:  # 允许20分的浮动
                    warnings.append(f"{school}分数要求较高，录取风险较大")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "recommendations": [
                "建议按照'冲稳保'策略填报志愿",
                "确保志愿批次顺序正确",
                "合理安排志愿梯度"
            ]
        }
    
    def get_rule_info(self) -> Dict[str, Any]:
        """获取规则信息"""
        return {
            "batch_count": len(self.rules["batch_rules"]),
            "area_count": len(self.rules["area_rules"]),
            "quota_types": list(self.rules["quota_rules"].keys()),
            "version": "1.0.0"
        }

# 全局规则引擎实例
rule_engine = RuleEngine()
