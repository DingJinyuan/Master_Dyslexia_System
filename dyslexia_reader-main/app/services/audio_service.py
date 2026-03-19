import json

from app.models.audio import AudioTrack
from app.models.document import Document
from app.services.adapters.tts_adapter import get_tts_provider


class AudioService:
    def __init__(self):
        self.tts = get_tts_provider()

    def create_audio(self, db, document_id: int, speed: float, voice: str, return_word_marks: bool = True) -> AudioTrack:
        document = db.get(Document, document_id)
        if not document or not document.extracted_text:
            raise ValueError("document not found or text not extracted")

        result = self.tts.synthesize(document.extracted_text, speed, voice, return_word_marks)
        track = AudioTrack(
            document_id=document_id,
            provider=self.tts.__class__.__name__,
            audio_url=result["audio_url"],
            marks_json=json.dumps(result["marks"], ensure_ascii=False),
            speed=str(speed),
        )
        db.add(track)
        db.commit()
        db.refresh(track)
        return track
