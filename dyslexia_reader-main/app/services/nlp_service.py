"""
NLP 服务：词性标注
对整段文本做词性标注（支持中英文）
"""
import re
import logging

import jieba.posseg as pseg
import spacy

from app.core.config import settings


logger = logging.getLogger(__name__)

_spacy_nlp = None


def _get_spacy_nlp():
    global _spacy_nlp
    if _spacy_nlp is None:
        _spacy_nlp = spacy.load(settings.SPACY_EN_MODEL)
    return _spacy_nlp


# 中文词性映射（jieba 词性 → 易读名称 + 颜色标签）
ZH_POS_MAP = {
    "n": {"label": "名词", "color": "#4A90D9"},
    "nr": {"label": "人名", "color": "#4A90D9"},
    "ns": {"label": "地名", "color": "#4A90D9"},
    "nt": {"label": "机构名", "color": "#4A90D9"},
    "nz": {"label": "其他名词", "color": "#4A90D9"},
    "v": {"label": "动词", "color": "#E74C3C"},
    "vd": {"label": "副动词", "color": "#E74C3C"},
    "vn": {"label": "动名词", "color": "#E74C3C"},
    "a": {"label": "形容词", "color": "#27AE60"},
    "ad": {"label": "副形词", "color": "#27AE60"},
    "an": {"label": "名形词", "color": "#27AE60"},
    "d": {"label": "副词", "color": "#F39C12"},
    "m": {"label": "数词", "color": "#9B59B6"},
    "q": {"label": "量词", "color": "#9B59B6"},
    "r": {"label": "代词", "color": "#1ABC9C"},
    "p": {"label": "介词", "color": "#95A5A6"},
    "c": {"label": "连词", "color": "#95A5A6"},
    "u": {"label": "助词", "color": "#BDC3C7"},
    "x": {"label": "标点", "color": "#BDC3C7"},
    "w": {"label": "标点", "color": "#BDC3C7"},
}

# 英文词性映射（spaCy POS → 易读名称 + 颜色标签）
EN_POS_MAP = {
    "NOUN": {"label": "Noun", "color": "#4A90D9"},
    "PROPN": {"label": "Proper Noun", "color": "#4A90D9"},
    "VERB": {"label": "Verb", "color": "#E74C3C"},
    "ADJ": {"label": "Adjective", "color": "#27AE60"},
    "ADV": {"label": "Adverb", "color": "#F39C12"},
    "PRON": {"label": "Pronoun", "color": "#1ABC9C"},
    "DET": {"label": "Determiner", "color": "#95A5A6"},
    "ADP": {"label": "Preposition", "color": "#95A5A6"},
    "CONJ": {"label": "Conjunction", "color": "#95A5A6"},
    "CCONJ": {"label": "Conjunction", "color": "#95A5A6"},
    "NUM": {"label": "Number", "color": "#9B59B6"},
    "PUNCT": {"label": "Punctuation", "color": "#BDC3C7"},
    "AUX": {"label": "Auxiliary", "color": "#E74C3C"},
    "PART": {"label": "Particle", "color": "#BDC3C7"},
    "INTJ": {"label": "Interjection", "color": "#E67E22"},
    "SCONJ": {"label": "Subordinating Conj.", "color": "#95A5A6"},
    "SYM": {"label": "Symbol", "color": "#BDC3C7"},
    "X": {"label": "Other", "color": "#BDC3C7"},
}


def detect_language(text: str) -> str:
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(text.strip())
    if total_chars == 0:
        return "en"
    return "zh" if chinese_chars / total_chars > 0.3 else "en"


def pos_tagging(text: str) -> dict:
    """
    对文本做词性标注
    返回每个词的文本、词性标签、词性名称、颜色
    """
    lang = detect_language(text)

    if lang == "zh":
        return _pos_tagging_zh(text)
    else:
        return _pos_tagging_en(text)


def _pos_tagging_zh(text: str) -> dict:
    """中文词性标注（jieba）"""
    words = pseg.cut(text)
    tokens = []

    for word, flag in words:
        pos_info = ZH_POS_MAP.get(flag, {"label": flag, "color": "#BDC3C7"})
        tokens.append({
            "word": word,
            "pos": flag,
            "posLabel": pos_info["label"],
            "color": pos_info["color"]
        })

    return {
        "language": "zh",
        "tokens": tokens,
        "totalTokens": len(tokens)
    }


def _pos_tagging_en(text: str) -> dict:
    """英文词性标注（spaCy）"""
    nlp = _get_spacy_nlp()
    doc = nlp(text)
    tokens = []

    for token in doc:
        pos_info = EN_POS_MAP.get(token.pos_, {"label": token.pos_, "color": "#BDC3C7"})
        tokens.append({
            "word": token.text,
            "pos": token.pos_,
            "posLabel": pos_info["label"],
            "color": pos_info["color"],
            "lemma": token.lemma_   # 词元（原形）
        })

    return {
        "language": "en",
        "tokens": tokens,
        "totalTokens": len(tokens)
    }