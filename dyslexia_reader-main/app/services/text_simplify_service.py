import re
import logging
import openai
from app.core.config import settings

logger = logging.getLogger(__name__)


def preprocess_text(text: str) -> str:
    """清洗文本"""
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


def simplify_text_with_deepseek(text: str, simplify_level: str, enable_word_replace: bool,
                                enable_keyword_mark: bool) -> str:
    """使用 DeepSeek API 进行文本简化"""
    clean_text = preprocess_text(text)
    lang = detect_language(clean_text)
    language = "中文" if lang == "zh" else "英文"

    # 构建 Prompt
    prompt = f"请帮我简化以下{language}文本，按照以下严格要求处理：\n"
    if lang == "zh":
        prompt += "1. 只替换复杂词汇为简单同义词，不要扩充额外内容\n2. 对于短句子不要拆分\n3. 对于长句子和长段落进行拆分\n4. 不要添加任何解释\n"
        if enable_keyword_mark: prompt += "5. 对关键词添加 <mark> 标签\n"
    else:
        prompt += "1. Only replace complex words with simpler synonyms\n2. Split long sentences/paragraphs\n3. Do not add explanations\n"
        if enable_keyword_mark: prompt += "4. Add <mark> tags to keywords\n"

    if simplify_level == "简易": prompt += "\n请使用更简单的语言进行简化。"
    prompt += f"\n\n原始文本：\n{clean_text}\n\n简化后的文本："

    try:
        # ================= 适配新版 OpenAI SDK (1.0.0+) =================
        from openai import OpenAI
        client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_BASE
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的文本简化助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
        # ==============================================================

    except Exception as e:
        # 如果报错，不仅记录日志，还把报错信息打印到控制台，方便你调试
        print(f"!!! DeepSeek 调用失败详情: {str(e)}")
        logger.error(f"DeepSeek API 调用失败: {str(e)}")
        # 暂时返回带错误信息的文本，方便你一眼看出哪里配置错了
        return f"[API报错: {str(e)}] " + clean_text


def simplify_text(original_text: str, simplify_level: str = "标准",
                  enable_word_replace: bool = True,
                  enable_keyword_mark: bool = True) -> dict:
    clean_text = preprocess_text(original_text)
    lang = detect_language(clean_text)

    simplified_text = simplify_text_with_deepseek(
        text=clean_text,
        simplify_level=simplify_level,
        enable_word_replace=enable_word_replace,
        enable_keyword_mark=enable_keyword_mark
    )

    return {
        "simplifiedText": simplified_text,
        "language": lang,
        "replacements": [],
        "originalLength": len(clean_text),
        "simplifiedLength": len(simplified_text)
    }
