"""
可读性评分接口 (支持大段文本粘贴)
"""
from fastapi import APIRouter, HTTPException, Form  # 导入 Form 替代 BaseModel
from app.services.readability_service import calculate_readability

router = APIRouter()

# 注意：这里不再需要 ReadabilityRequest 类，直接在函数参数里定义即可

@router.post("/readability", summary="可读性评分")
async def api_readability(
    text: str = Form(..., description="要评估的文本，支持直接粘贴带回车的文档内容")
):
    """
    计算文本的可读性评分
    - 采用 Form 表单提交，彻底解决直接粘贴文档时报 422 JSON Decode Error 的问题
    - 英文：Flesch-Kincaid 等多个指标
    - 中文：基于句长、词汇多样性的自定义指标
    """
    try:
        # 直接传入 Form 接收到的 text
        # 你的 service 层已经有了 preprocess_text 逻辑，它会处理这里的换行
        result = calculate_readability(text)
        return result
    except Exception as e:
        # 增加详细日志记录，方便排查
        import logging
        logging.error(f"可读性评分失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"可读性评分失败: {str(e)}")
