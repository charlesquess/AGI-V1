# 事实记忆体模块

from memory.sm_store import SMStore
from memory.ms_store import MSStore

class EMStore:
    def __init__(self):
        self.memory = []
        self.sm_store = SMStore()
        self.ms_store = MSStore()

    def add_memory(self, text, timestamp):
        # 添加记忆到事实记忆体
        self.memory.append({"text": text, "timestamp": timestamp})

    def select_memory(self):
        # 根据需要内容选择记忆
        # 这里可以实现更复杂的选择逻辑
        return self.memory[-1]

    def compress_memory(self):
        # 调取记忆筛选器进行压缩事实记忆体到知识记忆体或目标记忆体中
        # 压缩完成后清除该条事实记忆
        # 这里可以实现更复杂的压缩逻辑
        if self.memory:
            compressed_memory = self.memory.pop(0)
            return compressed_memory
        else:
            return None

    def clear_memory(self):
        # 清除不需要的记忆
        self.memory.clear()