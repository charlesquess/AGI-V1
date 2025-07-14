import sys
from config import *
from intent.intent_detector import IntentDetector
from memory.em_store import EMStore
from memory.sm_store import SMStore
from memory.ms_store import MSStore
from memory.memory_filter import MemoryFilter
from memory.abstractor import Abstractor
from wm.working_memory import WorkingMemory
from dialogue.language_dispatch import LanguageDispatcher
from llm.llm_client import LLMClient
from utils.tools import Tools
from config import API_KEY, API_URL


def main():
    """
    主入口函数，负责命令行交互、意图识别、记忆检索、LLM调度与记忆更新。
    """
    # 初始化模块
    intent_detector = IntentDetector()
    em_store = EMStore()
    sm_store = SMStore()
    ms_store = MSStore()
    api_key = API_KEY
    api_url = API_URL
    memory_filter = MemoryFilter(em_store, sm_store, ms_store)
    wm = WorkingMemory()
    llm_client = LLMClient(api_key, api_url)
    dispatcher = LanguageDispatcher(llm_client)
    abstractor = Abstractor(em_store)

    print("欢迎使用 AGI-V1 助手！输入 'exit' 或 'quit' 退出。")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        # 意图识别
        intent = intent_detector.detect_intent(user_input)

        # 记忆检索与工作记忆填充
        relevant_memories = memory_filter.filter(intent, user_input)
        wm.load_memories(relevant_memories)

        # 调度生成回复
        response = dispatcher.generate_response(user_input, intent, wm)
        print(f"Assistant: {response}\n")

        # 根据意图更新记忆
        # 判断意图并更新相应的记忆存储
        if intent == 'record':
            timestamp = Tools.tooget_timestamp()
            em_store.add_memory(user_input, timestamp)
        elif intent == 'update_goal':
            ms_store.add_goal(user_input, Tools.get_timestamp())
        # Summary memory 可在 em_store 内部或单独触发

    sys.exit(0)


if __name__ == '__main__':
    main()
