# 抽象记忆层


class Abstractor:
    def __init__(self, memory):
        self.memory = memory

    def em_memory_to_sm_memory(self, em_memory):
        # 分析事实记忆并转换成抽象记忆
        # 例如：频繁出现"麦当劳"→"早餐偏好为麦当劳"
        pass

    def em_memory_to_ms_memory(self, em_memory):
        # 分析事实记忆并转换成目标追踪记忆
        # 例如： 某天用户说。需要减肥。 ——> 减肥
        pass

    def should_abstract(self, em_count):
        # 判断是否需要进行抽象记忆
        return em_count > 10