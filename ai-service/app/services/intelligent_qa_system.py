#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能问答系统
基于知识库的智能问答，支持自然语言查询
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """知识库"""
    
    def __init__(self):
        self._questions = self._load_knowledge()
    
    def _load_knowledge(self) -> List[Dict[str, Any]]:
        """加载知识库"""
        return [
            # 招生政策相关
            {
                'question': '中考什么时候报名？',
                'keywords': ['报名', '时间', '中考报名'],
                'answer': """📅 云南省中考报名时间通常在每年的**11-12月**进行。
                
具体时间以当年云南省教育考试院发布的通知为准。建议关注：
• 当地教育局官网
• 学校班主任通知
• 云南省教育考试院官网

报名流程：
1. 网上报名（登录云南省招生考试网）
2. 现场确认（携带身份证、学籍证明等材料）
3. 缴纳报名费用
4. 信息核对与确认"""
            },
            {
                'question': '中考总分是多少？',
                'keywords': ['总分', '分数', '满分'],
                'answer': """📊 云南省中考总分**600分**（不含体育）。

各科分值：
• 语文：120分
• 数学：120分
• 英语：120分（含听力30分）
• 物理：100分
• 化学：80分
• 体育：50分（计入总分）

部分地区可能有政策性加分，如少数民族加分等。"""
            },
            {
                'question': '什么是定向生？',
                'keywords': ['定向生', '定向招生', '定向录取'],
                'answer': """🎯 **定向生**是指按照云南省教育厅的政策，省级示范高中和州市级重点高中必须将一定比例的招生计划定向分配到辖区内的初中学校。

主要特点：
• 招生比例：省级示范高中不低于50%的招生计划用于定向招生
• 录取优惠：定向生录取分数线通常比统招生低20-50分
• 报名条件：必须具有当地户籍和初中学籍
• 服务要求：毕业后原则上需回定向地区服务

定向生政策旨在促进教育公平，让农村和薄弱学校的学生也有机会进入优质高中。"""
            },
            {
                'question': '跨州市报考需要什么条件？',
                'keywords': ['跨州市', '跨地区', '异地报考', '外地报考'],
                'answer': """🌍 云南省跨州市报考条件：

**基本条件：**
1. 考生必须具有云南省户籍
2. 学籍与户籍不在同一州市的考生，可以选择在学籍地或户籍地报考
3. 随迁子女需提供父母居住证、就业证明等材料

**注意事项：**
• 多数优质高中主要面向本州市招生
• 省级示范高中有少量全省招生计划
• 民办高中通常可以跨州市招生
• 跨州市报考可能影响定向生资格

建议提前咨询目标学校的招生办确认具体政策。"""
            },
            {
                'question': '少数民族加分政策是怎样的？',
                'keywords': ['少数民族', '加分', '优惠政策'],
                'answer': """🏆 云南省少数民族加分政策：

**加分标准：**
• 少数民族考生：加10分
• 少数民族聚居区的少数民族考生：加20分
• 汉族考生在少数民族聚居区：加5分

**适用范围：**
• 适用于云南省内所有高中阶段学校招生
• 加分计入中考总分参与录取

**注意事项：**
• 需提供民族成分证明
• 加分政策以当年省教育厅通知为准
• 部分学校可能对加分有特殊规定"""
            },
            {
                'question': '体育考试考什么？',
                'keywords': ['体育', '体测', '体育考试'],
                'answer': """⚽ 云南省中考体育考试（50分）：

**必考项目（30分）：**
• 耐力跑：男生1000米 / 女生800米

**选考项目（20分）：**
• 技能类：篮球、足球、排球（三选一）
• 体能类：立定跳远、坐位体前屈、实心球（三选一）

**评分标准：**
• 根据《国家学生体质健康标准》评分
• 考试时间通常在4-5月

**注意事项：**
• 体育成绩计入中考总分
• 因病或残疾可申请免考或缓考"""
            },
            {
                'question': '如何填报志愿？',
                'keywords': ['志愿', '填报', '志愿填报'],
                'answer': """🎯 中考志愿填报流程：

1. **了解政策**：阅读当年的招生政策和志愿填报指南
2. **估分定位**：根据模拟考试成绩预估自己的位次
3. **志愿排序**：按"冲刺-稳妥-保底"原则填报
4. **网上填报**：登录云南省招生考试网填报系统
5. **确认提交**：仔细核对信息后提交

建议填报策略：
• 平行志愿：分数优先，遵循志愿顺序
• 服从调剂：增加录取机会
• 梯度设置：志愿之间拉开合理差距"""
            },
            {
                'question': '什么是定向招生？',
                'keywords': ['定向', '定向招生', '定向生'],
                'answer': """🎯 定向招生是指优质高中将部分招生计划定向分配到指定初中学校。

**特点：**
• 录取分数线通常比统招线低10-20分
• 仅限指定初中学校的学生报考
• 录取后需签订定向培养协议
• 毕业后可能有服务年限要求

**优势：**
• 为普通初中学生提供进入优质高中的机会
• 促进教育资源均衡分配

具体政策以当年教育局通知为准。"""
            },
            {
                'question': '跨州市报考需要什么条件？',
                'keywords': ['跨州', '跨市', '跨州市', '异地报考'],
                'answer': """📍 云南省中考跨州市报考政策：

**一般规定：**
• 云南省实行各州市独立招生政策
• 户籍在A州市的考生原则上只能报考A州市的高中
• 跨州市报考需符合特定条件

**允许跨州市报考的情况：**
1. 随迁子女（父母在异地工作）
2. 省级重点中学的全省招生计划
3. 民办高中的跨区域招生
4. 特殊政策照顾对象

**办理流程：**
• 向当地教育局提交申请
• 提供相关证明材料（户籍、学籍、工作证明等）
• 等待审批通过后即可报考"""
            },
            # 备考相关
            {
                'question': '如何提高数学成绩？',
                'keywords': ['数学', '提分', '数学成绩'],
                'answer': """🔢 数学提分攻略：

**基础阶段（1-2个月）：**
• 梳理课本知识点，建立知识框架
• 完成课后习题，巩固基础概念
• 整理错题本，分析错误原因

**强化阶段（1-2个月）：**
• 专题突破：函数、几何、应用题
• 限时训练，提高解题速度
• 总结解题方法和技巧

**冲刺阶段（1个月）：**
• 模拟考试，熟悉考试节奏
• 重点突破压轴题
• 查漏补缺，回归基础

**每日练习：**
• 10-15道基础题
• 2-3道中档题
• 1道压轴题（选做）"""
            },
            {
                'question': '如何缓解考试紧张？',
                'keywords': ['紧张', '焦虑', '考试紧张', '心态'],
                'answer': """🧘 考试紧张缓解方法：

**考前准备：**
• 制定合理的复习计划，避免临时抱佛脚
• 模拟考试环境，适应考试节奏
• 保证充足睡眠（7-8小时）
• 清淡饮食，避免刺激性食物

**考试当天：**
• 提前到达考场，熟悉环境
• 深呼吸放松法：吸气4秒，屏息2秒，呼气6秒
• 积极心理暗示："我已经准备好了"
• 从简单题开始，建立信心

**考后调整：**
• 不对答案，专注下一门考试
• 适当休息，保持体力"""
            },
            # 学校相关
            {
                'question': '公办高中和民办高中有什么区别？',
                'keywords': ['公办', '民办', '区别', '高中类型'],
                'answer': """🏫 公办高中 vs 民办高中：

| 对比项 | 公办高中 | 民办高中 |
|--------|----------|----------|
| 学费 | 较低（政府补贴） | 较高（市场定价） |
| 师资 | 稳定，公办编制 | 灵活，高薪聘名师 |
| 管理 | 相对宽松 | 通常更严格 |
| 招生 | 按学区划分 | 自主招生为主 |
| 特色 | 注重全面发展 | 特色教育突出 |

**选择建议：**
• 预算有限 → 公办高中
• 追求特色教育 → 民办高中
• 成绩优秀 → 重点公办高中
• 需要个性化培养 → 优质民办高中"""
            },
            {
                'question': '如何选择适合自己的高中？',
                'keywords': ['选择', '择校', '适合', '高中'],
                'answer': """🎯 择校指南：

**考虑因素：**
1. **成绩匹配**：选择录取分数线与自己成绩相当的学校
2. **学校类型**：公办vs民办，重点vs普通
3. **地理位置**：离家远近，是否住校
4. **办学特色**：理科强、文科强、艺术特色等
5. **校风校纪**：管理严格程度
6. **升学率**：历年高考成绩

**择校步骤：**
1. 列出目标学校清单
2. 实地考察（开放日、校园参观）
3. 咨询学长学姐
4. 参考家长和老师意见
5. 结合自身情况综合判断

**志愿填报原则：**
• 冲刺校：高于自己成绩10-15分
• 稳妥校：与自己成绩相当
• 保底校：低于自己成绩10-15分"""
            },
            # 常见问题
            {
                'question': '中考可以复读吗？',
                'keywords': ['复读', '重读', '初三复读'],
                'answer': """🔄 云南省中考复读政策：

**原则：**
• 云南省允许初中毕业生复读
• 复读生以"社会考生"身份参加中考
• 部分地区可能有特殊规定

**复读方式：**
1. 回原学校复读
2. 到专门的复读学校
3. 自学备考

**注意事项：**
• 复读生不能享受定向招生政策
• 部分优质高中可能限制录取复读生
• 需重新办理报名手续

建议咨询当地教育局了解最新政策。"""
            },
            {
                'question': '体育考试考什么？',
                'keywords': ['体育', '体测', '体育考试'],
                'answer': """⚽ 云南省中考体育考试：

**总分：50分（计入中考总分）**

**考试项目：**
1. **必考项**：男生1000米/女生800米
2. **选考项**：
   - 立定跳远
   - 实心球
   - 跳绳
   - 篮球运球
   - 足球绕杆
   - 排球垫球

**评分标准：**
• 根据完成时间或次数评分
• 平时成绩占一定比例（通常10%）

**训练建议：**
• 坚持日常锻炼
• 针对弱项专项训练
• 注意运动安全，避免受伤"""
            }
        ]
    
    def search(self, query: str) -> List[Tuple[Dict, float]]:
        """
        搜索知识库
        
        Args:
            query: 用户查询
        
        Returns:
            匹配结果列表（包含相似度分数）
        """
        query_lower = query.lower()
        results = []
        
        for item in self._questions:
            score = 0.0
            
            # 关键词匹配
            for keyword in item['keywords']:
                if keyword.lower() in query_lower:
                    score += 0.3
            
            # 问题相似度
            question_lower = item['question'].lower()
            common_chars = len(set(query_lower) & set(question_lower))
            total_chars = len(set(query_lower) | set(question_lower))
            if total_chars > 0:
                score += (common_chars / total_chars) * 0.5
            
            # 长度惩罚
            if abs(len(query) - len(item['question'])) > 20:
                score *= 0.7
            
            if score > 0.3:
                results.append((item, score))
        
        # 按分数排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results


class IntelligentQASystem:
    """智能问答系统"""
    
    def __init__(self):
        self._knowledge_base = KnowledgeBase()
        self._greetings = [
            '你好！有什么可以帮助你的吗？',
            '您好！我可以帮你解答中考相关问题。',
            '你好！请问有什么问题？'
        ]
        self._farewells = [
            '再见！祝你中考顺利！',
            '拜拜！有问题随时来找我！'
        ]
        logger.info("智能问答系统初始化完成")
    
    def answer(self, query: str) -> Dict[str, Any]:
        """
        回答用户问题
        
        Args:
            query: 用户查询
        
        Returns:
            回答结果
        """
        query = query.strip()
        
        # 检查是否是问候
        if self._is_greeting(query):
            import random
            return {
                'success': True,
                'answer': random.choice(self._greetings),
                'type': 'greeting',
                'confidence': 1.0
            }
        
        # 检查是否是告别
        if self._is_farewell(query):
            import random
            return {
                'success': True,
                'answer': random.choice(self._farewells),
                'type': 'farewell',
                'confidence': 1.0
            }
        
        # 搜索知识库
        results = self._knowledge_base.search(query)
        
        if results:
            best_result, confidence = results[0]
            return {
                'success': True,
                'answer': best_result['answer'],
                'type': 'knowledge',
                'confidence': confidence,
                'matched_question': best_result['question']
            }
        
        # 如果没有找到答案，尝试生成通用回答
        return {
            'success': False,
            'answer': self._generate_fallback(query),
            'type': 'fallback',
            'confidence': 0.0
        }
    
    def _is_greeting(self, query: str) -> bool:
        """检查是否是问候语"""
        greetings = ['你好', '您好', '嗨', 'hello', 'hi', '早上好', '下午好']
        return any(g.lower() in query.lower() for g in greetings)
    
    def _is_farewell(self, query: str) -> bool:
        """检查是否是告别语"""
        farewells = ['再见', '拜拜', 'goodbye', 'bye', '走了']
        return any(f.lower() in query.lower() for f in farewells)
    
    def _generate_fallback(self, query: str) -> str:
        """生成默认回答"""
        return f"""🤔 抱歉，我暂时无法回答这个问题。

你可以尝试询问以下方面的问题：
• 🏫 中考招生政策
• 📊 志愿填报指南
• 📚 备考学习方法
• ⚽ 体育考试信息
• 🏠 公办/民办高中区别

或者换一种方式提问，我会尽力帮你解答！"""


# 全局实例
qa_system = IntelligentQASystem()


def get_qa_system() -> IntelligentQASystem:
    """获取智能问答系统实例"""
    return qa_system


if __name__ == '__main__':
    # 测试问答系统
    print("=" * 70)
    print("智能问答系统测试")
    print("=" * 70)
    
    qa = IntelligentQASystem()
    
    test_queries = [
        '你好',
        '中考总分是多少？',
        '如何填报志愿？',
        '跨州市报考需要什么条件？',
        '如何提高数学成绩？',
        '公办高中和民办高中有什么区别？',
        '体育考试考什么？',
        '再见'
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"👤 用户: {query}")
        print(f"{'='*70}")
        
        result = qa.answer(query)
        print(f"🤖 助手: {result['answer']}")
        print(f"\n📊 类型: {result['type']}, 置信度: {result['confidence']:.2f}")
        if result.get('matched_question'):
            print(f"🔗 匹配问题: {result['matched_question']}")
    
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)