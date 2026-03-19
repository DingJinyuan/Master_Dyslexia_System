from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.services.tts_service import (
    text_to_speech,
    text_to_speech_by_sentences,
    get_available_voices,
    YOUDAO_VOICES,
)

router = APIRouter(prefix="/tts", tags=["tts"])


class TTSRequest(BaseModel):
    text: str = Field(..., description="要转换的文本", min_length=1)
    voice: Optional[str] = Field(None, description="edge-tts语音名，为空自动选择")
    voiceName: Optional[str] = Field(
        None,
        description="有道发音人(如 youxiaoqin/youxiaomei)，指定后优先使用有道TTS"
    )
    rate: str = Field("+0%", description="语速: '-30%'慢速, '+30%'快速")
    pitch: str = Field("+0Hz", description="音调(仅edge-tts)")


class TTSSentenceRequest(BaseModel):
    text: str = Field(..., description="要转换的文本")
    voice: Optional[str] = Field(None, description="edge-tts语音名")
    voiceName: Optional[str] = Field(None, description="有道发音人")
    rate: str = Field("+0%", description="语速")


@router.post("", summary="文字转语音（全文）")
async def api_tts(req: TTSRequest):
    result = await text_to_speech(
        text=req.text,
        voice=req.voice,
        rate=req.rate,
        pitch=req.pitch,
        voice_name=req.voiceName,
    )
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "TTS失败"))
    return result


@router.post("/sentences", summary="文字转语音（逐句，支持高亮跟随）")
async def api_tts_sentences(req: TTSSentenceRequest):
    result = await text_to_speech_by_sentences(
        text=req.text,
        voice=req.voice,
        rate=req.rate,
        voice_name=req.voiceName,
    )
    return result


@router.get("/voices", summary="获取可用语音列表")
async def api_get_voices(language: Optional[str] = None):
    voices = await get_available_voices(language)
    return {"voices": voices, "total": len(voices)}


@router.get("/youdao-voices", summary="获取有道发音人列表")
async def api_get_youdao_voices():
    result = []
    for voice_id, info in YOUDAO_VOICES.items():
        result.append({
            "voiceName": voice_id,
            "displayName": info["name"],
            "gender": info["gender"],
            "language": info["lang"],
        })
    return {"voices": result, "total": len(result)}
