# config.py 新增
LLM_CONFIG = {
    "model_path": "./models/llama3-8b",  # 本地模型路径
    "max_new_tokens": 256,
    "temperature": 0.7,
    "top_p": 0.9,
    "quantization": "q4_0",  # 量化选项：q4_0, q5_0, q8_0, f16
    "context_window": 4096,
    "n_gpu_layers": 40,  # 使用GPU加速的层数
    "system_prompt": "你是一个乐于助人的生活助理，根据用户记忆提供友好建议。"
}

SYSTEM_PROMPT = """
你是用户的私人助理AGI，你的所有回复应该是更像一个私人管家，称号用户为先生，语气温柔一点，也能根据用户记忆提供友好建议。。
"""

# 本地 Ollama 服务下要用的模型名
MODEL_NAME1 = "deepseek-llm:latest"
MODEL_NAME2 = "deepseek-r1:7b"

# Ollama HTTP 接口地址
MODEL_URL = "http://localhost:11434/v1/chat/completions"