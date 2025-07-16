# import os
# os.environ["TRANSFORMERS_NO_TF"] = "1"
import sys
from config import MODEL_NAME1, MODEL_URL, SYSTEM_PROMPT
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
import re

def strip_think_tags(text: str) -> str:
    # 删除 <think>...</think> 及其中所有内容
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

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
    dispatcher = LanguageDispatcher(llm_client,system_prompt=SYSTEM_PROMPT)
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
        # 删除think标签
        intents = strip_think_tags(intents)
        print(f"Assistant: 我判断你的意图是 {intents}")

        # 5. 向量检索最相关的记忆
        # hits = indexer.query(user_input, top_k=5)
        # 1) 生成检索短语
        query = intents
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
        print(f"user_input: {user_input}, intents: {intents},wm.context: {wm}")
        response = dispatcher.generate_response(user_input, intents, wm)
        print(f"Assistant: {response}\n")
        wm.add_context("assistant", response)
        # —— 自动记录用户输入到 Episodic Memory —— 
        ts = Tools.get_timestamp()
        # 这里把意图列表也当作 key 前缀，方便检索
        em_store.add(key="user:" + ";".join(intents), content=user_input, timestamp=ts)

        # —— 自动记录助手回复到 Episodic Memory（可选） —— 
        ts2 = Tools.get_timestamp()
        em_store.add(key="assistant:" + ";".join(intents), content=response, timestamp=ts2)

        # —— 定期生成摘要并存入 Semantic Memory —— 
        # 当工作记忆的轮次达到阈值时，摘要并清理
        if len(wm.context) >= 10:
            # 摘要最近 10 条
            summary = abstractor.abstract_conversation(wm.context[-10:])
            sm_store.add(key="conversation_summary", content=summary, timestamp=Tools.get_timestamp())
            # 可选择清空旧上下文
            wm.context = wm.context[-2:]

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
