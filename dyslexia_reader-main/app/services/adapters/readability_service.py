"""
可读性评分服务
- 英文：Flesch-Kincaid、Gunning Fog、SMOG 等
- 中文：自定义可读性指标（基于句长、词频等）
"""
import re
import math
import logging
import jieba

logger = logging.getLogger(__name__)

def preprocess_text(text: str) -> str:
    """清洗文本中的异常换行和空白字符"""
    if not text:
        return ""
    # 1. 将 Windows 风格的 \r\n 统一替换为 \n
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # 2. 清理掉“假”换行
    lines = [line.strip() for line in text.split('\n')]
    # 3. 过滤掉空白行，重新用标准换行符连接
    text = "\n".join([line for line in lines if line])
    return text

def detect_language(text: str) -> str:
    # 使用清洗后的 text 进行检测
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(text.strip())
    if total_chars == 0:
        return "en"
    return "zh" if chinese_chars / (total_chars + 1e-6) > 0.3 else "en"

# ========== 核心入口修改处 ==========

def calculate_readability(text: str) -> dict:
    """计算文本可读性评分"""
    # 1. 第一步：先清洗文本，处理掉回车换行
    clean_text = preprocess_text(text)

    # 2. 第二步：检测语言
    lang = detect_language(clean_text)

    # 3. 第三步：传入清洗后的文本进行计算
    if lang == "en":
        return _english_readability(clean_text)
    else:
        return _chinese_readability(clean_text)

# ==================================

def _english_readability(text: str) -> dict:
    """
    英文可读性评分
    使用 textstat 库计算多个指标
    """
    try:
        import textstat
        textstat.set_lang("en")

        # Flesch Reading Ease
        flesch_score = textstat.flesch_reading_ease(text)
        fk_grade = textstat.flesch_kincaid_grade(text)
        fog_index = textstat.gunning_fog(text)
        smog = textstat.smog_index(text)
        ari = textstat.automated_readability_index(text)

        word_count = textstat.lexicon_count(text)
        sentence_count = textstat.sentence_count(text)
        syllable_count = textstat.syllable_count(text)
        avg_sentence_len = word_count / max(sentence_count, 1)

        if flesch_score >= 80:
            level, level_en = "非常简单", "Very Easy"
        elif flesch_score >= 60:
            level, level_en = "简单", "Easy"
        elif flesch_score >= 40:
            level, level_en = "中等", "Medium"
        elif flesch_score >= 20:
            level, level_en = "较难", "Difficult"
        else:
            level, level_en = "非常难", "Very Difficult"

        return {
            "language": "en",
            "readabilityScore": round(flesch_score, 1),
            "level": level,
            "levelEn": level_en,
            "details": {
                "fleschReadingEase": round(flesch_score, 1),
                "fleschKincaidGrade": round(fk_grade, 1),
                "gunningFogIndex": round(fog_index, 1),
                "smogIndex": round(smog, 1),
                "automatedReadabilityIndex": round(ari, 1),
            },
            "statistics": {
                "wordCount": word_count,
                "sentenceCount": sentence_count,
                "syllableCount": syllable_count,
                "avgSentenceLength": round(avg_sentence_len, 1),
            }
        }
    except ImportError:
        return _english_readability_simple(text)

def _english_readability_simple(text: str) -> dict:
    """简化版英文可读性评分"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = text.split()
    word_count = len(words)
    sentence_count = max(len(sentences), 1)
    avg_sentence_len = word_count / sentence_count

    avg_syllables = sum(_count_syllables(w) for w in words) / max(word_count, 1)
    flesch = 206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables)
    flesch = max(0, min(100, flesch))

    level = "简单" if flesch >= 60 else ("中等" if flesch >= 40 else "较难")

    return {
        "language": "en",
        "readabilityScore": round(flesch, 1),
        "level": level,
        "statistics": {
            "wordCount": word_count,
            "sentenceCount": sentence_count,
            "avgSentenceLength": round(avg_sentence_len, 1),
        }
    }

def _count_syllables(word: str) -> int:
    word = word.lower().strip(".,!?;:'\"")
    if not word: return 0
    count, vowels, prev_vowel = 0, "aeiou", False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)

def _chinese_readability(text: str) -> dict:
    """
    中文可读性评分
    """
    # 这里的 re.split 会处理清洗后的标准换行符 \n
    sentences = re.split(r'[。！？!?\n]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = max(len(sentences), 1)

    words = list(jieba.cut(text))
    words = [w for w in words if w.strip() and not re.match(r'^[\s\W]+$', w)]
    word_count = len(words)

    char_count = len(re.findall(r'[\u4e00-\u9fff]', text))
    avg_sentence_len = char_count / sentence_count

    unique_words = len(set(words))
    ttr = unique_words / max(word_count, 1)

    long_words = [w for w in words if len(w) >= 4]
    long_word_ratio = len(long_words) / max(word_count, 1)

    score = 100
    score -= max(0, (avg_sentence_len - 15)) * 3
    score -= long_word_ratio * 50
    score -= max(0, (ttr - 0.8)) * 20
    score = max(0, min(100, score))

    if score >= 80: level = "非常简单"
    elif score >= 60: level = "简单"
    elif score >= 40: level = "中等"
    elif score >= 20: level = "较难"
    else: level = "非常难"

    return {
        "language": "zh",
        "readabilityScore": round(score, 1),
        "level": level,
        "statistics": {
            "charCount": char_count,
            "wordCount": word_count,
            "sentenceCount": sentence_count,
            "uniqueWordCount": unique_words,
            "avgSentenceLength": round(avg_sentence_len, 1),
            "typeTokenRatio": round(ttr, 3),
            "longWordRatio": round(long_word_ratio, 3),
        }
    }
