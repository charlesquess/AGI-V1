"""

语言模型调用模块
    该模块用于调用语言模型API，生成自然语言响应
    该模块需要调用OpenAI API，需要在config.py中配置API_KEY和API_URL
"""
import sys
from config import API_KEY, API_URL
from llm.llm_client import LLMClient # 导入语言模型客户端
from memory.em_store import EMStore # 导入事实记忆体
from memory.sm_store import SMStore # 导入知识记忆体
from memory.ms_store import MSStore # 导入目标记忆体
from memory.memory_filter import MemoryFilter # 导入记忆筛选器
from wm.working_memory import WorkingMemory # 导入工作记忆体
from utils.tools import Tools # 导入工具类

class IntentDetector:
    """
    意图识别模块
    该模块用于识别用户输入的意图
    """
    def __init__(self):
        self.llm_client = LLMClient(API_KEY, API_URL)
        self.em_store = EMStore()
        self.sm_store = SMStore()
        self.ms_store = MSStore()
        self.memory_filter = MemoryFilter(self.em_store, self.sm_store, self.ms_store)
        self.working_memory = WorkingMemory()
        # 定义意图关键词字典
        self.intent_keywords = {
            "record": ["记住", "记录", "保存"],
            "update_goal": ["目标", "计划", "设定目标"],
            "question": ["什么是", "为什么", "如何", "？", "吗"],
            "greet": ["你好", "嗨", "您好"],
            "farewell": ["再见", "拜拜", "退出", "离开"]
        }
        self.user_input = None

    def detect_intent(self, user_input):
        """
        识别用户输入的意图
        :param user_input: 用户输入的文本
        :return: 识别出的意图
        """
        # 将用户输入转换为小写，便于匹配
        self.user_input = user_input.lower()
        print(f"用户输入：{self.user_input}")
        # intent 是多个意图的集合
        intents = set()
        # 遍历意图关键词字典，检查用户输入是否包含关键词
        for intent, keywords in self.intent_keywords.items():
            if any(keyword in self.user_input for keyword in keywords):
                intents.add(intent)
        # 若有多个意图，则返回多个意图
        if len(intents) > 0:
            return intents
        # 若没有意图，则返回“不明确”
        return "unknown"
    
    def update_memory(self, intent):
        """
        根据识别出的意图检索相关记忆并更新工作记忆
        :param user_input: 用户输入的文本
        :param intent: 识别出的意图
        """
        relevant_memories = self.memory_filter.filter(self.user_input)
        self.working_memory.load_memories(relevant_memories)
        timestamp = Tools.get_timestamp() # 获取当前时间戳

        # 根据意图检索相应的记忆存储
        if intent == 'record':
            # 将用户输入和时间戳添加到事实记忆体
            self.em_store.add_memory(self.user_input, timestamp)
        elif intent == 'update_goal':
            self.ms_store.add_goal(self.user_input, Tools.get_timestamp())
        # 其他意图可以在这里添加处理逻辑

    def generate_response(self, prompt, model="gpt-3.5-turbo", temperature=0.7):
        """
        调用语言模型生成响应
        :param prompt: 用户输入的提示
        :param model: 使用的语言模型
        :param temperature: 生成文本的温度参数
        :return: 生成的响应文本
        """
        response = self.llm_client.call_llm(prompt, model, temperature)
        return response.get("text", "抱歉，我无法处理该请求。")

class LanguageDispatcher:
    """
    语言调度器模块
    该模块用于将用户输入的文本分派给相应的模块进行处理
    """
    def __init__(self, intent_detector):
        self.intent_detector = intent_detector

    def dispatch(self, user_input):
        """
        分派用户输入到意图识别器
        :param user_input: 用户输入的文本
        :return: 识别出的意图和生成的响应
        """
        intent = self.intent_detector.detect_intent(user_input)
        self.intent_detector.update_memory(intent)
        response = self.intent_detector.generate_response(user_input)
        return intent, response
