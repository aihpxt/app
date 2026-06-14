#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""初始化消息相关的数据库表"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'school_platform.db')

def init_tables():
    """创建消息相关的数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建会话表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            subject TEXT,
            last_message TEXT,
            last_time TEXT,
            unread_count INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # 创建消息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            content TEXT NOT NULL,
            sender_type TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    ''')
    
    # 创建聊天会话表（智能助手）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # 创建聊天消息表（智能助手）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("消息相关数据表创建完成")

if __name__ == '__main__':
    init_tables()
