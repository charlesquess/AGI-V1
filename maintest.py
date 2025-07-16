# import os
# os.environ["TRANSFORMERS_NO_TF"] = "1"
import sys
from config import MODEL_NAME1, MODEL_URL
from intent.intent_detector import IntentDetector
from memory.em_store import EMStore
from memory.sm_store import SMStore
from memory.ms_store import MSStore
from wm.working_memory import WorkingMemory
from dialogue.language_dispatch import LanguageDispatcher
from llm.llm_client import Llama3Client as LLMClient
from memory.abstractor import Abstractor
from utils.tools import Tools
from memory.simpl_retriever import SimpleMemoryRetriever

def main():
    # 1. 启动时检查 Ollama 服务
    try:
        Tools.ensure_ollama_running()
    except RuntimeError as e:
        print(f"启动失败：{e}")
        sys.exit(1)

    # 2. 初始化各组件
    intent_detector = IntentDetector()
    em_store = EMStore()
    sm_store = SMStore()
    ms_store = MSStore()

    # 3. 构建向量索引（启动一次）
    retriever = SimpleMemoryRetriever(em_store, sm_store, ms_store)

    wm = WorkingMemory()
    llm_client = LLMClient(model=MODEL_NAME1, url=MODEL_URL)
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

        # 4. 意图识别
        intents = intent_detector.detect_intent(user_input)
        print(f"Assistant: 我判断你的意图是 {intents}")

        # 5. 向量检索最相关的记忆
        # hits = indexer.query(user_input, top_k=5)
        # 1) 生成检索短语
        query = intent_detector.detect_intent(user_input)
        print(f"检索短语：{query}")
        # 2) 用短语在记忆中检索
        hits = retriever.query(query, top_k=5)
        mems = [
            {
                "source": h["source"],
                "key": h["key"],
                "content": h["content"],
                "timestamp": h["timestamp"]
            }
            for h in hits
        ]
        print("Assistant: 找到相关记忆：")
        for h in hits:
            print(f"  [{h['source']}][{h['timestamp']}]({h['score']:.2f}) {h['content']}")
        wm.load_memories(mems)
        wm.add_context("user", user_input)
        print(f"Assistant: 找到相关记忆：{[h['content'] for h in hits]}")

        # 6. 生成回复
        response = dispatcher.generate_response(user_input, intents, wm)
        print(f"Assistant: {response}\n")
        wm.add_context("assistant", response)

        # 7. 根据意图更新记忆（如果需要）
        if 'record' in intents:
            ts = Tools.get_timestamp()
            em_store.add(ts, user_input)
        elif 'update_goal' in intents:
            ts = Tools.get_timestamp()
            ms_store.add(ts, user_input)
        elif 'update_memory' in intents:
            ts = Tools.get_timestamp()
            sm_store.add(ts, user_input)
        elif 'clear_memory' in intents:
            em_store.clear(); sm_store.clear(); ms_store.clear()
        elif 'abstract' in intents:
            summary = abstractor.abstract(user_input)
            print(f"Assistant: 抽象结果：{summary}")

    sys.exit(0)

if __name__ == '__main__':
    main()
