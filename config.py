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