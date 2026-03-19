import re
import logging
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

def preprocess_text(text: str) -> str:
    """清洗文本中的异常回车、换行"""
    if not text: return ""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = [line.strip() for line in text.split('\n')]
    return "\n".join([line for line in lines if line])

def detect_language(text: str) -> str:
    """语言检测"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(text.strip())
    if total_chars == 0: return "en"
    return "zh" if chinese_chars / (total_chars + 1e-6) > 0.3 else "en"

def summarize_text_with_deepseek(text: str, summary_length: str) -> str:
    """调用 DeepSeek 进行文本总结"""
    clean_text = preprocess_text(text)
    lang = detect_language(clean_text)
    language = "中文" if lang == "zh" else "英文"

    # 根据长度要求定制 Prompt
    length_hint = {
        "简短": "请用极简短的几句话概括核心观点。",
        "标准": "请提供一个中等长度的总结，包含主要要点。",
        "详细": "请提供一个详细的总结，保留原文的关键细节和逻辑。"
    }.get(summary_length, "请提供一个标准长度的总结。")

    prompt = f"请帮我总结以下{language}文本，要求如下：\n"
    prompt += f"1. 保持使用{language}进行总结。\n"
    prompt += f"2. {length_hint}\n"
    prompt += f"3. 不要添加任何自我介绍或解释性语句。\n"
    prompt += f"\n\n原始文本：\n{clean_text}\n\n总结内容："

    try:
        # 使用新版 SDK 初始化
        client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_API_BASE)

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的文案总结助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"总结功能 DeepSeek 调用失败: {str(e)}")
        return f"[API报错: {str(e)}] " + clean_text[:100] + "..."

def summarize_text(original_text: str, summary_length: str = "标准") -> dict:
    """文本总结统一入口"""
    clean_text = preprocess_text(original_text)
    lang = detect_language(clean_text)

    summarized_text = summarize_text_with_deepseek(clean_text, summary_length)

    return {
        "summarizedText": summarized_text,
        "language": lang,
        "originalLength": len(clean_text),
        "summarizedLength": len(summarized_text)
    }
