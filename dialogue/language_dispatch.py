# 语言调度器模块

class LanguageDispatcher:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def generate_response(self, user_input, intent, working_memory):
        # 根据意图和工作记忆生成响应
        if intent == 'small_talk':
            return self.llm_client.generate_response(user_input)
        elif intent == 'task_management':
            return self.llm_client.generate_response(user_input)
        else:
            return "抱歉，我无法处理该请求。"
    
    def get_intent(self, user_input):
        # 识别用户输入的意图
        return self.llm_client.get_intent(user_input)
    
    def get_entities(self, user_input):
        # 识别用户输入的实体
        return self.llm_client.get_entities(user_input)
