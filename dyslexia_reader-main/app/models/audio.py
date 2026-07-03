from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AudioTrack(Base):
    __tablename__ = "audio_tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False)
    audio_url: Mapped[str] = mapped_column(String(500), nullable=False)
    marks_json: Mapped[str] = mapped_column(Text, nullable=False)
    speed: Mapped[str] = mapped_column(String(20), default="1.0")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
