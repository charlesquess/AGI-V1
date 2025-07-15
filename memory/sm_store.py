# memory/sm_store.py

import sqlite3
from datetime import datetime

class SMStore:
    """
    Semantic Memory Store，基于 SQLite 持久化到 sm.db。
    每个 key 只保留一条记录；重复 add 同一 key 会更新内容和时间戳。
    """

    def __init__(self, db_path: str = "sm.db"):
        """
        打开（或创建）SQLite 数据库，并确保表结构存在。
        """
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._ensure_table()

    def _ensure_table(self):
        """
        创建表 episodic_memory（如果不存在）。
        key 设置为 PRIMARY KEY，以便重复插入时自动替换。
        """
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS semantic_memory (
            key TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def add(self, key: str, content: str, timestamp: str = None):
        """
        添加或更新一条语义记忆。
        :param key: 概念或术语的标识符
        :param content: 该概念的定义或描述
        :param timestamp: 时间戳，默认为当前时间
        """
        ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO semantic_memory(key, content, timestamp)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET
            content = excluded.content,
            timestamp = excluded.timestamp
        """, (key, content, ts))
        self.conn.commit()

    def get(self, key: str):
        """
        获取指定 key 的定义和时间戳。
        :return: (content, timestamp) 或 None
        """
        c = self.conn.cursor()
        c.execute("""
        SELECT content, timestamp
        FROM semantic_memory
        WHERE key = ?
        """, (key,))
        row = c.fetchone()
        return tuple(row) if row else None

    def has(self, key: str) -> bool:
        """
        检查是否存在该概念。
        """
        c = self.conn.cursor()
        c.execute("SELECT 1 FROM semantic_memory WHERE key = ? LIMIT 1", (key,))
        return c.fetchone() is not None

    def all(self):
        """
        获取所有概念定义，返回 dict：{ key: (content, timestamp), ... }
        """
        c = self.conn.cursor()
        c.execute("SELECT key, content, timestamp FROM semantic_memory")
        return {k: (cont, ts) for k, cont, ts in c.fetchall()}

    def remove(self, key: str):
        """
        删除指定概念。
        """
        c = self.conn.cursor()
        c.execute("DELETE FROM semantic_memory WHERE key = ?", (key,))
        self.conn.commit()

    def clear(self):
        """
        清空所有语义记忆。
        """
        c = self.conn.cursor()
        c.execute("DELETE FROM semantic_memory")
        self.conn.commit()

    def close(self):
        """
        关闭数据库连接。
        """
        self.conn.close()
    
    def get_all_texts(self) -> list[str]:
        """
        返回所有语义记忆的文本内容列表，用于向量化。
        """
        c = self.conn.cursor()
        c.execute("SELECT content FROM semantic_memory")
        return [row[0] for row in c.fetchall()]

    def get_all_keys(self):
        """
        列出所有出现过的 key（无重复）。
        :return: list of keys
        """
        c = self.conn.cursor()
        c.execute("SELECT DISTINCT key FROM episodic_memory")
        return [row[0] for row in c.fetchall()]

if __name__ == '__main__':
    sm = SMStore()              # 打开（或创建）sm.db
    sm.add("地球", "地球是太阳系的第三颗行星。")
    sm.add("重力", "重力是物体间的引力。")
    sm.add("睡眠", "用户工作日睡眠时长为5小时，休息日睡眠时长为8小时。可以推荐用户每天早睡，或者给用户安排一个午休时间。或者用户自行更新睡眠时间。")  # 更新

    # 查询
    print(sm.get("地球"))
    # ('地球是太阳系的第三颗行星。', '2025-07-14 15:22:10')
    print(sm.get("睡眠"))
    sm.add("睡眠", "用户工作日睡眠时长为5小时，休息日睡眠时长为8小时。可以给用户安排一个午休时间。或者用户自行更新睡眠时间。")
    print(sm.get("睡眠"))
    sm.add("睡眠", "用户工作日睡眠时长为5小时，休息日睡眠时长为8小时。用户习惯在下午6点睡一会儿，或许这是用户不能早睡的原因，可以询问用户是否于这个时间点睡觉更舒服")
    print(sm.get("睡眠"))

    # 检查存在
    print(sm.has("重力"))        # True

    # 列出所有
    print(sm.all())
    # {'地球': ('...', '...'), '重力': ('...', '...')}

    # 删除一个
    sm.remove("重力")

    # 清空
    sm.clear()

    sm.close()