import time
from threading import Lock
from config import LLM_CONFIG
from utils.tools import logger

try:
    from llama_cpp import Llama
except ImportError:
    logger.error("请安装llama-cpp-python: pip install llama-cpp-python")
    raise

class Llama3Client:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize_model()
            return cls._instance
    
    def _initialize_model(self):
        """单例模式初始化模型"""
        start_time = time.time()
        logger.info(f"加载Llama3模型: {LLM_CONFIG['model_path']}")
        
        self.llm = Llama(
            model_path=LLM_CONFIG["model_path"],
            n_ctx=LLM_CONFIG["context_window"],
            n_gpu_layers=LLM_CONFIG["n_gpu_layers"],
            verbose=False
        )
        
        # 应用量化（如果有）
        if LLM_CONFIG["quantization"]:
            logger.info(f"应用量化: {LLM_CONFIG['quantization']}")
            self.llm.apply_quantization(LLM_CONFIG["quantization"])
        
        load_time = time.time() - start_time
        logger.success(f"模型加载完成! 耗时: {load_time:.2f}秒")

    def build_llama3_prompt(self, user_prompt):
        """构建Llama3专用提示格式"""
        return f"""
<|begin_of_text|>
<|start_header_id|>system<|end_header_id|>
{LLM_CONFIG['system_prompt']}
<|end_header_id|>
<|start_header_id|>user<|end_header_id|>
{user_prompt}
<|end_header_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

    def generate(self, prompt, **kwargs):
        """生成响应文本"""
        try:
            # 合并配置参数
            params = {
                "max_tokens": LLM_CONFIG["max_new_tokens"],
                "temperature": LLM_CONFIG["temperature"],
                "top_p": LLM_CONFIG["top_p"],
                "stop": ["<|end_header_id|>", "<|eot_id|>"],
                "echo": False
            }
            params.update(kwargs)
            
            # 构建Llama3专用提示
            full_prompt = self.build_llama3_prompt(prompt)
            
            # 执行推理
            start_time = time.time()
            output = self.llm(
                full_prompt,
                **params
            )
            gen_time = time.time() - start_time
            
            # 提取响应文本
            response = output['choices'][0]['text'].strip()
            tokens_used = output['usage']['prompt_tokens'] + output['usage']['completion_tokens']
            
            logger.debug(f"生成完成! 耗时: {gen_time:.2f}秒, Token: {tokens_used}")
            return response
        
        except Exception as e:
            logger.error(f"生成失败: {str(e)}")
            return "抱歉，我暂时无法处理这个请求。"