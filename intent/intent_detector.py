class IntentDetector:
    """
    Intent Detector: 基于关键字或规则识别用户输入的意图。
    可以扩展为调用 LLM 实现更复杂的意图识别。
    """
    def __init__(self):
        # 关键字到意图的映射
        self.keyword_intent_map = {
            # 记忆相关
            '记忆': 'record',
            '记录': 'record',
            # 目标更新
            '目标': 'update_goal',
            '计划': 'update_goal',
            # 查询记忆
            '回忆': 'query_memory',
            '检索': 'query_memory',
            # 默认交互
            '你好': 'greet',
            'hi': 'greet',
            '再见': 'farewell',
            'bye': 'farewell',
            # 其他意图
            '吃饭' :  '吃饭'
        }

    def detect_intent(self, text):
        """
        根据文本内容返回一组意图标签。
        :param text: str，用户输入
        :return: list，意图标签
        """
        text_lower = text.lower()
        intents = []
        for keyword, intent in self.keyword_intent_map.items():
            if keyword in text_lower:
                intents.append(intent)

        # 如果没有匹配到任何关键字，使用默认意图
        if not intents:
            intents.append('default')
        return intents