"""聊天记录管理路由"""

from fastapi import APIRouter, HTTPException, Query, Body
from datetime import datetime
from typing import Optional, List, Dict, Any
import sqlite3
import os

router = APIRouter()

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'school_platform.db')

def get_db_connection():
    return sqlite3.connect(DB_PATH)

@router.post("/chat/sessions", response_model=Dict[str, Any])
async def create_session(data: Dict[str, Any] = Body(...)):
    """创建新的聊天会话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    user_id = data.get('user_id', 'default_user')
    current_time = datetime.now().isoformat()
    title = f"聊天会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    try:
        cursor.execute("""
            INSERT INTO chat_sessions (user_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, title, current_time, current_time))
    except sqlite3.OperationalError:
        # 表不存在，创建表
        cursor.execute("""
            CREATE TABLE chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
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
            INSERT INTO chat_sessions (user_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, title, current_time, current_time))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "title": title,
            "created_at": current_time,
            "updated_at": current_time
        }
    }

@router.get("/chat/sessions", response_model=Dict[str, Any])
async def get_sessions(user_id: Optional[str] = Query("default_user", description="用户ID")):
    """获取用户的会话列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, user_id, title, created_at, updated_at
        FROM chat_sessions
        WHERE user_id = ?
        ORDER BY updated_at DESC
    """, (user_id,))
    
    rows = cursor.fetchall()
    sessions = []
    for row in rows:
        sessions.append({
            "session_id": row[0],
            "user_id": row[1],
            "title": row[2],
            "created_at": row[3],
            "updated_at": row[4]
        })
    
    conn.close()
    
    return {
        "success": True,
        "data": sessions
    }

@router.put("/chat/sessions/{session_id}", response_model=Dict[str, Any])
async def update_session(session_id: int, title: str):
    """更新会话标题"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE chat_sessions
        SET title = ?, updated_at = ?
        WHERE id = ?
    """, (title, datetime.now().isoformat(), session_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="会话不存在")
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": "会话标题更新成功"
    }

@router.delete("/chat/sessions/{session_id}", response_model=Dict[str, Any])
async def delete_session(session_id: int):
    """删除会话及其消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 先删除消息
    cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
    # 再删除会话
    cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="会话不存在")
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": "会话删除成功"
    }

@router.post("/chat/messages", response_model=Dict[str, Any])
async def save_message(session_id: int, role: str, content: str):
    """保存聊天消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    current_time = datetime.now().isoformat()
    
    # 保存消息
    cursor.execute("""
        INSERT INTO chat_messages (session_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (session_id, role, content, current_time))
    
    message_id = cursor.lastrowid
    
    # 更新会话的更新时间
    cursor.execute("""
        UPDATE chat_sessions
        SET updated_at = ?
        WHERE id = ?
    """, (current_time, session_id))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "data": {
            "message_id": message_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "created_at": current_time
        }
    }

@router.get("/chat/sessions/{session_id}/messages", response_model=Dict[str, Any])
async def get_messages(session_id: int):
    """获取会话的消息历史"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, session_id, role, content, created_at
        FROM chat_messages
        WHERE session_id = ?
        ORDER BY created_at ASC
    """, (session_id,))
    
    rows = cursor.fetchall()
    messages = []
    for row in rows:
        messages.append({
            "message_id": row[0],
            "session_id": row[1],
            "role": row[2],
            "content": row[3],
            "created_at": row[4]
        })
    
    conn.close()
    
    return {
        "success": True,
        "data": messages
    }