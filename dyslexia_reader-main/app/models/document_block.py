from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class DocumentBlock(Base):
    __tablename__ = "document_blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    page: Mapped[int] = mapped_column(Integer, nullable=False)
    block_order: Mapped[int] = mapped_column(Integer, nullable=False)

    # text / image
    block_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # text block
    text_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    # image block
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_caption: Mapped[str | None] = mapped_column(Text, nullable=True)

    # optional metadata
    bbox_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)