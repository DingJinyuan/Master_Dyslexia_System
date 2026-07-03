"""文本精炼迭代 API — POST /api/v1/refine"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import asyncio

from app.services.refine import RefineOrchestrator

router = APIRouter(prefix="/refine", tags=["refine"])

_orchestrator = RefineOrchestrator()


class RefineRequest(BaseModel):
    original_text: str = Field(..., min_length=1, description="需要处理的原文")
    mode: str = Field(..., pattern="^(full_refine|summary)$", description="模式：full_refine=全文改写, summary=摘要")
    summary_length: str = Field("标准", pattern="^(简短|标准|详细)$", description="摘要长度（仅 summary 模式生效）")
    max_iterations: int = Field(3, ge=1, le=5, description="最大迭代轮次")
    pass_threshold: Optional[float] = Field(None, ge=0.5, le=1.0, description="合格总分阈值，null 时自动按语言选择")


class RefineResponse(BaseModel):
    success: bool
    mode: str
    lang: Optional[str] = None
    refined_text: Optional[str] = None
    iterations: Optional[int] = None
    origin_score: Optional[dict] = None
    final_score: Optional[dict] = None
    improvement: Optional[dict] = None
    score_history: Optional[list] = None
    error: Optional[str] = None


@router.post("", response_model=RefineResponse, summary="文本精炼（全文改写 / 摘要）")
async def api_refine_text(req: RefineRequest):
    """
    多 Agent 迭代文本精炼：
    - full_refine：100% 保留原文信息，优化句式/排版/词汇
    - summary：精简压缩，保留核心关键词

    内置评估节点自动判断是否需要回炉优化，最多迭代 max_iterations 轮。
    """
    try:
        result = await _orchestrator.run(
            original_text=req.original_text,
            mode=req.mode,
            summary_length=req.summary_length,
            max_iterations=req.max_iterations,
            pass_threshold=req.pass_threshold,
        )

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "精炼失败"))

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"精炼异常: {str(e)}")
