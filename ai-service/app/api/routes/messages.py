"""消息管理路由"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional, List, Dict, Any
import sqlite3
import os

router = APIRouter()

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'school_platform.db')

def get_db_connection():
    return sqlite3.connect(DB_PATH)

@router.post("/messages/conversation", response_model=Dict[str, Any])
async def create_conversation(name: str, type: str, subject: Optional[str] = None, content: Optional[str] = ""):
    """创建新的消息会话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    current_time = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO conversations (name, type, subject, last_message, last_time, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, type, subject, content, current_time, current_time, current_time))
    
    conversation_id = cursor.lastrowid
    
    # 如果有初始消息，保存消息
    if content:
        cursor.execute("""
            INSERT INTO messages (conversation_id, content, sender_type, created_at)
            VALUES (?, ?, ?, ?)
        """, (conversation_id, content, 'teacher', current_time))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "data": {
            "conversation_id": conversation_id,
            "name": name,
            "type": type,
            "subject": subject
        }
    }

@router.get("/messages/conversations", response_model=Dict[str, Any])
async def get_conversations(user_type: str = "teacher"):
    """获取会话列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, type, subject, last_message, last_time, unread_count
        FROM conversations
        ORDER BY last_time DESC
    """)
    
    rows = cursor.fetchall()
    conversations = []
    for row in rows:
        conversations.append({
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "subject": row[3],
            "last_message": row[4],
            "last_time": row[5],
            "unread_count": row[6]
        })
    
    conn.close()
    
    return {
        "success": True,
        "data": conversations
    }

@router.post("/messages/send", response_model=Dict[str, Any])
async def send_message(conversation_id: int, content: str, sender_type: str = "teacher"):
    """发送消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    current_time = datetime.now().isoformat()
    
    # 保存消息
    cursor.execute("""
        INSERT INTO messages (conversation_id, content, sender_type, created_at)
        VALUES (?, ?, ?, ?)
    """, (conversation_id, content, sender_type, current_time))
    
    message_id = cursor.lastrowid
    
    # 更新会话
    cursor.execute("""
        UPDATE conversations
        SET last_message = ?, last_time = ?, updated_at = ?
        WHERE id = ?
    """, (content, current_time, current_time, conversation_id))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "data": {
            "message_id": message_id,
            "conversation_id": conversation_id,
            "content": content,
            "sender_type": sender_type,
            "created_at": current_time
        }
    }

@router.get("/messages/conversations/{conversation_id}", response_model=Dict[str, Any])
async def get_messages(conversation_id: int):
    """获取会话消息列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, content, sender_type, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at ASC
    """, (conversation_id,))
    
    rows = cursor.fetchall()
    messages = []
    for row in rows:
        messages.append({
            "id": row[0],
            "content": row[1],
            "sender_type": row[2],
            "created_at": row[3],
            "is_self": row[2] == "teacher"
        })
    
    # 标记为已读
    cursor.execute("""
        UPDATE conversations
        SET unread_count = 0
        WHERE id = ?
    """, (conversation_id,))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "data": messages
    }

@router.delete("/messages/conversations/{conversation_id}", response_model=Dict[str, Any])
async def delete_conversation(conversation_id: int):
    """删除会话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 先删除消息
    cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
    # 再删除会话
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="会话不存在")
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": "会话删除成功"
    }
