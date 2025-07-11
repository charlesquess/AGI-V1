# 工作记忆结构模块

class WorkingMemory:
    """
    工作记忆结构模块，负责管理当前对话的工作记忆。
    包括加载相关记忆、更新工作记忆等功能。
    """

    def __init__(self):
        self.memories = []

    def load_memories(self, memories):
        """
        加载相关记忆到工作记忆中。
        :param memories: 需要加载的记忆列表
        """
        self.memories.extend(memories)

    def clear(self):
        """
        清空工作记忆。
        """
        self.memories.clear()

    def update_memory(self, memory):
        """
        更新工作记忆。
        :param memory: 需要更新的记忆
        """
        self.memories.append(memory)

    def get_memories(self):
        """
        获取当前工作记忆中的所有记忆。
        :return: 当前工作记忆列表
        """
        return self.memories
    
    def __str__(self):
        return str(self.memories)
    