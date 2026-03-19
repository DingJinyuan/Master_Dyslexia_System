"""
文本总结接口 (支持 Form 提交，处理回车换行)
"""
from fastapi import APIRouter, HTTPException, Form
from typing import Optional
from pydantic import BaseModel

from app.services.text_summarize_service import summarize_text
from app.services.readability_service import calculate_readability

router = APIRouter()

# 定义返回模型
class SummarizeResponse(BaseModel):
    summarizedText: str
    language: str
    readabilityScore: Optional[float] = None
    readabilityLevel: Optional[str] = None
    originalLength: int = 0
    summarizedLength: int = 0

@router.post("/summarize", response_model=SummarizeResponse, summary="文本总结")
async def api_summarize_text(
    # 使用 Form 替代 BaseModel
    originalText: str = Form(..., description="需要总结的原文，支持直接粘贴"),
    summaryLength: str = Form("标准", description="总结长度：简短/标准/详细")
):
    """
    文本总结接口
    - 采用 Form 提交，支持物理换行
    - 自动检测中英文并生成精炼总结
    - 包含可读性评分
    """
    try:
        # 1. 调用总结服务
        result = summarize_text(
            original_text=originalText,
            summary_length=summaryLength
        )

        # 2. 调用已有的可读性评分服务
        # 注意：这里是对总结后的文字进行评分
        readability = calculate_readability(result["summarizedText"])

        return SummarizeResponse(
            summarizedText=result["summarizedText"],
            language=result["language"],
            readabilityScore=readability.get("readabilityScore"),
            readabilityLevel=readability.get("level"),
            originalLength=result["originalLength"],
            summarizedLength=result["summarizedLength"]
        )
    except Exception as e:
        import logging
        logging.error(f"文本总结接口报错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文本总结失败: {str(e)}")
