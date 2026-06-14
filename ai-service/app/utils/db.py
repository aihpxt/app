"""数据库工具模块"""

import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'sqlite', 'data', 'unified_school_data.db')

@contextmanager
def get_db_connection():
    """数据库连接上下文管理器"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def query_one(sql, params=None):
    """执行查询并返回单条结果"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or [])
        return cursor.fetchone()

def query_all(sql, params=None):
    """执行查询并返回所有结果"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or [])
        return cursor.fetchall()

def execute(sql, params=None):
    """执行SQL语句（INSERT/UPDATE/DELETE）"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params or [])
        conn.commit()
        return cursor.rowcount, cursor.lastrowid

def dict_factory(cursor, row):
    """将查询结果转换为字典"""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}