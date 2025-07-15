import sys
from config import MODEL_NAME, MODEL_URL
from intent.intent_detector import IntentDetector
from memory.em_store import EMStore
from memory.sm_store import SMStore
from memory.ms_store import MSStore
from memory.memory_filter import MemoryFilter
from wm.working_memory import WorkingMemory
from dialogue.language_dispatch import LanguageDispatcher
from llm.llm_client import Llama3Client as LLMClient
from memory.abstractor import Abstractor
from utils.tools import Tools

def main():
    # 1. 启动时检查 Ollama 服务
    try:
        Tools.ensure_ollama_running()
    except RuntimeError as e:
        print(f"启动失败：{e}")
        sys.exit(1)
    intent_detector = IntentDetector()
    em_store = EMStore()
    sm_store = SMStore()
    ms_store = MSStore()

    # ←—— 关键修改：直接传 Store 实例
    memory_filter = MemoryFilter(em_store, sm_store, ms_store)

    wm = WorkingMemory()
    llm_client = LLMClient()  # 会自动读取 config.MODEL_NAME 和 MODEL_URL
    dispatcher = LanguageDispatcher(llm_client)
    abstractor = Abstractor(em_store, sm_store)

    print("欢迎使用 AGI-V1 助手！输入 'exit' 或 'quit' 退出。")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input or user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        intents = intent_detector.detect_intent(user_input)
        print(f"Assistant: 你说的是{intents}。")

        relevant_memories = memory_filter.filter(intents, user_input)
        wm.load_memories(relevant_memories)
        print(f"Assistant: 相关记忆：{relevant_memories}")

        response = dispatcher.generate_response(user_input, intents, wm)
        print(f"Assistant: {response}\n")

        if 'record' in intents:
            ts = Tools.get_timestamp()
            em_store.add(ts, user_input)
        elif 'update_goal' in intents:
            ts = Tools.get_timestamp()
            ms_store.add(ts, user_input)

    sys.exit(0)

if __name__ == '__main__':
    main()
