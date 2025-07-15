
import json
from llm.llm_client import Llama3Client
from config import MODEL_NAME, MODEL_URL

class IntentDetector:
    """
    纯 LLM 驱动的意图检测器，不使用规则字典，
    通过 Local Llama3 模型进行意图分类。
    """

    def __init__(self, model=None, url=None):
        # 本地 Llama3 客户端
        self.llm = Llama3Client(model=model or MODEL_NAME,
                                url=url or MODEL_URL)
        # 可选意图集合
        self.intents = [
            "record",          # 记忆记录
            "update_goal",     # 更新目标
            "query_memory",    # 查询记忆
            "greet",           # 打招呼
            "farewell",        # 告别
            "set_language_chinese",  # 切换中文
            "default"          # 默认应答
        ]

    def detect_intent(self, text: str) -> list[str]:
        """
        调用 LLM，对输入文本进行意图分类。
        :param text: 用户原始输入
        :return: [intent] 或 多意图列表
        """
        # 构造 prompt
        intent_list = ", ".join(self.intents)
        prompt = (
            f"请根据用户输入，选择最匹配的意图。从以下列表中只能选一个：\n"
            f"{intent_list}\n\n"
            f"用户输入：{text}\n\n"
            f"只返回意图名称，不要带其他解释。"
        )

        # 调用 LLM
        response = self.llm.chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=16
        ).strip()

        # 有时模型会返回 JSON、逗号或多条，尝试解析：
        # 1）如果是 JSON list
        try:
            parsed = json.loads(response)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

        # 2）逗号分隔
        if "," in response:
            return [r.strip() for r in response.split(",") if r.strip()]

        # 3）单意图
        intent = response.split()[0]
        return [intent] if intent in self.intents else ["default"]