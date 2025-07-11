# LLM接口调用模块(OpenAI or 本地)

import os
import json
import requests

class LLMClient:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url

    def call_llm(self, prompt, model="gpt-3.5-turbo", temperature=0.7):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "model": model,
            "temperature": temperature
        }
        response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error calling LLM API: {response.status_code} {response.text}")
    
    def generate_response(self, prompt, model="gpt-3.5-turbo", temperature=0.7):
        # response = self.call_llm(prompt, model, temperature)
        response = "hello world"
        return response["text"]
    