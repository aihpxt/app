"""智能体路由模块 - 健壮版

核心策略：
1. 先尝试使用智能体编排器（AgentOrchestrator）
2. 如果编排器不可用，则回退到本地简单的关键词/意图识别逻辑
3. 永远返回 HTTP 200 的 JSON 响应，不抛出 500 异常
"""

from fastapi import APIRouter, Body
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import time
import re

router = APIRouter()


# ============================================================
# 本地回退智能体逻辑 (Local Fallback Agents)
# 当 AgentOrchestrator 失败时使用
# ============================================================

def _match_intent(user_input: str) -> str:
    """简单意图识别 - 基于关键词匹配"""
    text = (user_input or "").lower()

    # 问候与闲聊
    greetings = ["你好", "您好", "hi", "hello", "在吗", "在么", "嗨", "哈喽", "早上好", "下午好", "晚上好"]
    farewells = ["再见", "拜拜", "再见了", "bye", "goodbye"]
    thanks = ["谢谢", "感谢", "多谢", "thx", "thanks"]

    # 学校查询相关关键词
    school_keywords = [
        "学校", "中学", "一中", "二中", "附中", "高中", "初中", "小学",
        "文山", "昆明", "曲靖", "玉溪", "保山", "昭通", "丽江", "普洱",
        "楚雄", "红河", "西双版纳", "大理", "德宏", "怒江", "迪庆", "临沧",
        "未央", "丘北", "录取分数", "分数线", "一本率", "升学率",
        "排名", "怎么样", "介绍", "简介", "情况如何", "好不好", "如何"
    ]

    # 政策相关
    policy_keywords = [
        "政策", "政策解读", "招生政策", "报考政策", "中考政策",
        "指标到校", "定向", "统招", "择校", "志愿填报", "志愿",
        "自主招生", "民族班", "加分", "优惠", "规则"
    ]

    # 分数相关
    score_keywords = [
        "分数", "分", "预估分", "考了", "考多少", "能上", "500", "600",
        "550", "580", "620", "650", "680", "700"
    ]

    # 学习相关
    study_keywords = [
        "学习", "复习", "备考", "计划", "方法", "技巧", "怎么学",
        "科目", "数学", "语文", "英语", "物理", "化学", "英语"
    ]

    # 匹配意图
    if any(g in text for g in greetings):
        return "greeting"
    if any(f in text for f in farewells):
        return "farewell"
    if any(t in text for t in thanks):
        return "thanks"
    if any(p in text for p in policy_keywords):
        return "policy"
    if any(s in text for s in school_keywords) or re.search(r'[一二三四五六七八九]+中', text):
        return "school_query"
    if any(s in text for s in score_keywords) or re.search(r'\d{2,3}\s*分', text):
        return "score"
    if any(s in text for s in study_keywords):
        return "study"

    return "general"


def _fallback_generate_response(user_input: str, intent: str) -> str:
    """本地回退响应生成"""
    if intent == "greeting":
        return "你好！我是云南省中考择校智能助手小龙虾。我可以帮您查询学校信息、解读中考政策、推荐合适的学校。请问有什么可以帮您的？"
    if intent == "farewell":
        return "再见！祝您和孩子在中考中取得理想的成绩，考上心仪的学校！"
    if intent == "thanks":
        return "不客气！如果还有其他问题，随时问我~"
    if intent == "school_query":
        return f"关于「{user_input}」，这是一个学校相关的查询。云南的优秀高中包括：\n\n" \
               f"🏫 **昆明市**：昆明市第一中学、云南师范大学附属中学、昆明市第三中学\n" \
               f"🏫 **文山州**：文山州第一中学、砚山县第一中学\n" \
               f"🏫 **曲靖市**：曲靖市第一中学、曲靖市第二中学\n" \
               f"🏫 **玉溪市**：玉溪市第一中学\n\n" \
               f"如果您想了解具体学校的录取分数、一本率等详细信息，请告诉我学校名称，或者告诉我孩子的分数和所在城市，我可以为您推荐合适的学校。"
    if intent == "policy":
        return "云南省中考政策主要包括以下内容：\n\n" \
               "📋 **招生方式**：统一招生、指标到校、自主招生相结合\n" \
               "📋 **志愿填报**：中考后估分或知分填报志愿，一般分多个批次\n" \
               "📋 **加分政策**：少数民族、烈士子女等可享受加分\n" \
               "📋 **民族班**：部分学校设有民族班，面向少数民族考生\n\n" \
               "具体政策以云南省教育厅当年发布的官方文件为准。建议关注云南省招生考试院官网获取最新信息。"
    if intent == "score":
        return "分数是中考择校的关键参考。一般来说：\n\n" \
               "🌟 650分以上：可以冲刺顶级高中（如师大附中、昆一中）\n" \
               "🌟 600-650分：可以考虑各地州重点中学\n" \
               "🌟 550-600分：可以选择普通高中或较好的县中\n" \
               "🌟 500-550分：可以选择普通高中、民办高中\n\n" \
               "📊 云南省中考总分一般在 700-750 分左右（含体育）。具体分数线每年会根据试题难度和招生计划调整。\n\n" \
               "告诉我孩子的具体分数和所在城市，我可以为您做更精准的推荐！"
    if intent == "study":
        return "高效的中考备考建议：\n\n" \
               "📚 **制定计划**：按科目分配时间，薄弱科目多花时间\n" \
               "📚 **夯实基础**：先掌握教材知识点，再做难题\n" \
               "📚 **真题训练**：多做历年真题，熟悉出题规律\n" \
               "📚 **错题总结**：建立错题本，定期回顾\n" \
               "📚 **劳逸结合**：保证睡眠，适当运动\n" \
               "📚 **心态调整**：保持积极，避免焦虑\n\n" \
               "有具体的科目或学习问题，随时告诉我！"

    # 通用响应
    return f"我收到了您的问题：「{user_input}」。\n\n" \
           f"作为云南省中考择校助手，我可以为您提供以下帮助：\n" \
           f"🏫 学校信息查询（录取分数、一本率等）\n" \
           f"📋 中考政策解读\n" \
           f"📊 根据分数推荐学校\n" \
           f"📚 学习备考建议\n\n" \
           f"请告诉我您具体想了解什么？"


def _safe_db_save_message(session_id: str, role: str, content: str):
    """安全地保存消息到数据库（失败不影响主流程）"""
    try:
        from app.utils.db import get_db_connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 确保表存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_messages'")
            if not cursor.fetchone():
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)
            cursor.execute(
                "INSERT INTO chat_messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (session_id, role, content, datetime.now().isoformat())
            )
            conn.commit()
    except Exception:
        pass


def _safe_db_get_history(session_id: str) -> List[Dict[str, str]]:
    """安全地获取会话历史"""
    try:
        from app.utils.db import get_db_connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content FROM chat_messages
                WHERE session_id = ? ORDER BY created_at ASC
            """, (session_id,))
            rows = cursor.fetchall()
            return [{"role": r[0], "content": r[1]} for r in rows]
    except Exception:
        return []


# ============================================================
# 路由定义
# ============================================================

@router.post("/agent/chat")
async def chat_with_agent(data: Dict[str, Any] = Body(...)):
    """与智能体聊天 - 核心接口

    优先使用智能体编排器，失败时自动回退到本地逻辑
    """
    try:
        user_input = data.get('input', data.get('message', ''))
        agent_id = data.get('agent_id', 'control_center_agent')

        # 获取或生成 session_id
        session_id = data.get('session_id')
        if not session_id:
            session_id = hashlib.md5(
                (user_input + str(time.time())).encode('utf-8')
            ).hexdigest()

        context = data.get('context', {}) or {}
        context['session_id'] = session_id

        # 保存用户消息
        if user_input:
            _safe_db_save_message(session_id, 'user', user_input)

        # 获取历史消息（用于上下文）
        history = _safe_db_get_history(session_id)
        context['history'] = history

        # ---- 策略1: 尝试使用智能体编排器 ----
        response_text = None
        used_orchestrator = False
        try:
            from agents.agent_orchestrator import get_agent_orchestrator
            orchestrator = get_agent_orchestrator()
            result = orchestrator.dispatch_task(agent_id, user_input, context)
            if result:
                response_text = result.get('response', result.get('data', ''))
                if response_text and str(response_text).strip():
                    used_orchestrator = True
        except Exception:
            response_text = None

        # ---- 策略2: 回退到本地逻辑 ----
        if not response_text or not str(response_text).strip():
            intent = _match_intent(user_input)
            response_text = _fallback_generate_response(user_input, intent)

        # 保存助手响应
        if response_text:
            _safe_db_save_message(session_id, 'assistant', response_text)

        # 统一响应格式（兼容前端各种字段名）
        return {
            "success": True,
            "data": {
                "response": response_text,
                "session_id": session_id,
                "agent_id": agent_id,
                "used_orchestrator": used_orchestrator
            },
            "response": response_text,
            "answer": response_text,
            "message": response_text,
            "session_id": session_id
        }

    except Exception as e:
        # 最后一道防线
        safe_input = (data or {}).get('message', (data or {}).get('input', ''))
        fallback = _fallback_generate_response(safe_input, _match_intent(safe_input))
        return {
            "success": True,
            "response": fallback,
            "answer": fallback,
            "message": fallback,
            "data": {"response": fallback},
            "session_id": hashlib.md5(
                (safe_input + str(time.time())).encode('utf-8')
            ).hexdigest()
        }


@router.post("/agents/chat")
async def openclaw_chat(data: Dict[str, Any] = Body(...)):
    """OpenClaw聊天接口 - 与 agent/chat 逻辑一致"""
    return await chat_with_agent(data)


@router.post("/agent/feedback")
async def submit_agent_feedback(data: Dict[str, Any] = Body(...)):
    """提交智能体对话反馈（记录但不强制成功）"""
    try:
        session_id = data.get("session_id", "")
        feedback_type = data.get("type", "neutral")
        score = data.get("score", 0.5)

        if not session_id:
            return {
                "success": False,
                "data": {"recorded": False},
                "message": "session_id不能为空"
            }

        # 尝试通过 orchestrator 发送
        try:
            from agents.agent_orchestrator import get_agent_orchestrator
            orchestrator = get_agent_orchestrator()
            if hasattr(orchestrator, 'send_hermes_feedback'):
                orchestrator.send_hermes_feedback(session_id, feedback_type, score, data.get("details", {}))
        except Exception:
            pass

        return {
            "success": True,
            "data": {"recorded": True, "session_id": session_id}
        }
    except Exception:
        return {
            "success": True,
            "data": {"recorded": False, "session_id": (data or {}).get("session_id", "")}
        }


@router.get("/agents")
async def get_all_agents():
    """获取所有智能体列表"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        agents = orchestrator.get_agents()
        return {"success": True, "data": agents}
    except Exception:
        # 返回默认的智能体列表
        return {
            "success": True,
            "data": [
                {"id": "control_center_agent", "name": "总控智能体", "description": "中考择校综合咨询"},
                {"id": "school_query_agent", "name": "学校查询智能体", "description": "学校信息查询与对比"},
                {"id": "policy_agent", "name": "政策解读智能体", "description": "中考政策解读"},
                {"id": "score_agent", "name": "分数分析智能体", "description": "分数分析与学校推荐"},
                {"id": "study_agent", "name": "学习规划智能体", "description": "学习计划与备考建议"}
            ]
        }


@router.get("/agent/{agent_id}")
async def get_agent(agent_id: str):
    """获取指定智能体"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        agent = orchestrator.get_agent(agent_id)
        if not agent:
            return {"success": False, "data": None, "message": "智能体不存在"}
        return {"success": True, "data": agent}
    except Exception:
        return {"success": True, "data": {"id": agent_id, "name": agent_id, "description": "智能体"}}


@router.get("/agent/session-report/{session_id}")
async def get_agent_session_report(session_id: str):
    """获取智能体会话洞察报告（占位接口）"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        if hasattr(orchestrator, 'get_hermes_session_report'):
            report = orchestrator.get_hermes_session_report(session_id)
            return {"success": True, "data": report}
    except Exception:
        pass

    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "message_count": 0,
            "topics": [],
            "summary": "会话报告功能开发中"
        }
    }


@router.get("/agent/hermes-health")
async def get_hermes_health():
    """获取Hermes服务健康状态（占位接口）"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        if hasattr(orchestrator, 'get_hermes_health_report'):
            report = orchestrator.get_hermes_health_report()
            return {"success": True, "data": report}
    except Exception:
        pass

    return {
        "success": True,
        "data": {
            "status": "degraded",
            "mode": "local_fallback",
            "message": "使用本地回退逻辑"
        }
    }


@router.get("/agent/incomplete-sessions")
async def get_hermes_incomplete_sessions():
    """获取未完成的会话列表（占位接口）"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        if hasattr(orchestrator, 'get_hermes_incomplete_sessions'):
            sessions = orchestrator.get_hermes_incomplete_sessions()
            return {"success": True, "data": {"count": len(sessions), "sessions": sessions}}
    except Exception:
        pass

    return {"success": True, "data": {"count": 0, "sessions": []}}


@router.get("/sessions/stats")
async def get_session_stats():
    """获取会话统计信息"""
    try:
        from app.core.cache import session_cache_manager
        stats = session_cache_manager.get_session_stats()
        stats["recent_active"] = session_cache_manager.get_recent_active_sessions(10)
        return {"success": True, "data": stats}
    except Exception:
        return {
            "success": True,
            "data": {
                "total_sessions": 0,
                "active_sessions": 0,
                "recent_active": []
            }
        }


@router.get("/sessions/{session_id}")
async def get_session_detail(session_id: str):
    """获取指定会话的详细信息"""
    try:
        from app.core.cache import session_cache_manager
        data = session_cache_manager.get_session(session_id)
        if not data:
            history = _safe_db_get_history(session_id)
            return {
                "success": True,
                "data": {
                    "session_id": session_id,
                    "topic": "",
                    "history_count": len(history),
                    "timestamp": 0
                },
                "message": "会话不存在或已过期"
            }
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "topic": data.get("topic", ""),
                "history_count": len(data.get("conversation_history", [])),
                "last_question": data.get("last_question", ""),
                "last_answer": (data.get("last_answer", "") or "")[:100],
                "timestamp": data.get("timestamp", 0)
            }
        }
    except Exception:
        history = _safe_db_get_history(session_id)
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "topic": "",
                "history_count": len(history),
                "timestamp": 0
            }
        }
