from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from datetime import datetime

router = APIRouter()

DB_PATH = "data/schools.db"

class ChatSession(BaseModel):
    id: Optional[int] = None
    title: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: Optional[str] = None

class SaveChatRequest(BaseModel):
    user_id: str
    session_id: Optional[int] = None
    title: Optional[str] = None
    messages: List[ChatMessage]

@router.get("/sessions/{user_id}")
async def get_sessions(user_id: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, created_at, updated_at 
            FROM chat_sessions 
            WHERE user_id = ? 
            ORDER BY updated_at DESC
            LIMIT 50
        ''', (user_id,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "id": row[0],
                "title": row[1],
                "created_at": row[2],
                "updated_at": row[3]
            })
        
        conn.close()
        return {"success": True, "data": sessions}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages/{session_id}")
async def get_messages(session_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, created_at 
            FROM chat_messages 
            WHERE session_id = ? 
            ORDER BY created_at ASC
        ''', (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "created_at": row[2]
            })
        
        conn.close()
        return {"success": True, "data": messages}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
async def save_chat(request: SaveChatRequest):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if request.session_id:
            cursor.execute('''
                UPDATE chat_sessions 
                SET updated_at = CURRENT_TIMESTAMP, title = ?
                WHERE id = ? AND user_id = ?
            ''', (request.title or "新对话", request.session_id, request.user_id))
            session_id = request.session_id
        else:
            cursor.execute('''
                INSERT INTO chat_sessions (user_id, title)
                VALUES (?, ?)
            ''', (request.user_id, request.title or "新对话"))
            session_id = cursor.lastrowid
        
        cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
        
        for msg in request.messages:
            cursor.execute('''
                INSERT INTO chat_messages (session_id, role, content)
                VALUES (?, ?, ?)
            ''', (session_id, msg.role, msg.content))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "data": {"session_id": session_id}}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
async def delete_session(session_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM chat_sessions WHERE id = ?', (session_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
