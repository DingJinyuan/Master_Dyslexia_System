from app.models.document import Document
from app.models.document_block import DocumentBlock
from app.services.adapters.document_parser import DocumentParser
from app.services.adapters.ocr_adapter import get_ocr_provider
from app.services.storage_service import LocalStorageService


class DocumentService:
    def __init__(self):
        self.storage = LocalStorageService()
        self.ocr = get_ocr_provider()
        self.parser = DocumentParser()

    def ingest_file(self, db, user_id: int, upload_file) -> Document:
        ext = upload_file.filename.split(".")[-1].lower() if "." in upload_file.filename else ""

        file_type = (
            "pdf" if ext == "pdf"
            else "image" if ext in {"png", "jpg", "jpeg", "webp"}
            else "text"
        )

        file_url = self.storage.save_upload(upload_file.file, upload_file.filename)

        document = Document(
            user_id=user_id,
            original_filename=upload_file.filename,
            file_type=file_type,
            file_url=file_url,
            processing_status="processing",
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        # 先清理旧 block（为了后续支持重处理）
        db.query(DocumentBlock).filter(DocumentBlock.document_id == document.id).delete()

        if file_type == "pdf":
            parsed_blocks, extracted_text = self.parser.parse(file_url)

            for item in parsed_blocks:
                block = DocumentBlock(
                    document_id=document.id,
                    page=item["page"],
                    block_order=item["block_order"],
                    block_type=item["block_type"],
                    text_content=item.get("text_content"),
                    image_url=item.get("image_url"),
                    image_caption=item.get("image_caption"),
                    bbox_json=item.get("bbox_json"),
                )
                db.add(block)

            document.extracted_text = extracted_text
        else:
            # 兼容旧逻辑：图片仍走 OCR
            extracted = self.ocr.extract_text(file_url)
            document.extracted_text = extracted

            if extracted:
                db.add(
                    DocumentBlock(
                        document_id=document.id,
                        page=1,
                        block_order=1,
                        block_type="text",
                        text_content=extracted,
                        image_url=None,
                        image_caption=None,
                        bbox_json=None,
                    )
                )

        document.processing_status = "done"
        db.commit()
        db.refresh(document)
        return document

    def get_structured_document(self, db, document_id: int, user_id: int):
        document = db.get(Document, document_id)
        if not document or document.user_id != user_id:
            return None

        blocks = (
            db.query(DocumentBlock)
            .filter(DocumentBlock.document_id == document_id)
            .order_by(DocumentBlock.page.asc(), DocumentBlock.block_order.asc())
            .all()
        )

        return {
            "id": document.id,
            "original_filename": document.original_filename,
            "file_type": document.file_type,
            "file_url": document.file_url,
            "processing_status": document.processing_status,
            "created_at": document.created_at,
            "blocks": blocks,
        }