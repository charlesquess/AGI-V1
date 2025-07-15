# intent/intent_detector.py

from llm.llm_client import Llama3Client
from config import MODEL_NAME, MODEL_URL

class IntentDetector:
    """
    让 LLaMA3 根据用户输入，输出一个简短的“检索查询”。
    """

    def __init__(self, model=None, url=None):
        self.llm = Llama3Client(model=model or MODEL_NAME, url=url or MODEL_URL)

    def detect_intent(self, text: str) -> str:
        prompt = (
            "你是一名意图分析模块。只能使用中文。"
            f"请基于用户输入生成一个最精准的“查询短语”，用于检索与用户意图相关的信息或记忆。"
            "查询短语应尽量简短、包含核心关键词，不要额外说明。\n\n"
            f"用户输入：{text}\n\n"
            "只输出这个查询短语："
        )
        query = self.llm.chat(
            messages=[{"role":"user","content":prompt}],
            temperature=0.0,
            max_tokens=32
        ).strip()
        return query
