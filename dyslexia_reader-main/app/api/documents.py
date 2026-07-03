from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_approved_user
from app.db.session import get_db
from app.models.document import Document
from app.models.document_block import DocumentBlock
from app.models.user import User
from app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    ParagraphListResponse,
    StructuredDocumentResponse,
)
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])
service = DocumentService()

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_approved_user),
):
    allowed = {"application/pdf", "image/png", "image/jpeg", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="仅支持 PDF/PNG/JPEG/WEBP 格式")

    # 检查文件大小
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"文件大小超过限制（最大 {MAX_UPLOAD_SIZE // (1024*1024)} MB）")

    return service.ingest_file(db, current_user.id, file)


@router.get("", response_model=DocumentListResponse, summary="获取当前用户的文档列表")
def list_documents(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_approved_user),
):
    query = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return DocumentListResponse(total=total, items=items)


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


@router.get("/{document_id}/paragraphs", response_model=ParagraphListResponse, summary="获取文档段落列表")
def list_paragraphs(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_approved_user),
):
    document = db.get(Document, document_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="文档不存在")

    blocks = (
        db.query(DocumentBlock)
        .filter(DocumentBlock.document_id == document_id)
        .order_by(DocumentBlock.block_order.asc())
        .all()
    )

    paragraphs = []
    for i, block in enumerate(blocks):
        text = (block.text_content or "").strip()
        if text:
            paragraphs.append({
                "index": i,
                "text": text,
                "char_count": len(text),
            })

    return ParagraphListResponse(
        document_id=document.id,
        original_filename=document.original_filename,
        paragraphs=paragraphs,
    )
