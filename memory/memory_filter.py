# 记忆筛选器模块

class MemoryFilter:
    def __init__(self, em_store, sm_store, ms_store):
        self.em_store = em_store
        self.sm_store = sm_store
        self.ms_store = ms_store

    def filter(self, memory):
        # 筛选出符合条件的记忆
        filtered_memory = []
        for item in memory:
            if item in self.em_store:
                filtered_memory.append(item)
            elif item in self.sm_store:
                filtered_memory.append(item)
            elif item in self.ms_store:
                filtered_memory.append(item)
        return filtered_memory
