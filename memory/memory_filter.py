# memory/memory_filter.py

import difflib
from typing import List, Dict

class MemoryFilter:
    """
    根据 LLM 生成的查询短语，在 EM/SM/MS 三大记忆里检索最匹配的条目。
    """

    def __init__(self, em_store, sm_store, ms_store):
        self.em_store = em_store
        self.sm_store = sm_store
        self.ms_store = ms_store

    def filter(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        :param query: 从 IntentDetector 得到的检索短语
        :param top_k: 最多返回条数
        :return: List of {"source","key","content","timestamp","score"}
        """
        # 1) 把所有记忆体拼成一张大表
        pool = []
        # episodic
        for key, content, ts in self.em_store.get_all_records():
            pool.append({"source":"episodic_memory","key":key,
                         "content":content,"timestamp":ts})
        # semantic
        for key, content, ts in self.sm_store.get_all_records():
            pool.append({"source":"semantic_memory","key":key,
                         "content":content,"timestamp":ts})
        # mission
        for key, content, ts in self.ms_store.get_all_records():
            pool.append({"source":"mission_memory","key":key,
                         "content":content,"timestamp":ts})

        # 2) 对每条 content 计算简单相似度：子串匹配得高分，否则 difflib
        results = []
        for item in pool:
            text = item["content"]
            if query in text:
                score = 1.0
            else:
                # ratio([0,1])
                score = difflib.SequenceMatcher(None, query, text).ratio()
            if score > 0.1:  # 阈值可调
                results.append({**item, "score": score})

        # 3) 按 score 排序并取 top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
