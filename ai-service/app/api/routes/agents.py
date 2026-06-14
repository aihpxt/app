"""智能体路由模块"""

from fastapi import APIRouter, Depends, Body
from typing import Dict, Any, List
from datetime import datetime
from app.core.exceptions import BadRequestException, NotFoundException, InternalServerErrorException

router = APIRouter()

@router.post("/agent/chat")
async def chat_with_agent(data: Dict[str, Any] = Body(...)):
    """与智能体聊天"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        from app.utils.db import get_db_connection
        import hashlib
        import time
        
        orchestrator = get_agent_orchestrator()
        # 支持input和message两种字段名
        user_input = data.get('input', data.get('message', ''))
        agent_id = data.get('agent_id', 'control_center_agent')
        
        # 获取session_id，如果没有则生成一个新的
        session_id = data.get('session_id')
        if not session_id:
            session_id = hashlib.md5((user_input + str(time.time())).encode('utf-8')).hexdigest()
        
        # 将session_id放入context，确保智能体可以访问
        context = data.get('context', {})
        context['session_id'] = session_id
        
        # 先保存用户消息到数据库
        if user_input and session_id:
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    current_time = datetime.now().isoformat()
                    # 先检查表是否存在，不存在则创建
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_messages'")
                    if not cursor.fetchone():
                        cursor.execute("""
                            CREATE TABLE chat_messages (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                session_id TEXT NOT NULL,
                                role TEXT NOT NULL,
                                content TEXT NOT NULL,
                                created_at TEXT NOT NULL
                            )
                        """)
                    cursor.execute("""
                        INSERT INTO chat_messages (session_id, role, content, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (session_id, 'user', user_input, current_time))
                    conn.commit()
            except Exception as e:
                print(f'保存消息失败: {e}')
        
        # 获取会话历史作为上下文
        history = []
        if session_id:
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT role, content 
                        FROM chat_messages 
                        WHERE session_id = ? 
                        ORDER BY created_at ASC
                    """, (session_id,))
                    rows = cursor.fetchall()
                    history = [{"role": row[0], "content": row[1]} for row in rows]
            except Exception as e:
                print(f'获取会话历史失败: {e}')
        
        # 将历史消息放入上下文
        context['history'] = history
        
        result = orchestrator.dispatch_task(agent_id, user_input, context)
        
        # 保存智能体响应到数据库
        response_text = result.get('response', result.get('data', str(result)))
        if response_text and session_id:
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    current_time = datetime.now().isoformat()
                    cursor.execute("""
                        INSERT INTO chat_messages (session_id, role, content, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (session_id, 'assistant', response_text, current_time))
                    conn.commit()
            except Exception as e:
                print(f'保存响应消息失败: {e}')
        
        # 使用生成的session_id作为响应的session_id
        response_session_id = session_id
        
        return {
            "success": True,
            "data": result,
            "response": response_text,
            "session_id": response_session_id
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))


@router.post("/agent/feedback")
async def submit_agent_feedback(data: Dict[str, Any] = Body(...)):
    """提交智能体对话反馈"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        session_id = data.get("session_id", "")
        feedback_type = data.get("type", "neutral")
        score = data.get("score", 0.5)
        details = data.get("details", {})
        
        if not session_id:
            raise BadRequestException(detail="session_id不能为空")
        
        success = orchestrator.send_hermes_feedback(session_id, feedback_type, score, details)
        return {
            "success": True,
            "data": {"recorded": success, "session_id": session_id}
        }
    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))


@router.get("/agent/session-report/{session_id}")
async def get_agent_session_report(session_id: str):
    """获取智能体会话洞察报告"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        report = orchestrator.get_hermes_session_report(session_id)
        return {
            "success": True,
            "data": report
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))


@router.get("/agent/hermes-health")
async def get_hermes_health():
    """获取Hermes服务健康状态"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        report = orchestrator.get_hermes_health_report()
        return {
            "success": True,
            "data": report
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))


@router.get("/agent/incomplete-sessions")
async def get_hermes_incomplete_sessions():
    """获取未完成的会话列表"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        sessions = orchestrator.get_hermes_incomplete_sessions()
        return {
            "success": True,
            "data": {"count": len(sessions), "sessions": sessions}
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))

@router.get("/agents")
async def get_all_agents():
    """获取所有智能体"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        agents = orchestrator.get_agents()
        return {
            "success": True,
            "data": agents
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))

@router.get("/agent/{agent_id}")
async def get_agent(agent_id: str):
    """获取指定智能体"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        agent = orchestrator.get_agent(agent_id)
        if not agent:
            raise NotFoundException(detail="智能体不存在")
        return {
            "success": True,
            "data": agent
        }
    except NotFoundException:
        raise
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))

@router.post("/agents/chat")
async def openclaw_chat(data: Dict[str, Any] = Body(...)):
    """OpenClaw聊天接口"""
    try:
        from agents.agent_orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        question = data.get('question')
        if not question:
            raise BadRequestException(detail="问题不能为空")
        # 调用智能体编排器处理请求
        result = orchestrator.dispatch_task('zk-master', question, {})
        # 提取响应内容
        content = result.get('response', result.get('data', result.get('message', str(result))))
        return {
            "success": True,
            "response": content,
            "data": content,
            "message": content
        }
    except BadRequestException:
        raise
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))


@router.get("/sessions/stats")
async def get_session_stats():
    """获取会话统计信息"""
    try:
        from app.core.cache import session_cache_manager
        stats = session_cache_manager.get_session_stats()
        stats["recent_active"] = session_cache_manager.get_recent_active_sessions(10)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session_detail(session_id: str):
    """获取指定会话的详细信息"""
    try:
        from app.core.cache import session_cache_manager
        data = session_cache_manager.get_session(session_id)
        if not data:
            return {
                "success": True,
                "data": None,
                "message": "会话不存在或已过期"
            }
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "topic": data.get("topic", ""),
                "topic_history": data.get("topic_history", []),
                "history_count": len(data.get("conversation_history", [])),
                "last_question": data.get("last_question", ""),
                "last_answer": data.get("last_answer", "")[:100],
                "timestamp": data.get("timestamp", 0)
            }
        }
    except Exception as e:
        raise InternalServerErrorException(detail=str(e))
