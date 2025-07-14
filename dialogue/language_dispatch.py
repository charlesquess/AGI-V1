# 语言调度器模块

class LanguageDispatcher:
    """
    负责构建多角色对话消息 (roles)、调用 LLM 并返回最终回复。
    """

    def __init__(self, llm_client, system_prompt: str = None, abstractor=None, default_model: str = "gpt-3.5-turbo"):
        """
        :param llm_client: LLMClient 或 LocalLLMClient 实例
        :param system_prompt: 系统提示词
        :param abstractor: Abstractor 实例（可选）
        :param default_model: 默认模型名
        """
        self.llm = llm_client
        self.system_prompt = system_prompt or "你是一名智能助手。"
        self.abstractor = abstractor
        self.default_model = default_model

    def __init__(self):
        self.context = []    # 保存历史对话
        self.memories = ""   # 摘要后的记忆文本

    def load_memories(self, memory_items):
        if isinstance(memory_items, list):
            # 只取 content 字段构建字符串
            self.memories = "\n".join(item["content"] for item in memory_items)
        else:
            self.memories = str(memory_items)

    def add_context(self, text):
        self.context.append(text)

    def get_prompt(self, user_input, intents):
        # 如果你想继续使用这个，就保留
        parts = [
            "历史记忆：",
            self.memories,
            "\n对话上下文：",
            "\n".join(self.context),
            f"\n当前意图：{', '.join(intents)}",
            f"\n用户输入：{user_input}",
            "\n助手回复："
        ]
        return "\n".join(parts)
        
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

        # —— 2. 准备上下文和意图字符串 —— 
        context_str = "\n".join(working_memory.context)
        intent_str  = ", ".join(intents)

        # —— 3. 构造 OpenAI-compatible messages 格式 —— 
        messages = [
            {"role": "system",    "content": self.system_prompt},
            {"role": "assistant", "content": "历史记忆：\n" + memory_section},
            {"role": "assistant", "content": "对话上下文：\n" + context_str},
            {"role": "assistant", "content": f"当前意图：{intent_str}"},
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