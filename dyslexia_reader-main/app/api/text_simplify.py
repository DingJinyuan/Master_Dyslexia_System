
from fastapi import APIRouter, HTTPException, Form
from app.schemas.text_simplify import SimplifyResponse
from app.services.text_simplify_service import simplify_text

router = APIRouter()

@router.post("/simplify", response_model=SimplifyResponse, summary="文本简化")
async def api_simplify_text(
    # 将原来的 SimplifyRequest 拆解为 Form 参数
    originalText: str = Form(..., description="需要简化的原文，支持直接粘贴带回车的文档"),
    simplifyLevel: str = Form("标准", description="简化等级：简易/标准"),
    enableWordReplace: bool = Form(True, description="是否替换复杂词"),
    enableKeywordMark: bool = Form(True, description="是否标注关键词")
):
    """
    文本简化接口
    - 采用 Form 提交，解决直接粘贴文档时 JSON 解析报错（422）的问题
    - 自动检测中英文、拆分长句、替换复杂词、标注关键词
    """
    try:
        # 这里的参数名要对应你 service 里的 simplify_text 函数参数
        result = simplify_text(
            original_text=originalText,
            simplify_level=simplifyLevel,
            enable_word_replace=enableWordReplace,
            enable_keyword_mark=enableKeywordMark
        )

        return SimplifyResponse(
            simplifiedText=result["simplifiedText"],
            language=result["language"],
            replacements=result["replacements"],
            originalLength=result["originalLength"],
            simplifiedLength=result["simplifiedLength"]
        )
    except Exception as e:
        import logging
        logging.error(f"文本简化失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文本简化失败: {str(e)}")
