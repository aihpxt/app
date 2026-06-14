"""RAG 检索增强系统"""

import time
import random
from typing import Dict, Any, List, Optional

class RAGSystem:
    """RAG 检索增强系统"""
    
    def __init__(self):
        self.vector_store = {}
        self.knowledge_base = {
            "指标到校": "优质高中招生名额合理分配到区域内初中学校的招生方式，分配比例不低于50%。云南省教育厅要求，省级一等高中必须将不低于50%的招生计划分配到初中学校，其中农村初中学校的分配比例要适当提高。",
            "定向生": "针对特定区域或学校的招生名额，通常面向农村和薄弱学校倾斜。定向生录取分数线一般比统招生低20-30分，为农村学生提供更多进入优质高中的机会。",
            "郊县班": "面向昆明市郊县招生的班级，为郊县学生提供进入优质高中的机会。昆明市一级一等高中如师大附中、昆一中都设有郊县班，专门面向昆明市下辖的县市区招生。",
            "民办高中": "由社会力量举办的高中，学费较高但教学质量和特色各有不同。云南省的民办高中如云大附中星耀学校、北大附中云南实验学校等都是优质的民办高中。",
            "跨区报考": "学生可以报考其他区的学校，但需注意各区的录取规则和分数线差异。昆明市内学生可以跨区报考高中，但不同区的录取分数线可能有所不同。",
            "加分政策": "烈士子女、少数民族、归侨子女等可享受加分照顾，最高不超过20分。具体加分标准由云南省教育厅统一规定，每年可能会有调整。",
            "录取流程": "按照\"分数优先、遵循志愿\"原则，分批次进行录取。昆明市中考录取分为提前批、第一批、第二批等多个批次，每个批次录取结束后再进行下一批次。",
            "中考时间": "昆明市中考通常在每年6月中旬举行，具体时间以教育局通知为准。2024年昆明市中考时间为6月14日至16日。",
            "志愿填报": "中考成绩公布后，学生需要在规定时间内填报志愿，通常分为多个批次。昆明市中考志愿填报一般在成绩公布后3-5天内进行，采用网上填报方式。",
            "录取规则": "按照分数优先、遵循志愿的原则进行录取，同分情况下参考综合素质评价。如果考生分数相同，将依次比较数学、语文、英语、物理、化学等科目的成绩。",
            "昆明12中": "昆明市第十二中学是云南省一级二等普通高级中学，位于昆明市西山区。学校创建于1940年，是一所历史悠久的重点中学。2024年录取分数线约为640-650分。",
            "昆明14中": "昆明市第十四中学是云南省一级二等普通高级中学，位于昆明市五华区。学校创建于1954年，是昆明市的重点中学之一。2024年录取分数线约为630-640分。",
            "师大附中": "云南师范大学附属中学是云南省一级一等普通高级中学，位于昆明市五华区。学校创建于1940年，是云南省最顶尖的高中之一。2024年录取分数线约为680-690分。",
            "昆一中": "昆明市第一中学是云南省一级一等普通高级中学，位于昆明市五华区。学校创建于1905年，是云南省历史最悠久的中学之一。2024年录取分数线约为670-680分。",
            "昆三中": "昆明市第三中学是云南省一级一等普通高级中学，位于昆明市西山区。学校创建于1907年，是昆明市的重点中学之一。2024年录取分数线约为660-670分。",
            "未央中学": "丘北未央中学（文山州一中丘北校区）是文山州一中教育集团核心成员校，非营利性民办完全中学（初中+高中），位于丘北县锦屏镇文秀路129号。与州一中本部实行教学同步、管理同步、考核同步。全封闭管理，师资优质。招生热线：0876-4122666。",
            "丘北未央中学学费": "丘北未央中学学费标准：初一公费生（英才班）语数平均分≥180分学费0元/学期；自费生A类（实验班）语数平均分160-179分学费3900元/学期；自费生B类（平行班）语数平均分＜160分学费4900元/学期。住宿费600元/学期。高一按中考裸分段收费，620分以上公费，420-449分最高5600元/学期。",
            "丘北未央中学奖学金": "丘北未央中学奖学金政策：初一语数总分200分奖励5万元，199分奖励4万元，198分奖励3万元。高一中考全州第1名奖励30万元，第2名25万元，第3名20万元。高考考入清华北大额外奖励10万元。",
            "丘北未央中学招生": "丘北未央中学2026年招生：初一招收400人（英才班50人、实验班150人、平行班200人），高一招收600人（鹏程班50人、英才班150人、实验班400人）。报名需携带户口本、成绩单、学籍证明等材料到学校招生办现场办理。",
            "丘北未央中学预约看校": "丘北未央中学预约看校：工作日8:30-17:00，周末9:00-16:00，无需提前预约可直接到校参观。地址：丘北县锦屏镇文秀路129号（弘毅楼一楼招生办）。招生热线：0876-4122666。",
            "文山州一中": "文山州第一中学是文山州顶尖高中，位于文山市。2024年录取分数线约620分。丘北未央中学是文山州一中直管校区，位于丘北县。",
            "丘北初中": "丘北县初中推荐：丘北未央中学（文山州一中丘北校区），州一中直管，教学管理同步，全封闭管理。招生热线：0876-4122666。地址：丘北县锦屏镇文秀路129号。",
            "小升初": "小升初即小学升初中，通常指六年级学生升入初中的过程。云南省小升初主要采取划片招生、对口直升等方式。丘北未央中学初一面向文山州全州招生，需提供五年级下学期、六年级上学期语文数学成绩单。"
        }
        self._build_vector_store()
    
    def _build_vector_store(self):
        """构建向量存储"""
        # 模拟向量存储，实际项目中使用真实的向量数据库
        for key, value in self.knowledge_base.items():
            # 生成模拟向量
            vector = [random.random() for _ in range(10)]
            self.vector_store[key] = {
                "vector": vector,
                "content": value,
                "metadata": {
                    "type": "policy",
                    "source": "云南省教育局",
                    "timestamp": time.time()
                }
            }
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """检索相关信息"""
        # 模拟检索时间，实际项目中可以移除
        # time.sleep(0.3)  # 移除模拟延迟，提高响应速度
        
        # 改进的检索算法
        results = []
        for key, item in self.vector_store.items():
            # 计算匹配分数
            score = 0.0
            
            # 完全匹配
            if key == query:
                score = 1.0
            # 部分匹配
            elif key in query:
                score = 0.9
            # 关键词匹配
            elif any(word in query for word in key.split()):
                score = 0.8
            # 反向匹配（查询词在知识库条目中）
            elif query in item["content"]:
                score = 0.7
            # 模糊匹配
            elif any(word in item["content"] for word in query.split()):
                score = 0.6
            
            if score > 0.5:
                results.append({
                    "id": key,
                    "content": item["content"],
                    "score": score,
                    "metadata": item["metadata"]
                })
        
        # 按分数排序并返回前top_k个结果
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def generate_answer(self, query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成回答"""
        # 移除模拟延迟，提高响应速度
        # time.sleep(0.5)  # 模拟生成时间
        
        # 基于上下文生成回答
        if context:
            # 综合上下文信息，按照分数排序
            sorted_context = sorted(context, key=lambda x: x["score"], reverse=True)
            
            # 构建回答
            answer_parts = []
            answer_parts.append("根据知识库信息：")
            
            for item in sorted_context:
                answer_parts.append(f"- {item['content']}")
            
            # 添加总结
            if len(sorted_context) > 1:
                answer_parts.append("")
                answer_parts.append("综合以上信息，")
                if "分数线" in query:
                    answer_parts.append("建议您参考以上学校的录取分数线，结合自身成绩合理填报志愿。")
                elif "政策" in query:
                    answer_parts.append("建议您关注最新的招生政策，及时了解相关规定。")
                else:
                    answer_parts.append("希望以上信息对您有所帮助。")
            
            answer = "\n".join(answer_parts)
        else:
            answer = "抱歉，未找到相关信息。建议您尝试使用更具体的关键词进行查询。"
        
        # 计算置信度
        confidence = 0.5
        if context:
            confidence = sum(item["score"] for item in context) / len(context)
        
        return {
            "query": query,
            "answer": answer,
            "context": context,
            "confidence": confidence,
            "timestamp": time.time()
        }
    
    def rag_pipeline(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """RAG 完整流程"""
        # 检索相关信息
        context = self.retrieve(query, top_k)
        
        # 生成回答
        result = self.generate_answer(query, context)
        
        return {
            "success": True,
            "data": result,
            "retrieval_time": 0.3,  # 模拟时间
            "generation_time": 0.5,  # 模拟时间
            "total_time": 0.8
        }
    
    def add_document(self, id: str, content: str, metadata: Dict[str, Any]):
        """添加文档到知识库"""
        # 生成模拟向量
        vector = [random.random() for _ in range(10)]
        self.vector_store[id] = {
            "vector": vector,
            "content": content,
            "metadata": metadata
        }
        self.knowledge_base[id] = content
        return True
    
    def delete_document(self, id: str):
        """从知识库删除文档"""
        if id in self.vector_store:
            del self.vector_store[id]
        if id in self.knowledge_base:
            del self.knowledge_base[id]
        return True
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """获取知识库信息"""
        return {
            "document_count": len(self.knowledge_base),
            "vector_store_size": len(self.vector_store),
            "knowledge_areas": list(self.knowledge_base.keys())[:5],
            "version": "1.0.0"
        }

# 全局RAG系统实例
rag_system = RAGSystem()