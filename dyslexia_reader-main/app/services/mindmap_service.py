"""思维导图生成服务 — LLM 大纲提取 + MCP HTML 渲染"""

import os
import uuid
import logging
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.core.config import settings

logger = logging.getLogger(__name__)


class MindmapService:
    """思维导图生成：DeepSeek LLM 提取大纲 → MCP 渲染 HTML"""

    def __init__(self):
        self._llm = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_BASE,
            timeout=60.0,  # LLM HTTP 超时
        )
        self._server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@jinzcdev/markmap-mcp-server"],
        )

    async def generate(self, text: str, max_depth: int = 4) -> dict:
        """主流程：LLM 提取大纲 → MCP 渲染 HTML → 写入文件返回 URL"""
        markdown = await self._llm_extract_outline(text, max_depth)

        if not markdown or not markdown.strip():
            raise ValueError("LLM 返回的大纲为空")

        html = await self._mcp_render(markdown)

        if not html or not html.strip():
            raise ValueError("MCP 渲染的 HTML 为空")

        output_dir = os.path.join("storage", "mindmap")
        os.makedirs(output_dir, exist_ok=True)

        filename = f"{uuid.uuid4().hex}.html"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        return {
            "markdown": markdown,
            "html_url": f"/storage/mindmap/{filename}",
        }

    async def _llm_extract_outline(self, text: str, max_depth: int) -> str:
        """DeepSeek LLM 从原文提取 Markdown 大纲，失败自动重试"""
        system_prompt = (
            f"你是思维导图专家。从文本中提取结构，生成不超过{max_depth}级标题的Markdown大纲。"
            f"要求：\n"
            f"1. 使用 # ## ### #### 标题层级，不超过{max_depth}级\n"
            f"2. 保留核心概念、关键词、逻辑关系\n"
            f"3. 每个节点简洁（不超过15字/词）\n"
            f"4. 必须使用原文语种输出，不要翻译成其他语言\n"
            f"5. 即使文本较短，也必须输出至少3行Markdown\n"
            f"6. 只输出Markdown，不要任何解释"
        )

        last_error = None
        for attempt in range(3):
            try:
                response = await self._llm.chat.completions.create(
                    model=settings.LLM_MODEL_ID,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text},
                    ],
                    temperature=0.3 + attempt * 0.1,
                    max_tokens=3000,
                )
                content = response.choices[0].message.content
                if content and content.strip() and ('#' in content):
                    return content.strip()
                last_error = "LLM 返回的大纲为空"
            except Exception as e:
                last_error = str(e)
                logger.warning(f"大纲提取第{attempt+1}次失败: {e}")

        logger.error(f"LLM 大纲提取失败（3次重试）: {last_error}")
        raise RuntimeError(f"大纲提取失败: {last_error}")

    async def _mcp_render(self, markdown: str) -> str:
        """通过 MCP stdio 调用 markmap-mcp-server 渲染 HTML"""
        try:
            async with stdio_client(self._server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool("markdown_to_mindmap", {
                        "markdown": markdown,
                    })
        except Exception as e:
            logger.error(f"MCP 渲染失败: {e}")
            raise RuntimeError(f"思维导图渲染失败，请确认 Node.js v20+ 已安装: {e}")

        # 在 try/except 外部检查空内容，避免错误信息被吞噬
        if not result.content or len(result.content) == 0:
            raise ValueError("MCP 渲染的 HTML 为空")

        raw = result.content[0].text
        # markmap-mcp-server 可能返回 JSON {"filePath": "..."} 或直接返回 HTML
        if raw.startswith("{") and "filePath" in raw:
            import json
            data = json.loads(raw)
            file_path = data.get("filePath", "")
            if not file_path or not os.path.exists(file_path):
                raise ValueError(f"MCP 生成的 HTML 文件不存在: {file_path}")
            with open(file_path, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            html = raw

        # 精简 HTML：去掉 toolbar 和 html-to-image（加载失败会阻塞渲染）
        import re
        html = re.sub(r'<link[^>]*markmap-toolbar[^>]*>', '', html)
        html = re.sub(r'<script[^>]*markmap-toolbar[^>]*></script>', '', html)
        html = re.sub(r'<script[^>]*html-to-image[^>]*></script>', '', html)
        html = re.sub(r'<script[^>]*cdnjs\.cloudflare[^>]*></script>', '', html)
        # 替换 jsdelivr CDN → fastly 全球节点（国内可访问）
        html = html.replace('https://cdn.jsdelivr.net/npm/', 'https://fastly.jsdelivr.net/npm/')
        return html
