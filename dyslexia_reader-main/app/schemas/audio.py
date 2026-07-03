from pydantic import BaseModel


class TTSRequest(BaseModel):
    document_id: int
    speed: float = 1.0
    voice: str = "female_soft"
    return_word_marks: bool = True


class TTSResponse(BaseModel):
    audio_track_id: int
    audio_url: str
    speed: float
    sync_marks: list[dict]
