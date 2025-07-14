# LLM接口调用模块(OpenAI or 本地)

import os
import json
import requests

class LLMClient:
    def __init__(self, api_key, api_url):
        pass

    def chat(self, prompt, **kwargs):
        # 直接返回一句固定的“摘要”
        return "（这是一个模拟摘要）用户偏好清淡健康饮食。"
    
    def chat(self, messages, model, temperature, max_tokens):
        payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
        }