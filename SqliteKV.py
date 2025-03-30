import sqlite3
import pickle  # 替换为 pickle
import threading
from contextlib import contextmanager

class SQLiteKV:
    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        # 改用 BLOB 类型存储二进制数据
        with self._transaction() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value BLOB)"  # 修改字段类型
            )

    @contextmanager
    def _transaction(self):
        # 事务管理逻辑保持不变
        with self.lock:
            conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None,
            )
            conn.execute("BEGIN")
            try:
                yield conn
                conn.commit()
            except:
                conn.rollback()
                raise
            finally:
                conn.close()

    def set(self, key, value):
        # 使用 pickle 序列化对象
        with self._transaction() as conn:
            conn.execute(
                "REPLACE INTO kv (key, value) VALUES (?, ?)",
                (key, pickle.dumps(value))  # 替换为 pickle
            )

    def get(self, key):
        # 使用 pickle 反序列化对象
        with self._transaction() as conn:
            cursor = conn.execute(
                "SELECT value FROM kv WHERE key = ?",
                (key,)
            )
            result = cursor.fetchone()
            return pickle.loads(result[0]) if result else None  # 替换为 pickle

    def delete(self, key):
        # 删除逻辑保持不变
        with self._transaction() as conn:
            conn.execute("DELETE FROM kv WHERE kv = ?", (key,))
