"""FullRefineAgent — 全文改写，100% 保留信息，只调整句式/排版/词汇"""

from app.services.refine.base_agent import BaseAgent


class FullRefineAgent(BaseAgent):
    """全文改写 Agent：面向阅读障碍者，大幅简化句式与词汇"""

    @property
    def _system_prompt(self) -> str:
        return (
            "你是面向阅读障碍用户的文本优化专家。你必须像给小学生讲课一样改写原文，让它变得非常通俗好懂。\n"
            "严格遵循以下原则：\n"
            "1. 100% 保留原文全部信息——不得删减任何事实、数字、人名、地名、专业术语。\n"
            "2. 句式改造（最重要）：\n"
            "   - 把长句拆成多个短句，中文每句不超过 15 个字，英文每句不超过 12 个词。\n"
            "   - 不要用\"不仅…而且…\"\"虽然…但是…\"这类复杂句式，直接拆成两句话。\n"
            "   - 用最简单的主谓宾结构：谁做了什么。\n"
            "3. 词汇大幅简化：\n"
            "   - 把书面语、学术词、成语全部换成大白话。例如：\n"
            "     \"呈现下降趋势\" → \"下降了\"\n"
            "     \"相较于\" → \"比\"\n"
            "     \"显著提升\" → \"大大提高\"\n"
            "     \"深入探讨\" → \"仔细研究\"\n"
            "     \"在此基础上\" → \"在这个基础上\"\n"
            "     \"进行对比分析\" → \"做比较\"或\"对比\"\n"
            "     \"具有重要理论意义和实践价值\" → \"在理论上和实际中都很有用\"\n"
            "     \"不容忽视\" → \"不能被忽视\"或\"很重要\"\n"
            "     \"呈现出\" → \"表现出\"或直接说\"有\"\n"
            "     \"由此可见\" → \"这样看来\"\n"
            "     \"其\" → \"它的\"或\"它们的\"\n"
            "     \"该\" → \"这个\"\n"
            "   - 把\"的\"字长串拆开，不要出现\"……的……的……的……\"\n"
            "4. 排版分段：每个自然段不超过 3 句话，段落之间空一行。\n"
            "5. 保持原文语种输出，不要添加任何解释或评论。\n"
            "6. 输出必须为纯文本，不包含 markdown 标记。"
        )

    async def refine(self, original_text: str, lang: str, prev_score: dict = None) -> str:
        """执行全文改写"""
        max_len = 15 if lang == "zh" else 12
        lang_hint = "必须用中文输出" if lang == "zh" else "必须用英文输出"
        user_prompt = f"请把下面这段文字改写成小学生都能看懂的大白话。{lang_hint}，绝对不要翻译成其他语言。中文每句不超过 {max_len} 个字，英文每句不超过 {max_len} 个词。\n\n原文：\n{original_text}"

        if prev_score:
            hint = self._build_iteration_hint(prev_score, "full_refine")
            if hint:
                user_prompt += f"\n\n{hint}"

        user_prompt += "\n\n改写后的大白话（必须非常通俗、像聊天一样自然）："
        return await self._call_llm(self._system_prompt, user_prompt, temperature=0.7)
