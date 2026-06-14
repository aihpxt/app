#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能响应生成器
支持自然、流畅的对话响应，避免模式化回答
"""

import logging
import random
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SmartResponseGenerator:
    """智能响应生成器 - 增强版（集成个性化引擎和知识图谱）"""
    
    def __init__(self):
        # 导入个性化引擎
        try:
            from .personalization_engine import get_personalization_engine
            self._personalization_engine = get_personalization_engine()
        except ImportError:
            self._personalization_engine = None
        
        # 导入知识图谱服务
        try:
            from .knowledge_graph_service import get_knowledge_graph_service
            self._knowledge_graph_service = get_knowledge_graph_service()
        except ImportError:
            self._knowledge_graph_service = None
        
        # 响应模板库 - 扩展版
        self._templates = {
            # 基础对话
            'greeting': [
                '你好！我是云南省中考智能助手，很高兴为你服务！',
                '您好！我是小智，请问有什么可以帮助你的吗？',
                '嗨！很高兴见到你，我可以帮你解答中考相关问题哦！',
                '你好呀！需要了解中考择校、招生政策还是学习计划呢？',
                '哈喽！准备好迎接中考挑战了吗？我可以帮你制定策略！',
                '你好！欢迎咨询中考相关问题，我来帮你解答！',
                '嗨！我是你的中考智能助手，有什么问题尽管问！',
                '您好呀！中考备考路上，我来陪你一起加油！',
                '嘿！需要关于中考的帮助吗？我很乐意为你服务！',
                '你好！无论遇到什么问题，我都会尽力帮你解决！'
            ],
            'farewell': [
                '再见！祝你中考顺利！',
                '拜拜！有问题随时来找我！',
                '再见啦，祝你金榜题名！',
                '加油！期待你的好消息！',
                '祝你学习进步，考试顺利！',
                '再见！好好复习，相信你一定可以！',
                '拜拜！记得劳逸结合，保持好心态！',
                '再见！愿你旗开得胜，马到成功！',
                '拜拜啦！相信自己，你是最棒的！',
                '再见！祝你前程似锦，未来可期！'
            ],
            'thanks': [
                '不客气！能帮到你我很高兴！',
                '不用谢！祝你学习进步！',
                '这是我应该做的，加油！',
                '😊 不客气，祝你中考取得好成绩！',
                '不用客气，有问题随时找我！',
                '很高兴能帮到你！继续加油！',
                '不客气！祝你梦想成真！',
                '😊 能帮到你真是太好了，继续加油哦！',
                '不用谢！相信你的努力一定会有回报！',
                '这是我应该做的，祝你一切顺利！'
            ],
            
            # 择校相关
            'school_selection_missing_info': [
                '好的！我来帮你分析中考择校问题。为了给你提供准确的建议，请告诉我：',
                '没问题！要帮你分析择校情况，我需要了解一些信息：',
                '好的，我来帮你看看。首先想了解一下：',
                '当然可以！为了给你最合适的建议，我想知道：',
                '没问题！让我先了解一下你的情况：',
                '好的！要帮你择校，我需要知道一些信息：',
                '明白！我来帮你分析，需要一些信息：',
                '好的！让我帮你规划，先了解一下基本情况：'
            ],
            'school_selection_info_available': [
                '好的！我来帮你分析{district}的择校情况。根据云南省招生政策，{district}的考生通常可以报考本地优质高中、省级重点中学和民办优质高中。',
                '明白了！{district}的择校选择挺多的，我来给你分析分析：',
                '好的，{district}的情况我了解。让我来帮你看看有哪些合适的选择：',
                '知道了！{district}的考生在择校上有不少优势，我来帮你梳理一下：',
                '了解！{district}有不少优质高中，我来帮你分析：',
                '清楚了！{district}的高中资源很丰富，我来帮你推荐：',
                '好的！{district}的学校情况我很熟悉，让我来帮你分析：'
            ],
            
            # 推荐相关
            'recommendation_request': [
                '好的！我来给你推荐合适的学校。',
                '没问题！我来帮你找找看。',
                '当然可以！让我来帮你推荐。',
                '好的，我来分析一下，给你推荐几所合适的学校。',
                '没问题！我来帮你挑选适合的学校。',
                '好的！我来根据你的情况推荐最合适的学校：',
                '当然！我来帮你找到最适合的学校：',
                '没问题！让我来帮你推荐几所不错的学校。'
            ],
            
            # 政策相关
            'policy_info': [
                '好的！我来帮你了解中考招生政策。',
                '没问题！关于招生政策，你想了解哪方面？',
                '好的，招生政策我很熟悉，请问你想了解哪方面？',
                '当然可以！招生政策方面我可以帮你解答。',
                '好的！招生政策包含很多方面，你想了解哪一块？',
                '明白！招生政策挺复杂的，我来帮你梳理：',
                '没问题！我来帮你解读招生政策：'
            ],
            
            # 学习计划相关
            'study_plan': [
                '好的！我来帮你制定学习计划。',
                '没问题！让我来帮你规划一下学习时间。',
                '当然可以！学习计划很重要，我来帮你制定。',
                '好的，我来帮你制定一个高效的学习计划。',
                '没问题！让我根据你的情况帮你规划学习。',
                '好的！我来帮你设计一个科学的学习计划：',
                '当然！让我来帮你规划备考时间：'
            ],
            
            # 情感支持
            'emotional_support_positive': [
                '😊 很高兴听到你这么说！继续保持！',
                '太棒了！保持这份积极的心态！',
                '👍 好样的！继续加油！',
                '很高兴你能这么想，继续保持！',
                '👏 太棒了！继续保持这种状态！',
                '😊 不错！继续努力！',
                '🎉 太棒了！继续保持这份热情！',
                '💪 好样的！相信你一定可以！',
                '🌟 太棒了！继续加油哦！',
                '😊 很高兴看到你这么积极！继续保持！'
            ],
            'emotional_support_negative': [
                '💝 我理解你的感受，备考确实会有压力。不过请放心，只要合理规划，一定可以的！',
                '😔 压力大是正常的，每个人都会经历。我们可以一起制定计划，减轻压力。',
                '别担心，很多同学都有类似的感受。让我们一起想办法克服！',
                '我能感受到你的焦虑，这是正常的。让我们一起制定策略，一步一步来！',
                '💪 别灰心，困难只是暂时的，我们一起加油！',
                '我理解你的担忧，但请相信自己，你已经很棒了！',
                '💝 压力是成长的动力，让我们一起面对！',
                '别担心，我会陪你一起度过这段时光！',
                '💪 相信自己，你比想象中更强大！',
                '😊 困难只是暂时的，坚持下去就是胜利！'
            ],
            
            # 追问模板
            'ask_for_score': [
                '为了给你更准确的建议，我需要了解一下你目前的成绩大概在什么水平？',
                '想问问你目前的预估分数大概是多少呢？',
                '方便告诉我你现在的成绩大概是多少吗？',
                '想了解一下你目前的分数情况，可以告诉我吗？',
                '请问你目前的预估分数是多少呢？',
                '为了更精准的分析，能告诉我你的分数吗？',
                '想知道你现在大概能考多少分？'
            ],
            'ask_for_district': [
                '为了给你准确的建议，请告诉我你的户籍所在地是哪个区县？',
                '想知道你来自哪个区县，可以告诉我吗？',
                '方便告诉我你是哪个区县的考生吗？',
                '想了解一下你的户籍所在地，是哪个区县呢？',
                '请问你是哪个区县的考生？',
                '为了提供准确的信息，能告诉我你所在的区县吗？',
                '想知道你来自哪个地区？'
            ],
            'ask_for_grade': [
                '请问你目前在读几年级呢？',
                '想知道你现在是几年级了？',
                '方便告诉我你目前的年级吗？',
                '想了解一下你在读几年级，可以告诉我吗？',
                '你现在是几年级的学生呢？',
                '为了更好地帮助你，能告诉我你现在几年级吗？'
            ],
            'ask_for_school_type': [
                '你更倾向于报考公办学校还是民办学校呢？',
                '在选择学校时，你更看重公办还是民办？',
                '你有考虑过公办学校还是民办学校吗？',
                '想了解一下，你更倾向于哪种类型的学校？'
            ],
            
            # 录取概率相关
            'admission_probability': [
                '好的！我来帮你分析录取概率。为了给你准确的评估，我需要知道：',
                '没问题！想帮你分析录取可能性，需要一些信息：',
                '好的！让我帮你评估一下录取机会。我需要了解：',
                '当然可以！我来帮你分析录取概率。请告诉我：',
                '好的！我来帮你评估录取机会，需要一些信息：'
            ],
            
            # 学校对比相关
            'school_compare': [
                '好的！我来帮你对比学校。你想对比哪几所学校呢？',
                '没问题！让我帮你比较学校。请告诉我想对比哪些学校：',
                '当然可以！学校对比很重要，你想比较哪几所？',
                '好的！我来帮你分析学校差异。请说出你想对比的学校：',
                '没问题！让我来帮你对比分析，你想比较哪些学校？'
            ],
            
            # 学费相关
            'tuition_info': [
                '好的！我来帮你了解学费信息。你想了解哪所学校的学费？',
                '没问题！关于学费，你想了解哪方面？',
                '当然可以！学费信息我可以帮你查询。请问是哪所学校？',
                '好的！我来帮你了解收费情况。你想知道哪所学校的费用？',
                '没问题！让我帮你查询学费信息，是哪所学校呢？'
            ],
            
            # 学校信息详情
            'school_detail': [
                '{school_name}是{school_type}，位于{location}。学校{features}，{rate_info}，学费{tuition}元/学期。',
                '{school_name}是{school_type}中学，{location}。学校以{features}著称，{rate_info}，学费适中。',
                '{school_name}是一所{school_type}学校，位于{location}。学校{features}，{rate_info}。',
                '{school_name}是{school_type}，位于{location}，{features}，{rate_info}。'
            ],
            
            # 政策详情
            'policy_detail': [
                '关于{policy_name}，{description}。主要要点包括：{key_points}',
                '{policy_name}的相关规定是：{description}。具体包括：{key_points}',
                '{policy_name}：{description}。关键点有：{key_points}'
            ],
            
            # 默认响应
            'default': [
                '好的，我来帮你看看。',
                '没问题，我来帮你解答。',
                '好的，让我来分析一下。',
                '当然可以，我来帮你。',
                '好的！我来帮你解答。',
                '明白！我来帮你处理。',
                '没问题！我来帮你分析。'
            ]
        }
        
        # 自然语言模式
        self._natural_patterns = {
            'school_selection': [
                '我想选学校',
                '帮我看看高中',
                '想报考中学',
                '该怎么填志愿',
                '志愿怎么报',
                '选哪个学校好',
                '帮我推荐学校',
                '如何选择高中',
                '中考志愿怎么填',
                '如何报考高中'
            ],
            'recommendation': [
                '给我推荐一下',
                '哪个比较好',
                '推荐几所学校',
                '帮我选一下',
                '哪个更适合我',
                '哪所学校好',
                '适合我的学校',
                '推荐合适的学校'
            ],
            'question': [
                '这个是什么',
                '为什么这样',
                '怎么回事',
                '能不能解释一下',
                '这是什么意思',
                '什么是',
                '为什么',
                '怎么样',
                '好不好'
            ]
        }
        
        logger.info("智能响应生成器初始化完成（扩展版）")
    
    def generate_response(self, intent: str, sentiment: str, 
                          user_profile: Optional[Dict] = None, 
                          context: Optional[List[Dict]] = None,
                          semantic_result: Optional[Dict] = None) -> str:
        """
        生成智能响应（增强版，支持语义分析结果、个性化和知识图谱）
        
        Args:
            intent: 用户意图
            sentiment: 用户情感
            user_profile: 用户画像
            context: 对话上下文
            semantic_result: 语义分析结果（包含同义词、指代消解、多意图等）
        
        Returns:
            响应文本
        """
        response = ""
        
        # 根据意图选择响应
        if intent == 'greeting':
            response = self._pick_random('greeting')
        
        elif intent == 'farewell':
            response = self._pick_random('farewell')
        
        elif intent == 'thanks':
            response = self._pick_random('thanks')
        
        elif intent == 'school_selection':
            response = self._handle_school_selection(user_profile)
        
        elif intent == 'recommendation':
            response = self._handle_recommendation(user_profile, semantic_result)
        
        elif intent == 'policy':
            response = self._handle_policy(user_profile, semantic_result)
        
        elif intent == 'study_plan':
            response = self._handle_study_plan(user_profile)
        
        elif intent == 'emotional':
            response = self._handle_emotional(sentiment)
        
        elif intent == 'question':
            response = self._handle_question(context, semantic_result)
        
        elif intent == 'score':
            response = self._handle_score(user_profile)
        
        elif intent == 'school_info':
            response = self._handle_school_info(user_profile, semantic_result)
        
        elif intent == 'exam':
            response = self._handle_exam()
        
        elif intent == 'admission_probability':
            response = self._handle_admission_probability(user_profile, semantic_result)
        
        elif intent == 'school_compare':
            response = self._handle_school_compare(semantic_result)
        
        elif intent == 'tuition':
            response = self._handle_tuition(semantic_result)
        
        else:
            response = self._pick_random('default')
        
        # 应用个性化处理
        if self._personalization_engine and user_profile:
            response, _ = self._personalization_engine.personalize_response(
                response, 
                'session',
                user_profile,
                context
            )
        
        return response
    
    def _pick_random(self, template_key: str) -> str:
        """随机选择一个模板"""
        templates = self._templates.get(template_key, [])
        if templates:
            return random.choice(templates)
        return "好的，我来帮你看看。"
    
    def _handle_school_selection(self, user_profile: Optional[Dict]) -> str:
        """处理择校相关问题 - 增强版，支持生成完整志愿方案"""
        district = user_profile.get('district') if user_profile else None
        score = user_profile.get('score') if user_profile else None
        
        # 如果既有分数又有地区，直接生成完整志愿方案
        if score and district:
            return self._generate_volunteer_plan(score, district)
        
        if district:
            template = self._pick_random('school_selection_info_available')
            response = template.format(district=district)
            response += "\n\n为了给你更准确的建议，" + self._pick_random('ask_for_score')
        else:
            response = self._pick_random('school_selection_missing_info')
            response += "\n1. 你的户籍所在地是哪个区县？\n2. 你目前的成绩大概在什么水平？"
        
        return response
    
    def _generate_volunteer_plan(self, score: int, district: str) -> str:
        """生成完整的中考志愿填报方案"""
        # 标准化地区名称
        display_district = district
        if '昆明' in district:
            display_district = '昆明市'
        
        # 根据分数段推荐学校
        response = f"🎯 **中考志愿填报方案**\n\n"
        response += f"📊 **考生信息**：{display_district}考生，预估分数{score}分\n\n"
        
        # 定义昆明的优质高中及其录取分数参考
        kunming_high_schools = [
            {"name": "云南师范大学附属中学", "type": "一级一等", "score_low": 660, "score_high": 690, "address": "昆明市五华区东风西路484号", "feature": "云南省顶尖高中，一本率近100%"},
            {"name": "昆明市第一中学", "type": "一级一等", "score_low": 650, "score_high": 680, "address": "昆明市五华区西昌路233号", "feature": "百年名校，一本率95%以上"},
            {"name": "昆明市第三中学", "type": "一级一等", "score_low": 640, "score_high": 670, "address": "昆明市呈贡区惠通路6号", "feature": "教学质量高，一本率90%以上"},
            {"name": "昆明市第八中学", "type": "一级一等", "score_low": 620, "score_high": 650, "address": "昆明市五华区龙泉路628号", "feature": "学风优良，一本率85%以上"},
            {"name": "云南大学附属中学", "type": "一级一等", "score_low": 630, "score_high": 660, "address": "昆明市五华区一二一大街226号", "feature": "民办名校，一本率88%以上"},
            {"name": "昆明市第十中学", "type": "一级一等", "score_low": 600, "score_high": 630, "address": "昆明市盘龙区白塔路247号", "feature": "教学严谨，一本率80%以上"},
            {"name": "昆明市第十四中学", "type": "一级一等", "score_low": 580, "score_high": 610, "address": "昆明市五华区黑林铺前街79号", "feature": "管理严格，一本率75%以上"},
            {"name": "昆明市官渡区第一中学", "type": "一级二等", "score_low": 560, "score_high": 590, "address": "昆明市官渡区官渡街道云秀社区", "feature": "区域名校，一本率65%以上"}
        ]
        
        # 根据分数筛选合适的学校
        reach_schools = []   # 冲刺学校
        match_schools = []   # 匹配学校
        safe_schools = []    # 保底学校
        
        for school in kunming_high_schools:
            if score >= school['score_low'] - 10 and score <= school['score_high'] + 5:
                if score < school['score_low']:
                    reach_schools.append(school)
                elif score >= school['score_low'] and score <= school['score_high']:
                    match_schools.append(school)
                else:
                    safe_schools.append(school)
            elif score > school['score_high'] + 5:
                safe_schools.append(school)
            elif score >= school['score_low'] - 20:
                match_schools.append(school)
        
        # 生成志愿建议
        response += "📋 **志愿填报建议（冲稳保策略）**\n\n"
        
        # 冲刺志愿
        if reach_schools:
            response += "🔝 **第一志愿（冲刺）**\n"
            for school in reach_schools[:2]:
                response += f"  • {school['name']}（{school['type']}）\n"
                response += f"    - 地址：{school['address']}\n"
                response += f"    - 特色：{school['feature']}\n"
                response += f"    - 录取参考：{school['score_low']}-{school['score_high']}分\n\n"
        elif match_schools:
            # 如果没有冲刺学校，用匹配学校的第一个作为冲刺
            response += "🔝 **第一志愿（冲刺）**\n"
            response += f"  • {match_schools[0]['name']}（{match_schools[0]['type']}）\n"
            response += f"    - 地址：{match_schools[0]['address']}\n"
            response += f"    - 特色：{match_schools[0]['feature']}\n"
            response += f"    - 录取参考：{match_schools[0]['score_low']}-{match_schools[0]['score_high']}分\n\n"
        
        # 匹配志愿
        if match_schools:
            response += "✅ **第二志愿（稳妥）**\n"
            for school in match_schools[:2]:
                response += f"  • {school['name']}（{school['type']}）\n"
                response += f"    - 地址：{school['address']}\n"
                response += f"    - 特色：{school['feature']}\n"
                response += f"    - 录取参考：{school['score_low']}-{school['score_high']}分\n\n"
        
        # 保底志愿
        if safe_schools:
            response += "🛡️ **第三志愿（保底）**\n"
            for school in safe_schools[-2:]:
                response += f"  • {school['name']}（{school['type']}）\n"
                response += f"    - 地址：{school['address']}\n"
                response += f"    - 特色：{school['feature']}\n"
                response += f"    - 录取参考：{school['score_low']}-{school['score_high']}分\n\n"
        
        # 添加填报注意事项
        response += "📝 **填报注意事项**\n"
        response += "  1. 注意填报顺序，把最想上的学校放在前面\n"
        response += "  2. 了解学校近3年录取分数线的变化趋势\n"
        response += "  3. 考虑学校的地理位置和交通便利性\n"
        response += "  4. 关注学校的特色专业和优势学科\n"
        response += "  5. 参考往年同分段学生的录取情况\n"
        response += "  6. 了解学校的招生计划和政策变化\n\n"
        
        # 添加常见误区提醒
        response += "⚠️ **常见误区提醒**\n"
        response += "  1. 不要只填一个志愿，浪费宝贵的志愿机会\n"
        response += "  2. 不要盲目追求名校，忽略与自己分数的匹配度\n"
        response += "  3. 一定要了解学校的调剂政策和规则\n"
        response += "  4. 不要忽视民办学校，有些民办学校教学质量也很高\n\n"
        
        response += "💡 **温馨提示**：以上建议仅供参考，具体请以当年的招生政策和学校公布的分数线为准。"
        
        return response
    
    def _handle_recommendation(self, user_profile: Optional[Dict], 
                               semantic_result: Optional[Dict]) -> str:
        """处理推荐请求（集成知识图谱）"""
        response = self._pick_random('recommendation_request')
        
        district = user_profile.get('district') if user_profile else None
        score = user_profile.get('score') if user_profile else None
        
        # 如果有知识图谱服务且信息充足，直接推荐
        if self._knowledge_graph_service and district and score:
            try:
                # 获取该地区的学校
                schools = self._knowledge_graph_service.query_school_by_location(district)
                
                if schools:
                    response += f"\n\n📍 根据你的情况（{district}，{score}分），我为你推荐以下学校：\n\n"
                    
                    # 筛选适合分数的学校
                    suitable_schools = []
                    for school in schools:
                        base_score = 650 if school['type'] == '省级重点' else 600
                        if score >= base_score - 50:
                            suitable_schools.append(school)
                    
                    if suitable_schools:
                        for i, school in enumerate(suitable_schools[:3], 1):
                            response += f"{i}. **{school['name']}**\n"
                            response += f"   - 类型：{school['type']}\n"
                            response += f"   - 位置：{school['location']}\n"
                            response += f"   - 特色：{', '.join(school['features'])}\n"
                            response += f"   - 一本率：{school['rate_一本']}%\n\n"
                    else:
                        response += "暂时没有找到完全匹配的学校，建议你提供更多信息。\n"
                
                return response
            except Exception as e:
                logger.error(f"知识图谱查询失败: {e}")
        
        # 如果信息不足，继续追问
        if district:
            response += f"\n📍 已知你来自{district}"
        
        if not score:
            response += "\n\n" + self._pick_random('ask_for_score')
        
        return response
    
    def _handle_policy(self, user_profile: Optional[Dict], 
                       semantic_result: Optional[Dict]) -> str:
        """处理政策查询（集成知识图谱）"""
        # 尝试从语义分析结果中提取政策关键词
        entities = semantic_result.get('entities', []) if semantic_result else []
        policy_keywords = ['分数线', '录取', '志愿', '加分', '政策']
        
        target_policy = None
        for entity in entities:
            for keyword in policy_keywords:
                if keyword in entity:
                    target_policy = keyword
                    break
        
        # 如果有知识图谱服务，查询政策信息
        if self._knowledge_graph_service and target_policy:
            policy = self._knowledge_graph_service.query_policy(target_policy)
            if policy:
                response = f"📋 **{target_policy}**\n\n"
                response += f"{policy.get('description', '')}\n\n"
                response += "**主要要点：**\n"
                for i, point in enumerate(policy.get('key_points', []), 1):
                    response += f"{i}. {point}\n"
                return response
        
        response = self._pick_random('policy_info')
        
        # 如果有用户画像信息，个性化响应
        district = user_profile.get('district') if user_profile else None
        if district:
            response += f"\n📍 已知你来自{district}"
        
        return response
    
    def _handle_study_plan(self, user_profile: Optional[Dict]) -> str:
        """处理学习计划"""
        response = self._pick_random('study_plan')
        grade = user_profile.get('grade') if user_profile else None
        
        if grade:
            response += f"\n📌 已知你在读{grade}"
            
            # 根据年级提供不同建议
            if grade == '九年级':
                response += "\n\n⏰ **九年级备考重点：**\n"
                response += "• 系统复习所有知识点\n"
                response += "• 多做模拟题，熟悉考试形式\n"
                response += "• 重点突破薄弱科目\n"
                response += "• 调整心态，保持良好状态\n"
            elif grade == '八年级':
                response += "\n\n📚 **八年级准备建议：**\n"
                response += "• 打好基础，巩固知识点\n"
                response += "• 培养良好学习习惯\n"
                response += "• 了解中考考试科目和形式\n"
                response += "• 开始制定长期备考计划\n"
        
        response += "\n\n请问你目前最想提升哪个科目？或者有什么具体的时间安排需求吗？"
        
        return response
    
    def _handle_emotional(self, sentiment: str) -> str:
        """处理情感表达"""
        if sentiment == 'positive':
            response = self._pick_random('emotional_support_positive')
        elif sentiment == 'negative':
            response = self._pick_random('emotional_support_negative')
        else:
            response = "我能理解你的感受，有什么需要帮助的吗？"
        
        return response
    
    def _handle_question(self, context: Optional[List[Dict]], 
                         semantic_result: Optional[Dict]) -> str:
        """处理问题意图（集成知识图谱）"""
        # 尝试从语义分析结果中提取实体
        entities = semantic_result.get('entities', []) if semantic_result else []
        
        # 如果有学校实体，查询学校信息
        if self._knowledge_graph_service:
            for entity in entities:
                if '中学' in entity or '学校' in entity or '高中' in entity:
                    school = self._knowledge_graph_service.query_school(entity)
                    if school:
                        return self._format_school_info(school)
        
        # 有上下文，尝试理解上下文相关问题
        if context and len(context) > 2:
            recent_content = " ".join([msg.get('content', '') for msg in context[-3:]])
            
            if '学校' in recent_content or '高中' in recent_content:
                return "关于学校的问题，你想了解哪方面呢？比如录取分数线、学校特色、地理位置等。"
            elif '政策' in recent_content or '招生' in recent_content:
                return "关于招生政策，你想了解录取规则、加分政策还是志愿填报流程呢？"
            elif '学习' in recent_content or '计划' in recent_content:
                return "关于学习计划，你想了解时间安排、复习策略还是各科学习方法呢？"
        
        return "好的，请问你有什么问题呢？我可以帮你解答中考相关的各种问题。"
    
    def _format_school_info(self, school: Dict[str, Any]) -> str:
        """格式化学校信息"""
        features = ", ".join(school.get('features', []))
        rate_info = f"一本率{school.get('rate_一本', 0)}%，本科率{school.get('rate_本科', 0)}%"
        
        response = f"🏫 **{school['name']}**\n\n"
        response += f"📌 **学校类型**：{school['type']}\n"
        response += f"📍 **地理位置**：{school['location']}\n"
        response += f"✨ **学校特色**：{features}\n"
        response += f"📊 **升学情况**：{rate_info}\n"
        response += f"💰 **学费**：{school.get('tuition', 0)}元/学期\n"
        response += f"📞 **联系电话**：{school.get('phone', '未提供')}\n"
        response += f"🏠 **学校地址**：{school.get('address', '未提供')}\n"
        
        return response
    
    def _handle_score(self, user_profile: Optional[Dict]) -> str:
        """处理分数相关问题"""
        score = user_profile.get('score') if user_profile else None
        
        if score:
            try:
                score_val = int(score)
                
                # 使用知识图谱提供更精准的分析
                if self._knowledge_graph_service:
                    # 获取学校统计信息
                    stats = self._knowledge_graph_service.get_school_statistics()
                    
                    if score_val >= 650:
                        response = f"🎉 {score}分很不错！这个分数可以冲刺省级重点中学（如师大附中、昆一中等）！"
                        response += f"\n\n📊 参考信息：全省平均一本率约{stats.get('avg_rate_一本', 0)}%，你的分数处于上游水平！"
                    elif score_val >= 600:
                        response = f"👍 {score}分不错！可以考虑州市级重点中学！"
                        response += f"\n\n建议关注{stats.get('total_schools', 0)}所本地优质高中的招生信息。"
                    elif score_val >= 550:
                        response = f"💪 {score}分还可以！继续努力，冲刺更好的学校！"
                        response += "\n\n建议合理填报志愿，结合定向生政策增加录取机会。"
                    else:
                        response = f"📚 {score}分需要加油！制定好学习计划，还有提升空间！"
                        response += "\n\n建议重点突破薄弱科目，针对性复习。"
                else:
                    if score_val >= 600:
                        response = f"🎉 {score}分很不错！这个分数可以考虑省级重点中学！"
                    elif score_val >= 550:
                        response = f"👍 {score}分不错！可以考虑州市级重点中学！"
                    elif score_val >= 500:
                        response = f"💪 {score}分还可以！继续努力，冲刺更好的学校！"
                    else:
                        response = f"📚 {score}分需要加油！制定好学习计划，还有提升空间！"
                
                return response
            except:
                return f"好的，我知道你的分数是{score}分。"
        else:
            return self._pick_random('ask_for_score')
    
    def _handle_school_info(self, user_profile: Optional[Dict], 
                            semantic_result: Optional[Dict]) -> str:
        """处理学校信息查询（集成知识图谱）"""
        # 尝试从语义分析结果中提取学校实体
        entities = semantic_result.get('entities', []) if semantic_result else []
        
        if self._knowledge_graph_service:
            for entity in entities:
                school = self._knowledge_graph_service.query_school(entity)
                if school:
                    return self._format_school_info(school)
        
        district = user_profile.get('district') if user_profile else None
        
        if district:
            # 查询该地区的学校
            if self._knowledge_graph_service:
                schools = self._knowledge_graph_service.query_school_by_location(district)
                if schools:
                    response = f"📍 {district}的学校有：\n\n"
                    for i, school in enumerate(schools[:5], 1):
                        response += f"{i}. **{school['name']}** - {school['type']}\n"
                    response += "\n你想了解哪所学校的详细信息？"
                    return response
            
            return f"好的！我来帮你了解{district}的学校信息。你想了解哪所学校呢？"
        else:
            return "好的！我来帮你了解学校信息。你想了解哪所学校？或者你是哪个区县的考生呢？"
    
    def _handle_exam(self) -> str:
        """处理考试相关问题"""
        return """📅 关于中考，你想了解考试时间、考试科目、备考策略还是考场注意事项呢？
        
云南省中考通常在6月中下旬进行，具体安排如下：
• **考试科目**：语文、数学、英语、物理、化学、道德与法治、历史、生物学、地理、体育
• **总分**：700分
• **考试时间**：每年6月16-18日左右

需要我详细介绍哪方面吗？"""
    
    def _handle_admission_probability(self, user_profile: Optional[Dict], 
                                     semantic_result: Optional[Dict]) -> str:
        """处理录取概率相关问题（集成知识图谱推理）"""
        district = user_profile.get('district') if user_profile else None
        score = user_profile.get('score') if user_profile else None
        
        # 尝试从语义分析结果中提取学校实体
        entities = semantic_result.get('entities', []) if semantic_result else []
        target_school = None
        for entity in entities:
            if '中学' in entity or '高中' in entity or '学校' in entity:
                target_school = entity
                break
        
        # 如果信息充足，直接计算录取概率
        if self._knowledge_graph_service and score and target_school:
            probability, explanation = self._knowledge_graph_service.infer_admission_probability(score, target_school)
            response = f"📊 **录取概率分析**\n\n"
            response += f"目标学校：{target_school}\n"
            response += f"你的分数：{score}分\n"
            response += f"录取概率：{probability}%\n\n"
            response += f"💡 {explanation}"
            return response
        
        # 否则继续追问
        response = self._pick_random('admission_probability')
        
        if district:
            response += f"\n📍 已知你来自{district}"
        
        if target_school:
            response += f"\n🏫 目标学校：{target_school}"
        
        if not district:
            response += "\n1. 你的户籍所在地是哪个区县？"
        
        if not score:
            response += "\n" + ("2. " if district else "1. ") + "你目前的预估分数是多少？"
        
        if not target_school:
            response += "\n" + ("3. " if district and score else "2. " if district or score else "1. ") + "你想报考哪所学校？"
        
        return response
    
    def _handle_school_compare(self, semantic_result: Optional[Dict] = None) -> str:
        """处理学校对比相关问题（集成知识图谱）"""
        # 从语义分析结果中提取学校实体
        entities = semantic_result.get('entities', []) if semantic_result else []
        schools = [e for e in entities if '中学' in e or '高中' in e or '学校' in e]
        
        # 如果有知识图谱服务且有至少2所学校，进行对比
        if self._knowledge_graph_service and len(schools) >= 2:
            comparison = self._knowledge_graph_service.compare_schools(schools[:2])
            
            if 'error' not in comparison:
                response = f"🔍 **学校对比分析**\n\n"
                
                for school in comparison['schools']:
                    response += f"🏫 **{school['name']}**\n"
                    response += f"   - 类型：{school['type']}\n"
                    response += f"   - 位置：{school['location']}\n"
                    response += f"   - 一本率：{school['rate_一本']}%\n"
                    response += f"   - 本科率：{school['rate_本科']}%\n"
                    response += f"   - 学费：{school['tuition']}元/学期\n"
                    response += f"   - 特色：{', '.join(school['features'])}\n\n"
                
                response += "📊 **对比总结**\n"
                for metric in comparison['comparison_matrix']:
                    metric_name = {
                        'rate_一本': '一本率',
                        'rate_本科': '本科率',
                        'tuition': '学费'
                    }.get(metric['metric'], metric['metric'])
                    response += f"• **{metric_name}**：{metric['best']}领先\n"
                
                return response
        
        # 如果只有1所学校，询问另一所
        if schools and len(schools) == 1:
            return f"好的！我知道你想了解{schools[0]}，还想对比哪所学校呢？"
        
        response = self._pick_random('school_compare')
        return response
    
    def _handle_tuition(self, semantic_result: Optional[Dict]) -> str:
        """处理学费相关问题（集成知识图谱）"""
        # 尝试从语义分析结果中提取学校实体
        entities = semantic_result.get('entities', []) if semantic_result else []
        
        if self._knowledge_graph_service:
            for entity in entities:
                school = self._knowledge_graph_service.query_school(entity)
                if school:
                    response = f"💰 **{school['name']}学费信息**\n\n"
                    response += f"学费：{school.get('tuition', 0)}元/学期\n"
                    response += "注：以上为参考学费，具体以学校公布为准。\n"
                    return response
        
        response = self._pick_random('tuition_info')
        return response


# 全局实例
response_generator = SmartResponseGenerator()


def get_response_generator() -> SmartResponseGenerator:
    """获取智能响应生成器实例"""
    return response_generator


if __name__ == '__main__':
    # 测试智能响应生成器
    print("=" * 70)
    print("智能响应生成器测试（扩展版）")
    print("=" * 70)
    
    generator = SmartResponseGenerator()
    
    # 测试不同意图的响应
    test_cases = [
        ('greeting', 'positive', None),
        ('farewell', 'positive', None),
        ('thanks', 'positive', None),
        ('school_selection', 'neutral', {'district': '五华区'}),
        ('school_selection', 'neutral', None),
        ('recommendation', 'positive', {'district': '五华区', 'score': 620}),
        ('recommendation', 'positive', {'district': '五华区'}),
        ('emotional', 'negative', None),
        ('emotional', 'positive', None),
        ('score', 'neutral', {'score': 620}),
        ('school_info', 'neutral', {'district': '五华区'}),
        ('exam', 'neutral', None),
        ('admission_probability', 'neutral', {'district': '五华区', 'score': 620}),
        ('admission_probability', 'neutral', None),
        ('school_compare', 'neutral', None),
        ('tuition', 'neutral', None),
        ('policy', 'neutral', None)
    ]
    
    print("\n📝 测试不同意图的响应：")
    print("-" * 70)
    
    for intent, sentiment, profile in test_cases:
        response = generator.generate_response(intent, sentiment, profile)
        print(f"\n意图: {intent}")
        print(f"情感: {sentiment}")
        print(f"用户画像: {profile}")
        lines = response.split('\n')
        if len(lines) > 3:
            preview = '\n'.join(lines[:3]) + '...'
        else:
            preview = response
        print(f"响应: {preview}")
        print("-" * 70)
    
    print("\n✅ 测试完成！响应生成器工作正常！")
    print("=" * 70)