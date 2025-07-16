# 抽象记忆层


from llm.llm_client import Llama3Client
from config import MODEL_NAME1, MODEL_URL
from memory.sm_store import SMStore
from typing import List, Dict

class Abstractor:
    """
    抽象器模块：从 EMStore 中提取历史事实并总结抽象概念，写入 SMStore。
    """

    def __init__(self, em_store, sm_store=None):
        self.em_store = em_store
        self.sm_store = sm_store or SMStore()
        self.llm = Llama3Client()

    def abstract(self, key: str):
        """
        对指定 key（如“吃饭”、“学习”等）对应的历史事实进行抽象总结。
        :param key: 要抽象的意图或主题
        :return: 抽象总结字符串（并已写入 SMStore）
        """
        # 从 EMStore 中获取所有历史记录
        records = self.em_store.get_all(key)
        if not records:
            print(f"[Abstractor] No episodic records found for key: {key}")
            return None

        # 构建提示词，输入给 LLM
        memory_text = "\n".join([f"- {content}（{ts}）" for content, ts in records])
        prompt = f"""
            你是一名智能助理，请根据以下历史事实，为用户生成一个抽象总结。总结应简洁、概括，并包含用户的偏好或习惯。

            历史事实：
            {memory_text}

            请用一句简短的话总结这个主题：“{key}”。
            """

        # 请求 LLM
        summary = self.llm.chat(prompt).strip()

        # 存入 SMStore（语义记忆体）
        self.sm_store.add(key, summary)

        print(f"[Abstractor] 抽象结果已写入语义记忆体: {summary}")
        return summary
    
    def abstract_conversation(self, messages: List[Dict[str,str]]) -> str:
        """
        messages: [{"role":"user"/"assistant","text":..., "ts":...}, ...]
        用 LLM 做一个简短摘要
        """
        # 拼成 prompt
        convo = "\n".join(f"{m['role']}: {m['text']}" for m in messages)
        prompt = (
            "请对下面的对话进行简洁中文摘要，抓取核心信息：\n\n" + convo
        )
        return self.llm.chat(
            messages=[{"role":"user","content":prompt}],
            temperature=0.3,
            max_tokens=150
        ).strip()
    
if __name__ == '__main__':
    from memory.em_store import EMStore
    from memory.sm_store import SMStore

    em = EMStore()
    sm = SMStore()
    ab = Abstractor(em, sm)

    # 示例调用
    summary = ab.abstract("吃饭")
    print("抽象总结:", summary)

    # 现在可以用 sm.get("吃饭") 查看抽象结果