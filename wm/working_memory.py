import datetime
from typing import List, Dict, Union

class WorkingMemory:
    """
    工作记忆：存储对话历史、记忆条目，并构建对话 prompt。
    """

    def __init__(self, max_history: int = 10):
        self.context: List[Dict[str, str]] = []  # [{"role": "user"/"assistant", "text": "...", "ts": "..."}]
        self.memories: List[Dict[str, str]] = [] # [{"source": ..., "key": ..., "content": ..., "timestamp": ...}]
        self.max_history = max_history

    def load_memories(self, memory_items: List[Dict[str, str]]):
        """加载或刷新记忆摘要条目（来自 MemoryFilter）。"""
        self.memories = memory_items.copy()

    def add_context(self, role: str, text: str):
        """记录一轮对话，按最大长度截断历史。"""
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.context.append({"role": role, "text": text, "ts": ts})
        if len(self.context) > self.max_history * 2:
            self.context = self.context[-self.max_history*2:]

    def get_context_text(self) -> str:
        """生成上下文文本块：带角色与时间戳。"""
        lines = []
        for entry in self.context:
            prefix = "用户" if entry["role"] == "user" else "助手"
            lines.append(f"{entry['ts']} {prefix}: {entry['text']}")
        return "\n".join(lines)

    def get_memories_text(self) -> str:
        """生成记忆文本块：包括来源和摘要时间戳。"""
        lines = []
        for m in self.memories:
            ts = m.get("timestamp", "")
            lines.append(f"[{m['source']}][{ts}][{m['key']}] {m['content']}")
        return "\n".join(lines)

    def get_prompt(self, user_input: str, intents: List[str]) -> str:
        """
        综合上下文、历史记忆和当前输入，生成适合 LLM 的完整 prompt。
        """
        parts = [
            "历史记忆：",
            self.get_memories_text() or "（无）",
            "\n对话历史：",
            self.get_context_text() or "（无历史）",
            f"\n当前意图：{', '.join(intents)}",
            f"\n用户输入：{user_input}",
            "\n助手回复："
        ]
        return "\n".join(parts)