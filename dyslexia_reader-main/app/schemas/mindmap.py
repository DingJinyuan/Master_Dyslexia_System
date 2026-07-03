"""思维导图 — 请求/响应 Schema"""

from pydantic import BaseModel, Field
from typing import Optional


class MindmapRequest(BaseModel):
    text: str = Field(..., min_length=1, description="需要提取大纲的原文")
    max_depth: int = Field(4, ge=2, le=6, description="导图最大层级深度")


class MindmapResponse(BaseModel):
    success: bool
    markdown: Optional[str] = Field(None, description="LLM 生成的 Markdown 大纲")
    html_url: Optional[str] = Field(None, description="MCP 渲染后的 HTML 导图 URL")
    error: Optional[str] = Field(None, description="错误信息")
