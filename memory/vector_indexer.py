# memory/vector_indexer.py

from memory.em_store import EMStore
from memory.sm_store import SMStore
from memory.ms_store import MSStore
from memory.vector_store import VectorStore

class MemoryVectorIndexer:
    """
    将三大记忆体的所有文本一次性向量化并构建索引，
    并提供 query(text) 接口做检索。
    """

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.em_store = EMStore()
        self.sm_store = SMStore()
        self.ms_store = MSStore()

        self.vs_em = VectorStore(model_name=model_name)
        self.vs_sm = VectorStore(model_name=model_name)
        self.vs_ms = VectorStore(model_name=model_name)

    def build_indexes(self):
        texts = self.em_store.get_all_texts()
        if texts:
            self.vs_em.add_texts(texts)

        texts = self.sm_store.get_all_texts()
        if texts:
            self.vs_sm.add_texts(texts)

        texts = self.ms_store.get_all_texts()
        if texts:
            self.vs_ms.add_texts(texts)

    def query(self, text: str, top_k: int = 5):
        results = []
        for source, vs in [("episodic", self.vs_em),
                           ("semantic", self.vs_sm),
                           ("mission",  self.vs_ms)]:
            hits = vs.query(text, top_k)
            for content, score in hits:
                results.append({"source": source, "content": content, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]