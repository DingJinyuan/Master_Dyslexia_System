"""SummaryAgent — 摘要，精简内容 + 保留核心关键词"""

from app.services.refine.base_agent import BaseAgent


class SummaryAgent(BaseAgent):
    """摘要 Agent：精简压缩原文，保留核心术语，必须原语种输出"""

    _LENGTH_HINTS = {
        "简短": "请用 2-3 句话概括核心观点，极简。",
        "标准": "请提供一个中等长度的摘要，覆盖所有主要要点。",
        "详细": "请提供一个较详细的摘要，保留关键细节和逻辑脉络。",
    }

    @property
    def _system_prompt(self) -> str:
        return (
            "你是面向阅读障碍用户的文本摘要专家。请严格按照以下原则生成摘要：\n"
            "1. 精简压缩原文，保留核心关键词、专业术语、关键数据。\n"
            "2. 用简单短句重述，去除次要细节和冗余修饰。\n"
            "3. 【最重要】必须和原文用同一种语言！原文是英文就输出英文，原文是中文就输出中文。绝对不要翻译！\n"
            "4. 输出必须为纯文本，不包含 markdown 标记。"
        )

    async def summarize(self, original_text: str, lang: str, summary_length: str = "标准",
                        prev_score: dict = None) -> str:
        """执行摘要"""
        length_hint = self._LENGTH_HINTS.get(summary_length, self._LENGTH_HINTS["标准"])
        lang_hint = "必须用英文输出" if lang == "en" else "必须用中文输出"
        user_prompt = f"{length_hint}\n{lang_hint}\n\n原文：\n{original_text}"

        if prev_score:
            hint = self._build_iteration_hint(prev_score, "summary")
            if hint:
                user_prompt += f"\n\n{hint}"

        user_prompt += "\n\n摘要："
        return await self._call_llm(self._system_prompt, user_prompt, temperature=0.3)
