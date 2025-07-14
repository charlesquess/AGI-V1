import os
import sqlite3
from datetime import datetime

class EMStore:
    """
    Episodic Memory Store，基于 SQLite 持久化到 em.db。
    每次 add() 都插入一条新记录，不会覆盖旧记录。
    """

    def __init__(self, db_path: str = "em.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._ensure_table()

    def _ensure_table(self):
        """创建表结构，如果不存在则新建。"""
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS episodic_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def add(self, key: str, content: str, timestamp: str = None):
        """
        添加一条记忆（每次都插入新记录）。
        :param key: 记忆关键词
        :param content: 记忆内容
        :param timestamp: 时间戳字符串，默认当前时间
        """
        ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO episodic_memory (key, content, timestamp)
        VALUES (?, ?, ?)
        """, (key, content, ts))
        self.conn.commit()

    def get_all(self, key: str):
        """
        获取指定 key 的所有历史记录，按时间升序排列。
        :return: list of (content, timestamp)
        """
        c = self.conn.cursor()
        c.execute("""
        SELECT content, timestamp 
        FROM episodic_memory 
        WHERE key = ? 
        ORDER BY timestamp ASC
        """, (key,))
        return c.fetchall()

    def get_latest(self, key: str):
        """
        获取指定 key 的最新一条记录。
        :return: (content, timestamp) or None
        """
        c = self.conn.cursor()
        c.execute("""
        SELECT content, timestamp 
        FROM episodic_memory 
        WHERE key = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
        """, (key,))
        row = c.fetchone()
        return tuple(row) if row else None

    def has(self, key: str) -> bool:
        """检查是否至少有一条该 key 的记录。"""
        c = self.conn.cursor()
        c.execute("SELECT 1 FROM episodic_memory WHERE key = ? LIMIT 1", (key,))
        return c.fetchone() is not None

    def all_keys(self):
        """
        列出所有出现过的 key（无重复）。
        :return: list of keys
        """
        c = self.conn.cursor()
        c.execute("SELECT DISTINCT key FROM episodic_memory")
        return [row[0] for row in c.fetchall()]

    def clear(self, key: str = None):
        """
        清空所有记忆，或者只清空指定 key 的所有记录。
        :param key: str or None
        """
        c = self.conn.cursor()
        if key is None:
            c.execute("DELETE FROM episodic_memory")
        else:
            c.execute("DELETE FROM episodic_memory WHERE key = ?", (key,))
        self.conn.commit()

    def close(self):
        """关闭数据库连接。"""
        self.conn.close()

if __name__ == '__main__':
    em = EMStore(db_path="em.db")

    # 添加多条同一个 key
    em.add("吃饭", "你上午说你饿了。")
    em.add("吃饭", "你中午去吃了拉面。")
    em.add("花费", "中午的拉面花了 10 块钱。")
    em.add("吃饭", "你下午又饿了。")


    # 查询所有“吃饭”记录
    all_records = em.get_all("吃饭")
    for content, ts in all_records:
        print(f"{ts}  -  {content}")

    # 查询最新记录
    latest = em.get_latest("吃饭")
    print("最新：", latest)

    # 查看有哪些 key
    print("所有 key：", em.all_keys())

    # 删除某个 key 的记录
    # em.clear("吃饭")

    # 全部清空
    # em.clear()