"""BaseAgent — LLM 调用、语言检测、迭代微调提示 公共层"""

import re
import logging
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """所有改写/摘要 Agent 的公共基类"""

    def __init__(self, llm_client: AsyncOpenAI = None):
        if llm_client:
            self.client = llm_client
        else:
            self.client = AsyncOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_API_BASE,
                timeout=60.0,
            )

    # ---------- 语言检测 ----------

    def _detect_lang(self, text: str) -> str:
        """判定中/英文，支持 CJK 基本区 + 扩展 A 区"""
        if not text or not text.strip():
            return "en"
        # 㐀-䶿=CJK Ext-A, 一-鿿=CJK 基本, 豈-﫿=兼容汉字
        chinese_chars = len(re.findall(r"[㐀-䶿一-鿿豈-﫿]", text))
        total_chars = len(text.replace(" ", "").replace("\n", ""))
        if total_chars == 0:
            return "en"
        return "zh" if chinese_chars / total_chars > 0.15 else "en"

    # ---------- 通用 LLM 调用 ----------

    async def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """调用 DeepSeek，返回文本"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.LLM_MODEL_ID,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=4000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise

    # ---------- 迭代微调提示 ----------

    def _build_iteration_hint(self, prev_score: dict, mode: str) -> str:
        """根据上一轮评分生成本轮微调指导语"""
        content = prev_score.get("content", {})
        reading = prev_score.get("reading", {})

        hints = []
        if mode == "full_refine":
            if content.get("dimension_score", 1.0) < 0.70:
                hints.append("上一轮内容保真度不足，请确保不丢失任何原文信息、事实、数字、术语")
            if reading.get("dimension_score", 1.0) < 0.60:
                hints.append("上一轮可读性偏低，请进一步拆分长句、用更简单的词替代复杂词、增加段落分段")
        else:  # summary
            if content.get("keyword_keep", 1.0) < 0.70:
                hints.append("上一轮关键词保留不足，请保留更多核心术语和关键概念")
            if reading.get("dimension_score", 1.0) < 0.65:
                hints.append("上一轮仍偏冗长，请进一步精简、用更短的句子表达")

        if hints:
            return "【本轮微调指导】\n" + "\n".join(f"- {h}" for h in hints)
        return ""

    # ---------- 语言相关的阈值 ----------

    @property
    def max_sentence_len(self) -> int:
        """由子类覆盖"""
        return 80
