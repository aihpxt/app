"""数据库工具模块"""

import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'sqlite', 'data', 'unified_school_data.db')


def _ensure_database():
    """确保数据库文件和目录存在，必要时创建默认表结构"""
    db_dir = os.path.dirname(DB_PATH)
    try:
        os.makedirs(db_dir, exist_ok=True)
    except Exception:
        pass

    # 如果数据库文件不存在，或者存在但没有 schools 表，则创建基础表结构
    needs_init = not os.path.exists(DB_PATH)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schools'")
        if not cursor.fetchone():
            needs_init = True
        conn.close()
    except Exception:
        needs_init = True

    if needs_init:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            # schools 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    type INTEGER DEFAULT 1,
                    type_name TEXT DEFAULT '高中',
                    is_public INTEGER DEFAULT 1,
                    nature TEXT DEFAULT '公办',
                    min_score REAL,
                    min_rank INTEGER,
                    max_score REAL,
                    avg_score REAL,
                    one_rate REAL,
                    boarding INTEGER DEFAULT 0,
                    tuition INTEGER DEFAULT 0,
                    style TEXT,
                    features TEXT,
                    address TEXT,
                    phone TEXT,
                    website TEXT,
                    description TEXT,
                    city TEXT,
                    prefecture TEXT,
                    level TEXT,
                    logo TEXT,
                    view_count INTEGER DEFAULT 0,
                    student_count INTEGER DEFAULT 0,
                    teacher_count INTEGER DEFAULT 0,
                    is_key INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # policies 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT,
                    prefecture TEXT,
                    category TEXT,
                    publish_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # users 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    email TEXT,
                    phone TEXT,
                    display_name TEXT,
                    role TEXT DEFAULT 'user',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # chat_messages 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
        except Exception:
            pass


@contextmanager
def get_db_connection():
    """数据库连接上下文管理器"""
    _ensure_database()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def query_one(sql, params=None):
    """执行查询并返回单条结果"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params or [])
            return cursor.fetchone()
    except Exception:
        return None


def query_all(sql, params=None):
    """执行查询并返回所有结果"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params or [])
            return cursor.fetchall()
    except Exception:
        return []


def execute(sql, params=None):
    """执行SQL语句（INSERT/UPDATE/DELETE）"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params or [])
            conn.commit()
            return cursor.rowcount, cursor.lastrowid
    except Exception:
        return 0, None


def dict_factory(cursor, row):
    """将查询结果转换为字典"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def table_exists(table_name: str) -> bool:
    """检查指定表是否存在"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            return cursor.fetchone() is not None
    except Exception:
        return False
