"""
Hermes 智能服务
提供智能分派和技能推荐功能
"""

import sys
import os
import time
import json
import logging
import re
from flask import Flask, request, jsonify
from threading import Thread
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class HermesService:
    """Hermes智能服务核心类 - 提供高级AI能力"""

    def __init__(self):
        self._llm_service = None
        self._conversation_states = {}
        self._user_profiles = {}
        self._knowledge_cache = {}
        self._feedback_store = {}
        self._session_last_active = {}
        self._knowledge_base = []
        self._start_time = time.time()
        self._request_count = 0
        self._session_expiry = 3600
        self._auto_cleanup_interval = 600
        self._last_cleanup = time.time()
        self._load_persisted_state()
        logger.info("Hermes核心服务初始化完成，加载了 %d 个会话状态", len(self._conversation_states))

    @property
    def llm_service(self):
        """延迟导入LLM服务"""
        if self._llm_service is None:
            from openclaw.llm_service import LLMService
            self._llm_service = LLMService()
        return self._llm_service

    def _init_session(self, session_id: str):
        """初始化会话状态"""
        if session_id not in self._conversation_states:
            self._conversation_states[session_id] = {
                "turn_count": 0,
                "topic_history": [],
                "current_topic": None,
                "user_info": {},
                "last_intent": None,
                "satisfaction": 0.5,
                "questions_asked": [],
                "answers_given": [],
                "needs_identified": [],
                "sentiment_history": [],
                "stage": "intro",
                "created_at": time.time(),
                "last_activity": time.time(),
                "feedback_scores": [],
                "journey_complete": False
            }
        self._session_last_active[session_id] = time.time()
        self._maybe_cleanup_sessions()

    def _maybe_cleanup_sessions(self):
        """定期清理过期会话"""
        if time.time() - self._last_cleanup < self._auto_cleanup_interval:
            return
        self._last_cleanup = time.time()
        expired = []
        now = time.time()
        for sid, last_time in list(self._session_last_active.items()):
            if now - last_time > self._session_expiry:
                expired.append(sid)
        for sid in expired:
            self._conversation_states.pop(sid, None)
            self._user_profiles.pop(sid, None)
            self._session_last_active.pop(sid, None)
            self._feedback_store.pop(sid, None)
        if expired:
            logger.info("自动清理了 %d 个过期会话", len(expired))
            self._persist_state()

    def _load_persisted_state(self):
        """从磁盘加载持久化状态"""
        persist_file = os.path.join(os.path.dirname(__file__), 'hermes_state.json')
        try:
            if os.path.exists(persist_file):
                with open(persist_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._conversation_states = data.get('conversation_states', {})
                    self._user_profiles = data.get('user_profiles', {})
                    self._knowledge_base = data.get('knowledge_base', [])
                    self._feedback_store = data.get('feedback_store', {})
                    now = time.time()
                    for sid in list(self._conversation_states.keys()):
                        state = self._conversation_states[sid]
                        if now - state.get('last_activity', 0) > self._session_expiry:
                            del self._conversation_states[sid]
                            self._user_profiles.pop(sid, None)
                            self._feedback_store.pop(sid, None)
                        else:
                            self._session_last_active[sid] = state.get('last_activity', now)
                    logger.info("状态持久化加载完成")
        except Exception as e:
            logger.warning("加载持久化状态失败: %s", e)

    def _persist_state(self):
        """持久化会话状态到磁盘"""
        persist_file = os.path.join(os.path.dirname(__file__), 'hermes_state.json')
        try:
            data = {
                'conversation_states': self._conversation_states,
                'user_profiles': self._user_profiles,
                'knowledge_base': self._knowledge_base[-200:],
                'feedback_store': {k: v for k, v in list(self._feedback_store.items())[-100:]}
            }
            with open(persist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("持久化状态失败: %s", e)

    def _update_user_profile(self, session_id: str, user_input: str, context: dict = None):
        """更新用户画像"""
        if session_id not in self._user_profiles:
            self._user_profiles[session_id] = {
                "grade": None,
                "location": None,
                "score": None,
                "school_preferences": [],
                "budget": None,
                "concerns": [],
                "communication_style": "neutral",
                "target_schools": [],
                "education_type_preference": None,  # 公办/民办/均可
                "boarding_preference": None,  # 住校/走读
                "special_needs": [],  # 特长、少数民族加分等
                "interaction_count": 0
            }

        profile = self._user_profiles[session_id]
        user_lower = user_input.lower()
        profile["interaction_count"] += 1

        # 提取年级信息
        if not profile["grade"]:
            grade_patterns = {"初三": ["初三", "九年级", "9年级"],
                            "初二": ["初二", "八年级", "8年级"],
                            "初一": ["初一", "七年级", "7年级"],
                            "六年级": ["六年级", "小六", "小升初"]}
            for grade, patterns in grade_patterns.items():
                if any(p in user_lower for p in patterns):
                    profile["grade"] = grade
                    break

        # 提取地点信息（支持更多城市）
        if not profile["location"]:
            locations = ["昆明", "文山", "丘北", "红河", "曲靖", "玉溪", "大理", "丽江", "昭通", "普洱", "版纳", "楚雄", "保山", "临沧", "德宏", "怒江", "迪庆", "蒙自", "开远", "个旧", "弥勒", "宜良", "呈贡", "安宁"]
            for loc in locations:
                if loc in user_lower:
                    profile["location"] = loc
                    break

        # 提取分数信息（支持多种格式）
        if not profile["score"]:
            import re
            # 匹配 "680分", "680", "预估680", "能考680"
            score_patterns = [r'(\d{2,3})[分分]', r'预估(\d{2,3})', r'能考(\d{2,3})', r'考(\d{2,3})分']
            for pattern in score_patterns:
                score_match = re.search(pattern, user_input)
                if score_match:
                    score = int(score_match.group(1))
                    if 100 <= score <= 750:
                        profile["score"] = score
                        break

        # 提取预算信息
        if not profile["budget"]:
            budget_patterns = {
                "低": ["便宜", "不贵", "经济", "实惠", "低价"],
                "中": ["适中", "一般", "普通", "正常"],
                "高": ["贵", "高价", "优质", "最好", "顶级"]
            }
            for budget, patterns in budget_patterns.items():
                if any(p in user_lower for p in patterns):
                    profile["budget"] = budget
                    break

        # 提取学校偏好
        schools = ["未央中学", "师大附中", "昆一中", "昆三中", "云大附中", "文山州一中", "昆八中", "昆十中", "曲靖一中", "玉溪一中", "昆明三中", "昆明八中", "昆明十中"]
        for school in schools:
            if school in user_input and school not in profile["school_preferences"]:
                profile["school_preferences"].append(school)

        # 提取关注点（扩展）
        concern_keywords = {
            "升学率": ["一本率", "升学率", "上线率", "清北", "985", "211", "双一流"],
            "费用": ["学费", "费用", "贵不贵", "多少钱", "收费", "价格", "多少钱一年"],
            "管理": ["管理", "严格", "封闭", "校风", "纪律", "校规"],
            "住宿": ["住宿", "住校", "宿舍", "走读", "住", "寝室"],
            "师资": ["老师", "师资", "教师", "教学质量", "师资力量"],
            "环境": ["环境", "校园", "设施", "条件", "硬件"],
            "录取难度": ["录取", "分数线", "能上", "好考", "难不难"],
            "学习压力": ["压力", "累", "辛苦", "竞争", "负担"],
            "交通": ["交通", "方便", "远不远", "接送", "车程"],
            "口碑": ["口碑", "评价", "怎么样", "好不好"]
        }
        for concern, keywords in concern_keywords.items():
            if any(kw in user_lower for kw in keywords) and concern not in profile["concerns"]:
                profile["concerns"].append(concern)

        # 提取学校类型偏好
        if not profile["education_type_preference"]:
            if any(kw in user_lower for kw in ["公办", "公立", "免费"]):
                profile["education_type_preference"] = "公办"
            elif any(kw in user_lower for kw in ["民办", "私立", "自费"]):
                profile["education_type_preference"] = "民办"

        # 提取住宿偏好
        if not profile["boarding_preference"]:
            if any(kw in user_lower for kw in ["住校", "住宿", "寄宿"]):
                profile["boarding_preference"] = "住校"
            elif any(kw in user_lower for kw in ["走读", "回家"]):
                profile["boarding_preference"] = "走读"

        # 提取特殊需求
        if any(kw in user_lower for kw in ["特长", "艺术", "体育", "音乐", "美术", "舞蹈"]):
            if "特长生" not in profile["special_needs"]:
                profile["special_needs"].append("特长生")
        if any(kw in user_lower for kw in ["少数民族", "加分"]):
            if "少数民族加分" not in profile["special_needs"]:
                profile["special_needs"].append("少数民族加分")

        if profile["interaction_count"] % 10 == 0:
            self._persist_state()

    def analyze_emotion(self, user_input: str) -> dict:
        """分析用户情感状态"""
        # 首先尝试基于规则的情感分析（快速且可靠）
        rule_based_result = self._rule_based_emotion_analysis(user_input)
        if rule_based_result["confidence"] >= 0.7:
            return rule_based_result
        
        # 如果规则匹配不够自信，尝试使用LLM进行更精确的分析
        try:
            rule_emotion = rule_based_result.get("emotion", "中性")
            rule_confidence = rule_based_result.get("confidence", 0.5)
            
            prompt = f"""你是一个专业的中考择校咨询情感分析专家。分析用户输入的情感状态。

## 情绪分类（选择最匹配的一个）：
- **积极**: 正面情绪，如感谢、满意、赞扬（"谢谢"、"很好"、"明白了"）
- **期待**: 有明确需求寻求帮助，带疑问或探索语气（"推荐学校"、"这个怎么样"、"能上吗"、"多少分"）
- **焦虑**: 担忧、不安、压力（"怎么办"、"考不上"、"担心"、"没信心"）
- **困惑**: 不理解、需要澄清（"不懂"、"什么意思"、"不清楚"）
- **消极**: 拒绝、否定、放弃（"不需要"、"算了"、"不用了"）
- **兴奋**: 非常高兴、激动（"太好了"、"太棒了"）
- **中性**: 平淡陈述，无明显情绪

## 判断规则：
1. 含数字+学校+疑问语气 = 期待（不是中性！）
2. 含"推荐/建议/帮忙"等求助词 = 期待
3. 含"怎么办/不行/考不上"等焦虑词 = 焦虑
4. 含"不需要/算了/不用"等拒绝词 = 消极
5. 简短感谢或认可 = 积极
6. 纯陈述事实 = 中性

## urgency判断：高(紧急/压力) | 中(正常咨询) | 低(轻松随意)
## needs_support: 期待/焦虑/困惑=true, 消极/中性=false
## confidence: 0.5-0.95

## 参考示例：
"680分能上师大附中吗" → {{"emotion":"期待","urgency":"中","sentiment":"其他","needs_support":true,"confidence":0.9}}
"孩子成绩不好怎么办" → {{"emotion":"焦虑","urgency":"高","sentiment":"焦虑","needs_support":true,"confidence":0.9}}
"好的，谢谢" → {{"emotion":"积极","urgency":"低","sentiment":"满意","needs_support":false,"confidence":0.9}}
"不需要了" → {{"emotion":"消极","urgency":"低","sentiment":"不满","needs_support":false,"confidence":0.9}}
"这个学费多少" → {{"emotion":"期待","urgency":"中","sentiment":"其他","needs_support":false,"confidence":0.75}}
"太失望了" → {{"emotion":"消极","urgency":"中","sentiment":"不满","needs_support":false,"confidence":0.85}}

规则分析结果：{rule_emotion}(置信度{rule_confidence})

## 用户输入：
{user_input}

只返回JSON:"""

            result = self.llm_service.generate_answer(prompt)
            if result and "answer" in result:
                import re
                json_match = re.search(r'\{[^}]+\}', result["answer"])
                if json_match:
                    llm_result = json.loads(json_match.group())
                    # 合并LLM和规则的结果，优先LLM
                    merged = {**rule_based_result, **llm_result}
                    merged["confidence"] = max(float(merged.get("confidence", 0.5)), rule_confidence)
                    return merged
        except Exception as e:
            logger.error(f"LLM情感分析失败: {e}")

        return rule_based_result

    def _rule_based_emotion_analysis(self, user_input: str) -> dict:
        """基于规则的情感分析（多维度评分）"""
        user_lower = user_input.lower()
        
        # 多维度评分系统
        emotion_scores = {
            "积极": 0,
            "兴奋": 0,
            "焦虑": 0,
            "困惑": 0,
            "期待": 0,
            "消极": 0,
            "中性": 1
        }
        
        # 积极情绪关键词及权重
        positive_keywords = {
            "谢谢": 3, "感谢": 3, "太好了": 3, "非常感谢": 4, "辛苦了": 3, "帮大忙了": 4,
            "好的": 2, "不错": 2, "满意": 2, "很好": 2, "挺好": 2, "真不错": 3,
            "棒棒的": 3, "给力": 3, "厉害": 2, "牛": 1, "赞": 2, "靠谱": 3,
            "明白了": 2, "了解": 1, "懂了": 2, "知道了": 1
        }
        
        # 兴奋情绪关键词
        excited_keywords = {
            "太棒了": 4, "太好了": 4, "开心": 3, "高兴": 3, "兴奋": 4,
            "激动": 4, "喜出望外": 5, "惊喜": 4, "欢呼": 4, "太赞了": 4
        }
        
        # 焦虑情绪关键词及权重
        anxiety_keywords = {
            "怎么办": 4, "考不上": 5, "担心": 3, "焦虑": 4, "压力": 3,
            "紧张": 3, "害怕": 4, "担忧": 3, "着急": 3, "忐忑": 4,
            "不安": 3, "发愁": 4, "头疼": 3, "崩溃": 4, "绝望": 5,
            "不好": 2, "困难": 2, "太难了": 3, "没信心": 4, "老是": 1,
            "还是不行": 3, "一直": 1, "为什么不": 2
        }
        
        # 困惑情绪关键词
        confused_keywords = {
            "不懂": 4, "不清楚": 4, "不明白": 4, "困惑": 4, "迷茫": 3,
            "糊涂": 3, "疑问": 2, "疑惑": 3, "搞不懂": 4, "看不明白": 4,
            "什么意思": 3, "不理解": 3
        }
        
        # 期待情绪关键词
        expect_keywords = {
            "推荐": 3, "可以吗": 3, "怎么样": 2, "多少": 2, "什么": 1,
            "如何": 2, "怎么": 1, "能上": 3, "适合": 2, "查询": 2,
            "咨询": 2, "想知道": 3, "了解一下": 3, "能不能": 3, "能不能上": 4,
            "建议": 2, "帮我看看": 4, "帮我分析": 4, "介绍一下": 3, "介绍": 2,
            "帮忙": 2, "请": 1, "有没有": 2, "有哪些": 2, "选哪个": 3,
            "考多少": 3, "分数线": 2, "录取": 2
        }
        
        # 消极情绪关键词
        negative_keywords = {
            "不需要": 4, "不要了": 4, "不用了": 4, "算了": 3, "不要": 3,
            "不用": 3, "暂时不需要": 4, "下次再说": 4, "算了吧": 4,
            "太失望了": 4, "没用": 3, "不好用": 3, "不满意": 4, "没用处": 4,
            "放弃了": 4, "不": 1, "不会": 1, "不能": 1, "不行": 3
        }
        
        # 逐词匹配并累加分数
        for keyword, score in positive_keywords.items():
            if keyword in user_lower:
                emotion_scores["积极"] += score
        
        for keyword, score in excited_keywords.items():
            if keyword in user_lower:
                emotion_scores["兴奋"] += score
        
        for keyword, score in anxiety_keywords.items():
            if keyword in user_lower:
                emotion_scores["焦虑"] += score
        
        for keyword, score in confused_keywords.items():
            if keyword in user_lower:
                emotion_scores["困惑"] += score
        
        for keyword, score in expect_keywords.items():
            if keyword in user_lower:
                emotion_scores["期待"] += score
        
        for keyword, score in negative_keywords.items():
            if keyword in user_lower:
                emotion_scores["消极"] += score
        
        # 上下文信号加分
        # 分数+学校查询 = 高期待
        if re.search(r'\d{2,3}', user_lower) and any(kw in user_lower for kw in ["分", "分能", "考", "上"]):
            emotion_scores["期待"] += 5
        
        # 问号表示疑问/期待
        if "?" in user_lower or "？" in user_lower:
            emotion_scores["期待"] += 2
            emotion_scores["困惑"] += 1
        
        # 感叹号表示强烈情绪
        if "!" in user_lower or "！" in user_lower:
            top_emotion = max(emotion_scores, key=emotion_scores.get)
            if top_emotion not in ["中性", "消极", "困惑"]:
                emotion_scores[top_emotion] += 2
        
        # "啊"结尾表示感叹
        if user_lower.endswith("啊") or user_lower.endswith("呀"):
            emotion_scores["期待"] += 1
        
        # 找出最高分
        max_score = max(emotion_scores.values())
        best_emotion = max(emotion_scores, key=emotion_scores.get)
        
        # 如果最高分<=1，就是中性
        if max_score <= 1:
            return {
                "emotion": "中性", "urgency": "中", "sentiment": "其他",
                "needs_support": False, "confidence": 0.6
            }
        
        # 计算置信度（最高分/总分）
        total_score = sum(emotion_scores.values())
        confidence = min(max_score / max(total_score, 1), 1.0)
        
        # 根据情绪类型设置结果
        urgency_map = {
            "焦虑": "高", "困惑": "中", "期待": "中", "兴奋": "低",
            "积极": "低", "消极": "低", "中性": "中"
        }
        sentiment_map = {
            "积极": "满意", "兴奋": "开心", "焦虑": "焦虑", "困惑": "疑惑",
            "期待": "其他", "消极": "不满", "中性": "其他"
        }
        needs_support_map = {
            "焦虑": True, "困惑": True, "期待": True,
            "兴奋": False, "积极": False, "消极": False, "中性": False
        }
        
        result = {
            "emotion": best_emotion,
            "urgency": urgency_map.get(best_emotion, "中"),
            "sentiment": sentiment_map.get(best_emotion, "其他"),
            "needs_support": needs_support_map.get(best_emotion, False),
            "confidence": round(confidence, 2)
        }
        
        # 如果置信度不是很高，尝试LLM
        if confidence < 0.7:
            result["confidence"] = round(confidence, 2)
        
        return result

    def track_conversation_state(self, session_id: str, user_input: str, context: dict = None) -> dict:
        """跟踪对话状态"""
        self._init_session(session_id)
        self._update_user_profile(session_id, user_input, context)

        state = self._conversation_states[session_id]
        state["turn_count"] += 1
        state["last_activity"] = time.time()
        self._session_last_active[session_id] = time.time()

        state["questions_asked"].append(user_input)
        if len(state["questions_asked"]) > 10:
            state["questions_asked"] = state["questions_asked"][-10:]

        topic = self._extract_topic(user_input)
        if topic != state["current_topic"]:
            if topic:
                state["topic_history"].append(topic)
                state["current_topic"] = topic
            if state["turn_count"] <= 2:
                state["stage"] = "intro"
            elif state["turn_count"] <= 5:
                state["stage"] = "exploration"
            elif any(kw in user_input for kw in ["报名", "预约", "确定", "选择"]):
                state["stage"] = "decision"
            else:
                state["stage"] = "exploration"

        emotion = self.analyze_emotion(user_input)
        state["sentiment_history"].append(emotion)
        if len(state["sentiment_history"]) > 5:
            state["sentiment_history"] = state["sentiment_history"][-5:]

        needs = self.identify_needs(session_id, user_input)
        for need in needs:
            if need not in state["needs_identified"]:
                state["needs_identified"].append(need)

        if state["turn_count"] % 5 == 0:
            self._persist_state()

        return state

    def record_answer(self, session_id: str, answer: str):
        """记录系统回复内容"""
        if session_id in self._conversation_states:
            state = self._conversation_states[session_id]
            state["answers_given"].append(answer)
            if len(state["answers_given"]) > 10:
                state["answers_given"] = state["answers_given"][-10:]

    def _extract_topic(self, user_input: str) -> str:
        """提取话题（基础方法）"""
        topics = {
            "学校查询": ["学校", "高中", "初中", "录取", "分数", "升学率", "校风", "师资"],
            "政策咨询": ["政策", "中考", "志愿", "填报", "录取规则", "加分", "自主招生"],
            "费用咨询": ["学费", "费用", "收费", "价格", "多少钱", "奖学金", "赞助费"],
            "学校比较": ["比较", "对比", "哪个好", "区别", "哪个更好", "哪个适合"],
            "报名咨询": ["报名", "怎么报", "如何报", "招生", "报名时间", "报名条件"],
            "学习计划": ["学习", "备考", "复习", "计划", "辅导", "补习", "冲刺"],
            "预约看校": ["预约", "看校", "参观", "开放日", "校园开放", "咨询会"]
        }

        user_lower = user_input.lower()
        for topic, keywords in topics.items():
            if any(kw in user_lower for kw in keywords):
                return topic
        return "其他"

    def classify_intent(self, user_input: str) -> dict:
        """增强的意图识别"""
        user_lower = user_input.lower()
        
        # 意图分类规则
        intents = [
            {
                "intent": "school_inquiry",
                "name": "学校查询",
                "keywords": ["学校", "高中", "初中", "中学", "附中", "一中", "二中", "三中", 
                           "录取", "分数线", "升学率", "校风", "师资", "环境", "住宿"],
                "patterns": [r".*中学怎么样", r".*学校好不好", r".*高中推荐"]
            },
            {
                "intent": "policy_inquiry",
                "name": "政策咨询",
                "keywords": ["政策", "中考", "志愿", "填报", "录取规则", "加分", "自主招生",
                           "定向生", "配额生", "录取流程", "志愿设置"],
                "patterns": [r".*政策是什么", r".*怎么填志愿", r".*志愿怎么报"]
            },
            {
                "intent": "fee_inquiry",
                "name": "费用咨询",
                "keywords": ["学费", "费用", "收费", "价格", "多少钱", "奖学金", "赞助费",
                           "住宿费", "书本费", "择校费"],
                "patterns": [r"学费多少", r".*收费标准", r".*多少钱"]
            },
            {
                "intent": "school_compare",
                "name": "学校比较",
                "keywords": ["比较", "对比", "哪个好", "区别", "哪个更好", "哪个适合",
                           "vs", "和", "与"],
                "patterns": [r".*和.*哪个好", r".*与.*对比", r".*vs.*"]
            },
            {
                "intent": "application_inquiry",
                "name": "报名咨询",
                "keywords": ["报名", "怎么报", "如何报", "招生", "报名时间", "报名条件",
                           "招生简章", "报名流程", "网上报名"],
                "patterns": [r"怎么报名", r".*报名时间", r".*招生简章"]
            },
            {
                "intent": "study_plan",
                "name": "学习计划",
                "keywords": ["学习", "备考", "复习", "计划", "辅导", "补习", "冲刺",
                           "刷题", "错题", "知识点", "提分"],
                "patterns": [r".*学习方法", r".*复习计划", r".*备考策略"]
            },
            {
                "intent": "campus_visit",
                "name": "预约看校",
                "keywords": ["预约", "看校", "参观", "开放日", "校园开放", "咨询会",
                           "开放日时间", "参观校园"],
                "patterns": [r"预约参观", r".*开放日", r"参观.*学校"]
            },
            {
                "intent": "score_recommendation",
                "name": "分数推荐",
                "keywords": ["分", "分数", "推荐", "能上", "可以上", "适合"],
                "patterns": [r"\d+分.*推荐", r"\d+分.*能上", r"\d+分.*可以上"]
            },
            {
                "intent": "general_question",
                "name": "一般咨询",
                "keywords": ["什么", "怎么", "如何", "为什么", "多少"],
                "patterns": []
            }
        ]
        
        # 优先匹配模式
        for intent_info in intents:
            for pattern in intent_info["patterns"]:
                if re.search(pattern, user_lower):
                    return {
                        "intent": intent_info["intent"],
                        "name": intent_info["name"],
                        "confidence": 0.95
                    }
        
        # 然后匹配关键词
        for intent_info in intents:
            if any(kw in user_lower for kw in intent_info["keywords"]):
                return {
                    "intent": intent_info["intent"],
                    "name": intent_info["name"],
                    "confidence": 0.8
                }
        
        # 默认返回
        return {
            "intent": "general_question",
            "name": "一般咨询",
            "confidence": 0.5
        }

    def get_conversation_insight(self, session_id: str, user_input: str) -> dict:
        """获取对话洞察 - 增强版：更智能的话题检测和跟进问题生成"""
        state = self._conversation_states.get(session_id, {})
        profile = self._user_profiles.get(session_id, {})
        user_lower = user_input.lower()

        insight_prompt = f"""你是一个中考择校咨询专家，分析对话上下文并给出具体建议。

当前用户输入：{user_input}

对话信息：
- 轮次：{state.get('turn_count', 0)}
- 话题历史：{state.get('topic_history', [])}
- 当前话题：{state.get('current_topic', '未知')}
- 对话阶段：{state.get('stage', 'intro')}
- 已识别需求：{state.get('needs_identified', [])}

用户画像：
- 年级：{profile.get('grade', '未知')}
- 城市：{profile.get('location', '未知')}
- 分数：{profile.get('score', '未知')}
- 关注学校：{profile.get('school_preferences', [])}
- 关注点：{profile.get('concerns', [])}

请给出JSON格式的建议（所有字段用中文）：
{{
    "suggested_response_style": "专业详细/简洁直接/亲切友好/引导探索",
    "should_ask_followup": true/false,
    "followup_topic": "具体的中文追问，要自然、有引导性",
    "rapport_level": "高/中/低",
    "is_topic_switch": true/false,
    "emotional_tone": "理解/支持/激励/中性",
    "missing_info": ["需要补充的信息列表"],
    "suggested_schools": ["根据分数和地区推荐的具体学校名称"],
    "conversation_goal": "当前阶段的目标（建立信任/收集信息/推荐方案/促成行动）"
}}

只返回JSON："""

        try:
            result = self.llm_service.generate_answer(insight_prompt)
            if result and "answer" in result:
                import re
                json_match = re.search(r'\{[^}]+\}', result["answer"])
                if json_match:
                    insight = json.loads(json_match.group())
                    followup = insight.get('followup_topic', '')
                    if followup and not self._is_valid_followup(followup):
                        insight['followup_topic'] = self._generate_smart_followup(state, profile, user_input)
                        insight['should_ask_followup'] = bool(insight['followup_topic'])
                    return insight
        except Exception as e:
            logger.error(f"对话洞察LLM分析失败: {e}")

        missing_info = self._detect_missing_info(profile, state, user_input)
        conversation_stage = self._detect_detailed_stage(state, user_input)
        followup_topic = self._generate_smart_followup(state, profile, user_input)

        return {
            "suggested_response_style": self._suggest_style(conversation_stage, profile),
            "should_ask_followup": bool(followup_topic),
            "followup_topic": followup_topic,
            "rapport_level": "高" if state.get("turn_count", 0) > 2 else "中",
            "is_topic_switch": False,
            "emotional_tone": "理解",
            "missing_info": missing_info,
            "suggested_schools": self._suggest_schools_by_profile(profile),
            "conversation_goal": self._determine_goal(conversation_stage)
        }

    def _is_valid_followup(self, followup: str) -> bool:
        """检查跟进问题是否有效"""
        invalid_patterns = [
            "了解更多信息", "请继续", "还有其他问题", "还有什么",
            "有什么问题", "什么问题", "有什么需要"
        ]
        if not followup or len(followup) < 4:
            return False
        for pattern in invalid_patterns:
            if pattern in followup and len(followup) < 15:
                return False
        return True

    def _generate_smart_followup(self, state: dict, profile: dict, user_input: str) -> str:
        """智能生成最合适的跟进问题"""
        turn_count = state.get("turn_count", 0)
        missing_info = self._detect_missing_info(profile, state, user_input)
        stage = self._detect_detailed_stage(state, user_input)
        user_lower = user_input.lower()

        if missing_info:
            priority_map = {
                "预估分数": ["分数", "分", "预估", "考多少"],
                "所在城市": ["城市", "哪个", "在哪儿", "哪里"],
                "孩子年级": ["年级", "几年级", "初中", "高中", "小学"],
                "学校偏好": ["学校", "想上", "目标"],
                "费用预算": ["预算", "学费", "费用", "价格"]
            }
            prioritized = sorted(missing_info, key=lambda x: sum(
                1 for kw in priority_map.get(x, []) if kw in user_lower
            ), reverse=True)
            top_missing = prioritized[0] if prioritized else missing_info[0]

            followup_templates = {
                "预估分数": [
                    "孩子预估能考多少分呢？这样我可以给您精准匹配学校~",
                    "方便告诉我孩子的预估分数吗？不同分数段适合的学校差别很大哦~"
                ],
                "所在城市": [
                    "请问您在哪个城市呢？我可以为您推荐当地及周边的学校~",
                    "方便告诉我您在哪个城市吗？不同地区的招生政策差别挺大的~"
                ],
                "孩子年级": [
                    "孩子现在读几年级呢？不同年级的规划重点不太一样~",
                    "方便告诉我孩子现在几年级吗？这样我能提供更精准的建议~"
                ],
                "学校偏好": [
                    "您有心仪的目标学校吗？或者对学校有什么特殊要求？",
                    "您比较看重学校的哪些方面呢？比如升学率、师资、还是管理模式？"
                ],
                "费用预算": [
                    "您对学费方面有什么预算要求吗？公办和民办的差别还是比较大的~",
                    "您在经济方面有什么考虑吗？我可以帮您筛选不同价位的学校~"
                ]
            }
            import random
            return random.choice(followup_templates.get(top_missing, [
                f"方便告诉我{top_missing}吗？这样我能为您提供更精准的建议~"
            ]))

        if turn_count <= 2:
            return "请问您想了解哪方面的信息呢？比如学校介绍、录取分数线，还是志愿填报建议？"

        if stage == "exploration":
            current_topic = state.get("current_topic", "")
            if "学校" in current_topic:
                return "您还想了解其他学校吗？或者需要我帮您对比几所学校？"
            elif "政策" in current_topic:
                return "关于政策方面，您还有其他想了解的吗？"
            elif "分数" in current_topic:
                return "需要我帮您分析更多学校的录取情况吗？"
        elif stage == "decision":
            return "需要我帮您整理一份志愿填报方案，或者预约学校参观吗？"

        return ""

    def _detect_missing_info(self, profile: dict, state: dict, user_input: str) -> list:
        """检测对话中缺失的关键信息"""
        missing = []
        if not profile.get("grade"):
            missing.append("孩子年级")
        if not profile.get("location"):
            missing.append("所在城市")
        if not profile.get("score") and state.get("turn_count", 0) > 1:
            missing.append("预估分数")
        if not profile.get("school_preferences") and state.get("turn_count", 0) > 2:
            missing.append("学校偏好")
        if not profile.get("budget") and state.get("stage", "") == "exploration":
            missing.append("费用预算")
        return missing

    def _detect_detailed_stage(self, state: dict, user_input: str) -> str:
        """检测更精细的对话阶段"""
        turn_count = state.get("turn_count", 0)
        user_lower = user_input.lower()

        if turn_count <= 1:
            return "intro"

        decision_keywords = ["报名", "预约", "缴费", "确定", "决定", "选哪个", "哪个好"]
        if any(kw in user_lower for kw in decision_keywords):
            return "decision"

        if turn_count >= 4:
            return "decision"

        if turn_count >= 2:
            return "exploration"

        return state.get("stage", "intro")

    def _suggest_style(self, stage: str, profile: dict) -> str:
        """根据阶段和用户画像建议回复风格"""
        if stage == "intro":
            return "亲切友好"
        elif stage == "exploration":
            return "专业详细"
        elif stage == "decision":
            return "简洁直接"
        return "亲切友好"

    def _suggest_schools_by_profile(self, profile: dict) -> list:
        """根据用户画像推荐学校"""
        schools = []
        location = profile.get("location", "")
        score = profile.get("score", 0)

        school_db = {
            "昆明": {
                "high": ["云南师范大学附属中学", "昆明市第一中学", "昆明市第三中学"],
                "mid": ["昆明市第八中学", "昆明市第十中学", "云南大学附属中学"],
                "low": ["昆明市第十四中学", "官渡区第一中学", "安宁中学"]
            },
            "文山": {
                "high": ["文山州第一中学"],
                "mid": ["丘北未央中学", "文山州第二中学"],
                "low": ["砚山一中", "丘北一中"]
            },
            "曲靖": {
                "high": ["曲靖市第一中学"],
                "mid": ["曲靖市第二中学"],
                "low": ["麒麟区第一中学"]
            }
        }

        city_schools = school_db.get(location, school_db.get("昆明", {}))

        if score >= 650:
            schools = city_schools.get("high", [])
        elif score >= 580:
            schools = city_schools.get("mid", [])
        elif score > 0:
            schools = city_schools.get("low", [])

        return schools

    def _determine_goal(self, stage: str) -> str:
        """确定当前阶段的对话目标"""
        goal_map = {
            "intro": "建立信任",
            "exploration": "收集信息",
            "decision": "推荐方案"
        }
        return goal_map.get(stage, "建立信任")

    def generate_intelligent_followup(self, session_id: str, context: dict = None) -> str:
        """生成智能追问问题"""
        profile = self._user_profiles.get(session_id, {})
        state = self._conversation_states.get(session_id, {})
        
        # 构建缺失信息列表
        missing_info = []
        if not profile.get("grade"):
            missing_info.append(("grade", "年级"))
        if not profile.get("location"):
            missing_info.append(("location", "城市"))
        if not profile.get("score"):
            missing_info.append(("score", "分数"))
        
        # 如果没有缺失信息，尝试根据对话阶段生成追问
        if not missing_info:
            return self._generate_contextual_followup(state, profile)
        
        # 根据缺失信息生成自然的追问
        followup_map = {
            "grade": [
                "方便告诉我孩子目前在读几年级吗？这样我可以提供更针对性的建议。",
                "想了解一下孩子现在是几年级呢？不同年级的规划重点不太一样。",
                "请问孩子目前读几年级？我可以根据年级给出合适的建议。"
            ],
            "location": [
                "请问您在哪个城市呢？这样我可以推荐当地的学校。",
                "方便告诉我您所在的城市吗？我会为您推荐当地合适的学校。",
                "想了解一下您在哪个城市？这样能更好地为您推荐学校。"
            ],
            "score": [
                "孩子的预估分数大概是多少呢？这样我可以精准推荐学校。",
                "方便告诉我孩子的预估中考分数吗？我来帮您匹配合适的学校。",
                "想了解一下孩子的预估分数是多少？这样能更精准地推荐学校。"
            ]
        }
        
        # 优先选择最重要的缺失信息（分数 > 城市 > 年级）
        priority_order = ["score", "location", "grade"]
        for info_type, _ in missing_info:
            if info_type in priority_order:
                import random
                return random.choice(followup_map[info_type])
        
        return ""
    
    def _generate_contextual_followup(self, state: dict, profile: dict) -> str:
        """根据对话阶段生成上下文感知的追问"""
        stage = state.get("stage", "intro")
        current_topic = state.get("current_topic", "")
        turn_count = state.get("turn_count", 0)
        
        followups = []
        
        if stage == "intro":
            followups = [
                "除了这些，您还想了解哪方面的信息呢？",
                "还有什么想了解的吗？我可以继续为您解答。",
                "您还有其他想咨询的问题吗？"
            ]
        elif stage == "exploration":
            if current_topic == "学校查询":
                followups = [
                    "您还想了解其他学校吗？",
                    "除了这所学校，还想了解哪所学校的信息？",
                    "需要我为您介绍其他学校吗？"
                ]
            elif current_topic == "政策咨询":
                followups = [
                    "关于中考政策，您还有其他疑问吗？",
                    "还想了解哪方面的政策信息？",
                    "需要我详细解释某个政策细节吗？"
                ]
            elif current_topic == "分数推荐":
                followups = [
                    "这个分数段还有其他感兴趣的学校吗？",
                    "需要我为您分析其他学校的录取情况吗？",
                    "还想了解哪些学校的信息？"
                ]
            else:
                followups = [
                    "您还想了解哪方面的信息呢？",
                    "还有什么需要帮助的吗？"
                ]
        elif stage == "decision":
            followups = [
                "需要我帮您预约看校吗？",
                "想了解具体的报名流程吗？",
                "需要我帮您整理一份对比表吗？"
            ]
        
        if not followups:
            followups = [
                "还有什么想了解的吗？",
                "需要我帮您解答其他问题吗？"
            ]
        
        import random
        return random.choice(followups)

    def rewrite_question(self, session_id: str, user_input: str) -> str:
        """智能问题重写 - 将模糊问题转化为具体查询"""
        state = self._conversation_states.get(session_id, {})
        profile = self._user_profiles.get(session_id, {})

        # 构建上下文
        history_context = ""
        if state.get("topic_history"):
            history_context = f"之前讨论过: {', '.join(state['topic_history'])}"

        prompt = f"""你是一个智能问题重写器，负责将用户的模糊问题转化为更具体、更清晰的查询。

用户输入：{user_input}
对话历史：{history_context}
用户已知信息：
- 年级：{profile.get('grade', '未知')}
- 城市：{profile.get('location', '未知')}
- 分数：{profile.get('score', '未知')}

请将用户输入重写为一个清晰、完整的问题，补充缺失的上下文信息。

例如：
输入："这个学校怎么样"
重写："请问{{之前讨论的学校}}这所学校怎么样？"

输入："学费多少"
重写："请问{{之前讨论的学校}}的学费是多少？"

只返回重写后的问题："""

        try:
            result = self.llm_service.generate_answer(prompt)
            if result and "answer" in result:
                rewritten = result["answer"].strip()
                if rewritten and rewritten != user_input:
                    logger.info(f"问题重写: {user_input} -> {rewritten}")
                    return rewritten
        except Exception as e:
            logger.error(f"问题重写失败: {e}")

        return user_input

    def generate_conversation_summary(self, session_id: str) -> str:
        """生成对话总结"""
        state = self._conversation_states.get(session_id, {})
        profile = self._user_profiles.get(session_id, {})
        
        # 如果没有对话历史，返回提示
        if not state.get("questions_asked") or not state.get("answers_given"):
            return "我们刚刚开始对话，还没有太多内容可以总结。有什么我可以帮助您的吗？"
        
        # 构建对话历史摘要
        questions = state.get("questions_asked", [])
        answers = state.get("answers_given", [])
        
        conversation_summary = []
        for i, (q, a) in enumerate(zip(questions, answers), 1):
            # 简短化答案
            short_answer = a[:60] + "..." if len(a) > 60 else a
            conversation_summary.append(f"{i}. 您问：{q}\n   我答：{short_answer}")
        
        # 构建用户画像摘要
        profile_info = []
        if profile.get("grade"):
            profile_info.append(f"孩子{profile['grade']}")
        if profile.get("location"):
            profile_info.append(f"在{profile['location']}")
        if profile.get("score"):
            profile_info.append(f"预估分数{profile['score']}分")
        if profile.get("school_preferences"):
            profile_info.append(f"关注学校: {', '.join(profile['school_preferences'])}")
        if profile.get("concerns"):
            profile_info.append(f"关注点: {', '.join(profile['concerns'])}")
        
        user_context = "；".join(profile_info) if profile_info else "暂无信息"
        
        # 构建总结内容
        summary_parts = []
        summary_parts.append("📋 对话总结")
        summary_parts.append("")
        summary_parts.append(f"【对话轮次】共{len(questions)}轮")
        summary_parts.append(f"【用户信息】{user_context}")
        summary_parts.append("")
        summary_parts.append("【对话内容】")
        summary_parts.extend(conversation_summary)
        
        # 添加已识别的需求
        if state.get("needs_identified"):
            summary_parts.append("")
            summary_parts.append(f"【已识别需求】{'、'.join(state['needs_identified'])}")
        
        # 添加下一步建议
        summary_parts.append("")
        summary_parts.append("【下一步建议】")
        
        # 根据对话阶段和用户画像生成建议
        if not profile.get("score"):
            summary_parts.append("• 如果方便，请告诉我孩子的预估分数，我可以为您推荐合适的学校")
        if not profile.get("location"):
            summary_parts.append("• 如果方便，请告诉我您所在的城市，我会推荐当地的学校")
        if profile.get("score") and profile.get("location"):
            summary_parts.append("• 需要我为您详细分析推荐的学校吗？")
            summary_parts.append("• 需要我帮您整理学校对比表吗？")
        
        summary_parts.append("")
        summary_parts.append("如果您还有其他问题，随时可以问我！")
        
        return "\n".join(summary_parts)

    def generate_contextual_response(self, session_id: str, user_input: str, base_response: str = "") -> str:
        """生成上下文感知的个性化回复"""
        state = self._conversation_states.get(session_id, {})
        profile = self._user_profiles.get(session_id, {})
        emotion = self.analyze_emotion(user_input)

        # 构建对话历史
        history_text = ""
        if state.get("questions_asked"):
            qa_pairs = []
            questions = state.get("questions_asked", [])[-5:]
            answers = state.get("answers_given", [])[-5:]
            for i, (q, a) in enumerate(zip(questions, answers), 1):
                qa_pairs.append(f"用户: {q}\n顾问: {a[:80]}...")
            history_text = "\n".join(qa_pairs)

        # 构建用户上下文
        context_info = []
        if profile.get("grade"):
            context_info.append(f"孩子{profile['grade']}")
        if profile.get("location"):
            context_info.append(f"在{profile['location']}")
        if profile.get("score"):
            context_info.append(f"预估分数{profile['score']}分")
        if profile.get("school_preferences"):
            context_info.append(f"关注学校: {', '.join(profile['school_preferences'])}")
        if profile.get("concerns"):
            context_info.append(f"关注点: {', '.join(profile['concerns'])}")

        user_context = "；".join(context_info) if context_info else "暂无信息"

        needs_text = ""
        if state.get("needs_identified"):
            needs_text = "已识别需求：" + "、".join(state["needs_identified"])

        prompt = f"""你是一个专业的中考择校顾问，需要根据对话历史和用户画像生成个性化回复。

用户当前输入：{user_input}
用户情感状态：{emotion.get('emotion', '中性')}、{emotion.get('sentiment', '其他')}
用户画像：{user_context}
对话阶段：{state.get('stage', 'intro')}
{needs_text}

对话历史：
{history_text if history_text else '（首轮对话）'}

基础回复：{base_response if base_response else '（无）'}

请生成一个高度个性化、温暖专业的回复，要求：
1. 如果已知用户城市和分数，直接给出针对性的学校推荐和分析
2. 如果已知用户年级，调整信息针对该年级
3. 根据情感状态调整语气：焦虑→多安慰和确定性信息、积极→多鼓励和具体建议、疑惑→耐心解释
4. 每次回复最多推荐2-3所学校，避免信息过载
5. 使用emoji增强亲和力，但不要过度
6. 回复要有逻辑结构，分段清晰
7. 如果基础回复不空，在其基础上优化而非完全重写

个性化回复："""

        try:
            result = self.llm_service.generate_answer(prompt)
            if result and "answer" in result:
                enhanced = result["answer"].strip()
                if enhanced and len(enhanced) > 10:
                    logger.info(f"上下文感知回复生成成功 (长度: {len(enhanced)})")
                    return enhanced
        except Exception as e:
            logger.error(f"上下文感知回复生成失败: {e}")

        return base_response if base_response else self._get_fallback_response(profile)

    def _get_fallback_response(self, profile: dict) -> str:
        """当LLM不可用时的后备回复"""
        parts = []
        if profile.get("location"):
            parts.append(f"我看到您在{profile['location']}，")
        if profile.get("grade"):
            parts.append(f"孩子是{profile['grade']}，")
        if profile.get("score"):
            parts.append(f"预估{profile['score']}分。")
        
        if parts:
            return "您好！" + "".join(parts) + "\n\n请告诉我您想了解什么，我会为您提供针对性的建议~"
        return "您好！请告诉我您想了解什么，我会为您提供专业的择校建议~"

    def identify_needs(self, session_id: str, user_input: str) -> list:
        """识别用户潜在需求"""
        profile = self._user_profiles.get(session_id, {})
        state = self._conversation_states.get(session_id, {})

        needs_context = ""
        if profile.get("grade"):
            needs_context += f"孩子{profile['grade']}，"
        if profile.get("location"):
            needs_context += f"在{profile['location']}，"
        if profile.get("score"):
            needs_context += f"预估{profile['score']}分，"

        prompt = f"""分析用户输入，识别潜在需求（中考择校场景）：

用户输入：{user_input}
已知信息：{needs_context}
对话阶段：{state.get('stage', 'intro')}

请列出用户最可能的3-5个潜在需求，例如：
- 需要了解某学校的具体信息
- 需要分数匹配学校推荐
- 需要了解学费和费用
- 需要志愿填报策略
- 需要了解中考政策
- 需要预约看校
- 需要学习/备考指导
- 需要缓解升学焦虑
- 需要比较多个学校

返回格式（每行一个需求）："""
        
        try:
            result = self.llm_service.generate_answer(prompt)
            if result and "answer" in result:
                needs = []
                for line in result["answer"].strip().split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        import re
                        line = re.sub(r'^[\d]+[\.\、\)\s]*', '', line)
                        line = line.strip()
                        if line and len(line) > 2:
                            needs.append(line)
                logger.info(f"识别到需求: {needs[:5]}")
                return needs[:5]
        except Exception as e:
            logger.error(f"需求识别失败: {e}")

        return []

    def analyze_intent(self, user_input: str, context: dict = None) -> dict:
        """分析用户意图，返回推荐的智能体"""
        try:
            prompt = f"""你是一个智能对话系统的大脑，负责分析用户意图并选择最合适的智能体来处理请求。

用户输入：{user_input}

可用智能体：
1. zk-master (总控智能体): 处理学校查询、政策咨询、分数推荐等综合咨询
2. zk-info (信息智能体): 处理信息检索、网页抓取、数据分析
3. zk-learning (学习智能体): 处理学习计划、备考建议、科目辅导
4. zk-marketing (营销智能体): 处理推广素材、话术优化
5. zk-dev (开发智能体): 处理技术支持、代码问题

请根据用户输入判断最合适的智能体，只返回智能体ID（如：zk-master）。

用户输入分析：{user_input}

最佳智能体："""

            result = self.llm_service.generate_answer(prompt)
            recommended_agent = "zk-master"

            if result and "answer" in result:
                answer = result["answer"].lower()
                if "learning" in answer or "学习" in answer or "备考" in answer or "辅导" in answer:
                    recommended_agent = "zk-learning"
                elif "info" in answer or "信息" in answer or "查询" in answer:
                    recommended_agent = "zk-info"
                elif "market" in answer or "营销" in answer or "推广" in answer:
                    recommended_agent = "zk-marketing"
                elif "dev" in answer or "开发" in answer or "技术" in answer:
                    recommended_agent = "zk-dev"

            return {
                "success": True,
                "data": {
                    "recommended_agent": recommended_agent,
                    "intent": self._classify_intent(user_input),
                    "confidence": 0.9
                }
            }
        except Exception as e:
            logger.error(f"意图分析失败: {e}")
            return {
                "success": True,
                "data": {
                    "recommended_agent": "zk-master",
                    "intent": "general_inquiry",
                    "confidence": 0.5
                }
            }

    def recommend_skills(self, user_input: str, context: dict = None) -> dict:
        """推荐需要的技能"""
        try:
            prompt = f"""你是一个智能技能推荐系统，负责分析用户请求并推荐最合适的技能来处理。

用户输入：{user_input}

可用技能：
1. find - 查找信息、学校、政策等
2. search - 搜索网络内容
3. policy-parser - 解析招生政策
4. school-matcher - 学校匹配推荐
5. school-comparator - 学校比较分析
6. learning-style-analyzer - 学习风格分析
7. weak-subjects-analyzer - 薄弱科目分析
8. study-time-planner - 学习时间规划
9. data-analyzer - 数据分析
10. wechat-scraper - 微信内容抓取

请根据用户输入，推荐最合适的2-3个技能（用逗号分隔）。

用户输入：{user_input}

推荐技能："""

            result = self.llm_service.generate_answer(prompt)
            recommended_skills = ["find", "policy-parser"]

            if result and "answer" in result:
                answer = result["answer"].lower()
                if "学校" in answer or "school" in answer:
                    recommended_skills.append("school-matcher")
                if "比较" in answer or "对比" in answer:
                    recommended_skills.append("school-comparator")
                if "政策" in answer:
                    recommended_skills.append("policy-parser")
                if "学习" in answer or "备考" in answer:
                    recommended_skills.append("learning-style-analyzer")

            return {
                "success": True,
                "data": {
                    "recommended_skills": list(set(recommended_skills))[:3]
                }
            }
        except Exception as e:
            logger.error(f"技能推荐失败: {e}")
            return {
                "success": True,
                "data": {
                    "recommended_skills": ["find"]
                }
            }

    def collect_feedback(self, session_id: str, feedback_type: str, score: float = 0.5, details: dict = None):
        """收集用户反馈并自适应调整"""
        if session_id not in self._feedback_store:
            self._feedback_store[session_id] = []
        
        feedback = {
            "type": feedback_type,
            "score": score,
            "details": details or {},
            "timestamp": time.time(),
            "turn_count": self._conversation_states.get(session_id, {}).get("turn_count", 0)
        }
        self._feedback_store[session_id].append(feedback)
        
        state = self._conversation_states.get(session_id, {})
        if state:
            state["feedback_scores"].append(score)
            if len(state["feedback_scores"]) > 10:
                state["feedback_scores"] = state["feedback_scores"][-10:]
            
            avg_score = sum(state["feedback_scores"]) / len(state["feedback_scores"])
            state["satisfaction"] = avg_score
        
        if feedback_type == "negative" or score < 0.3:
            self._learn_from_negative_feedback(session_id, feedback)
        elif feedback_type == "positive" or score > 0.8:
            self._learn_from_positive_feedback(session_id, feedback)
        
        logger.info("反馈收集: session=%s, type=%s, score=%.2f", session_id, feedback_type, score)

    def _learn_from_negative_feedback(self, session_id: str, feedback: dict):
        """从负面反馈中学习"""
        state = self._conversation_states.get(session_id, {})
        profile = self._user_profiles.get(session_id, {})
        
        if state.get("answers_given"):
            last_answer = state["answers_given"][-1] if state["answers_given"] else ""
            self._knowledge_base.append({
                "type": "negative_pattern",
                "prompt": state.get("questions_asked", [])[-1] if state.get("questions_asked") else "",
                "response_snippet": last_answer[:200],
                "reason": feedback.get("details", {}).get("reason", "未知"),
                "timestamp": time.time()
            })

    def _learn_from_positive_feedback(self, session_id: str, feedback: dict):
        """从正面反馈中学习"""
        state = self._conversation_states.get(session_id, {})
        
        if state.get("answers_given"):
            last_answer = state["answers_given"][-1] if state["answers_given"] else ""
            self._knowledge_base.append({
                "type": "positive_pattern",
                "prompt": state.get("questions_asked", [])[-1] if state.get("questions_asked") else "",
                "response_snippet": last_answer[:200],
                "timestamp": time.time()
            })

    def get_session_insight_report(self, session_id: str) -> dict:
        """生成会话洞察报告"""
        state = self._conversation_states.get(session_id, {})
        profile = self._user_profiles.get(session_id, {})
        feedbacks = self._feedback_store.get(session_id, [])
        
        if not state:
            return {"error": "会话不存在", "session_id": session_id}
        
        avg_satisfaction = state.get("satisfaction", 0.5)
        sentiment_trend = []
        for s in state.get("sentiment_history", [])[-10:]:
            sentiment_trend.append(s.get("emotion", "中性"))
        
        feedback_scores = state.get("feedback_scores", [])
        
        return {
            "session_id": session_id,
            "turn_count": state.get("turn_count", 0),
            "current_stage": state.get("stage", "intro"),
            "current_topic": state.get("current_topic", "其他"),
            "topic_history": state.get("topic_history", [])[-10:],
            "needs_identified": state.get("needs_identified", []),
            "avg_satisfaction": round(avg_satisfaction, 2),
            "sentiment_trend": sentiment_trend[-5:],
            "feedback_count": len(feedbacks),
            "feedback_avg": round(sum(feedback_scores) / len(feedback_scores), 2) if feedback_scores else 0,
            "last_activity": state.get("last_activity", 0),
            "journey_complete": state.get("journey_complete", False),
            "profile": {
                "grade": profile.get("grade"),
                "location": profile.get("location"),
                "score": profile.get("score"),
                "school_preferences": profile.get("school_preferences", []),
                "concerns": profile.get("concerns", []),
                "education_type_preference": profile.get("education_type_preference"),
                "boarding_preference": profile.get("boarding_preference"),
                "special_needs": profile.get("special_needs", [])
            }
        }

    def get_incomplete_sessions(self) -> list:
        """获取未完成的会话列表（用于主动唤醒）"""
        incomplete = []
        now = time.time()
        for sid, state in self._conversation_states.items():
            last_activity = state.get("last_activity", 0)
            idle_time = now - last_activity
            turn_count = state.get("turn_count", 0)
            
            if not state.get("journey_complete", False) and turn_count >= 2:
                if 300 < idle_time < self._session_expiry:
                    profile = self._user_profiles.get(sid, {})
                    incomplete.append({
                        "session_id": sid,
                        "turn_count": turn_count,
                        "idle_minutes": round(idle_time / 60, 1),
                        "current_topic": state.get("current_topic", "其他"),
                        "stage": state.get("stage", "intro"),
                        "missing_info": self._detect_missing_info(profile, state, ""),
                        "profile_summary": {
                            "grade": profile.get("grade"),
                            "location": profile.get("location"),
                            "score": profile.get("score")
                        }
                    })
        
        return sorted(incomplete, key=lambda x: x["turn_count"], reverse=True)

    def get_system_health_report(self) -> dict:
        """生成系统健康报告"""
        now = time.time()
        active_sessions = sum(1 for t in self._session_last_active.values() 
                            if now - t < self._session_expiry)
        total_feedback = sum(len(fb) for fb in self._feedback_store.values())
        avg_satisfaction = 0
        satisfaction_count = 0
        for state in self._conversation_states.values():
            if state.get("satisfaction"):
                avg_satisfaction += state["satisfaction"]
                satisfaction_count += 1
        
        return {
            "service": "Hermes Smart Service",
            "uptime_seconds": round(now - self._start_time, 0),
            "uptime_hours": round((now - self._start_time) / 3600, 1),
            "active_sessions": active_sessions,
            "total_sessions": len(self._conversation_states),
            "total_profiles": len(self._user_profiles),
            "total_feedback": total_feedback,
            "avg_satisfaction": round(avg_satisfaction / max(satisfaction_count, 1), 2),
            "knowledge_base_size": len(self._knowledge_base),
            "session_expiry_seconds": self._session_expiry,
            "last_cleanup": self._last_cleanup,
            "memory_usage": {
                "states": len(self._conversation_states),
                "profiles": len(self._user_profiles),
                "feedback": len(self._feedback_store),
                "knowledge": len(self._knowledge_base)
            }
        }

    def _classify_intent(self, user_input: str) -> str:
        """分类用户意图"""
        user_lower = user_input.lower()
        if any(word in user_lower for word in ["学校", "高中", "初中", "录取", "分数"]):
            return "school_inquiry"
        elif any(word in user_lower for word in ["政策", "中考", "志愿", "填报"]):
            return "policy_inquiry"
        elif any(word in user_lower for word in ["学习", "备考", "复习", "计划"]):
            return "learning_inquiry"
        elif any(word in user_lower for word in ["学费", "费用", "收费", "价格"]):
            return "fee_inquiry"
        else:
            return "general_inquiry"

hermes = HermesService()

@app.route('/v1/agent', methods=['POST'])
def handle_agent():
    """处理智能体分派请求"""
    try:
        hermes._request_count += 1
        data = request.get_json()
        user_input = data.get('data', {}).get('input', '')
        context = data.get('data', {}).get('context', {})
        request_type = data.get('type', 'dispatch')

        logger.info(f"Hermes收到请求: type={request_type}, input={user_input[:30]}...")

        if request_type == 'dispatch':
            result = hermes.analyze_intent(user_input, context)
        elif request_type == 'skills':
            result = hermes.recommend_skills(user_input, context)
        elif request_type == 'emotion':
            result = hermes.analyze_emotion(user_input)
            return jsonify({"success": True, "data": result})
        elif request_type == 'intent':
            result = hermes.classify_intent(user_input)
            return jsonify({"success": True, "data": result})
        elif request_type == 'insight':
            session_id = context.get('session_id', 'default') if context else 'default'
            result = hermes.get_conversation_insight(session_id, user_input)
            return jsonify({"success": True, "data": result})
        elif request_type == 'rewrite':
            session_id = context.get('session_id', 'default') if context else 'default'
            result = hermes.rewrite_question(session_id, user_input)
            return jsonify({"success": True, "data": {"rewritten": result}})
        elif request_type == 'profile':
            session_id = context.get('session_id', 'default') if context else 'default'
            result = hermes._user_profiles.get(session_id, {})
            return jsonify({"success": True, "data": result})
        elif request_type == 'summary':
            session_id = data.get('data', {}).get('session_id', 'default')
            result = hermes.generate_conversation_summary(session_id)
            return jsonify({"success": True, "data": {"summary": result}})
        else:
            result = hermes.analyze_intent(user_input, context)

        return jsonify(result)
    except Exception as e:
        logger.error(f"Hermes处理失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/v1/contextual-response', methods=['POST'])
def handle_contextual_response():
    """生成上下文感知的个性化回复"""
    try:
        data = request.get_json()
        user_input = data.get('data', {}).get('input', '')
        base_response = data.get('data', {}).get('base_response', '')
        session_id = data.get('data', {}).get('session_id', 'default')

        logger.info(f"Hermes上下文回复: input={user_input[:30]}...")

        result = hermes.generate_contextual_response(session_id, user_input, base_response)
        return jsonify({
            "success": True,
            "data": {"response": result}
        })
    except Exception as e:
        logger.error(f"Hermes上下文回复失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/v1/identify-needs', methods=['POST'])
def handle_identify_needs():
    """识别用户潜在需求"""
    try:
        data = request.get_json()
        user_input = data.get('data', {}).get('input', '')
        session_id = data.get('data', {}).get('session_id', 'default')

        logger.info(f"Hermes需求识别: input={user_input[:30]}...")

        needs = hermes.identify_needs(session_id, user_input)
        return jsonify({
            "success": True,
            "data": {"needs": needs}
        })
    except Exception as e:
        logger.error(f"Hermes需求识别失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/v1/record-answer', methods=['POST'])
def handle_record_answer():
    """记录系统回复内容，用于上下文跟踪"""
    try:
        data = request.get_json()
        answer = data.get('data', {}).get('answer', '')
        session_id = data.get('data', {}).get('session_id', 'default')

        logger.info(f"Hermes记录回复: session={session_id}, answer={answer[:30]}...")

        hermes.record_answer(session_id, answer)
        return jsonify({
            "success": True,
            "data": {"recorded": True}
        })
    except Exception as e:
        logger.error(f"Hermes记录回复失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/v1/complete', methods=['POST'])
def handle_complete():
    """综合智能分析：整合意图、情感、洞察"""
    try:
        data = request.get_json()
        user_input = data.get('data', {}).get('input', '')
        context = data.get('data', {}).get('context', {})
        session_id = context.get('session_id', 'default') if context else 'default'

        logger.info(f"Hermes综合分析: input={user_input[:30]}...")

        # 并行执行各项分析
        intent = hermes.analyze_intent(user_input, context)
        emotion = hermes.analyze_emotion(user_input)
        insight = hermes.get_conversation_insight(session_id, user_input)
        state = hermes.track_conversation_state(session_id, user_input, context)

        return jsonify({
            "success": True,
            "data": {
                "intent": intent.get('data', {}),
                "emotion": emotion,
                "insight": insight,
                "conversation_state": {
                    "turn_count": state.get('turn_count', 0),
                    "current_topic": state.get('current_topic', '其他'),
                    "topic_history": state.get('topic_history', [])
                }
            }
        })
    except Exception as e:
        logger.error(f"Hermes综合分析失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/v1/feedback', methods=['POST'])
def handle_feedback():
    """收集用户反馈"""
    try:
        data = request.get_json()
        session_id = data.get('data', {}).get('session_id', 'default')
        feedback_type = data.get('data', {}).get('type', 'neutral')
        score = data.get('data', {}).get('score', 0.5)
        details = data.get('data', {}).get('details', {})

        logger.info("Hermes反馈: session=%s, type=%s, score=%.2f", session_id, feedback_type, score)

        hermes.collect_feedback(session_id, feedback_type, score, details)
        return jsonify({
            "success": True,
            "data": {"recorded": True}
        })
    except Exception as e:
        logger.error("Hermes反馈收集失败: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/v1/session-report', methods=['POST'])
def handle_session_report():
    """获取会话洞察报告"""
    try:
        data = request.get_json()
        session_id = data.get('data', {}).get('session_id', 'default')

        report = hermes.get_session_insight_report(session_id)
        return jsonify({
            "success": True,
            "data": report
        })
    except Exception as e:
        logger.error("Hermes会话报告失败: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/v1/incomplete-sessions', methods=['GET'])
def handle_incomplete_sessions():
    """获取未完成的会话（主动唤醒用）"""
    try:
        sessions = hermes.get_incomplete_sessions()
        return jsonify({
            "success": True,
            "data": {
                "count": len(sessions),
                "sessions": sessions[:20]
            }
        })
    except Exception as e:
        logger.error("Hermes未完成会话获取失败: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        "success": True,
        "status": "healthy",
        "service": "Hermes Smart Service"
    })

@app.route('/metrics', methods=['GET'])
def metrics():
    """获取详细指标和健康报告"""
    try:
        report = hermes.get_system_health_report()
        report["api_requests"] = hermes._request_count
        return jsonify({
            "success": True,
            "data": report
        })
    except Exception as e:
        logger.error("Hermes指标获取失败: %s", e)
        return jsonify({
            "success": True,
            "data": {
                "requests_count": hermes._request_count,
                "uptime": time.time()
            }
        })

def run_server(port=8888):
    """运行服务器"""
    logger.info(f"启动Hermes智能服务，端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

if __name__ == '__main__':
    run_server()