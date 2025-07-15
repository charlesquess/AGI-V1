# 工具函数模块(打标签/时间戳等)

import psutil
import time
from datetime import datetime

class Tools:
    @staticmethod
    def add_timestamp(data):
        """为数据添加时间戳"""
        data['timestamp'] = time.time()
        return data

    @staticmethod
    def add_label(data, label):
        """为数据添加标签"""
        if 'labels' not in data:
            data['labels'] = []
        data['labels'].append(label)
        return data

    @staticmethod
    def remove_label(data, label):
        """从数据中移除标签"""
        if 'labels' in data and label in data['labels']:
            data['labels'].remove(label)
        return data
    
    @staticmethod
    def get_timestamp():
        """获取当前时间戳"""
        return time.time()

    @staticmethod
    def to_unix_timestamp():
        return int(time.time())

    @staticmethod
    def ensure_ollama_running(process_name="ollama"):
        """
        检查 Ollama 服务进程是否在运行，若未运行则抛出 RuntimeError。
        """
        for proc in psutil.process_iter(["name"]):
            if process_name in proc.info["name"]:
                return True
        raise RuntimeError("Ollama 服务未运行，请先启动 Ollama。")
