"""AI相关路由模块"""

from fastapi import APIRouter, Body
from typing import Dict, Any, List
from pydantic import BaseModel

router = APIRouter()


class CompareRequest(BaseModel):
    schoolIds: List[int]
    studentScore: int = None


class SchoolCompareData(BaseModel):
    schoolId: int
    schoolName: str
    schoolType: str
    minScore: int
    minRank: int
    oneRate: float
    boarding: int
    tuition: int
    prefecture: str


class CompareResponse(BaseModel):
    success: bool
    data: Dict[str, Any] = None
    message: str = None


# ==================== 学校对比接口 ====================
@router.post("/compare/schools", response_model=CompareResponse)
async def compare_schools(data: Dict[str, Any] = Body(...)):
    """对比多所学校"""
    try:
        from app.utils.db import get_db_connection
        
        school_ids = data.get('schoolIds', [])
        student_score = data.get('studentScore')
        
        if not school_ids or len(school_ids) < 2:
            return {
                "success": False,
                "message": "请至少选择2所学校进行对比"
            }
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            placeholders = ','.join('?' * len(school_ids))
            query = f"""
                SELECT id, name, type, min_score, min_rank, one_rate, boarding, tuition, prefecture, level, description 
                FROM schools 
                WHERE id IN ({placeholders})
            """
            cursor.execute(query, tuple(school_ids))
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        
        if not rows:
            return {
                "success": False,
                "message": "未找到指定的学校信息"
            }
        
        schools = []
        for row in rows:
            school_dict = dict(zip(columns, row))
            type_name = str(school_dict.get("type") or "普通高中")
            if "重点" in type_name:
                school_type = 2
            elif "民办" in type_name:
                school_type = 4
            else:
                school_type = 1
            
            schools.append({
                "schoolId": school_dict["id"],
                "schoolName": school_dict["name"],
                "schoolType": type_name,
                "typeName": type_name,
                "type": school_type,
                "minScore": school_dict.get("min_score") or 0,
                "minRank": school_dict.get("min_rank") or 0,
                "oneRate": school_dict.get("one_rate") or 0,
                "boarding": "提供" if school_dict["boarding"] else "不提供",
                "tuition": school_dict["tuition"] or 0,
                "style": "适中",
                "nature": "民办" if "民办" in type_name else "公办",
                "features": ["优质教育"] if school_dict["level"] and "一级" in school_dict["level"] else ["标准化教育"],
                "address": school_dict["prefecture"] or "",
                "prefecture": school_dict["prefecture"] or "",
                "level": school_dict["level"] or "",
                "description": school_dict.get("description") or ""
            })
        
        avg_score = sum(s["minScore"] for s in schools) / len(schools)
        avg_rank = sum(s["minRank"] for s in schools) / len(schools)
        avg_rate = sum(s["oneRate"] for s in schools) / len(schools)
        avg_tuition = sum(s["tuition"] for s in schools) / len(schools)
        
        schools_sorted_by_score = sorted(schools, key=lambda x: x["minScore"], reverse=True)
        
        match_results = []
        if student_score:
            for school in schools:
                score_diff = student_score - school["minScore"]
                if score_diff >= 20:
                    match_rate = min(95, 80 + score_diff * 0.75)
                    advice = "保底选择"
                elif score_diff >= 10:
                    match_rate = 70 + score_diff
                    advice = "稳妥选择"
                elif score_diff >= 0:
                    match_rate = 60 + score_diff * 2
                    advice = "冲刺选择"
                elif score_diff >= -10:
                    match_rate = 50 + score_diff
                    advice = "冲刺选择"
                else:
                    match_rate = max(10, 40 + score_diff * 0.5)
                    advice = "不建议"
                
                school["advice"] = advice
                
                match_results.append({
                    "schoolId": school["schoolId"],
                    "schoolName": school["schoolName"],
                    "matchRate": round(match_rate, 1),
                    "scoreDiff": score_diff,
                    "recommendation": "强烈推荐" if match_rate >= 80 else "推荐" if match_rate >= 60 else "谨慎考虑"
                })
            
            match_results.sort(key=lambda x: x["matchRate"], reverse=True)
        
        winner = None
        analysis = ""
        if schools:
            best_school = max(schools, key=lambda x: x["oneRate"])
            winner = {
                "schoolName": best_school["schoolName"],
                "reason": f"一本率最高({best_school['oneRate']}%)，综合实力强"
            }
            analysis = f"根据对比分析，{best_school['schoolName']}的一本率达到{best_school['oneRate']}%，在选择的学校中表现最为突出。"
            if student_score:
                score_diff = student_score - best_school["minScore"]
                if score_diff >= 0:
                    analysis += f"您的分数超过该校录取线，录取概率较高，建议作为首选志愿。"
                else:
                    analysis += f"您的分数距离该校录取线还有{-score_diff}分差距，可以作为冲刺目标。"
        
        return {
            "success": True,
            "data": {
                "schools": schools,
                "schoolsSortedByScore": schools_sorted_by_score,
                "statistics": {
                    "avgScore": round(avg_score, 1),
                    "avgRank": round(avg_rank, 1),
                    "avgOneRate": round(avg_rate, 1),
                    "avgTuition": round(avg_tuition, 1)
                },
                "matchResults": match_results if student_score else None,
                "totalSchools": len(schools),
                "winner": winner,
                "analysis": analysis
            }
        }
    except Exception as e:
        print(f'Compare API Error: {e}')
        return {
            "success": False,
            "message": str(e)
        }


# ==================== 意图识别接口 ====================
@router.post("/chat/intent", response_model=Dict[str, Any])
async def recognize_intent(data: Dict[str, Any] = Body(...)):
    """意图识别接口"""
    try:
        message = data.get('message', '')
        
        if not message.strip():
            return {
                "success": False,
                "message": "请输入消息内容"
            }
        
        intent, confidence = recognize_user_intent(message)
        
        return {
            "success": True,
            "data": {
                "intent": intent,
                "confidence": confidence,
                "message": message
            }
        }
    except Exception as e:
        print(f'Intent Recognition API Error: {e}')
        return {
            "success": False,
            "message": str(e)
        }


# ==================== AI聊天接口（使用ChatService） ====================
@router.post("/chat", response_model=Dict[str, Any])
async def ai_chat(data: Dict[str, Any] = Body(...)):
    """AI智能聊天接口"""
    try:
        from app.services.chat_service import get_chat_service
        
        chat_service = get_chat_service()
        
        message = data.get('message', '')
        session_id = data.get('session_id')
        
        if not message.strip():
            return {
                "success": False,
                "message": "请输入问题"
            }
        
        # 使用ChatService处理消息
        result = chat_service.process_message(session_id, message)
        
        return {
            "success": result.get('success', False),
            "data": {"content": result.get('content', '')},
            "session_id": result.get('session_id', session_id)
        }
    except Exception as e:
        print(f'AI Chat Error: {e}')
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e)
        }


# ==================== 政策解读接口 ====================
@router.post("/interpret-policy", response_model=Dict[str, Any])
async def interpret_policy(data: Dict[str, Any] = Body(...)):
    """AI政策解读接口"""
    try:
        policy_content = data.get('policyContent', '') or data.get('content', '')
        policy_id = data.get('policyId') or data.get('policy_id')
        
        if not policy_content.strip():
            return {
                "success": False,
                "message": "缺少政策内容"
            }
        
        key_points = []
        for line in policy_content.split('\n')[:10]:
            stripped = line.strip()
            if stripped and len(stripped) > 5:
                key_points.append(stripped[:80])
        
        return {
            "success": True,
            "data": {
                "keyPoints": key_points[:5],
                "impact": "本政策对考生志愿填报和学校选择有重要参考价值，建议结合自身分数和排名进行综合评估。",
                "suggestions": [
                    "仔细阅读政策全文，了解具体要求和限制条件",
                    "结合自身成绩和兴趣选择合适的学校",
                    "关注政策中提到的时间节点和申报流程",
                    "如有疑问及时咨询学校或教育部门"
                ],
                "policyId": policy_id
            },
            "message": "解读成功"
        }
    except Exception as e:
        print(f'Policy Interpretation Error: {e}')
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e)
        }


# ==================== 分数预测接口 ====================
@router.post("/predict/score", response_model=Dict[str, Any])
async def predict_score(data: List[Dict[str, Any]] = Body(...)):
    """预测中考分数"""
    try:
        if not data or len(data) == 0:
            return {
                "success": False,
                "message": "缺少考试数据"
            }
        
        scores = [exam.get('score', 0) for exam in data]
        valid_scores = [s for s in scores if s > 0]
        
        if not valid_scores:
            return {
                "success": False,
                "message": "没有有效的考试分数"
            }
        
        avg_score = sum(valid_scores) / len(valid_scores)
        
        variance = sum((s - avg_score) ** 2 for s in valid_scores) / len(valid_scores)
        std_dev = variance ** 0.5
        
        trend = 0
        trend_value = 0
        if len(valid_scores) >= 2:
            recent_avg = sum(valid_scores[-3:]) / min(3, len(valid_scores))
            earlier_avg = sum(valid_scores[:3]) / min(3, len(valid_scores))
            trend_value = recent_avg - earlier_avg
            if trend_value > 5:
                trend = "上升"
            elif trend_value < -5:
                trend = "下降"
            else:
                trend = "稳定"
        
        predicted_score = avg_score + trend_value * 0.5
        confidence_interval = std_dev * 1.5
        
        predicted_rank = max(100, int(85000 - predicted_score * 110))
        
        confidence = min(95, max(60, 70 + (len(valid_scores) - 1) * 5 - std_dev / 5))
        
        analysis = f"根据您的{len(valid_scores)}次模考成绩分析，"
        if trend == "上升":
            analysis += f"成绩呈上升趋势（+{abs(trend_value):.1f}分），"
        elif trend == "下降":
            analysis += f"成绩呈下降趋势（-{abs(trend_value):.1f}分），"
        else:
            analysis += "成绩保持稳定，"
        analysis += f"预测中考分数为{predicted_score:.1f}分左右。"
        
        return {
            "success": True,
            "data": {
                "predictedScore": round(predicted_score, 1),
                "scoreRange": {
                    "low": round(predicted_score - confidence_interval, 1),
                    "high": round(predicted_score + confidence_interval, 1)
                },
                "predictedRank": predicted_rank,
                "rankRange": {
                    "low": predicted_rank + 2000,
                    "high": predicted_rank - 2000 if predicted_rank > 2000 else 100
                },
                "trend": trend,
                "trendValue": round(trend_value, 1),
                "confidence": round(confidence, 1),
                "analysis": analysis
            }
        }
    except Exception as e:
        print(f'Predict Score API Error: {e}')
        return {
            "success": False,
            "message": str(e)
        }


# ==================== 录取概率预测接口 ====================
@router.post("/predict/admission", response_model=Dict[str, Any])
async def predict_admission(data: Dict[str, Any] = Body(...)):
    """预测录取概率"""
    try:
        from app.utils.db import get_db_connection
        
        student_score = data.get('score', 0)
        school_id = data.get('schoolId', 0)
        
        if not student_score or not school_id:
            return {
                "success": False,
                "message": "缺少必要参数"
            }
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT min_score, min_rank, one_rate FROM schools WHERE id = ?"
            cursor.execute(query, (school_id,))
            row = cursor.fetchone()
        
        if not row:
            return {
                "success": False,
                "message": "学校不存在"
            }
        
        min_score_val, min_rank_val, one_rate_val = row
        
        score_diff = student_score - min_score_val
        if score_diff >= 30:
            probability = min(99, 90 + score_diff * 0.3)
        elif score_diff >= 20:
            probability = 80 + score_diff
        elif score_diff >= 10:
            probability = 70 + score_diff * 1.5
        elif score_diff >= 0:
            probability = 50 + score_diff * 2
        elif score_diff >= -10:
            probability = 30 + score_diff * 2
        elif score_diff >= -20:
            probability = max(5, 20 + score_diff)
        else:
            probability = max(1, 10 + score_diff * 0.3)
        
        return {
            "success": True,
            "data": {
                "probability": round(probability, 1),
                "scoreDiff": score_diff,
                "schoolMinScore": min_score_val,
                "schoolMinRank": min_rank_val,
                "oneRate": one_rate_val
            }
        }
    except Exception as e:
        print(f'Predict API Error: {e}')
        return {
            "success": False,
            "message": str(e)
        }


# ==================== 学校推荐接口 ====================
@router.post("/recommend/schools", response_model=Dict[str, Any])
async def recommend_schools(data: Dict[str, Any] = Body(...)):
    """推荐学校"""
    try:
        from app.utils.db import get_db_connection
        
        student_data = data.get('studentData', {})
        student_score = student_data.get('score', 0) or student_data.get('totalScore', 0)
        city = student_data.get('city', '')
        
        if not student_score:
            return {
                "success": False,
                "message": "缺少学生分数"
            }
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT id, name, type, min_score, min_rank, one_rate, boarding, tuition, prefecture, level FROM schools WHERE 1=1"
            params = []
            
            if city:
                query += " AND (city = ? OR prefecture = ?)"
                params.extend([city, city])
            
            query += " AND min_score BETWEEN ? AND ?"
            params.extend([student_score - 30, student_score + 30])
            
            query += " ORDER BY ABS(min_score - ?)"
            params.append(student_score)
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        
        recommendations = []
        for row in rows[:10]:
            school_dict = dict(zip(columns, row))
            score_diff = student_score - school_dict["min_score"]
            
            if score_diff >= 20:
                probability = min(95, 85 + score_diff * 0.5)
            elif score_diff >= 10:
                probability = 75 + score_diff
            elif score_diff >= 0:
                probability = 60 + score_diff * 1.5
            elif score_diff >= -10:
                probability = 45 + score_diff * 1.5
            else:
                probability = max(10, 30 + score_diff * 0.5)
            
            level_bonus = 0
            level = str(school_dict.get("level", ""))
            if level and "一级一等" in level:
                level_bonus = 10
            elif level and "一级二等" in level:
                level_bonus = 5
            elif level and "省级示范" in level:
                level_bonus = 8
            
            match_score = probability + level_bonus
            
            recommendations.append({
                "schoolId": school_dict["id"],
                "schoolName": school_dict["name"],
                "schoolType": school_dict.get("type"),
                "type": school_dict.get("type", 1),
                "minScore": school_dict.get("min_score"),
                "minRank": school_dict.get("min_rank"),
                "oneRate": school_dict.get("one_rate"),
                "boarding": school_dict["boarding"],
                "tuition": school_dict["tuition"],
                "prefecture": school_dict["prefecture"],
                "level": school_dict["level"],
                "matchProbability": round(probability, 1),
                "matchScore": round(match_score, 1),
                "scoreDiff": score_diff,
                "reason": generate_reason(school_dict, probability, score_diff)
            })
        
        recommendations.sort(key=lambda x: x["matchScore"], reverse=True)
        
        return {
            "success": True,
            "data": {
                "recommendations": recommendations,
                "total": len(recommendations)
            }
        }
    except Exception as e:
        print(f'Recommend API Error: {e}')
        return {
            "success": False,
            "message": str(e)
        }


def generate_reason(school_dict, probability, score_diff):
    """生成推荐理由"""
    reasons = []
    
    if probability >= 90:
        reasons.append("录取概率极高")
    elif probability >= 80:
        reasons.append("录取概率较高")
    elif probability >= 70:
        reasons.append("有一定录取机会")
    else:
        reasons.append("可作为冲刺选择")
    
    if score_diff >= 0:
        reasons.append(f"分数超过录取线{score_diff}分")
    else:
        reasons.append(f"距离录取线还差{abs(score_diff)}分")
    
    level = school_dict.get("level", "")
    if level and "一级" in level:
        reasons.append(f"{level}优质学校")
    
    return "；".join(reasons)


# ==================== 智能匹配学校接口 ====================
@router.post("/match/schools", response_model=Dict[str, Any])
async def match_schools(data: Dict[str, Any] = Body(...)):
    """智能匹配学校"""
    try:
        student_info = data.get('studentInfo', data)
        student_score = student_info.get('score', 0) or student_info.get('totalScore', 0)
        
        if not student_score:
            return {
                "success": False,
                "message": "缺少学生分数"
            }
        
        result = await recommend_schools({'studentData': student_info})
        return result
    except Exception as e:
        print(f'Match API Error: {e}')
        return {
            "success": False,
            "message": str(e)
        }


# ==================== 志愿方案生成接口 ====================
@router.post("/volunteer/generate", response_model=Dict[str, Any])
async def generate_volunteer(data: Dict[str, Any] = Body(...)):
    """生成志愿方案"""
    try:
        student_form = data.get('studentForm', data)
        student_score = student_form.get('totalScore', student_form.get('score', 0))
        
        if not student_score:
            return {
                "success": False,
                "message": "缺少学生分数"
            }
        
        result = await recommend_schools({'studentData': student_form})
        if not result.get('success'):
            return result
        
        recommendations = result['data']['recommendations']
        
        volunteers = []
        categories = ['冲刺', '稳妥', '保底']
        order = 1
        
        for i, school in enumerate(recommendations[:7]):
            category = categories[min(i // 2, 2)]
            volunteers.append({
                "order": order,
                "batch": "第一批",
                "schoolId": school['schoolId'],
                "schoolName": school['schoolName'],
                "category": category,
                "probability": school.get('matchProbability', school.get('probability', 0)),
                "suggestion": f"{category}志愿，录取概率{school.get('matchProbability', school.get('probability', 0))}%"
            })
            order += 1
        
        chong_count = sum(1 for v in volunteers if v['category'] == '冲刺')
        wen_count = sum(1 for v in volunteers if v['category'] == '稳妥')
        bao_count = sum(1 for v in volunteers if v['category'] == '保底')
        avg_prob = round(sum(v['probability'] for v in volunteers) / len(volunteers), 1) if volunteers else 0
        
        suggestions = [
            "建议按照志愿序号顺序填报",
            "冲刺志愿可以尝试报考高于自己分数的学校",
            "保底志愿确保有学可上",
            "注意各学校的招生计划和录取规则"
        ]
        
        return {
            "success": True,
            "data": {
                "volunteers": volunteers,
                "summary": {
                    "chongCount": chong_count,
                    "wenCount": wen_count,
                    "baoCount": bao_count,
                    "totalProbability": avg_prob
                },
                "suggestions": suggestions,
                "strategy": "根据您的分数，建议采用冲稳保策略",
                "total": len(volunteers)
            }
        }
    except Exception as e:
        print(f'Volunteer Generate API Error: {e}')
        return {
            "success": False,
            "message": str(e)
        }


# ==================== 志愿风险检查接口 ====================
@router.post("/volunteer/risk", response_model=Dict[str, Any])
async def check_volunteer_risk(data: Dict[str, Any] = Body(...)):
    """检查志愿风险"""
    try:
        volunteer_table = data.get('volunteerTable', [])
        
        if not volunteer_table:
            return {
                "success": False,
                "message": "缺少志愿数据"
            }
        
        risks = []
        high_risk_count = 0
        
        for volunteer in volunteer_table:
            probability = volunteer.get('probability', 0)
            if probability < 30:
                risks.append({
                    "schoolId": volunteer.get('schoolId'),
                    "schoolName": volunteer.get('schoolName'),
                    "riskLevel": "高风险",
                    "reason": "录取概率低于30%，建议调整"
                })
                high_risk_count += 1
            elif probability < 50:
                risks.append({
                    "schoolId": volunteer.get('schoolId'),
                    "schoolName": volunteer.get('schoolName'),
                    "riskLevel": "中风险",
                    "reason": "录取概率较低，需谨慎"
                })
        
        return {
            "success": True,
            "data": {
                "risks": risks,
                "highRiskCount": high_risk_count,
                "isSafe": high_risk_count == 0,
                "suggestion": "志愿方案合理" if high_risk_count == 0 else f"发现{high_risk_count}个高风险志愿，建议调整"
            }
        }
    except Exception as e:
        print(f'Volunteer Risk API Error: {e}')
        return {
            "success": False,
            "message": str(e)
        }


# ==================== 高中升学规划接口 ====================
@router.post("/transition/high-school", response_model=Dict[str, Any])
async def high_school_transition(data: Dict[str, Any] = Body(...)):
    """高中升学规划"""
    try:
        plan_form = data.get('planForm', {})
        
        return {
            "success": True,
            "data": {
                "plan": {
                    "phases": [
                        {"name": "高一适应期", "tasks": ["适应高中学习节奏", "打好基础知识"]},
                        {"name": "高二提升期", "tasks": ["深入学习各科知识", "参加学科竞赛"]},
                        {"name": "高三冲刺期", "tasks": ["系统复习", "模拟考试训练"]}
                    ],
                    "suggestions": [
                        "制定合理的学习计划",
                        "保持良好的作息习惯",
                        "积极参加课外活动"
                    ]
                },
                "message": "升学规划已生成"
            }
        }
    except Exception as e:
        print(f'Transition API Error: {e}')
        return {
            "success": False,
            "message": str(e)
        }


# ==================== 反馈提交接口 ====================
@router.post("/feedback", response_model=Dict[str, Any])
async def submit_feedback(data: Dict[str, Any] = Body(...)):
    """提交反馈"""
    try:
        content = data.get('content', '')
        feedback_type = data.get('type', 'general')
        
        if not content:
            return {
                "success": False,
                "message": "反馈内容不能为空"
            }
        
        return {
            "success": True,
            "data": {
                "feedbackId": "fb_" + str(hash(content))[:8],
                "status": "submitted",
                "message": "感谢您的反馈，我们会尽快处理"
            }
        }
    except Exception as e:
        print(f'Feedback API Error: {e}')
        return {
            "success": False,
            "message": str(e)
        }


# ==================== 增强版学校对比接口 ====================
@router.post("/crawl/enhanced/school-compare", response_model=Dict[str, Any])
async def enhanced_crawl_school_compare(data: Dict[str, Any] = Body(...)):
    """增强版学校对比"""
    try:
        from app.utils.db import get_db_connection
        
        schools = data.get('schools', [])
        
        if len(schools) < 2:
            return {
                "success": False,
                "message": "请至少提供2所学校"
            }
        
        school_ids = []
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for school_name in schools:
            cursor.execute("SELECT id FROM schools WHERE name LIKE ?", (f"%{school_name}%",))
            row = cursor.fetchone()
            if row:
                school_ids.append(row[0])
        
        conn.close()
        
        if len(school_ids) < 2:
            return {
                "success": False,
                "message": "未找到足够的学校信息"
            }
        
        result = await compare_schools({'schoolIds': school_ids})
        return result
    except Exception as e:
        print(f'Enhanced Crawl School Compare API Error: {e}')
        return {
            "success": False,
            "message": str(e)
        }


# ==================== 增强版录取计算器接口 ====================
@router.post("/crawl/enhanced/admission-calculator", response_model=Dict[str, Any])
async def enhanced_crawl_admission_calculator(data: Dict[str, Any] = Body(...)):
    """增强版录取计算器"""
    try:
        from app.utils.db import get_db_connection
        
        student_data = data.get('studentData', {})
        student_score = student_data.get('score', 0)
        
        if not student_score:
            return {
                "success": False,
                "message": "缺少学生分数"
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, min_score FROM schools ORDER BY ABS(min_score - ?) LIMIT 5", (student_score,))
        rows = cursor.fetchall()
        conn.close()
        
        predictions = []
        for row in rows:
            school_id, school_name, min_score_val = row
            score_diff = student_score - min_score_val
            
            if score_diff >= 20:
                probability = min(95, 85 + score_diff * 0.5)
            elif score_diff >= 10:
                probability = 75 + score_diff
            elif score_diff >= 0:
                probability = 60 + score_diff * 1.5
            elif score_diff >= -10:
                probability = 45 + score_diff * 1.5
            else:
                probability = max(10, 30 + score_diff * 0.5)
            
            predictions.append({
                "schoolId": school_id,
                "schoolName": school_name,
                "probability": round(probability, 1),
                "scoreDiff": score_diff
            })
        
        return {
            "success": True,
            "data": {
                "predictions": predictions,
                "studentScore": student_score,
                "suggestion": "根据您的分数，以上学校是较为合适的选择"
            }
        }
    except Exception as e:
        print(f'Enhanced Crawl Admission Calculator API Error: {e}')
        return {
            "success": False,
            "message": str(e)
        }


# ==================== 意图识别工具函数 ====================
def recognize_user_intent(message: str) -> tuple:
    """识别用户意图"""
    message = message.lower().strip()
    
    intent_keywords = {
        "school_inquiry": ["学校", "高中", "中学", "哪个学校", "哪所学校", "学校排名", "升学率"],
        "score_recommendation": ["分数", "录取线", "分数线", "多少分", "能上", "推荐", "适合"],
        "policy_inquiry": ["政策", "招生", "报名", "志愿", "报考", "录取", "加分", "优惠"],
        "fee_inquiry": ["学费", "收费", "多少钱", "费用", "住宿费"],
        "study_plan": ["学习计划", "备考", "复习", "规划", "升学"],
        "campus_life": ["校园", "宿舍", "食堂", "环境", "生活"],
        "exam_prep": ["考试", "模拟考", "中考", "复习", "冲刺"],
        "general_question": ["你好", "嗨", "在吗", "帮助", "什么", "怎么"]
    }
    
    scores = {}
    for intent, keywords in intent_keywords.items():
        score = sum(1 for keyword in keywords if keyword in message)
        scores[intent] = score
    
    max_score = max(scores.values())
    if max_score == 0:
        return "general_question", 0.5
    
    top_intents = [intent for intent, score in scores.items() if score == max_score]
    
    if len(top_intents) == 1:
        return top_intents[0], min(1.0, 0.6 + max_score * 0.1)
    
    return top_intents[0], min(1.0, 0.5 + max_score * 0.08)
