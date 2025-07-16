# 语言调度器模块
from llm.llm_client import Llama3Client


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
        self.system_prompt = system_prompt or "你是用户的私人助理AGI，你的所有回复应该是更像一个私人管家，称号用户为先生，语气温柔一点。"
        self.abstractor = abstractor
        self.default_model = default_model

    def generate_response(
        self,
        user_input: str,
        intents: list[str],
        working_memory,  # 传入 WorkingMemory 实例
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
        # —— 1. 准备记忆块和历史对话块 —— 
        mem_text = working_memory.get_memories_text()
        ctx_text = working_memory.get_context_text()
        intent_str = ", ".join(intents)

        # —— 2. 构造 OpenAI-compatible messages 格式 —— 
        messages = [
            {"role": "system",    "content": self.system_prompt},
            {"role": "assistant", "content": "历史记忆：\n" + (mem_text or "（无记忆）")},
            {"role": "assistant", "content": "对话历史：\n" + (ctx_text or "（无历史）")},
            {"role": "assistant", "content": f"当前意图：{intent_str}"},
            {"role": "user",      "content": user_input},
        ]

        # —— 3. 调用 LLMClient.chat —— 
        try:
            return self.llm.chat(
                messages=messages,
                model=self.default_model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as err:
            print(f"[LanguageDispatcher] LLM 调用失败：{err}")
            return "抱歉，处理请求失败，请稍后重试。"