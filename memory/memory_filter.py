# 记忆筛选器模块

class MemoryFilter:
    def __init__(self, em_store, sm_store, ms_store):
        self.em_store = em_store
        self.sm_store = sm_store
        self.ms_store = ms_store

    def filter(self, memory):
        # 筛选出符合条件的记忆
        # memory 是一个列表，包含了需要筛选的记忆项
        filtered_memory = []
        # 遍历 memory 列表，检查每个记忆项是否在各个存储中
        # 如果在事实记忆体、语义记忆体或目标追踪模块中存在所需相关项，则添加到 filtered_memory 列表中
        for item in memory:
            # 遍历事实记忆体
            if item in self.em_store:
                filtered_memory.append(item)
            # 遍历语义记忆体
            elif item in self.sm_store:
                filtered_memory.append(item)
            # 遍历目标追踪模块
            elif item in self.ms_store:
                filtered_memory.append(item)
        return filtered_memory
