import sqlite3
import threading

class ConnectionPool:
    """数据库连接池"""
    
    def __init__(self, db_file, max_connections=5):
        """初始化连接池
        
        Args:
            db_file (str): 数据库文件路径
            max_connections (int): 最大连接数
        """
        self.db_file = db_file
        self.max_connections = max_connections
        self.connections = []
        self.lock = threading.Lock()
        
        # 初始化连接池
        for _ in range(min(3, max_connections)):
            conn = sqlite3.connect(db_file, check_same_thread=False)
            self.connections.append(conn)
    
    def get_connection(self):
        """获取数据库连接"""
        with self.lock:
            if self.connections:
                return self.connections.pop()
            else:
                # 创建新连接
                return sqlite3.connect(self.db_file, check_same_thread=False)
    
    def return_connection(self, conn):
        """归还数据库连接"""
        with self.lock:
            if len(self.connections) < self.max_connections:
                self.connections.append(conn)
            else:
                # 超过最大连接数，关闭连接
                conn.close()
    
    def close_all(self):
        """关闭所有连接"""
        with self.lock:
            for conn in self.connections:
                try:
                    conn.close()
                except:
                    pass
            self.connections = []

# 数据库文件路径
import os
data_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(data_dir, exist_ok=True)
db_file = os.path.join(data_dir, 'school_platform.db')

# 创建全局连接池实例
conn_pool = ConnectionPool(db_file, max_connections=10)

# 获取数据库连接的便捷函数
def get_db_connection():
    """获取数据库连接"""
    return conn_pool.get_connection()
