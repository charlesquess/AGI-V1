# llm/llm_client.py

from config import MODEL_NAME, MODEL_URL
import json, urllib.request

class Llama3Client:
    def __init__(self, model=None, url=None):
        self.model = model or MODEL_NAME
        self.url   = url   or MODEL_URL

    def chat(self, messages, model=None, temperature=0.0, max_tokens=None, **kwargs):
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {"seed":123, "temperature":temperature, "num_ctx":2048}
        }
        if max_tokens:
            payload["options"]["max_new_tokens"] = max_tokens

        req = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type":"application/json"},
            method="POST"
        )
        result = ""
        with urllib.request.urlopen(req) as resp:
            for line in resp:
                chunk = json.loads(line.decode("utf-8").strip())
                # OpenAI-compatible
                if "choices" in chunk:
                    result += chunk["choices"][0]["message"]["content"]
                elif "message" in chunk:
                    result += chunk["message"]["content"]
        return result