# llm/llm_client.py

from config import MODEL_NAME, MODEL_URL
import json, urllib.request
import random

class Llama3Client:
    def __init__(self, model=None, url=None):
        self.model = model or MODEL_NAME
        self.url   = url   or MODEL_URL

    def chat(self, messages, model=None, temperature=0.7, max_tokens=None, **kwargs):
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "seed": random.randint(0, 2**32 - 1),
            "stream": False  # 禁用流，保证响应完整
        }

        if max_tokens:
            payload["options"] = {"max_new_tokens": max_tokens}

        req = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        result = ""
        with urllib.request.urlopen(req) as resp:
            resp_json = json.load(resp)  # 一次性解析整个响应
            if "choices" in resp_json:
                result += resp_json["choices"][0]["message"]["content"]
            elif "message" in resp_json:
                result += resp_json["message"]["content"]
        return result
