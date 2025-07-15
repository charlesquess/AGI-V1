# memory/ms_store.py

import sqlite3
from datetime import datetime

class MSStore:
    """
    Mission State Store，基于 SQLite 持久化到 ms.db。
    每个 key 只保留一条当前状态；重复 add 同一 key 会更新内容和时间戳。
    """

    def __init__(self, db_path: str = "ms.db"):
        """
        打开（或创建）SQLite 数据库，并确保表结构存在。
        """
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._ensure_table()

    def _ensure_table(self):
        """
        创建表 mission_state，如果不存在则新建。
        key 设置为 PRIMARY KEY，以便重复插入时自动替换。
        """
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS mission_state (
            key TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def add(self, key: str, content: str, timestamp: str = None):
        """
        添加或更新一条 mission state。
        :param key: 任务或目标标识
        :param content: 该任务当前状态或描述
        :param timestamp: 时间戳，默认当前时间
        """
        ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c = self.conn.cursor()
        c.execute("""
        INSERT INTO mission_state(key, content, timestamp)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET
            content = excluded.content,
            timestamp = excluded.timestamp
        """, (key, content, ts))
        self.conn.commit()

    def get(self, key: str):
        """
        获取指定 key 的 mission content 和时间戳。
        :return: (content, timestamp) 或 None
        """
        c = self.conn.cursor()
        c.execute("""
        SELECT content, timestamp
        FROM mission_state
        WHERE key = ?
        """, (key,))
        row = c.fetchone()
        return tuple(row) if row else None

    def has(self, key: str) -> bool:
        """
        检查是否存在该 mission key。
        """
        c = self.conn.cursor()
        c.execute("SELECT 1 FROM mission_state WHERE key = ? LIMIT 1", (key,))
        return c.fetchone() is not None

    def all(self):
        """
        获取所有 mission state，返回 dict：{ key: (content, timestamp), ... }
        """
        c = self.conn.cursor()
        c.execute("SELECT key, content, timestamp FROM mission_state")
        return {k: (cont, ts) for k, cont, ts in c.fetchall()}

    def remove(self, key: str):
        """
        删除指定 mission key。
        """
        c = self.conn.cursor()
        c.execute("DELETE FROM mission_state WHERE key = ?", (key,))
        self.conn.commit()

    def clear(self):
        """
        清空所有 mission state。
        """
        c = self.conn.cursor()
        c.execute("DELETE FROM mission_state")
        self.conn.commit()

    def close(self):
        """
        关闭数据库连接。
        """
        self.conn.close()

    def get_all_texts(self) -> list[str]:
        """
        返回所有目标记忆的文本内容列表，用于向量化。
        """
        c = self.conn.cursor()
        c.execute("SELECT content FROM mission_state")
        return [row[0] for row in c.fetchall()]

    def get_all_keys(self) -> list[str]:
        c = self.conn.cursor()
        c.execute("SELECT DISTINCT key FROM mission_state")
        return [row[0] for row in c.fetchall()]

    def get_all_records(self) -> list[tuple[str, str, str]]:
        c = self.conn.cursor()
        c.execute("SELECT key, content, timestamp FROM mission_state")
        return c.fetchall()

if __name__ == '__main__':
    ms = MSStore() 

    # 设置或更新一个目标
    ms.add("写论文", "正在撰写绪论部分。")
    # 再次 update
    ms.add("写论文", "已完成绪论，开始写方法章节。")

    # 查询
    print(ms.get("写论文"))
    # ('已完成绪论，开始写方法章节。', '2025-07-14 16:30:45')

    # 检查
    print(ms.has("写论文"))  # True

    # 列出所有
    print(ms.all())
    # {'写论文': ('已完成绪论，开始写方法章节。', '2025-07-14 16:30:45')}

    # 删除
    ms.remove("写论文")

    # 清空
    ms.clear()

    ms.close()