# -*- coding: utf-8 -*-
"""
DyslexiaEvaluator — 文本质量评估器
从项目根目录 ai.py 迁移，接口不变，依赖路径适配
"""

import re
import json
import string
import asyncio
import logging

import jieba
import numpy as np
from openai import AsyncOpenAI
from rouge_score import rouge_scorer
from nltk.tokenize import word_tokenize
from bert_score import score as bert_score_fn

logger = logging.getLogger(__name__)

# 固定权重
DIM_WEIGHTS = {
    "reading_effectiveness": 1/3,
    "content_fidelity": 1/3,
    "layout_effectiveness": 1/3,
}
SUB_WEIGHTS = {
    "reading": [1/3, 1/3, 1/3],
    "content": [1.0],
    "layout": [1/3, 1/3, 1/3],
}

# 中英文标点正则 - 使用 unicode 转义避免编码问题
CHN_PUNC = re.compile(
    "[" + "。" + "！" + "？" + "；" + "：" + "，"
    + "、" + "“" + "”" + "（" + "）" + "《" + "》" + "]"
)
ENG_PUNC = re.compile(r'[.!?;:,\"\']')


class DyslexiaEvaluator:
    def __init__(self, llm_client: AsyncOpenAI):
        self.client = llm_client
        self.rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
        jieba.initialize()

    # ==================== 语言 & 工具 ====================

    def _detect_lang(self, text: str) -> str:
        """判定中/英文，支持 CJK 基本区 + 扩展 A 区"""
        if not text or not text.strip():
            return "en"
        # 㐀-䶿=CJK Ext-A, 一-鿿=CJK 基本, 豈-﫿=兼容汉字
        chinese_chars = len(re.findall(r"[㐀-䶿一-鿿豈-﫿]", text))
        total_chars = len(text.replace(" ", "").replace("\n", ""))
        if total_chars == 0:
            return "en"
        return "zh" if chinese_chars / max(total_chars, 1) > 0.15 else "en"

    def _extract_float(self, raw: str) -> float:
        res = re.search(r"\d+\.?\d*", raw)
        if res is None:
            return 0.5
        return float(np.clip(float(res.group()), 0.0, 1.0))

    def _split_sentences(self, text: str, lang: str):
        if not text.strip():
            return []
        seps = r"[。！？；]" if lang == "zh" else r"[.!?]"
        sentences = re.split(seps, text)
        return [s.strip() for s in sentences if s.strip()]

    def _tokenize(self, text: str, lang: str):
        if lang == "zh":
            return [w for w in jieba.cut(text) if w.strip() and w not in string.punctuation]
        else:
            try:
                tokens = word_tokenize(text)
            except LookupError:
                import nltk
                nltk.download("punkt_tab", quiet=True)
                tokens = word_tokenize(text)
            return [w for w in tokens if w.isalpha()]

    def _split_paragraphs(self, text: str):
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        return paras if paras else [text.strip()]

    # ==================== 阅读有效性 ====================

    def calc_fre(self, text: str, lang: str):
        sents = self._split_sentences(text, lang)
        tokens = self._tokenize(text, lang)
        if len(sents) == 0 or len(tokens) == 0:
            return 0.0
        avg_sen_len = len(tokens) / len(sents)
        if lang == "en":
            total_chars = sum(len(tok) for tok in tokens)
            avg_char_per_word = total_chars / len(tokens)
            fre = 206.835 - 1.015 * avg_sen_len - 84.6 * avg_char_per_word
            return float(np.clip(fre / 100, 0.0, 1.0))
        else:
            total_chars = len(text.replace(" ", "").replace("\n", ""))
            avg_char_per_token = total_chars / len(tokens)
            read_score = 1 - (0.22 * avg_sen_len / 30 + 0.45 * avg_char_per_token / 3)
            return float(np.clip(read_score, 0.0, 1.0))

    def calc_fkgl(self, text: str, lang: str):
        sents = self._split_sentences(text, lang)
        tokens = self._tokenize(text, lang)
        if len(sents) == 0 or len(tokens) == 0:
            return 0.0
        avg_sen_len = len(tokens) / len(sents)
        if lang == "en":
            total_chars = sum(len(tok) for tok in tokens)
            avg_char_per_word = total_chars / len(tokens)
            grade = 0.39 * avg_sen_len + 11.8 * avg_char_per_word - 15.59
            grade = np.clip(grade, 0, 20)
            return float(1.0 - (grade / 20))
        else:
            avg_char_per_token = len(text.replace(" ", "")) / len(tokens)
            grade = 0.35 * avg_sen_len + 9.2 * avg_char_per_token - 12
            grade = np.clip(grade, 0, 18)
            return float(1.0 - (grade / 18))

    def calc_avg_sent_len(self, text: str, lang: str):
        sen = self._split_sentences(text, lang)
        if not sen:
            return 0.0
        avg_len = float(np.mean([len(s) for s in sen]))
        max_limit = 80 if lang == "zh" else 120
        return float(1.0 - np.clip(avg_len / max_limit, 0, 1))

    def evaluate_reading(self, text: str, lang: str):
        f1 = self.calc_fre(text, lang)
        f2 = self.calc_fkgl(text, lang)
        f3 = self.calc_avg_sent_len(text, lang)
        total = f1 * SUB_WEIGHTS["reading"][0] + f2 * SUB_WEIGHTS["reading"][1] + f3 * SUB_WEIGHTS["reading"][2]
        return {"fre": round(f1, 4), "fkgl": round(f2, 4), "avg_sent_len": round(f3, 4), "dimension_score": round(total, 4)}

    # ==================== 内容保真 ====================

    def calc_bleu(self, ori: str, simp: str, lang: str):
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
        ref = [self._tokenize(ori, lang)]
        cand = self._tokenize(simp, lang)
        return sentence_bleu(ref, cand, smoothing_function=SmoothingFunction().method1)

    def calc_bertscore(self, ori: str, simp: str, lang: str):
        _, _, f1 = bert_score_fn([simp], [ori], lang=lang, verbose=False)
        return float(f1[0])

    async def calc_keyword_keep(self, ori: str, simp: str, lang: str):
        if lang == "zh":
            prompt = "提取原文所有核心专有名词、专业术语、关键概念，只返回纯JSON数组。示例：[\"中原\",\"礼制\"]\n原文："
        else:
            prompt = "Extract core proper nouns and technical terms only. Return ONLY pure JSON array. Example:[\"Central Plains\",\"ritual\"]\nText: "
        prompt += ori

        try:
            res = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"},
            )
            content = res.choices[0].message.content.strip()
            data = json.loads(content)
            if isinstance(data, dict):
                keys = next((v for v in data.values() if isinstance(v, list)), [])
            elif isinstance(data, list):
                keys = data
            else:
                keys = []
        except Exception:
            keys = []

        if not keys:
            return 1.0

        keep = 0
        simp_tokens = set(self._tokenize(simp, lang))
        if lang == "zh":
            for k in keys:
                kw_parts = set(jieba.cut(k))
                if kw_parts & simp_tokens:
                    keep += 1
        else:
            simp_lower = simp.lower()
            for k in keys:
                if k.lower() in simp_lower:
                    keep += 1
        return keep / len(keys)

    # ==================== 叙事有效性 ====================

    async def calc_formality_score(self, text: str, lang: str):
        if lang == "zh":
            prompt = f"文本正式度打分0~1。0=极度口语低幼，0.5适中通俗易懂，1=极度晦涩学术。面向阅读障碍人群，适度通俗更佳。仅返回数字。文本：{text}"
        else:
            prompt = f"Rate formality 0~1. 0=very casual oral, 0.5=moderate, 1=overly academic. For dyslexia readers, slightly casual is better. Return number only. Text: {text}"
        res = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        raw_score = self._extract_float(res.choices[0].message.content.strip())
        base = 1.0 - abs(raw_score - 0.4) * 2
        return float(np.clip(base, 0.0, 1.0))

    async def calc_naturalness_score(self, text: str, lang: str):
        if lang == "zh":
            prompt = f"面向阅读障碍者评估语句流畅度0~1，通顺自然、无生硬机器翻译、简洁易懂得分高，只返回0~1数字。文本：{text}"
        else:
            prompt = f"Evaluate text naturalness 0~1 for dyslexia readers. Smooth, natural, easy sentences score higher. Return number only. Text: {text}"
        res = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        return self._extract_float(res.choices[0].message.content.strip())

    # ==================== 排版有效性 ====================

    def calc_paragraph_count_score(self, text: str):
        paras = self._split_paragraphs(text)
        cnt = len(paras)
        score = np.log1p(cnt) / np.log1p(10)
        return float(np.clip(score, 0.0, 1.0))

    def calc_avg_paragraph_len(self, text: str):
        paras = self._split_paragraphs(text)
        if not paras:
            return 0.0
        avg = float(np.mean([len(p) for p in paras]))
        return float(1.0 - np.clip(avg / 200, 0, 1))

    def calc_punctuation_norm(self, text: str, lang: str):
        total_char = len(text.replace(" ", "").replace("\n", ""))
        if total_char == 0:
            return 0.0
        punc_pattern = CHN_PUNC if lang == "zh" else ENG_PUNC
        punc_num = len(re.findall(punc_pattern, text))
        ratio = punc_num / total_char
        return float(np.clip(ratio * 15, 0, 1))

    def evaluate_layout(self, text: str, lang: str):
        l1 = self.calc_paragraph_count_score(text)
        l2 = self.calc_avg_paragraph_len(text)
        l3 = self.calc_punctuation_norm(text, lang)
        total = l1 * SUB_WEIGHTS["layout"][0] + l2 * SUB_WEIGHTS["layout"][1] + l3 * SUB_WEIGHTS["layout"][2]
        return {"para_count": round(l1, 4), "avg_para_len": round(l2, 4), "punctuation": round(l3, 4), "dimension_score": round(total, 4)}

    # ==================== 总入口 ====================

    async def evaluate_all(self, original_text: str, simplified_text: str):
        lang = self._detect_lang(original_text)

        res_read = self.evaluate_reading(simplified_text, lang)
        res_layout = self.evaluate_layout(simplified_text, lang)

        b1 = self.calc_bleu(original_text, simplified_text, lang)
        res_content = {"bleu": round(b1, 4), "dimension_score": round(b1, 4)}

        total_score = (
            res_read["dimension_score"] * DIM_WEIGHTS["reading_effectiveness"]
            + res_content["dimension_score"] * DIM_WEIGHTS["content_fidelity"]
            + res_layout["dimension_score"] * DIM_WEIGHTS["layout_effectiveness"]
        )

        return {
            "total_score": round(total_score, 4),
            "reading": res_read,
            "content": res_content,
            "layout": res_layout,
        }
