"""
词典查询服务（划词翻译）
- 英文：使用 Free Dictionary API（免费，无需 key）
- 中文：使用汉典爬取或自建简易词典
- 同时返回词性信息
"""
import re
import logging
from typing import Optional

import httpx
from pypinyin import pinyin, Style

logger = logging.getLogger(__name__)

# Free Dictionary API（英文，免费无需key）
FREE_DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"


async def lookup_word(word: str, source_lang: str = None) -> dict:
    """
    划词翻译 + 词性查询统一入口
    点击一个单词 → 返回发音、词性、释义、例句
    """
    word = word.strip()
    if not word:
        return {"success": False, "error": "空查询"}

    if source_lang is None:
        source_lang = _detect_word_lang(word)

    if source_lang == "en":
        return await _lookup_english(word)
    else:
        return await _lookup_chinese(word)


def _detect_word_lang(word: str) -> str:
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', word))
    return "zh" if chinese_chars > 0 else "en"


async def _lookup_english(word: str) -> dict:
    """
    英文单词查询 - 使用 Free Dictionary API
    返回：音标、词性、释义、例句
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{FREE_DICT_API}{word.lower()}")

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                entry = data[0]
                result = {
                    "success": True,
                    "word": word,
                    "language": "en",
                    "phonetic": "",
                    "audioUrl": "",
                    "meanings": [],
                }

                # 提取音标
                if entry.get("phonetic"):
                    result["phonetic"] = entry["phonetic"]

                # 提取发音音频URL
                for ph in entry.get("phonetics", []):
                    if ph.get("audio"):
                        result["audioUrl"] = ph["audio"]
                        break
                    if ph.get("text") and not result["phonetic"]:
                        result["phonetic"] = ph["text"]

                # 提取词性和释义
                for meaning in entry.get("meanings", []):
                    pos = meaning.get("partOfSpeech", "unknown")
                    definitions = []
                    for defn in meaning.get("definitions", [])[:3]:  # 最多取3个释义
                        d = {
                            "definition": defn.get("definition", ""),
                            "example": defn.get("example", "")
                        }
                        definitions.append(d)

                    synonyms = meaning.get("synonyms", [])[:5]  # 最多5个同义词

                    result["meanings"].append({
                        "partOfSpeech": pos,
                        "definitions": definitions,
                        "synonyms": synonyms
                    })

                return result

        # API 返回404等
        return {
            "success": False,
            "word": word,
            "language": "en",
            "error": f"未找到单词 '{word}' 的释义"
        }

    except Exception as e:
        logger.error(f"英文词典查询失败: {str(e)}")
        return {
            "success": False,
            "word": word,
            "language": "en",
            "error": str(e)
        }


async def _lookup_chinese(word: str) -> dict:
    """
    中文词语查询
    - 拼音：用 pypinyin
    - 释义：使用自建简易词典 + 免费API回退
    """
    try:
        # 获取拼音
        word_pinyin = " ".join([p[0] for p in pinyin(word, style=Style.TONE)])

        # 词性标注（用 jieba）
        import jieba.posseg as pseg
        pos_result = list(pseg.cut(word))
        pos_tag = pos_result[0].flag if pos_result else "unknown"

        # 中文词性名映射
        pos_label_map = {
            "n": "名词", "v": "动词", "a": "形容词", "d": "副词",
            "nr": "人名", "ns": "地名", "nt": "机构名",
            "r": "代词", "m": "数词", "q": "量词", "p": "介词",
            "c": "连词", "u": "助词", "vn": "动名词",
        }
        pos_label = pos_label_map.get(pos_tag, pos_tag)

        # 尝试用免费的汉典 API 或本地词典
        definition = await _get_chinese_definition(word)

        result = {
            "success": True,
            "word": word,
            "language": "zh",
            "pinyin": word_pinyin,
            "partOfSpeech": pos_tag,
            "partOfSpeechLabel": pos_label,
            "meanings": [
                {
                    "partOfSpeech": pos_label,
                    "definitions": [
                        {"definition": definition, "example": ""}
                    ],
                    "synonyms": []
                }
            ]
        }

        return result

    except Exception as e:
        logger.error(f"中文词典查询失败: {str(e)}")
        return {
            "success": False,
            "word": word,
            "language": "zh",
            "error": str(e)
        }


# 简易中文词典（兜底使用）
_SIMPLE_ZH_DICT = {
    "翱翔": "在空中飞行",
    "矗立": "高高地直立着",
    "巍峨": "形容山或建筑物高大",
    "蕴含": "包含在内",
    "瞻仰": "恭敬地看",
    "倏忽": "形容非常快",
    "恳请": "真诚地请求",
    "购置": "购买，置办",
    "践行": "实行，去做",
    "告罄": "指东西用完了",
    "稀缺": "稀少缺乏",
    "竭力": "用尽全力",
    "摒弃": "舍弃不要",
    "协助": "帮助，辅助",
    "抵达": "到达目的地",
    "即刻": "立刻，马上",
}


async def _get_chinese_definition(word: str) -> str:
    """获取中文词语释义"""
    # 1. 先查本地词典
    if word in _SIMPLE_ZH_DICT:
        return _SIMPLE_ZH_DICT[word]

    # 2. 尝试免费的网络词典API
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # 使用一个公开的中文词典查询
            response = await client.get(
                f"https://api.pearktrue.cn/api/hanyu/?word={word}"
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200 and data.get("explain"):
                    return data["explain"]
    except Exception as e:
        logger.warning(f"网络词典查询失败，使用默认释义: {e}")

    return f"'{word}' 的释义暂无，请联网查询"