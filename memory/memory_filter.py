class MemoryFilter:
    """
    MemoryFilter：接收三个持久化记忆体实例，按意图筛选并返回结构化记忆列表。
    """

    def __init__(self, em_store, sm_store, ms_store):
        """
        :param em_store: EMStore 实例（持久化到 em.db）
        :param sm_store: SMStore 实例（持久化到 sm.db）
        :param ms_store: MSStore 实例（持久化到 ms.db）
        """
        self.em_store = em_store
        self.sm_store = sm_store
        self.ms_store = ms_store

    def filter(self, intents, user_input=None):
        """
        根据意图列表，从各记忆体中检索并返回相关记忆项。
        :param intents: list[str] 当前意图标签
        :param user_input: str（可选），原始用户输入
        :return: list[dict] 每个 dict 包含: source, key, content, timestamp
        """
        print(f"MemoryFilter: filter called with intents={intents!r}, user_input={user_input!r}")
        results = []

        for intent in intents:
            # 事实记忆体：取出所有历史记录
            if self.em_store.has(intent):
                records = self.em_store.get_all(intent)
                for content, ts in records:
                    results.append({
                        "source": "episodic_memory",
                        "key": intent,
                        "content": content,
                        "timestamp": ts
                    })
                print(f" ✔ EMStore: {len(records)} records for key {intent!r}")

            # 语义记忆体：只取最新一条
            if self.sm_store.has(intent):
                rec = self.sm_store.get(intent)  # (content, timestamp)
                results.append({
                    "source": "semantic_memory",
                    "key": intent,
                    "content": rec[0],
                    "timestamp": rec[1]
                })
                print(f" ✔ SMStore: latest for key {intent!r} → {rec}")

            # 目标记忆体：只取最新一条
            if self.ms_store.has(intent):
                rec = self.ms_store.get(intent)
                results.append({
                    "source": "mission_memory",
                    "key": intent,
                    "content": rec[0],
                    "timestamp": rec[1]
                })
                print(f" ✔ MSStore: latest for key {intent!r} → {rec}")

        return results

if __name__ == '__main__':
    from memory.em_store import EMStore
    from memory.sm_store import SMStore
    from memory.ms_store import MSStore
    from memory.memory_filter import MemoryFilter

    # 初始化各记忆体
    em = EMStore()
    sm = SMStore()
    ms = MSStore()

    # 插入一些测试数据
    em.add("吃饭", "你上午说过想吃早餐。")
    em.add("吃饭", "你中午吃了寿司。")
    sm.add("天气", "今天多云，适合出门散步。")
    ms.add("写论文", "已完成绪论，准备开始方法章节。")

    # 筛选
    filter = MemoryFilter(em, sm, ms)
    intents = ["吃饭", "天气", "写论文"]
    mems = filter.filter(intents, user_input="我饿了，接下来该做什么？")

    for m in mems:
        print(f"[{m['source']}][{m['timestamp']}][{m['key']}] {m['content']}")