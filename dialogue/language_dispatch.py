# 语言调度器模块
from llm.llm_client import Llama3Client

class LanguageDispatcher:
    """
    负责构建多角色对话消息 (roles)、调用 LLM 并返回最终回复。
    """

    def __init__(self, llm_client, system_prompt=None, abstractor=None, default_model="gpt-3.5-turbo"):
        self.llm = Llama3Client(model="llama3", url="http://localhost:11434/api/chat")
        self.system_prompt = system_prompt or "你是一名智能助手。"
        self.abstractor = abstractor
        self.default_model = default_model
        self.context = []
        self.memories = ""
    
    def generate_response(
        self,
        user_input: str,
        intents: list[str],
        working_memory,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> str:
        """
        构造 messages 列表并调用 llm.chat()。
        :param user_input: 用户输入
        :param intents: 意图列表
        :param working_memory: WorkingMemory 实例
        :param temperature: 采样温度
        :param max_tokens: 最大 tokens
        :return: LLM 返回的回复
        """
        # —— 1. 可选地用抽象器生成抽象记忆 —— 
        memory_section = working_memory.memories
        if self.abstractor:
            abstracts = []
            for key in intents:
                summary = self.abstractor.abstract(key)
                if summary:
                    abstracts.append(f"- {key}：{summary}")
            if abstracts:
                memory_section = "抽象记忆：\n" + "\n".join(abstracts)

        # —— 2. 准备上下文和意图字符串，生成 memory_section 文本内容 —— 
        if isinstance(memory_section, list):
            # 提取每条记忆的 content 字段
            memory_text = "\n".join(
                m["content"] if isinstance(m, dict) else str(m)
                for m in memory_section
            )
        else:
            memory_text = str(memory_section)

        # —— 3. 构造 messages —— 
        messages = [
            {"role": "system",    "content": self.system_prompt},
            {"role": "assistant", "content": "历史记忆：\n" + memory_text},
            {"role": "assistant", "content": "对话上下文：\n" + "\n".join(working_memory.context)},
            {"role": "assistant", "content": f"当前意图：{', '.join(intents)}"},
            {"role": "user",      "content": user_input},
        ]
        # —— 4. 调用 LLMClient.chat —— 
        try:
            # 这里假设你的 LLMClient.chat 接口签名为 chat(messages=..., model=..., ...)
            return self.llm.chat(
                messages=messages,
                model=self.default_model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as err:
            print(f"[LanguageDispatcher] LLM 调用失败：{err}")
            return "抱歉，处理请求失败，请稍后重试。"