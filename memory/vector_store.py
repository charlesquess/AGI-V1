import os
import faiss
import numpy as np
import pickle
import requests
from typing import List, Tuple, Optional, Dict


class VectorStore:
    """
    向量检索存储：
    - 使用 Ollama 本地模型将文本编码成向量
    - 用 FAISS 做快速近似最近邻检索
    - 支持持久化索引和元数据
    """

    def __init__(
        self,
        model_name: str = "all-minilm:l6-v2",
        dim: int = 384,
        index_path: str = "vs_index.faiss",
        meta_path: str = "vs_meta.pkl",
        batch_size: int = 64,
        host: str = "http://localhost:11434"
    ):
        self.model_name = model_name
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path
        self.batch_size = batch_size
        self.ollama_url = f"{host}/api/embeddings"

        if os.path.exists(index_path) and os.path.exists(meta_path):
            self._load()
        else:
            self.index = faiss.IndexFlatIP(dim)
            self.keys: List[str] = []
            self.texts: List[str] = []

    def _embed(self, text: str) -> np.ndarray:
        """调用 Ollama 接口获取单个文本的嵌入"""
        response = requests.post(self.ollama_url, json={
            "model": self.model_name,
            "prompt": text
        })
        response.raise_for_status()
        embedding = response.json()["embedding"]
        return np.array(embedding, dtype=np.float32).reshape(1, -1)

    def _embed_batch(self, texts: List[str]) -> np.ndarray:
        """批量嵌入多个文本（按顺序逐条请求 Ollama）"""
        vectors = [self._embed(text) for text in texts]
        return np.vstack(vectors)

    def add(self, key: str, text: str):
        if key in self.keys:
            return
        vec = self._embed(text)
        self.index.add(vec)
        self.keys.append(key)
        self.texts.append(text)

    def add_batch(self, items: List[Tuple[str, str]]):
        new_items = [(k, t) for k, t in items if k not in self.keys]
        if not new_items:
            return

        all_texts = [t for _, t in new_items]
        embeddings = []
        for i in range(0, len(all_texts), self.batch_size):
            batch = all_texts[i: i + self.batch_size]
            emb = self._embed_batch(batch)
            embeddings.append(emb)
        vecs = np.vstack(embeddings)

        self.index.add(vecs)
        for k, t in new_items:
            self.keys.append(k)
            self.texts.append(t)

    def query(self, q: str, top_k: int = 5) -> List[Dict]:
        q_vec = self._embed(q)
        scores, ids = self.index.search(q_vec, top_k)
        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < len(self.keys):
                results.append({
                    "key": self.keys[idx],
                    "text": self.texts[idx],
                    "score": float(score)
                })
        return results

    def save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump({
                "keys": self.keys,
                "texts": self.texts
            }, f)

    def _load(self):
        self.index = faiss.read_index(self.index_path)
        with open(self.meta_path, "rb") as f:
            meta = pickle.load(f)
        self.keys = meta["keys"]
        self.texts = meta["texts"]

    def clear(self):
        self.index = faiss.IndexFlatIP(self.dim)
        self.keys = []
        self.texts = []
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.meta_path):
            os.remove(self.meta_path)
