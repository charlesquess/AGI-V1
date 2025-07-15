# memory/simple_retriever.py

import difflib
from typing import List, Dict

class SimpleMemoryRetriever:
    """
    用于基于检索短语，在三大记忆体中做子串+相似度匹配，返回 Top-K 结果。
    """

    def __init__(self, em_store, sm_store, ms_store):
        self.em = em_store
        self.sm = sm_store
        self.ms = ms_store

    def get_all(self) -> List[Dict]:
        """
        把三大记忆体的所有记录都读出来，格式化成列表。
        """
        pool = []
        # 事实记忆：可能多条
        for key, content, ts in self.em.get_all_records():
            pool.append({"source":"episodic_memory","key":key,"content":content,"timestamp":ts})
        # 语义记忆：只要最新一条
        for key, content, ts in self.sm.get_all_records():
            pool.append({"source":"semantic_memory","key":key,"content":content,"timestamp":ts})
        # 目标记忆：只要最新一条
        for key, content, ts in self.ms.get_all_records():
            pool.append({"source":"mission_memory","key":key,"content":content,"timestamp":ts})
        return pool

    def query(self, query: str, top_k: int = 5, cutoff: float = 0.2) -> List[Dict]:
        """
        对所有 content 做子串和 difflib 相似度匹配，返回 Top-K。
        """
        pool = self.get_all()
        results = []
        for item in pool:
            text = item["content"]
            if query in text:
                score = 1.0
            else:
                score = difflib.SequenceMatcher(None, query, text).ratio()
            if score >= cutoff:
                results.append({**item, "score": score})
        # 排序，取前 K
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
