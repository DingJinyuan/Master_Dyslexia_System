from pydantic import BaseModel, Field
from typing import Optional, List

class SimplifyRequest(BaseModel):
    originalText: str = Field(..., description="需要简化的原文", min_length=1)
    simplifyLevel: str = Field("标准", description="简化等级：简易/标准")
    enableWordReplace: bool = Field(True, description="是否替换复杂词")
    enableKeywordMark: bool = Field(True, description="是否标注关键词")

class SimplifyResponse(BaseModel):
    simplifiedText: str
    language: str
    readabilityScore: Optional[float] = None
    readabilityLevel: Optional[str] = None
    replacements: List = []
    originalLength: int = 0
    simplifiedLength: int = 0
