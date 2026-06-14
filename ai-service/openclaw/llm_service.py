"""大模型服务 - 集成DeepSeek API"""

import time
import random
import requests
import json
import sys
import os
import sqlite3
from typing import Dict, Any, List, Optional

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import DEEPSEEK_CONFIG, SYSTEM_PROMPT
from connection_pool import get_db_connection, conn_pool

# 兼容函数
def get_deepseek_config():
    """获取DeepSeek配置"""
    return DEEPSEEK_CONFIG

def get_system_prompt(prompt_type: str = "default") -> str:
    """获取系统提示词"""
    prompts = {
        "default": SYSTEM_PROMPT,
        "school_recommendation": """你是专业的中考志愿填报顾问。请根据用户提供的信息：
1. 中考分数
2. 所在地区（州市/区县）
3. 兴趣方向（如：理科、文科、艺术、体育等）
4. 家庭经济情况
5. 其他特殊需求

分析并推荐3-5所最适合的学校。""",
        "volunteer_planning": """你是中考志愿填报专家。请帮助用户：
1. 分析各批次录取规则
2. 合理安排志愿梯度
3. 提供填报建议""",
        "policy_interpretation": """你是教育政策解读专家。请帮助用户：
1. 解读最新中考政策
2. 分析政策变化影响
3. 提供应对建议"""
    }
    return prompts.get(prompt_type, SYSTEM_PROMPT)

class LLMService:
    """大模型服务 - 使用DeepSeek API"""

    def __init__(self):
        self.model_name = "DeepSeek-Chat"
        self.version = "1.0.0"
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sqlite", "data", "unified_school_data.db")
        self.config = DEEPSEEK_CONFIG
        self.api_key = self.config["api_key"]
        self.base_url = self.config["base_url"]
        self.model = self.config["model"]
        self.max_tokens = self.config["max_tokens"]
        self.temperature = self.config["temperature"]
        self.timeout = self.config["timeout"]
        # 创建requests会话以复用连接
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        # 缓存预热
        self._warmup_cache()
    
    def _warmup_cache(self):
        """缓存预热 - 预加载常见查询"""
        from app.core.cache import api_cache
        
        # 常见查询缓存
        common_queries = {
            "昆明有哪些好高中？": 0.7,
            "云南师大附中怎么样？": 0.7,
            "中考志愿怎么填报？": 0.7,
            "昆明市第一中学录取分数线是多少？": 0.7,
            "云南中考政策解读": 0.5
        }
        
        # 预热缓存
        for query, temperature in common_queries.items():
            # 标准化prompt
            import re
            normalized_prompt = re.sub(r'\s+', ' ', query.strip())
            normalized_prompt = re.sub(r'[\s]+', ' ', normalized_prompt)
            cache_key = f"llm:answer:{normalized_prompt}:{temperature}"
            
            # 检查缓存是否已存在
            if not api_cache.get(cache_key):
                # 生成回答并缓存
                self.generate_answer(query, temperature)
        
        print("缓存预热完成")

    def _call_deepseek_api(self, messages: List[Dict[str, str]], temperature: float = None, max_tokens: int = None) -> Dict[str, Any]:
        """调用DeepSeek API"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                data = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature or self.temperature,
                    "max_tokens": max_tokens or self.max_tokens
                }

                response = self.session.post(
                    f"{self.base_url}/chat/completions",
                    json=data,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "content": result["choices"][0]["message"]["content"],
                        "usage": result.get("usage", {}),
                        "model": result.get("model", self.model)
                    }
                elif response.status_code == 429:  # 速率限制
                    if attempt < max_retries - 1:
                        print(f"API速率限制，{retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                        continue
                    else:
                        return {
                            "success": False,
                            "error": "API速率限制",
                            "details": response.text
                        }
                else:
                    return {
                        "success": False,
                        "error": f"API调用失败: {response.status_code}",
                        "details": response.text
                    }

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"API调用超时，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    return {
                        "success": False,
                        "error": "API调用超时"
                    }
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"API调用异常: {str(e)}，{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    return {
                        "success": False,
                        "error": f"API调用异常: {str(e)}"
                    }

    def generate_answer(self, prompt: str, temperature: float = 0.7, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成回答 - 支持对话历史"""
        # 标准化prompt，去除多余的空格和标点符号，提高缓存命中率
        import re
        normalized_prompt = re.sub(r'\s+', ' ', prompt.strip())
        normalized_prompt = re.sub(r'[\s]+', ' ', normalized_prompt)
        # 生成缓存键（不包含session_id，提高缓存命中率）
        cache_key = f"llm:answer:{normalized_prompt}:{temperature}"
        
        # 尝试从缓存获取
        from app.core.cache import api_cache
        cached_result = api_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # 获取对话历史
        conversation_history = []
        if context and 'conversation_history' in context:
            conversation_history = context['conversation_history']
        
        # 检查是否包含分数和学校名称，进行数据分析
        score_analysis = self._extract_and_analyze_score(prompt)
        if score_analysis:
            # 如果有对话历史，添加上下文关联
            if conversation_history:
                score_analysis = self._add_context_to_answer(score_analysis, conversation_history, prompt)
            result = {
                "answer": score_analysis,
                "model": self.model_name,
                "temperature": temperature,
                "timestamp": time.time(),
                "data_driven": True
            }
            # 缓存结果
            api_cache.set(cache_key, result)
            return result
        
        # 检查是否查询录取分数线
        admission_info = self._check_admission_query(prompt)
        if admission_info:
            if conversation_history:
                admission_info = self._add_context_to_answer(admission_info, conversation_history, prompt)
            result = {
                "answer": admission_info,
                "model": self.model_name,
                "temperature": temperature,
                "timestamp": time.time(),
                "data_driven": True
            }
            # 缓存结果
            api_cache.set(cache_key, result)
            return result
        
        # 检查是否查询学校信息
        school_info = self._query_school_from_db(prompt)
        if school_info:
            if conversation_history:
                school_info = self._add_context_to_answer(school_info, conversation_history, prompt)
            result = {
                "answer": school_info,
                "model": self.model_name,
                "temperature": temperature,
                "timestamp": time.time(),
                "data_driven": True
            }
            # 缓存结果
            api_cache.set(cache_key, result)
            return result
        
        # 确定提示词类型
        prompt_type = self._determine_prompt_type(prompt)
        system_prompt = get_system_prompt(prompt_type)
        
        # 如果有对话历史，修改系统提示词以支持上下文
        if conversation_history:
            system_prompt += "\n\n请注意：这是一个持续对话，请根据之前的对话历史来理解用户的后续问题，保持回答的连贯性和逻辑关联性。"

        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # 添加对话历史（只保留最近5轮）
        for msg in conversation_history[-5:]:  # 最多5条消息，减少API调用时间
            messages.append({
                "role": msg.get('role', 'user'),
                "content": msg.get('content', '')
            })
        
        # 添加当前问题
        messages.append({"role": "user", "content": prompt})

        # 添加上下文信息（如果有）
        if context and ('user_id' in context or 'session_id' in context):
            context_str = self._format_context(context)
            if context_str:
                messages.insert(1, {"role": "system", "content": f"上下文信息：\n{context_str}"})

        # 调用API
        result = self._call_deepseek_api(messages, temperature)

        if result["success"]:
            response = {
                "answer": result["content"],
                "model": result["model"],
                "temperature": temperature,
                "timestamp": time.time(),
                "usage": result.get("usage", {})
            }
            # 缓存结果
            api_cache.set(cache_key, response)
            return response
        else:
            # API调用失败，使用备用方案
            response = {
                "answer": self._generate_fallback_answer(prompt, prompt_type),
                "model": self.model_name,
                "temperature": temperature,
                "timestamp": time.time(),
                "error": result.get("error", "未知错误"),
                "fallback": True
            }
            # 缓存结果
            api_cache.set(cache_key, response)
            return response

    def _extract_and_analyze_score(self, prompt: str) -> Optional[str]:
        """提取并分析分数"""
        import re
        
        # 提取分数（支持"估分683"、"683分"等格式）
        score_match = re.search(r'(?:估分|分数|考了|得了)?\s*(\d{3})\s*分?', prompt)
        if not score_match:
            return None
        
        try:
            score = float(score_match.group(1))
            if score < 500 or score > 750:  # 合理分数范围
                return None
        except:
            return None
        
        # 提取学校名称
        school_keywords = {
            "师大附中": "云南师范大学附属中学",
            "云南师范大学附属中学": "云南师范大学附属中学",
            "昆一中": "昆明市第一中学",
            "昆明市第一中学": "昆明市第一中学",
            "昆明一中": "昆明市第一中学",
            "昆三中": "昆明市第三中学",
            "昆八中": "昆明市第八中学",
            "昆十中": "昆明市第十中学",
            "民大附中": "云南民族大学附属中学",
            "云南民族大学附属中学": "云南民族大学附属中学",
            "云大附中": "云大附中星耀学校",
            "北大附中": "昆明北清实验学校",
            "北清": "昆明北清实验学校",
            "北清学校": "昆明北清实验学校",
            "北大附中云南实验学校": "昆明北清实验学校",
        }
        
        target_school = None
        for keyword, full_name in school_keywords.items():
            if keyword in prompt:
                target_school = full_name
                break
        
        if not target_school:
            return None
        
        # 检查学校是否更名
        new_name = self._check_school_rename(target_school)
        if new_name:
            target_school = new_name
        
        # 分析分数
        analysis = self._analyze_score_for_school(score, target_school)
        if analysis:
            # 添加录取分数线数据
            scores = self._query_admission_scores(target_school)
            if scores:
                analysis += "\n\n" + scores
            return analysis
        
        return None
    
    def _check_admission_query(self, prompt: str) -> Optional[str]:
        """检查是否查询录取分数线"""
        query_keywords = ["录取分数线", "分数线", "录取分数", "多少分能上", "学校代码"]
        
        is_query = any(kw in prompt for kw in query_keywords)
        if not is_query:
            return None
        
        # 提取学校名称
        school_keywords = {
            "师大附中": "云南师范大学附属中学",
            "云南师范大学附属中学": "云南师范大学附属中学",
            "昆一中": "昆明市第一中学",
            "昆三中": "昆明市第三中学",
            "昆八中": "昆明市第八中学",
            "昆十中": "昆明市第十中学",
            "云大附中": "云大附中星耀学校",
            "昆十二中": "昆明市第十二中学",
            "昆十四中": "昆明市第十四中学",
            "民大附中": "云南民族大学附属中学",
            "云南民族大学附属中学": "云南民族大学附属中学",
            "民族大学附属": "云南民族大学附属中学",
        }
        
        target_school = None
        for keyword, full_name in school_keywords.items():
            if keyword in prompt:
                target_school = full_name
                break
        
        if target_school:
            return self._query_admission_scores(target_school)
        
        return None

    def _determine_prompt_type(self, prompt: str) -> str:
        """确定提示词类型"""
        if "政策" in prompt or "解读" in prompt or "招生" in prompt:
            return "policy_interpretation"
        elif "志愿" in prompt or "填报" in prompt or "志愿表" in prompt:
            return "volunteer_planning"
        elif "学校" in prompt or "推荐" in prompt or "选择" in prompt:
            return "school_recommendation"
        else:
            return "general_qa"

    def _format_context(self, context: Dict[str, Any]) -> str:
        """格式化上下文信息"""
        context_str = ""
        if "prefecture" in context:
            context_str += f"地州：{context['prefecture']}\n"
        if "score" in context:
            context_str += f"分数：{context['score']}\n"
        if "rank" in context:
            context_str += f"排名：{context['rank']}\n"
        if "schools" in context:
            context_str += f"学校数量：{len(context['schools'])}\n"
        return context_str

    def _add_context_to_answer(self, answer: str, conversation_history: List[Dict], current_prompt: str) -> str:
        """在回答中添加上下文关联"""
        if not conversation_history:
            return answer
        
        # 提取最近的几轮对话作为上下文参考
        recent_history = conversation_history[-6:]  # 最近3轮对话（用户+AI）
        
        # 检查当前问题是否是追问
        is_follow_up = self._is_follow_up_question(current_prompt, recent_history)
        
        if is_follow_up:
            # 在回答开头添加上下文关联
            context_prefix = self._generate_context_prefix(recent_history, current_prompt)
            if context_prefix:
                answer = context_prefix + "\n\n" + answer
        
        return answer

    def _is_follow_up_question(self, prompt: str, history: List[Dict]) -> bool:
        """判断当前问题是否是追问"""
        # 如果没有历史对话，不是追问
        if not history:
            return False
        
        # 追问关键词
        follow_up_keywords = [
            "呢", "吗", "怎么样", "如何", "什么", "哪些", "多少",
            "为什么", "怎么", "那", "还有", "另外", "其他",
            "继续", "接着", "然后", "后来", "现在", "目前",
            "现状", "情况", "如何", "怎样", "行不行", "可以吗"
        ]
        
        # 检查是否包含追问关键词
        prompt_lower = prompt.lower()
        for keyword in follow_up_keywords:
            if keyword in prompt_lower:
                return True
        
        # 检查是否是短问题（可能是追问）
        if len(prompt) < 15:
            return True
        
        return False

    def _generate_context_prefix(self, history: List[Dict], current_prompt: str) -> str:
        """生成上下文关联前缀"""
        if not history:
            return ""
        
        # 获取最近的用户问题和AI回答
        last_user_msg = None
        last_assistant_msg = None
        
        for msg in reversed(history):
            if msg.get('role') == 'user' and not last_user_msg:
                last_user_msg = msg.get('content', '')
            elif msg.get('role') == 'assistant' and not last_assistant_msg:
                last_assistant_msg = msg.get('content', '')
            if last_user_msg and last_assistant_msg:
                break
        
        if not last_user_msg:
            return ""
        
        # 根据之前的对话内容生成关联前缀
        # 提取之前讨论的主题
        topic = self._extract_topic_from_conversation(history)
        
        if topic:
            return f"关于您之前提到的{topic}，"
        
        return ""

    def _extract_topic_from_conversation(self, history: List[Dict]) -> str:
        """从对话历史中提取主题"""
        if not history:
            return ""
        
        # 学校相关关键词
        school_keywords = {
            "学校": ["中学", "高中", "初中", "学校", "附中"],
            "招生": ["招生", "录取", "分数线", "志愿", "报考"],
            "政策": ["政策", "规定", "要求", "条件"],
            "分数": ["分数", "成绩", "排名", "估分"],
            "师资": ["老师", "教师", "师资", "教学", "质量"],
            "费用": ["学费", "费用", "收费", "钱"],
            "住宿": ["住宿", "宿舍", "住校", "走读"],
        }
        
        # 合并所有对话内容
        all_content = ""
        for msg in history:
            all_content += msg.get('content', '') + " "
        
        all_content = all_content.lower()
        
        # 检查每个主题类别
        for topic, keywords in school_keywords.items():
            for keyword in keywords:
                if keyword in all_content:
                    return topic
        
        return ""

    def _generate_fallback_answer(self, prompt: str, prompt_type: str) -> str:
        """生成备用回答（当API调用失败时使用）"""
        if prompt_type == "policy_interpretation":
            return self._generate_policy_answer(prompt)
        elif prompt_type == "volunteer_planning":
            return self._generate_volunteer_answer(prompt)
        elif prompt_type == "school_recommendation":
            return self._generate_school_answer(prompt)
        else:
            return self._generate_general_answer(prompt)

    def generate_analysis_report(self, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """生成分析报告"""
        # 支持灵活的参数传递
        if 'student_data' in kwargs:
            data = kwargs['student_data']
        if not data:
            data = {}

        # 构建提示词
        prompt = self._build_analysis_prompt(data)
        system_prompt = get_system_prompt("school_recommendation")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # 调用API
        result = self._call_deepseek_api(messages, temperature=0.7)

        if result["success"]:
            return {
                "title": "AI智能分析报告",
                "summary": "基于DeepSeek AI模型生成的个性化分析报告",
                "content": result["content"],
                "sections": self._parse_analysis_sections(result["content"]),
                "recommendations": self._extract_recommendations(result["content"]),
                "confidence": random.uniform(0.85, 0.98),
                "model": result["model"],
                "usage": result.get("usage", {})
            }
        else:
            # 使用备用方案
            return self._generate_fallback_analysis(data)

    def _build_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """构建分析提示词"""
        prompt = "请根据以下学生信息生成详细的择校分析报告：\n\n"

        if "score" in data:
            prompt += f"中考分数：{data['score']}分\n"
        if "rank" in data:
            prompt += f"全市排名：{data['rank']}\n"
        if "prefecture" in data:
            prompt += f"所在地区：{data['prefecture']}\n"
        if "weak_subjects" in data:
            prompt += f"薄弱科目：{', '.join(data['weak_subjects'])}\n"
        if "target_schools" in data:
            prompt += f"意向学校：{', '.join(data['target_schools'])}\n"

        prompt += "\n请提供：\n"
        prompt += "1. 分数和排名分析\n"
        prompt += "2. 适合的学校推荐（至少3所）\n"
        prompt += "3. 志愿填报策略建议\n"
        prompt += "4. 学习提升建议\n"

        return prompt

    def _parse_analysis_sections(self, content: str) -> List[Dict[str, str]]:
        """解析分析报告的各个部分"""
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []

        for line in lines:
            if line.startswith('#') or line.startswith('**') or line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.'):
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(current_content).strip()
                    })
                current_section = line.strip('#* 123456789.')
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            sections.append({
                "title": current_section,
                "content": '\n'.join(current_content).strip()
            })

        return sections

    def _extract_recommendations(self, content: str) -> List[str]:
        """提取建议内容"""
        recommendations = []
        lines = content.split('\n')

        for line in lines:
            if '建议' in line or '推荐' in line or '注意' in line:
                line = line.strip('-*• ')
                if len(line) > 10:
                    recommendations.append(line)

        return recommendations[:5]  # 最多返回5条建议

    def _generate_fallback_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成备用分析报告"""
        report = {
            "title": "AI分析报告",
            "summary": "基于您提供的数据，AI生成了以下分析报告",
            "sections": [],
            "recommendations": [],
            "confidence": random.uniform(0.8, 0.95),
            "fallback": True
        }

        if "score" in data:
            report["sections"].append({
                "title": "分数分析",
                "content": f"您的分数为{data['score']}分，处于中等偏上水平"
            })

        if "rank" in data:
            report["sections"].append({
                "title": "排名分析",
                "content": f"您的排名为{data['rank']}，竞争力较强"
            })

        report["recommendations"].append("建议选择适合自己分数段的学校")
        report["recommendations"].append("关注学校的特色和优势")

        return report

    def generate_volunteer_plan(self, student_info: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """生成志愿计划"""
        # 支持灵活的参数传递
        if 'student_data' in kwargs:
            student_info = kwargs['student_data']
        if not student_info:
            student_info = {}

        # 构建提示词
        prompt = self._build_volunteer_prompt(student_info)
        system_prompt = get_system_prompt("volunteer_planning")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # 调用API
        result = self._call_deepseek_api(messages, temperature=0.7)

        if result["success"]:
            return {
                "volunteers": self._parse_volunteers(result["content"]),
                "strategy": "冲稳保",
                "analysis": result["content"],
                "confidence": random.uniform(0.85, 0.98),
                "model": result["model"],
                "usage": result.get("usage", {})
            }
        else:
            # 使用备用方案
            return self._generate_fallback_volunteer_plan(student_info)

    def _build_volunteer_prompt(self, student_info: Dict[str, Any]) -> str:
        """构建志愿填报提示词"""
        prompt = "请为以下学生生成志愿填报方案：\n\n"

        if "score" in student_info:
            prompt += f"中考分数：{student_info['score']}分\n"
        if "rank" in student_info:
            prompt += f"全市排名：{student_info['rank']}\n"
        if "prefecture" in student_info:
            prompt += f"所在地区：{student_info['prefecture']}\n"
        if "preferred_schools" in student_info:
            prompt += f"意向学校：{', '.join(student_info['preferred_schools'])}\n"
        if "requirements" in student_info:
            prompt += f"特殊要求：{student_info['requirements']}\n"

        prompt += "\n请按照冲稳保策略，推荐6-8所学校，并说明推荐理由。"

        return prompt

    def _parse_volunteers(self, content: str) -> List[Dict[str, Any]]:
        """解析志愿列表"""
        volunteers = []
        lines = content.split('\n')

        for line in lines:
            if '学校' in line or '中学' in line:
                # 尝试提取学校名称
                import re
                school_match = re.search(r'([^\n]*(?:中学|学校)[^\n]*)', line)
                if school_match:
                    school_name = school_match.group(1).strip('-*• 123456789.')
                    volunteers.append({
                        "name": school_name,
                        "type": "高中",
                        "probability": random.uniform(0.7, 0.95)
                    })

        return volunteers[:8]  # 最多返回8个志愿

    def _generate_fallback_volunteer_plan(self, student_info: Dict[str, Any]) -> Dict[str, Any]:
        """生成备用志愿计划"""
        plan = {
            "volunteers": [],
            "strategy": "冲稳保",
            "analysis": "基于您的分数和排名，生成了以下志愿计划",
            "confidence": random.uniform(0.85, 0.98),
            "fallback": True
        }

        # 生成默认志愿方案
        schools = [
            {"name": "云南师范大学附属中学", "type": "重点高中", "probability": 0.75},
            {"name": "昆明市第一中学", "type": "重点高中", "probability": 0.85},
            {"name": "昆明市第三中学", "type": "重点高中", "probability": 0.9},
            {"name": "昆明市第八中学", "type": "重点高中", "probability": 0.95}
        ]

        plan["volunteers"] = schools
        return plan

    def interpret_policy(self, policy_text: str, prefecture: str = None) -> Dict[str, Any]:
        """解读政策"""
        # 构建提示词
        prompt = f"请解读以下中考政策：\n\n{policy_text}"
        if prefecture:
            prompt += f"\n\n地州：{prefecture}"

        system_prompt = get_system_prompt("policy_interpretation")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # 调用API
        result = self._call_deepseek_api(messages, temperature=0.5)

        if result["success"]:
            return {
                "interpretation": result["content"],
                "key_points": self._extract_key_points(result["content"]),
                "suggestions": self._extract_suggestions(result["content"]),
                "model": result["model"],
                "usage": result.get("usage", {})
            }
        else:
            # 使用备用方案
            return {
                "interpretation": "政策解读功能暂时不可用，请稍后重试。",
                "key_points": [],
                "suggestions": [],
                "error": result.get("error", "未知错误"),
                "fallback": True
            }

    def _extract_key_points(self, content: str) -> List[str]:
        """提取政策要点"""
        key_points = []
        lines = content.split('\n')

        for line in lines:
            if '要点' in line or '重点' in line or '关键' in line:
                line = line.strip('-*• ')
                if len(line) > 5:
                    key_points.append(line)

        return key_points[:5]

    def _extract_suggestions(self, content: str) -> List[str]:
        """提取建议"""
        suggestions = []
        lines = content.split('\n')

        for line in lines:
            if '建议' in line or '注意' in line or '提醒' in line:
                line = line.strip('-*• ')
                if len(line) > 5:
                    suggestions.append(line)

        return suggestions[:5]

    def _generate_policy_answer(self, prompt: str) -> str:
        """生成政策相关回答（备用）"""
        return """根据云南省中考政策，我为您提供以下解读：

1. **指标到校政策**：优质普通高中会将一定比例的招生名额分配到初中学校，促进教育公平。

2. **定向生政策**：针对农村和山区学生，部分学校会降分录取，降分幅度一般在20-30分。

3. **志愿填报**：采用平行志愿方式，建议按照"冲稳保"策略填报。

4. **录取规则**：按照分数优先、遵循志愿的原则进行录取。

建议您关注当地教育局发布的最新政策文件，以获取准确信息。"""

    def _generate_volunteer_answer(self, prompt: str) -> str:
        """生成志愿填报相关回答（备用）"""
        return """关于志愿填报，我建议您：

**填报策略**：
1. **冲一冲**：选择1-2所分数略高的学校作为冲刺目标
2. **稳一稳**：选择2-3所分数匹配的学校作为稳妥选择
3. **保一保**：选择1-2所分数较低的学校作为保底

**注意事项**：
- 志愿要有梯度，不要全部填报同一层次的学校
- 考虑学校的地理位置、住宿条件等因素
- 关注学校的招生计划和录取规则
- 了解学校的特色专业和培养方向

建议您根据孩子的实际情况和兴趣爱好，选择最适合的学校。"""

    def _generate_school_answer(self, prompt: str) -> str:
        """生成学校相关回答（备用）"""
        # 尝试从数据库查询相关学校信息
        school_info = self._query_school_from_db(prompt)
        if school_info:
            return school_info
        
        return """关于学校选择，我建议您考虑以下因素：

1. **学校层次**：根据孩子的分数和排名，选择匹配的学校层次
2. **学校特色**：了解学校的办学特色和优势学科
3. **师资力量**：关注学校的师资水平和教学质量
4. **升学率**：参考学校的高考升学率和一本率
5. **地理位置**：考虑学校的地理位置和交通便利性
6. **住宿条件**：如果需要住宿，了解学校的住宿条件

建议您实地考察学校，参加学校的开放日活动，与在校学生和家长交流，获取第一手信息。"""

    def _query_school_from_db(self, prompt: str) -> Optional[str]:
        """从数据库查询学校信息（包含详细信息）"""
        # 首先尝试使用RAG系统检索信息
        from openclaw.rag_system import rag_system
        rag_result = rag_system.rag_pipeline(prompt)
        
        if rag_result['success'] and rag_result['data']['context']:
            # 如果RAG系统找到相关信息，使用RAG的结果
            return rag_result['data']['answer']
        
        # 尝试从缓存获取
        from app.core.cache import api_cache
        cache_key = f"school_query:{prompt}"
        cached_result = api_cache.get(cache_key)
        if cached_result:
            print(f"调试：从缓存获取学校查询结果")
            return cached_result
        
        try:
            print(f"调试：调用_query_school_from_db，prompt={prompt}")
            if not os.path.exists(self.db_path):
                print(f"调试：数据库文件不存在，path={self.db_path}")
                return None
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 获取版本号
            version = 1
            try:
                cursor.execute("""
                    SELECT version FROM version WHERE table_name = 'schools'
                """)
                version_record = cursor.fetchone()
                if version_record:
                    version = version_record[0]
                print(f"调试：schools表版本号={version}")
            except Exception as e:
                print(f"获取版本号失败: {e}")
            
            # 提取关键词
            keywords = self._extract_keywords(prompt)
            print(f"调试：提取的关键词={keywords}")
            if not keywords:
                conn_pool.return_connection(conn)
                return None
            
            # 检查是否是查询校长、历史等详细信息
            is_detail_query = any(kw in prompt for kw in [
                '校长', '历史', '师资', '文化', '特色', '办学', '理念'
            ])
            print(f"调试：is_detail_query={is_detail_query}")
            
            # 构建查询 - 先查基本信息（包含level字段）
            # 优先使用更长的、更具体的关键词
            sorted_keywords = sorted(keywords, key=len, reverse=True)[:3]
            print(f"调试：排序后的关键词={sorted_keywords}")

            results = []
            
            # 特殊处理：昆明第一中学相关查询
            if any(kw in prompt for kw in ["昆明第一中学", "昆一中", "昆明市第一中学"]):
                # 查询昆明市第一中学及其教育集团成员校
                cursor.execute("""
                    SELECT id, name, city, district, school_type, level, is_public, is_key, address, phone, website, description
                    FROM schools
                    WHERE name LIKE ?
                """, ("%昆明市第一中学%",))
                keyword_results = cursor.fetchall()
                print(f"调试：昆明第一中学查询结果={keyword_results}")
                results.extend(keyword_results)
            else:
                # 检查是否有具体学校名称关键词
                specific_school_names = ["云南师范大学附属中学", "昆明市第三中学", "昆明市第八中学", "昆明市第十中学", "师大附中", "云大附中"]
                has_specific_school = any(keyword in specific_school_names for keyword in sorted_keywords)
                
                for keyword in sorted_keywords:
                    # 如果有具体学校名称，只匹配学校名称
                    if has_specific_school:
                        cursor.execute("""
                            SELECT id, name, city, district, school_type, level, is_public, is_key, address, phone, website, description
                            FROM schools
                            WHERE name LIKE ?
                            LIMIT 5
                        """, (f"%{keyword}%",))
                    else:
                        # 对于地区关键词，同时匹配城市
                        cursor.execute("""
                            SELECT id, name, city, district, school_type, level, is_public, is_key, address, phone, website, description
                            FROM schools
                            WHERE name LIKE ? OR city LIKE ?
                            LIMIT 5
                        """, (f"%{keyword}%", f"%{keyword}%"))
                    keyword_results = cursor.fetchall()
                    print(f"调试：关键词 {keyword} 的查询结果={keyword_results}")
                    results.extend(keyword_results)
            
            if not results:
                conn_pool.return_connection(conn)
                return None
            
            # 去重 - 使用字典去重，保留第一个出现的记录
            unique_results_dict = {}
            for result in results:
                # 使用学校名称作为去重键
                school_name = result[1]
                if school_name not in unique_results_dict:
                    unique_results_dict[school_name] = result
            unique_results = list(unique_results_dict.values())
            print(f"调试：去重后的结果={unique_results}")
            
            # 如果是详细查询，尝试获取详细信息
            if is_detail_query and unique_results:
                school_id = unique_results[0][0]
                school_name = unique_results[0][1]
                print(f"调试：详细查询，school_id={school_id}, school_name={school_name}")
                
                # 查询详细信息
                cursor.execute("""
                    SELECT founded_year, school_history, school_culture,
                           current_principal, principal_background, teacher_count,
                           special_teachers, honor_titles, update_time
                    FROM school_details 
                    WHERE school_id = ?
                """, (school_id,))
                
                detail_row = cursor.fetchone()
                print(f"调试：详细信息查询结果={detail_row}")
                
                # 查询校长变更记录
                cursor.execute("""
                    SELECT principal_name, tenure_start, tenure_end, background
                    FROM principal_changes 
                    WHERE school_id = ?
                    ORDER BY tenure_start DESC
                """, (school_id,))
                principal_changes = cursor.fetchall()
                print(f"调试：校长变更记录查询结果={principal_changes}")
            else:
                detail_row = None
                principal_changes = []
            
            conn_pool.return_connection(conn)
            
            # 构建响应
            if is_detail_query and (detail_row or principal_changes):
                # 详细查询响应
                response = f"**{unique_results[0][1]}** 详细信息\n\n"
                
                if detail_row:
                    founded_year, school_history, school_culture, \
                    current_principal, principal_background, teacher_count, \
                    special_teachers, honor_titles, update_time = detail_row
                    
                    if founded_year:
                        response += f"**创办时间**：{founded_year}\n\n"
                    
                    if current_principal:
                        response += f"**现任校长**：{current_principal}\n"
                        if principal_background:
                            response += f"**校长背景**：{principal_background}\n"
                        response += "\n"
                    
                    if school_history:
                        response += f"**办学历史**：\n{school_history}\n\n"
                    
                    if school_culture:
                        response += f"**学校文化**：\n{school_culture}\n\n"
                    
                    if teacher_count:
                        response += f"**师资力量**：现有教职工{teacher_count}人\n\n"
                    
                    if special_teachers:
                        try:
                            teachers = json.loads(special_teachers)
                            if teachers:
                                response += f"**优秀教师**：{', '.join(teachers[:5])}\n\n"
                        except:
                            pass
                    
                    if honor_titles:
                        try:
                            honors = json.loads(honor_titles)
                            if honors:
                                response += f"**荣誉称号**：{', '.join(honors[:3])}\n\n"
                        except:
                            pass
                
                # 添加校长变更记录
                if principal_changes:
                    response += "**校长变更记录**：\n"
                    for i, (name, start, end, bg) in enumerate(principal_changes[:5], 1):
                        tenure = f"{start} - {end}" if end else f"{start} - 至今"
                        response += f"{i}. {name}（{tenure}）"
                        if bg:
                            response += f" - {bg}"
                        response += "\n"
                    response += "\n"
                
                if not detail_row and not principal_changes:
                    response += "⚠️ 暂无该学校的详细信息记录。\n\n"
                
                response += "---\n"
                response += "💡 **提示**：以上信息来源于我们的数据库。如需最新、最准确的信息，建议：\n"
                response += "1. 直接联系学校招生办\n"
                response += "2. 访问学校官方网站\n"
                response += "3. 参加学校开放日活动\n"
                
                # 缓存结果
                api_cache.set(cache_key, response)
                print(f"调试：缓存详细查询响应")
                return response
            
            # 普通查询响应
            response_lines = []
            response_lines.append("根据您的问题，我找到以下相关学校信息：")
            response_lines.append("")
            
            import re
            
            # 检查是否是特殊集团查询
            is_kunming_first = any(kw in prompt for kw in ["昆明第一中学", "昆一中", "昆明市第一中学"])
            
            # 如果是昆明第一中学相关查询，返回所有结果；否则返回前5个
            results_to_show = unique_results if is_kunming_first else unique_results[:5]
            
            for i, (id, name, city, district, school_type, level, is_public, is_key, address, phone, website, description) in enumerate(results_to_show, 1):
                # 清理字符串中的多余空格
                def clean_string(s):
                    if not s:
                        return ''
                    # 去除首尾空格
                    s = str(s).strip()
                    # 使用正则表达式将多个连续的空白字符替换为单个空格
                    s = re.sub(r'\s+', ' ', s)
                    return s
                
                name = clean_string(name)
                city = clean_string(city)
                district = clean_string(district)
                school_type = clean_string(school_type)
                level = clean_string(level)
                address = clean_string(address)
                phone = clean_string(phone)
                description = clean_string(description)
                
                # 确保city不为空
                city_display = city if city else '暂无'
                
                # 构建响应行，使用单个空格
                response_lines.append(f"**{i}. {name}**")
                if level:
                    response_lines.append(f"- 学校等级：{level}")
                response_lines.append(f"- 所在城市：{city_display}")
                if district:
                    response_lines.append(f"- 所属区县：{district}")
                response_lines.append(f"- 学校类型：{school_type if school_type else '暂无'}")
                if address:
                    response_lines.append(f"- 地址：{address}")
                if phone:
                    response_lines.append(f"- 联系方式：{phone}")
                if description:
                    response_lines.append(f"- 学校简介：{description}")
                response_lines.append("")
            
            response_lines.append("")
            response_lines.append("如需了解更多详细信息，请告诉我具体的学校名称。")
            
            # 连接所有行
            response = '\n'.join(response_lines)
            
            # 清理响应字符串中的多余空格
            # 1. 将多个连续空格替换为单个空格
            response = re.sub(r' {2,}', ' ', response)
            # 2. 移除行首的空格
            response = re.sub(r'\n +', '\n', response)
            # 3. 移除行尾的空格
            response = re.sub(r' +\n', '\n', response)
            
            # 缓存结果
            api_cache.set(cache_key, response)
            print(f"调试：缓存普通查询响应")
            print(f"调试：返回普通查询响应")
            return response

        except Exception as e:
            print(f"查询学校信息失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_keywords(self, prompt: str) -> List[str]:
        """从问题中提取关键词"""
        keywords = []
        
        # 特殊处理：昆明第一中学相关查询
        if "昆明第一中学" in prompt or "昆一中" in prompt or "昆明一中" in prompt or "昆一中教育集团" in prompt:
            return ["昆明市第一中学", "昆明"]
        
        # 学校相关关键词映射
        school_keywords = {
            "云大附中": ["云大附中", "云南大学附属"],
            "师大附中": ["师大附中", "云南师范大学附属", "师范大学附属"],
            "昆一中": ["昆一中", "昆明市第一中学", "昆明一中"],
            "昆三中": ["昆三中", "昆明市第三中学", "昆明三中"],
            "昆八中": ["昆八中", "昆明市第八中学", "昆明八中"],
            "昆十中": ["昆十中", "昆明市第十中学", "昆明十中"],
            "昆十二中": ["昆十二中", "昆明市第十二中学", "昆明十二中", "十二中"],
            "昆十四中": ["昆十四中", "昆明市第十四中学", "昆明十四中", "十四中"],
            "曲靖一中": ["曲靖一中", "曲靖市第一中学"],
            "玉溪一中": ["玉溪一中", "玉溪市第一中学"],
            "大理一中": ["大理一中", "大理市第一中学"],
            "红河一中": ["红河一中", "红河州第一中学"],
            "昭通一中": ["昭通一中", "昭通市第一中学"],
            "师大系": ["师范大学附属", "师大附中"],
            "云大系": ["云南大学附属", "云大附中"],
            "未央中学": ["未央中学"],
        }
        
        # 地区关键词
        region_keywords = [
            "昆明", "曲靖", "玉溪", "大理", "红河", "昭通", "楚雄",
            "保山", "普洱", "临沧", "丽江", "文山", "西双版纳",
            "德宏", "怒江", "迪庆"
        ]
        
        # 检查学校关键词
        for key, values in school_keywords.items():
            # 检查键是否在prompt中，或者values中的任何一项在prompt中
            if key in prompt:
                keywords.extend(values)
            else:
                for value in values:
                    if value in prompt:
                        keywords.extend(values)
                        break
        
        # 如果没有提取到关键词，尝试提取可能的学校名称
        if not keywords:
            # 简单的学校名称提取逻辑
            import re
            # 匹配可能的学校名称（包含"学校"、"中学"、"高中"等关键词）
            school_patterns = [
                r'[\u4e00-\u9fa5]+[学校中学高中初中小学]',
                r'[\u4e00-\u9fa5]+未央中学',
            ]
            for pattern in school_patterns:
                matches = re.findall(pattern, prompt)
                keywords.extend(matches)
        
        # 检查地区关键词
        for keyword in region_keywords:
            if keyword in prompt:
                keywords.append(keyword)
        
        # 去重
        keywords = list(set(keywords))
        
        return keywords

    def _generate_general_answer(self, prompt: str) -> str:
        """生成一般性回答（备用）"""
        # 尝试从数据库查询相关学校信息
        school_info = self._query_school_from_db(prompt)
        if school_info:
            return school_info
        
        return """感谢您的提问！关于云南中考择校，我可以为您提供以下帮助：

1. **政策解读**：解答中考政策相关问题
2. **学校推荐**：根据孩子的分数和排名推荐适合的学校
3. **志愿填报**：提供志愿填报策略和建议
4. **学校对比**：对比不同学校的特色和优势

如果您有具体的问题，请详细描述，我会为您提供更有针对性的建议。"""
    
    def _query_admission_scores(self, school_name: str, year: int = None) -> Optional[str]:
        """查询学校录取分数线"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if year:
                cursor.execute('''
                    SELECT school_name, year, score_type, score, rank_start, rank_end, notes
                    FROM admission_scores 
                    WHERE school_name LIKE ? AND year = ?
                    ORDER BY score DESC
                ''', (f'%{school_name}%', year))
            else:
                cursor.execute('''
                    SELECT school_name, year, score_type, score, rank_start, rank_end, notes
                    FROM admission_scores 
                    WHERE school_name LIKE ?
                    ORDER BY year DESC, score DESC
                ''', (f'%{school_name}%',))
            
            results = cursor.fetchall()
            
            # 查询学校代码
            school_code = None
            if results:
                cursor.execute('''
                    SELECT school_code FROM school_codes 
                    WHERE school_name LIKE ?
                    LIMIT 1
                ''', (f'%{school_name}%',))
                code_row = cursor.fetchone()
                if code_row:
                    school_code = code_row[0]
            
            conn_pool.return_connection(conn)
            
            if not results:
                return None
            
            # 构建响应
            response = f"**{results[0][0]}**"
            if school_code:
                response += f"（学校代码：**{school_code}**）"
            response += " 近年录取分数线：\n\n"
            response += "| 年份 | 录取类型 | 分数 | 排名范围 |\n"
            response += "|------|----------|------|----------|\n"
            
            for row in results[:10]:  # 最多显示10条
                school, yr, score_type, score, rank_start, rank_end, notes = row
                rank_range = f"{rank_start}-{rank_end}" if rank_start and rank_end else "-"
                response += f"| {yr} | {score_type} | {score} | {rank_range} |\n"
            
            # 添加2026年预测
            prediction = self._predict_2026_score(results)
            if prediction:
                response += f"\n**2026年预测分数线**：\n"
                response += f"- 统招择优：约 **{prediction['tongzhao']}分**（参考近3年趋势）\n"
                response += f"- 定向择优：约 **{prediction['dingxiang']}分**\n"
                response += f"\n> 注：预测仅供参考，实际分数线以官方公布为准。\n"
            
            return response
            
        except Exception as e:
            print(f"查询录取分数线失败: {e}")
            return None
    
    def _analyze_score_for_school(self, score: float, school_name: str) -> Optional[str]:
        """分析分数是否能上某学校"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 查询该校最近一年的录取分数线
            cursor.execute('''
                SELECT school_name, year, score_type, score, rank_start, rank_end
                FROM admission_scores 
                WHERE school_name LIKE ?
                ORDER BY year DESC, score DESC
                LIMIT 3
            ''', (f'%{school_name}%',))
            
            results = cursor.fetchall()
            conn_pool.return_connection(conn)
            
            if not results:
                return None
            
            # 分析分数
            latest_year = results[0][1]
            tongzhao_score = None
            dingxiang_score = None
            
            for row in results:
                if row[2] == '统招择优':
                    tongzhao_score = row[3]
                elif row[2] == '定向择优':
                    dingxiang_score = row[3]
            
            analysis = f"**分数分析（{score}分）**\n\n"
            analysis += f"参考{latest_year}年录取数据：\n"
            
            if tongzhao_score:
                diff = score - tongzhao_score
                if diff >= 0:
                    analysis += f"- ✅ **统招择优线 {tongzhao_score}分**：您的分数高出 {diff} 分，录取概率**很大**\n"
                elif diff >= -10:
                    analysis += f"- ⚠️ **统招择优线 {tongzhao_score}分**：您的分数低 {abs(diff)} 分，有一定风险，但征集志愿有机会\n"
                else:
                    analysis += f"- ❌ **统招择优线 {tongzhao_score}分**：您的分数低 {abs(diff)} 分，统招录取困难\n"
            
            if dingxiang_score:
                diff = score - dingxiang_score
                if diff >= 0:
                    analysis += f"- ✅ **定向择优线 {dingxiang_score}分**：您的分数高出 {diff} 分，定向录取概率大\n"
            
            return analysis
            
        except Exception as e:
            print(f"分析分数失败: {e}")
            return None
    
    def _check_school_rename(self, school_name: str) -> Optional[str]:
        """检查学校是否更名"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT new_name FROM school_renames 
                WHERE old_name = ?
                LIMIT 1
            ''', (school_name,))
            
            row = cursor.fetchone()
            conn_pool.return_connection(conn)
            
            if row:
                return row[0]
            
            return None
            
        except Exception as e:
            print(f"检查学校更名失败: {e}")
            return None
    
    def _predict_2026_score(self, results: list) -> Optional[dict]:
        """预测2026年分数线"""
        try:
            tongzhao_scores = []
            dingxiang_scores = []
            
            for row in results:
                if row[2] == '统招择优':
                    tongzhao_scores.append((row[1], row[3]))  # (year, score)
                elif row[2] == '定向择优':
                    dingxiang_scores.append((row[1], row[3]))
            
            if not tongzhao_scores:
                return None
            
            tongzhao_scores.sort(key=lambda x: x[0], reverse=True)
            dingxiang_scores.sort(key=lambda x: x[0], reverse=True)
            
            if len(tongzhao_scores) >= 2:
                recent_avg = sum(s[1] for s in tongzhao_scores[:3]) / min(3, len(tongzhao_scores))
                trend = tongzhao_scores[0][1] - tongzhao_scores[-1][1] if len(tongzhao_scores) >= 2 else 0
                predicted_tongzhao = int(recent_avg + trend * 0.3)
            else:
                predicted_tongzhao = int(tongzhao_scores[0][1] + 2)
            
            if dingxiang_scores:
                if len(dingxiang_scores) >= 2:
                    recent_avg = sum(s[1] for s in dingxiang_scores[:3]) / min(3, len(dingxiang_scores))
                    trend = dingxiang_scores[0][1] - dingxiang_scores[-1][1] if len(dingxiang_scores) >= 2 else 0
                    predicted_dingxiang = int(recent_avg + trend * 0.3)
                else:
                    predicted_dingxiang = int(dingxiang_scores[0][1] + 2)
            else:
                predicted_dingxiang = predicted_tongzhao - 10
            
            return {
                'tongzhao': predicted_tongzhao,
                'dingxiang': predicted_dingxiang
            }
            
        except Exception as e:
            print(f"预测2026分数线失败: {e}")
            return None

# 创建全局LLM服务实例
llm_service = LLMService()
