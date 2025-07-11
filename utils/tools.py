# 工具函数模块(打标签/时间戳等)

import time

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