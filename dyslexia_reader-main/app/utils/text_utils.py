"""
文本处理公共工具函数
- detect_language: 检测文本语言（中/英）
- preprocess_text: 清洗文本中的异常换行和空白字符
"""

import re


def detect_language(text: str) -> str:
    """检测文本语言：返回 'zh'（中文）或 'en'（英文）"""
    if not text:
        return "en"
    chinese_chars = len(re.findall(r'[一-鿿]', text))
    total_chars = len(text.strip())
    if total_chars == 0:
        return "en"
    return "zh" if chinese_chars / total_chars > 0.3 else "en"


def preprocess_text(text: str) -> str:
    """清洗文本中的异常换行和空白字符"""
    if not text:
        return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = [line.strip() for line in text.split('\n')]
    return "\n".join([line for line in lines if line])
