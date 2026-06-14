"""
统一的数据访问层
提供标准化的数据库操作接口
"""

import sqlite3
import json
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
from datetime import datetime
import os


class UnifiedDatabaseManager:
    """统一数据库管理器"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data',
                'school_platform.db'
            )
        self.db_path = db_path
        self._ensure_directory()
        self._ensure_tables()

    def _ensure_directory(self):
        """确保数据目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def _ensure_tables(self):
        """确保必要的表存在"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 创建学校信息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    city TEXT,
                    district TEXT,
                    school_type TEXT,
                    level TEXT,
                    is_public INTEGER,
                    is_key INTEGER,
                    address TEXT,
                    phone TEXT,
                    website TEXT,
                    description TEXT,
                    minScore INTEGER,
                    minRank INTEGER,
                    oneRate REAL,
                    boarding INTEGER,
                    tuition INTEGER,
                    prefecture TEXT,
                    level_detail TEXT,
                    features TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

            # 创建对话消息表（统一的新结构）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    message_type TEXT DEFAULT 'text',
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_session_id
                ON chat_messages(session_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_created_at
                ON chat_messages(created_at)
            """)

            # 创建用户反馈表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    school_id INTEGER,
                    school_name TEXT,
                    feedback_type TEXT,
                    feedback_content TEXT,
                    contact_info TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT,
                    updated_at TEXT,
                    FOREIGN KEY (school_id) REFERENCES schools(id)
                )
            """)

            # 创建更新日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS update_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    update_type TEXT,
                    school_count INTEGER,
                    success_count INTEGER,
                    failure_count INTEGER,
                    details TEXT,
                    created_at TEXT
                )
            """)

            conn.commit()

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # ==================== 学校数据操作 ====================

    def get_school_by_name(self, name: str) -> Optional[Dict]:
        """根据名称查找学校"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM schools
                WHERE name LIKE ? OR name LIKE ?
                LIMIT 1
            """, (f'%{name}%', f'%{name.replace("附中", "师范大学附属中学")}%'))

            row = cursor.fetchone()
            return dict(row) if row else None

    def search_schools(self, keyword: str, limit: int = 10) -> List[Dict]:
        """搜索学校"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM schools
                WHERE name LIKE ? OR city LIKE ? OR prefecture LIKE ?
                ORDER BY is_key DESC, level DESC
                LIMIT ?
            """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))

            return [dict(row) for row in cursor.fetchall()]

    def get_all_schools(self, limit: int = 100) -> List[Dict]:
        """获取所有学校"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM schools
                ORDER BY prefecture, is_key DESC, level DESC
                LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

    # ==================== 对话历史操作 ====================

    def save_message(self, session_id: str, role: str, content: str,
                     message_type: str = 'text', metadata: Dict = None) -> int:
        """
        保存消息

        Args:
            session_id: 会话ID
            role: 角色 (user/assistant/system)
            content: 消息内容
            message_type: 消息类型
            metadata: 附加元数据

        Returns:
            插入的消息ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()
            metadata_json = json.dumps(metadata) if metadata else None

            cursor.execute("""
                INSERT INTO chat_messages
                (session_id, role, content, message_type, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, role, content, message_type, metadata_json, current_time))

            conn.commit()
            return cursor.lastrowid

    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """获取会话历史"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, session_id, role, content, message_type, metadata, created_at
                FROM chat_messages
                WHERE session_id = ?
                ORDER BY created_at ASC
                LIMIT ?
            """, (session_id, limit))

            rows = cursor.fetchall()
            result = []
            for row in rows:
                item = dict(row)
                # 解析metadata JSON
                if item.get('metadata'):
                    try:
                        item['metadata'] = json.loads(item['metadata'])
                    except json.JSONDecodeError:
                        item['metadata'] = None
                result.append(item)

            return result

    def get_recent_conversations(self, limit: int = 100) -> List[Dict]:
        """获取最近的会话列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT session_id,
                       MAX(created_at) as last_activity,
                       COUNT(*) as message_count
                FROM chat_messages
                GROUP BY session_id
                ORDER BY last_activity DESC
                LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def delete_conversation(self, session_id: str) -> int:
        """删除会话"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM chat_messages
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()
            return cursor.rowcount

    # ==================== 反馈操作 ====================

    def save_feedback(self, school_id: Optional[int], school_name: str,
                     feedback_type: str, feedback_content: str,
                     contact_info: str = None) -> int:
        """保存反馈"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO user_feedback
                (school_id, school_name, feedback_type, feedback_content,
                 contact_info, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (school_id, school_name, feedback_type, feedback_content,
                  contact_info, current_time, current_time))

            conn.commit()
            return cursor.lastrowid

    def get_pending_feedback(self) -> List[Dict]:
        """获取待处理的反馈"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM user_feedback
                WHERE status = 'pending'
                ORDER BY created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def update_feedback_status(self, feedback_id: int, status: str) -> bool:
        """更新反馈状态"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()

            cursor.execute("""
                UPDATE user_feedback
                SET status = ?, updated_at = ?
                WHERE id = ?
            """, (status, current_time, feedback_id))

            conn.commit()
            return cursor.rowcount > 0

    # ==================== 统计操作 ====================

    def get_conversation_stats(self) -> Dict[str, Any]:
        """获取对话统计信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 总消息数
            cursor.execute("SELECT COUNT(*) as count FROM chat_messages")
            total_messages = cursor.fetchone()['count']

            # 总会话数
            cursor.execute("SELECT COUNT(DISTINCT session_id) as count FROM chat_messages")
            total_sessions = cursor.fetchone()['count']

            # 用户消息数
            cursor.execute("""
                SELECT COUNT(*) as count FROM chat_messages
                WHERE role = 'user'
            """)
            user_messages = cursor.fetchone()['count']

            # 助手消息数
            cursor.execute("""
                SELECT COUNT(*) as count FROM chat_messages
                WHERE role = 'assistant'
            """)
            assistant_messages = cursor.fetchone()['count']

            # 活跃会话（最近24小时）
            cursor.execute("""
                SELECT COUNT(DISTINCT session_id) as count FROM chat_messages
                WHERE created_at > datetime('now', '-1 day')
            """)
            active_sessions = cursor.fetchone()['count']

            return {
                'total_messages': total_messages,
                'total_sessions': total_sessions,
                'user_messages': user_messages,
                'assistant_messages': assistant_messages,
                'active_sessions_24h': active_sessions,
                'avg_messages_per_session': round(total_messages / total_sessions, 2) if total_sessions > 0 else 0
            }


# 全局实例
db_manager = UnifiedDatabaseManager()
