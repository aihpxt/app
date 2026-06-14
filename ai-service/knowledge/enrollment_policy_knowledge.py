#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招生政策知识库
包含云南省各地州市详细的中考招生政策
"""

from typing import Dict, List, Optional
from datetime import datetime


class EnrollmentPolicyKnowledge:
    """招生政策知识库"""
    
    def __init__(self):
        self.policy_database = self._init_policy_database()
        self.school_database = self._init_school_database()
        self.score_lines = self._init_score_lines()
        self.special_student_policies = self._init_special_student_policies()
    
    def _init_special_student_policies(self) -> Dict:
        """初始化特长生和专项招生政策数据库"""
        return {
            '特长生': {
                'description': '面向有体育、艺术、科技等特长的学生',
                'types': {
                    '体育特长生': {
                        'categories': ['田径', '篮球', '足球', '排球', '游泳', '武术', '羽毛球', '乒乓球'],
                        'requirements': [
                            '具有一定的体育专项技能',
                            '身体健康，符合体育训练要求',
                            '初中阶段获得过县级以上比赛奖项优先'
                        ],
                        'test_content': [
                            '专项技能测试',
                            '身体素质测试',
                            '文化课成绩要求'
                        ],
                        'admission_benefit': '可享受降低10-30分录取优惠',
                        'application_time': '每年3-4月'
                    },
                    '艺术特长生': {
                        'categories': ['音乐', '舞蹈', '美术', '书法', '播音主持', '表演'],
                        'requirements': [
                            '具有一定的艺术专业基础',
                            '初中阶段获得过县级以上比赛奖项优先',
                            '部分学校要求提供作品集'
                        ],
                        'test_content': [
                            '专业技能展示',
                            '乐理知识测试（音乐类）',
                            '文化课成绩要求'
                        ],
                        'admission_benefit': '可享受降低10-30分录取优惠',
                        'application_time': '每年3-4月'
                    },
                    '科技特长生': {
                        'categories': ['科技创新', '信息学竞赛', '机器人', '航模'],
                        'requirements': [
                            '初中阶段参加过科技类竞赛',
                            '获得过相关竞赛奖项优先',
                            '具有一定的编程或科技实践能力'
                        ],
                        'test_content': [
                            '专业知识测试',
                            '实践操作能力',
                            '项目展示与答辩'
                        ],
                        'admission_benefit': '可享受降低10-20分录取优惠',
                        'application_time': '每年3-4月'
                    }
                }
            },
            '民族班': {
                'description': '面向少数民族学生的专项招生计划',
                'target_groups': ['彝族', '哈尼族', '傣族', '白族', '回族', '苗族', '壮族', '傈僳族', '拉祜族', '佤族', '纳西族', '瑶族', '景颇族', '藏族', '布朗族', '布依族', '阿昌族', '普米族', '蒙古族', '怒族', '基诺族', '德昂族', '水族', '满族', '独龙族', '其他少数民族'],
                'requirements': [
                    '具有云南省户籍的少数民族学生',
                    '符合中考报名条件',
                    '部分学校要求在少数民族地区就读'
                ],
                'admission_benefit': '可享受降低20-40分录取优惠',
                'quota': '根据当年招生计划确定',
                'application_time': '与普通志愿填报同步'
            },
            '海军航空班': {
                'description': '面向立志从事海军航空事业的优秀学生',
                'target_groups': ['符合条件的初中应届毕业生'],
                'requirements': [
                    '男性，年龄14-16周岁',
                    '身高162-180cm，体重符合标准',
                    '视力：双眼裸眼视力不低于4.6，无色盲、色弱',
                    '身体健康，符合海军招飞体检标准',
                    '热爱祖国，立志献身国防事业'
                ],
                'test_content': [
                    '体格检查',
                    '心理测试',
                    '政治考核',
                    '中考成绩'
                ],
                'admission_benefit': '学费减免，享受海军专项培养',
                'quota': '每年全省招生约50人',
                'application_time': '每年2-3月',
                'training_features': [
                    '军事化管理',
                    '航空特色课程',
                    '定期体能训练',
                    '寒暑假军事体验'
                ]
            },
            '国际班': {
                'description': '面向有意向出国留学的学生',
                'target_groups': ['初中应届毕业生'],
                'requirements': [
                    '具有较好的英语基础',
                    '家庭经济条件允许',
                    '有志于出国留学'
                ],
                'test_content': [
                    '英语水平测试',
                    '综合素质评估',
                    '中考成绩'
                ],
                'admission_benefit': '国际化课程体系，外教教学',
                'curriculum': ['A-Level', 'AP', 'IB', '中加课程', '中英课程'],
                'application_time': '每年3-5月'
            }
        }
    
    def get_special_student_policy(self, policy_type: str, prefecture: str = None) -> Optional[Dict]:
        """获取特长生或专项招生政策"""
        return self.special_student_policies.get(policy_type)
    
    def get_policy_by_prefecture(self, prefecture: str) -> Optional[Dict]:
        """获取某州市的招生政策"""
        return self.policy_database.get(prefecture)
    
    def _init_policy_database(self) -> Dict:
        """初始化各地州市招生政策数据库"""
        return {
            '昆明市': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 5,  # 可填报志愿数
                'batch_settings': ['提前批', '第一批次', '第二批次', '第三批次'],
                'special_policies': {
                    '定向生': '优质高中定向招生，占招生计划30%',
                    '特长生': '体育、艺术特长生招生',
                    '民族班': '面向少数民族学生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-20分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['云南师范大学附属中学', '昆明市第一中学', '昆明市第三中学', '昆明市第八中学', '昆明市第十中学', '昆明市第十四中学']
                },
                'tiqian_pi': {
                    'schools': ['云南师范大学附属中学', '昆明市第一中学', '昆明市第三中学'],
                    'types': ['民族班', '海军航空班', '特色班']
                }
            },
            '玉溪市': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '玉溪一中等优质高中定向招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-15分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['玉溪第一中学', '玉溪师范学院附属中学']
                },
                'tiqian_pi': {
                    'schools': ['玉溪第一中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '曲靖市': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '曲靖一中等优质高中定向招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-15分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['曲靖第一中学', '曲靖第二中学', '宣威第六中学']
                },
                'tiqian_pi': {
                    'schools': ['曲靖第一中学', '曲靖第二中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '文山壮族苗族自治州': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '州一中等优质高中定向招生',
                    '民族班': '面向少数民族学生招生，享受政策倾斜',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-20分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['文山州第一中学', '文山州民族中学']
                },
                'tiqian_pi': {
                    'schools': ['文山州第一中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '红河哈尼族彝族自治州': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '红河一中等优质高中定向招生，占招生计划50%',
                    '民族班': '面向少数民族学生招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-15分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['红河州第一中学', '建水一中', '蒙自第一高级中学']
                },
                'tiqian_pi': {
                    'schools': ['红河州第一中学', '建水一中'],
                    'types': ['民族班', '特长生']
                }
            },
            '大理白族自治州': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '大理一中等优质高中定向招生',
                    '民族班': '面向少数民族学生招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-15分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['大理第一中学', '大理州民族中学', '下关第一中学']
                },
                'tiqian_pi': {
                    'schools': ['大理第一中学', '下关第一中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '楚雄彝族自治州': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '楚雄一中等优质高中定向招生',
                    '民族班': '面向少数民族学生招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-15分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['楚雄第一中学', '楚雄州民族中学']
                },
                'tiqian_pi': {
                    'schools': ['楚雄第一中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '昭通市': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '昭通一中等优质高中定向招生',
                    '民族班': '面向少数民族学生招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-20分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['昭通市第一中学', '昭通市实验中学']
                },
                'tiqian_pi': {
                    'schools': ['昭通市第一中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '普洱市': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '普洱一中等优质高中定向招生',
                    '民族班': '面向少数民族学生招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-15分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['普洱市第一中学', '普洱市第二中学']
                },
                'tiqian_pi': {
                    'schools': ['普洱市第一中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '西双版纳傣族自治州': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '景洪一中等优质高中定向招生',
                    '民族班': '面向少数民族学生招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-15分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['景洪市第一中学', '西双版纳州民族中学']
                },
                'tiqian_pi': {
                    'schools': ['景洪市第一中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '德宏傣族景颇族自治州': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '德宏一中等优质高中定向招生',
                    '民族班': '面向少数民族学生招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-15分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['德宏州第一中学', '芒市第一中学']
                },
                'tiqian_pi': {
                    'schools': ['德宏州第一中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '丽江市': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '丽江一中等优质高中定向招生',
                    '民族班': '面向少数民族学生招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-15分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['丽江市第一中学', '古城区第一中学']
                },
                'tiqian_pi': {
                    'schools': ['丽江市第一中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '怒江傈僳族自治州': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '怒江一中等优质高中定向招生',
                    '民族班': '面向少数民族学生招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '15-25分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['怒江州第一中学']
                },
                'tiqian_pi': {
                    'schools': ['怒江州第一中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '迪庆藏族自治州': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '迪庆一中等优质高中定向招生',
                    '民族班': '面向少数民族学生招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '15-25分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['迪庆州第一中学']
                },
                'tiqian_pi': {
                    'schools': ['迪庆州第一中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '临沧市': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '临沧一中等优质高中定向招生',
                    '民族班': '面向少数民族学生招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-15分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['临沧市第一中学', '临沧市第二中学']
                },
                'tiqian_pi': {
                    'schools': ['临沧市第一中学'],
                    'types': ['民族班', '特长生']
                }
            },
            '保山市': {
                'enrollment_method': '统一考试招生',
                'volunteer_count': 4,
                'batch_settings': ['提前批', '第一批次', '第二批次'],
                'special_policies': {
                    '定向生': '保山一中等优质高中定向招生',
                    '民族班': '面向少数民族学生招生',
                    '特长生': '体育、艺术特长生招生'
                },
                'score_calculation': {
                    'total_score': 700,
                    'subjects': {
                        '语文': 120,
                        '数学': 120,
                        '英语': 120,
                        '物理': 80,
                        '化学': 50,
                        '道德与法治': 50,
                        '历史': 50,
                        '体育': 50,
                        '生物': 30,
                        '地理': 30
                    }
                },
                'key_dates': {
                    '报名时间': '3月中旬',
                    '考试时间': '6月16-18日',
                    '成绩公布': '7月初',
                    '录取时间': '7月中下旬'
                },
                'zhibiao_daoxiao': {
                    'ratio': '50%',
                    'score_discount': '10-15分',
                    'requirement': '连续三年在学籍所在学校就读',
                    'schools': ['保山市第一中学', '腾冲市第一中学']
                },
                'tiqian_pi': {
                    'schools': ['保山市第一中学', '腾冲市第一中学'],
                    'types': ['民族班', '特长生']
                }
            }
        }
    
    def _init_school_database(self) -> Dict:
        """初始化学校数据库"""
        return {
            '昆明市': [
                {
                    'name': '昆明第一中学',
                    'level': '一级一等',
                    'type': '公办',
                    'address': '五华区西昌路',
                    'features': ['百年名校', '教学质量优异', '竞赛成绩突出'],
                    'enrollment_plan': {'2025': 800, '2024': 800},
                    'score_line': {'2024': 680, '2023': 678}
                },
                {
                    'name': '昆明第三中学',
                    'level': '一级一等',
                    'type': '公办',
                    'address': '呈贡区',
                    'features': ['百年名校', '理科见长', '师资力量强'],
                    'enrollment_plan': {'2025': 700, '2024': 700},
                    'score_line': {'2024': 675, '2023': 673}
                },
                {
                    'name': '昆明第八中学',
                    'level': '一级一等',
                    'type': '公办',
                    'address': '五华区龙泉路',
                    'features': ['教学质量高', '文科优势', '校园环境优美'],
                    'enrollment_plan': {'2025': 750, '2024': 750},
                    'score_line': {'2024': 672, '2023': 670}
                },
                {
                    'name': '昆明第十中学',
                    'level': '一级一等',
                    'type': '公办',
                    'address': '白塔路',
                    'features': ['综合实力强', '艺术特色', '国际交流多'],
                    'enrollment_plan': {'2025': 700, '2024': 700},
                    'score_line': {'2024': 668, '2023': 666}
                },
                {
                    'name': '昆明第十四中学',
                    'level': '一级一等',
                    'type': '公办',
                    'address': '五华区黑林铺',
                    'features': ['理科强势', '科技创新', '体育特色'],
                    'enrollment_plan': {'2025': 650, '2024': 650},
                    'score_line': {'2024': 665, '2023': 663}
                },
                {
                    'name': '云南师范大学附属中学',
                    'level': '一级一等',
                    'type': '公办',
                    'address': '高新区',
                    'features': ['省属重点', '教学质量顶尖', '升学率高'],
                    'enrollment_plan': {'2025': 600, '2024': 600},
                    'score_line': {'2024': 685, '2023': 683}
                }
            ],
            '玉溪市': [
                {
                    'name': '玉溪第一中学',
                    'level': '一级一等',
                    'type': '公办',
                    'address': '红塔区',
                    'features': ['玉溪市顶尖高中', '教学质量优异', '百年名校'],
                    'enrollment_plan': {'2025': 1000, '2024': 1000},
                    'score_line': {'2024': 650, '2023': 648}
                },
                {
                    'name': '玉溪师范学院附属中学',
                    'level': '一级二等',
                    'type': '公办',
                    'address': '红塔区',
                    'features': ['师资力量强', '教学质量高', '文科优势'],
                    'enrollment_plan': {'2025': 800, '2024': 800},
                    'score_line': {'2024': 630, '2023': 628}
                },
                {
                    'name': '江川区第一中学',
                    'level': '一级三等',
                    'type': '公办',
                    'address': '江川区',
                    'features': ['江川区重点', '教学质量稳定', '本地优势'],
                    'enrollment_plan': {'2025': 600, '2024': 600},
                    'score_line': {'2024': 580, '2023': 578}
                },
                {
                    'name': '通海县第一中学',
                    'level': '二级一等',
                    'type': '公办',
                    'address': '通海县',
                    'features': ['通海县重点', '教学质量良好'],
                    'enrollment_plan': {'2025': 500, '2024': 500},
                    'score_line': {'2024': 560, '2023': 558}
                }
            ],
            '曲靖市': [
                {
                    'name': '曲靖第一中学',
                    'level': '一级一等',
                    'type': '公办',
                    'address': '麒麟区',
                    'features': ['曲靖市顶尖高中', '教学质量优异', '理科强势'],
                    'enrollment_plan': {'2025': 1200, '2024': 1200},
                    'score_line': {'2024': 660, '2023': 658}
                },
                {
                    'name': '曲靖第二中学',
                    'level': '一级一等',
                    'type': '公办',
                    'address': '麒麟区',
                    'features': ['综合实力强', '教学质量高', '文科优势'],
                    'enrollment_plan': {'2025': 1000, '2024': 1000},
                    'score_line': {'2024': 645, '2023': 643}
                },
                {
                    'name': '宣威第六中学',
                    'level': '一级二等',
                    'type': '公办',
                    'address': '宣威市',
                    'features': ['宣威市重点', '教学质量稳定'],
                    'enrollment_plan': {'2025': 800, '2024': 800},
                    'score_line': {'2024': 620, '2023': 618}
                }
            ],
            '文山壮族苗族自治州': [
                {
                    'name': '文山州第一中学',
                    'level': '一级二等',
                    'type': '公办',
                    'address': '文山市',
                    'features': ['州内顶尖高中', '教学质量优异', '民族教育特色'],
                    'enrollment_plan': {'2025': 1000, '2024': 1000},
                    'score_line': {'2024': 620, '2023': 618}
                },
                {
                    'name': '丘北未央中学',
                    'level': '州一中直管校区',
                    'type': '民办',
                    'address': '丘北县锦屏镇文秀路129号',
                    'features': ['州一中直管', '教学管理同步', '全封闭管理', '师资优质'],
                    'enrollment_plan': {'2026': {'初一': 400, '高一': 600}},
                    'score_line': {'2026': {'高一最低': 420}},
                    'tuition': {
                        '初一': {
                            '公费生（英才班）': {'条件': '语数平均分≥180分', '学费': 0},
                            '自费生A类（实验班）': {'条件': '语数平均分160-179分', '学费': 3900},
                            '自费生B类（平行班）': {'条件': '语数平均分＜160分', '学费': 4900},
                            '住宿费': 600
                        },
                        '高一': {
                            '620分以上': {'学费': 0, '住宿费': 0},
                            '600-619分': {'学费': 800, '住宿费': 600},
                            '570-599分': {'学费': 2000, '住宿费': 600},
                            '540-569分': {'学费': 2500, '住宿费': 600},
                            '510-539分': {'学费': 3000, '住宿费': 600},
                            '480-509分': {'学费': 3500, '住宿费': 600},
                            '450-479分': {'学费': 4000, '住宿费': 600},
                            '420-449分': {'学费': 5000, '住宿费': 600}
                        }
                    },
                    'scholarship': {
                        '初一': {
                            '语数总分200分': 50000,
                            '语数总分199分': 40000,
                            '语数总分198分': 30000,
                            '语数总分197分': 20000,
                            '语数总分196分': 10000
                        },
                        '高一': {
                            '中考全州第1名': 300000,
                            '中考全州第2名': 250000,
                            '中考全州第3名': 200000,
                            '中考全州4-100名': '5-15万'
                        },
                        '高考': {
                            '考入清华北大': 100000
                        }
                    },
                    'contact': {
                        'phone': '0876-4122666',
                        'address': '丘北县锦屏镇文秀路129号（弘毅楼一楼招生办）',
                        'work_time': '工作日8:30-17:00，周末9:00-16:00'
                    },
                    'teachers': {
                        '朱老师': {'phone': '15288462036', 'area': '丘北县二小、八道哨乡、腻脚乡、新店乡、密纳、嘎勒和砚山县'},
                        '黄老师': {'phone': '15911534748', 'area': '麻栗坡、西畴'},
                        '赖老师': {'phone': '13888444021', 'area': '丘北县天星乡、双龙营镇、戈寒乡、县一小、舍得乡'},
                        '陈老师': {'phone': '15368422446', 'area': '丘北县树皮乡、曰者镇、平寨乡、锦屏小学、师大附小、文山、马关'}
                    }
                },
                {
                    'name': '文山州民族中学',
                    'level': '一级三等',
                    'type': '公办',
                    'address': '文山市',
                    'features': ['民族教育特色', '面向全州招生', '政策倾斜'],
                    'enrollment_plan': {'2025': 800, '2024': 800},
                    'score_line': {'2024': 600, '2023': 598}
                },
                {
                    'name': '广南县第一中学',
                    'level': '二级一等',
                    'type': '公办',
                    'address': '广南县',
                    'features': ['广南县重点', '教学质量良好'],
                    'enrollment_plan': {'2025': 600, '2024': 600},
                    'score_line': {'2024': 560, '2023': 558}
                }
            ]
        }
    
    def _init_score_lines(self) -> Dict:
        """初始化历年分数线数据"""
        return {
            '昆明市': {
                '2024': {
                    '第一批次录取线': 620,
                    '第二批次录取线': 580,
                    '第三批次录取线': 550
                },
                '2023': {
                    '第一批次录取线': 618,
                    '第二批次录取线': 578,
                    '第三批次录取线': 548
                }
            },
            '玉溪市': {
                '2024': {
                    '第一批次录取线': 580,
                    '第二批次录取线': 540,
                    '第三批次录取线': 500
                },
                '2023': {
                    '第一批次录取线': 578,
                    '第二批次录取线': 538,
                    '第三批次录取线': 498
                }
            },
            '曲靖市': {
                '2024': {
                    '第一批次录取线': 590,
                    '第二批次录取线': 550,
                    '第三批次录取线': 510
                },
                '2023': {
                    '第一批次录取线': 588,
                    '第二批次录取线': 548,
                    '第三批次录取线': 508
                }
            },
            '文山壮族苗族自治州': {
                '2024': {
                    '第一批次录取线': 560,
                    '第二批次录取线': 520,
                    '第三批次录取线': 480
                },
                '2023': {
                    '第一批次录取线': 558,
                    '第二批次录取线': 518,
                    '第三批次录取线': 478
                }
            }
        }
    
    def get_policy_by_prefecture(self, prefecture: str) -> Optional[Dict]:
        """获取某州市的招生政策"""
        return self.policy_database.get(prefecture)
    
    def get_schools_by_prefecture(self, prefecture: str) -> List[Dict]:
        """获取某州市的学校列表"""
        return self.school_database.get(prefecture, [])
    
    def get_school_detail(self, prefecture: str, school_name: str) -> Optional[Dict]:
        """获取学校详细信息"""
        schools = self.school_database.get(prefecture, [])
        for school in schools:
            if school['name'] == school_name:
                return school
        return None
    
    def get_score_lines(self, prefecture: str, year: str = '2024') -> Optional[Dict]:
        """获取某州市某年的分数线"""
        prefecture_data = self.score_lines.get(prefecture, {})
        return prefecture_data.get(year)
    
    def match_schools_by_score(self, prefecture: str, score: int) -> Dict[str, List[Dict]]:
        """根据分数匹配合适的学校"""
        schools = self.school_database.get(prefecture, [])

        sprint_schools = []
        stable_schools = []
        safe_schools = []

        for school in schools:
            score_line = school.get('score_line', {}).get('2024', 0)

            if score >= score_line + 20:
                stable_schools.append(school)
            elif score >= score_line - 10:
                sprint_schools.append(school)
            elif score >= score_line - 30:
                safe_schools.append(school)
        
        return {
            '冲刺': sprint_schools,
            '稳妥': stable_schools,
            '保底': safe_schools
        }
    
    def generate_volunteer_suggestion(self, prefecture: str, score: int) -> str:
        """生成志愿填报建议"""
        matched_schools = self.match_schools_by_score(prefecture, score)
        policy = self.get_policy_by_prefecture(prefecture)
        
        if not policy:
            return "暂无可用的招生政策信息"
        
        suggestion_parts = []
        
        # 1. 分数分析
        suggestion_parts.append(f"📊 **分数分析**：预估分数 {score} 分")
        
        # 2. 批次建议
        score_lines = self.get_score_lines(prefecture, '2024')
        if score_lines:
            if score >= score_lines.get('第一批次录取线', 600):
                suggestion_parts.append(f"✅ 达到第一批次录取线，可填报优质高中")
            elif score >= score_lines.get('第二批次录取线', 550):
                suggestion_parts.append(f"✅ 达到第二批次录取线，可填报一般高中")
            else:
                suggestion_parts.append(f"⚠️ 建议关注第三批次学校或考虑其他选择")
        
        # 3. 学校推荐
        suggestion_parts.append(f"\n🏫 **学校推荐**：")
        
        if matched_schools['冲刺']:
            suggestion_parts.append(f"\n**冲刺志愿**（分数略低于录取线，有一定风险）：")
            for school in matched_schools['冲刺'][:2]:
                score_line = school.get('score_line', {}).get('2024', 0)
                suggestion_parts.append(f"  • {school['name']}（{school['level']}）- 预估线：{score_line}分")
        
        if matched_schools['稳妥']:
            suggestion_parts.append(f"\n**稳妥志愿**（分数高于录取线，录取概率大）：")
            for school in matched_schools['稳妥'][:2]:
                score_line = school.get('score_line', {}).get('2024', 0)
                suggestion_parts.append(f"  • {school['name']}（{school['level']}）- 预估线：{score_line}分")
        
        if matched_schools['保底']:
            suggestion_parts.append(f"\n**保底志愿**（分数远高于录取线，确保录取）：")
            for school in matched_schools['保底'][:2]:
                score_line = school.get('score_line', {}).get('2024', 0)
                suggestion_parts.append(f"  • {school['name']}（{school['level']}）- 预估线：{score_line}分")
        
        # 4. 填报策略
        suggestion_parts.append(f"\n💡 **填报策略**：")
        suggestion_parts.append(f"  • 可填报 {policy['volunteer_count']} 个志愿")
        suggestion_parts.append("  • 建议按'冲刺-稳妥-保底'梯度填报")
        suggestion_parts.append("  • 关注定向生、特长生等特殊招生政策")
        suggestion_parts.append("  • 注意各批次录取时间和规则")
        
        return "\n".join(suggestion_parts)


# 全局实例
_policy_knowledge = None


def get_enrollment_policy_knowledge() -> EnrollmentPolicyKnowledge:
    """获取招生政策知识库实例（单例）"""
    global _policy_knowledge
    if _policy_knowledge is None:
        _policy_knowledge = EnrollmentPolicyKnowledge()
    return _policy_knowledge


if __name__ == '__main__':
    # 测试招生政策知识库
    knowledge = EnrollmentPolicyKnowledge()
    
    print("=" * 70)
    print("招生政策知识库测试")
    print("=" * 70)
    
    # 测试获取政策
    print("\n📋 玉溪市招生政策：")
    policy = knowledge.get_policy_by_prefecture('玉溪市')
    if policy:
        print(f"  志愿填报数: {policy['volunteer_count']}个")
        print(f"  总分: {policy['score_calculation']['total_score']}分")
        print(f"  批次设置: {', '.join(policy['batch_settings'])}")
    
    # 测试获取学校
    print("\n🏫 玉溪市学校列表：")
    schools = knowledge.get_schools_by_prefecture('玉溪市')
    for school in schools:
        print(f"  • {school['name']}（{school['level']}）")
    
    # 测试分数线匹配
    print("\n🎯 分数匹配测试（江川区学生，预估600分）：")
    matched = knowledge.match_schools_by_score('玉溪市', 600)
    for category, schools in matched.items():
        if schools:
            print(f"\n{category}:")
            for school in schools:
                print(f"  • {school['name']}")
    
    # 测试志愿填报建议
    print("\n" + "=" * 70)
    print("志愿填报建议（玉溪市，预估600分）：")
    print("=" * 70)
    suggestion = knowledge.generate_volunteer_suggestion('玉溪市', 600)
    print(suggestion)
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)
