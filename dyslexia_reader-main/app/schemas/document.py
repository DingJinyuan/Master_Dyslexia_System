from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    original_filename: str
    file_type: str
    file_url: str
    extracted_text: str | None
    processing_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentBlockResponse(BaseModel):
    id: int
    document_id: int
    page: int
    block_order: int
    block_type: str
    text_content: str | None = None
    image_url: str | None = None
    image_caption: str | None = None
    bbox_json: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class StructuredDocumentResponse(BaseModel):
    id: int
    original_filename: str
    file_type: str
    file_url: str
    processing_status: str
    created_at: datetime
    blocks: list[DocumentBlockResponse]