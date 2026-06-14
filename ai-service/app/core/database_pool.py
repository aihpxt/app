"""数据库连接池管理"""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
import os
import logging
from contextlib import contextmanager
from typing import Generator

_APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ABS_DB_PATH = os.path.join(_APP_DIR, "app.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_ABS_DB_PATH}")

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""

    def __init__(self, database_url: str = DATABASE_URL):
        self.database_url = database_url

        # 根据数据库类型选择连接池
        if database_url.startswith("sqlite"):
            # SQLite不支持连接池
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=NullPool,
                echo=False
            )
        else:
            # 其他数据库使用连接池
            self.engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )

        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """提供事务作用域的会话"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def init_tables(self):
        """初始化数据库表"""
        try:
            # 导入模型并创建表
            from app.models.user import Base, User
            Base.metadata.create_all(bind=self.engine, tables=[User.__table__])
            logger.info("数据库表初始化成功")
        except Exception as e:
            logger.warning(f"数据库表初始化失败: {e}")

    def close(self):
        """关闭引擎"""
        self.engine.dispose()

# 全局数据库管理器
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """获取数据库管理器"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.init_tables()  # 自动初始化表
    return _db_manager

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话的依赖项"""
    db_manager = get_db_manager()
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()

# SQLite优化：启用WAL模式
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """设置SQLite优化参数"""
    if "sqlite" in type(dbapi_conn).__module__:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB缓存
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()
