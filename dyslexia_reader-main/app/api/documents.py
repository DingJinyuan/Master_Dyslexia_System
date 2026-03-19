from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_approved_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse, StructuredDocumentResponse
from app.services.document_service import DocumentService
from app.services.tts_service import text_to_speech, text_to_speech_by_sentences
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/documents", tags=["documents"])
service = DocumentService()


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_approved_user),
):
    allowed = {"application/pdf", "image/png", "image/jpeg", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="only PDF/PNG/JPEG/WEBP are supported")

    return service.ingest_file(db, current_user.id, file)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_approved_user),
):
    document = db.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="document not found")
    return document


@router.get("/{document_id}/structured", response_model=StructuredDocumentResponse)
def get_structured_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_approved_user),
):
    result = service.get_structured_document(db, document_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="document not found")
    return result

class DocumentTTSRequest(BaseModel):
    voice: Optional[str] = Field(None, description="edge-tts语音名，为空自动选择")
    voiceName: Optional[str] = Field(
        None, description="有道发音人(如 youxiaoqin/youxiaomei)"
    )
    rate: str = Field("+0%", description="语速: '-30%'慢速, '+30%'快速")
    pitch: str = Field("+0Hz", description="音调(仅edge-tts)")


@router.post("/{document_id}/tts", summary="将文档全文转换为语音")
async def document_tts(
    document_id: int,
    req: DocumentTTSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_approved_user),
):
    # 1. 权限 + 文档校验
    document = db.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="document not found")

    if not document.extracted_text:
        raise HTTPException(status_code=400, detail="document has no extracted text")

    # 2. 调用 TTS
    result = await text_to_speech(
        text=document.extracted_text,
        voice=req.voice,
        rate=req.rate,
        pitch=req.pitch,
        voice_name=req.voiceName,
    )

    # 3. 错误处理
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "TTS failed"))

    # 4. 返回（包含 audioUrl）
    return result


@router.post("/{document_id}/tts/sentences", summary="将文档逐句转换为语音")
async def document_tts_by_sentences(
    document_id: int,
    req: DocumentTTSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_approved_user),
):
    document = db.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="document not found")

    if not document.extracted_text:
        raise HTTPException(status_code=400, detail="document has no extracted text")

    result = await text_to_speech_by_sentences(
        text=document.extracted_text,
        voice=req.voice,
        rate=req.rate,
        voice_name=req.voiceName,
    )
    return result
