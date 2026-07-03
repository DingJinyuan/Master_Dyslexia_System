# app/api/nlp.py
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.nlp_service import pos_tagging
from app.services.dictionary_service import lookup_word

router = APIRouter(prefix="/nlp", tags=["nlp"])


class PosTagRequest(BaseModel):
    text: str = Field(..., description="需要做词性标注的文本", min_length=1)


class WordLookupRequest(BaseModel):
    word: str = Field(..., description="要查询的单词/词语", min_length=1)
    sourceLang: Optional[str] = Field(None, description="语言：zh/en，为空自动检测")


@router.post("/pos-tagging", summary="词性标注（整段文本）")
async def api_pos_tagging(req: PosTagRequest):
    try:
        return pos_tagging(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"词性标注失败: {e}")


@router.post("/word-lookup", summary="划词翻译（词性 + 释义 + 发音）")
async def api_word_lookup(req: WordLookupRequest):
    try:
        return await lookup_word(req.word, req.sourceLang)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"词典查询失败: {e}")



