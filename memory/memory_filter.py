# 记忆筛选器模块

class MemoryFilter:
    def __init__(self, em_store, sm_store, ms_store):
        """
        初始化 MemoryFilter
        :param em_store: dict，事实记忆体（episodic memory）
        :param sm_store: dict，语义记忆体（semantic memory）
        :param ms_store: dict，目标追踪模块（mission state memory）
        """
        self.em_store = em_store
        self.sm_store = sm_store
        self.ms_store = ms_store

    def filter(self, intents, user_input):
        """
        根据意图和用户输入筛选匹配的记忆项
        :param intents: list，表示当前识别出的用户意图关键词或标签
        :param user_input: str，原始用户输入
        :return: list，符合意图的记忆项内容
        """
        print(f"MemoryFilter: filter method called with intents: {intents}, user_input: {user_input}")

        filtered_memory = []

        for intent in intents:
            print(f"\n检索意图: {intent}")

            if intent in self.em_store:
                print("\u2714 匹配到事实记忆体")
                filtered_memory.append({"source": "em_store", "intent": intent, "content": self.em_store[intent]})

            if intent in self.sm_store:
                print("\u2714 匹配到语义记忆体")
                filtered_memory.append({"source": "sm_store", "intent": intent, "content": self.sm_store[intent]})

            if intent in self.ms_store:
                print("\u2714 匹配到目标追踪模块")
                filtered_memory.append({"source": "ms_store", "intent": intent, "content": self.ms_store[intent]})

        return filtered_memory